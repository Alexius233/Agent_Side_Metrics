import sys
sys.path.append('/yuanzichen/LlamaChat')
from Agent.MultiAgentCon import LLMEvalAgents

from Agent.utils import ReadUtils
import yaml
import pandas as pd
import re


path_item = "/yuanzichen/LlamaChat/data/serendipity_sac2018/processed/updated_movies.csv"
path_user = "/yuanzichen/LlamaChat/data/serendipity_sac2018/answers.csv"


item = pd.read_csv(path_item)
user = pd.read_csv(path_user)


user_history = ReadUtils.User2History(user, item)


ids = [1, 11, 21]
#user_history = ReadUtils.User2History(user, item)
items = ReadUtils.MultiItemInfoReader(ids, item)

print(items)



# 读取YAML配置文件
with open('/yuanzichen/LlamaChat/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

llm_eval_agents = LLMEvalAgents(**config)

llm_eval_agents.Chat(user_history, items)

