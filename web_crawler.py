import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

#建立表格,有4個欄位:分類(category)、名稱(name)、排行(rank)、超連結(hyperlink)
df = pd.DataFrame({'category': [], 'name': [], 'rank': [], 'hyperlink': []})
pattern = 'https:\/\/www\.books\.com\.tw\/web\/(.*)'#category

#https://www.books.com.tw/robots.txt來看可用的User-Agent
headers = {
    'User-Agent': '*', 
    'From': 'caac21008@gmail.com'#E-mail
}
#粗體字分類
r = requests.get('https://www.books.com.tw/web/sys_categoryIndex', headers = headers, allow_redirects = True)
soup = BeautifulSoup(r.text, 'html.parser')
category_list = soup.find_all("div", "mod type03_m008 clearfix")

#尋找該分類的前10暢銷品,並將資訊加入df
def category_bestseller(url, df):
    r_category = requests.get(url, headers = headers, allow_redirects = True)
    soup = BeautifulSoup(r_category.text, 'html.parser')
    category_list = soup.find_all("ul", "number_a")
    count = 1
    #不是每一分類都有熱門排行
    if category_list != []:
        for item in category_list:
            for i in range(1,len(item.find_all("a"))):
                new_row = {'category': re.match(pattern, url).group(1), 'name': item.find_all("a")[i].text, 'rank': count, 'hyperlink': item.find_all("a")[i]['href']}
                df = df.append(new_row, ignore_index = True)
                count = count + 1
    return df

#透過超連結找出分類,並透過category_bestseller尋找該分類的前10暢銷品
for i in range(1, len(category_list)):
    if category_list[i].find('a') == None:
        continue
    df = category_bestseller(category_list[i].find('a')['href'], df)

#觀察df,因magazine與fbooks資訊與books、china、mooks不同,將兩分類刪除
df.drop(df.loc[df['category']=='magazine'].index, inplace = True)
df.drop(df.loc[df['category']=='fbooks'].index, inplace = True)
df.reset_index(drop = True, inplace = True)

#輸出
df.to_csv("博客來排行.csv", index = False)
df.to_excel('博客來排行.xls', index = False)