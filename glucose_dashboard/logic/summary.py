def compute_summary_metrics(df):
    avg = df["glucose_mg_dl"].mean()
    std = df["glucose_mg_dl"].std()
    cv = (std / avg) * 100 if avg else 0

    in_range = df[(df["glucose_mg_dl"] >= 70) & (df["glucose_mg_dl"] <= 180)]
    high = df[df["glucose_mg_dl"] > 180]
    low = df[df["glucose_mg_dl"] < 70]

    total = len(df)
    return {
        "avg": avg,
        "std": std,
        "cv": cv,
        "in_range_pct": len(in_range) / total * 100 if total else 0,
        "high_pct": len(high) / total * 100 if total else 0,
        "low_pct": len(low) / total * 100 if total else 0,
    }