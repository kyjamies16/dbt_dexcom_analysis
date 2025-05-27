import duckdb
import pandas as pd
import streamlit as st

def load_glucose_data():
    con = duckdb.connect(
    "C:/Users/krjam/dexcom/dexcom_glucose_analytics/dbt_duckdb.db", read_only=True)
    df = con.execute("SELECT * FROM main_mart.mart_glucose_readings").fetchdf()
    df["reading_timestamp"] = pd.to_datetime(df["reading_timestamp"])
    df["hour"] = df["reading_timestamp"].dt.hour
    return df
