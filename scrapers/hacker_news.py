#Author : Andrew Franklin
#Date : 10/2/2024
#Purpose : This script will allow users to scrape different data sources from hacker news integrating their API with the newspaper3k scraper library
#Dependancies : requests, newspaper3k, lxml_html_clean, pandas

import requests
from newspaper import Article
import pandas as pd
#hacker news api reference: https://hn.algolia.com/api
link = requests.get("https://hn.algolia.com/api/v1/search?query=ai%20winter&restrictSearchableAttributes=url&hitsPerPage=100")
info = link.json()
master_df = list()
for hit in info["hits"]:
    try:
        #dowload the html content to a article object
        a = Article(hit['url'])
        #preprocessing and lemmatinization
        a.download()
        a.parse()
        a.nlp()
        #get all avialable information
        a = Article(hit['url'])
        a.download()
        a.parse()
        a.nlp()
        summary = a.summary.strip().replace("\n"," ")
        full_text = a.text.strip().replace("\n"," ")
        temp_df = {"title": a.title.strip(), "author":", ".join(a.authors),"url":hit["url"],"summary":summary,"full_text":full_text,"key_words":", ".join(a.keywords),"pub_date": a.publish_date}
        master_df.append(temp_df)
    except:
        pass
master_df = pd.DataFrame(master_df)
master_df.to_csv(path_or_buf="out.csv")