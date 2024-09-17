import streamlit as st
import sqlite3
import pandas as pd
import json
import polars as pl

# Set the layout to wide
st.set_page_config(layout="wide")

# Load the pages_meta.json file to create a mapper
with open('scraping/inputs/pages_meta.json') as f:
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

# Function to fetch tables from the database (static data)
@st.cache_data
def get_tables(_conn):
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql_query(query, _conn)

    list_tables = [x for x in tables['name'].tolist() if x.startswith("processed_")]

    return list_tables

# Function to fetch columns of a table (static data)
@st.cache_data
def get_columns(_conn, table_name):
    query = f"PRAGMA table_info({table_name});"
    columns = pd.read_sql_query(query, _conn)
    return columns['name'].tolist()

# Function to fetch data from the selected table and columns (dynamic data, no cache)
def fetch_data(_conn, table_name, columns):
    # Quote the column names properly to handle special characters
    quoted_columns = [f'"{col}"' for col in columns]
    query = f"SELECT {', '.join(quoted_columns)} FROM {table_name};"
    data = pd.read_sql_query(query, _conn)

    # Fetch existing labels from tbl_labels
    label_query = f"SELECT url, label FROM tbl_labels WHERE table_name='{table_name}';"
    labels = pd.read_sql_query(label_query, _conn)

    # Merge the labels with the main data
    data = pd.merge(data, labels, how='left', left_on='url', right_on='url')

    # Preserve any new changes by setting the default only for NaN values not set by the user
    data['label'] = data['label'].fillna('None')  # Default value set to 'None' if no change was made by the user
    data = data.loc[:, ['label'] + [c for c in data.columns if c != 'label']]

    return data

# Updated function to save updated labels to the database
def save_labels(_conn, table_name, labels_df):
    _cursor = _conn.cursor()
    update_query = """UPDATE tbl_labels SET label = ? WHERE url = ?"""

    # Convert the DataFrame to a list of tuples (records) and update the database
    rows_to_update = labels_df[['label', 'url']].to_records(index=False).tolist()

    for row in rows_to_update:
        _cursor.execute(update_query, row)
        conn.commit()

# Initialize session state for filter and table selection
if 'selected_display_names' not in st.session_state:
    st.session_state.selected_display_names = []
if 'label_filter_options' not in st.session_state:
    st.session_state.label_filter_options = ["None", "Interesting", "Applied"]

# Title of the Streamlit app
st.title("PhD positions in Europe")
st.markdown(
    """
    ---
    
    ### Welcome to Baltic Green's PhD finder! 

    The app is designed to ease you PhD search by gathering data about open European PhD positions into one place. 
    All data is scraped directly from the primary source - pages of the universities. The data is oriented to PhD job
    positions in biomedical field. However, some universities post various vacancies in the single list. Therefore, 
    don't be surprised to find positions in linguistics, theology or arts. This will be fixed in further updates of the scrapers.

    ## Navigation
    On the left you can select university by its name. In later updates, there will be additional filter of university's country.
    Meanwhile, you will find country code at the end of each name.  

    Upon selecting the university, a table will pop up. Here, you can assign labels to the selected position with a double click.
    Upon selecting the cell in the table it is convenient to navigate through records with Arrow and Enter keys. 
    After assigning labels to the job positions, don't forget to click Save Labels!

    ## Saving labels
    So far, this web application is designed to run locally as it saves-data-onto/displays-data-from the local database. 
    Further updates will bring option to download/upload your own labels and use them in the web app. 
    Meanwhile, **use this app locally. The web version is only for demo.**
    
    ---
    """
)

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

# Sidebar for table selection with multiselect
selected_display_names = st.sidebar.multiselect(
    "Select universities",
    table_display_names,
    default=st.session_state.selected_display_names
)

# Button to select all tables
if st.sidebar.button('Show all tables'):
    st.session_state.selected_display_names = table_display_names

# Button to clear table selection
if st.sidebar.button('Clear table selection'):
    st.session_state.selected_display_names = []

# Get the actual table names from the selected display names
selected_tables = [display_to_table_name[display_name] for display_name in selected_display_names]

# Filter widget for the label column
label_filter_options = st.sidebar.multiselect(
    "Filter by label",
    ["None", "Discard", "Interesting", "Applied"],
    default=st.session_state.label_filter_options
)

# Store selections in session state
st.session_state.selected_display_names = selected_display_names
st.session_state.label_filter_options = label_filter_options

# Display selected tables and columns
if selected_tables:
    for table in selected_tables:
        display_name = f"{table_name_mapper.get(table, {}).get('university', table)} ({table_name_mapper.get(table, {}).get('country_code', 'Unknown')})"
        st.subheader(f"{display_name}")
        columns = get_columns(conn, table)
        selected_columns = st.multiselect(f"Select columns to display from {display_name}", columns, default=columns)

        if selected_columns:
            data = fetch_data(conn, table, selected_columns)

            # Apply the filter for selected labels
            data = data[data['label'].isin(st.session_state.label_filter_options)]

            # Display an editable data editor
            edited_data = st.data_editor(data, column_config={"label": st.column_config.SelectboxColumn(
                "label",
                help="Assign value for future filtering",
                width="medium",
                options=["None", "Discard", "Interesting", "Applied"],
                required=True
            )}, hide_index=True)

            # Save labels when the user clicks the button
            if st.button('Save Labels', key=f"save_{table}"):
                save_labels(conn, table, edited_data[['url', 'label']].dropna())  # Drop any rows where label is NaN
                st.cache_data.clear()  # Clear cache to refresh data
                st.rerun()  # Rerun the script to avoid duplicate display

# Close the connection to the database
conn.close()
