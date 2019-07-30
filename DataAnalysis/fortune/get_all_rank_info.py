from multiprocessing.pool import Pool
import requests, pyquery, json, os, logging
import pandas as pd

logging.basicConfig(level=logging.DEBUG)


def get_xhr_url(url):
    base_url = 'https://content.fortune.com/wp-json/irving/v1/data/franchise-search-results?list_id='

    try:
        response = requests.get(url)
        if response.status_code == 200:
            source = pyquery.PyQuery(response.text)
            script = source('head script').filter('[type="application/ld+json"]')
            doc = json.loads(script.text())
            id = doc.get('identifier')
            return base_url + str(id)
    except requests.ConnectionError:
        print('请求失败')
        return None


def get_response(xhr_url, referer):
    response = requests.get(xhr_url)
    if response.status_code == 200:
        return response.text
    else:
        print('失败：' + referer)


def parse_page(result):
    result = json.loads(result)[1]
    if result.get('items'):
        items = result.get('items')
        rank_info = []
        for company in items:
            company = company.get('fields')
            cmn = []
            for item in company:
                v = list(dict(item).values())[-1]
                cmn.append(v)
            rank_info.append(cmn)
        return rank_info


def save_csv(res_info, year, col):
    global PATH
    path = PATH + '\\fortune\\'
    if not os.path.exists(path):
        os.mkdir(path)
    fortune = pd.DataFrame(data=res_info, columns=col)
    fortune.to_csv(path + year + '.csv', index=False)
    print('已保存' + year + '年世界五百强信息，路径:' + path)


def get_columns(result):
    col = []
    items = json.loads(result)[1].get('items')
    for i in items[1].get('fields'):
        col.append(list(dict(i).values())[-2])
    return col


def main(year):
    url = 'https://fortune.com/global500/' + str(year) + '/search/'
    xhr_url = get_xhr_url(url)
    result = get_response(xhr_url, url)
    res_info = parse_page(result)
    columns = get_columns(result)
    save_csv(res_info, str(year), columns)


PATH = 'A:\Temp'
START_YEAR = 1995
END_YEAR = 2019
# 线程池
if __name__ == '__main__':
    pool = Pool()
    groups = [year for year in range(START_YEAR, END_YEAR + 1)]
    pool.map(main, groups)
    pool.close()
    pool.join()
