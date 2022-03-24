from numpy.lib.function_base import append
import requests
from bs4 import BeautifulSoup
import mysql.connector



URL = "https://www.nbcnews.com/world"
SITE = 'NBC news'
#connect to database
mydb = mysql.connector.connect(
    host="localhost",
    user="******",
    passwd="*******",
    database="newscrawler",
    auth_plugin='mysql_native_password'
    )
mycursor = mydb.cursor()

r = requests.get(URL)
coverpage = r.content

records=[]
#getting all articles in first page
soup = BeautifulSoup(coverpage, 'html5lib')
coverpage_news = soup.find_all(class_='wide-tease-item__info-wrapper flex-grow-1-m')
#parse every article for process
for n in range(0,len(coverpage_news)):

    title = coverpage_news[n].find(class_='wide-tease-item__headline').getText()
    link = coverpage_news[n].find(class_ ="wide-tease-item__image-wrapper flex-none relative dt dn-m")['href']
    
    #getting the content 
    article = requests.get(link)
    article_content = article.content
    soup_article = BeautifulSoup(article_content, 'html5lib')
    body = soup_article.find_all('div', class_='article-body__content')
    try:    
        x = body[0].find_all('p')

        #unifying the paragraphs
        list_paragraphs = []
        for p in range(0, len(x)-1):
            paragraph = x[p].get_text()
            list_paragraphs.append(paragraph)
            final_text = " ".join(list_paragraphs)
        #sending to database
        records = (title,link,final_text,SITE)
        query = "INSERT INTO articles (title,link,content,news_site) VALUES(%s, %s, %s, %s)"
        mycursor.execute(query, records)
        mydb.commit()
    except:
        pass
