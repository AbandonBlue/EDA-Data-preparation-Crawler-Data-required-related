import requests
import re
import time
import random
import json
from bs4 import BeautifulSoup
import odbc_fucntion
import math
import save

# 此檔案目的: 查詢HK的各大品牌網站


# 傳送郵件地址、內容

def get_html(url: str):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                                 'AppleWebKit/537.36 (KHTML, like Gecko)'
                                 'Chrome/75.0.3770.100 Safari/537.36'}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()     # 如果請求有問題，直接發生錯誤
        resp.encoding = resp.apparent_encoding  # 正確編碼以顯示網頁，損失部分性能
        return resp.text
    except Exception as e:
        print(e)


def get_info(text):
    shoes = json.loads(text)
    # print(shoes)
    return shoes


def crawl_nb(page, gender, mail_list):
    # 因為網站的查詢方式，不能一次查詢所有鞋類
    # 有頁數問題，超過頁數參數輸入，會直接進入最後一頁
    # 官方有bug把女鞋一雙放到男鞋，造成key的問題。

    # 將清單載入

    try:
        # 標準作業流程
        url = 'https://www.newbalance.com.hk/zh/{}men/shoes?p={}'.format('', page) if \
            gender == 'men' else 'https://www.newbalance.com.hk/zh/{}men/shoes?p={}'.format('wo', page)
        soup = BeautifulSoup(get_html(url), 'html.parser')
        shoes = soup.find_all('div', 'product-item-info')
        MAX_NUMBER = re.search('[0-9]+', soup.find('span', 'base').text).group()
        PAGE = math.ceil(int(MAX_NUMBER) / 12)
        # 前置作業、找尋tag需要的東西，如regex、url_prefix
        # products = {}
        pattern = '[^HK$]+'
        for shoe in shoes:
            price = re.search(pattern, shoe.find('span', 'price').text)

            product_id = 'HK_NB_' + shoe.find('div', 'price-box price-final_price')['data-product-id']
            image_url = shoe.find('img', 'product-image-photo')['src']
            product_name = shoe.find('a', class_='product-item-link').text.strip()
            image_name = product_id + '.jpg'

            insert_data = (product_id,
                           product_name,
                           '',
                           'HKD',
                           price.group().split('.')[0],
                           image_name,
                           shoe.find('a')['href']
                           )
            print(insert_data)
            
            ################################################################################################
            # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
            database_price = odbc_fucntion.odbc_select_data("SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('NB', insert_data[0]))
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
                save.save(image_url, 'HK_NB', image_name)
            #################################################################################################

        time.sleep(random.uniform(0.5, 2.5))  # 等待時間
        if page == PAGE:
            return -1

    except Exception as e:
        print(e)
        return


def crawl_ua(page, mail_list):
    """
        遇到困難，快顯沒有圖片
        需要以抓到的網址進去，才可以抓，費工
        有效率問題
        """
    
    # 標準作業流程
    url = 'https://www.underarmour.tw/sys/navigation/loading?searchWord=%E9%9E%8B%E5%AD' \
          '%90&cf=&qf=&nav=&sortStr=&pf=&pageNumber={}&_=1562131504598'.format(page)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                             'AppleWebKit/537.36 (KHTML, like Gecko)'
                             'Chrome/75.0.3770.100 Safari/537.36'}
    soup = BeautifulSoup(get_html(url), 'html.parser')
    shoes = soup.find_all('div', 'list-item col-12-3')

    # 前置作業、找尋tag需要的東西，如regex、url_prefix
    url_prefix = 'https://www.underarmour.tw'
    pattern = '[^NT$]+'
    insert_data = set()
    # 解析html
    for shoe in shoes:
        resp_img = requests.get(url=url_prefix + (shoe.find('a', 'good-txt')['href']), headers=headers)
        soup_imgs = BeautifulSoup(resp_img.text, 'html.parser')

        price = re.search(pattern, shoe.find('p', 'good-price').text)

        product_id = 'HK_UA_' + re.search('p[0-9]{7}-[0-9]{3}', shoe.find('a', 'good-txt')['href']).group()
        image_url = soup_imgs.find_all('div', 'scroll-background-image')[1].find('a').find('img')['data-cloudzoom'].replace('zoomImage: ', '').strip("'")
        product_name = shoe.find('a', class_='good-txt').text
        image_name = product_id + '.png'

        insert_data = (product_id,
                       product_name,
                       '',
                       'HKD',
                       price.group().split('.')[0],
                       image_name,
                       url_prefix + shoe.find('a', 'good-txt')['href']
                       )
        
        print(insert_data)
        # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
        database_price = odbc_fucntion.odbc_select_data("SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('UA', insert_data[0]))
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
                            "SELECT [Email] FROM Goods.dbo.CeneralMenucrs WHERE [AccountId]='{}'".format(account_id))[0]
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
            save.save(image_url, 'HK_UA', image_name)

        

    time.sleep(random.uniform(0.5, 2.5))     # 等待時間
    if insert_data == set():
        return -1


