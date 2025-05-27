import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.load_env import load_root_env
load_root_env()

import streamlit as st
import time
from datetime import datetime
from data.load_data import load_glucose_data
from utils.filters import date_range_sidebar, time_of_day_filter
from utils.metrics import compute_summary_metrics
from utils.charts import (
    generate_glucose_time_chart,
    generate_glucose_heatmap,
    generate_daily_average_chart
)
from utils.formatting import format_pretty_date

# Setup
st.set_page_config(page_title="Glucose Overview", layout="wide")

# Load data
raw_df = load_glucose_data()

# Sidebar date range selection
start_date, end_date, range_label = date_range_sidebar(raw_df)

# Filter data by date
filtered_df = raw_df[
    (raw_df["reading_timestamp"].dt.date >= start_date) &
    (raw_df["reading_timestamp"].dt.date <= end_date)
].copy()

# Apply time of day filter
selected_bucket = time_of_day_filter(filtered_df)
if selected_bucket != "All":
    filtered_df = filtered_df[filtered_df["time_of_day_bucket"] == selected_bucket]

# Early stop if no data
if filtered_df.empty:
    st.title("Overview")
    st.caption(f"{range_label}  |  {start_date} - {end_date}")
    st.warning("No data available for the selected date range.")
    st.stop()

# Download CSV
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name="glucose_data.csv",
    mime="text/csv"
)

# Last reading timestamp
last_reading_ts = filtered_df["reading_timestamp"].max()
last_reading_str = last_reading_ts.strftime("%b %d, %Y at %I:%M %p")

# Compute daily averages
daily_df = filtered_df.copy()
daily_df["date"] = daily_df["reading_timestamp"].dt.date
daily_avg_df = (
    daily_df.groupby("date")["glucose_mg_dl"]
    .mean()
    .reset_index(name="avg_glucose")
)

# Summary metrics
metrics = compute_summary_metrics(filtered_df)

# Header
st.title("Overview")
st.caption(f"{range_label}  |  {start_date} - {end_date}   |  📍 Last Reading: {last_reading_str}")
st.markdown("---")

# Metrics
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

# Glucose Time Series Chart
start_str = format_pretty_date(start_date)
end_str = format_pretty_date(end_date)

if selected_bucket == "All":
    subtitle = f"Glucose Trends by Time of Day ({start_str} to {end_str})"
else:
    subtitle = f"{selected_bucket} Glucose Trends ({start_str} to {end_str})"

st.subheader(subtitle)
chart_placeholder = st.empty()

with st.spinner("Loading chart..."):
    st.markdown("💡 Tip: Right-click the chart to save it as an image.")
    chart = generate_glucose_time_chart(filtered_df, start_date, end_date)
    time.sleep(0.1)
    if chart:
        chart_placeholder.altair_chart(chart, use_container_width=True)
    else:
        chart_placeholder.info("No chart data available.")

st.markdown("---")

# Heatmap
st.markdown("## Glucose Heatmaps")
heatmap_type = st.radio("Select heatmap type:", ["Low", "High"], horizontal=True)

with st.spinner("Generating heatmap..."):
    st.markdown("💡 Tip: Right-click the chart to save it as an image.")
    heatmap = generate_glucose_heatmap(filtered_df, heatmap_type)
    if heatmap:
        st.altair_chart(heatmap, use_container_width=True)
    else:
        st.info("Not enough data to generate heatmap.")

st.markdown("---")

# Daily Average Chart
st.header("Daily Average Glucose Over Time")
daily_chart = generate_daily_average_chart(filtered_df, start_date, end_date)

if daily_chart:
    st.altair_chart(daily_chart, use_container_width=True)
else:
    st.info("No data available to plot daily averages.")
