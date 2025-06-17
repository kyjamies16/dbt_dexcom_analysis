import plotly.graph_objects as go
import pandas as pd
import platform

def generate_glucose_time_chart(df, start_date, end_date):
    """
    Creates a time-of-day glucose chart with shaded P15–P75 band and average line.
    Adds clear labels to hover tooltip including P15 and P75.
    """

    # ----------------------------------------
    # 1️⃣ Filter data for selected date range
    # ----------------------------------------
    chart_df = df.loc[
        (df["reading_timestamp"].dt.date >= start_date) & 
        (df["reading_timestamp"].dt.date <= end_date),
        ["reading_timestamp", "glucose_mg_dl"]
    ].copy()

    if chart_df.empty:
        return None

    # ----------------------------------------
    # 2️⃣ Extract half-hour time slots
    # ----------------------------------------
    chart_df["reading_timestamp"] = pd.to_datetime(chart_df["reading_timestamp"])
    chart_df["time_of_day"] = chart_df["reading_timestamp"].dt.floor("30min").dt.strftime("%H:%M")

    # ----------------------------------------
    # 3️⃣ Calculate P15, Avg, P75 for each time slot
    # ----------------------------------------
    agg = chart_df.groupby("time_of_day")["glucose_mg_dl"].agg([
        ("p15", lambda x: x.quantile(0.15)),
        ("avg", "mean"),
        ("p75", lambda x: x.quantile(0.75))
    ]).reset_index()

    # ----------------------------------------
    # 4️⃣ Generate full time ticks & pretty labels
    # ----------------------------------------
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

    # Map labels & keep valid slots only
    agg = agg[agg["time_of_day"].isin(tick_map.keys())].copy()
    agg["label"] = agg["time_of_day"].map(tick_map)
    agg = agg.drop_duplicates(subset="label")

    # ----------------------------------------
    # 5️⃣ Build Plotly figure with P15–P75 band + Avg
    # ----------------------------------------
    fig = go.Figure()

    # Lower bound (P15)
    fig.add_trace(go.Scatter(
        x=agg["label"],
        y=agg["p15"],
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip",
        name="15th %"
    ))

    # Upper bound (P75) + fill to lower
    fig.add_trace(go.Scatter(
        x=agg["label"],
        y=agg["p75"],
        mode="lines",
        fill="tonexty",
        fillcolor="rgba(0,100,250,0.2)",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip",
        name="75th %"
    ))

    # Avg line + detailed hover template with P15 and P75
    fig.add_trace(go.Scatter(
        x=agg["label"],
        y=agg["avg"],
        mode="lines+markers",
        name="Avg Glucose",
        line=dict(color="blue"),
        hovertemplate=(
            "Time: %{x}<br>"
            "Avg: %{y:.1f} mg/dL<br>"
            "P15: %{customdata[0]:.1f} mg/dL<br>"
            "P75: %{customdata[1]:.1f} mg/dL"
        ),
        customdata=agg[["p15", "p75"]].values  # pass P15, P75 for each point
    ))

    # ----------------------------------------
    # 6️⃣ Add horizontal reference lines for LOW & HIGH
    # ----------------------------------------
    fig.add_hline(
        y=70,
        line=dict(color="red", dash="dash"),
        annotation_text="LOW",
        annotation_position="bottom left"
    )
    fig.add_hline(
        y=180,
        line=dict(color="orange", dash="dash"),
        annotation_text="HIGH",
        annotation_position="top left"
    )

    # ----------------------------------------
    # 7️⃣ Final layout tweaks
    # ----------------------------------------
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
