# Loads glucose data from a DuckDB database stored in an S3 bucket.

import duckdb
import pandas as pd
import streamlit as st

def load_glucose_data():
    s3_url = "https://chumbucket4356.s3.amazonaws.com/mart_glucose_readings.parquet"

    
    df = duckdb.sql(f"SELECT * FROM '{s3_url}'").df()

    df["reading_timestamp"] = pd.to_datetime(df["reading_timestamp"])
    df["hour"] = df["reading_timestamp"].dt.hour

    return df

