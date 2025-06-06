import streamlit as st

import charts
import logic
from utils.load_env import load_root_env
from utils.formatting import format_pretty_date
from data.load_data import load_glucose_data
from config import settings

# Load environment variables and set up paths
load_root_env()

# Page config
st.set_page_config(page_title= settings.APP_TITLE, layout="wide")

# Load data
raw_df = load_glucose_data()

# --- Date Selection ---
start_date, end_date, range_label = logic.get_date_range_selector(raw_df)

# --- Filter Data ---
filtered_df = raw_df[
    (raw_df["reading_timestamp"].dt.date >= start_date) &
    (raw_df["reading_timestamp"].dt.date <= end_date)
].copy()

selected_bucket = logic.time_of_day_filter(filtered_df)
if selected_bucket != "All":
    filtered_df = filtered_df[filtered_df["time_of_day_bucket"] == selected_bucket]

if filtered_df.empty:
    st.title("Overview")
    st.caption(f"{range_label}  |  {start_date} - {end_date}")
    st.warning("No data available for the selected date range.")
    st.stop()

# --- Download ---
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download CSV", csv, settings.CSV_FILENAME, "text/csv")

# --- Metrics ---
last_reading_ts = filtered_df["reading_timestamp"].max()
last_reading_str = last_reading_ts.strftime(settings.LAST_TIME_FORMAT)
metrics = logic.compute_summary_metrics(filtered_df)

st.title("Overview")
st.caption(f"{range_label}  |  {start_date} - {end_date}   |  📍 Last Reading: {last_reading_str}")
st.divider()

logic.display_glucose_metrics(metrics)

st.divider()

# --- Time Series Chart ---
start_str = format_pretty_date(start_date)
end_str = format_pretty_date(end_date)
subtitle = (
    f"Glucose Trends by Time of Day ({start_str} to {end_str})"
    if selected_bucket == "All"
    else f"{selected_bucket} Glucose Trends ({start_str} to {end_str})"
)
st.subheader(subtitle)
with st.spinner("Loading chart..."):
    st.markdown(settings.TOOLTIP_HINT)
    chart = charts.generate_glucose_time_chart(filtered_df, start_date, end_date)
    if chart:
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No chart data available.")

st.divider()

# --- Heatmap ---
st.markdown("## Glucose Heatmaps")
heatmap_type = st.radio("Select heatmap type:", ["Low", "High"], horizontal=True)
with st.spinner("Generating heatmap..."):
    st.markdown(settings.TOOLTIP_HINT)
    heatmap = charts.generate_glucose_heatmap(filtered_df, heatmap_type)
    if heatmap:
        st.altair_chart(heatmap, use_container_width=True)
    else:
        st.info("Not enough data to generate heatmap.")

st.divider()

# --- Daily Average Chart ---
st.header("Daily Average Glucose Over Time")
st.markdown(settings.TOOLTIP_HINT)
daily_chart = charts.generate_daily_average_chart(filtered_df, start_date, end_date)
if daily_chart:
    st.altair_chart(daily_chart, use_container_width=True)
else:
    st.info("No data available to plot daily averages.")
