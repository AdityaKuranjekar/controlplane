import streamlit as st
import streamlit.components.v1 as components
from theme import inject_global_css

st.set_page_config(page_title="How It Works", page_icon="🔍", layout="wide")
inject_global_css()
st.title("🔍 How a Request Actually Flows Through ControlPlane")
st.caption("This is a live animation of the real architecture — not a mockup. Every stage shown here maps to real code you can inspect in the repo.")

components.html("""
<div style="background:#0d0d0d; border-radius:16px; padding:40px 20px; font-family:Inter,sans-serif;">
<svg viewBox="0 0 1000 220" style="width:100%; height:auto;">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#666"/>
    </marker>
  </defs>

  <!-- connecting line -->
  <line x1="60" y1="110" x2="940" y2="110" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- traveling packet -->
  <circle r="8" fill="#A100FF">
    <animateMotion dur="4s" repeatCount="indefinite"
      path="M60,110 L940,110" />
    <animate attributeName="fill" values="#A100FF;#A100FF;#D62828;#A100FF" dur="4s" repeatCount="indefinite"/>
  </circle>

  <!-- stage boxes -->
  <g font-size="13" font-weight="700" fill="white" text-anchor="middle">
    <rect x="20" y="80" width="120" height="60" rx="8" fill="#1a1a1a" stroke="#A100FF" stroke-width="1.5"/>
    <text x="80" y="105">L0</text><text x="80" y="122" font-size="11" font-weight="400" fill="#999">PII + Safety</text>

    <rect x="220" y="80" width="120" height="60" rx="8" fill="#1a1a1a" stroke="#A100FF" stroke-width="1.5"/>
    <text x="280" y="105">L1</text><text x="280" y="122" font-size="11" font-weight="400" fill="#999">Cache/Cascade</text>

    <rect x="420" y="80" width="120" height="60" rx="8" fill="#1a1a1a" stroke="#A100FF" stroke-width="1.5"/>
    <text x="480" y="105">L2</text><text x="480" y="122" font-size="11" font-weight="400" fill="#999">Grounding</text>

    <rect x="620" y="80" width="120" height="60" rx="8" fill="#1a1a1a" stroke="#A100FF" stroke-width="1.5"/>
    <text x="680" y="105">L3</text><text x="680" y="122" font-size="11" font-weight="400" fill="#999">Action Gate</text>

    <rect x="820" y="80" width="120" height="60" rx="8" fill="#1a1a1a" stroke="#1a7f37" stroke-width="1.5"/>
    <text x="880" y="105">✓ ALLOW</text><text x="880" y="122" font-size="11" font-weight="400" fill="#999">or BLOCK</text>
  </g>
</svg>
<p style="color:#888; text-align:center; margin-top:10px; font-size:13px;">
  The purple dot flashes red when a stage decides to intercept — exactly what the real gateway logs to the audit chain.
</p>
</div>
""", height=320)

st.markdown("---")

# Step-by-step explainer, each one an expander so it doesn't overwhelm a first-time viewer
steps = [
    ("L0 — Pre-Gate (< 25ms)", "Every prompt is scanned for PII (credit cards via Luhn checksum, emails, phone numbers) and prompt-injection markers before it goes anywhere near an LLM. This is synchronous — the request cannot proceed until this clears."),
    ("L1 — Semantic Cache + Frugal Cascade", "If a semantically similar question was answered before (measured via embedding cosine similarity), the cached answer returns in ~11ms — no LLM call at all. On a genuine miss, the cheapest capable model tries first; only escalates to a stronger model if its answer looks unreliable."),
    ("L2 — Grounding Gate (RAG use case only)", "For internal-knowledge-assistant traffic, each sentence of the answer is checked against the retrieved source documents using an NLI model, streamed sentence-by-sentence — fabricated claims get flagged before the user finishes reading."),
    ("L3 — Action Gateway (agent use case only)", "For any AI that can take real actions (send email, transfer funds, update a record), every single tool call is checked against a declared Intent Contract before it executes — including catching injected instructions hidden inside a *tool's own return data*, not just the user's prompt."),
    ("L4 — Adaptive Optimization + Audit", "Every decision is written to a SHA-256 hash-chained log — tamper-evident by construction. An offline learning loop continuously re-evaluates whether current thresholds are still optimal."),
]
for title, desc in steps:
    with st.expander(f"**{title}**"):
        st.write(desc)

st.info("👉 Head to **Live Inspector** to run these stages against a real request yourself.")
