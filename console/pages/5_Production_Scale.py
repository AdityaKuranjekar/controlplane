import streamlit as st
from theme import inject_global_css, render_top_navbar

st.set_page_config(page_title="Production Scale — ControlPlane", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")
inject_global_css()
render_top_navbar("Production_Scale")

st.markdown("""
<div class="cp-page-title">
  🚀 From Prototype to Enterprise Production Scale<span class="cp-cursor"></span>
</div>
<p class="cp-page-desc">
  System engineering migration roadmap: scaling from single-process prototype to high-throughput, horizontally partitioned cloud infrastructure.
</p>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("Weekly Ingestion Volume", "~50,000 req/wk")
col2.metric("Average Throughput", "~0.08 req/s")
col3.metric("Peak Burst Throughput (10x)", "~0.8 req/s")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### Architecture Migration Matrix: Prototype vs Production")

comparison = [
    ("Gateway Ingestion", "Single FastAPI process, in-process asyncio", "Horizontally scaled Rust / Axum pods behind Envoy / K8s HPA with connection pooling"),
    ("Semantic Cache", "In-process FAISS flat index", "Distributed Qdrant / Pinecone cluster shared across all edge pods with sub-millisecond gRPC routing"),
    ("Cascade LLM Calls", "Direct synchronous Groq client", "Async task queue (Redis / Kafka) with circuit breakers and multi-provider failover"),
    ("Audit Log", "SQLite single file with SHA-256 chain", "ClickHouse append-only log with AWS S3 WORM / Object Lock compliance immutability"),
    ("Safety & PII Scanners", "In-process compiled regex & ONNX MiniLM", "Triton Inference Server pool with batch GPU acceleration"),
    ("Rate Limiting", "Per-profile threshold policy", "Redis token-bucket rate limiting at the API gateway edge with backpressure signaling"),
]

for component, prototype, production in comparison:
    with st.container():
        st.markdown(f"""
        <div class="cp-box">
          <div class="cp-card-title">{component}</div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; font-size: 13.5px;">
            <div style="color: #4B5563;"><strong>🔧 Prototype:</strong> {prototype}</div>
            <div style="color: #111827;"><strong>🏭 Production:</strong> {production}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### What Genuinely Remains Invariant")
st.info("""
The **deadline-tiered decision engine**, multi-label risk vectors, conformal calibration methods, and intent contract models are completely infrastructure-independent. Scaling this system is a distributed systems engineering process, not a rewrite of the security governance core.
""")
