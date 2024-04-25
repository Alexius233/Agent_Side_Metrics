import json
import torch
from typing import Sequence, List
import sys
sys.path.append('/yuanzichen/LlamaChat')
from llama_index.llms import ChatMessage
from llama_index.tools import BaseTool, FunctionTool
from llama_index.prompts.prompts import SimpleInputPrompt
from llama_index.llms import HuggingFaceLLM
from transformers import AutoTokenizer, AutoModelForCausalLM
from llama_index import SimpleDirectoryReader
from llama_index import VectorStoreIndex
from llama_index.retrievers import VectorIndexRetriever

import nest_asyncio
import Agent.utils.ReadUtils as ru
import prompt.AgentPrompt as Prompt
import prompt.Interaction as InterPrompt
from Agent.utils import ReadUtils
import pandas as pd
# llamaindex的openai agent实现

model_path = "/yuanzichen/HF/Llama2ChatHF"

nest_asyncio.apply()

def multiply(a: int, b: int) -> int:
    """Multiple two integers and returns the result integer"""
    return a * b


multiply_tool = FunctionTool.from_defaults(fn=multiply)

def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b


add_tool = FunctionTool.from_defaults(fn=add)

def get_tokenizer_model():
    """
    # Create tokenizer
    tokenizer = AutoTokenizer.from_pretrained(name, cache_dir='./model/')

    # Create model
    model = AutoModelForCausalLM.from_pretrained(name, cache_dir='./model/'
                            , torch_dtype=torch.float16, 
                            rope_scaling={"type": "dynamic", "factor": 2}, load_in_8bit=True)
    """
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path).eval()

    return tokenizer, model


tokenizer, model = get_tokenizer_model()
device = torch.device("cuda")
model.to(device)


# Throw together the query wrapper
query_wrapper_prompt = SimpleInputPrompt("{query_str} [/INST]")

class AIAgent:
    def __init__(
        self,
        model,
        system_prompt,
        query_wrapper_prompt,
        tools: Sequence[BaseTool] = [],
        chat_history: List[ChatMessage] = [],
    ) -> None:
        
        self._model = model
        self._tools = {tool.metadata.name: tool for tool in tools}
        self._chat_history = chat_history
        self._system_prompt = system_prompt
        self._query_wrapper_prompt = query_wrapper_prompt

        self._llm = HuggingFaceLLM(context_window=8192,
                        max_new_tokens=512,
                        system_prompt=self._system_prompt,
                        query_wrapper_prompt=self._query_wrapper_prompt,
                        model=self._model,
                        tokenizer=tokenizer)


    def get_history(self) -> List:
        return self._chat_history

    def update_history(self, message) -> List:
        return self._chat_history.append(message)
    
    def reset(self) -> None:
        self._chat_history = [] 

    def chat(self, message: str) -> str:
        chat_history = self.get_history()
        chat_history.append(ChatMessage(role="user", content=message))

        tools = [
            tool.metadata.to_openai_tool() for _, tool in self._tools.items()
        ]

        ai_message = self._llm.chat(chat_history, tools=tools).message
        additional_kwargs = ai_message.additional_kwargs

        self.update_history(ai_message)
    
        tool_calls = ai_message.additional_kwargs.get("tool_calls", None)
        # parallel function calling is now supported
        if tool_calls is not None:
            for tool_call in tool_calls:
                function_message = self._call_function(tool_call)
                chat_history.append(function_message)
                ai_message = self._llm.chat(chat_history).message
                chat_history.append(ai_message)

        return ai_message.content

    def _call_function(self, tool_call: dict) -> ChatMessage:
        id_ = tool_call.id
        function_call = tool_call.function
        tool = self._tools[function_call.name]
        output = tool(**json.loads(function_call.arguments))
        print(f"> Calling tool: {function_call.name}")
        return ChatMessage(
            name=function_call.name,
            content=str(output),
            role="tool",
            additional_kwargs={
                "tool_call_id": id_,
                "name": function_call.name,
            },
        )
    


