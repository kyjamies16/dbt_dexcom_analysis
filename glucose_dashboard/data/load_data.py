import os
import duckdb
import pandas as pd
import streamlit as st
from utils.load_env import load_root_env

# Load environment variables once
load_root_env()

def load_glucose_data():
    db_path = os.getenv("DATABASE_PATH")  
    
    if not db_path:
        st.error("DATABASE_PATH is not set in your environment variables.")
        st.stop()

    # Open connection in read-only mode
    con = duckdb.connect(db_path, read_only=True)

    # Run query
    df = con.execute("SELECT * FROM main_mart.mart_glucose_readings").fetchdf()

    # Preprocess timestamps
    df["reading_timestamp"] = pd.to_datetime(df["reading_timestamp"])
    df["hour"] = df["reading_timestamp"].dt.hour

    return df
