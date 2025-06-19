import streamlit as st
import datetime
import charts
import logic 
from utils.load_env import load_root_env
from utils.formatting import format_pretty_date
from data.load_data import load_glucose_data
from config import settings

# Load environment variables and set up paths
load_root_env()

# Page config
st.set_page_config(page_title=settings.APP_TITLE, layout="wide")


# Load data
raw_df = load_glucose_data()

# --- Date Selection ---
start_date, end_date, range_label = logic.get_date_range_selector(raw_df)

# --- Adjust adjusted_end_date to max out at yesterday ---
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

# Use the earlier of (adjusted_end_date from selector) or yesterday
adjusted_end_date = min(end_date, yesterday)

# --- Filter Data ---
filtered_df = raw_df[
    (raw_df["reading_timestamp"].dt.date >= start_date) &
    (raw_df["reading_timestamp"].dt.date <= adjusted_end_date)
].copy()

selected_bucket = logic.time_of_day_filter(filtered_df)
if selected_bucket != "All":
    filtered_df = filtered_df[filtered_df["time_of_day_bucket"] == selected_bucket]

selected_range = logic.blood_sugar_type_filter(filtered_df)
if selected_range != "All":
    filtered_df = filtered_df[filtered_df["glucose_range_label"] == selected_range]

if filtered_df.empty:
    st.title("Glucose Dashboard")
    st.caption(f"{range_label} | {start_date} to {adjusted_end_date}")
    st.warning("⚠️ No data available for the selected date range.")
    st.stop()

# --- Download ---
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Filtered CSV", csv, settings.CSV_FILENAME, "text/csv")

# --- Metrics ---
last_reading_ts = filtered_df["reading_timestamp"].max()
last_reading_str = last_reading_ts.strftime(settings.LAST_TIME_FORMAT)
metrics = logic.compute_summary_metrics(filtered_df)

# Improved main title and context line
st.title("Glucose Overview")
st.caption(f"**{range_label}** &nbsp; | &nbsp; **{start_date} — {adjusted_end_date}** &nbsp; | &nbsp; **Last Reading:** {last_reading_str}")
st.info("ℹ️ **Note:** Glucose data is refreshed daily with a one-day delay. The most recent readings reflect data up to yesterday and are updated each morning by 9:40 AM Central Time..")

st.divider()

logic.display_glucose_metrics(metrics)

st.divider()

# --- Time Series Chart ---
start_str = format_pretty_date(start_date)
end_str = format_pretty_date(adjusted_end_date)

subtitle = (
    f" Glucose Trends by Time of Day ({start_str} to {end_str})"
    if selected_bucket == "All"
    else f" {selected_bucket} Glucose Trends ({start_str} to {end_str})"
)

st.header(subtitle)

with st.spinner("Loading trend chart..."):
    st.markdown("""
Shows **average glucose levels** at each time of day, with a shaded band for the typical P15–P75 range.
""")
    chart = charts.generate_glucose_time_chart(filtered_df, start_date, adjusted_end_date)
    if chart:
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.info("No data available to plot trends for this selection.")

st.divider()

# --- Heatmap ---
st.header(" Glucose Heatmaps")

heatmap_type = st.radio("Select heatmap type:", ["Low", "High"], horizontal=True)
with st.spinner("Rendering heatmap..."):
    st.markdown("""
Highlights **low or high glucose readings** by time of day. Darker shades indicate more frequent readings in that range.
""")
    heatmap = charts.generate_glucose_heatmap(filtered_df, heatmap_type)
    if heatmap:
        st.altair_chart(heatmap, use_container_width=True)
    else:
        st.info("Not enough data to generate this heatmap.")

st.divider()

# --- Daily Average Chart ---
st.header("Daily Average Glucose Over Time")

with st.expander("ℹ️ How the daily average & anomaly band work"):
    st.markdown("""
    **What this chart shows:**
    
    - **Daily Average:** The blue line shows your average glucose for each day.
    - **7-Day Rolling Average:** The orange line smooths out daily ups and downs to show your weekly trend.
    - **Normal Range Band:** The shaded orange area represents the typical range based on your rolling average ± 2 standard deviations. This adapts to your recent readings.
    - **Anomalies:** Red dots highlight days where your daily average is unusually high or low compared to your typical week.

    This helps you see if your glucose control is staying consistent, drifting gradually, or having unusual spikes/dips that might need attention.
    """)


std_multiplier = st.slider(
    "Anomaly Band Width (Standard Deviations)", 
    min_value=1.5, 
    max_value=3.0, 
    value=2.0, 
    step=0.5,
    help="Controls how wide the 'normal' range is. Wider bands flag only more extreme daily glucose changes."

)
daily_chart = charts.generate_daily_average_chart(raw_df, start_date, adjusted_end_date, std_multiplier=std_multiplier)
if daily_chart:
    st.altair_chart(daily_chart, use_container_width=True)
else:
    st.info("No daily average data available for the selected period.")

st.divider()

# --- Spike Recovery Chart ---
st.header(" Spike Recovery Analysis")
st.markdown("""
Visualizes detected **glucose spike events** and how quickly levels return to normal.
""")

with st.expander("ℹ️ How spikes are defined"):
    st.markdown("""
**How it works:**

- **Spike start:** Glucose rises ≥ 30 mg/dL per hour and crosses 140 mg/dL.
- **Recovery:** Ends when glucose drops back to ≤ 140 mg/dL.
- Each point shows the spike’s start time, peak level, and duration.

This helps monitor recovery speed and spike severity.
""")

spike_events = logic.find_spike_events(filtered_df)
spike_chart = charts.plot_spike_recovery(spike_events)

if spike_chart:
    st.altair_chart(spike_chart, use_container_width=True)
else:
    st.info("No spike recovery events detected for this data slice.")
