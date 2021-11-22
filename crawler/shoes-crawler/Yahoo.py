
import requests
import time
import random
import re
from bs4 import BeautifulSoup
import save
import odbc_fucntion


def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                             'AppleWebKit/537.36 (KHTML, like Gecko)'
                             'Chrome/75.0.3770.100 Safari/537.36'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()  # 如果請求有問題，直接發生錯誤
    resp.encoding = resp.apparent_encoding  # 正確編碼以顯示網頁，損失部分性能
    return resp.text


def crawl_shoes(page, gender, mail_list):
    # 因為tag裡面滿多雜訊的，字符串切割需要比較清楚，用.strip()以及.split()去做切割

    # 前置作業
    try:
        url = 'https://tw.buy.yahoo.com/category/31407672?flc=%E9%81%8B%E5%8B%95%E9%9E%8B%2F%E6%88%' \
              'B6%E5%A4%96%E7%99%BB%E5%B1%B1%E9%9E%8B&pg={}'.format(page)
        if gender == 'women':
            url = 'https://tw.buy.yahoo.com/search/product?p=%E9%81%8B%E5%8B%95%E5%A5%B3%E9%9E%8B&pg={}'.format(page)
        soup = BeautifulSoup(get_html(url), 'html.parser')
        shoes = soup.find_all('li', 'BaseGridItem__grid___2wuJ7 imprsn BaseGridItem__multipleImage___37M7b')
        brands = ['adidas', 'nike', 'under', 'new', 'puma', 'reebok']
        insert_data = set()

        for shoe in shoes:
            brand = shoe.find('span', 'BaseGridItem__title___2HWui').text.split(' ')[0].lower()
            if brand in brands:   # 我要的brand
                if brand == 'new':
                    brand = 'NB'
                elif brand == 'under':
                    brand = 'UA'
                else:
                    brand = brand.capitalize()
            else:
                continue
            product_url = shoe.find('a', 'BaseGridItem__content___3LORP')['href']
            product_id = re.search('gdid=\w+', product_url)
            price = ''

            if product_id:
                product_id = 'Yahoo_' + product_id.group()[5:]
            else:
                product_id = 'Yahoo_' + re.search('\d{7}', product_url).group()

            image_url = shoe.find('div', 'Square_wrap_hQgrV').find('img', 'SquareImg_img_2gAcq')['srcset'].strip().split(' ')[0]
            product_name = shoe.find('span', 'BaseGridItem__title___2HWui').text
            price_middle = shoe.find('em', 'BaseGridItem__price___31jkj')
            image_name = product_id + '.jpg'

            if price_middle:
                price = re.search('[0-9,]+', price_middle.text).group()
            else:
                price = re.search('[0-9,]+', shoe.find('span', 'BaseGridItem__price___31jkj').text).group()
            insert_data = (product_id,
                           product_name,
                           '',
                           'TWD',
                           price.replace(',', ''),
                           image_name,
                           product_url
                           )
            print(insert_data)
            ################################################################################################
            # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
            database_price = odbc_fucntion.odbc_select_data(
                "SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format(brand, insert_data[0]))
            if database_price:  # 如果資料庫有這筆資料
                if database_price[0] != insert_data[4]:
                    odbc_fucntion.odbc_update_data(brand, (insert_data[4], insert_data[0]),
                                                   (insert_data[4], insert_data[1]))  # 記得兩個都要更新
                    # 郵件清單更新
                    # 帳戶
                    account_ids = odbc_fucntion.odbc_select_data(
                        "SELECT [AccountId] FROM Goods.dbo.CollectionTable WHERE [Name]='{}'".format(insert_data[1]))
                    if account_ids:
                        gmails = []
                        # 求郵件地址
                        for account_id in account_ids:
                            # return 的是tuple所以後面要加[0], m代表郵件地址
                            m = odbc_fucntion.odbc_select_data(
                                "SELECT [Email] FROM Goods.dbo.CeneralMenucrs WHERE [AccountId]='{}'".format(
                                    account_id))[0]
                            gmails.append(m)
                        # 將所有郵件的內容裝起來,以列表裝起來,要寄信時再解析
                        for gmail in gmails:
                            if mail_list != dict():
                                mail_list[gmail].append({insert_data[1]: '{}, {} -> {}\n{}'.format(insert_data[1],
                                                                                                   database_price[0],
                                                                                                   insert_data[4],
                                                                                                   insert_data[6])})
                            else:
                                mail_list[gmail] = [{insert_data[1]: '親愛的顧客您好,您的追蹤商品更新如下:\n\n{}, {} -> {}\n{}'.format(
                                    insert_data[1], database_price[0], insert_data[4], insert_data[6])}]

            else:
                odbc_fucntion.odbc_insert_data(brand, insert_data)
                save.save(image_url, 'Yahoo_{}'.format(brand), image_name)
            #################################################################################################

        time.sleep(random.uniform(0.5, 2.5))

        if insert_data == set():
            return -1
    except Exception as e:
        print(e)

# 跑起來!!!!


""""""
def main(mail_list):
    # for i in range(1, 10000):
    #     print(i)
    #     if crawl_shoes(i, 'women', mail_list) == -1:
    #         break
    for i in range(1, 10000):
        print(i)
        if crawl_shoes(i, 'men', mail_list) == -1:
            break


if __name__ == '__main__':
    main({})