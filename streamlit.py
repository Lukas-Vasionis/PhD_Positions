import streamlit as st
import sqlite3
import pandas as pd
import json
import polars as pl
from io import BytesIO

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
def fetch_data(_conn, table_name,
               # columns
               ):
    # quoted_columns = [f'"{col}"' for col in columns]
    # query = f"SELECT {', '.join(quoted_columns)} FROM {table_name};"
    query = f"SELECT * FROM {table_name};"
    data = pd.read_sql_query(query, _conn)

    # Fetch existing labels from tbl_labels
    label_query = f"SELECT url, label FROM tbl_labels WHERE table_name='{table_name}';"
    labels = pd.read_sql_query(label_query, _conn)

    # Merge the labels with the main data
    data = pd.merge(data, labels, how='left', left_on='url', right_on='url')
    data['label'] = data['label'].fillna('None')  # Default value set to 'None'

    # Reorder columns
    first_cols=['label', 'title', 'url']
    other_cols=[c for c in data.columns if c not in first_cols]
    data = data.loc[:, first_cols + other_cols]

    # sorting
    def select_sort_column(data):
        if "deadline" in data.columns:
            return "deadline"
        else:
            return "date_scraped"
    data = data.sort_values(by=select_sort_column(data), ascending=False)

    return data

label_options=["None", "Discard", "Interesting", "Applied", 'Rejected']

# Function to save updated labels to the database
def save_labels(_conn, table_name, labels_df):
    _cursor = _conn.cursor()
    update_query = """UPDATE tbl_labels SET label = ? WHERE url = ?"""
    rows_to_update = labels_df[['label', 'url']].to_records(index=False).tolist()
    for row in rows_to_update:
        _cursor.execute(update_query, row)
        conn.commit()

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

# Initialize session state
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
    - On the left you can select university by its name. In later updates, there will be additional filter of university's country.
    Meanwhile, you will find country code at the end of each name.  

    - Upon selecting the university, a table will pop up. Here, you can assign labels to the selected position with a double click.
    - Upon selecting the cell in the table it is convenient to navigate through records and label them with Arrow and Enter keys.

    - **After assigning labels to the job positions, don't forget to click Save Labels!**

    - If you label a record as 'discard' it will disappear upon clicking "Save Labels". **However, you can always get them back by adding 'Discard' to the label filters**


    ## Saving labels
    So far, this web application is designed to run locally as it saves-data-onto/displays-data-from the local database.
    Further updates will bring option to download/upload your own labels and use them in the web app.
    Meanwhile, **use this app locally. The web version is only for demo.**

    ---
    """
)

# Get all tables from the database
tables = get_tables(conn)

# Create display names for selection
table_display_names = [
    f"{table_name_mapper.get(table, {}).get('university', table)} ({table_name_mapper.get(table, {}).get('country_code', 'Unknown')})"
    for table in tables
]

# Reverse lookup for selected display name to table name
display_to_table_name = {
    f"{table_name_mapper.get(table, {}).get('university', table)} ({table_name_mapper.get(table, {}).get('country_code', 'Unknown')})": table
    for table in tables
}


# Sidebar for table selection
selected_display_names = st.sidebar.multiselect(
    "Select universities",
    table_display_names,
    key=f'select-uni',
    # default=st.session_state.selected_display_names
)



# Button to select all tables
if st.sidebar.button('Show all tables'):
    st.session_state.selected_display_names = table_display_names
    selected_display_names = table_display_names  # Update the current selection

# Button to clear table selection
if st.sidebar.button('Clear table selection'):
    st.session_state.selected_display_names = []
    selected_display_names = []  # Update the current selection

# Get the actual table names from the selected display names
selected_tables = [display_to_table_name[display_name] for display_name in selected_display_names]

# Filter widget for the label column
label_filter_options = st.sidebar.multiselect(
    "Filter by label",
    label_options,
    key='select-labels',
    default=st.session_state.label_filter_options
)

# Store selections in session state
st.session_state.selected_display_names = selected_display_names
st.session_state.label_filter_options = label_filter_options

# Button to download all filtered tables as Excel (only once in the sidebar)
if selected_tables:
    if st.sidebar.button('Download filtered tables as Excel'):
        excel_data = download_filtered_tables(selected_tables, conn)
        st.sidebar.download_button(
            label="Download Excel file",
            data=excel_data,
            file_name="filtered_tables.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# Display selected tables and columns
if selected_tables:
    for table in selected_tables:
        display_name = f"{table_name_mapper.get(table, {}).get('university', table)} ({table_name_mapper.get(table, {}).get('country_code', 'Unknown')})"
        st.subheader(f"{display_name}")
        columns = get_columns(conn, table)
        # selected_columns = st.multiselect(f"Select columns to display from {display_name}", columns,key=f'select-cols-{table}', default=columns)

        # if selected_columns:
        data = fetch_data(conn, table)

        # Apply the filter for selected labels
        data = data[data['label'].isin(st.session_state.label_filter_options)]

        # Display an editable data editor
        edited_data = st.data_editor(data,
                                     column_config={
                                         "label": st.column_config.SelectboxColumn(
                                             "label",
                                             help="Assign value for future filtering",
                                             width="medium",
                                             options=label_options,
                                             required=True
                                         ),
                                         "url":st.column_config.LinkColumn("url")
                                     },
                                     key=f'data_editor-{table}',
                                     hide_index=True)

        # Save labels when the user clicks the button
        if st.button('Save Labels', key=f"save_{table}"):
            save_labels(conn, table, edited_data[['url', 'label']].dropna())
            st.cache_data.clear()
            st.rerun()

# Close the connection to the database
conn.close()
