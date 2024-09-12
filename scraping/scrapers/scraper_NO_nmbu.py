import bs4
import utils.scraping_utils as su
import os
import traceback


def job_to_structure(job):
    # Find the job opportunity item
    job_item = soup.find('a', class_='job-opportunity')

    # Extract job details
    job_link = job_item['href']
    published_date = job_item.find('p', class_='job-opportunity__info').get_text(strip=True).replace('Published date: ',
                                                                                                     '')
    job_title = job_item.find('p', class_='job-opportunity__title').get_text(strip=True)
    job_description = job_item.find('p', class_='job-opportunity__description').get_text(strip=True)

    # Further split the title to get position and deadline
    position, deadline = job_title.split(' - Deadline: ')

    # Structure the extracted data
    return {
        'description': job_description,
        'position': position.strip(),
        'deadline': " ".join(deadline.strip().split(", ")[-2:]),
        'link': job_link,
        'published_date': published_date,
    }



try:
    page = su.get_page_through_selenium("https://www.nmbu.no/en/about/vacancies","wp-block-nmbu-job-opportunities")
    soup = bs4.BeautifulSoup(page, "html.parser")

    jobs = soup.find_all("a","job-opportunity")
    jobs_structured=[job_to_structure(x) for x in jobs]

    tbl_name=os.path.basename(__file__).replace(".py","")
    su.save_to_db_as_tbl(scraped_data=jobs_structured, table_name=tbl_name, db_path=su.get_db_path())

except Exception:
    print(traceback.format_exc())
