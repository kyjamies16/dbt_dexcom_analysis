import pandas as pd
import altair as alt

def generate_glucose_time_chart(df: pd.DataFrame, start_date, end_date):
    """
    Generates an Altair chart showing glucose mean, 15th and 75th percentile
    by time of day (rounded to nearest 30 minutes).
    """

    # Filter early and reduce columns
    chart_df = df.loc[
        (df["reading_timestamp"].dt.date >= start_date) &
        (df["reading_timestamp"].dt.date <= end_date),
        ["reading_timestamp", "glucose_mg_dl"]
    ].copy()

    # ✅ Drop duplicates for cleaner aggregation
    chart_df.drop_duplicates(subset=["reading_timestamp", "glucose_mg_dl"], inplace=True)

    # ✅ Remove timezone info if present
    chart_df["reading_timestamp"] = pd.to_datetime(chart_df["reading_timestamp"]).dt.tz_localize(None)

    # Return early if no data left
    if chart_df.empty:
        return None

    # Round timestamps to nearest 30-minute interval and extract time-of-day
    chart_df["time_of_day"] = chart_df["reading_timestamp"].dt.floor("30min").dt.strftime("%H:%M")

    # Aggregate glucose percentiles and mean by time-of-day
    agg = chart_df.groupby("time_of_day")["glucose_mg_dl"].agg([
        ("15th", lambda x: x.quantile(0.15)),
        ("mean", "mean"),
        ("75th", lambda x: x.quantile(0.75))
    ]).reset_index()

    # Generate 30-minute labels and readable display values
    time_ticks = pd.date_range("00:00", "23:30", freq="30min").strftime("%H:%M").tolist()
    label_map = {
        f"{h:02}:{m:02}": f"{(h % 12) or 12}:{m:02} {'AM' if h < 12 else 'PM'}"
        for h in range(24) for m in [0, 30]
    }
    agg["label"] = agg["time_of_day"].map(label_map)

    # Line chart: Mean glucose
    line = alt.Chart(agg).mark_line().encode(
        x=alt.X(
            "time_of_day:N",
            sort=time_ticks,
            axis=alt.Axis(
                labelAngle=-45,
                values=time_ticks,
                labelExpr='{'
                    + ', '.join(f'"{k}": "{v}"' for k, v in label_map.items())
                    + '}[datum.value]'
            )
        ),
        y=alt.Y("mean:Q", title="Glucose (mg/dL)"),
        tooltip=["label", "mean"]
    ).properties(height=300)

    # Band area: 15th–75th percentile range
    band = alt.Chart(agg).mark_area(opacity=0.3).encode(
        x=alt.X("time_of_day:N", sort=time_ticks),
        y="15th:Q",
        y2="75th:Q"
    )

    # Threshold lines: 70 and 180
    threshold_df = pd.DataFrame({
        "y": [70, 180],
        "label": ["LOW", "HIGH"],
        "color": ["red", "orange"]
    })

    ref_lines = alt.Chart(threshold_df).mark_rule().encode(
        y="y:Q",
        color=alt.Color("color:N", scale=None),
        tooltip="label"
    )

    return (band + line + ref_lines).resolve_scale(y='shared')
