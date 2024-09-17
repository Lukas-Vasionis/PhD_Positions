import datetime
from pprint import pprint

import requests
import pandas as pd
import utils.scraping_utils as su
import os

"""
Found their api. In the url one must set the offset=0 and limit=999. Hope they will never post more than 999 ads...
"""
def convert_array_columns_to_string(df):
    """
    All scraped data is stored as tables with str type only. However, this scraper returns table where some columns are
    array type. So, this f-tion converts them and aligns the table dtypes with tables of other scraping.
    Otherwise, the table fails to upload into db

    Convert array-like columns in a pandas DataFrame to string columns with comma-separated values.

    :param df: (pd.DataFrame): The input pandas DataFrame.
    :return: pd.DataFrame: The DataFrame with array-like columns converted to string columns.
    """

    for column in df.columns:
        # Check if the column is of type list, ndarray, or any iterable (excluding strings)
        if df[column].apply(lambda x: isinstance(x, (list, tuple, set))).any():
            # Convert the column to a string representation with comma-separated values
            df[column] = df[column].apply(lambda x: ', '.join(map(str, x)) if isinstance(x, (list, tuple, set)) else x)

    return df

data=requests.get("https://ohws.prospective.ch/public/v1/medium/1002007/jobs?lang=en&offset=0&limit=9999&f=10:1170342,1180031,1170334,1170341&f=20:1647268,1647271")
data=data.json()

jobs=data['jobs']

jobs_structured=pd.json_normalize(jobs)
jobs_structured=jobs_structured.drop(
    ['szas.sza_benefits',"szas.sza_company_logo","szas.sza_workplace.zip",
     "szas.sza_location.zip","szas.sza_tasks","szas.sza_company_profil","szas.sza_requirements", "szas.sza_workplace.boundingBox",
     "szas.sza_workplace.placeId","id","viewkey"],
                     axis=1)
jobs_structured['date_scraped'] = datetime.date.today()
jobs_structured.rename(columns={"links.directlink":"url"}, inplace=True) # unifying url links as they are key columns in label tables

jobs_structured = convert_array_columns_to_string(jobs_structured)
jobs_structured = jobs_structured.to_dict(orient='records') # Not the most elegant solution, but this f-tion deals nicely with nested jsons

tbl_name=os.path.basename(__file__).replace(".py","")
su.save_to_db_as_tbl(scraped_data=jobs_structured, table_name=tbl_name, db_path=su.get_db_path())


