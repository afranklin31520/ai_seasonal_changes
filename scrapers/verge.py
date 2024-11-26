import requests
from bs4 import BeautifulSoup
from newspaper import Article
from database_inserter import insert_into_db
def main() -> None:
    seen = dict()
    url = "https://www.theverge.com/sitemaps"
    sitemap_req = requests.get(url)
    sitemap_parser = BeautifulSoup(sitemap_req.text,'html.parser')
    for entry in sitemap_parser.find_all("loc"):
        if "entries" in entry.text:
            entry_req = requests.get(entry.text)
            entry_parser = BeautifulSoup(entry_req.text,'html.parser')
            for article in entry_parser.find_all("url"):
                article_link = article.loc.text
                if article_link in seen:
                    continue
                print("starting to parse",article_link)
                try:
                    article_parser = Article(article_link,fetch_images=False, request_timeout=20)
                    article_parser.download()
                    article_parser.parse()
                    article_parser.nlp()
                    title = article_parser.title.strip().replace("\n"," ")
                    authors = ", ".join(article_parser.authors).strip().replace("\n"," ")
                    summary = article_parser.summary.strip().replace("\n"," ")
                    keywords = ", ".join(article_parser.keywords).strip().replace("\n"," ")
                    url = article_link
                    full_text = article_parser.text.strip().replace("\n"," ")
                    pub_date = str(article_parser.publish_date)
                    instance = [
                        title,
                        authors,
                        url,
                        summary,
                        full_text,
                        keywords,
                        pub_date,
                        "The Verge"
                    ]
                    insert_into_db(instance)
                    print("succeccful add the article",title)
                    seen[article_link] = True
                except Exception as e:
                    print(e)
                    seen[article_link] = False
                print()
if __name__ == "__main__":
    main()