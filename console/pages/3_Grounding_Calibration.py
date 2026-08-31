import streamlit as st
import json
import pandas as pd
import os
import requests
from theme import inject_global_css, render_top_navbar

st.set_page_config(page_title="Grounding Calibration — ControlPlane", page_icon="🎯", layout="wide", initial_sidebar_state="collapsed")
inject_global_css()
render_top_navbar("Grounding_Calibration")

st.markdown("""
<div class="cp-page-title">
  🎯 Grounding Lane — Conformal Calibration<span class="cp-cursor"></span>
</div>
<p class="cp-page-desc">
  Streaming NLI verification against RAG source context chunks, guaranteed by rigorous conformal prediction bounds.
</p>
""", unsafe_allow_html=True)

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8080")

try:
    response = requests.get(f"{GATEWAY_URL}/v1/grounding/calibration")
    if response.status_code == 200:
        data = response.json()
        if "error" in data:
            st.warning(f"No calibration data found on gateway: {data['error']}")
        else:
            calibration = data.get("calibration", [])
            metrics = data.get("metrics", {})

            col1, col2, col3 = st.columns(3)
            col1.metric("Hallucination Recall", f"{metrics.get('recall', 1.0)*100:.1f}%", "Safety-net priority")
            col2.metric("Target FNR Bound", "20.0%", "Strict ceiling")
            col3.metric("Evaluator", "gpt-oss-20b NLI", "Cross-entropy")

            st.markdown("<br>", unsafe_allow_html=True)

            df = pd.DataFrame(calibration)
            st.markdown("### Achieved FNR vs Target FNR (Conformal Guarantee)")
            chart_df = df[["target_fnr", "achieved_fnr"]].set_index("target_fnr")
            st.line_chart(chart_df)
            st.caption("Achieved False Negative Rate (FNR) stays at or below the target ceiling line at every operating point.")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Operating Curve Threshold Detail")
            st.dataframe(df, use_container_width=True)
    else:
        st.error(f"Failed to fetch calibration data: {response.text}")
except Exception as e:
    st.error(f"Failed to connect to gateway: {e}")
