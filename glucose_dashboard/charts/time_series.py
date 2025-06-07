
import pandas as pd
import altair as alt

def generate_glucose_time_chart(df: pd.DataFrame, start_date, end_date):
    """
    Creates a time series chart of glucose readings over a specified date range
    """

    chart_df = df.loc[
        (df["reading_timestamp"].dt.date >= start_date) &
        (df["reading_timestamp"].dt.date <= end_date),
        ["reading_timestamp", "glucose_mg_dl"]
    ].copy()

    chart_df.drop_duplicates(subset=["reading_timestamp", "glucose_mg_dl"], inplace=True)
    chart_df["reading_timestamp"] = pd.to_datetime(chart_df["reading_timestamp"])

    if chart_df.empty:
        return None

    chart_df["time_of_day"] = chart_df["reading_timestamp"].dt.floor("30min").dt.strftime("%H:%M")

    agg = chart_df.groupby("time_of_day")["glucose_mg_dl"].agg([
        ("p15", lambda x: x.quantile(0.15)),
        ("avg", "mean"),
        ("p75", lambda x: x.quantile(0.75))
    ]).reset_index()

    agg["avg_str"] = agg["avg"].round(1).astype(str) + " mg/dL"
    agg["p15_str"] = agg["p15"].round(1).astype(str) + " mg/dL"
    agg["p75_str"] = agg["p75"].round(1).astype(str) + " mg/dL"

    # 1. All 30-min intervals (data categories)
    full_time_ticks = pd.date_range("00:00", "23:30", freq="30min").strftime("%H:%M").tolist()

    # 2. Hourly ticks for axis labeling
    visible_ticks = pd.date_range("00:00", "23:00", freq="1H").strftime("%H:%M").tolist()

    # 3. Label map: include labels for *all* 30-min intervals
    label_map = {}
    for t in full_time_ticks:
        dt = pd.to_datetime(t, format="%H:%M")
        label = dt.strftime("%I:%M %p").lstrip("0")  # '1:00 AM', '1:30 AM', etc.
        if label == "12:00 AM":
            label = "Midnight"
        elif label == "12:00 PM":
            label = "Noon"
        label_map[t] = label

    agg["label"] = agg["time_of_day"].map(label_map)

    # Handle missing or NaN percentiles
    p75_max = agg["p75"].max()
    y_max = p75_max + 10 if pd.notnull(p75_max) else 220
    y_domain = [0, max(220, y_max)]

    shared_x = alt.X(
        "time_of_day:N",
        sort=full_time_ticks,
        axis=alt.Axis(
            title="Time",
            labelAngle=-45,
            values=visible_ticks,  # 👈 only hourly labels shown
            labelExpr='{'
                + ', '.join(f'"{k}": "{v}"' for k, v in label_map.items())
                + '}[datum.value]'
        )
    )

    base = alt.Chart(agg).encode(
        x=shared_x,
        tooltip=[
            alt.Tooltip("label:N", title="Time"),
            alt.Tooltip("avg_str:N", title="Avg Glucose"),
            alt.Tooltip("p15_str:N", title="15th Percentile"),
            alt.Tooltip("p75_str:N", title="75th Percentile")
        ]
    )

    band = base.mark_area(opacity=0.3).encode(
        y=alt.Y("p15:Q", scale=alt.Scale(domain=y_domain), title="Glucose (mg/dL)"),
        y2="p75:Q"
    )

    line = base.mark_line().encode(
        y=alt.Y("avg:Q", scale=alt.Scale(domain=y_domain))
    )

    threshold_df = pd.DataFrame({
        "y": [70, 180],
        "label": ["LOW", "HIGH"],
        "color": ["red", "orange"]
    })

    rule_chart = alt.Chart(threshold_df).mark_rule().encode(
        y=alt.Y("y:Q", scale=alt.Scale(domain=y_domain)),
        color=alt.Color("color:N", scale=None),
        tooltip=alt.Tooltip("label")
    )

    threshold_labels = alt.Chart(threshold_df).mark_text(
        align="left",
        baseline="middle",
        dx=10,
        fontWeight="bold",
        fontSize=12,
        color="white",
        clip=False
    ).encode(
        y=alt.Y("y:Q", scale=alt.Scale(domain=y_domain)),
        text=alt.Text("y:Q")
    )

    return (
        alt.layer(band, line, rule_chart, threshold_labels)
        .resolve_scale(y='shared')
        .properties(padding={"bottom": 80})
        .configure_view(stroke=None)
        .configure_axis(grid=False)
        .interactive()
    )
