# scraper_CH_unibas.py
def run():
    # from telnetlib import EC
    import datetime
    import os

    import bs4
    import regex as re
    import requests
    import phdfinder.scraping.scraping_utils as su
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.wait import WebDriverWait


    def scrape_job_list(source_html):
        # Load html into soup
        soup = bs4.BeautifulSoup(source_html, 'html.parser')
        # Find all div elements with class names that start with "job job-"
        list_job_divs = soup.find_all('div', class_=re.compile(r'^job job-'))

        return list_job_divs

    class ScrUniBas:
        """
        Usage:
        First, scrape div elements of jobs with self.iterate_and_collect()
        Second, structure divs into list of dictionaries with self.structure_all_jobs()

        """
        def __init__(self, method: str):
            """
            :param method: selects method of scraping: 'from_url' or 'from_driver
            """
            self.method=method
            self.driver = None
            self.jobs_divs=None
            self.jobs_structured=None


        def iterate_and_collect(self):

            """
            Depending on value of self.driver, the function picks one of two ways to scrape: via selenium bot, or via request
            (Innitialy, I could not find a way to scrape it via requests so I wrote a bot script. Later, found a way to scrape it via url)
            Both ways returns all_jobs_divs list

            if using url vie reqeusts lib:
                Requests html code of a page via url string that increases viewed jobs in the page to 9999 (see limit argument in url)
                Finds all elements with PhD jobs (see filter details defined in the scrape_with_requests()

            If using bot:
                Iterates over page pagination,
                Collects div elements of the jobs,
                Stores them into single list

            stores all_jobs_divs into self.jobs_divs
            :return: self
            """


            def scrape_with_request() -> list:

                # Scrapes job list elements using url (filter_20=1083152 keeps only PhD ads)
                # r=requests.get("https://jobs.unibas.ch/?lang=en&offset=0&limit=9999&lang=en&query=&filter_20=1083152")
                r=requests.get("https://jobs.unibas.ch/?lang=en&offset=0&limit=9999&lang=en&query=&filter_10=1082962&filter_10=1082964&filter_10=1082966&filter_10=1082968&filter_20=1083152")
                all_jobs_divs = scrape_job_list(r.content)

                return all_jobs_divs

            def scrape_with_bot() -> list:

                self.driver = su.get_page_through_selenium(page="https://jobs.unibas.ch/?lang=en",
                                                    ad_element="jobs-list",
                                                    return_driver=True)

                all_job_divs=[]

                while True:

                    # CHECK PAGINATION ELEMENT
                    try:
                        # Wait until the 'pagination' element is loaded
                        wait=WebDriverWait(self.driver, 10)
                        pagination_element = wait.until(EC.presence_of_element_located((By.ID, "pagination")))
                    except Exception:
                        self.driver.quit()
                        print(Exception)


                    # SCRAPE JOB ELEMENT
                    try:
                        # Scrape job element
                        job_list_elements=scrape_job_list(self.driver.page_source)

                        # collect into all_jobs_divs list
                        all_job_divs.append(job_list_elements)
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
                        current_active_page =  list(filter(lambda x: pages[x]=='ui primary button page active', pages))[0]
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
                jobs_divs = [y for x in all_job_divs for y in x]
                return jobs_divs

            print("Scraping...")
            if self.method=='from_url':
                all_job_divs=scrape_with_request()
            elif self.method=='from_driver':
                all_job_divs=scrape_with_bot()
            else:
                raise ValueError("Invalid attribute of ScrUniBas. Attribute 'method' must be either 'from_url' or 'from_driver")


            self.jobs_divs=all_job_divs

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
                    'url': job_link,
                    'date_posted': date_posted,
                    'date_scraped': datetime.date.today()
                }
                # Structure the extracted data
                return res_dict

            print("Structuring")
            self.jobs_structured = [job_to_structure(x) for x in self.jobs_divs]

            return self


    scr_unibas=ScrUniBas(method="from_url").iterate_and_collect().structure_all_jobs()
    jobs_structured=scr_unibas.jobs_structured

    print(f"\tSCRAPED JOBS: {len([x for x in jobs_structured if x['title'] != ""])}\n")

    tbl_name=os.path.basename(__file__).replace(".py","")
    su.save_to_db_as_tbl(scraped_data=jobs_structured, table_name=f"raw_{tbl_name}", db_path=su.get_db_path())


