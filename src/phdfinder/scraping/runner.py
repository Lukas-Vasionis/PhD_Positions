from tqdm import tqdm
import logging
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    filename="logs/scraping_errors.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

from phdfinder.scraping.universities import (
    uio,
    ntnu,
    uib,
    nord,
    nmbu,
    unibas,
    unibe,
    unil,
    uzh,
    ethz,
)

def run_all_scrapers():
    scrapers = [
        uio.run,
        ntnu.run,
        uib.run,
        nord.run,
        nmbu.run,
        unibas.run,
        unibe.run,
        unil.run,
        uzh.run,
        ethz.run,
    ]

    for scraper_fn in tqdm(scrapers):
        try:
            print(f"Running {scraper_fn.__module__}...")
            scraper_fn()
            print(f"✅ Completed {scraper_fn.__module__}")
        except Exception as e:
            logging.error(f"Failed {scraper_fn.__module__}", exc_info=True)
