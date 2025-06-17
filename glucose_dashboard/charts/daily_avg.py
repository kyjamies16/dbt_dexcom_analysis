import pandas as pd
import altair as alt

def generate_daily_average_chart(df: pd.DataFrame, start_date, end_date, std_multiplier=2.0):
    """
    Shows daily average glucose with 7-day rolling average,
    shaded band (±std_multiplier * std dev), and highlights anomalies in bright red.
    Excludes today's date to avoid partial data.
    """

    if df.empty:
        return None

    df = df.copy()
    df["reading_timestamp"] = pd.to_datetime(df["reading_timestamp"])
    df["date"] = pd.to_datetime(df["reading_timestamp"].dt.date)

    # --- Compute daily average ---
    daily_avg_df = (
        df.groupby("date")["glucose_mg_dl"]
        .mean()
        .reset_index(name="avg_glucose")
    )

    if daily_avg_df.empty:
        return None

    # --- Compute rolling mean & std with adjustable multiplier ---
    daily_avg_df["rolling_mean"] = daily_avg_df["avg_glucose"].rolling(window=7, min_periods=1).mean()
    daily_avg_df["rolling_std"] = daily_avg_df["avg_glucose"].rolling(window=7, min_periods=1).std().fillna(0)
    daily_avg_df["upper_band"] = daily_avg_df["rolling_mean"] + std_multiplier * daily_avg_df["rolling_std"]
    daily_avg_df["lower_band"] = daily_avg_df["rolling_mean"] - std_multiplier * daily_avg_df["rolling_std"]

    # --- Flag anomalies ---
    daily_avg_df["is_anomaly"] = (
        (daily_avg_df["avg_glucose"] > daily_avg_df["upper_band"]) |
        (daily_avg_df["avg_glucose"] < daily_avg_df["lower_band"])
    )

    # --- Filter to selected date range & exclude today ---
    today = pd.Timestamp.now().normalize()
    filtered_df = daily_avg_df[
        (daily_avg_df["date"] >= pd.to_datetime(start_date)) &
        (daily_avg_df["date"] <= pd.to_datetime(end_date)) &
        (daily_avg_df["date"] < today)
    ].copy()

    if filtered_df.empty:
        return None

    # --- Build chart layers ---
    tick_count = min(30, filtered_df["date"].nunique())
    y_domain = [100, 180]

    # Rolling band (area)
    band = alt.Chart(filtered_df).mark_area(opacity=0.2, color='orange').encode(
        x='date:T',
        y='lower_band:Q',
        y2='upper_band:Q'
    )

    # Rolling mean line
    rolling_line = alt.Chart(filtered_df).mark_line(color='orange').encode(
        x='date:T',
        y='rolling_mean:Q'
    )

    # Daily average line
    daily_line = alt.Chart(filtered_df).mark_line(point=True, color='#1f77b4').encode(
        x='date:T',
        y='avg_glucose:Q',
        tooltip=[
            alt.Tooltip("date:T", title="Date", format="%B %d, %Y"),
            alt.Tooltip("avg_glucose:Q", title="Daily Avg", format=".1f"),
            alt.Tooltip("rolling_mean:Q", title="Rolling Mean", format=".1f"),
            alt.Tooltip("upper_band:Q", title="Upper Band", format=".1f"),
            alt.Tooltip("lower_band:Q", title="Lower Band", format=".1f")
        ]
    )

    # Anomaly points — vivid red
    anomalies = alt.Chart(filtered_df[filtered_df["is_anomaly"]]).mark_point(
        color='#FF0000',
        size=80
    ).encode(
        x='date:T',
        y='avg_glucose:Q'
    )

    chart = (band + rolling_line + daily_line + anomalies).properties(
        title="Daily Average Glucose with Anomaly Detection",
    ).encode(
        x=alt.X(
            "date:T",
            axis=alt.Axis(
                format="%b %d",
                labelAngle=-45,
                tickCount=tick_count
            ),
            title="Date"
        ),
        y=alt.Y(
            "avg_glucose:Q",
            scale=alt.Scale(domain=y_domain),
            title="Glucose (mg/dL)"
        )
    ).configure_view(
        stroke=None
    ).configure_axis(
        grid=False
    ).interactive()

    return chart
