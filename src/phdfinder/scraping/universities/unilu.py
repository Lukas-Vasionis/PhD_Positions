# scraper_LX_unilu.py
def run():
    import datetime
    import os

    import requests
    from .. import scraping_utils as su

    # URL for the request with updated parameters
    url = "https://emea3.recruitmentplatform.com/syndicated/lay/jsoutputinitrapido.cfm"

    # Parameters for the request
    params = {
        "ID": "QMUFK026203F3VBQB7V7VV4S8", "LG": "UK", "mask": "karriereseiten", "mtbrwchk": "nok", "browserchk": "no",
        "JobAdLG": "UK", "LOV52": "11696", "SUBDEPT2": "All", "LOV53": "11737", "keywords": "", "Resultsperpage": "999",
        "srcsubmit": "Search", "statlog": "1", "page1": "index.html", "component": "lay9999_lst400a", "rapido": "false",
    }

    # Headers for the request, excluding invalid ones
    headers = {}

    # Send the GET request with parameters
    response = requests.get(url, headers=headers,
                            params=params
                            )

    import re

    from bs4 import BeautifulSoup

    content=response.text

    # Extract the HTML within document.write
    html_content = re.search(r'document.write\("(.*)"\);', content, re.DOTALL).group(1)

    # Unescape HTML (because it may contain escaped characters like \n, \t, etc.)
    html_content = bytes(html_content, "utf-8").decode("unicode_escape")

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract job listings
    jobs_structured = []
    for row in soup.select("tr[class^='Lst-BG']"):
        title_element = row.find("td", {"class": "Lst-Desc1T"}) or row.find("td", {"class": "Lst-Desc2T"})
        contract_type_element = row.find("td", {"class": "Lst-Desc12"}) or row.find("td", {"class": "Lst-Desc22"})

        if title_element and contract_type_element:
            job_title = title_element.get_text(strip=True)
            job_link = title_element.find("a")["href"] if title_element.find("a") else None
            contract_type = contract_type_element.get_text(strip=True)

            jobs_structured.append({
                "title": job_title.replace("(Please note: this link will open the page in a new browser window.)",""),
                "url": "https://recruitment.uni.lu/en/"+job_link,
                'deadline': "",
                "contract_type": contract_type,
                'date_scraped': datetime.date.today()
            })

    print(f"\tSCRAPED JOBS: {len([x for x in jobs_structured if x['title'] != ""])}\n")

    tbl_name=os.path.basename(__file__).replace(".py","")
    su.save_to_db_as_tbl(scraped_data=jobs_structured, table_name=f"raw_{tbl_name}", db_path=su.get_db_path())
