import pandas as pd
import numpy as np  # 用于处理NaN
import csv

# 路径可能需要调整为实际路径
file_path_detail = '/yuanzichen/serendipity_sac2018/movie_detail.csv'
file_path_raw = '/yuanzichen/serendipity_sac2018/cleared_movies.csv'

#file_path_raw = '/path/to/your/raw/csv/file.csv'

"""
# 尝试用utf-8编码打开文件
output_path = '/yuanzichen/serendipity_sac2018/cleared_movies.csv'  # 输出文件的路径

with open(file_path_raw, mode='rb') as infile, open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    while True:
        try:
            # 逐行读取原始文件
            line = infile.readline()
            # 如果读到文件末尾，跳出循环
            if not line:
                break
            # 尝试使用utf-8解码
            decoded_line = line.decode('utf-8')
            # 解码成功，使用csv模块处理解码后的行
            reader = csv.reader([decoded_line])
            for row in reader:
                # 将解码成功的行写入到新文件
                writer.writerow(row)
        except UnicodeDecodeError:
            print("Skipped a line due to decoding error.")
            continue
"""

# 读取CSV文件
df_detail = pd.read_csv(file_path_detail)
df_raw = pd.read_csv(file_path_raw, encoding='utf-8')





# 为df_raw添加一个空的'summary'列
df_raw['summary'] = 'NaN'

# 遍历df_raw中的每一行
for index, row in df_raw.iterrows():
    movieid = row['movieId']  # 假设movieid是第一列，列名为'movieid'
    
    # 在df_detail中找到匹配的movieid行
    match = df_detail[df_detail['movie_id'] == movieid]
    
    # 如果找到匹配的行，提取summary并更新到df_raw的对应行
    if not match.empty:
        df_raw.at[index, 'summary'] = match.iloc[0]['summary']

# 现在df_raw已经更新，包含了匹配到的summary或NaN（如果未匹配）

# 删除所有以"Unnamed:"开头的列
df_raw = df_raw.loc[:, ~df_raw.columns.str.startswith('Unnamed:')]
df_raw = df_raw.loc[:, ~df_raw.columns.str.startswith(',')]

# 将更新后的df_raw写入新的CSV文件
output_path = '/yuanzichen/serendipity_sac2018/updated_movies.csv'  # 保存在可访问的路径
df_raw.to_csv(output_path, index=False)

