import requests, json, time
from typing import List, Dict
import pandas as pd
from urllib.parse import urlencode
from multiprocessing.pool import Pool

movie_id = {'1061156738': 1, '1061112026': 2, '1061115893': 3, '1061118825': 4, '1061124294': 5, '1061127128': 6,
            '1061129956': 7, '1061138103': 8, '1061158257': 9, '1061163269': 10, '1061197140': 11, '1061201689': 12,
            '1062795534': 13, '1062795536': 14, '1062807618': 15, '1062807619': 16, '1066480126': 17, '1066468697': 18,
            '1066165020': 19, '1066259359': 20, '1067105825': 21, '1067435975': 22, '1067446903': 23, '1067415987': 24,
            '1067415158': 25, '1069080226': 26, '1070240468': 27, '1070243186': 28, '1070321169': 29, '1070248357': 30,
            '1071064780': 31, '1071125061': 32, '1072769719': 33, '1072779089': 34, '1072761780': 35, '1073412465': 36,
            '1073394590': 37, '1073412466': 38, '1074956629': 39, '1074957642': 40, '1074955533': 41, '1074961953': 42,
            '1074955980': 43, '1075631338': 44, '1075656698': 45, '1075660995': 46, '1076454253': 47, '1076449851': 48}
headers = {
    'Sec-Fetch-Mode': 'no-cors',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
}

error_bullet, error_comment = [], []
path_bullet = r'A:\Temp\bullet_'
path_comment = r'A:\Temp\comment_'


def get_bullet_page(iid: str, mat: int) -> List:
    base_url = 'https://service.danmu.youku.com/list?'
    param = {
        'mat': mat,
        'iid': iid,
    }
    url = base_url + urlencode(param)
    try:
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            response = json.loads(response.text)
            if response.get('result'):
                return list(response.get('result'))
            else:
                return None
        else:
            error_bullet.append((iid, mat))
            print(url + ' 错误码：' + response.status_code)
    except requests.ConnectionError:
        error_bullet.append((iid, mat))
        print('请求失败')


def parse_bullet(page: List[Dict]) -> List[Dict]:
    res = []
    for item in page:
        tmp = dict()
        tmp['uid'] = item['uid']
        tmp['mat'] = item['mat']
        tmp['createtime'] = item['createtime']
        tmp['voteUp'] = item['extFields']['voteUp']
        tmp['content'] = item['content']
        res.append(tmp)
    return res


def save_bullet(res: List[Dict], num: int) -> None:
    pd.DataFrame(res, index=([num] * len(res))).to_csv(path_bullet + str(num) + '.csv', encoding='utf_8_sig', )
    print('已存储第{num}集弹幕'.format(num=num))


def get_comment_page(iid: str, currentPage: int) -> List[Dict]:
    base_url = 'https://p.comments.youku.com/ycp/comment/pc/commentList?'
    param = {
        'app': '100-DDwODVkv',
        'objectId': iid,
        'listType': 0,
        'currentPage': currentPage,
        'sign': '072c4ac1a0e2aaf812d8e994943e5a5d',
        'time': '1566131118',
    }
    url = base_url + urlencode(param)
    try:
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            response = json.loads(response.text)
            if response.get('data'):
                return list(response.get('data').get('comment'))
            else:
                return None
        else:
            error_bullet.append((iid, currentPage))
            print(url + ' 错误码：' + response.status_code)
    except requests.ConnectionError:
        error_bullet.append((iid, currentPage))
        print('请求失败')


def parse_comment(page: List[Dict]) -> List[Dict]:
    res = []
    for item in page:
        tmp = dict()
        tmp['uid'] = item['userId']
        user = item['user']
        tmp['userLevel'] = user['userLevel']
        tmp['userName'] = user['userName']
        if user['vipInfo']:
            tmp['vipGrade'] = user['vipInfo']['vipGrade']
        else:
            tmp['vipGrade'] = 0
        tmp['createtime'] = item['createTime']
        tmp['voteUp'] = item['upCount']
        tmp['downCount'] = item['downCount']
        tmp['content'] = item['content']
        res.append(tmp)
    return res


def save_comment(res: List[Dict], num: int) -> None:
    pd.DataFrame(res, index=([num] * len(res))).to_csv(path_comment + str(num) + '.csv', encoding='utf_8_sig', )
    print('已存储第{num}集评论'.format(num=num))


def check_comment_size(iid: str, num: int) -> int:
    base_url = 'https://p.comments.youku.com/ycp/comment/pc/commentList?'
    param = {
        'app': '100-DDwODVkv',
        'objectId': iid,
        'listType': 0,
        'currentPage': 1,
        'sign': '072c4ac1a0e2aaf812d8e994943e5a5d',
        'time': '1566131118',
    }
    url = base_url + urlencode(param)
    while True:
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            response = json.loads(response.text)
            if response.get('data'):
                return response.get('data').get('totalPage')
        print('第{num}集评论页数获取失败，5s后重新发起请求'.format(num=num))
        time.sleep(5)


def get_bullet(iid: str) -> None:
    mat, res = 0, []
    num = movie_id[iid]
    while True:
        page = get_bullet_page(iid, mat)
        if not page:
            time.sleep(5)
            print('第{num}集的第{mat}分钟弹幕获取失败，5s后重新发起请求'.format(num=num, mat=mat + 1))
            continue
        tmp = parse_bullet(page)
        res += tmp
        if len(tmp) < 355: break
        mat += 1
    save_bullet(res, num)


def get_comment(iid: str) -> None:
    res, current_page = [], 1
    num = movie_id[iid]
    totalPage = check_comment_size(iid, num)
    while current_page <= totalPage:
        page = get_comment_page(iid, current_page)
        if page:
            tmp = parse_comment(page)
            current_page += 1
            res += tmp
        else:
            print('第{num}集的第{cp}页评论获取失败，5s后重新发起请求'.format(num=num, cp=current_page))
            time.sleep(5)
    save_comment(res, num)


def main(iid: str) -> None:
    get_bullet(iid)
    get_comment(iid)


if __name__ == '__main__':
    main('1061124294')
    # pool = Pool()  # 线程池
    # groups = [i for i in movie_id.keys()]  # 偏移量每次增大20
    # pool.map(main, groups)
    # pool.close()
    # pool.join()
    # print('失败码：', error_bullet, error_comment)
