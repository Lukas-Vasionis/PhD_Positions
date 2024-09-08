# from telnetlib import EC

import bs4
import requests
from pprint import pprint
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
import regex as re
from utils import scraping_utils as su

import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC


class ScrUniBas:
    def __init__(self, driver):
        self.driver = driver
        self.jobs_divs=None
        self.jobs_structured=None

    def iterate_and_collect(self):
        """
        Iterates over page pagination,
        Collects div elements of the jobs,
        Stores them into single list

        :return: self; list of job div elements and stores them into self.jobs_divs
        """
        all_job_divs=[]

        while True:


            # CHECK PAGINATION ELEMENT
            try:
                # Wait until the 'pagination' element is loaded
                wait=WebDriverWait(self.driver, 10)
                pagination_element = wait.until(EC.presence_of_element_located((By.ID, "pagination")))
            except:
                self.driver.quit()
                print(Exception)


            # SCRAPE JOB ELEMENT
            try:
                # Scrape job element
                # Parse the page source with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')

                # Find all div elements with class names that start with "job job-"
                job_list_element = soup.find_all('div', class_=re.compile(r'^job job-'))

                # collect into all_jobs_divs list
                all_job_divs.append(job_list_element)
            except:
                self.driver.quit()
                print(Exception)


            # MARK: ACTIVE PAGE AND FINAL PAGE
            try:
                # Creating the dict that marks which page is active and which page is the last (max)
                page_buttons = pagination_element.find_elements(By.CSS_SELECTOR, 'a[id="button-page"]')
                page_indexes=[x.get_attribute("innerHTML") for x in page_buttons]
                page_classes=[x.get_attribute("class") for x in page_buttons]
                pages=dict(zip(page_indexes, page_classes))
            except:
                self.driver.quit()
                print(Exception)


            # DECIDE: MOVE TO NEXT PAGE OR NOT (BREAK AND RETURN)
            try:
                # Checking if scraper is in the last page (checks if scraper is on the last (max) page).
                current_max_page = max(int(button.get_attribute('title').split()[-1]) for button in page_buttons)
                current_active_page =  list(filter(lambda x: pages[x] == 'ui primary button page active', pages))[0]
                print(f"Scraping page: {current_active_page}")

                # if str(current_active_page) == '2': # This one is for debugging
                if str(current_active_page) != str(current_max_page):
                    # Click the "Next" button
                    next_button = self.driver.find_element(By.ID, "button-forward")
                    next_button.click()
                else:
                    # Break and return all_job_divs
                    self.driver.quit()
                    break

            except Exception as e:
                self.driver.quit()
                print(f"An error occurred: {e}")

        # PROCESS
        self.jobs_divs = [y for x in all_job_divs for y in x]

        return self

    def structure_all_jobs(self):
        """
        Intakes self.jobs_divs and structures them into list of dicts
        :return: list of dicts
        """
        def job_to_structure(job_element):
            """
            Structures div of a single job ad into a dict
            :param job_element: div element of a job ad
            :return: dict of job details
            """

            # Extract job title, link, and date_posted
            job_title_element = job_element.find('a', class_='job-title')

            job_title = job_title_element.get_text(strip=True)
            job_link = job_title_element['href']
            date_posted = job_element.find('span', class_='job-date').get_text(strip=True)

            res_dict = {
                'title': job_title,
                'link': job_link,
                'date_posted': date_posted
            }
            # Structure the extracted data
            return res_dict

        self.jobs_structured = [job_to_structure(x) for x in self.jobs_divs]

        return self

driver_url = su.get_page_through_selenium(page="https://jobs.unibas.ch/?lang=en",
                                    ad_element="jobs-list",
                                    return_driver=True)

scr_unibas=ScrUniBas(driver=driver_url
           ).iterate_and_collect().structure_all_jobs()

df=pd.DataFrame(scr_unibas.jobs_structured)
print(df.head().to_string())

