import sys
sys.path.append('/yuanzichen/LlamaChat')
import torch
from Agent.GenAgent import GenAgent
import Agent.utils.AgentUtils as AgentUtils
import yaml

class LLMEvalAgents():
    def __init__(self,
                 model_path,
                 U_Agent_config: dict,
                 I_Agent_config: dict,
                 max_conv_turns: int,
                 ) -> None:
        
        self._U_Agent_config = U_Agent_config
        self._I_Agent_config = I_Agent_config
        self._max_conv_turns = max_conv_turns

        tokenizer, model = AgentUtils.get_tokenizer_model(model_path)
        device = torch.device("cuda")
        model.eval()
        model.to(device)
        

        system_prompt1 = """<s>[INST] <<SYS>>
        You are now playing the role of a chatbot and you need to initiate a topic.<</SYS>>
        """

        system_prompt2 = """<s>[INST] <<SYS>>
        You are now playing the role of a chatbot and you need to talk freely based on what the other person is saying to you .<</SYS>>
        """


        self._U_Agent = GenAgent(model=model, 
                                 tokenizer=tokenizer, 
                                 system_prompt=system_prompt1,
                                 **self._U_Agent_config)
        
        self._I_Agent = GenAgent(model=model, 
                                 tokenizer=tokenizer, 
                                 system_prompt=system_prompt2,
                                 **self._I_Agent_config)
        
    def Chat(self):

        r_u = self._U_Agent.chat('You can start the conversation. You can say whatever you want')
        print("agent_u的回应:", r_u)

        for i in range(self._max_conv_turns):
            r_i = self._U_Agent.chat(r_u)
            print("agent_i的回应:", r_i)

            r_u = self._I_Agent.chat(r_i)
            print("agent_i的回应:", r_i)


if __name__ == "__main__":

    # 读取YAML配置文件
    with open('/yuanzichen/LlamaChat/Agent/test/TestConfig.yaml', 'r') as file:
        config = yaml.safe_load(file)

    llm_eval_agents = LLMEvalAgents(**config)

    # 执行Chat方法
    llm_eval_agents.Chat()