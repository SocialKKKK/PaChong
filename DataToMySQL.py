import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# MySQL数据库连接信息
mysql_user = 'root'
mysql_password = 'root'
mysql_host = 'localhost'
mysql_port = 3306
mysql_db = 'ZhiLianJob'

# 创建MySQL数据库连接引擎
engine = create_engine(f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}')

# 城市和对应的编号
cities = {
    '上海': 538, '北京': 530, '广州': 763, '深圳': 765, '天津': 531,
    '武汉': 736, '西安': 854, '成都': 801, '南京': 635, '杭州': 653,
    '重庆': 551, '厦门': 682
}

# 循环遍历每个城市的CSV文件并导入到MySQL数据库
for city in cities.keys():
    file_name = f'F:/python_code/PaChong/智联招聘数据/{city}.csv'
    try:
        # 读取CSV文件到DataFrame
        data = pd.read_csv(file_name)
        print(f"正在处理城市: {city}")
        print(data.head())

        # 将DataFrame写入MySQL数据库
        data.to_sql(name=city, con=engine, if_exists='replace', index=False, schema=None)
        print(f"{city}的数据已成功导入。")
    except FileNotFoundError:
        print(f"文件未找到: {file_name}")
    except pd.errors.EmptyDataError:
        print(f"文件中没有数据: {file_name}")
    except SQLAlchemyError as e:
        print(f"导入{city}数据时出错: {e}")
    except Exception as e:
        print(f"处理{city}数据时发生意外错误: {e}")

print("所有数据已成功导入到MySQL数据库。")
