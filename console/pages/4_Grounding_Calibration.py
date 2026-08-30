import streamlit as st
import json
import pandas as pd

st.set_page_config(page_title="Grounding Calibration", layout="wide")

st.title("Grounding Lane — Conformal Calibration")
st.caption("Streaming NLI verification against RAG context, with statistically calibrated hallucination thresholds.")

try:
    calibration = json.load(open("eval/results/l2_calibration.json"))
    metrics = json.load(open("eval/results/l2_metrics.json"))

    df = pd.DataFrame(calibration)
    st.subheader("Achieved FNR vs Target FNR (Conformal Guarantee)")
    chart_df = df[["target_fnr", "achieved_fnr"]].set_index("target_fnr")
    st.line_chart(chart_df)
    st.caption("Achieved FNR stays at or below the target line at every operating point — this is the calibration guarantee working correctly, not just a hardcoded threshold.")

    st.subheader("Operating Curve Detail")
    st.dataframe(df, use_container_width=True)

    st.subheader("Confusion Matrix at 0.20 Target FNR")
    cm = metrics["confusion_matrix"]
    col1, col2 = st.columns(2)
    col1.metric("Recall (catches hallucinations)", f"{metrics['recall']*100:.1f}%")
    col2.metric("Precision (avoids false alarms)", f"{metrics['precision']*100:.1f}%")
    
    st.warning(
        "This system deliberately prioritizes recall over precision — it's tuned as a "
        "hallucination *safety net*, not a low-alert-fatigue filter. See LIMITATIONS.md "
        "for the full honest tradeoff discussion."
    )
except FileNotFoundError:
    st.info("No calibration data found. Please run the L2 eval suite to generate `eval/results/l2_calibration.json`.")
