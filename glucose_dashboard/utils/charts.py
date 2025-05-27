import pandas as pd
import altair as alt

def generate_glucose_time_chart(df: pd.DataFrame, start_date, end_date):
    chart_df = df.loc[
        (df["reading_timestamp"].dt.date >= start_date) &
        (df["reading_timestamp"].dt.date <= end_date),
        ["reading_timestamp", "glucose_mg_dl"]
    ].copy()

    chart_df.drop_duplicates(subset=["reading_timestamp", "glucose_mg_dl"], inplace=True)
    chart_df["reading_timestamp"] = pd.to_datetime(chart_df["reading_timestamp"]).dt.tz_localize(None)

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

    time_ticks = pd.date_range("00:00", "23:30", freq="30min").strftime("%H:%M").tolist()
    label_map = {
        h: pd.to_datetime(h, format="%H:%M").strftime("%I:%M %p").lstrip("0")
        for h in time_ticks
    }
    agg["label"] = agg["time_of_day"].map(label_map)

    # 🛡️ Handle missing or NaN percentiles
    p75_max = agg["p75"].max()
    y_max = p75_max + 10 if pd.notnull(p75_max) else 220
    y_domain = [0, max(220, y_max)]

    shared_x = alt.X(
        "time_of_day:N",
        sort=time_ticks,
        axis=alt.Axis(
            title="Time",
            labelAngle=-45,
            values=time_ticks,
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
        .configure_view(stroke=None)
        .configure_axis(grid=False)
        .interactive()
    )



def generate_glucose_heatmap(df: pd.DataFrame, threshold_type: str):
  """
  Generates a weekday x hour heatmap for high or low glucose events.
  """
  if df.empty:
    return None

  df = df.copy()
  df["weekday"] = df["reading_timestamp"].dt.strftime("%A")
  df["hour_of_day"] = df["reading_timestamp"].dt.strftime("%H:00")

  if threshold_type == "Low":
    filtered_df = df[df["glucose_mg_dl"] < 70]
  elif threshold_type == "High":
    filtered_df = df[df["glucose_mg_dl"] > 180]
  else:
    return None

  events = filtered_df.groupby(["weekday", "hour_of_day"]).size().reset_index(name="event_count")
  totals = df.groupby(["weekday", "hour_of_day"]).size().reset_index(name="total_count")

  merged = pd.merge(totals, events, how="left", on=["weekday", "hour_of_day"])
  merged["event_count"].fillna(0, inplace=True)
  merged["rate_pct"] = (merged["event_count"] / merged["total_count"]) * 100
  merged["rate_pct"] = merged["rate_pct"].round(1)
  merged["rate_str"] = merged["rate_pct"].round(1).astype(str) + "%"


  # Format hour label for tooltip
  merged["hour_label"] = merged["hour_of_day"].apply(
    lambda h: pd.to_datetime(h, format="%H:%M").strftime("%I:00 %p").lstrip("0")
  )

  hour_order = [f"{h:02}:00" for h in range(24)]
  label_map = {
    h: pd.to_datetime(h, format="%H:%M").strftime("%I:%M %p").lstrip("0")
    for h in hour_order
  }
  weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

  chart = alt.Chart(merged).mark_rect().encode(
    x=alt.X(
      "hour_of_day:O",
      title="Hour of Day",
      sort=hour_order,
      axis=alt.Axis(
        labelAngle=-45,
        labelExpr='{'
          + ', '.join(f'"{k}": "{v}"' for k, v in label_map.items())
          + '}[datum.value]'
      )
    ),
    y=alt.Y("weekday:O", sort=weekday_order, title="Day of Week"),
    color=alt.Color("rate_pct:Q", scale=alt.Scale(scheme="reds"), title="Rate (%)"),
    tooltip=[
      alt.Tooltip("weekday:N", title="Day"),
      alt.Tooltip("hour_label:N", title="Time"),
      alt.Tooltip("rate_str:N", title="Rate")
    ]
  ).properties(
    width=800,
    height=350,
    title=f"{threshold_type} Blood Glucose Heat Map"
  )

  

  return chart


import pandas as pd
import altair as alt

def generate_daily_average_chart(df: pd.DataFrame, start_date, end_date):
    """
    Shows daily average glucose with 7-day rolling average and clean x-axis.
    """
    if df.empty:
        return None

    # Ensure date column exists
    df = df.copy()
    df["date"] = pd.to_datetime(df["reading_timestamp"].dt.date)

    # Step 1: Compute daily average
    daily_avg_df = (
        df.groupby("date")["glucose_mg_dl"]
        .mean()
        .reset_index(name="avg_glucose")
    )

    if daily_avg_df.empty:
        return None

    # Step 2: Compute rolling average (7-day window)
    daily_avg_df["rolling_avg"] = daily_avg_df["avg_glucose"].rolling(window=7).mean()

    # Step 3: Filter after rolling avg computation
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    filtered_df = daily_avg_df[
        (daily_avg_df["date"] >= start_date) &
        (daily_avg_df["date"] <= end_date)
    ].copy()

    # Step 4: Prepare long-form dataframe for plotting
    # - Drop NaNs from rolling line
    # - Explicitly cast dates to datetime
    # - Drop any accidental duplicates

    rolling_df = (
        filtered_df[["date", "rolling_avg"]]
        .dropna()
        .rename(columns={"rolling_avg": "glucose"})
        .assign(label="7-Day Rolling Avg")
    )

    daily_df = (
        filtered_df[["date", "avg_glucose"]]
        .rename(columns={"avg_glucose": "glucose"})
        .assign(label="Daily Avg")
    )

    melted_df = pd.concat([daily_df, rolling_df])
    melted_df["date"] = pd.to_datetime(melted_df["date"])
    melted_df = melted_df.drop_duplicates(subset=["date", "label"])

    tick_count = min(30, melted_df["date"].nunique())


    if melted_df.empty:
        return None

    # Step 5: Define color palette
    color_scale = alt.Scale(
        domain=["Daily Avg", "7-Day Rolling Avg"],
        range=["#1f77b4", "orange"]
    )

    y_domain = [100, 180]  # Customize based on typical glucose range

    # Step 6: Build chart
    chart = alt.Chart(melted_df).mark_line(point=True).encode(
      x=alt.X(
        "date:T",
        title="Date",
        axis=alt.Axis(
          format="%b %d",
          labelAngle=-45,
          tickCount=tick_count,
          labelOverlap=True
        )
      ),
      y=alt.Y(
        "glucose:Q",
        title="Avg Glucose (mg/dL)",
        scale=alt.Scale(domain=y_domain)
      ),
      color=alt.Color("label:N", scale=color_scale, legend=alt.Legend(title="Legend")),
      strokeDash=alt.StrokeDash("label:N", legend=None),
      tooltip=[
        alt.Tooltip("date:T", title="Date", format="%B %d, %Y"),
        alt.Tooltip("glucose:Q", title="Glucose", format=".1f"),
        alt.Tooltip("label:N", title="Line")
      ]
    ).properties(
      title="📈 Daily Average Glucose Over Time"
    ).configure_view(
      stroke=None
    ).configure_axis(
      grid=False
    ).interactive()

    return chart








