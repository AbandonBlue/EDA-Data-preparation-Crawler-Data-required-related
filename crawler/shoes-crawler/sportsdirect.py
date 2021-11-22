import requests
import re
import time
import random
import json
import save
import odbc_fucntion


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


def crawl_sportsdirect(page, brand, mail_list):
    # 因為商品數量過多，網站先用篩選器篩選類別、品牌再用api得到資訊
    # 會卡住...why? ---> 網站寫說禁止爬api, 不知道是不是鎖ip
    try:
        urls = {'Adidas': 'https://www.sportsdirect.com/DesktopModules/BrowseV2/API/BrowseV2Service/GetProductsInformation?categoryName=SD_ADIALL&currentPage={}&productsPerPage=100&sortOption=rank&selectedFilters=AFLOR%5EMens%2CWomens%7CCATG%5ETrainers&isSearch=false&descriptionFilter=&columns=4&mobileColumns=2&clearFilters=false&pathName=%2Fadidas%2Fview-all-adidas&searchTermCategory=&selectedCurrency=GBP'.format(page),
                'NB': 'https://www.sportsdirect.com/DesktopModules/BrowseV2/API/BrowseV2Service/GetProductsInformation?categoryName=SD_BRANBRUNNING&currentPage={}&productsPerPage=100&sortOption=rank&selectedFilters=AFLOR%5EMens%2CWomens%7CCATG%5ETrainers&isSearch=false&descriptionFilter=&columns=4&mobileColumns=2&clearFilters=false&pathName=%2Fnew-balance%2Fnew-balance-running&searchTermCategory=&selectedCurrency=GBP'.format(page),
                'Nike': 'https://www.sportsdirect.com/DesktopModules/BrowseV2/API/BrowseV2Service/GetProductsInformation?categoryName=SD_BRANIKEALLMENS&currentPage={}&productsPerPage=100&sortOption=rank&selectedFilters=AFLOR%5EMens%2CUnisex+Adults%7CCATG%5ETrainers&isSearch=false&descriptionFilter=&columns=4&mobileColumns=2&clearFilters=false&pathName=%2Fnike%2Fnike-mens%2Fall-nike-mens&searchTermCategory=&selectedCurrency=GBP'.format(page),
                'Puma': 'https://www.sportsdirect.com/DesktopModules/BrowseV2/API/BrowseV2Service/GetProductsInformation?categoryName=SD_BRAPUMAALLTRA&currentPage={}&productsPerPage=100&sortOption=rank&selectedFilters=AFLOR%5EMens%2CWomens%7CCATG%5ETrainers&isSearch=false&descriptionFilter=&columns=4&mobileColumns=2&clearFilters=false&pathName=%2Fpuma%2Fall-puma-fitness-and-training&searchTermCategory=&selectedCurrency=GBP'.format(page),
                'Reebok': 'https://www.sportsdirect.com/DesktopModules/BrowseV2/API/BrowseV2Service/GetProductsInformation?categoryName=SD_BRAREEBOKFOOTAL&currentPage={}&productsPerPage=100&sortOption=rank&selectedFilters=AFLOR%5EMens%2CWomens%7CCATG%5ETrainers&isSearch=false&descriptionFilter=&columns=4&mobileColumns=2&clearFilters=false&pathName=%2Freebok%2Freebok-footwear%2Fall-reebok-footwear&searchTermCategory=&selectedCurrency=GBP'.format(page),
                'UA': 'https://www.sportsdirect.com/DesktopModules/BrowseV2/API/BrowseV2Service/GetProductsInformation?categoryName=SD_UNDERALL&currentPage={}&productsPerPage=100&sortOption=rank&selectedFilters=AFLOR%5EMens%2CWomens%7CCATG%5ETrainers&isSearch=false&descriptionFilter=&columns=4&mobileColumns=2&clearFilters=false&pathName=%2Funder-armour%2Fall-under-armour&searchTermCategory=&selectedCurrency=GBP'.format(page)
                }
        url = ''
        if brand == 'Adidas':
            url = urls['Adidas']
        elif brand == 'NB':
            url = urls['NB']
        elif brand == 'Nike':
            url = urls['Nike']
        elif brand == 'Puma':
            url = urls['Puma']
        elif brand == 'Reebok':
            url = urls['Reebok']
        elif brand == 'UA':
            url = urls['UA']

        # 從json轉成python的dict檔案，再由此取出需要的資料
        page_content = get_info(get_html(url))

        # 100個商品一次
        #   products  ->  PrdUrl(URL需要+prefix), MainImage(images), Brand, DisplayName, ListPrice(英鎊),
        end_page = page_content['totalProductsCount'] // 100 + 1

        # 前置作業
        url_prefix = 'https://www.sportsdirect.com'
        pattern = '[0-9.]+'
        for shoe in page_content['products']:
            product_url = url_prefix + shoe['PrdUrl']
            product_id = 'SportsDirect_' + shoe['ItemCode']
            image_url = shoe['MainImage']
            product_name = shoe['DisplayName']
            image_name = product_id + '.jpg'
            price = re.search(pattern, shoe['ListPrice']).group()

            insert_data = (product_id,
                           product_name,
                           '',
                           'GBP',
                           price,
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
                save.save(image_url, 'SportsDirect_{}'.format(brand), image_name)
            #################################################################################################

            # save.save(image_url, 'SportsDirect_{}'.format(brand), image_name)
            # odbc_fucntion.odbc_insert_data(brand, insert_data)

        # 等待時間
        time.sleep(random.uniform(0.5, 2.5))
        if page > end_page:
            return -1
    except Exception as e:
        print(e)


def main(mail_list):
    """"""
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_sportsdirect(i, 'Nike', mail_list) == -1:
            break


    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_sportsdirect(i, 'Adidas', mail_list) == -1:
            break
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_sportsdirect(i, 'Puma', mail_list) == -1:
            break
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_sportsdirect(i, 'Reebok', mail_list) == -1:
            break
    # for i in range(1, 10000):
    #     print('page:%s' % i)
    #     if crawl_sportsdirect(i, 'UA', mail_list) == -1:
    #         break
    # for i in range(1, 10000):
    #     print('page:%s' % i)
    #     if crawl_sportsdirect(i, 'NB', mail_list) == -1:
    #         break


if __name__ == '__main__':
    main({})
"""
這是mongodb的方式
conn = pymongo.MongoClient('localhost', 27017)
db = conn.shoesDB
collection_nike = db.nike
collection_adidas = db.adidas
collection_new_balance = db.new_balance
collection_under_armour = db.under_armour
collection_puma = db.puma
collection_reebok = db.reebok

answer = input('Ready to delete.')

if answer[0].lower().startswith('y'):
    collections = [collection_nike, collection_reebok, collection_under_armour, collection_puma, collection_adidas,
                   collection_new_balance]
    for collection in collections:
        collection.delete_many({})
    print('Collections deleted.')
else:
    print('Keep them in Database(shoesDB).')
"""


"""
# conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=.\sqlexpress; DATABASE=Goods; UID=sa; PWD=12345678')
conn = pyodbc.connect('DRIVER={SQL Server}; SERVER=.\sqlexpress; DATABASE=Goods; UID=sa; PWD=12345678')
cursor = conn.cursor()
conn.close()
"""




