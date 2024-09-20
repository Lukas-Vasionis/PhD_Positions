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

CH_ethz=up.ScrData(tbl_name="CH_ethz").load_tbl_to_pd()
CH_ethz.filter_by_occupation_percent("work_time_percentage")
CH_ethz.parse_date_columns(list_date_cols=["date_posted"], date_format='%d.%m.%Y').sort_by_column(col_name=["date_scraped","date_posted"], ascend=False)
CH_ethz.update_scraper_tbl().save_to_db()
CH_ethz.create_or_update_tbl_labels()

CH_unibas=up.ScrData(tbl_name="CH_unibas").load_tbl_to_pd()
CH_unibas.parse_date_columns(['date_posted']).sort_by_column(col_name=["date_scraped","date_posted"], ascend=False)
CH_unibas.update_scraper_tbl().save_to_db()
CH_unibas.create_or_update_tbl_labels()

CH_unibe = up.ScrData(tbl_name="CH_unibe").load_tbl_to_pd()
CH_unibe.parse_date_columns(['date_posted']).sort_by_column(col_name=["date_scraped","date_posted"], ascend=False)
CH_unibe.update_scraper_tbl().save_to_db()
CH_unibe.create_or_update_tbl_labels()

CH_unil = up.ScrData(tbl_name="CH_unil").load_tbl_to_pd()
CH_unil.filter_CH_unil_PhD().filter_CH_unil_Area_Of_Activity()
CH_unil.parse_date_columns(list_date_cols=['Posted Date'], date_format='%m/%d/%Y').sort_by_column(col_name=["date_scraped",'Posted Date'], ascend=False)
CH_unil.update_scraper_tbl().save_to_db()
CH_unil.create_or_update_tbl_labels()


CH_uzh = up.ScrData(tbl_name="CH_uzh").load_tbl_to_pd()
CH_uzh.filter_by_occupation_percent("szas.sza_pensum.max")
CH_uzh.update_scraper_tbl().save_to_db()
CH_uzh.create_or_update_tbl_labels()


NO_nmbu = up.ScrData(tbl_name="NO_nmbu").load_tbl_to_pd()
NO_nmbu.parse_date_columns(list_date_cols=["deadline"], date_format='%B %d %Y').sort_by_column(col_name="deadline", ascend=False)
NO_nmbu.update_scraper_tbl().save_to_db()
NO_nmbu.create_or_update_tbl_labels()


NO_nord = up.ScrData(tbl_name="NO_nord").load_tbl_to_pd()
NO_nord.parse_date_columns(list_date_cols=["deadline"], date_format='%B %d %Y').sort_by_column(col_name=["date_scraped","deadline"], ascend=False)
NO_nord.update_scraper_tbl().save_to_db()
NO_nord.create_or_update_tbl_labels()

NO_ntnu = up.ScrData(tbl_name="NO_ntnu").load_tbl_to_pd()
NO_ntnu.parse_date_columns(list_date_cols=["deadline"], date_format='%d %b %Y').sort_by_column(col_name=["date_scraped","deadline"], ascend=False)
NO_ntnu.update_scraper_tbl().save_to_db()
NO_ntnu.create_or_update_tbl_labels()

NO_uib = up.ScrData(tbl_name="NO_uib").load_tbl_to_pd()
NO_uib = NO_uib.parse_date_columns(list_date_cols=["deadline"], date_format='%B %d %Y').sort_by_column(col_name=["date_scraped","deadline"], ascend=False)
NO_uib.update_scraper_tbl().save_to_db()
NO_uib.create_or_update_tbl_labels()

NO_uio = up.ScrData(tbl_name="NO_uio").load_tbl_to_pd()
NO_uio.parse_date_columns(list_date_cols=["deadline"], date_format='%B %d %Y').sort_by_column(col_name=["date_scraped","deadline"], ascend=False)
NO_uio.update_scraper_tbl().save_to_db()
NO_uio.create_or_update_tbl_labels()

scr_data_objects = [obj for obj in globals().values() if isinstance(obj, up.ScrData)]

df_all_label_tbls = pd.concat([obj.df_labels for obj in scr_data_objects])
df_all_label_tbls = df_all_label_tbls.drop_duplicates()
all_label_tbls=up.ScrData(tbl_name='labels_tbl', df=df_all_label_tbls)
all_label_tbls.save_to_db(table_name='tbl_labels')


"""
To do:
    rename url columns - unify names
    concat all df_labels into one table
    drop duplicates as urls are job ids
"""