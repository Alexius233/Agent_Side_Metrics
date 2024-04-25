import json
from typing import Sequence, List

from llama_index.llms import ChatMessage
from llama_index.tools import BaseTool, FunctionTool
from llama_index.prompts.prompts import SimpleInputPrompt
from llama_index.llms import HuggingFaceLLM

from llama_index import SimpleDirectoryReader
from llama_index import VectorStoreIndex
from llama_index.retrievers import VectorIndexRetriever

import nest_asyncio

# llamaindex的openai agent实现

nest_asyncio.apply()


class AIAgent:
    def __init__(
        self,
        model,
        tokenizer,
        system_prompt: str,
        query_wrapper_prompt,
        context_window: int,
        max_new_tokens: int,
        tools: Sequence[BaseTool] = [],
        chat_history: List[ChatMessage] = [],   # 用 Chatmessage.context应该能找出来
    ) -> None:
        
        self._model = model
        self._tokenizer = tokenizer
        self._tools = {tool.metadata.name: tool for tool in tools}
        self._chat_history = chat_history
        self._system_prompt = system_prompt
        self._query_wrapper_prompt = SimpleInputPrompt(query_wrapper_prompt)
        self._contex_window = context_window
        self._max_new_tokens = max_new_tokens

        self._llm = HuggingFaceLLM(context_window=self._contex_window,
                        max_new_tokens=self._max_new_tokens,
                        system_prompt=self._system_prompt,
                        query_wrapper_prompt=self._query_wrapper_prompt,
                        model=self._model,
                        tokenizer=self._tokenizer)


    def get_history(self) -> List:
        return self._chat_history

    def update_history(self, message: str, role: str) -> List:
        
        """
        role类型:

        SYSTEM = "system"
        USER = "user"
        ASSISTANT = "assistant"
        FUNCTION = "function"
        TOOL = "tool"
        CHATBOT = "chatbot"

        """

        return self._chat_history.append(ChatMessage(role=role, content=message))
    
    def reset(self) -> None:
        self._chat_history = [] 

    def chat(self, message: str) -> str:
        # chat的时候要制定message

        chat_history = self.get_history()
        chat_history.append(ChatMessage(role='user', content=message))
        tools = [
            tool.metadata.to_openai_tool() for _, tool in self._tools.items()
        ]
        ai_message = self._llm.chat(chat_history, tools=tools).message    # 这个.meaasge是ChatMessage类型，role是assistant
        additional_kwargs = ai_message.additional_kwargs

        chat_history.append(ai_message)
    
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
    


