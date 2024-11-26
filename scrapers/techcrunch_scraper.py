from database_inserter import insert_into_db
import requests
from bs4 import BeautifulSoup
import datetime , sys
    
    
#collect all information from acedemic papers
def scrape_articles(page_number:int):
    link = f"https://techcrunch.com/category/artificial-intelligence/page/"+str(page_number)
    print(link)
    website = requests.get(link)
    parser = BeautifulSoup(website.text,"html.parser")
    parser.prettify()
    table = parser.find("div",attrs={"class":"wp-block-tc23-post-picker-group"})
    #row is of type bs4.element.Tag
    dicto = {}
    for row in table.find_all("div",attrs={"class":"wp-block-tc23-post-picker"}):
        link = row.h2.a.get("href")
        title = row.h2.a.text.strip()
        abstract = row.find("p",attrs={"class": "wp-block-post-excerpt__excerpt"}).text.strip()
        author = row.find("div",attrs={"class": "wp-block-group wp-block-tc23-author-card__info is-layout-flow wp-block-group-is-layout-flow"}).text.strip()
        date = row.time.get("datetime")[:10].strip()
        article = scrape_article(link)
        body_text = article[0].replace("\n","")
        body_text = body_text.replace("\'","")
        body_text = body_text.replace("\"","")

        tags = article[1]
        ins_aff , geo_aff , funding = "", "", ""
        date = date.split("-")
        date = datetime.date(year=int(date[0]),month=int(date[1]),day=int(date[2]))
        values = [title,author,date,link,abstract,body_text,tags,funding,geo_aff,ins_aff]
        insert_into_db(values)
        print("article record added to db")
def scrape_article(link:str):
    website = requests.get(link)
    parser = BeautifulSoup(website.text,"html.parser")
    parser.prettify()
    body = parser.find("div",attrs={"class":"entry-content wp-block-post-content is-layout-flow wp-block-post-content-is-layout-flow"})
    tags = parser.find("div",attrs={"class":"tc23-post-relevant-terms__terms"})
    tags = tags.text
    return body.text.strip() , tags.strip()
def batch_insert():
    #first command line arg is the number of pages you want to scrape
    for i in range(1,501):
        try:
            scrape_articles(i)
        except:
            pass