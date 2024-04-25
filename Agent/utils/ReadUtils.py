import csv
import pandas as pd
from pandas import DataFrame
from pprint import pprint
import numpy as np

# 读一个csv成为dataframe
def FileReader(FilePath: str) -> DataFrame:

    df = pd.read_csv(FilePath) 

    return df

# 按行读取一个item的信息
def ItemInfoReader(ItemID: int, container: DataFrame) -> dict:

        # 找到匹配的行
    movie_row = container.loc[container['movieId'] == ItemID]
    
    # 如果没有找到匹配的行，返回None
    if movie_row.empty:
        return None
    
    # 提取所需的列信息
    movie_info = {
        'movieId': movie_row.iloc[0]['movieId'],
        'title': movie_row.iloc[0]['title'],
        'releaseDate': movie_row.iloc[0]['releaseDate'],
        'directedBy': movie_row.iloc[0]['directedBy'],
        'starring': movie_row.iloc[0]['starring'],
        'genres': movie_row.iloc[0]['genres'],
        'summary': movie_row.iloc[0]['summary'],
    }
    
    return movie_info

def MultiItemInfoReader(Items, container: DataFrame) -> dict:

    movie_infos = []
    for item in Items:
        movie_infos.append(ItemInfoReader(item, container))
    
    return movie_infos


# 把user和对应的历史读取出来
def History2Dict(UserID: int, ItemIDs: list, container: DataFrame) -> dict:

    Items = []

    for i in ItemIDs:
        item_info = ItemInfoReader(i, container)
        Items.append(item_info)

    UserHistory = {
        "user": UserID,
        "history": Items
    }

    return UserHistory


def Dict2String(UserHistory: dict) -> str:
    result_strings = []  # 用于存储格式化的字符串

    # 添加用户ID部分
    result_strings.append(f"User ID: {UserHistory['user']}")

    # 遍历历史记录
    history_items = UserHistory['history']
    for item in history_items:
        if item is not None:  # 确保项目信息不为空
            item_strings = [f"{key}: {value}" for key, value in item.items()]
            result_strings.append("\n".join(item_strings))
        else:
            continue
            # result_strings.append("Item info not found.")  # 项目信息为空时的处理

    # 将所有部分合并为一个字符串
    return "\n\n".join(result_strings)

# 从 dataset里sample一个数据
def User2History(UserContainer: DataFrame, ItemContainer: DataFrame) -> dict:

    grouped = UserContainer.groupby('userId')
    group_keys = list(grouped.groups.keys())
    # 随机选择一个组的键
    random_group = np.random.choice(group_keys)
    # 获取选中组的数据
    selected_group = grouped.get_group(random_group)

    UserId = selected_group['userId'].iloc[0]
    MovieIds = selected_group['movieId'].tolist()

    History = History2Dict(UserId, MovieIds, ItemContainer)
    History = Dict2String(History)
    
    return History




######################################################################
def test(path, id, items):
    df = FileReader(path)

    info = History2Dict(id, items, df)

    return info

#info = test(path, 13, [1, 11, 21])

#pprint(info)

# 假设 user_history 是上面函数的输出
user_history_example = {
    "user": 1,
    "history": [
        {
            'movieId': 101,
            'title': 'Example Movie',
            'releaseDate': '2021-01-01',
            'directedBy': 'Jane Doe',
            'starring': 'John Doe, Jane Smith',
            'genres': 'Drama, Comedy',
            'summary': 'This is an example summary.'
        },
        {
            'movieId': 102,
            'title': 'Another Movie',
            'releaseDate': '2022-02-02',
            'directedBy': 'John Smith',
            'starring': 'Doe Jane, Smith John',
            'genres': 'Action, Adventure',
            'summary': 'This is another example summary.'
        },
        None,  # 假设有一个项目信息未找到
        {
            'movieId': 103,
            'title': 'Yet Another Movie',
            'releaseDate': '2023-03-03',
            'directedBy': 'Diana Jones',
            'starring': 'Jane Doe, John Smith',
            'genres': 'Sci-Fi, Thriller',
            'summary': 'This is yet another example summary.'
        }
    ]
}

# 使用 dict_to_string 函数
#formatted_history = Dict2String(user_history_example)
#print(formatted_history)

