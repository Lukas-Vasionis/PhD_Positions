import sqlite3

import pandas as pd
import sqlalchemy
import polars as pl

class ScrData:
    def __init__(self, tbl_name):
        self.tbl_name=tbl_name
        self.df=None

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
        for date_col in list_date_cols:
            self.df.loc[:,date_col]=pd.to_datetime(self.df[date_col], format = date_format).dt.date
        return self

    def filter_CH_unil_PhD(self,):
        self.df.loc[self.df['Type of Position'].str.contains(r"PhD|Research")]
        return self

    def filter_CH_unil_Area_Of_Activity(self,):
        self.df=self.df.loc[self.df['Area of Activity'].isin(
            ["Biology and medicine",
             "Laboratoire, analyse, animalerie"])]
        return self

    def sort_by_column(self, col_name, ascend):
        self.df=self.df.sort_values(by=col_name, ascending=ascend)
        return self

    def save_to_db(self):
        df = pl.from_pandas(self.df) # Transforming into polars df only because uploading it into sql db is easier than pandas.

        processed_tbl_name=self.tbl_name.replace("scraper_","processed_")
        df.write_database(
            processed_tbl_name,
            connection=f"sqlite:///phd_jobs_in_schengen.db",
            if_table_exists="replace"
        )