# scraper_DE_tum.py
def run():
    import datetime
    import os
    import traceback
    import xml.etree.ElementTree as ET

    import requests
    from .. import scraping_utils as su


    def fetch_and_parse_xml(url):
        # Fetch the XML data from the URL
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful

        # Parse the XML content (response.content is the bytes-like object)
        root = ET.fromstring(response.content)

        # Define namespaces based on the XML structure
        namespaces = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'sy': 'http://purl.org/rss/1.0/modules/syndication/',
            'rss': 'http://purl.org/rss/1.0/',
            'tum': 'http://portal.mytum.de/namspaces/tum',
            'content': 'http://purl.org/rss/1.0/modules/content/'
        }

        # List to store structured data
        jobs_structured = []

        # Iterate over each <item> in the XML
        for item in root.findall('channel/item'):
            job = {
                'title': item.find('title').text,
                'url': item.find('link').text,
                'description': item.find('description').text,
                'pubDate': item.find('pubDate').text,
                'guid': item.find('guid').text,
                'publisher': item.find('dc:publisher', namespaces).text if item.find('dc:publisher', namespaces) is not None else None,
                'author': item.find('author').text,
                'creator': item.find('dc:creator', namespaces).text if item.find('dc:creator', namespaces) is not None else None,
                'category': item.find('category').text,
                'date_scraped':datetime.date.today()
            }
            jobs_structured.append(job)

        return jobs_structured




    attempts=3
    while attempts!=0:
        try:
            url = "https://portal.mytum.de/jobs/wissenschaftler/asRss"
            jobs_structured = fetch_and_parse_xml(url)

            if not jobs_structured:

                jobs_structured={
                'title': "",
                'url': "",
                'description': "",
                'pubDate': "",
                'guid': "",
                'publisher': "",
                'author': "",
                'creator': "",
                'category': "",
                'date_scraped':""
            }
            print(f"\tSCRAPED JOBS: {len([x for x in jobs_structured if x['title'] != ""])}\n")

            tbl_name=os.path.basename(__file__).replace(".py","")
            su.save_to_db_as_tbl(scraped_data=jobs_structured, table_name=f"raw_{tbl_name}", db_path=su.get_db_path())

            break

        except Exception as e:
            print("Trying again")
            attempts=-1
            if attempts == -1:
                print(traceback.format_exc())