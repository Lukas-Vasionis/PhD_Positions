import datetime

import bs4
import requests
import utils.scraping_utils as su
import os
page = requests.get("https://www.nord.no/en/about/vacancies")
soup=bs4.BeautifulSoup(page.content, "html.parser")

jobs=soup.find_all("div","jobbnorge-feed-item")

def job_to_structure(job):

    link_element = job.find('a')
    job_link = link_element['href']
    job_title = job.find('div', class_='jobbnorge-heading').find('span').get_text(strip=True)

    department = job.find('div', class_='jobbnorge-department-mame').get_text(strip=True)
    deadline = job.find('div', class_='jobbnorge-application-deadline').get_text(strip=True).replace(
        'Application deadline:', '').strip()
    category = job.find('div', class_='jobbnorge-category').get_text(strip=True)

    return {
        'title': job_title,
        'department': department,
        'deadline': " ".join(deadline.strip().split(", ")[-2:]),
        'url': job_link,
        'category': category,
        'date_scraped': datetime.date.today(),
    }

jobs_structured=[job_to_structure(x) for x in jobs]
if not jobs_structured:
    jobs_structured = [{
        'title': '',
        'department': '',
        'deadline': "",
        'url': "",
        'category': "",
        'date_scraped': "",
    }]
print(f"\tSCRAPED JOBS: {len([x for x in jobs_structured if x['title'] != ""])}\n")

tbl_name=os.path.basename(__file__).replace(".py","")
su.save_to_db_as_tbl(scraped_data=jobs_structured, table_name=tbl_name, db_path=su.get_db_path())


