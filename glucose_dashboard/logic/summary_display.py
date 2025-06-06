# logic/summary_display.py

import streamlit as st

def display_glucose_metrics(metrics: dict):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Glucose", f"{metrics['avg']:.0f} mg/dL")
        st.metric("Standard Deviation", f"{metrics['std']:.0f} mg/dL")
        st.caption("ℹ️ Normal std dev range is 30–50 mg/dL.")
    with col2:
        st.metric("Coefficient of Variation", f"{metrics['cv']:.1f}%")
        st.caption("ℹ️ CV = std dev / mean. Below 36% indicates good stability.")
    with col3:
        st.markdown("**Time in Range**")
        st.markdown(f"🟩 In Range: **{metrics['in_range_pct']:.0f}%**")
        st.markdown(f"🟥 Low: **{metrics['low_pct']:.0f}%**")
        st.markdown(f"🟧 High: **{metrics['high_pct']:.0f}%**")
        st.caption("Target range: 70–180 mg/dL.")
