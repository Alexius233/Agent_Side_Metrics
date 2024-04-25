import sys
sys.path.append('/yuanzichen/LlamaChat')
from typing import Sequence, List
from llama_index.llms import ChatMessage
from llama_index.tools import BaseTool
import Agent.utils.ReadUtils as ReadUtils
from Agent.GenAgent import GenAgent
import utils.AgentUtils  
from prompt import AgentPrompt, Interaction
import torch
import re

# 训练的时候需要在上面再封一个class

# 用yaml来初始化
class LLMEvalAgents():
    def __init__(self,
                 model_path: str,
                 E_Agent_config: dict,
                 U_Agent_config: dict,
                 I_Agent_config: dict,
                 max_conv_turns: int,
                 data_path: dict,  # 读取dataset
                 ) -> None:
        
        self._E_Agent_config = E_Agent_config
        self._U_Agent_config = U_Agent_config
        self._I_Agent_config = I_Agent_config
        self._max_conv_turns = max_conv_turns
        
        tokenizer, model = utils.AgentUtils .get_tokenizer_model(model_path)
        model.eval()
        device = torch.device("cuda")
        model.to(device)

        self._UAgent_prompt = AgentPrompt.UAgentPrompt
        self._IAgent_prompt = AgentPrompt.IAgentPrompt
        self._EAgent_prompt = AgentPrompt.EAgentPrompt

        self._InterationPrompt = Interaction.InteractionPrompt

        self._U_Agent = GenAgent(model=model, 
                                 tokenizer=tokenizer, 
                                 system_prompt=self._UAgent_prompt.system_prompt,
                                 **self._U_Agent_config)
        
        self._I_Agent = GenAgent(model=model, 
                                 tokenizer=tokenizer, 
                                 system_prompt=self._IAgent_prompt.system_prompt,
                                 **self._I_Agent_config)
        
        self._E_Agent = GenAgent(model=model, 
                                 tokenizer=tokenizer, 
                                 system_prompt=self._EAgent_prompt.system_prompt,
                                 **self._E_Agent_config)
    
    # 从 U agent的第一轮对话里提取 userPortrait
    def ExtractUserPortrait(self, response: str) -> str:
        pattern = r"(User ID:.+?Visual and Aesthetic Preferences:.+?)\n"

        match = re.search(pattern, response, re.DOTALL)

        if match:
            extracted_text = match.group(1)  # 提取匹配的文本
            # 权宜之计? 可能调整prompt可以不用clean
            cleaned_text = re.sub(r"^User ID: \d+:\n\n", "", extracted_text, flags=re.MULTILINE)

            return cleaned_text
        else:
            print("!!! No match found in user protrait extraction !!!")
    
    def ExtractItemProtrait(self, response: str) -> str:
        pattern = r"(?s)Movie Portrait:(.*?)Overall,\s"  
        match = re.search(pattern, response, re.DOTALL | re.MULTILINE)

        if match:
            extracted_text = match.group(1)  # 提取匹配的文本

            return extracted_text
        else:
            # TODO: 通过调prompt应该可以弄好, padding只是权宜之计
            print("!!! No match found in item protrait extraction !!!")
            pad = "padding"
            return pad
        
    
    # 从 E agent 中抽取 query
    def QueryExtraction(self, response: str) -> str:
        user_analyst_query = re.search(r"Query for user analyst:\n(.*?)\n", response, re.DOTALL)
        if user_analyst_query:
            user_query = user_analyst_query.group(1).strip()

        # 提取“Query for movie analyst:”后的内容
        movie_analyst_query = re.search(r"Query for movie analyst:\n(.*?)\n", response, re.DOTALL)
        if movie_analyst_query:
            movie_query = movie_analyst_query.group(1).strip()

        return user_query, movie_query
    
    # 启动 Agents 然后注入 init_prompt
    def InitStep(self) -> None:

        self._U_Agent.chat(self._UAgent_prompt.init_prompt)
        self._I_Agent.chat(self._IAgent_prompt.init_prompt)

        return None

    # generate用户画像和物品画像
    def FirstStep(self, user_history, items) -> list:
        # uAgent分析用户, iAgent分析item,先u后i

        item_portrait = " "

        count = 1
        for item in items:
            print(f"这是第{count}个item的处理")
            self._IAgent_usage_prompt = self._IAgent_prompt.start_prompt.format(item) 
            response_i = self._I_Agent.chat(self._IAgent_usage_prompt)
            print(response_i)
            item_portrait = item_portrait + "/n" + self.ExtractItemProtrait(response_i)

            count += 1

        self._UAgent_usage_prompt = self._UAgent_prompt.start_prompt.format(user_history) 
        response_u = self._U_Agent.chat(self._UAgent_usage_prompt)

        user_portrait = self.ExtractUserPortrait(response_u)


        self._EAgent_usage_prompt = self._EAgent_prompt.usage_prompt.format(user_portrait, item_portrait)
        response_e = self._E_Agent.chat(self._EAgent_usage_prompt)
        
        return response_u, response_i, response_e
        
    def Step(self, response_u: str, response_i:str, response_e:str) -> list:
        # 循环的step: u/i agent 生成, eAgent总结

        query_u, query_i = self.QueryExtraction(response_e)

        query_u = utils.AgentUtils.fill_query_template(query_u, self._I_Agent, self._InterationPrompt.U_interaction_prompt)
        query_i = utils.AgentUtils.fill_query_template(query_i, self._I_Agent, self._InterationPrompt.I_interaction_prompt)

        response_u = self._U_Agent.chat(query_u)
        response_i = self._I_Agent.chat(query_i)

        query_e = self._InterationPrompt.EG_interaction_prompt.format(response_u, response_i)

        response_e = self._E_Agent.chat(query_e)

        return response_u, response_i, response_e

        

    def Chat(self, user_history, items):
        # 总的调用
        
        _ = self.InitStep()

        r_u, r_i, r_e = self.FirstStep(user_history, items)
        
        #for i in range(self._max_conv_turns):
            
            #r_u, r_i, r_e = self.Step(r_u, r_i, r_e)

        print("agent u的回应:", r_u)
        print("/n")
        print("agent u的回应:", r_i)
        print("/n")
        print("agent u的回应:", r_e)

        # TODO: 驱动EAgent做Evaluate