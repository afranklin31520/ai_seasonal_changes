import arxiv , os 
import pandas as pd
from PyPDF2 import PdfReader
def load_pdfs(topic:str):
    illegal_chars = ['<', '>', ':', '"', '/', r'\\', '|', '?', '*',".",","]
    res = arxiv.Search(
        query= topic ,#what do you want to search for
        max_results= 50 #how many articles do you want
    )
    master_df = []
    os.chdir(r"..\\")
    os.chdir(r"pdfs")
    client = arxiv.Client()
    counter = 1
    for output in client.results(search=res):
        file_name = f"{topic}_{counter}.pdf"
        print(file_name)
        output.download_pdf(filename=f"{file_name}")
        full_text = get_full_text(file_name).replace("\n"," ")
        title = output.title.replace("\n"," ")
        author = ", ".join([x.name for x in output.authors])
        pub_date = output.published
        source_url = output.pdf_url.replace("\n"," ")
        summary = output.summary.replace("\n"," ")
        keywords = ", ".join(output.categories).replace("\n"," ")
        values = {"title":title,"author":author,"pub_date":pub_date,"source_url":source_url,"summary":summary,"full_text":full_text,"keywords":keywords,"data_source":"Arxiv"}
        master_df.append(values)
        counter+=1
    df1 = pd.DataFrame(master_df)
    os.chdir(r"..\\")
    df1.to_csv(r"output\arxiv_results.csv")
def get_full_text(path_name:str):
    loader = PdfReader(path_name)
    pages = " ".join([page.extract_text() for page in loader.pages])
    pages = pages.strip(r"./ \\")
    pages = pages.replace("\"","")
    pages = pages.replace("\'","")
    return pages
if __name__ == "__main__":
    load_pdfs("AI spring")