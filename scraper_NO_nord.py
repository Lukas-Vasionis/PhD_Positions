import bs4
import requests
from pprint import pprint
from bs4 import BeautifulSoup
import pandas as pd

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
        'link': job_link,
        'department': department,
        'deadline': deadline,
        'category': category
    }

jobs_structured=[job_to_structure(x) for x in jobs]
df=pd.DataFrame(jobs_structured)
print(df.to_string())