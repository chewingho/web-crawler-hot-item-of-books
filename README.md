# web-crawler-hot-item-of-books
----
## Description
> 爬取博客來商品分類，取得分類的前10熱門商品分類、名稱、排名、超連結，並匯出成實體檔案
----
## Process
1. import要使用到的module
```python
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
```
2. 建立表格，共4個欄位:分類(category)、名稱(name)、排行(rank)、超連結(hyperlink)，pattern是為了之後category準備
```python
df = pd.DataFrame({'category': [], 'name': [], 'rank': [], 'hyperlink': []})
pattern = 'https:\/\/www\.books\.com\.tw\/web\/(.*)'#category
```
3.  在博客來首頁，點擊看全部商品分類，取得網址後，開始爬蟲！但是回傳資訊怪怪的!  
```python
r = requests.get('https://www.books.com.tw/web/sys_categoryIndex')
soup = BeautifulSoup(r.text, 'html.parser')
print(soup)
```
> print(soup)結果如下：
```
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"><head><meta content="TEXT/HTML; CHARSET=utf-8" http-equiv="CONTENT-TYPE"/><title>Error</title></head><body><h2>Error</h2><table bgcolor="#FEEE7A" border="0" cellpadding="0" cellspacing="0" summary="Error" width="400"><tr><td><table border="0" cellpadding="3" cellspacing="1" summary="Error"><tr align="left" bgcolor="#FBFFDF" valign="top"><td><strong>Error</strong></td></tr><tr bgcolor="#FFFFFF" valign="top"><td>This page can't be displayed. Contact support for additional information.<br/>The Event ID is: 5343500884002.<br/>The Session ID is: N/A.</td></tr></table></td></tr></table></body></html>
```
> google發生什麼事，發現沒有提供user-agent，因此被重新導向了，如何取得user-agent呢？  
> 在博客來首頁網址後面加入/robots.txt，可以得知user-agent為*，再加上From為自己的E-mail  
> 發出request時傳出headers，之後就可以取得原始碼，進一步剖析  
```python
headers = {
    'User-Agent': '*', 
    'From': ''#E-mail
}
```
4. 檢視原始碼，大分類可以用div,class_=mod type03_m008 clearfix取得  
```python
category_list = soup.find_all("div", "mod type03_m008 clearfix")
for i in range(1, len(category_list)):
    if category_list[i].find('a') == None:
        continue
    print(category_list[i].find('a')['href'])
```
> print結果來看看，可以獲得分類的超連結，之後就可以透過function來爬取超連結的熱門商品  
```
https://www.books.com.tw/web/books
https://www.books.com.tw/web/china
https://www.books.com.tw/web/fbooks
https://www.books.com.tw/web/cd
https://www.books.com.tw/web/dvd
https://www.books.com.tw/web/magazine
https://www.books.com.tw/web/mook
https://www.books.com.tw/web/3C
https://www.books.com.tw/web/bag
https://www.books.com.tw/web/clean
https://www.books.com.tw/web/cosmetic
https://www.books.com.tw/web/design
https://www.books.com.tw/web/fashion
https://www.books.com.tw/web/fm
https://www.books.com.tw/web/food
https://www.books.com.tw/web/giftcard
https://www.books.com.tw/web/health
https://www.books.com.tw/web/icash
https://www.books.com.tw/web/kitchen
https://www.books.com.tw/web/mammybaby
https://www.books.com.tw/web/muji
https://www.books.com.tw/web/outdoors
https://www.books.com.tw/web/starbucks
https://www.books.com.tw/web/stationery
https://www.books.com.tw/web/watch
```
5.  爬取熱門商品的function如下
```python
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
```
6. 來看看df的結果，row的數量應該要是10的倍數才對！  
> 其實magazine、fbooks雖然有爬到資訊，但是和books、china、mooks的資訊不相同，將這兩個分類刪除
```python
df.drop(df.loc[df['category']=='magazine'].index, inplace = True)
df.drop(df.loc[df['category']=='fbooks'].index, inplace = True)
df.reset_index(drop = True, inplace = True)
```
7. 最後將資料表匯出成csv檔、xls檔
```python
df.to_csv("博客來排行.csv", index = False)
df.to_excel('博客來排行.xls', index = False)
```
----
## Review ##  
 本來以為每個分類皆可以爬到前10暢銷排行榜，結果只有中文書、簡體書、MOOKS三個分類有爬到。  
其他大類點進去，有的也有暢銷商品，但是並不是前10暢銷排行榜，意義上不同就將分類刪除；
有的是沒有暢銷商品，有新品上市前10名；  
有的可能都沒有這些資訊。  
所以爬到的資訊其實不多QQ  
----
## Thanks
* [使用偽裝user-agent爬取蝦皮購物網](https://freelancerlife.info/zh/blog/python-web-scraping-user-agent-for-shopee/)
