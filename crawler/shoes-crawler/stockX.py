

import requests
import json
import time
import random


def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                             'AppleWebKit/537.36 (KHTML, like Gecko)'
                             'Chrome/75.0.3770.100 Safari/537.36'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()  # 如果請求有問題，直接發生錯誤
    resp.encoding = resp.apparent_encoding  # 正確編碼以顯示網頁，損失部分性能
    return resp.text


def get_info(text):
    info = json.loads(text)
    return info


def crawl_stockx(page):
    # 由網址可以找出pn為頁數，更改即可由json檔撈出我們要的資料
    # url = 'https://stockx.com/api/browse?_tags=adidas&page={}&productCategory=sneakers'.format(page)  # 頁碼處特別處理
    # url = 'https://stockx.com/api/browse?_tags=air%20jordan&productCategory=sneakers&page={}'.format(page)
    # url = 'https://stockx.com/api/browse?_tags=nike&productCategory=sneakers&page={}'.format(page)
    # url = 'https://stockx.com/api/browse?_tags=puma&productCategory=sneakers&page={}'.format(page)
    # url = 'https://stockx.com/api/browse?_tags=new%20balance&productCategory=sneakers&page={}'.format(page)
    # url = 'https://stockx.com/api/browse?_tags=reebok&productCategory=sneakers&page={}'.format(page)
    url = 'https://stockx.com/api/browse?_tags=under%20armour&productCategory=sneakers&page={}'.format(page)

    # 結構圖
    """
        Products    -> brand, gender, *media                -> imageUrl
                        retailPrice, title(品名、前面含牌子)
                        market                              -> lowestAsk(價格)
        Pagination  -> total, page, nextPage,currentPage(url)
    """

    # 前置作業
    # 從json轉成python的dict檔案，再由此取出需要的資料
    page_content = get_info(get_html(url))
    total_pages = page_content['Pagination']['total'] // page_content['Pagination']['limit'] + 1
    current_page = page_content['Pagination']['page']
    products = {}
    count = 1

    for product in page_content['Products']:
        products[count] = dict()
        products[count]['記數'] = count
        products[count]['品牌'] = product['brand']
        products[count]['品名'] = product['title']
        products[count]['幣別'] = '$'
        try:
            products[count]['價錢'] = [product['retailPrice'], product['market']['lowestAsk']]
        except:
            products[count]['價錢'] = []
            print('沒有任何價格')
        products[count]['圖片'] = product['media']['thumbUrl']
        products[count]['URL'] = '?'
        count += 1

    print(products)
    time.sleep(random.uniform(0.5, 2.5))

    if products == {}:
        return -1


for i in range(1, 100):
    if crawl_stockx(i) == -1:
        break
    print('down')