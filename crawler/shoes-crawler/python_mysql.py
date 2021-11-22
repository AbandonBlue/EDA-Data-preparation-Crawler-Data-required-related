import mysql.connector
# workflow
# 連線 -> 創建資料庫 -> 創建Tables -> 設定Tables的columns -> 插入資料


# create connection
# need
    # host
    # username
    # password
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    auth_plugin="mysql_native_password" # 解決預設認證問題
)

print(f'Connection: {mydb.is_connected()}')

# create a database
# need
mycursor = mydb.cursor()
# mycursor.execute(operation="create database testdb")
# check if the db exists
# Code below needs both
mycursor.execute("SHOW DATABASES")
# print('Databases:')
# print()
# for db in mycursor:
#     print(db)


# create a table
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="123456",
    database="testdb",
    auth_plugin="mysql_native_password"
)

mycursor = mydb.cursor()
# mycursor.execute("show tables")
# print()
# print('Tables:')
# print()
# for table in mycursor:
#     print(table)
# mycursor.execute("create table test_table (name VARCHAR(255), price int(32), address VARCHAR(255))")
# # mycursor.execute("alter table momo_items add column id int auto_increment primary key")


# When work above all be done, let's insert some information!
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="123456",
    database="testdb",
    auth_plugin="mysql_native_password"
)
mycursor = mydb.cursor()

sql_cmd = "insert into test_table (name, price, address) values (%s, %s, %s)"  
# values = ('冰箱', 10000, 'some url or else')
# mycursor.execute(sql_cmd, values)

# # When you wanna deliver a trancsaction, you need to commmit to execute it!
# # Just keep in mind. It's rules.
# mydb.commit()

# rowcount = how many records in that table.
# print(mycursor.rowcount, "record inserted.")

# # Insert many records works the same
# val = [
#     (f'冰箱{i}', i, f'address{i}') for i in range(10)
# ]
# print(val)
# mycursor.executemany(sql_cmd, val)
# mydb.commit()

# select data from table
mycursor.execute('select * from test_table')
# mycursor.fetchall()
for record in mycursor:
    print(record)