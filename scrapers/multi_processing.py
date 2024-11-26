from concurrent.futures import ThreadPoolExecutor
import techcrunch_scraper
import pdf_reader
import yt_scraper
with ThreadPoolExecutor(max_workers=4) as executor:
    articles = techcrunch_scraper.batch_insert()
    pdfs_1 = lambda : pdf_reader.load_pdfs(topic="ai winter")
    pdfs_2 = lambda : pdf_reader.load_pdfs(topic="ai summer")
    videos = lambda : yt_scraper.batch_insert()
    job_1 = executor.submit(articles)
    job_2 = executor.submit(pdfs_1)
    job_3 = executor.submit(pdfs_2)
    job_4 = executor.submit(videos)
    job_1.result()
    job_2.result()
    job_3.result()
    job_4.result()
