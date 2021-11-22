import pyodbc


def odbc_select_data(cmd):
    # 利用cmd取決要拿什麼資料
    cursor = odbc_connect()
    raw_data = cursor.execute(cmd).fetchone()
    cursor.commit()
    return raw_data


def odbc_connect():
    # 把你的帳密改一下就可以用了
    with pyodbc.connect(r'DRIVER={SQL Server}; SERVER=.\sqlexpress; DATABASE=Goods; UID=sa; PWD=12345678') as conn:
        cursor = conn.cursor()
    return cursor


def odbc_command(cursor, cmd, data):
    cursor.execute(cmd, data)


def odbc_get_primary_keys(brand: str, keys):
    cursor = odbc_connect()
    row = cursor.execute('SELECT Id FROM Goods.dbo.{}_Table'.format(brand)).fetchone()  # 一筆資料
    while row:
        keys.add(row)
        row.fetchone()
    return keys


def odbc_update_data(brand: str, update_data, update_data2):
    # 若變數為字符串，會自動加單引號
    # UPDATE [Goods].[dbo].[NB_Table] SET [Price]=100000 WHERE [Id]='FinishLine_CM997HFA';
    # UPDATE progress SET CockpitDrill = ? WHERE progress_primarykey = ?
    cmd_update = 'UPDATE Goods.dbo.{}_Table ' \
                 'SET Price= ? ' \
                 'WHERE Id=?'.format(brand)
    # 這是收藏庫的
    cmd_update2 = 'UPDATE Goods.dbo.CollectionTable ' \
                 'SET Price= ? ' \
                 'WHERE Name=?'
    cursor = odbc_connect()
    odbc_command(cursor, cmd_update, update_data)
    odbc_command(cursor, cmd_update2, update_data2)
    cursor.commit()
    cursor.close()


def odbc_insert_data(brand: str, insert_data):
    # 把資料填入，含關閉
    try:
        cmd_insert = 'INSERT INTO Goods.dbo.{}_Table(Id, Name, Style, Currency, Price, Images, URL) VALUES ' \
                     '(?, ?, ?, ?, ?, ?, ?)'.format(brand)

        cursor = odbc_connect()
        odbc_command(cursor, cmd_insert, insert_data)
        cursor.commit()
        cursor.close()
    except Exception as e:
        print(e)


def odbc_delete_data(brand:str):
    try:
        cmd_delete = 'DELETE FROM Goods.dbo.{}_Table'.format(brand)
        cursor = odbc_connect()
        cursor.execute(cmd_delete)
        cursor.commit()
    except Exception as e:
        print(e)

"""
cmd_user = "SELECT Email FROM Goods.dbo.CeneralMenucrs WHERE AccountId='{}'".format(9)
cmd_followId = "SELECT * FROM Goods.dbo.CollectionTable WHERE [Name]='{}'".format('SUPERSTAR 360 運動鞋')

data = odbc_select_data(cmd_followId)
print(data)
"""
