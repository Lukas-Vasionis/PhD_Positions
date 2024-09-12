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
        'link': job_link,
        'location': location,
        'employment_type': employment_type,
    }


jobs_structured=[job_to_structure(x) for x in jobs]

def get_db_path(relative_path="../db/phd_jobs_in_schengen.db"):
    # When executing from execute_scrapers files, the program cant find the path of database.
    # This is caused by different db relevant paths between this script and execute_scrapers scrips
    # Hence, this function.

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the absolute path to the database
    return os.path.join(script_dir, relative_path)

tbl_name=os.path.basename(__file__).replace(".py","")
su.save_to_db_as_tbl(scraped_data=jobs_structured, table_name=tbl_name, db_path=get_db_path())

