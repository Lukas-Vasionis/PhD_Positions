## In short... 
The app scrapes primary sources of PhD vacancies (university pages) and views them in the
single app interface. Here you can label the vacancies to follow which of them you already looked through.
The data is updated once a week.

## The data
Currently, the scrapers are designed to collect PhD vacancies specifically in biomedical 
sciences. However, since some universities publish all positions—ranging from Postdocs to 
administrative roles—in a single listing, some scrapers may capture unrelated vacancies in
fields like economics, gender studies, or theology.

In the future, I plan to explore filtering these using a language model. Until then, consider 
it a devine nudge towards a new career path and call it a feature. ¯\_(ツ)_/¯

## Why the struggle ?

So I am looking for a PhD in Europe and I have to constantly monitor multiple university pages for open positions which is painful.
So, being a programmer I figured I could automate this monitoring by writing a few scrapers 
and displaying gathered data in a single interface of a streamlit app. Now with a few clicks I have the newest data in one place. 
Moreover, I can mark which positions to ignore, and which are interesting. 


The app is engineered with intend to upscale it. Over the time I will add scrapers for more universities. 

!['App iamge'](docs/img/app_demo.png)
# Usage

Run these commands locally be executing these commands in the **terminal**:
- Clone the repo and move to the root dir of this project
  ```
  git clone https://github.com/Lukas-Vasionis/PhD_Positions.git
  ```
- Get to the root of the project
  ```
  cd PhD_Positions
  ```
- Install the requirements
  ```
  pip install poetry              # Installs Poetry if you havent
  poetry install                  # Sets up poetry environment with the project requirements
  ```
  
- Run `poetry run scrape` to gather the data.
- Run `poetry run process` to process the data (parse dates, sort, join, etc.).
- Run `poetry run app` to execute the app locally in your browser

# To do
## Scraping
- Improve parallel processing of scraper execution - sometimes scrapers fail due to it.

## Processing
- Unify columns of tables. Those columns that don't match - display as other info in pop ups or other containers.
- ETH Zurich - Swiss Federal Institute of Technology (CH) - add 'jobs.' to the beginning of job url. 
- Filter data of Swiss Universities - keep only those that offer 90% or more occupancy.
- Reorder columns - put essentials first: "title", "url", "deadline" ... other columns
- Move scraping and processing to Github actions
## Application
- Add filtering for countries
- Update scrapers to filter out non-biomedical, non-phd vacancies
- Create 2nd scraper to scrape deeper data from individual job offers
- Create on button 'Save Labels' for all tables and place it to the side panel near the filters.
- Add option to upload/download of own labels for use in web app
- Add option to download labeled tables as one or multiple datasets
- Add option to update deadline column (or the whole record)
- Add column for specific annotations

# Further institutions to add
- Swiss bioinformatics institute: https://apply.refline.ch/499599/search.html
- University Hospitals
- Netherland Universities
- Swedish Universities
- Finnish Universities