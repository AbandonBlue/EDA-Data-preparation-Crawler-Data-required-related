import requests
import re
import time
import random
import json
import save
import odbc_fucntion
from bs4 import BeautifulSoup


def get_html(url: str, verify=None):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                             'AppleWebKit/537.36 (KHTML, like Gecko)'
                             'Chrome/75.0.3770.100 Safari/537.36'}
    # verify 是用來處理SSL，但原理還不是太懂
    resp = requests.get(url, headers=headers, verify=verify)   # , verify=False
    resp.raise_for_status()     # 如果請求有問題，直接發生錯誤
    resp.encoding = resp.apparent_encoding  # 正確編碼以顯示網頁，損失部分性能
    return resp.text


def get_info(text):
    shoes = json.loads(text)
    # print(shoes)
    return shoes


def crawl_nb():
    # 形式跟其他網站不太一樣,有空再弄
    pass


def crawl_ua(page, mail_list):
    try:
        # 圖片有些存不下來
        url = 'https://www.underarmour.tw/sys/navigation/loading?searchWord=%E9%9E%8B&cf=&qf' \
              '=&nav=&sortStr=salesprice_desc&pf=&pageNumber={}&_=1563757517807'.format(page)
        soup = BeautifulSoup(get_html(url), 'html.parser')
        shoes = soup.find_all('div', 'list-item col-12-3')
        insert_data = set()

        # prefix
        url_prefix = 'https://www.underarmour.tw'

        for shoe in shoes:
            product_url = url_prefix + shoe.find('a', 'good-txt')['href']
            product_id = 'TW_UA_' + shoe.find('a', 'active')['id']
            image_url = shoe.find('img', 'imgUrl1')['hidden_url']
            product_name = shoe.find('a', 'good-txt').text
            price = re.search('[\d\.]+', str(shoe.find('p', 'good-price'))).group()
            image_name = product_id + '.png'

            insert_data = (product_id,
                           product_name,
                           '',
                           'TWD',
                           price,
                           image_name,
                           product_url
                           )
            print(insert_data)
            ################################################################################################
            # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
            database_price = odbc_fucntion.odbc_select_data(
                "SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('UA', insert_data[0]))
            if database_price:  # 如果資料庫有這筆資料
                if database_price[0] != insert_data[4]:
                    odbc_fucntion.odbc_update_data('UA', (insert_data[4], insert_data[0]),
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
                odbc_fucntion.odbc_insert_data('UA', insert_data)
                save.save(image_url, 'TW_UA', image_name)
            #################################################################################################

        if insert_data == set():
            return -1
    except Exception as e:
        print(e)


def crawl_puma(page, mail_list):
    try:
        url = 'http://www.pumastore.com.tw/product/search-puma-page-{}.html'.format(page)
        soup = BeautifulSoup(get_html(url), 'html.parser')
        shoes = soup.find('div', 'content').find_all('li')
        insert_data = set()

        for shoe in shoes:
            product_url = shoe.find('div', 'pimage').find('a')['href']
            product_id = 'TW_Puma_' + re.search('\d{5,8}\.html', product_url).group()[1:-6]
            image_url = shoe.find('div', 'pimage').find('img')['src']
            product_name = shoe.find('div', 'pname').find('a').text
            price = shoe.find('div', 'pprice').find('span').text.replace(',', '').replace('$', '')
            image_name = product_id + '.jpg'

            insert_data = (product_id,
                           product_name,
                           '',
                           'TWD',
                           price,
                           image_name,
                           product_url
                           )
            print(insert_data)
            ################################################################################################
            # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
            database_price = odbc_fucntion.odbc_select_data(
                "SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('Puma', insert_data[0]))
            if database_price:  # 如果資料庫有這筆資料
                if database_price[0] != insert_data[4]:
                    odbc_fucntion.odbc_update_data('Puma', (insert_data[4], insert_data[0]),
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
                odbc_fucntion.odbc_insert_data('Puma', insert_data)
                save.save(image_url, 'TW_Puma', image_name)
            #################################################################################################

        if insert_data == set():
            return -1
    except Exception as e:
        print(e)


def crawl_nike(page, gender, mail_list):
    try:
        url = 'https://store.nike.com/html-services/gridwallData?country=AU&lang_locale' \
              '=en_GB&gridwallPath=mens-shoes/7puZoi3&pn={}'.format(page)
        if gender == 'women':
            url = 'https://store.nike.com/html-services/gridwallData?country=AU&lang_locale' \
                  '=en_GB&gridwallPath=womens-shoes/7ptZoi3&pn={}'.format(page)

        # 從json轉成python的dict檔案，再由此取出需要的資料
        page_content = get_info(get_html(url))

        # 資料抓出與放入

        for shoe in page_content['sections'][0]['items']:
            price = str(shoe['rawPrice'])
            product_url = shoe['pdpUrl']
            image_url = shoe['spriteSheet']
            product_name = shoe['title']
            product_id = 'TW_Nike_' + re.search('-shoe(s)?-.{6}/?', product_url).group()[5:-1]
            image_name = product_id + '.jpg'

            insert_data = (product_id,
                           product_name,
                           shoe['subtitle'],
                           'USD',
                           price,
                           image_name,
                           product_url
                           )
            print(insert_data)
            ################################################################################################
            # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
            database_price = odbc_fucntion.odbc_select_data(
                "SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('Nike', insert_data[0]))
            if database_price:  # 如果資料庫有這筆資料
                if database_price[0] != insert_data[4]:
                    odbc_fucntion.odbc_update_data('Nike', (insert_data[4], insert_data[0]),
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
                odbc_fucntion.odbc_insert_data('Nike', insert_data)
                save.save(image_url, 'TW_Nike', image_name)
            #################################################################################################
        # 等待時間
        time.sleep(random.uniform(0.5, 2.5))
        if insert_data == set():
            return -1
    except Exception as e:
        print(e)
        return -1


def crawl_adidas(page, mail_list):
    try:
        url = 'https://www.adidas.com.tw/openchan-b/api/v1/mall/search?sortType=3' \
              '&page={}&keywords=%E9%9E%8B&pageCount=48'.format(page)

        # 從json轉成python的dict檔案，再由此取出需要的資料
        page_content = get_info(get_html(url, verify=False))

        #  result -> productDetailList -> cpro_price, cpdt_name, picpath,
        #                               -> product_tags  -> tags -> tag_name(Gender)
        #                               -> cpdt_num(id由此進一步取得網址)

        insert_data = set()

        # 資料抓出與放入
        for shoe in page_content['result']['productDetailList']:
            price = shoe['cpro_price']
            product_url = 'https://www.adidas.com.tw/product/{}?article=EG1506' \
                                     '&sizeindex=550'.format(shoe['cpdt_num'])
            image_url = shoe['picpath']
            product_name = shoe['cpdt_name']
            product_id = 'TW_Adidas_' + str(shoe['cpdt_num'])
            image_name = product_id + '.jpg'

            insert_data = (product_id,
                           product_name,
                           '',
                           'TWD',
                           price,  # 有的沒放...
                           image_name,
                           product_url
                           )
            print(insert_data)
            ################################################################################################
            # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
            database_price = odbc_fucntion.odbc_select_data(
                "SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('Adidas', insert_data[0]))
            if database_price:  # 如果資料庫有這筆資料
                if database_price[0] != insert_data[4]:
                    odbc_fucntion.odbc_update_data('Adidas', (insert_data[4], insert_data[0]),
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
                odbc_fucntion.odbc_insert_data('Adidas', insert_data)
                save.save(image_url, 'TW_Adidas', image_name)
            #################################################################################################

        # 等待時間
        time.sleep(random.uniform(0.5, 2.5))
        if insert_data == set():
            return -1
    except Exception as e:
        print(e)

def main(mail_list):
    # *adidas
    """"""
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_adidas(i, mail_list) == -1:
            break

    """"""
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_nike(i, 'men', mail_list) == -1:
            break
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_nike(i, 'women', mail_list) == -1:
            break

    """"""
    for i in range(1, 7):
        print('page:%s' % i)
        if crawl_puma(i, mail_list) == -1:
            break

    """"""
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_ua(i, mail_list) == -1:
            break

if __name__ == '__main__':
    main({})