import streamlit as st
from data.load_data import load_glucose_data
from utils.filters import date_range_sidebar
from utils.metrics import compute_summary_metrics
from utils.charts import generate_glucose_time_chart

# Setup
st.set_page_config(page_title="Glucose Overview", layout="wide")

# Load data
df = load_glucose_data()

# Sidebar date range selection
start_date, end_date, range_label = date_range_sidebar(df)
filtered_df = df[(df["reading_timestamp"].dt.date >= start_date) & (df["reading_timestamp"].dt.date <= end_date)].copy()
last_reading_ts = filtered_df["reading_timestamp"].max()
last_reading_str = last_reading_ts.strftime("%b %d, %Y at %I:%M %p")


# Summary Metrics
metrics = compute_summary_metrics(filtered_df)

# Header
st.title("Overview")
st.caption(f"{range_label}  |  {start_date} - {end_date}   |  📍 Last Reading: {last_reading_str}")
st.markdown("---")

# Metrics Row
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Average Glucose", f"{metrics['avg']:.0f} mg/dL")
    st.metric("Standard Deviation", f"{metrics['std']:.0f} mg/dL")
    st.caption("ℹ️ Normal std dev range is 30–50 mg/dL.")

with col2:
    st.metric("Coefficient of Variation", f"{metrics['cv']:.1f}%")
    st.caption("ℹ️ CV = std dev / mean. Below 36% indicates good stability.")

with col3:
    st.markdown("**Time in Range**")
    st.markdown(f"🟩 In Range: **{metrics['in_range_pct']:.0f}%**")
    st.markdown(f"🟥 Low: **{metrics['low_pct']:.0f}%**")
    st.markdown(f"🟧 High: **{metrics['high_pct']:.0f}%**")
    st.caption("Target range: 70–180 mg/dL.")

st.markdown("---")

# Chart
if not filtered_df.empty:
    st.subheader(f"Glucose Trends by Time of Day ({start_date} to {end_date})")
    chart = generate_glucose_time_chart(filtered_df, start_date, end_date)
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No data available for the selected date range.")
