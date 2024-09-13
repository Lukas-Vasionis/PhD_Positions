import pandas as pd
import sqlalchemy
import utils_processing as up

"""
TASKS: 
    Rename columns
        Assign human readable names
        unify column names
    
    Filter:
        only phd Positions 
        english languages
        not behind the deadline
    Values dtypes:
        parse dates
"""

CH_ethz=up.ScrData(tbl_name="scraper_CH_ethz").load_tbl_to_pd()
CH_ethz.filter_by_occupation_percent("work_time_percentage")
CH_ethz.parse_date_columns(list_date_cols=["date_posted"]).sort_by_column(col_name="date_posted", ascend=False)
CH_ethz.save_to_db()
CH_ethz.create_labeling_tbl(col_urls='link').save_to_db(tbl_type='labels')

CH_unibas=up.ScrData(tbl_name="scraper_CH_unibas").load_tbl_to_pd()
CH_unibas.parse_date_columns(['date_posted']).sort_by_column(col_name="date_posted", ascend=False)
CH_unibas.save_to_db()
CH_unibas.create_labeling_tbl(col_urls='link').save_to_db(tbl_type='labels')

CH_unibe = up.ScrData(tbl_name="scraper_CH_unibe").load_tbl_to_pd()
CH_unibe.parse_date_columns(['date_posted']).sort_by_column(col_name="date_posted", ascend=False)
CH_unibe.save_to_db()
CH_unibe.create_labeling_tbl(col_urls='job_url').save_to_db(tbl_type='labels')



CH_unil = up.ScrData(tbl_name="scraper_CH_unil").load_tbl_to_pd()
CH_unil.filter_CH_unil_PhD().filter_CH_unil_Area_Of_Activity()
CH_unil.parse_date_columns(list_date_cols=['Posted Date'], date_format='%m/%d/%Y').sort_by_column('Posted Date', ascend=False)
CH_unil.save_to_db()
CH_unil.create_labeling_tbl(col_urls='Job Link').save_to_db(tbl_type='labels')


CH_uzh = up.ScrData(tbl_name="scraper_CH_uzh").load_tbl_to_pd()
CH_uzh.filter_by_occupation_percent("szas.sza_pensum.max")
CH_uzh.save_to_db()
CH_uzh.create_labeling_tbl(col_urls='links.directlink').save_to_db(tbl_type='labels')


NO_nmbu = up.ScrData(tbl_name="scraper_NO_nmbu").load_tbl_to_pd()
NO_nmbu.parse_date_columns(list_date_cols=["deadline"], date_format='%B %d %Y').sort_by_column(col_name="deadline", ascend=False)
NO_nmbu.save_to_db()
NO_nmbu.create_labeling_tbl(col_urls='link').save_to_db(tbl_type='labels')


NO_nord = up.ScrData(tbl_name="scraper_NO_nord").load_tbl_to_pd()
NO_nord.parse_date_columns(list_date_cols=["deadline"], date_format='%B %d %Y').sort_by_column(col_name="deadline", ascend=False)
NO_nord.save_to_db()
NO_nord.create_labeling_tbl(col_urls='link').save_to_db(tbl_type='labels')

NO_ntnu = up.ScrData(tbl_name="scraper_NO_ntnu").load_tbl_to_pd()
NO_ntnu.parse_date_columns(list_date_cols=["deadline"], date_format='%d %b %Y').sort_by_column(col_name="deadline", ascend=False)
NO_ntnu.save_to_db()
NO_ntnu.create_labeling_tbl(col_urls='link').save_to_db(tbl_type='labels')

NO_uib = up.ScrData(tbl_name="scraper_NO_uib").load_tbl_to_pd()
NO_uib = NO_uib.parse_date_columns(list_date_cols=["deadline"], date_format='%B %d %Y').sort_by_column(col_name="deadline", ascend=False)
NO_uib.save_to_db()
NO_uib.create_labeling_tbl(col_urls='link').save_to_db(tbl_type='labels')

NO_uio = up.ScrData(tbl_name="scraper_NO_uio").load_tbl_to_pd()
NO_uib = NO_uib.parse_date_columns(list_date_cols=["deadline"], date_format='%B %d %Y').sort_by_column(col_name="deadline", ascend=False)
NO_uio.save_to_db()
NO_uio.create_labeling_tbl(col_urls='job_url').save_to_db(tbl_type='labels')


