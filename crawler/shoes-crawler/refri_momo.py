import requests
from bs4 import BeautifulSoup
import json

def get_html(url: str, verify=None):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                             'AppleWebKit/537.36 (KHTML, like Gecko)'
                             'Chrome/75.0.3770.100 Safari/537.36'}
    # verify 是用來處理SSL，但原理還不是太懂
    resp = requests.get(url, headers=headers, verify=verify)   # , verify=False
    resp.raise_for_status()     # 如果請求有問題，直接發生錯誤
    resp.encoding = resp.apparent_encoding  # 正確編碼以顯示網頁，損失部分性能
    return resp.text

# pre
url = "https://tw.buy.yahoo.com/category/4387514"
soup = BeautifulSoup(get_html(url), 'html.parser')

# parameter
item_count = 1
item_urls = []

# scrap item urls
# for item_list in soup.find_all(name='ul', class_='gridList'):
#     # print(item_list)
#     for item in item_list.find_all(name='li', class_='BaseGridItem__grid___2wuJ7 BaseGridItem__multipleImage___37M7b'):
#         item_url = item.find(name='a')['href']
#         item_urls.append(item_url)
#         print(item_count, item_url)
#         print('='*100)
#         item_count += 1

# for url in item_urls:
#     soup = BeautifulSoup(get_html(url), 'html.parser')
#     res = soup.find('div', 'ProductHtmlDetail__dangerouslyContent___2S9JU ProductHtmlDetail__spec___32i-F')
#     print(res)
#     break

url = 'https://tw.buy.yahoo.com/graphql'

# 參考, 做到這邊
# https://tw.buy.yahoo.com/gdsale/Panasonic%E5%9C%8B%E9%9A%9B%E7%89%8C-610L-%E7%B4%9A%E8%AE%8A%E9%A0%BB4%E9%96%80%E9%9B%BB%E5%86%B0-8221899.html
# yahoo
# request payload問題
params = {'accept': '*/*',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
'Cache-Control': 'no-cache',
'Connection': 'keep-alive',
'Content-Length': '179',
'content-type': 'application/json',
'Cookie': 'APID=UPd329e0c5-9639-11e9-a004-0addf49d5636; B=9tf7pddegm75u&b=3&s=27; A1=d=AQABBFOhM14CEBswNH_tFuFhz__U7GNukNIFEgEBAQEYal5TX73Lb2UB_SMAAAcIvhwLXWv5vJ4&S=AQAAAh_7sfYusAPgtipvgtR06i0; A3=d=AQABBFOhM14CEBswNH_tFuFhz__U7GNukNIFEgEBAQEYal5TX73Lb2UB_SMAAAcIvhwLXWv5vJ4&S=AQAAAh_7sfYusAPgtipvgtR06i0; GUC=AQEBAQFeahhfU0IgTwSd; _ga=GA1.3.343528155.1583927287; _gid=GA1.3.1001738359.1583927287; APIDTS=1583929074; _gat=1; A1S=d=AQABBFOhM14CEBswNH_tFuFhz__U7GNukNIFEgEBAQEYal5TX73Lb2UB_SMAAAcIvhwLXWv5vJ4&S=AQAAAh_7sfYusAPgtipvgtR06i0&j=WORLD',
'Host': 'tw.buy.yahoo.com',
'Origin': 'https://tw.buy.yahoo.com',
'Pragma': 'no-cache',
'Referer': 'https://tw.buy.yahoo.com/gdsale/Panasonic%E5%9C%8B%E9%9A%9B%E7%89%8C-610L-%E7%B4%9A%E8%AE%8A%E9%A0%BB4%E9%96%80%E9%9B%BB%E5%86%B0-8221899.html',
'Sec-Fetch-Dest': 'empty',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Site': 'same-origin',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36}'}
data = {"operationName":'null',"variables":{"id":"8221899"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"16613f5be475ac4508776982965ab9b1608af24b47e7f58d0bad85563b077405"}}}
res = requests.post(url, params, json.dumps(data))
print(res)