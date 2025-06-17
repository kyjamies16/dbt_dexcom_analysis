import pandas as pd

def find_spike_events(df, roc_threshold=30, normal_threshold=140, max_duration_min=400, gap_threshold_min=10):
    """
    Detect spike recovery events in glucose data.
    
    Parameters:
        df (pd.DataFrame): Must have 'reading_timestamp' and 'glucose_mg_dl'.
        roc_threshold (float): Minimum rate of change (mg/dL/hr) to define a spike start.
        normal_threshold (float): Glucose value that marks spike recovery.
        max_duration_min (float): Maximum duration in minutes; events longer than this are discarded.
        gap_threshold_min (float): Maximum allowed gap between readings in minutes; larger gaps break data into chunks.

    Returns:
        pd.DataFrame: One row per detected spike event.
    """

    # Sort by timestamp for safety
    df = df.copy().sort_values("reading_timestamp")

    # ---------------------------------------------
    # STEP 1: Detect data gaps to split into chunks
    # ---------------------------------------------
    df["time_diff_min"] = df["reading_timestamp"].diff().dt.total_seconds() / 60
    # Any gap larger than threshold means a new chunk
    df["chunk"] = (df["time_diff_min"] > gap_threshold_min).cumsum()

    # ---------------------------------------------
    # STEP 2: Prepare binning for peak glucose
    # ---------------------------------------------
    bins = [140, 160, 180, 200, 250, 300, float("inf")]
    labels = ["140–160", "160–180", "180–200", "200–250", "250–300", "300+"]

    # ---------------------------------------------
    # STEP 3: Loop through each chunk independently
    # ---------------------------------------------
    all_spikes = []

    for _, chunk in df.groupby("chunk"):
        chunk = chunk.copy()

        # Compute Rate of Change (RoC) for this chunk
        chunk["glucose_shift"] = chunk["glucose_mg_dl"].shift(1)
        chunk["time_diff_hr"] = (chunk["reading_timestamp"] - chunk["reading_timestamp"].shift(1)).dt.total_seconds() / 3600
        chunk["roc"] = (chunk["glucose_mg_dl"] - chunk["glucose_shift"]) / chunk["time_diff_hr"]
        chunk["spike_start"] = chunk["roc"] >= roc_threshold

        in_spike = False
        start_idx = None
        peak_glucose = None

        for idx, row in chunk.iterrows():
            if row["spike_start"]:
                if not in_spike:
                    # Start a new spike
                    in_spike = True
                    start_idx = idx
                    peak_glucose = row["glucose_mg_dl"]
                else:
                    # Update peak if higher
                    peak_glucose = max(peak_glucose, row["glucose_mg_dl"])
            else:
                if in_spike and row["glucose_mg_dl"] <= normal_threshold:
                    # End the spike
                    start_time = chunk.loc[start_idx, "reading_timestamp"]
                    end_time = row["reading_timestamp"]
                    duration_min = (end_time - start_time).total_seconds() / 60

                    peak_bin = pd.cut([peak_glucose], bins=bins, labels=labels, right=False)[0]

                    all_spikes.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration_min": round(duration_min, 1),
                        "peak_glucose": peak_glucose,
                        "peak_bin": peak_bin
                    })

                    # Reset spike state
                    in_spike = False
                    start_idx = None
                    peak_glucose = None

    # ---------------------------------------------
    # STEP 4: Combine and filter by max duration
    # ---------------------------------------------
    spikes_df = pd.DataFrame(all_spikes)
    if not spikes_df.empty:
        spikes_df = spikes_df[spikes_df["duration_min"] <= max_duration_min]

    return spikes_df
