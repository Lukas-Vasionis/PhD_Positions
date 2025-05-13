import sqlite3
from pathlib import Path
import streamlit as st
from db.viewer import download_filtered_tables, fetch_data
from db.viewer import get_columns as _get_columns
from db.viewer import get_tables as _get_tables
from db.viewer import save_labels

from config import pages_meta


def get_db_connection(db_path: Path) -> sqlite3.Connection:
    """Open (or create) and return a SQLite connection."""
    conn = sqlite3.connect(str(db_path))
    return conn

def render_ui(metadata: list, conn: sqlite3.Connection):
    # Set the layout to wide
    st.set_page_config(layout="wide")


    # Create a mapping of table names to university names and country codes
    table_name_mapper = {
        f"processed_{entry['country_code']}_{entry['id']}": {
            "university": entry["name"],
            "country_code": entry["country_code"]
        }
        for entry in metadata
    }

    # Function to fetch tables from the database (static data)
    @st.cache_data
    def get_tables(_conn):
        return _get_tables(_conn)

    # Function to fetch columns of a table (static data)
    @st.cache_data
    def get_columns(_conn, table_name):
        return _get_columns(_conn, table_name)


    label_options=["None", "Discard", "Interesting", "Applied", 'Rejected']

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

    st.sidebar.markdown(
        """
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
        """
    )


def main():
    BASE = Path(__file__).parent
    db_path = BASE.parent / "data" / "phd_jobs_in_schengen.db"

    metadata = pages_meta
    conn = get_db_connection(db_path)

    try:
        render_ui(metadata, conn)
    finally:
        # Close the connection to the database
        conn.close()


if __name__ == "__main__":
    main()