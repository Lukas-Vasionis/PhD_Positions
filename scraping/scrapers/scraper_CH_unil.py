import datetime
import traceback
from selenium.webdriver.support.wait import WebDriverWait

import time
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import utils.scraping_utils as su
import os

class ScrUniL:
    def __init__(self, driver):
        self.driver=driver

    def expand_listing_to_50(self):
        """
        Clicks on button that expand list to 50 elements per page. Reduces number of page itterations
        :param driver: Web Driver
        :return: None
        """
        # Wait for the dropdown to be visible
        wait = WebDriverWait(self.driver, 10)
        dropdown_element = wait.until(EC.presence_of_element_located((By.ID, "41:")))

        # Initialize Select class and choose the option with value "50"
        select = Select(dropdown_element)
        select.select_by_value("50")

    def is_driver_in_the_last_page(self):

        """
        Checks if driver is in the last page or not. Scrapes and compares number of current page and the last page in the list
        :param driver: Web Driver
        :return: bool, is current page is the last page?
        """

        # Wait because page needs time to update after entering the next page
        time.sleep(1)

        # Locate the list item containing the page information
        pagination_element = self.driver.find_element(By.ID, "40:_pageIndex")

        # Extract the current page number from the input field
        current_page_number = pagination_element.find_element(By.ID, "40:index").get_attribute("value")

        # Extract the last page number from the text within the same element
        last_page_number_text = pagination_element.text
        last_page_number = last_page_number_text.split()[
            -1]  # Extracts the last word in the string, which is the page number

        return str(current_page_number) == str(last_page_number)

    def click_next_page(self):
        """
        Clicks next page button
        :param driver:
        :return: None
        """
        try:
            # Locate the button "Next Page"
            wait = WebDriverWait(self.driver, 10)
            next_page_element = wait.until(EC.presence_of_element_located((By.ID, "40:_next_link")))

            # Click the 'Next Page' button
            next_page_element.click()
        except Exception as e:
            print(e)
            self.driver.quit()

class JobLists:
    def __init__(self):
        # container to collect data of jobs
        self.list_all_jobs=[]


    def collect_raw_lists(self, driver):
        def get_job_list():
            """
            Gets html of all job ad elements in the page
            :return: list of job html elements
            """
            job_list = driver.find_elements(By.CLASS_NAME, "jobResultItem")
            job_html_list = [job.get_attribute('outerHTML') for job in job_list]

            return job_html_list

        # From driver in current page, extracts raw html strings of job description
        job_raw_list=get_job_list()

        # Add to the rest of the lists
        self.list_all_jobs += job_raw_list
        return self
    def process_raw_lists(self):

        def structure_job(job):
            """
            Structures html element into dictionary of a single job ad
            :param job: str, html element of the job
            :return: dict of job details
            """
            # Parse the job HTML using BeautifulSoup
            soup = BeautifulSoup(job, 'html.parser')
            try:
                # Extract job title and link
                job_title_element = soup.find('a', class_='jobTitle')
                job_title = job_title_element.get_text(strip=True) if job_title_element else 'N/A'

                # Extract and process link
                job_link = job_title_element['href'] if job_title_element else 'N/A'
                job_link = "https://career5.successfactors.eu/"+ job_link.split("&selected_lang")[0]

                # Extract requisition ID and posted date
                note_section = soup.find('div', class_='noteSection')
                requisition_id = note_section.find('span', class_='jobContentEM').get_text(
                    strip=True) if note_section and note_section.find('span', class_='jobContentEM') else 'N/A'
                posted_date = note_section.find_all('span', class_='jobContentEM')[1].get_text(
                    strip=True) if note_section and len(note_section.find_all('span', class_='jobContentEM')) > 1 else 'N/A'
                posted_date = posted_date.replace("Posted on ","")
                type_of_position = \
                note_section.find('span', {'aria-label': lambda x: x and 'Type of position' in x}).get('onclick').split('["')[
                    1].split('"]')[0] if note_section and note_section.find('span', {
                    'aria-label': lambda x: x and 'Type of position' in x}) else 'N/A'
                area_of_activity = \
                note_section.find('span', {'aria-label': lambda x: x and 'Area of Activity' in x}).get('onclick').split('["')[
                    1].split('"]')[0] if note_section and note_section.find('span', {
                    'aria-label': lambda x: x and 'Area of Activity' in x}) else 'N/A'
                rate_of_participation = \
                note_section.find('span', {'aria-label': lambda x: x and 'Rate of Participation' in x}).get('onclick').split(
                    '["')[1].split('"]')[0] if note_section and note_section.find('span', {
                    'aria-label': lambda x: x and 'Rate of Participation' in x}) else 'N/A'
                faculty_service = \
                note_section.find('span', {'aria-label': lambda x: x and 'Faculty / Service' in x}).get('onclick').split('["')[
                    1].split('"]')[0] if note_section and note_section.find('span', {
                    'aria-label': lambda x: x and 'Faculty / Service' in x}) else 'N/A'
                personnel_category = \
                note_section.find('span', {'aria-label': lambda x: x and 'Personnel Category' in x}).get('onclick').split('["')[
                    1].split('"]')[0] if note_section and note_section.find('span', {
                    'aria-label': lambda x: x and 'Personnel Category' in x}) else 'N/A'

                # Append the extracted data to the list
                return {
                    "title": job_title,
                    "Faculty / Service": faculty_service,
                    "Type of Position": type_of_position,
                    "Rate of Participation": rate_of_participation,
                    "Posted Date": posted_date,
                    "Area of Activity": area_of_activity,
                    "url": job_link,
                    "Personnel Category": personnel_category,
                    "Requisition ID": requisition_id,
                    "date_scraped":datetime.date.today(),
                }

            except:
                print(traceback.format_exc())
                print(soup.prettify())

        self.list_all_jobs = [structure_job(x) for x in self.list_all_jobs]
        return self


"""
Start
"""

url="https://career5.successfactors.eu/career?company=universitdP&career_ns=job_listing_summary"
# Executes the driver of job listings page

# Initiate scraper class
scraper_unil=ScrUniL(su.get_page_through_selenium(page=url,
                                    ad_element="41:_outer",
                                    return_driver=True))
# Container for job ads
list_all_jobs=JobLists()

# Expands the amount of job ads per page
scraper_unil.expand_listing_to_50()
time.sleep(0.5) # Need to wait for element to refresh. Otherwise, retruns initial list of len 10
while True:
    # Scrape, add raw data into the list_all_jobs
    list_all_jobs.collect_raw_lists(scraper_unil.driver)
    print(len(list_all_jobs.list_all_jobs))

    # Check if driver is on the last page. If yes - break
    if scraper_unil.is_driver_in_the_last_page():

        break
    else:
        scraper_unil.click_next_page()
scraper_unil.driver.quit()

print("Structuring data")
list_all_jobs.process_raw_lists()
jobs_structured=list_all_jobs.list_all_jobs

tbl_name=os.path.basename(__file__).replace(".py","")
su.save_to_db_as_tbl(scraped_data=jobs_structured, table_name=tbl_name, db_path=su.get_db_path())

