from transformers import AutoTokenizer, AutoModelForCausalLM
from llama_index.tools import BaseTool, FunctionTool
from Agent.GenAgent import GenAgent

def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiple two integers and returns the result integer"""
    return a * b


def get_tokenizer_model(model_path):

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)

    return tokenizer, model


multiply_tool = FunctionTool.from_defaults(fn=multiply)


add_tool = FunctionTool.from_defaults(fn=add)


def fill_query_template(query:str, agent: GenAgent, template: str):
    # 用来UI交互的query生成
    CounterpartResponse = agent.format_history
    query = template.format(query, CounterpartResponse)

    agent.ResetHistory()

    return query
