import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from utils import scraping_utils as su


page_content = su.get_page_through_selenium("https://www.ntnu.edu/vacancies", ad_element="card-deck")

# Parse the page content with BeautifulSoup
soup = BeautifulSoup(page_content, "html.parser")

# Find the 'card-deck' div
jobs = soup.find("div", class_="card-deck")

def job_to_structure(job):
    job_link = job['href']
    job_title = job.find('h2', class_='card-title').get_text(strip=True)
    job_description = job.find('p', class_='card-text text-dark').get_text(strip=True)

    location = job.find('div', class_='card-text text-muted text-uppercase').get_text(strip=True)
    employment_type = job.find_all('div', class_='card-text text-muted text-uppercase')[1].get_text(strip=True)
    deadline = job.find_all('div', class_='card-text text-muted text-uppercase')[2].get_text(strip=True)

    return {
        'title': job_title,
        'link': job_link,
        'description': job_description,
        'location': location,
        'employment_type': employment_type,
        'deadline': deadline
    }

jobs_structured=[job_to_structure(x) for x in jobs]
df=pd.DataFrame(jobs_structured)
print(df.to_string())