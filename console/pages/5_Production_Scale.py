import streamlit as st
import pandas as pd
from console.theme import inject_global_css, render_sidebar, render_page_header, section, kpi_card

st.set_page_config(page_title="ControlPlane | Production Scale", layout="wide")
inject_global_css()
render_sidebar(active="5_Production_Scale")

render_page_header("From Prototype to Production Scale", "This prototype runs single-process on free-tier infrastructure. Here's exactly what changes — and what doesn't — to handle real enterprise load.")

section("Reference Load Assumptions")
col1, col2, col3 = st.columns(3)
with col1: kpi_card("Weekly Volume", "~50,000", "Assumed requests")
with col2: kpi_card("Average req/sec", "~0.08", "Sustained load")
with col3: kpi_card("Peak req/sec", "~0.8", "10x burst multiplier")

st.markdown("""
<div style="font-size:13px; color:var(--text-muted); margin:16px 0 32px 0;">
Even generous peak assumptions land under 1 req/s sustained — the real engineering question isn't raw throughput, it's tail latency and correctness under concurrent load.
</div>
""", unsafe_allow_html=True)

section("Architecture: Prototype vs. Production")
comparison = [
    {"Component": "Gateway process", "Prototype": "Single FastAPI process, in-process asyncio", "Production": "Horizontally scaled FastAPI/Rust pods behind a load balancer (K8s HPA on CPU + queue depth)"},
    {"Component": "Semantic cache", "Prototype": "In-process FAISS flat index", "Production": "Managed vector DB (Qdrant/Pinecone) shared across all gateway pods"},
    {"Component": "Cascade LLM calls", "Prototype": "Direct synchronous Groq call per request", "Production": "Async request queue (Kafka/Redis Streams); connection pooling + circuit breakers"},
    {"Component": "Audit log", "Prototype": "SQLite, single file", "Production": "Append-only distributed log (ClickHouse) with WORM/S3 Object Lock"},
    {"Component": "Safety/PII model", "Prototype": "ONNX INT8 MiniLM, in-process", "Production": "Served via a dedicated low-latency inference pool (e.g., Triton/ONNX Runtime Server)"},
    {"Component": "Rate limiting", "Prototype": "None", "Production": "Per-tenant token-bucket rate limiting at the edge with backpressure"},
    {"Component": "Governance Logic", "Prototype": "Deadline-tiered, Intent Contract, calibration", "Production": "UNCHANGED"},
    {"Component": "Observability", "Prototype": "Streamlit console (manual)", "Production": "Prometheus metrics + Grafana + PagerDuty alerting on FNR/FPR drift or SLO breaches"}
]

# Create a custom HTML table to allow subtle tags on specific rows
table_html = """
<div class="cp-card" style="padding:0; overflow:hidden;">
  <table style="width:100%; border-collapse:collapse; text-align:left; font-size:14px;">
    <thead>
      <tr style="background:var(--bg-canvas); border-bottom:1px solid var(--border);">
        <th style="padding:16px 20px; font-weight:600; font-size:13px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em; width:20%;">Component</th>
        <th style="padding:16px 20px; font-weight:600; font-size:13px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em; width:35%;">Prototype (Current)</th>
        <th style="padding:16px 20px; font-weight:600; font-size:13px; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em; width:45%;">Production Target</th>
      </tr>
    </thead>
    <tbody>
"""

for i, row in enumerate(comparison):
    border_style = "border-bottom:1px solid var(--border);" if i < len(comparison) - 1 else ""
    is_unchanged = row["Production"] == "UNCHANGED"
    
    prod_content = f"""<span class="cp-chip" style="background:var(--success-bg); color:var(--success); border:1px solid var(--success-border);">Unchanged</span>""" if is_unchanged else f"<span style='color:var(--text-secondary);'>{row['Production']}</span>"
    
    if is_unchanged:
        proto_content = f"<span style='color:var(--text-secondary);'>{row['Prototype']}</span>"
    else:
        proto_content = f"<span style='color:var(--text-secondary);'>{row['Prototype']}</span>"

    table_html += f"""
      <tr style="{border_style}">
        <td style="padding:16px 20px; font-weight:500;">{row['Component']}</td>
        <td style="padding:16px 20px;">{proto_content}</td>
        <td style="padding:16px 20px;">{prod_content}</td>
      </tr>
    """

table_html += """
    </tbody>
  </table>
</div>
"""
st.markdown(table_html, unsafe_allow_html=True)

st.markdown("""
<div style="font-size:13px; color:var(--text-muted); margin:16px 0 32px 0;">
The decision logic itself is infrastructure-independent. Scaling this system is a systems-engineering problem (queues, pools, replication), not a redesign of the governance logic.
</div>
""", unsafe_allow_html=True)

section("Scaling Risks to Address First")
st.markdown("""
<div class="cp-warning-callout">
    <ul style="margin:0; padding-left:20px;">
        <li style="margin-bottom:8px;"><strong>Cache consistency across pods:</strong> At high concurrency, requires careful invalidation design (e.g., preventing a stale cached answer served from Pod A while Pod B just updated the entry).</li>
        <li style="margin-bottom:8px;"><strong>L2 Grounding precision limits:</strong> The ~57% precision means false-positive review load could overwhelm a human queue at scale — needs either a larger NLI model or a cheaper second-stage filter, not just infra scaling.</li>
        <li><strong>Cold-start latency:</strong> Newly spun-up pods loading models need a warm-pool strategy, not just autoscaling; otherwise, latency spikes occur exactly when load is highest.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
