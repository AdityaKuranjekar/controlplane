import streamlit as st
from theme import inject_global_css

st.set_page_config(page_title="Production Scale", page_icon="🚀", layout="wide")
inject_global_css()
st.title("🚀 From Prototype to Production Scale")
st.caption("This prototype runs single-process on free-tier infrastructure. Here's exactly what changes — and what doesn't — to handle real enterprise load.")

st.subheader("The PS's own reference load, worked out")
col1, col2, col3 = st.columns(3)
col1.metric("Assumed weekly volume", "~50,000 requests")
col2.metric("→ Average req/sec", "~0.08 req/s")
col3.metric("→ Peak req/sec (10x burst)", "~0.8 req/s")
st.caption("Even generous peak assumptions land under 1 req/s sustained — the real engineering question isn't raw throughput, it's tail latency and correctness under concurrent load, which is what this page addresses.")

st.markdown("---")
st.subheader("Architecture: Prototype → Production")

comparison = [
    ("Gateway process", "Single FastAPI process, in-process asyncio", "Horizontally scaled FastAPI/Rust pods behind a load balancer (K8s HPA on CPU + queue depth), stateless by design so any pod can serve any request"),
    ("Semantic cache", "In-process FAISS flat index", "Managed vector DB (Qdrant/Pinecone) shared across all gateway pods — cache hits must be visible cluster-wide, not per-pod"),
    ("Cascade LLM calls", "Direct synchronous Groq call per request", "Async request queue (Kafka/Redis Streams) decouples ingestion from LLM latency; connection pooling + circuit breakers per provider"),
    ("Audit log", "SQLite, single file", "Append-only distributed log (ClickHouse) with WORM/S3 Object Lock for compliance-grade immutability; hash-chain verification runs as a background job, not synchronously"),
    ("Safety/PII model", "ONNX INT8 MiniLM, in-process", "Same model, but served via a dedicated low-latency inference pool (e.g. Triton/ONNX Runtime Server) so gateway pods don't each load a model into memory"),
    ("Rate limiting", "None (prototype)", "Per-tenant token-bucket rate limiting at the gateway edge, with backpressure signaled to callers rather than silent queuing"),
    ("Observability", "Streamlit console (manual)", "Prometheus metrics + Grafana dashboards + PagerDuty alerting on FNR/FPR drift, latency SLO breach, or audit-chain verification failure"),
]

for component, prototype, production in comparison:
    with st.container(border=True):
        c1, c2, c3 = st.columns([1, 1.5, 2])
        c1.markdown(f"**{component}**")
        c2.markdown(f"🔧 *Prototype:* {prototype}")
        c3.markdown(f"🏭 *Production:* {production}")

st.markdown("---")
st.subheader("What genuinely wouldn't change")
st.success("""
The **decision logic itself** — the deadline-tiered classification, the multi-label risk vector,
the conformal calibration method, the Intent Contract model — is infrastructure-independent.
Scaling this system is a systems-engineering problem (queues, pools, replication), not a
redesign of the governance logic. That separation is why this prototype's core mechanism
is a valid proof of the production architecture, not just a demo of unrelated ideas.
""")

st.subheader("Honest scaling risks we'd tackle first")
st.warning("""
- **Cache consistency across pods** at high concurrency needs careful invalidation design (a stale cached answer served from Pod A while Pod B just updated the same entry).
- **The L2 grounding gate's ~57% precision** (see Grounding Calibration page) means at real volume, false-positive review load could genuinely overwhelm a human review queue — this needs either a bigger NLI model or a cheaper second-stage filter before it's production-viable at scale, not just infra scaling.
- **Cold-start latency** on any newly-spun-up pod (model loading) needs a warm-pool strategy, not just autoscaling — autoscaling alone would cause a latency spike exactly when load is highest.
""")
