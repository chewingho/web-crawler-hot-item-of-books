#資料清理用
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
#匯入資料庫
import mysql.connector from mysql.connector
import pymysql

categoryDic = {}
subCategoryDic = {}
today = datetime.today().strftime('%Y-%m-%d')
#取得用robots.txt來看可用的User-Agent
headers = {
    'User-Agent': '*'
    #'From': ''#E-mail
}

r = requests.get('https://www.books.com.tw/web/sys_categoryIndex', headers=headers, allow_redirects=True)
soup = BeautifulSoup(r.text, 'html.parser')
category_list = soup.find_all("div","mod type03_m008 clearfix")
df = pd.DataFrame({'category' : [], 'item_name' : [], 'ranking' : [], 'hyperlink' : [], 'update_date': []})

def category_bestseller(url, df):
    r_category = requests.get(url, headers=headers,allow_redirects=True)
    soup = BeautifulSoup(r_category.text, 'html.parser')
    category_list = soup.find_all("ul","number_a")
    count = 1
    if category_list != []:
        for item in category_list:
            for i in range(1,len(item.find_all("a"))):
                new_row = {'category':categoryDic[url], 'item_name':item.find_all("a")[i].text, 'ranking':f'{count:.0f}', 'hyperlink':item.find_all("a")[i]['href'], 'update_date': today}
                df = df.append(new_row, ignore_index=True)
                count = count + 1
    return df

#大分類,利用category_bestseller尋找該分類的前10暢銷品
for i in range(1, len(category_list)):
    if category_list[i].find('a') == None:
        continue
    categoryDic[category_list[i].find('a')['href']] = category_list[i].find('a').text
    df = category_bestseller(category_list[i].find('a')['href'], df)

#不是每一分類都有熱門排行,就算找得到也要看內容才能確定是否正確,將找出不正確資訊的分類刪除   
df.drop(df.loc[df['category']=='magazine'].index, inplace=True)
df.drop(df.loc[df['category']=='fbooks'].index, inplace=True)
df.drop(df.loc[df['category']=='雜誌'].index, inplace=True)
df.drop(df.loc[df['category']=='外文書'].index, inplace=True)
df.reset_index(drop=True, inplace=True)

#中文書的細類,利用category_bestseller尋找該分類的前10暢銷品
categoryDic = {}
df_sub = pd.DataFrame({'category' : [], 'item_name' : [], 'ranking' : [], 'hyperlink' : [], 'update_date': []})
r_category = requests.get('https://www.books.com.tw/web/books/', headers=headers,allow_redirects=True)

soup = BeautifulSoup(r_category.text, 'html.parser')
category_list = soup.find("div","mod_b type02_l001-1 clearfix").find_all("a")

for i in range(0, len(category_list)):
    categoryDic[category_list[i]['href']] = category_list[i].text
    df_sub = category_bestseller(category_list[i]['href'], df_sub)
    
try:
    #連接 MySQL資料庫
    connection = mysql.connector.connect(
        host = "127.0.0.1",
        user = "python_user",
        password = "python123",
        database = "mynewdb",
        use_pure = True)

    #將匯入資料庫
    cursor = connection.cursor()

    for index, row  in df.iterrows():
        sql = "INSERT INTO TB_RANKING(CATEGORY, ITEM_NAME, RANKING, HYPERLINK, UPDATE_DATE) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, tuple(row))
    connection.commit()
    
    for index, row  in df_sub.iterrows():
        sql = "INSERT INTO TB_SUBCATEGORY(CATEGORY, ITEM_NAME, RANKING, HYPERLINK, UPDATE_DATE) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, tuple(row))
    connection.commit()
    print("資料庫匯入已完成")

except mysql.connector.Error as e:
    print("資料庫連接失敗：", e)

finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("資料庫連線已關閉")