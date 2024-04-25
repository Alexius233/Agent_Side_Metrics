from TextAgent import AIAgent
from Agent.GenAgent import GenAgent
from typing import Sequence, List
from llama_index.llms import ChatMessage
from llama_index.tools import BaseTool


def aggregate_response(u_agent: GenAgent, i_agent: GenAgent, template: str):

    UserPartResponse = u_agent.format_history
    ItemPartResponse = i_agent.format_history

    query = template.format(UserPartResponse, ItemPartResponse)

    return query 
