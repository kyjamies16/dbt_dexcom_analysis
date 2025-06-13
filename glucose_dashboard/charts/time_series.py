import plotly.graph_objects as go
import pandas as pd
import platform


def generate_glucose_time_chart(df, start_date, end_date):
    chart_df = df.loc[
        (df["reading_timestamp"].dt.date >= start_date) & 
        (df["reading_timestamp"].dt.date <= end_date),
        ["reading_timestamp", "glucose_mg_dl"]
    ].copy()

    if chart_df.empty:
        return None

    chart_df["reading_timestamp"] = pd.to_datetime(chart_df["reading_timestamp"])
    chart_df["time_of_day"] = chart_df["reading_timestamp"].dt.floor("30min").dt.strftime("%H:%M")

    agg = chart_df.groupby("time_of_day")["glucose_mg_dl"].agg([
        ("p15", lambda x: x.quantile(0.15)),
        ("avg", "mean"),
        ("p75", lambda x: x.quantile(0.75))
    ]).reset_index()

    # Format ticks like "Midnight", "1 AM", "Noon", etc.
    tick_times = pd.date_range("00:00", "23:30", freq="30min")
    full_time_ticks = tick_times.strftime("%H:%M").tolist()

    def format_time_label(t):
        dt = pd.to_datetime(t, format="%H:%M")
        hour = dt.hour
        if hour == 0:
            return "Midnight"
        elif hour == 12:
            return "Noon"
        else:
            fmt = "%#I %p" if platform.system() == "Windows" else "%-I %p"
            return dt.strftime(fmt)

    tick_map = {t: format_time_label(t) for t in full_time_ticks}
    agg = agg[agg["time_of_day"].isin(tick_map.keys())].copy()
    agg["label"] = agg["time_of_day"].map(tick_map)

    # Remove potential duplicate labels
    agg = agg.drop_duplicates(subset="label")

    fig = go.Figure()

    # Add shaded band
    fig.add_trace(go.Scatter(
        x=agg["label"], y=agg["p15"], mode="lines",
        line=dict(width=0), showlegend=False, hoverinfo='skip', name="15th %"
    ))
    fig.add_trace(go.Scatter(
        x=agg["label"], y=agg["p75"], mode="lines",
        fill='tonexty', fillcolor='rgba(0,100,250,0.2)',
        line=dict(width=0), showlegend=False, hoverinfo='skip', name="75th %"
    ))

    # Add average line
    fig.add_trace(go.Scatter(
        x=agg["label"], y=agg["avg"], mode="lines+markers",
        name="Avg Glucose", line=dict(color='blue'),
        hovertemplate="Time: %{x}<br>Avg: %{y:.1f} mg/dL"
    ))

    # Reference lines
    fig.add_hline(y=70, line=dict(color="red", dash="dash"), annotation_text="LOW", annotation_position="bottom left")
    fig.add_hline(y=180, line=dict(color="orange", dash="dash"), annotation_text="HIGH", annotation_position="top left")

    fig.update_layout(
        yaxis=dict(title="Glucose (mg/dL)", range=[50, 250]),
        xaxis=dict(
            title="Time of Day",
            tickmode="array",
            tickvals=agg["label"].tolist(),
            ticktext=agg["label"].tolist(),
            tickangle=-45
        ),
        margin=dict(t=40, b=100),
        height=400,
        showlegend=False
    )

    return fig