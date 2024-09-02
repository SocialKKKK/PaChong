import os
import re
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号#有中文出现的情况，需要u'内容'

citys = ['上海', '北京', '广州', '深圳', '天津', '武汉', '西安', '成都', '南京', '杭州', '重庆', '厦门']

# 辅助函数
def convert_to_numeric(value, unit):
    if unit == '千':
        return float(value) * 1000
    elif unit == '万':
        return float(value) * 10000
    else:
        return float(value)

# 数据清洗
def data_clear():
    for city in citys:
        file_name = f'F:/python_code/PaChong/智联招聘数据/{city}.csv'
        df = pd.read_csv(file_name)
        for j in range(df.shape[0]):
            s = df.loc[j, 'salary']
            if isinstance(s, str) and '-' in s:
                a, b = s.split('-')
                a_value = re.findall(r'\d+\.?\d*', a)[0]
                b_value = re.findall(r'\d+\.?\d*', b)[0]
                a_unit = '千' if '千' in a else '万' if '万' in a else ''
                b_unit = '千' if '千' in b else '万' if '万' in b else ''
                a_numeric = convert_to_numeric(a_value, a_unit)
                b_numeric = convert_to_numeric(b_value, b_unit)
                df.at[j, 'salary'] = (a_numeric + b_numeric) / 2
            else:
                df.at[j, 'salary'] = None

        os.remove(file_name)
        df.to_csv(file_name,index=False, encoding='utf-8')

# 各个城市职位数量条形图:
def citys_jobs():
    job_num = list()
    for i in citys:
        file_name = f'F:/python_code/PaChong/智联招聘数据/{i}.csv'
        df = pd.read_csv(file_name)
        job_num.append(df.shape[0])

    # 创建 DataFrame
    df = pd.DataFrame(list(zip(citys, job_num)), columns=['City', 'Job Count'])
    df = df.sort_values('Job Count', ascending=False)
    x = list(df['City'])
    y = list(df['Job Count'])

    # 创建图表
    fig, ax = plt.subplots(dpi=200, figsize=(12, 8))
    bars = ax.bar(x, y, alpha=0.8)
    ax.set_title('该职位在全国主要城市的数量分布')
    ax.set_xlabel('城市')
    ax.set_ylabel('职位数量')
    ax.set_ylim(0, max(y) + 100)  # 动态设置 y 轴范围

    # 添加数据标签
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    # 保存图表
    output_path = './static/images/该职位在全国主要城市的数量分布.jpg'
    plt.savefig(output_path)
    plt.show()

# 不同城市薪资分布条形图：
def citys_salary():
    y = []
    for city in citys:
        file_name = f'F:/python_code/PaChong/智联招聘数据/{city}.csv'
        df = pd.read_csv(file_name, index_col=0)
        y0 = df['salary'].mean()
        y.append(round(y0 / 1000, 1))  # 将薪资单位转换为千

    # 创建 DataFrame
    df_salary = pd.DataFrame(list(zip(citys, y)), columns=['City', 'Average Salary'])
    df_salary = df_salary.sort_values('Average Salary', ascending=False)

    # 提取 x 和 y 轴数据
    x = df_salary['City'].tolist()
    y = df_salary['Average Salary'].tolist()

    # 创建图表
    fig, ax = plt.subplots(dpi=200, figsize=(12, 8))
    bars = ax.bar(x, y, alpha=0.8)
    ax.set_title('该职位在一些主要城市的薪资分布（单位：千）')
    ax.set_xlabel('城市')
    ax.set_ylabel('平均薪资（千）')
    ax.set_ylim(0, max(y) + 2)  # 动态设置 y 轴范围

    # 添加数据标签
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    # 保存图表
    output_path = './static/images/该职位在一些主要城市的薪资分布.jpg'
    plt.savefig(output_path)
    plt.show()

