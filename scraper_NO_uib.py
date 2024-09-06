import bs4
import requests
from pprint import pprint
from bs4 import BeautifulSoup
import pandas as pd

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
        'link': job_link,
        'department': department,
        'deadline': deadline
    }

jobs_structured = [job_to_structure(x) for x in jobs]
df = pd.DataFrame(jobs_structured)
print(df.to_string())