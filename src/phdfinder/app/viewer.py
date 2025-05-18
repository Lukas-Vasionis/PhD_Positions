import pandas as pd
from typing import List, Tuple

import sqlite3
from io import BytesIO
import streamlit as st


def get_tables(_conn: sqlite3.Connection) -> List[str]:
    """
    # Function to fetch tables from the database (static data)
    :param _conn:  sqlite connection object
    :return: list of tables
    """
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql_query(query, _conn)
    list_tables = [x for x in tables['name'].tolist() if x.startswith("processed_")]
    return list_tables

def get_columns(_conn: sqlite3.Connection, table_name: str) -> List[Tuple[str, str]]:
    """
    # Function to fetch columns of a table (static data)
    :param _conn: sqlite connection object
    :param table_name: list of tables
    :return: list of columns
    """
    query = f"PRAGMA table_info({table_name});"
    columns = pd.read_sql_query(query, _conn)
    return columns['name'].tolist()

def fetch_data(_conn: sqlite3.Connection, table_name: str) -> pd.DataFrame:
    # Function to fetch data from the selected table and columns (dynamic data, no cache)

    query = f"SELECT * FROM {table_name};"
    data = pd.read_sql_query(query, _conn)

    # Fetch existing labels from tbl_labels
    label_query = f"SELECT url, label FROM tbl_labels WHERE table_name='{table_name}';"
    labels = pd.read_sql_query(label_query, _conn)

    # Merge the labels with the main data
    data = pd.merge(data, labels, how='left', left_on='url', right_on='url')
    data['label'] = data['label'].fillna('None')  # Default value set to 'None'

    # Reorder columns
    first_cols = ['label', 'title', 'url']
    other_cols = [c for c in data.columns if c not in first_cols]
    data = data.loc[:, first_cols + other_cols]

    # sorting
    def select_sort_column(data):
        if "deadline" in data.columns:
            return "deadline"
        else:
            return "date_scraped"

    data = data.sort_values(by=select_sort_column(data), ascending=False)

    return data


label_options = ["None", "Discard", "Interesting", "Applied", 'Rejected']


# Function to save updated labels to the database
def save_labels(_conn: sqlite3.Connection, labels_df: pd.DataFrame) -> None:
    _cursor = _conn.cursor()
    update_query = """UPDATE tbl_labels SET label = ? WHERE url = ?"""
    rows_to_update = labels_df[['label', 'url']].to_records(index=False).tolist()
    for row in rows_to_update:
        _cursor.execute(update_query, row)
        _conn.commit()


# Function to download all filtered tables as an Excel file
def download_filtered_tables(selected_tables, conn):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for table in selected_tables:
            columns = get_columns(conn, table)
            data = fetch_data(conn, table, columns)
            # Apply the label filter
            filtered_data = data[data['label'].isin(st.session_state.label_filter_options)]
            filtered_data.to_excel(writer, sheet_name=table, index=False)
    output.seek(0)
    return output