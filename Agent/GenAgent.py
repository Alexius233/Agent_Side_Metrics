from Agent.TextAgent import AIAgent
from typing import Sequence, List
from llama_index.llms import ChatMessage
from llama_index.tools import BaseTool


class GenAgent(AIAgent):
    def __init__(
        self,
        model,
        tokenizer,
        system_prompt,
        Agent_name,
        query_wrapper_prompt,
        context_window,
        max_new_tokens,
        tools: Sequence[BaseTool] = [],
        chat_history: List[ChatMessage] = [],
    ) -> None:
        
        super().__init__(
            model,
            tokenizer,
            system_prompt,
            query_wrapper_prompt,
            context_window,
            max_new_tokens,
            tools,
            chat_history,
        )

        self.agent_name = Agent_name
        self.agent_role = []
        self.history_prompt = "agent_name: {}, role_description: {}, response: {}"
        self.format_history = [] # 这个是给另一个agent提取这一轮response用的, 用prompt加到query
    
    
    def StoreHistory(self, message):

        SingleResponse = self.history_prompt.format(self.agent_name, self.agent_role, message)
        self.format_history.append(SingleResponse)
    
    def ResetHistory(self):
        self.format_history = []

    def chat(self, message: str) -> str:

        self.ResetHistory()

        chat_history = self.get_history()
        chat_history.append(ChatMessage(role="user", content=message))
        tools = [
            tool.metadata.to_openai_tool() for _, tool in self._tools.items()
        ]

        ai_message = self._llm.chat(chat_history, tools=tools).message
        additional_kwargs = ai_message.additional_kwargs

        chat_history.append(ai_message)

        self.StoreHistory(ai_message.content)

        tool_calls = ai_message.additional_kwargs.get("tool_calls", None)
        # parallel function calling is now supported
        if tool_calls is not None:
            for tool_call in tool_calls:
                function_message = self._call_function(tool_call)
                chat_history.append(function_message)
                ai_message = self._llm.chat(chat_history).message
                chat_history.append(ai_message)

        return ai_message.content




    
