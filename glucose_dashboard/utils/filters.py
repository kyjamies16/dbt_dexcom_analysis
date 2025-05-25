from datetime import datetime, timedelta
import streamlit as st

def date_range_sidebar(df):
    st.sidebar.title("Date Range Selector")
    earliest_date = df["reading_timestamp"].min().date()
    today = datetime.today().date()
    options = {
        "Last 2 Weeks": max(earliest_date, today - timedelta(days=14)),
        "Last 30 Days": max(earliest_date, today - timedelta(days=30)),
        "Last 6 Months": max(earliest_date, today - timedelta(days=180)),
        "Full Range": earliest_date
    }
    choice = st.sidebar.radio("Select range:", list(options.keys()))
    return options[choice], today, choice

def time_of_day_filter(df):
    st.sidebar.title("Time of Day Filter")
    bucket_options = ["All"] + sorted(df["time_of_day_bucket"].dropna().unique())
    selection = st.sidebar.selectbox("Select time of day:", bucket_options)
    return selection