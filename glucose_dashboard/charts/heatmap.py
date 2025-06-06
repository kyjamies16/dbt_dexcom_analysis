import pandas as pd
import altair as alt

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