def crawl_nike(page, mail_list):
    """
    https://www.nike.com.hk/search/list.json?ca=shoe&SearchPage=true&page=4
    改變page即可以找出想要的資料
    由開發者工具先找出XHR的動態封包
    其中點選copy選擇copy as fetch
    得到以下
    fetch("https://www.nike.com.hk/search/list.json?ca=shoe",
    {"credentials":"include","headers":{"accept":"*/*","accept-language":"zh-TW,zh;q=0.9,
    en-US;q=0.8,en;q=0.7","content-type":"application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with":"XMLHttpRequest"},"referrer":"https://www.nike.com.hk/search/list.json?ca=shoe",
    "referrerPolicy":"no-referrer-when-downgrade","body":"isSearchPage=true&page=2&order=","method":"POST","mode":"cors"});
    可知道其傳遞方法以及參數給予
    我就把'body'的參數加上網址
    試出想要的結果
    原理尚未完全懂，但已經可以實現了
    """

    # 標準作業流程
    try:
        url = 'https://www.nike.com.hk/search/list.json?ca=shoe&SearchPage=true&page={}'.format(page)

        soup = BeautifulSoup(get_html(url), 'html.parser')
        shoes = soup.find_all('li', 'style_liborder_new')

        # 前置作業、找尋tag需要的東西，如regex、url_prefix
        pattern = '[^HK$]+'
        url_prefix = 'https://www.nike.com.hk'
        insert_data = set()
        # 找tag
        for shoe in shoes:
            price = re.search(pattern, shoe.find('dd', id='oriPrice').text)

            image_url = shoe.find('dt', 'pro_hover_larim0 skul_spic').find('img')['lazy_src']
            product_url = url_prefix + shoe.find('a', 'product_list_name')['href']
            product_name = shoe.find('span', class_='up').text.strip(';').strip(r'\\')
            image_name = product_id + '.png'
            product_id = 'HK_Nike_' + shoe.find('dl', 'product_list_content')['code']
            product_price = price.group().replace(',', '')

            insert_data = (product_id,
                           product_name,
                           '',
                           'HKD',
                           product_price,
                           image_name,
                           product_url
                           )
            print(insert_data)
            ################################################################################################
            # 放入
            """"""
            # cmd_insert = "INSERT INTO Goods.dbo.Nike_Table(Id, Name, Style, Currency, Price, Images, URL)" \
            #              " VALUES (?, ?, ?, ?, ?, ?, ?)"


            # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
            database_price = odbc_fucntion.odbc_select_data("SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('Nike', insert_data[0]))
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
                save.save(image_url, 'HK_Nike', image_name)
            #################################################################################################

        time.sleep(random.uniform(0.5, 2.5))     # 等待時間
        if insert_data == set():
            return -1
    except Exception as e:
        print(e)


def crawl_reebok(page, mail_list):

    try:
        # 由網址可以找出pn為頁數，更改即可由json檔撈出我們要的資料
        url = 'https://www.reebok.hk/plp/waterfall.json?stick=&keyword=%E9%9E%8B&pn={}'.format(page)  # 頁碼處特別處理

        # 結構圖
        """
            returnObject    ->  view    ->  itemsListWithOutGroup   ->  code(Id), imageUrl, salePrice, subTitle(男女、種類), title(品名)
                                            totalPages
                                            currentPage
        """

        # 前置作業
        # 從json轉成python的dict檔案，再由此取出需要的資料
        page_content = get_info(get_html(url))
        total_pages = page_content['returnObject']['view']['totalPages']
        current_page = page_content['returnObject']['view']['currentPage']
        image_prefix = 'https://img.reebok.hk/resources/'
        product_id = ''

        for product in page_content['returnObject']['view']['itemsListWithOutGroup']:
            insert_data = set()
            if 'itemColorList' in product:
                product_id = 'HK_Reebok_' + product['code']
                image_name = product_id + '.png'

                insert_data = (product_id,
                               product['title'],
                               product['subTitle'],
                               'HKD',
                               str(product['salePrice']),
                               image_name,
                               'https://www.reebok.hk/item/{}'.format(product['code'])
                               )
                save.save(image_prefix + product['itemColorList'][0]['picUrl'], 'HK_Reebok', image_name)
            elif 'imageUrl' in product:
                product_id = 'HK_Reebok_' + product['code']
                image_name = product_id + '.png'

                insert_data = (product_id,
                               product['title'],
                               product['subTitle'],
                               'HKD',
                               str(product['salePrice']),
                               image_name,
                               'https://www.reebok.hk/item/{}'.format(product['code'])
                               )
                save.save(image_prefix + product['imageUrl'][0], 'HK_Reebok', image_name)
            print(insert_data)

            ################################################################################################
            # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
            database_price = odbc_fucntion.odbc_select_data("SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('Reebok', insert_data[0]))
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
            #################################################################################################

        time.sleep(random.uniform(0.5, 2.5))

        if current_page == total_pages:
            return -1
    except Exception as e:
        print(e)


def crawl_adidas_ajax(page, mail_list):
    # AJAX 動態瀏覽
    # 感覺更好抓了
    # 但是圖面檔案...那個怎麼變成網址資料

    try:
        # 由網址可以找出pn為頁數，更改即可由json檔撈出我們要的資料
        url = 'https://www.adidas.com.hk/plp/waterfall.json?commingsoontype=&pr=-&keyword=%E9%9E%8B\
        &pn=1&pageSize=120&isSaleTop=false&isNew=false&ps=0&cp={}&iz=120&ci=&_=1562051785231' \
            .format(page)  # 頁碼處特別處理
        # 從json轉成python的dict檔案，再由此取出需要的資料
        page_content = get_info(get_html(url))

        #   returnObject -> view -> items(此頁商品資訊集)      -> c(產品編號),img(圖片檔),lp(價格),sp(價格),st(男女),t(品項名)
        #                        -> count(總共商品數)
        #                        -> currentPage(目前頁數)
        #                        -> size(此頁商品數)
        #                        -> totalPages(總共頁數)

        # 前置作業
        image_prefix = 'https://img.adidas.com.hk/resources/'
        # https://www.adidas.com.hk/item/G15890?locale=zh_HK    例子

        # 資料抓出與放入
        # try:
        for item in page_content['returnObject']['view']['items']:

            product_id = 'HK_Adidas_' + item['c']
            image_name = product_id + '.png'

            insert_data = (product_id,
                        item['t'],
                        '',
                        'HKD',
                        str(item['sp']),
                        image_name,
                        'https://www.adidas.com.hk/item/{}?locale=zh_HK'.format(item['c'])
                        )
            print(insert_data)

            
            ################################################################################################

            # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
            database_price = odbc_fucntion.odbc_select_data("SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('Adidas', insert_data[0]))
            if database_price:      # 如果資料庫有這筆資料
                if database_price[0] != insert_data[4]:
                    odbc_fucntion.odbc_update_data('Adidas', (insert_data[4], insert_data[0]), (insert_data[4], insert_data[1]))  # 記得兩個都要更新
                    # 郵件清單更新
                    # 帳戶
                    account_ids = odbc_fucntion.odbc_select_data("SELECT [AccountId] FROM Goods.dbo.CollectionTable WHERE [Name]='{}'".format(insert_data[1]))
                    if account_ids:
                        gmails = []
                        # 求郵件地址
                        for account_id in account_ids:
                            # return 的是tuple所以後面要加[0], m代表郵件地址
                            m = odbc_fucntion.odbc_select_data("SELECT [Email] FROM Goods.dbo.CeneralMenucrs WHERE [AccountId]='{}'".format(account_id))[0]
                            gmails.append(m)
                        # 將所有郵件的內容裝起來,以列表裝起來,要寄信時再解析
                        for gmail in gmails:
                            if mail_list != dict():
                                mail_list[gmail].append({insert_data[1]: '{}, {} -> {}\n{}'.format(insert_data[1], database_price[0], insert_data[4], insert_data[6])})
                            else:
                                mail_list[gmail] = [{insert_data[1]:'親愛的顧客您好,您的追蹤商品更新如下:\n\n{}, {} -> {}\n{}'.format(insert_data[1], database_price[0], insert_data[4], insert_data[6])}]
            else:
                odbc_fucntion.odbc_insert_data('Adidas', insert_data)
                save.save(image_prefix + item['img'], 'HK_Adidas', image_name)
            #################################################################################################
        # 等待時間
        time.sleep(random.uniform(0.5, 2.5))
        if insert_data == set():
            return -1
    except Exception as e:
        print(e)
        return -1      # 暫時先這樣...



def main(mail_list):

    # 將清單載入

    # *adidas
    """    """
    for i in range(1, 43):
        print('page:%s' % i)
        if crawl_adidas_ajax(i, mail_list) == -1:
            break

    # *nike
    """"""
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_nike(i, mail_list) == -1:
            break

    # *UA 效率問題
    """"""
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_ua(i, mail_list) == -1:
            break

    # *NB
    """"""
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_nb(i, 'men', mail_list) == -1:
            break
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_nb(i, 'women', mail_list) == -1:
            break

    # *Reebok
    """"""
    for i in range(1, 10000):
        if crawl_reebok(i, mail_list) == -1:
            break

"""

"""
if __name__ == '__main__':
    mail_list = ''
    main(mail_list)
