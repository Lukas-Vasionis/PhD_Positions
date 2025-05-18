# scraper_CH_ethz
def run():
    import datetime
    import os
    import bs4
    import phdfinder.scraping.scraping_utils as su
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait


    def select_phd_jobs(driver_page):
        try:
            print("Filtering PhD pages")
            # Wait for the "Stellentyp" dropdown to be clickable and then click it
            stellentyp_dropdown = WebDriverWait(driver_page, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='select-selected' and text()='Stellentyp']"))
            )
            stellentyp_dropdown.click()

            # Wait for the desired option to be visible and click it
            doktorierende_option = WebDriverWait(driver_page, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@class='select-items']/div[text()='Doktorierende']"))
            )
            doktorierende_option.click()

            return driver_page
        except Exception as e:
            print(f"An error occurred: {e}")


    driver_pg = su.get_page_through_selenium("https://jobs.ethz.ch/","job-ad__wrapper", return_driver=True)
    driver_pg = select_phd_jobs(driver_page=driver_pg)

    soup = bs4.BeautifulSoup(driver_pg.page_source, "html.parser")

    jobs = soup.find_all("li","job-ad__item__wrapper")

    # contract types required to scrape job details more dynamicaly. Used only within function
    contract_types = ['fixed-term', 'permanent', 'Lehrstelle', 'unbefristet', 'befristet']


    def job_to_structure(job):
        link_element = job.find('a', class_='job-ad__item__link')
        job_link = "https://jobs.ethz.ch" + link_element['href']  # Assume the link is relative; prepend the base URL

        job_title = job.find('div', class_='job-ad__item__title').get_text(strip=True)
        job_details = job.find('div', class_='job-ad__item__details').get_text(strip=True)
        job_company_info = job.find('div', class_='job-ad__item__company').get_text(strip=True)

        # Split job_details dynamically
        details_parts = job_details.split(',')
        work_time_percentage = next((part.strip() for part in details_parts if '%' in part), None)
        city = details_parts[1].strip() if len(details_parts) > 1 else None
        contract_type = next((part.strip() for part in details_parts if part.strip() in contract_types), None)

        # Split job_company_info to get deadline and department/company
        date_posted, company = job_company_info.split('|',1)
        date_posted = date_posted.strip()
        company = company.strip()

        # Structure the extracted data
        return {
            'title': job_title,
            'company': company,
            'date_posted': date_posted,
            'work_time_percentage': work_time_percentage,
            'url': job_link,
            'city': city,
            'contract_type': contract_type,
            'date_scraped': datetime.date.today()
        }

    jobs_structured=[job_to_structure(x) for x in jobs]
    if not jobs_structured:
        jobs_structured = [{
            'title': "",
            'company': "",
            'date_posted': "",
            'work_time_percentage': "",
            'url': "",
            'city': "",
            'contract_type': "",
            'date_scraped': ""
        }]
    print(f"\tSCRAPED JOBS: {len([x for x in jobs_structured if x['title'] != ""])}\n")

    tbl_name=os.path.basename(__file__)
    su.save_to_db_as_tbl(scraped_data=jobs_structured, table_name=f"raw_{tbl_name}", db_path=su.get_db_path())


