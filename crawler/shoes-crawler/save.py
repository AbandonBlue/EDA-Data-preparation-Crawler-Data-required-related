from urllib.request import urlretrieve
import os
import requests


def save(img_url, title, img_name, path=None):
    if img_url:
        if not (img_url.startswith('https:') or img_url.startswith('http:')):       # 可能有http，但暫時忽略
            img_url = 'https:' + img_url
        if not (img_name.endswith('.jpg') or img_name.endswith('.png')):            # 沒有處理好
            img_name += '.jpg'
        try:
            # os.chdir(r'C:\Users\aband\OneDrive\桌面\CMoney\期末專題\GoodsManager_TW_v3.1\UI\Content\images')
            # if not os.path.exists(title):
                # os.makedirs(title)
            # urlretrieve(img_url, os.path.join(title, img_name))  # 第一個參數為url網址,後者為合成路徑
            os.chdir(r'C:\Users\aband\OneDrive\桌面\CMoney\期末專題\GoodsManager_TW_v3.6(測試data+收藏與比價詳細)\UI\Content\images')
            urlretrieve(img_url, os.path.join(img_name))
        except Exception as e:
            print(e)


# 資料流的下載方式
def download_pic(image_url, file_path):
    r = requests.get(image_url, stream=True)
    with open(file_path, "wb") as file:
        for chunk in r.iter_content(chunk_size=32):
            file.write(chunk)

# 例子
# url = 'http://test.com/images/1803_android.jpg'
# filePath = "E://pics/1803.jpg"
# downloadPic(url,filePath)




