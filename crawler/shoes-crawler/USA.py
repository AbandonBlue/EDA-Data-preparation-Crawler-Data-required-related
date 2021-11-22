import requests
import re
import time
import random
import json
from bs4 import BeautifulSoup
import odbc_fucntion
import save


def get_html(url: str):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                             'AppleWebKit/537.36 (KHTML, like Gecko)'
                             'Chrome/75.0.3770.100 Safari/537.36'}
    resp = requests.get(url, headers=headers)
    # resp.raise_for_status()     # 如果請求有問題，直接發生錯誤
    resp.encoding = resp.apparent_encoding  # 正確編碼以顯示網頁，損失部分性能
    return resp.text


def get_info(text):
    shoes = json.loads(text)
    # print(shoes)
    return shoes


def crawl_reebok(page, gender, mail_list):

    # 第一個JSON裡面竟然沒有價格....
    # 有點麻煩，要做2段式查詢，
    # 從第一個JSON得到型號id，
    # 再往第二個JSON得到該型號的所有資訊
    try:
        url = 'https://www.reebok.com/api/search/query?sitePath=us&query=shoes&start={}'.format((page-1)*48)
        if gender == 'women':
            url = 'https://www.reebok.com/api/search/taxonomy?sitePath=us&query=women-shoes&start={}'.format((page-1)*48)

        # 從json轉成python的dict檔案，再由此取出需要的資料
        page_content1 = get_info(get_html(url))

        # 第一個JSON(48個商品)
        #   itemList -> items -> items(此頁商品資訊集)    -> displayName(Name), productId(可能會用到), link(需要prefix)
        #                                                 -> image -> src (Images)

        # 第二個JSON(單一商品)
        # price取得Price
        # 前置作業
        url_prefix = 'https://www.reebok.com'

        # 資料抓出與放入
        for shoe in page_content1['itemList']['items']:
            product_id = 'USA_Reebok_' + shoe['productId']
            product_name = shoe['displayName']
            api_url = 'https://www.reebok.com/api/search/product/{}?sitePath=us'.format(shoe['productId'])
            image_url = shoe['image']['src']
            image_name = product_id + '.jpg'

            page_content2 = get_info(get_html(api_url))  # magic
            price = page_content2['price']
            product_url = url_prefix + shoe['link']

            insert_data = (product_id,
                           product_name,
                           '',
                           'USD',
                           price,  # 有的沒放...
                           image_name,
                           product_url
                           )
            print(insert_data)
            ################################################################################################
            # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
            database_price = odbc_fucntion.odbc_select_data(
                "SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('Reebok', insert_data[0]))
            if database_price:  # 如果資料庫有這筆資料
                if database_price[0] != insert_data[4]:
                    odbc_fucntion.odbc_update_data('Reebok', (insert_data[4], insert_data[0]),
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
                odbc_fucntion.odbc_insert_data('Reebok', insert_data)
                save.save(image_url, 'USA_Reebok', image_name)
            #################################################################################################

        # 等待時間
        time.sleep(random.uniform(0.5, 2.5))
        if insert_data == set():
            return -1
    except Exception as e:
        print(e)


def crawl_nb(page, gender, mail_list):
    # 會用try except是因為竟然有沒有放價格的鞋款
    # 效率問題需要解決
    try:
        url = 'https://www.newbalance.com/men/shoes/all-shoes/?sz=24&format=ajax&start={}&' \
              'refinements=true&refinements=true&format=ajax'.format((page-1)*24)  # 頁碼處特別處理
        if gender == 'women':
            url = 'https://www.newbalance.com/search?q=shoes&prefn1=genderAndAgeGroupCombo&sz=12&' \
                  'format=ajax&start={}&prefv1=Women&refinements=true&refinements=true&format=ajax'.format((page-1)*12)

        # 前置作業
        soup = BeautifulSoup(get_html(url), 'html.parser')
        shoes = soup.find_all('div', class_='product product-tile')
        pattern = '[0-9.]+'  # 解析價格
        end_page = 17 if gender == 'men' else 12

        # 資料抓出與放入
        for shoe in shoes:
            product_id = 'USA_NB_' + shoe['data-product-id']
            product_name = shoe.find('p', 'product-name').text.strip()
            product_url = shoe.find('a', 'product-image')['href']
            price = re.search(pattern, shoe.find('div', 'product-pricing').text.strip()).group()
            soup_image = BeautifulSoup(get_html(product_url), 'html.parser')
            image_url = soup_image.find('picture').find('img')['src']
            image_name = product_id + '.jpg'

            insert_data = (product_id,
                           product_name,
                           '',
                           'USD',
                           price,    # 有的沒放...
                           image_name,
                           product_url
                           )
            print(insert_data)
            ################################################################################################
            # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
            database_price = odbc_fucntion.odbc_select_data(
                "SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('NB', insert_data[0]))
            if database_price:  # 如果資料庫有這筆資料
                if database_price[0] != insert_data[4]:
                    odbc_fucntion.odbc_update_data('NB', (insert_data[4], insert_data[0]),
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
                odbc_fucntion.odbc_insert_data('NB', insert_data)
                save.save(image_url, 'USA_NB', image_name)
            #################################################################################################

        # 等待時間,效率差,不等待
        if page == end_page:
            return -1
    except Exception as e:
        if page == end_page:
            return -1
        print(e)


def crawl_puma(page, gender, mail_list):
    try:
        url = 'https://us.puma.com/on/demandware.store/Sites-NA-Site/en_US/Search-UpdateGrid?cgid=21000&start={}&sz=36'.format(34+(page-1)*36)  # 頁碼處特別處理
        if gender == 'women':
            url = 'https://us.puma.com/on/demandware.store/Sites-NA-Site/en_US/Search-UpdateGrid?cgid=11000&start={}&sz=36'.format(34+(page-1)*36)

        # 前置作業
        soup = BeautifulSoup(get_html(url), 'html.parser')
        shoes = soup.find_all('div', class_='col-6 col-sm-4 col-md-3')
        pattern = '[^$]+'   # 解析價格
        url_prefix = 'https://us.puma.com'
        insert_data = set()

        # 資料抓出與放入
        for shoe in shoes:

            product_id = 'USA_Puma_' + shoe.find('div', 'grid-tile')['data-masterpid']
            product_name = shoe.find('a', 'link').text
            image_url = shoe.find('img', 'tile-image')['src']
            image_name = product_id + '.jpg'

            insert_data = (product_id,
                           product_name,
                           '',
                           'USD',
                           re.search(pattern, shoe.find('span', 'value').text).group(),
                           image_name,
                           url_prefix + shoe.find('img', 'tile-image').parent['href']
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
                save.save(image_url, 'USA_Puma', image_name)
            #################################################################################################

        # 等待時間
        time.sleep(random.uniform(0.5, 2.5))
        if insert_data == set():
            return -1
    except Exception as e:
        print(e)


def crawl_adidas(page, gender, mail_list):
    # 網頁動態生成的頻率不同步，導致我無法解析一次到位，
    # 先以初始網頁抓取id，
    # 再用id進入json抓取所有資訊，但效率不好。

    # 很直接用get傳遞頁碼參數
    try:
        url = 'https://www.adidas.com/us/{}-lifestyle-shoes?start={}'.format(gender, (page-1)*48)  # 頁碼處特別處理

        # 前置作業
        soup = BeautifulSoup(get_html(url), 'html.parser')
        shoes = soup.find_all('div', class_='col-s-6 col-m-4 col-l-8 col-xl-6 no-gutters plp-column___3gy6t')
        url_prefix = 'https://www.adidas.com/'
        product_ids = {}
        insert_data = set()

        # 資料抓出與放入
        for shoe in shoes:
            product_name = shoe.find('div', 'gl-product-card__name gl-label gl-label--m').text
            product_id = (re.search('/.{6}\.html', shoe.find('a')['href']).group()[1:7])
            product_ids[product_id] = product_name

        # 進入各個json檔
        """"""
        for id, name in product_ids.items():
            page_content = get_info(get_html('https://www.adidas.com/api/search/product/{}?sitePath=us'.format(id)))
            product_id = 'USA_Adidas_' + id
            image_name = product_id + '.jpg'
            image_url = page_content['image']['src']

            insert_data = (product_id,
                           name,
                           '',
                           'USD',
                           page_content['price'],
                           image_name,
                           url_prefix + page_content['link']
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
                save.save(image_url, 'USA_Adidas', image_name)
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
        print(i)
        if crawl_adidas(i, 'men', mail_list) == -1:
            break
    for i in range(1, 10000):
        print(i)
        if crawl_adidas(i, 'women', mail_list) == -1:
            break


    # *puma
    """"""
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_puma(i, 'women', mail_list) == -1:
            break
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_puma(i, 'men', mail_list) == -1:
            break


    # *NB
    """"""
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_nb(i, 'women', mail_list) == -1:
            break
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_nb(i, 'men', mail_list) == -1:
            break


    # reebok
    """"""
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_reebok(i, 'men', mail_list) == -1:
            break
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_reebok(i, 'women', mail_list) == -1:
            break

if __name__ == '__main__':
    main({})