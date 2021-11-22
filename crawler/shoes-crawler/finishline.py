import requests
import time
import random
import re
from bs4 import BeautifulSoup
import odbc_fucntion
import save

# 資料庫還沒處理


def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                             'AppleWebKit/537.36 (KHTML, like Gecko)'
                             'Chrome/75.0.3770.100 Safari/537.36'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()  # 如果請求有問題，直接發生錯誤
    resp.encoding = resp.apparent_encoding  # 正確編碼以顯示網頁，損失部分性能
    return resp.text


def crawl_finishline(page, gender, mail_list):
    # 價格處理有點麻煩
    # 前置作業
    try:
        url = 'https://www.finishline.com/store/men/shoes/_/N-1737dkj?mnid=men_shoes&No={}&isAjax=true'.format((page-1)*40)
        if gender == 'women':
            url = 'https://www.finishline.com/store/women/shoes/_/N-1' \
                  'hednxh?mnid=women_shoes&No={}&isAjax=true'.format((page-1)*40)
        soup = BeautifulSoup(get_html(url), 'html.parser')
        shoes = soup.find_all('div', 'product-card')
        end_page = soup.find('div', 'column shrink pl-1 pr-1').find_all('option')[-1]['value']      # 最終頁
        url_prefix = 'https://www.finishline.com'
        pattern = '[0-9.]+'  # 把價格分離出來
        brands = {'ADIDAS': 0, 'NIKE': 0, 'PUMA': 0, 'NEW BALANCE': 0, 'REEBOK': 0, 'UNDER ARMOUR': 0}
        insert_data = set()

        for shoe in shoes:
            if shoe['data-brand'] in brands:
                pass
            else:
                continue        # 非這幾個牌子就不是我要的，提升速度
            product_url = url_prefix + shoe.find('a')['href']
            product_id = 'FinishLine_' + shoe['data-styleid']
            image_url = shoe.find('img', 'productImage')['src']

            if image_url == '/store/assets/images/shoe_placeholder.png':
                image_url = shoe.find('img', 'productImage')['data-src']
            product_name = shoe.find('h2', 'product-name').text.strip()
            image_name = product_id + '.jpg'

            price1 = shoe.find('div', 'product-price').find_next().text
            price = re.search(pattern, price1).group()
            # print(shoe.find('div', 'product-price'))
            possible = shoe.find('div', 'product-price').find_all('span')
            for p in possible:
                if re.search(pattern, p.text) is not None:
                    price = re.search(pattern, p.text).group()

            insert_data = (product_id,  #
                           product_name,
                           '',
                           'USD',
                           price,
                           image_name,
                           product_url
                           )
            if shoe['data-brand'] == 'ADIDAS':
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
                            "SELECT [AccountId] FROM Goods.dbo.CollectionTable WHERE [Name]='{}'".format(
                                insert_data[1]))
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
                                                                                                       database_price[
                                                                                                           0],
                                                                                                       insert_data[4],
                                                                                                       insert_data[6])})
                                else:
                                    mail_list[gmail] = [
                                        {insert_data[1]: '親愛的顧客您好,您的追蹤商品更新如下:\n\n{}, {} -> {}\n{}'.format(
                                            insert_data[1], database_price[0], insert_data[4], insert_data[6])}]

                else:
                    odbc_fucntion.odbc_insert_data('Adidas', insert_data)
                    save.save(image_url, 'FinishLine_Adidas', image_name)
                #################################################################################################
            elif shoe['data-brand'] == 'NIKE':
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
                            "SELECT [AccountId] FROM Goods.dbo.CollectionTable WHERE [Name]='{}'".format(
                                insert_data[1]))
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
                                                                                                       database_price[
                                                                                                           0],
                                                                                                       insert_data[4],
                                                                                                       insert_data[6])})
                                else:
                                    mail_list[gmail] = [
                                        {insert_data[1]: '親愛的顧客您好,您的追蹤商品更新如下:\n\n{}, {} -> {}\n{}'.format(
                                            insert_data[1], database_price[0], insert_data[4], insert_data[6])}]

                else:
                    odbc_fucntion.odbc_insert_data('Nike', insert_data)
                    save.save(image_url, 'FinishLine_Nike', image_name)
                #################################################################################################
            elif shoe['data-brand'] == 'PUMA':
                ################################################################################################
                # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
                database_price = odbc_fucntion.odbc_select_data(
                    "SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('Puma', insert_data[0]))
                if database_price:  # 如果資料庫有這筆資料
                    if database_price[0] != insert_data[4]:
                        odbc_fucntion.odbc_update_data('Nike', (insert_data[4], insert_data[0]),
                                                       (insert_data[4], insert_data[1]))  # 記得兩個都要更新
                        # 郵件清單更新
                        # 帳戶
                        account_ids = odbc_fucntion.odbc_select_data(
                            "SELECT [AccountId] FROM Goods.dbo.CollectionTable WHERE [Name]='{}'".format(
                                insert_data[1]))
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
                                                                                                       database_price[
                                                                                                           0],
                                                                                                       insert_data[4],
                                                                                                       insert_data[6])})
                                else:
                                    mail_list[gmail] = [
                                        {insert_data[1]: '親愛的顧客您好,您的追蹤商品更新如下:\n\n{}, {} -> {}\n{}'.format(
                                            insert_data[1], database_price[0], insert_data[4], insert_data[6])}]

                else:
                    odbc_fucntion.odbc_insert_data('Puma', insert_data)
                    save.save(image_url, 'FinishLine_Puma', image_name)
                #################################################################################################
            elif shoe['data-brand'] == 'NEW BALANCE':
                ################################################################################################
                # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
                database_price = odbc_fucntion.odbc_select_data(
                    "SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('NB', insert_data[0]))
                if database_price:  # 如果資料庫有這筆資料
                    if database_price[0] != insert_data[4]:
                        odbc_fucntion.odbc_update_data('Nike', (insert_data[4], insert_data[0]),
                                                       (insert_data[4], insert_data[1]))  # 記得兩個都要更新
                        # 郵件清單更新
                        # 帳戶
                        account_ids = odbc_fucntion.odbc_select_data(
                            "SELECT [AccountId] FROM Goods.dbo.CollectionTable WHERE [Name]='{}'".format(
                                insert_data[1]))
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
                                                                                                       database_price[
                                                                                                           0],
                                                                                                       insert_data[4],
                                                                                                       insert_data[6])})
                                else:
                                    mail_list[gmail] = [
                                        {insert_data[1]: '親愛的顧客您好,您的追蹤商品更新如下:\n\n{}, {} -> {}\n{}'.format(
                                            insert_data[1], database_price[0], insert_data[4], insert_data[6])}]

                else:
                    odbc_fucntion.odbc_insert_data('NB', insert_data)
                    save.save(image_url, 'FinishLine_NB', image_name)
            elif shoe['data-brand'] == 'REEBOK':
                ################################################################################################
                # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
                database_price = odbc_fucntion.odbc_select_data(
                    "SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('Reebok', insert_data[0]))
                if database_price:  # 如果資料庫有這筆資料
                    if database_price[0] != insert_data[4]:
                        odbc_fucntion.odbc_update_data('Nike', (insert_data[4], insert_data[0]),
                                                       (insert_data[4], insert_data[1]))  # 記得兩個都要更新
                        # 郵件清單更新
                        # 帳戶
                        account_ids = odbc_fucntion.odbc_select_data(
                            "SELECT [AccountId] FROM Goods.dbo.CollectionTable WHERE [Name]='{}'".format(
                                insert_data[1]))
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
                                                                                                       database_price[
                                                                                                           0],
                                                                                                       insert_data[4],
                                                                                                       insert_data[6])})
                                else:
                                    mail_list[gmail] = [
                                        {insert_data[1]: '親愛的顧客您好,您的追蹤商品更新如下:\n\n{}, {} -> {}\n{}'.format(
                                            insert_data[1], database_price[0], insert_data[4], insert_data[6])}]

                else:
                    odbc_fucntion.odbc_insert_data('Reebok', insert_data)
                    save.save(image_url, 'FinishLine_Reebok', image_name)
            elif shoe['data-brand'] == 'UNDER ARMOUR':
                ################################################################################################
                # 這邊直接檢查資料庫有無此筆資料,有的話進一步檢查是否有價格變動
                database_price = odbc_fucntion.odbc_select_data(
                    "SELECT PRICE FROM Goods.dbo.{}_Table WHERE [Id]='{}'".format('Puma', insert_data[0]))
                if database_price:  # 如果資料庫有這筆資料
                    if database_price[0] != insert_data[4]:
                        odbc_fucntion.odbc_update_data('UA', (insert_data[4], insert_data[0]),
                                                       (insert_data[4], insert_data[1]))  # 記得兩個都要更新
                        # 郵件清單更新
                        # 帳戶
                        account_ids = odbc_fucntion.odbc_select_data(
                            "SELECT [AccountId] FROM Goods.dbo.CollectionTable WHERE [Name]='{}'".format(
                                insert_data[1]))
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
                                                                                                       database_price[
                                                                                                           0],
                                                                                                       insert_data[4],
                                                                                                       insert_data[6])})
                                else:
                                    mail_list[gmail] = [
                                        {insert_data[1]: '親愛的顧客您好,您的追蹤商品更新如下:\n\n{}, {} -> {}\n{}'.format(
                                            insert_data[1], database_price[0], insert_data[4], insert_data[6])}]

                else:
                    odbc_fucntion.odbc_insert_data('UA', insert_data)
                    save.save(image_url, 'FinishLine_UA', image_name)

            print(insert_data)

        time.sleep(random.uniform(0.5, 2.5))
        if page > int(end_page):
            return -1
    except Exception as e:
        print(e)
# 跑起來!!!!


def main(mail_list):
    """"""
    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_finishline(i, 'men', mail_list) == -1:
            break

    for i in range(1, 10000):
        print('page:%s' % i)
        if crawl_finishline(i, 'women', mail_list) == -1:
            break


if __name__ == '__main__':
    main({})