# 该职位岗位总体薪资的分布
def salary_distribute():
    salary_list = []
    for city in citys:
        file_name = f'F:/python_code/PaChong/智联招聘数据/{city}.csv'
        df = pd.read_csv(file_name)
        salary_list += list(df['salary'])

    salarys = [round(s / 1000, 1) for s in salary_list if not pd.isnull(s)]
    mean = np.mean(salarys)

    # 创建图表
    plt.figure(dpi=200, figsize=(12, 8))
    sns.histplot(salarys, kde=True, color='blue', linewidth=0)
    plt.axvline(mean, color='r', linestyle=":")
    plt.text(mean, plt.ylim()[1] * 0.9, '平均薪资: %.1f千' % mean, color='r', horizontalalignment='center', fontsize=15)
    plt.xlim(0, 50)
    plt.xlabel('薪资分布（单位：千）')
    plt.ylabel('频数')
    plt.title('该职位整体薪资分布')

    # 保存图表
    output_path = './static/images/该职位整体薪资分布.jpg'
    plt.savefig(output_path)
    plt.show()

# 学历要求分布饼图
def education_distribute():
    table = pd.DataFrame()
    for city in citys:
        file_name = f'F:/python_code/PaChong/智联招聘数据/{city}.csv'
        df = pd.read_csv(file_name, index_col=0)
        table = pd.concat([table, df])

    education_counts = pd.value_counts(table['education'])
    education_counts = education_counts.sort_values(ascending=False)
    x = list(education_counts.index)
    y = list(education_counts)

    # 动态生成 explode 参数
    explode = [0.1] * len(y)  # 将所有的 explode 设置为相同的值，这里是 0.1

    fig, ax = plt.subplots(dpi=200, figsize=(10, 6))
    ax.pie(y, labels=x, autopct='%.1f%%', explode=explode)  # explode 必须与 y 的长度一致
    ax.set_title('该职位对学历要求的占比')
    ax.axis('equal')  # 确保饼图是一个正圆

    # 保存图表
    output_path = './static/images/该职位对学历要求的占比.jpg'
    plt.savefig(output_path)
    plt.show()

def wordfrequence():
    table = pd.DataFrame()
    for city in citys:
        file_name = f'F:/python_code/PaChong/智联招聘数据/{city}.csv'
        df = pd.read_csv(file_name, index_col=0)
        table = pd.concat([table, df])
    l1 = list(table['ability'])
    l2 = list()
    for i in range(len(l1)):
        if not pd.isnull(l1[i]):
            l2.append(l1[i])
    words = ''.join(l2)

    cloud = WordCloud(
        font_path='C:/Windows/Fonts/simhei.ttf',  # 设置字体文件获取路径，默认字体不支持中文
        background_color='white',  # 设置背景颜色  默认是black
        max_words=20,  # 词云显示的最大词语数量
        random_state=1,  # 设置随机生成状态，即多少种配色方案
        collocations=False,  # 是否包括词语之间的搭配，默认True，可能会产生语意重复的词语
        width=1200, height=900  # 设置大小，默认图片比较小，模糊
    ).generate(words)
    plt.figure(dpi=200)
    plt.imshow(cloud)  # 该方法用来在figure对象上绘制传入图像数据参数的图像
    plt.axis('off')  # 设置词云图中无坐标轴
    # plt.savefig('F:/python_code/PaChong/DataAnalysisResult/技能关键词频统计.jpg')
    plt.savefig('./static/images/该职位技能关键词频统计.jpg')
    plt.show()

if __name__ == "__main__":
    print("=====================# 数据清洗 #=====================")
    data_clear()
    print("============# 各个城市该职位数量条形图 #============")
    citys_jobs()
    print("=================# 不同城市薪资分布条形图 #==============")
    citys_salary()
    print("================# 该职位岗位总体薪资的分布 #============")
    salary_distribute()
    print("===============# 该职位对学历要求的分布 #===========")
    education_distribute()
    print("===================# 技能关键词频统计 #==================")
    wordfrequence()

