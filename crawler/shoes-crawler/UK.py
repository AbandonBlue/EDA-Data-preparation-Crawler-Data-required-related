import requests
import re
import time
import random
import json
from bs4 import BeautifulSoup
import threading


def get_html(url: str):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                             'AppleWebKit/537.36 (KHTML, like Gecko)'
                             'Chrome/75.0.3770.100 Safari/537.36'}
    # verify 是用來處理SSL，但原理還不是太懂
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()     # 如果請求有問題，直接發生錯誤
    resp.encoding = resp.apparent_encoding  # 正確編碼以顯示網頁，損失部分性能
    return resp.text


def get_info(text):
    shoes = json.loads(text)
    # print(shoes)
    return shoes


def crawl_nike(page, gender):
    url = 'https://store.nike.com/html-services/gridwallData?country=AU&lang_locale' \
          '=en_GB&gridwallPath=mens-shoes/7puZoi3&pn={}'.format(page)
    if gender == 'women':
        url = 'https://store.nike.com/html-services/gridwallData?country=AU&lang_locale' \
              '=en_GB&gridwallPath=womens-shoes/7ptZoi3&pn={}'.format(page)

    # 從json轉成python的dict檔案，再由此取出需要的資料
    page_content = get_info(get_html(url))

    #   sections -> [0] -> items -> [每個商品,從0開始] -> rawPrice, title, pdpUrl, spriteSheet(Images),
    #
    #

    # 前置作業
    products = {}
    count = 1

    # 資料抓出與放入
    if 'sections' in page_content.keys():
        for item in page_content['sections'][0]['items']:
            products[count] = dict()
            products[count]['Gender'] = gender
            products[count]['Brand'] = 'nike'
            products[count]['Name'] = item['title']
            products[count]['Currency'] = '$'
            products[count]['Price'] = item['rawPrice']
            #products[count]['Images'] = item['spriteSheet']
            #products[count]['URL'] = item['pdpUrl']

            count += 1

    # 看檔案有無問題
    print(products)

    # 等待時間
    time.sleep(random.uniform(0.5, 2.5))
    if products == {}:
        return -1


for i in range(1, 40):
    print('page:%s' %i)
    thread_nike_men = threading.Thread(target=crawl_nike, args=[i, 'men'])
    thread_nike_men.start()
    if crawl_nike(i, 'women') == -1:
        break