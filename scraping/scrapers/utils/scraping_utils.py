import inspect
import os
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import polars as pl

def get_page_through_selenium(page, ad_element, return_driver=False):
    """

    :param page: URL of the page to scrape
    :param ad_element: any name of element tag class or other string in plain text of scraped html. This string indicates that the desired element is loaded
    :param return_driver: if TRUE - returns driver instead of page's source code
    :return: str: source code of the page
    """
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    print("Setting up the Chrome WebDriver")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    print("Opening the webpage")
    driver.get(page)

    print("Scraping, looking for ad element")
    # Initialize a maximum wait time (in seconds)
    max_wait_time = 30
    start_time = time.time()

    # Wait until the 'card-deck' element appears or until the timeout is reached
    while True:
        page_content_local = driver.page_source
        if ad_element in page_content_local or time.time() - start_time > max_wait_time:
            break
        time.sleep(1)  # Sleep for a short time before checking again

    # Return one of two: driver (if marked in the f-tion arguments), or else page source_code
    if return_driver:
        return driver
    else:
        # Get the page content
        page_content_local = driver.page_source
        return page_content_local

def get_db_path(relative_path="../../db/phd_jobs_in_schengen.db"):
    # Get the file path of the calling script
    calling_script = inspect.stack()[1].filename  # Get the filename of the caller
    # Get the directory of the calling script
    script_dir = os.path.dirname(os.path.abspath(calling_script))
    # Construct the absolute path to the database
    absolute_path = os.path.join(script_dir, relative_path)
    return absolute_path

def save_to_db_as_tbl(table_name, scraped_data, db_path):

    df = pl.DataFrame(scraped_data)
    df.write_database(
        table_name.replace(".py","").replace("scraper_",""),
        connection = f"sqlite:///{db_path}",
        if_table_exists = "replace")