if __name__ == "__main__":

    # Create a system prompt 
    system_prompt = """<s>[INST] <<SYS>>
    [Role Definition]
    You excel at role-playing. Imagine you are an expert hired by a user to explore a movie recommendation system. \
    Your responsibility is to explore and analyze the user's movie viewing preferences based on their browsing history data.
    [Task Description: Portrait Generation]
    Upon initiation of this task, you will be provided with a unique identifier, {user_id}, alongside a \
    comprehensive {history} of movies that the user has interacted with. 
    
    Deep Dive Analysis: Analyze the user's movie browsing {history} to spot trends in genre preferences, viewing frequency,\
    and rating patterns. Aim to create a detailed profile of the user's movie tastes.

    Synthesis and Strategy: Use your analysis to form a personalized recommendation plan. This includes suggesting movies \
    that fit the user's known preferences and introducing new genres or films that match the identified patterns in \
    their viewing habits.<</SYS>>
    """
    path = "/yuanzichen/serendipity_sac2018/processed/updated_movies.csv"
    #item = ru.test(path, 1, [12, 99, 222])

    #items = ru.Dict2String(item)


    user = """
User ID: 1

Emotional Resonance: The user tends to seek movies that elicit a range of emotions, including excitement, drama, romance, and comedy. They may enjoy movies with complex, multi-threaded narratives that keep them engaged and invested in the story.

Narrative Preferences: The user prefers narratives that are character-driven and focus on the personal growth and development of the characters. They may enjoy stories that explore themes of heroism, justice, and personal transformation.

Thematic Exploration: The user consistently engages with movies that explore themes of love, relationships, and personal identity. They may be interested in stories that delve into the complexities of human emotions and the challenges of navigating different social and cultural contexts

User ID: 2

Emotional Resonance: The user typically seeks movies that offer excitement, adventure, and comedy. They enjoy stories that make them laugh and provide a sense of escapism.

Narrative Preferences: The user favors complex, multi-threaded narratives with intricate plotting and unexpected twists. They enjoy stories that are engaging and challenging to follow.

Thematic Exploration: The user consistently engages with themes of personal growth, exploration, and heroism. They are interested in stories that showcase characters overcoming obstacles and achieving their goals.

Visual and Aesthetic Preferences: The user appreciates unique visual storytelling and cinematography, particularly in comedies. They enjoy movies with vibrant colors, creative camera angles, and memorable visual moments.
"""

    movie = """
- Movie ID: 1
- Title: The Shawshank Redemption
- Appeal: High overall appeal and audience reception, with a timeless classic status
- Key Attributes:
+ Genre: Drama, Crime, Thriller
+ Themes: Hope, redemption, human spirit
+ Storytelling Quality: Engaging and well-paced narrative with a strong focus on character development
- Core Audience:
+ Emotional Resonance: Viewers who enjoy movies that elicit a range of emotions, including drama, romance, and comedy
+ Narrative Preferences: Characters-driven stories with complex, multi-threaded narratives
+ Thematic Exploration: Themes of love, relationships, personal identity, and personal growth

"""
    path_item = "/yuanzichen/LlamaChat/data/serendipity_sac2018/processed/updated_movies.csv"
    path_user = "/yuanzichen/LlamaChat/data/serendipity_sac2018/answers.csv"


    item = pd.read_csv(path_item)
    user = pd.read_csv(path_user)

    ids = [1, 11, 21]
    #user_history = ReadUtils.User2History(user, item)
    items = ReadUtils.MultiItemInfoReader(ids, item)

    # tool怎么用，暂时不会我看看怎么搞

    # 实例化两个AIAgent
    agent1 = AIAgent(
        model=model,
        system_prompt=Prompt.IAgentPrompt.system_prompt,
        query_wrapper_prompt=query_wrapper_prompt,
        tools=[multiply_tool, add_tool])

    
    user_input = Prompt.IAgentPrompt.init_prompt
    response1 = agent1.chat(user_input)
    print("agent1聊天代理的回应:", response1)

    for i in items:
        user_input = Prompt.IAgentPrompt.start_prompt.format(i)
        response1 = agent1.chat(user_input)
        print("agent1聊天代理的回应:", response1)


"""
    while True:
        user_input = input("请输入您对agent1的问题或对话内容: ")

        if user_input.lower() == 'exit':
            break

        if user_input.lower() == 'reset':
            agent1.reset()
            continue

        if user_input.lower() == 'start':
            #user_input = Prompt.UAgentPrompt.start_prompt + items
            user_input = Prompt.IAgentPrompt.init_prompt
        
        if user_input.lower() == 'evaluate':
            #user_input = InterPrompt.InteractionPrompt.EG_interaction_prompt.format(user, movie)
            user_input = Prompt.IAgentPrompt.start_prompt.format(item)
        

        response1 = agent1.chat(user_input)
        print("agent1聊天代理的回应:", response1)
"""
    




    # 使用第一个agent生成一个故事
    #response = agent1.chat("I am bored now, tell me a story")

    # 使用第一个agent的输出作为第二个agent的输入

    #query = "Give me the summary of this story"

    #filled_template = f"query:{query}, response:{response}"

   # response2 = agent2.chat(filled_template)


