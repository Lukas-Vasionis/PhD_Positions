import bs4
import requests
from pprint import pprint
from bs4 import BeautifulSoup
import pandas as pd
from utils import scraping_utils as su

page = su.get_page_through_selenium("https://www.nmbu.no/en/about/vacancies","wp-block-nmbu-job-opportunities")

soup = bs4.BeautifulSoup(page, "html.parser")

jobs = soup.find_all("a","job-opportunity")

def job_to_structure(job):
    # Find the job opportunity item
    job_item = soup.find('a', class_='job-opportunity')

    # Extract job details
    job_link = job_item['href']
    published_date = job_item.find('p', class_='job-opportunity__info').get_text(strip=True).replace('Published date: ',
                                                                                                     '')
    job_title = job_item.find('p', class_='job-opportunity__title').get_text(strip=True)
    job_description = job_item.find('p', class_='job-opportunity__description').get_text(strip=True)

    # Further split the title to get position and deadline
    position, deadline = job_title.split(' - Deadline: ')

    # Structure the extracted data
    return {
        'link': job_link,
        'published_date': published_date,
        'position': position.strip(),
        'deadline': deadline.strip(),
        'description': job_description
    }

jobs_structured=[job_to_structure(x) for x in jobs]
df=pd.DataFrame(jobs_structured)
print(df.to_string())