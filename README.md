## In short... 
The app scrapes primary sources of PhD vacancies and views them in the
app where you can label the vacancies to follow which of them you already looked through.

## The data
So far, the scrapers take only vacancies of PhDs in biomedical science. However, some 
universities post everything in one list. So, some scrapers take everything and you 
may find vacancies for Post-docs or Managers in fields like gender studies or theology.
Maybe it's a sign from the above for a career change? Who knows.  ¯\_(ツ)_/¯

## Why the struggle ?

So I am looking for PhD in Norway and Switzerland 
and I have to constantly monitor multiple university pages for open positions and that is painful.
So, being a programmer I figured I could automate this monitoring by writing a few scrapers 
and displaying gathered data in a single interface of a streamlit app. Now with few clicks I have the newest data in one place. Moreover - I can mark which positions to ignore, and which are interesting.


The app is engineered with intend to upscale it. Over the time I will add scrapers for more universities. 

!['App iamge'](docs/img/app_demo.png)
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
