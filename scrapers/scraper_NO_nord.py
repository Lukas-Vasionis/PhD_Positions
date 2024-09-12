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
        'department': department,
        'title': job_title,
        'deadline': " ".join(deadline.strip().split(", ")[-2:]),
        'link': job_link,
        'category': category
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


