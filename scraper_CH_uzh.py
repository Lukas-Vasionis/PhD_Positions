import json

import bs4
import requests
from pprint import pprint
from bs4 import BeautifulSoup
import pandas as pd
from utils import scraping_utils as su

"""
Found their api. In the url one must set the offset=0 and limit=999. Hope they will never post more than 999 ads...
"""
data=requests.get("https://ohws.prospective.ch/public/v1/medium/1002007/jobs?lang=en&offset=0&limit=999")
data=data.json()

jobs=data['jobs']

df=pd.json_normalize(jobs)
print(df.to_string())
