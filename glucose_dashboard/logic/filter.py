import streamlit as st

def time_of_day_filter(df):
    st.sidebar.title("Time of Day Filter")
    bucket_options = ["All"] + sorted(df["time_of_day_bucket"].dropna().unique())
    selection = st.sidebar.selectbox("Select time of day:", bucket_options)
    return selection

def blood_sugar_type_filter(df):
    st.sidebar.title("Blood Sugar Type Filter")
    bucket_options = ["All"] + sorted(df["glucose_range_label"].dropna().unique())
    selection = st.sidebar.selectbox("Select blood sugar category:", bucket_options)
    return selection