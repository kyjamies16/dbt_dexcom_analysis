import altair as alt

def plot_spike_recovery(spike_events):
    # Filter to complete spikes and peaks >= 140
    spike_events = spike_events[
        (spike_events["peak_glucose"] >= 140)
        & spike_events["start_time"].notna()
        & spike_events["end_time"].notna()
    ]

    scatter = alt.Chart(spike_events).mark_circle(
        size=60,
        opacity=0.5,
        color="#4dabf7"
    ).encode(
        x=alt.X(
            "peak_glucose:Q",
            title="Peak Glucose (mg/dL)",
            scale=alt.Scale(domain=[140, spike_events["peak_glucose"].max() + 10])
        ),
        y=alt.Y(
            "duration_min:Q",
            title="Time to Recover (minutes)"
        ),
        tooltip=[
            alt.Tooltip("start_time:T", title="Start", format="%B %d, %Y %I:%M %p"),
            alt.Tooltip("end_time:T", title="End", format="%B %d, %Y %I:%M %p"),
            alt.Tooltip("peak_glucose:Q", title="Peak (mg/dL)"),
            alt.Tooltip("duration_min:Q", title="Duration (min)")
        ]
    )

    trend = alt.Chart(spike_events).transform_loess(
        "peak_glucose", "duration_min"
    ).mark_line(
        color="orange",
        size=3
    ).encode(
        x="peak_glucose:Q",
        y="duration_min:Q"
        
    )

    chart = (scatter + trend).properties(
        title="Spike Recovery Time vs. Peak Glucose",
        width=800,
        height=400
    )

    return chart
