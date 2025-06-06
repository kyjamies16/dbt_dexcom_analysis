import datetime
import streamlit as st

def get_date_range_selector(df):
    predefined_options = {
        "Last 7 Days": (datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()),
        "Last 30 Days": (datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()),
        "This Month": (datetime.date.today().replace(day=1), datetime.date.today()),
        "All Time": (
            df["reading_timestamp"].min().date(),
            df["reading_timestamp"].max().date(),
        ),
        "Custom Range": None,
    }

    choice = st.sidebar.selectbox("Select a date range:", options=list(predefined_options.keys()))

    if choice == "Custom Range":
        custom_range = st.sidebar.date_input(
            "Pick a custom range:",
            value=(datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()),
            min_value=df["reading_timestamp"].min().date(),
            max_value=df["reading_timestamp"].max().date(),
        )
        if isinstance(custom_range, tuple) and len(custom_range) == 2:
            return custom_range[0], custom_range[1], "Custom Range"
        else:
            st.error("Please select both a start and end date.")
            st.stop()
    else:
        return *predefined_options[choice], choice
