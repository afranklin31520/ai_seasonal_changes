import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
def get_abstract_and_keywords(link:str):
    response = requests.get(link)
    parser = BeautifulSoup(response.text,'html.parser')
    abstract = parser.find("div",attrs={"class":"abstract-content selected","id":'eng-abstract'}).text.strip().replace("\n","")
    return abstract

def get_artitle_titles_links():
    os.chdir("output")
    df1 = pd.DataFrame(columns=["title","url"])
    BASE_URL = "https://pubmed.ncbi.nlm.nih.gov"
    searchTerm = "artificial intelligence".replace(" ","+")
    #get the # of pages based off the search term
    link = "https://pubmed.ncbi.nlm.nih.gov/?term={}&filter=simsearch2.ffrft".format(searchTerm)
    response = requests.get(link)
    parser = BeautifulSoup(response.text,'html.parser')
    total_pages = int(parser.find("label",attrs={"class":"of-total-pages"}).text.split(" ")[-1].replace(",",""))
    for page_index in range(1,3):
        link = "https://pubmed.ncbi.nlm.nih.gov/?term={}&filter=simsearch2.ffrft&page={}".format(searchTerm,page_index)
        response = requests.get(link)
        parser = BeautifulSoup(response.text,'html.parser')
        for article in parser.find_all("a",attrs={"class":"docsum-title"}):
            title = article.text.strip()
            url = BASE_URL + article["href"].strip()
            abstract = get_abstract_and_keywords(url)
            temp_df = pd.DataFrame([{"title":title,"url":url,"abstract":abstract}])
            get_abstract_and_keywords(url)
            df1 = pd.concat(objs=[df1,temp_df])
    df1.to_csv("pubmed.csv")
if __name__ == "__main__":
    get_artitle_titles_links()