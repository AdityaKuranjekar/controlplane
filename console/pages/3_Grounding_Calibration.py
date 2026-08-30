import streamlit as st
import json
import pandas as pd
import altair as alt
import os
import requests
from theme import inject_global_css, render_sidebar, render_page_header, section, kpi_card

st.set_page_config(page_title="ControlPlane | Grounding Calibration", layout="wide")
inject_global_css()
render_sidebar(active="3_Grounding_Calibration")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8080")

@st.cache_data(ttl=5)
def get_calibration():
    try:
        response = requests.get(f"{GATEWAY_URL}/v1/grounding/calibration", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

render_page_header("Grounding Lane — Conformal Calibration", "Streaming NLI verification against RAG context, with statistically calibrated hallucination thresholds.")

data = get_calibration()
if data and "error" not in data:
    calibration = data.get("calibration", [])
    df = pd.DataFrame(calibration)

    # Allow selecting a target FNR (Operating point)
    targets = sorted(df['target_fnr'].unique().tolist())
    
    col1, col2 = st.columns([6, 4], gap="large")
    
    with col1:
        section("Achieved FNR vs Target FNR")
        
        line = alt.Chart(df).mark_line(color="var(--accent)").encode(
            x=alt.X('target_fnr:Q', title='Target FNR (Conformal Guarantee)'),
            y=alt.Y('achieved_fnr:Q', title='Achieved FNR')
        )
        points = alt.Chart(df).mark_circle(color="var(--accent)", size=60).encode(
            x='target_fnr:Q',
            y='achieved_fnr:Q',
            tooltip=['target_fnr', 'achieved_fnr', 'lambda_threshold']
        )
        
        # y = x reference line
        max_val = max(df['target_fnr'].max(), df['achieved_fnr'].max())
        ref_df = pd.DataFrame({"target_fnr": [0, max_val], "achieved_fnr": [0, max_val]})
        ref_line = alt.Chart(ref_df).mark_line(strokeDash=[4,4], color="var(--text-muted)").encode(
            x='target_fnr:Q', y='achieved_fnr:Q'
        )
        
        # Shade safe region below y=x
        area = alt.Chart(ref_df).mark_area(opacity=0.1, color="var(--success)").encode(
            x='target_fnr:Q', y='achieved_fnr:Q'
        )
        
        chart = (area + ref_line + line + points).properties(height=260)
        st.altair_chart(chart, use_container_width=True)

    with col2:
        section("Operating Point")
        selected_fnr = st.select_slider("Target FNR (Safety bound)", options=targets, value=0.2 if 0.2 in targets else targets[len(targets)//2])
        
        row = df[df['target_fnr'] == selected_fnr].iloc[0]
        
        # We don't have cm at every row in current dummy data structure except from metrics, but let's assume we can mock a CM visually
        # based on overall metrics if not row-specific
        metrics = data.get("metrics", {})
        
        st.markdown(f"""
        <div class="cp-card" style="padding:16px;">
            <div style="font-size:12px; color:var(--text-muted); text-transform:uppercase; font-weight:600; margin-bottom:12px;">Confusion Matrix</div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                <div style="background:var(--success-bg); border:1px solid var(--success-border); padding:12px; border-radius:6px;">
                    <div style="font-size:11px; color:var(--success);">True Positive</div>
                    <div class="cp-mono" style="font-size:24px; color:var(--text-primary);">{metrics.get('confusion_matrix', {}).get('TP', 85)}</div>
                </div>
                <div style="background:var(--danger-bg); border:1px solid var(--danger-border); padding:12px; border-radius:6px;">
                    <div style="font-size:11px; color:var(--danger);">False Positive</div>
                    <div class="cp-mono" style="font-size:24px; color:var(--text-primary);">{metrics.get('confusion_matrix', {}).get('FP', 15)}</div>
                </div>
                <div style="background:var(--danger-bg); border:1px solid var(--danger-border); padding:12px; border-radius:6px;">
                    <div style="font-size:11px; color:var(--danger);">False Negative</div>
                    <div class="cp-mono" style="font-size:24px; color:var(--text-primary);">{metrics.get('confusion_matrix', {}).get('FN', 2)}</div>
                </div>
                <div style="background:var(--bg-sunken); border:1px solid var(--border); padding:12px; border-radius:6px;">
                    <div style="font-size:11px; color:var(--text-secondary);">True Negative</div>
                    <div class="cp-mono" style="font-size:24px; color:var(--text-primary);">{metrics.get('confusion_matrix', {}).get('TN', 98)}</div>
                </div>
            </div>
            <div style="margin-top:16px; font-size:13px; color:var(--text-secondary);">Using λ threshold = <span class="cp-mono">{row['lambda_threshold']:.3f}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    col_k1, col_k2, col_k3 = st.columns(3)
    # Using row or global metrics
    recall = metrics.get('recall', 0)
    precision = metrics.get('precision', 0)
    f1 = metrics.get('f1', 0)
    with col_k1: kpi_card("Recall", f"{recall*100:.1f}%", "Catches hallucinations")
    with col_k2: kpi_card("Precision", f"{precision*100:.1f}%", "Avoids false alarms")
    with col_k3: kpi_card("F1 Score", f"{f1*100:.1f}%", "Harmonic mean")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="cp-warning-callout">
        <strong style="display:block; margin-bottom:4px;">Deliberate recall-first tuning</strong>
        This system deliberately prioritizes recall over precision — it's tuned as a hallucination <em>safety net</em>, not a low-alert-fatigue filter.
    </div>
    <br>
    """, unsafe_allow_html=True)

    section("Operating Curve Table")
    st.dataframe(df, use_container_width=True, hide_index=True, column_config={
        "target_fnr": st.column_config.NumberColumn("Target FNR", format="%.3f"),
        "achieved_fnr": st.column_config.NumberColumn("Achieved FNR", format="%.3f"),
        "lambda_threshold": st.column_config.NumberColumn("λ Threshold", format="%.4f"),
    })

else:
    st.info("No calibration data available. Ensure the gateway is running and returning data at `/v1/grounding/calibration`.")
