import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_page_through_selenium(page, ad_element):
    """

    :param page: URL of the page to scrape
    :param ad_element: any name of element tag class or other string in plain text of scraped html. This string indicates that the desired element is loaded
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

    # Get the page content
    page_content_local = driver.page_source
    return page_content_local