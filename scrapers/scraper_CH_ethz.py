import bs4
import utils.scraping_utils as su
import os


page = su.get_page_through_selenium("https://jobs.ethz.ch/","job-ad__wrapper")

soup = bs4.BeautifulSoup(page, "html.parser")

jobs = soup.find_all("li","job-ad__item__wrapper")

# contract types required to scrape job details more dynamicaly. Used only within function
contract_types = ['fixed-term', 'permanent', 'Lehrstelle', 'unbefristet', 'befristet']
def job_to_structure(job):
    link_element = job.find('a', class_='job-ad__item__link')
    job_link = "https://www.ethz.ch" + link_element['href']  # Assume the link is relative; prepend the base URL

    job_title = job.find('div', class_='job-ad__item__title').get_text(strip=True)
    job_details = job.find('div', class_='job-ad__item__details').get_text(strip=True)
    job_company_info = job.find('div', class_='job-ad__item__company').get_text(strip=True)

    # Split job_details dynamically
    details_parts = job_details.split(',')
    work_time_percentage = next((part.strip() for part in details_parts if '%' in part), None)
    city = details_parts[1].strip() if len(details_parts) > 1 else None
    contract_type = next((part.strip() for part in details_parts if part.strip() in contract_types), None)

    # Split job_company_info to get deadline and department/company
    deadline, company = job_company_info.split('|',1)
    deadline = deadline.strip()
    company = company.strip()

    # Structure the extracted data
    return {
        'title': job_title,
        'link': job_link,
        'work_time_percentage': work_time_percentage,
        'city': city,
        'contract_type': contract_type,
        'deadline': deadline,
        'company': company
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


