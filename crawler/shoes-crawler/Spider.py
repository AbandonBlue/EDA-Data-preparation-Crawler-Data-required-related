import HK
import Taiwan
import USA
import Yahoo
import sportsdirect
import finishline
import threading
# import multiprocessing as mp
import time
from odbc_fucntion import odbc_delete_data
from mail_send import send_gmail


# 記得改2個地方
# 1. save.py ---> os.chdir(r'C:\Users\aband\OneDrive\桌面\CMoney\期末專題\GoodsManager_TW_v3.1.0\UI\Content\images')
#                   上述改成你的本地位置
# 2. odbc_fucntion.py ---> odbc_connect()函式內的資料庫帳密
# 3. 如果還有問題,記得將環境 pip 下載一些套件


""""""
try:
    # 郵件初始化
    all_mails = dict()

    # 刪除資料
    # brands = ['Nike', 'Adidas', 'NB', 'UA', 'Reebok', 'Puma']
    # for brand in brands:
    #     odbc_delete_data(brand)

    # input('Ready to test!')
    t1 = time.time()
    thd_HK = threading.Thread(target=HK.main, name='HK', args=(all_mails,))
    thd_Taiwan = threading.Thread(target=Taiwan.main, name='Taiwan', args=(all_mails,))
    thd_USA = threading.Thread(target=USA.main, name='USA', args=(all_mails,))
    thd_Yahoo = threading.Thread(target=Yahoo.main, name='Yahoo', args=(all_mails,))
    thd_Sportsdirect = threading.Thread(target=sportsdirect.main, name='Sportsdirect', args=(all_mails,))
    thd_Finishline = threading.Thread(target=finishline.main, name='Finishline', args=(all_mails,))

    # 多進程的優化方式
    # p_HK = mp.Process(target=HK.main, name='HK')
    # p_Taiwan = mp.Process(target=Taiwan.main, name='Taiwan')
    # p_USA = mp.Process(target=USA.main, name='USA')


    """
    
    """

    """
    
    """

    thd_HK.start()
    thd_Taiwan.start()
    thd_USA.start()
    thd_Yahoo.start()
    thd_Sportsdirect.start()
    thd_Finishline.start()

    thd_HK.join()
    thd_Taiwan.join()
    thd_USA.join()
    thd_Yahoo.join()
    thd_Sportsdirect.join()
    thd_Finishline.join()

    now = time.time()
    print('Total time:', now-t1)
except Exception as e:
    print(e)
finally:
    # 寄出mail
    for mail in all_mails:

        contents = []                       # 內容,先用list裝起來
        for prods in all_mails[mail]:       # 得到每一個prods ---> {'商品名':'內容'}
            for k, v in prods.items():      # k(商品名) v(內容)
                contents.append(v)          # 
                contents.append('\n\n')     # 排版
        # 將內容轉成str
        contents = "\n".join(contents)
        send_gmail(id=mail, title='您追蹤的商品價格變動了,來看看吧!', content=contents)


