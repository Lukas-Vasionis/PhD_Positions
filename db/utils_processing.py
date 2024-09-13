import sqlite3
import time
import traceback

import pandas as pd
import sqlalchemy
import polars as pl

def get_list_of_tbls_in_db():
    list_tbl=pl.read_database_uri(
        query="SELECT name FROM sqlite_master WHERE type='table';",
        # query="SELECT * FROM scraper_NO_uib",
        uri="sqlite://phd_jobs_in_schengen.db"
    ).select("name").to_series().to_list()
    return list_tbl


class ScrData:
    def __init__(self, tbl_name, df=None):
        self.tbl_name=tbl_name
        self.df=df
        self.df_labels=None

    def load_tbl_to_pd(self):
        """
        Loads table into pandas dataframe
        :param tbl_name:
        :return: pd.DataFrame
        """
        print(f"Loading table: {self.tbl_name}")
        with sqlalchemy.create_engine("sqlite:///phd_jobs_in_schengen.db").connect() as connection:
            self.df=pd.read_sql(f"""SELECT * FROM {self.tbl_name}""",
                                con=connection)
        return self

    def filter_by_occupation_percent(self, percentage_column: str) -> pd.DataFrame:
       """
        Swiss universities offer PhD positions with less than 100% occupancy (Part-time PhD positions)
        This f-tion filters and keeps positions that offer => 90% occupancy

       :param table_name: table to filter
       :param percentage_column: name of the column that holds occupancy percentage
       :return: pd.DataFrame()
       """
       # Filter records that contain '90', '100' or None in the identified column
       self.df = self.df[
           self.df[percentage_column].isna() |
           self.df[percentage_column].str.contains(r'(90|100)', na=False)
           ]
       return self

    def parse_date_columns(self, list_date_cols:list, date_format='%d.%m.%Y'):
        """Converts columns of strings to dates"""
        for date_col in list_date_cols:
            self.df.loc[:,date_col]=pd.to_datetime(self.df[date_col], format = date_format).dt.date
            return self

    def filter_CH_unil_PhD(self,):
        """Keeps only positions of PhD/Research type"""
        self.df.loc[self.df['Type of Position'].str.contains(r"PhD|Research")]
        return self

    def filter_CH_unil_Area_Of_Activity(self,):
        """Keeps records within biomedical area"""

        self.df=self.df.loc[self.df['Area of Activity'].isin(
            ["Biology and medicine",
             "Laboratoire, analyse, animalerie"])]
        return self

    def sort_by_column(self, col_name, ascend):
        """Sorts column by defined order"""
        self.df=self.df.sort_values(by=col_name, ascending=ascend)
        return self

    def create_or_update_tbl_labels(self):
        """
        Labels table holds record labels that were assigned in the app ('applied', 'interesting', 'DNA not interesting', 'DNA requirements')
        This table holds records of all scrapers
        If didn't exist: Creates labels table
        If exists: Appends scraped new records to it, removes duplicates
        """
        def get_label_tbl_of_old_records():
            cnx = sqlite3.connect('phd_jobs_in_schengen.db')
            df_table_labels_old = pd.read_sql_query(f"""SELECT * FROM tbl_labels WHERE table_name = '{self}'""", cnx)
            return df_table_labels_old


        def get_label_tbl_of_new_records():
            df_labels_new=self.df
            df_labels_new.loc[:,'label']=''
            df_labels_new.loc[:, 'table_name'] = f"processed_{self.tbl_name}"
            df_labels_new=df_labels_new.loc[:,["table_name","url", "label"]]
            return df_labels_new

        def update_tbl_labels_records(df_labels_old, df_labels_new):

            # Concatenate the dataframes
            df_labels = pd.concat([df_labels_old, df_labels_new])

            # Sort so that records with 'label' as None are last
            df_labels = df_labels.sort_values(by=['table_name', 'url', 'label'], ascending=[True, True, False])

            # Drop duplicates, keeping the first occurrence where 'label' is not None
            df_labels = df_labels.drop_duplicates(subset=['table_name', 'url'], keep='first')
            return df_labels

        # Create labels table if it doesnt exist
        if 'tbl_labels' not in get_list_of_tbls_in_db():
            conn = sqlite3.connect("phd_jobs_in_schengen.db")
            cursor = conn.cursor()
            cursor.execute(f"CREATE TABLE tbl_labels (table_name TEXT,url TEXT,label TEXT);")
            conn.commit()
            conn.close()

        # Update labels data with new records, but keep old records with labels
        df_labels_old = get_label_tbl_of_old_records()
        df_labels_new = get_label_tbl_of_new_records()
        df_labels = update_tbl_labels_records(df_labels_old, df_labels_new)

        df_labels = pl.from_pandas(df_labels)  # Transforming into polars df only because uploading it into sql db is easier than pandas.
        df_labels.write_database(
            "tbl_labels",
            connection=f"sqlite:///phd_jobs_in_schengen.db",
            if_table_exists='replace'
        )

        self.df_labels = df_labels_new
        return self

    def save_to_db(self, df_to_upload=None, table_name=None, if_table_exists="replace"):
        # By default, this function is designed to upload processed tables. However, its is possible to upload any table to db if default arguments are changed

        if table_name is None:
            table_name=f"processed_{self.tbl_name}"
        if df_to_upload is None:
            df_to_upload=self.df

        # new_tbl_name="tbl_labels"
        # df_to_upload = self.df_labels

        try:
            df_to_upload = pl.from_pandas(df_to_upload) # Transforming into polars df only because uploading it into sql db is easier than pandas.
            df_to_upload.write_database(
                table_name,
                connection=f"sqlite:///phd_jobs_in_schengen.db",
                if_table_exists=if_table_exists
            )
        except Exception as e:
            print(e)

