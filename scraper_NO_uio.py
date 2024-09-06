import bs4
import requests
from pprint import pprint
from bs4 import BeautifulSoup
import pandas as pd

page = requests.get("https://www.uio.no/english/about/vacancies/academic/")
soup=bs4.BeautifulSoup(page.content, "html.parser")

jobs=soup.find_all("div","vrtx-list-item-content")

def job_to_structure(job):

    title_element = job.find('a', class_='item-title')
    job_title = title_element.get_text(strip=True)
    job_link = title_element['href']

    department = job.find('div', class_='department').find('span').get_text(strip=True)
    faculty = job.find('div', class_='topDepartmentName').find('span').get_text(strip=True)
    languages = job.find('div', class_='language').find('span').get_text(strip=True)
    deadline = job.find('div', class_='deadline').find('span').get_text(strip=True)

    return {
        'title': job_title,
        'link': job_link,
        'department': department,
        'faculty': faculty,
        'languages': languages,
        'deadline': deadline
    }

jobs_structured=[job_to_structure(x) for x in jobs]
df=pd.DataFrame(jobs_structured)
