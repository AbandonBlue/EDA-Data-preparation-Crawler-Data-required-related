import requests
import json


def get_html(url: str):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                             'AppleWebKit/537.36 (KHTML, like Gecko)'
                             'Chrome/75.0.3770.100 Safari/537.36'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()     # 如果請求有問題，直接發生錯誤
    resp.encoding = resp.apparent_encoding  # 正確編碼以顯示網頁，損失部分性能
    return resp.text


def get_info(text):
    shoes = json.loads(text)
    # print(shoes)
    return shoes