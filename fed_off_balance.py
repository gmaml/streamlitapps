import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import requests
from io import StringIO

# Assuming csv_url is defined somewhere in your code
csv_url = (
    "https://www.federalreserve.gov/releases/efa/off-balance-sheet-items-historical.csv"
)


def convert_quarter_to_datetime(date_str):
    if isinstance(date_str, str):
        parts = date_str.split(":")
        if len(parts) == 2:
            year, quarter = parts
            # Extract the numeric part of the quarter string
            quarter_number = int(quarter[1])  # Assuming the format is 'Q1', 'Q2', etc.
            month = (quarter_number - 1) * 3 + 1
            return pd.Timestamp(year=int(year), month=month, day=1)
        elif len(parts) == 1:
            return pd.Timestamp(year=int(parts[0]), month=1, day=1)
    else:
        return date_str


def download_csv(url):
    """Download CSV file and return a DataFrame."""
    response = requests.get(url)
    if response.status_code == 200:
        csv_data = StringIO(response.content.decode("utf-8"))
        df = pd.read_csv(csv_data)
        # Convert the 'Date' column from 'YYYY:QQ' format to datetime
        df["Date"] = df["Date"].apply(convert_quarter_to_datetime)
        return df
    else:
        return None


st.title("Federal Reserve Off Balance Sheet Data")

# Initialize session state variables if they don't exist
if "csv_downloaded" not in st.session_state:
    st.session_state.csv_downloaded = False
if "dataframe" not in st.session_state:
    st.session_state.dataframe = None


if st.button("Download CSV", key="download_csv") or st.session_state.csv_downloaded:
    if not st.session_state.csv_downloaded:
        df = download_csv(csv_url)
        if df is not None:
            df["Date"] = df["Date"].apply(convert_quarter_to_datetime)
            st.session_state.dataframe = df
            st.session_state.csv_downloaded = True
            st.write(df)
    else:
        st.write(st.session_state.dataframe)

    if st.session_state.dataframe is not None:
        # Dropdown to select a column to plot
        column_to_plot = st.selectbox(
            "Select a column to plot:",
            st.session_state.dataframe.columns,
            key="select_column_to_plot",
        )

        # Button to trigger the plot
        if st.button("Plot Data", key="plot_data"):
            # Plot selected column against "Date"
            fig, ax = plt.subplots()
            ax.plot(
                st.session_state.dataframe["Date"],
                st.session_state.dataframe[column_to_plot],
            )  # Plot with Date
            ax.set_title(f"{column_to_plot} over Time")
            ax.set_xlabel("Date")
            # Use st.pyplot() to display the plot in the Streamlit app
            st.pyplot(fig)
