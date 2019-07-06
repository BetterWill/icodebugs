import urllib
import requests
from pyquery import PyQuery as pq
from pymongo import MongoClient
import os
from hashlib import md5
from multiprocessing.pool import Pool


def get_page(offset, referer):
    param = {
        'include': 'data[*].is_normal,admin_closed_comment,reward_info,is_collapsed,annotation_action,annotation_detail,collapse_reason,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled,is_recognized,paid_info;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics',
        'limit': '20',  # 限制当页显示的回答数，知乎最大20
        'offset': offset,  # 偏移量
        'platform': 'desktop',
        'sort_by': 'default',
    }
    headers = {
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
        'Referer': referer,  # 问题的 url 地址
        'x-requested-with': 'fetch',
    }
    base_URL = 'https://www.zhihu.com/api/v4/questions/297715922/answers?include='  # 基础 url 用来构造请求url
    url = base_URL + urllib.parse.urlencode(param)  # 构造请求地址
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        print('请求失败')
        return None


def get_answer(json):
    for answer in json['data']:
        answer_info = {}
        # 获取作者信息
        author_info = answer['author']
        author = {}
        author['follower_count'] = author_info['follower_count']  # 作者被关注数量
        author['headline'] = author_info['headline']  # 个性签名
        author['name'] = author_info['name']  # 昵称
        author['index_url'] = author_info['url']  # 主页地址
        # 获取回答信息
        voteup_count = answer['voteup_count']  # 赞同数
        comment_count = answer['comment_count']  # 评论数
        # 解析回答内容
        content = pq(answer['content'])  # content 内容为 xml 格式的网页，用pyquery解析
        imgs_url = []
        imgs = content('figure noscript img').items()
        for img_url in imgs:
            imgs_url.append(img_url.attr('src'))  # 获取每个图片地址
        # 获取回答内容引用的其他相似问题
        question_info = content('a').items()
        questions = {}
        for que in question_info:
            url = que.attr('href')
            question = que.text()
            questions['url'] = question + ' ' + url  # 其他相似问题标题及地址
        # 字典映射存储回答信息
        answer_info['author'] = author
        answer_info['voteup_count'] = voteup_count
        answer_info['comment_count'] = comment_count
        answer_info['imgs_url'] = imgs_url
        answer_info['questions'] = questions
        yield answer_info  # yield 关键字把函数变成迭代器


# 存储在mongoDB
# client = MongoClient(host='localhost')
# print(client)
# db = client['zhihu']
# collection = db['zhihu']
# def save_to_mongodb(answer_info):
#     if collection.insert(answer_info):
#         print('已存储一条回答到MongoDB')

def save_to_img(imgs_url, author_name, base_path):
    path = base_path + author_name
    if not os.path.exists(path):  # 判断路径文件夹是否已存在
        os.mkdir(path)

        for url in imgs_url:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    img_path = '{0}/{1}.{2}'.format(path,
                                                    md5(response.content).hexdigest(), 'jpg')  # 以图片的md5字符串命名防止重复图片
                    if not os.path.exists(img_path):
                        with open(img_path, 'wb') as jpg:
                            jpg.write(response.content)
                    else:
                        print('图片已存在，跳过该图片')
            except requests.ConnectionError:
                print('图片链接失效，下载失败，跳过该图片')
        print('已保存答主：' + author_name + ' 回答内容的所有图片')


def main(offset):
    path = 'A:\Temp\zhihu\\'  # 指定图片存储路径
    json = get_page(offset, "https://www.zhihu.com/question/297715922")  # referer 地址，如果有需要可以根据获取的其他相似问题，继续抓取其他问题的图片。
    for answer in get_answer(json):
        # save_to_mongodb(answer)
        save_to_img(answer['imgs_url'], answer['author']['name'], path)


START = 0  # 开始
END = 40  # 结束
if __name__ == "__main__":
    pool = Pool()  # 线程池
    groups = [i * 20 for i in range(START, END)]  # 偏移量每次增大20
    pool.map(main, groups)
    pool.close()
    pool.join()
