import pandas as pd

# 假设你的CSV文件路径
file_path = '/yuanzichen/serendipity_sac2018/answers.csv'
file_path_movie = '/yuanzichen/serendipity_sac2018/processed/movies_details_align.csv'

# 读取CSV文件
df = pd.read_csv(file_path)
df_movie = pd.read_csv(file_path_movie)

# 从df_movie中提取所有movieId到一个列表
movie_ids_in_movie_file = df_movie['movieId'].unique().tolist()


# 自定义n的值，例如查找至少有2个movieId在movies文件中也存在的组
n = 2
# 按userId分组
groups = df.groupby('userId')

# 初始化符合条件的组的数量
count = 0

# 遍历每个组
for group_name, group_data in groups:
    # 提取当前组的所有movieId
    movies_list = group_data['movieId'].unique().tolist()
    
    # 检查这些movieId中有多少个在df_movie中
    matches_count = sum(movie_id in movie_ids_in_movie_file for movie_id in movies_list)
    
    # 如果在df_movie中存在至少n个movieId，则增加计数
    if matches_count >= n:
        count += 1

print(count)
