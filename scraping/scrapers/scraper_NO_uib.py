import datetime
import os

import bs4
import pandas as pd
import requests
import utils.scraping_utils as su

page = requests.get("https://www.uib.no/en/about/84777/vacant-positions-uib")
soup=bs4.BeautifulSoup(page.content, "html.parser")

jobs=soup.find("ul","uib-vacancies")
jobs=jobs.find_all("li")

def job_to_structure(job):

    # Extract job details
    job_title = job.find('h3').get_text(strip=True)
    job_link = job.find('a')['href']
    job_description = job.find('p').get_text(strip=True)

    # Further split the description to get department and deadline
    department, deadline = job_description.split(' - Application deadline: ')

    # Structure the extracted data
    return {
        'title': job_title,
        'department': department,
        'deadline': " ".join(deadline.strip().split(", ")[-2:]),
        'url': job_link,
        'date_scraped': datetime.date.today(),
    }

jobs_structured = [job_to_structure(x) for x in jobs]
if not jobs_structured:
    jobs_structured={
        'title': "",
        'department': "",
        'deadline': "",
        'url': "",
        'date_scraped': "",
    }
print(f"\tSCRAPED JOBS: {len([x for x in jobs_structured if x['title'] != ""])}\n")

tbl_name=os.path.basename(__file__).replace(".py","")
su.save_to_db_as_tbl(scraped_data=jobs_structured, table_name=tbl_name, db_path=su.get_db_path())
