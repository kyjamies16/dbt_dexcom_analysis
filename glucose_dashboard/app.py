import sys
from pathlib import Path
import datetime
import streamlit as st
import charts


# Setup path and environment
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.load_env import load_root_env
load_root_env()

from data.load_data import load_glucose_data
from utils.filters import time_of_day_filter
from utils.metrics import compute_summary_metrics
from utils.formatting import format_pretty_date

# Page config
st.set_page_config(page_title="Glucose Overview", layout="wide")

# Load data
raw_df = load_glucose_data()

# --- Date Selection ---
predefined_options = {
    "Last 7 Days": (datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()),
    "Last 30 Days": (datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()),
    "This Month": (datetime.date.today().replace(day=1), datetime.date.today()),
    "All Time": (
        raw_df["reading_timestamp"].min().date(),
        raw_df["reading_timestamp"].max().date(),
    ),
    "Custom Range": None
}

range_choice = st.sidebar.selectbox("Select a date range:", options=list(predefined_options.keys()))

if range_choice == "Custom Range":
    custom_range = st.sidebar.date_input(
        "Pick a custom range:",
        value=(datetime.date.today() - datetime.timedelta(days=7), datetime.date.today()),
        min_value=raw_df["reading_timestamp"].min().date(),
        max_value=raw_df["reading_timestamp"].max().date(),
    )
    if isinstance(custom_range, tuple) and len(custom_range) == 2:
        start_date, end_date = custom_range
    else:
        st.error("Please select both a start and end date.")
        st.stop()
    range_label = "Custom Range"
else:
    start_date, end_date = predefined_options[range_choice]
    range_label = range_choice

# --- Filter Data ---
filtered_df = raw_df[
    (raw_df["reading_timestamp"].dt.date >= start_date) &
    (raw_df["reading_timestamp"].dt.date <= end_date)
].copy()

selected_bucket = time_of_day_filter(filtered_df)
if selected_bucket != "All":
    filtered_df = filtered_df[filtered_df["time_of_day_bucket"] == selected_bucket]

if filtered_df.empty:
    st.title("Overview")
    st.caption(f"{range_label}  |  {start_date} - {end_date}")
    st.warning("No data available for the selected date range.")
    st.stop()

# --- Download ---
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download CSV", csv, "glucose_data.csv", "text/csv")

# --- Metrics ---
last_reading_ts = filtered_df["reading_timestamp"].max()
last_reading_str = last_reading_ts.strftime("%b %d, %Y at %I:%M %p")
metrics = compute_summary_metrics(filtered_df)

st.title("Overview")
st.caption(f"{range_label}  |  {start_date} - {end_date}   |  📍 Last Reading: {last_reading_str}")
st.markdown("---")

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
    st.markdown("💡 Tip: Right-click the chart to save it as an image.")
    chart = charts.generate_glucose_time_chart(filtered_df, start_date, end_date)
    if chart:
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No chart data available.")

st.markdown("---")

# --- Heatmap ---
st.markdown("## Glucose Heatmaps")
heatmap_type = st.radio("Select heatmap type:", ["Low", "High"], horizontal=True)
with st.spinner("Generating heatmap..."):
    st.markdown("💡 Tip: Right-click the chart to save it as an image.")
    heatmap = charts.generate_glucose_heatmap(filtered_df, heatmap_type)
    if heatmap:
        st.altair_chart(heatmap, use_container_width=True)
    else:
        st.info("Not enough data to generate heatmap.")

st.markdown("---")

# --- Daily Average Chart ---
st.header("Daily Average Glucose Over Time")
daily_chart = charts.generate_daily_average_chart(filtered_df, start_date, end_date)
if daily_chart:
    st.altair_chart(daily_chart, use_container_width=True)
else:
    st.info("No data available to plot daily averages.")
