
import requests as r
from bs4 import BeautifulSoup
from newspaper import Article
import pandas as pd
class parser(BeautifulSoup):
    def __init__(self, markup=None, features=None, builder=None, parse_only=None, from_encoding=None, exclude_encodings=None, element_classes=None, **kwargs) -> None:
        super().__init__(markup, features, builder, parse_only, from_encoding, exclude_encodings, element_classes, **kwargs)
    def get_titles(self):
        titles = []
        for title in self.find_all("h2",{"class":"mt-2 line-clamp-3 sm:line-clamp-2 text-xl xs:text-2xl xs:leading-8 sm:text-[1.625rem] sm:leading-9 font-bold hover:text-main dark:hover:text-main-400 hover:underline"}):
            titles.append(title.text.strip())
        return titles
    def get_summaries(self):
        summaries = []
        for summary in self.find_all("p",{"class":"mt-2 line-clamp-3 sm:line-clamp-2 font-serif xs:text-lg text-ellipsis break-words"}):
            summaries.append(summary.text.strip())
        return summaries
    def get_dates(self):
        dates = []
        for date in self.find_all("time",{"class":"updated text-black dark:text-white"}):
            dates.append(date['datetime'][:10])
        return dates
    def get_authors(self):
        authors = []
        for author in self.find_all("a",{'class':"fn text-black dark:text-white font-bold"}):
            authors.append(author.text.strip())
        return authors
    def get_urls(self):
        urls = []
        for url in self.find_all("a",{"class":"flex-none relative overflow-hidden rounded sm:w-5/12"}):
            urls.append(url['href'])
        return urls
    def get_full_text(self):
        string_builder = ""
        for ft in self.find_all("p"):
            string_builder+=(ft.text.strip() + " ")
        return string_builder
if __name__ == "__main__":
    article_data = {
        "title": [],
        "author": [],
        "pub_date": [],
        "url": [],
        "abstract": [],
        "full_text": [],
        "key_words": [],
        "data_source": []
    }
    counter = 0
    for i in range(1,2):
        link = "https://gizmodo.com/tech/artificial-intelligence/page/{}".format(i)
        req = r.get(link)
        tester = parser(req.text,'html.parser')
        links = tester.get_urls()
        full_texts = list()
        key_words = list()
        for hl in links:
            counter+=1
            req_2 = r.get(hl)
            key_word_extractor = Article(hl)
            key_word_extractor.download()
            key_word_extractor.parse()
            key_word_extractor.nlp()
            sub_parser = parser(req_2.text,'html.parser')
            full_text = sub_parser.get_full_text()
            full_texts.append(full_text)
            key_words.append(", ".join(key_word_extractor.keywords))
        article_data["author"].extend(tester.get_authors())
        article_data["title"].extend(tester.get_titles())
        article_data["pub_date"].extend(tester.get_dates())
        article_data["url"].extend(tester.get_urls())
        article_data["abstract"].extend(tester.get_summaries())  # Add article summary
        article_data["full_text"].extend(full_texts)
        article_data["key_words"].extend(key_words)  # Join keywords
    article_data["data_source"] = ["Gizmodo" for i in range(counter)]
    df1 = pd.DataFrame(article_data)
    df1.to_csv(r"ouput\gizmodo.csv")    
        
            
        