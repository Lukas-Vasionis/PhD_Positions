import datetime
import os
import traceback
import bs4
import requests
import utils.scraping_utils as su


def show_all_jobs_in_one_page(page_soup, limit_jobs_viewed, page_url):
    """
    Makes sure that the initial page shows all jobs in one page (to avoid pagination).
    First it scrapes element "counter" that tells how many jobs did the query return and stores value in total_jobs_found
    Then compares it to the innitialy set limit of jobs to show (LIMIT_JOBS_VIEWED=10)
        if total_jobs_found - no jobs, terminate further actions
        elif more jobs were found than the set limit to show - adjust view limit to the total_jobs_found and re-scrape page
        elif less jobs were found than the set limit to show - do nothing

    :param page_soup: bs4.soup element of the page with initial limit of jobs viewed
    :param limit_jobs_viewed: initial limit of jobs to view in the page
    :return: bs4.soup element with all job ads in one page
    """
    total_jobs_found = page_soup.find('div', {'id': 'counter'}).text.strip().split()[0]

    if int(total_jobs_found) == 0:  # No jobs found
        print("No Job offerings. Exitting...")
        exit()

    elif int(total_jobs_found) > limit_jobs_viewed:  # Not all jobs are in one page - adjust limit and reload
        limit_jobs_viewed = total_jobs_found

        page_url = page_url.replace("&limit=10&",f"&limit={str(limit_jobs_viewed)}&")
        page = requests.get(url=page_url)
        page_soup = bs4.BeautifulSoup(page.content, "html.parser")

        print(page)
        return page_soup

    elif int(total_jobs_found) <= LIMIT_JOBS_VIEWED:  # All jobs are listed in one page
        return page_soup


def get_raw_list_of_jobs(page_soup):
    page_soup = page_soup.find('table', {'class': 'item-list desktop'})
    page_soup = page_soup.find('tbody')
    elements = page_soup.find_all('tr')
    return elements


def job_to_structure(job):
    job_link = job.find('a', href=True)
    job_title = job_link.get('title')
    job_url = job_link['href']

    institute_info = job.find('div', {'id': 'institut'}).text.strip().split('\n')
    employment_info = institute_info[-1].strip()
    occupation_percent = institute_info[-2].strip()
    location = job.find_all('td')[1].text.strip()
    date_posted = job.find_all('td')[2].text.strip()

    return {
        'title': job_title,
        'institute':institute_info[0],
        'url': job_url,
        'date_posted': date_posted,
        "date_scraped":datetime.date.today(),
        'occupation_percent': occupation_percent,
        'employment_info': employment_info,
        'location': location,
    }


"""
The parameters of url are found in the payload
By playing with page filters and checking payload, you can decipher the url encoding of the filters
"""

LIMIT_JOBS_VIEWED = 10
page_url=f"https://unibe.prospective.ch/?lang=en&offset=0&limit={LIMIT_JOBS_VIEWED}&lang=en&workload=10%2C100&query=&filter_20=1160359&filter_20=1160361&filter_20=1160362&filter_10=1160350&filter_10=1160354&workload=10&workload=100"

try:
    print("Retrieving the data...")
    page = requests.get(
        url=page_url
        )
    print("Processing")
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    soup = show_all_jobs_in_one_page(page_soup=soup, limit_jobs_viewed=LIMIT_JOBS_VIEWED, page_url=page_url)

    jobs_raw = get_raw_list_of_jobs(soup)
    jobs_structured = [job_to_structure(x) for x in jobs_raw]

    # Adding scrape date
    scrape_date=datetime.date.today()
    jobs_structured = [dict(item, date_scraped=scrape_date) for item in jobs_structured]

    if not jobs_structured:
        jobs_structured =  [{
            'title':"",
            'institute':"",
            'url':"",
            'date_posted':"",
            "date_scraped":"",
            'occupation_percent':"",
            'employment_info':"",
            'location':"",
        }]
    print(f"\tSCRAPED JOBS: {len([x for x in jobs_structured if x['title'] != ""])}\n")
    print("Saving...")
    tbl_name=os.path.basename(__file__).replace(".py","")
    su.save_to_db_as_tbl(scraped_data=jobs_structured, table_name=tbl_name, db_path=su.get_db_path())

except Exception:
    print(traceback.format_exc())

# print(df.to_string())
