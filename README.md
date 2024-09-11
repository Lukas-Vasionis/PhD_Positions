So I am looking for PhD in Norway and Switzerland 
and I have to constantly monitor multiple university pages for open postions. 
Being a programmer I figured I could automate this monitoring by writing a a few scrapers 
and displaying scraped data in streamlit app. Now I dont need to browse multiple
pages and remember which of them I didn't look yet.

I engineered this program in a way where I could upscale it and easily debug it.

# Usage
Run these commands in the console to perform these tasks
- Install the requirements with `pip install -r requirements.txt`
- Run `./execute_scrapers.py` to gather the data. 
- Run `streamlit run ./steamlit.py`

# To do
## Scraping
- Improve parallel processing of scraper execution - sometimes scrapers fail due to it.

## Processing
- Unify columns of tables. Those columns that don't match - display as other info in pop ups or other containers.
- ETH Zurich - Swiss Federal Institute of Technology (CH) - add 'jobs.' to the beginning of job url. 
- Filter data of Swiss Universities - keep only those that offer 90% or more occupancy.

## Application
- Add filtering options
