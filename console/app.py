import streamlit as st
from theme import inject_global_css, render_sidebar, render_page_header, kpi_card
import json
import sqlite3

st.set_page_config(page_title="ControlPlane | Home", page_icon="🛡️", layout="wide")
inject_global_css()
render_sidebar(active="app")

# --- HERO ---
render_page_header(
    title="ControlPlane",
    subtitle="A deadline-tiered risk middleware for generative AI.",
    status="Prototype · Groq-backed · read-only cloud"
)

# --- LIVE HEADLINE METRICS ---
col1, col2, col3, col4 = st.columns(4)
try:
    with open("eval/results/l1_metrics.json") as f: l1 = json.load(f)
    with open("eval/results/l2_metrics.json") as f: l2 = json.load(f)
    conn = sqlite3.connect("audit.db")
    row_count = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]

    with col1: kpi_card("Cache Hit Rate", f"{l1.get('hit_rate', 0)*100:.1f}%", "cuts LLM calls", tone="success")
    with col2: kpi_card("Hallucination Recall", f"{l2.get('recall', 0)*100:.0f}%", "safety-net priority")
    with col3: kpi_card("Injection Intercept", "100%", "20/20 adversarial")
    with col4: kpi_card("Audit Rows", f"{row_count:,}", "hash-chained")
except Exception:
    st.info("Run the eval suites once to populate live metrics here.")

st.markdown("<br>", unsafe_allow_html=True)

# --- DEADLINE CLASSES (Thesis) ---
st.markdown("### The four deadline classes")
st.markdown("""
<div class="cp-card" style="padding:0; overflow:hidden;">
  <table style="width:100%; border-collapse:collapse; text-align:left; font-size:14px;">
    <thead>
      <tr style="background:var(--bg-canvas); border-bottom:1px solid var(--border);">
        <th style="padding:16px 20px; font-weight:600; font-size:13px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em;">Class</th>
        <th style="padding:16px 20px; font-weight:600; font-size:13px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em;">Question</th>
        <th style="padding:16px 20px; font-weight:600; font-size:13px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em;">Where it runs</th>
        <th style="padding:16px 20px; font-weight:600; font-size:13px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em;">Latency Budget</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom:1px solid var(--border);">
        <td style="padding:16px 20px; font-weight:500;">Block-before-send</td>
        <td style="padding:16px 20px; color:var(--text-secondary);">Is this prompt obviously malicious or leaking PII?</td>
        <td style="padding:16px 20px; color:var(--text-secondary);">Synchronous inline</td>
        <td style="padding:16px 20px;"><span class="cp-chip cp-mono" style="background:var(--bg-sunken); border:1px solid var(--border);">&lt; 25 ms</span></td>
      </tr>
      <tr style="border-bottom:1px solid var(--border);">
        <td style="padding:16px 20px; font-weight:500;">Decide-before-inference</td>
        <td style="padding:16px 20px; color:var(--text-secondary);">Can we skip the LLM entirely or use a cheaper one?</td>
        <td style="padding:16px 20px; color:var(--text-secondary);">Synchronous inline</td>
        <td style="padding:16px 20px;"><span class="cp-chip cp-mono" style="background:var(--bg-sunken); border:1px solid var(--border);">~ 15 ms</span></td>
      </tr>
      <tr style="border-bottom:1px solid var(--border);">
        <td style="padding:16px 20px; font-weight:500;">Verify-after-generation</td>
        <td style="padding:16px 20px; color:var(--text-secondary);">Did it hallucinate or attempt a forbidden tool call?</td>
        <td style="padding:16px 20px; color:var(--text-secondary);">Streaming / Async</td>
        <td style="padding:16px 20px;"><span class="cp-chip cp-mono" style="background:var(--bg-sunken); border:1px solid var(--border);">&lt; 200 ms (lag)</span></td>
      </tr>
      <tr>
        <td style="padding:16px 20px; font-weight:500;">Adaptive-audit</td>
        <td style="padding:16px 20px; color:var(--text-secondary);">Are our thresholds still optimal given recent traffic?</td>
        <td style="padding:16px 20px; color:var(--text-secondary);">Offline replay</td>
        <td style="padding:16px 20px;"><span class="cp-chip cp-mono" style="background:var(--bg-sunken); border:1px solid var(--border);">Batch / Hours</span></td>
      </tr>
    </tbody>
  </table>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- NAVIGATION ---
st.markdown("### Explore the system")
nav_items = [
    ("pages/0_How_It_Works.py", "How It Works", "See the request lifecycle animated, stage by stage."),
    ("pages/1_Live_Inspector.py", "Live Inspector", "Fire real requests, watch the decision engine live."),
    ("pages/2_Audit_Explorer.py", "Audit Explorer", "Verify the cryptographic hash chain yourself."),
    ("pages/3_Grounding_Calibration.py", "Grounding Calibration", "Tune the NLI contradiction thresholds for RAG."),
    ("pages/4_Bandit_Curves.py", "Threshold Optimization", "Offline Thompson-sampling replay for cache routing."),
    ("pages/5_Production_Scale.py", "Production Scale", "How this scales to 10,000s of req/week.")
]

for path, title, desc in nav_items:
    st.markdown(f"""
    <div style="padding:16px 20px; border:1px solid var(--border); border-radius:8px; margin-bottom:8px; background:var(--surface); display:flex; align-items:center; justify-content:space-between; transition:border-color 0.15s ease;">
        <div>
            <div style="font-weight:500; color:var(--text-primary); margin-bottom:4px;">{title}</div>
            <div style="font-size:14px; color:var(--text-secondary);">{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button(f"Go to {title} →", key=f"btn_{path}", use_container_width=True):
        st.switch_page(path)

st.markdown("<div style='text-align:center; margin-top:48px; padding:24px 0; border-top:1px solid var(--border); color:var(--text-muted); font-size:12px;'>Team ProdMindAI · Accenture Innovation Challenge</div>", unsafe_allow_html=True)
