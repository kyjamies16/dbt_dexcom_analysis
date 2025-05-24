import duckdb
import pandas as pd
import streamlit as st

@st.cache_data
def load_glucose_data():
    con = duckdb.connect("dbt_duckdb.db", read_only=True)
    df = con.execute("SELECT * FROM main_mart.mart_glucose_readings").fetchdf()
    df["reading_timestamp"] = pd.to_datetime(df["reading_timestamp"])
    df["hour"] = df["reading_timestamp"].dt.hour
    return df
