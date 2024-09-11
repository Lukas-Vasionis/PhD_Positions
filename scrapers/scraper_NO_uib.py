import os

import bs4
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
        'link': job_link,
        'department': department,
        'deadline': deadline
    }

jobs_structured = [job_to_structure(x) for x in jobs]

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
