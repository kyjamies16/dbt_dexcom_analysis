import pandas as pd
import altair as alt

def generate_daily_average_chart(df: pd.DataFrame, start_date, end_date):
  """
  Shows daily average glucose with 7-day rolling average.

  Args:
    df (pd.DataFrame): DataFrame with at least 'reading_timestamp' and 'glucose_mg_dl' columns.
    start_date (str or datetime): Start date for filtering (inclusive).
    end_date (str or datetime): End date for filtering (inclusive).

  Returns:
    alt.Chart or None: Altair chart object or None if no data.
  """
  if df.empty:
    return None

  # Copy DataFrame and ensure 'date' column exists (date part only)
  df = df.copy()
  df["reading_timestamp"] = pd.to_datetime(df["reading_timestamp"])
  df["date"] = pd.to_datetime(df["reading_timestamp"].dt.date)

  # Validate start_date and end_date
  try:
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
  except Exception as e:
    raise ValueError(f"Invalid date format for start_date or end_date: {e}")

  # Step 1: Compute daily average glucose values
  daily_avg_df = (
    df.groupby("date")["glucose_mg_dl"]
    .mean()
    .reset_index(name="avg_glucose")
  )

  if daily_avg_df.empty:
   daily_avg_df["rolling_avg"] = daily_avg_df["avg_glucose"].rolling(window=7, min_periods=1).mean()

  # Step 2: Compute 7-day rolling average of daily averages
  daily_avg_df["rolling_avg"] = daily_avg_df["avg_glucose"].rolling(window=7).mean()

  # Step 3: Filter data to the specified date range
  start_date = pd.to_datetime(start_date)
  end_date = pd.to_datetime(end_date)
  filtered_df = daily_avg_df[
    (daily_avg_df["date"] >= start_date) &
    (daily_avg_df["date"] <= end_date)
  ].copy()

  # Step 4: Prepare data for plotting
  # - rolling_df: 7-day rolling average (drop NaNs)
  # - daily_df: daily average
  # - Combine both for plotting
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

  # Combine daily and rolling data, ensure dates are datetime, drop duplicates
  melted_df = pd.concat([daily_df, rolling_df])
  melted_df["date"] = pd.to_datetime(melted_df["date"])
  melted_df = melted_df.drop_duplicates(subset=["date", "label"])

  # Limit number of x-axis ticks for readability
  # Limit the number of x-axis ticks to 30 for better visual clarity and readability
  tick_count = min(30, melted_df["date"].nunique())

  if melted_df.empty:
    return None

  # Step 5: Define color palette for the lines
  color_scale = alt.Scale(
    domain=["Daily Avg", "7-Day Rolling Avg"],
    range=["#1f77b4", "orange"]
  )
  # Dynamically calculate y-axis domain based on data range or use default
  y_min = melted_df["glucose"].min() - 10  # Add padding
  y_max = melted_df["glucose"].max() + 10  # Add padding
  y_domain = [y_min, y_max]
  y_domain = [100, 180]

  # Step 6: Build Altair line chart
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
