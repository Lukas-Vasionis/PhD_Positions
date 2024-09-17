import datetime

from bs4 import BeautifulSoup
import utils.scraping_utils as su
import os
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
        'description': job_description,
        'deadline': deadline.replace(". ", " "),
        'url': job_link,
        'location': location,
        'employment_type': employment_type,
        'date_scraped': datetime.date.today(),
    }


jobs_structured=[job_to_structure(x) for x in jobs]



tbl_name=os.path.basename(__file__).replace(".py","")
su.save_to_db_as_tbl(scraped_data=jobs_structured, table_name=tbl_name, db_path=su.get_db_path())

