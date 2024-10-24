import datetime

import bs4
import requests
from pprint import pprint
import utils.scraping_utils as su
import os
import traceback


def get_raw_list_of_jobs(page_soup) -> list:
    # Check if any jobs are listed
    page_soup_jobs=page_soup.find("ul", class_="items")

    if page_soup_jobs: #If yes, scrape them
        raw_elements=page_soup_jobs.find_all("div", class_="vrtx-list-item-content")

    else: # If no, check if page writes no vacancies
        if page_soup.find("p", class_="vrtx-empty-message").text=='No vacancies.':
            print("No vacancies.")
            raw_elements='No vacancies.'
        else: # Else could mean the elements has been renamed. Check the page
            raw_elements= ""
    return raw_elements

def structure_job_info(job_raw) -> dict:
    try:
        title_element = job_raw.find('a', class_='item-title')
        job_title = title_element.text.strip() if title_element else None
        job_url = title_element['href'] if title_element and 'href' in title_element.attrs else None

        description_element = job_raw.find('div', class_='item-description')

        # Use safer element finding with defaults to avoid NoneType errors
        department_element = description_element.find('div', class_='department').find(
            'span') if description_element else None
        faculty_element = description_element.find('div', class_='topDepartmentName').find(
            'span') if description_element else None
        language_element = description_element.find('div', class_='language').find('span') if description_element else None
        deadline_element = description_element.find('div', class_='deadline').find('span') if description_element else None

        department = department_element.text.strip() if department_element else None
        faculty = faculty_element.text.strip() if faculty_element else None
        language = language_element.text.strip() if language_element else None
        deadline = deadline_element.text.strip() if deadline_element else None
    except:

        pprint(f"JOb raw: {job_raw}")
        print(traceback.format_exc())
        exit()
    return {
            'title': job_title,
            'department': department,
            'deadline': " ".join(deadline.strip().split(", ")[-2:]),
            'language': language,
            'url': job_url,
            'faculty': faculty,
            'date_scraped':datetime.date.today(),
        }


pages=[
    'https://www.med.uio.no/english/about/vacancies/index.html',
    "https://www.mn.uio.no/english/about/vacancies/index.html",
       "https://www.sum.uio.no/english/about/vacancies/"
]

all_structured_data=[]
try:
    for page_url in pages:
        # page_url=f"https://www.uio.no/english/about/vacancies/academic/"

        print(f"Retrieving the data... {page_url}")
        page = requests.get(url=page_url)

        soup = bs4.BeautifulSoup(page.content, "html.parser")

        jobs_raw = get_raw_list_of_jobs(soup)
        if (jobs_raw is None) or type(jobs_raw)==str:
            print(f"No data? Failed to scrape, check the page {page_url}")
            continue

        jobs_structured = [structure_job_info(x) for x in jobs_raw]
        all_structured_data += jobs_structured

    print("Saving...")
    tbl_name=os.path.basename(__file__).replace(".py","")
    su.save_to_db_as_tbl(scraped_data=all_structured_data, table_name=tbl_name, db_path=su.get_db_path())

except Exception as e:
    print(e)
    print(traceback.format_exc())

