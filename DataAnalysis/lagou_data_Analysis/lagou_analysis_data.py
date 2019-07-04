import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import jieba
from scipy.misc import imread

plt.rcParams['font.sans-serif'] = ['SimHei']  # 替换sans-serif字体显示中文
plt.rcParams['axes.unicode_minus'] = False  # 解决坐标轴负数的负号显示问题

path = 'A:\Temp\\'  # 指定爬取的数据存储路径

lagou_data = pd.read_csv(path+'lagou_algorithm_data.csv')
pattern = '\d+'  # 正则表达式-匹配连续数字

# 统计每个公司的平均经验要求
lagou_data['平均经验'] = lagou_data['经验'].str.findall(
    pattern)  # findall查找所有['经验']下的数字字符串
avg_work_year = []
for i in lagou_data['平均经验']:
    if len(i) == 0:  # 长度为0则意为着没有数字，既工作经验为'不限'、'应届毕业生'等等,即没有工作经验要求
        avg_work_year.append(0)
    else:  # 匹配的是两个数值的工作经验区间 几年到几年，，
        year_list = [int(j) for j in i]  # 得到每一个数转为int型
        avg_year = sum(year_list)/2  # 求工作区间的平均值
        avg_work_year.append(avg_year)
lagou_data['平均经验'] = avg_work_year

# 统计每个公司给出的平均工资
lagou_data['平均工资'] = lagou_data['工资'].str.findall(pattern)
avg_salary = []
for k in lagou_data['平均工资']:
    salary_list = [int(n) for n in k]
    salary = sum(salary_list)/2
    avg_salary.append(salary)
lagou_data['平均工资'] = avg_salary

# 绘制工资频率直方图
plt.hist(lagou_data['平均工资'], alpha=0.8, color='steelblue')
plt.xlabel('工资/千元')
plt.ylabel('频数')
plt.title("算法工程师平均工资直方图")
plt.savefig(path+'lagou_algorithm_salary.jpg')  # 指定保存路径
plt.show()

plt.hist(lagou_data['平均经验'], alpha=0.8, color='greenyellow')
plt.xlabel('经验/年')
plt.ylabel('频数')
plt.title("算法工程师平均工作经验直方图")
plt.savefig(path+'lagou_algorithm_work_year.jpg')  # 指定保存路径
plt.show()
# 绘制学历要求饼图
count = lagou_data['学历'].value_counts()
plt.pie(count, labels=count.keys(), shadow=True, autopct='%2.2f%%')
plt.savefig(path+'lagou_algorithm_education.jpg')
plt.show()

# 绘制福利待遇词云
color_mask = imread(path+'china_map.jpg')
strs = ''
for line in lagou_data['福利']:
    strs += line  # 连接所有字符串
cut_strs = ' '.join(jieba.cut(strs))  # 使用中文分词jieba，将字符串分割成列表
word_cloud = WordCloud(font_path='C:\Windows\Fonts\微软雅黑\msyh.ttc', mask=color_mask, background_color='white').generate(
    cut_strs)  # 指定显示字体防止乱码
word_cloud.to_file(path+'lagou_algorithm_wordcloud.jpg')
plt.imshow(word_cloud)
plt.show()
