from pprint import pprint

import streamlit as st
import sqlite3
import pandas as pd
import json

# Set the layout to wide
st.set_page_config(layout="wide")

# Load the pages_meta.json file to create a mapper
with open('scrapers/inputs/pages_meta.json') as f:
    pages_meta = json.load(f)
# Create a mapping of table names to university names and country codes
table_name_mapper = {
    f"processed_{entry['country_code']}_{entry['id']}": {
        "university": entry["name"],
        "country_code": entry["country_code"]
    }
    for entry in pages_meta
}

# Connect to the SQLite database
db_path = "db/phd_jobs_in_schengen.db"
conn = sqlite3.connect(db_path)


# Function to fetch tables from the database
@st.cache_data
def get_tables(_conn):
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql_query(query, _conn)

    list_tables=[x for x in tables['name'].tolist() if x.startswith("processed_")]

    return list_tables


# Function to fetch columns of a table
@st.cache_data
def get_columns(_conn, table_name):
    query = f"PRAGMA table_info({table_name});"
    columns = pd.read_sql_query(query, _conn)
    return columns['name'].tolist()


# Function to fetch data from the selected table and columns
@st.cache_data
def fetch_data(_conn, table_name, columns):
    # Quote the column names properly to handle special characters
    quoted_columns = [f'"{col}"' for col in columns]
    query = f"SELECT {', '.join(quoted_columns)} FROM {table_name};"
    data = pd.read_sql_query(query, _conn)

    return data


# Title of the Streamlit app
st.title("SQLite Database Viewer")

# Get all tables from the database
tables = get_tables(conn)

# Create a list of display names for selection in the format "University Name (Country Code)"
table_display_names = [
    f"{table_name_mapper.get(table, {}).get('university', table)} ({table_name_mapper.get(table, {}).get('country_code', 'Unknown')})"
    for table in tables
]

# Create a reverse lookup for selected display name to table name
display_to_table_name = {
    f"{table_name_mapper.get(table, {}).get('university', table)} ({table_name_mapper.get(table, {}).get('country_code', 'Unknown')})": table
    for table in tables
}

# Sidebar for table selection
selected_display_name = st.sidebar.selectbox("Select a table to view", table_display_names)

# Get the actual table name from the selected display name
selected_table = display_to_table_name[selected_display_name]

# Option to show all tables
show_all_tables = st.sidebar.checkbox("Show all tables", value=True)

if show_all_tables:
    # Display all tables and columns
    for table in tables:
        display_name = f"{table_name_mapper.get(table, {}).get('university', table)} ({table_name_mapper.get(table, {}).get('country_code', 'Unknown')})"
        st.subheader(f"Table: {display_name}")
        columns = get_columns(conn, table)
        selected_columns = st.multiselect(f"Select columns to display from {display_name}", columns, default=columns)

        if selected_columns:
            data = fetch_data(conn, table, selected_columns)
            st.dataframe(data)
else:
    # Display selected table and columns
    if selected_table:
        st.subheader(f"Table: {selected_display_name}")
        columns = get_columns(conn, selected_table)
        selected_columns = st.multiselect("Select columns to display", columns, default=columns)

        if selected_columns:
            data = fetch_data(conn, selected_table, selected_columns)
            st.dataframe(data)

# Close the connection to the database
conn.close()
