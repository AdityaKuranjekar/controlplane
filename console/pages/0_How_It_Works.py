import streamlit as st
import streamlit.components.v1 as components
from theme import inject_global_css, render_top_navbar

st.set_page_config(page_title="How It Works — ControlPlane", page_icon="🔍", layout="wide", initial_sidebar_state="collapsed")
inject_global_css()
render_top_navbar("How_It_Works")

st.markdown("""
<div class="cp-page-title">
  🔍 How Requests Flow Through ControlPlane<span class="cp-cursor"></span>
</div>
<p class="cp-page-desc">
  Live deadline-tiered execution pipeline. Classifies risk by <em>when decisions must happen</em> to minimize latency and guarantee security.
</p>
""", unsafe_allow_html=True)

components.html("""
<div style="background:#0F172A; border-radius:16px; padding:36px 20px; font-family:'Inter',sans-serif; border: 1px solid #1E293B;">
<svg viewBox="0 0 1000 200" style="width:100%; height:auto;">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#64748B"/>
    </marker>
  </defs>

  <!-- connecting line -->
  <line x1="60" y1="100" x2="940" y2="100" stroke="#334155" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- traveling packet -->
  <circle r="8" fill="#38BDF8">
    <animateMotion dur="4s" repeatCount="indefinite" path="M60,100 L940,100" />
    <animate attributeName="fill" values="#38BDF8;#38BDF8;#EF4444;#10B981" dur="4s" repeatCount="indefinite"/>
  </circle>

  <!-- stage boxes -->
  <g font-size="13" font-weight="700" fill="white" text-anchor="middle">
    <rect x="20" y="70" width="130" height="60" rx="10" fill="#1E293B" stroke="#38BDF8" stroke-width="1.5"/>
    <text x="85" y="95" fill="#F8FAFC">L0: Pre-Gate</text><text x="85" y="114" font-size="11" font-weight="400" fill="#94A3B8">PII + Injection</text>

    <rect x="220" y="70" width="130" height="60" rx="10" fill="#1E293B" stroke="#38BDF8" stroke-width="1.5"/>
    <text x="285" y="95" fill="#F8FAFC">L1: Cache</text><text x="285" y="114" font-size="11" font-weight="400" fill="#94A3B8">FAISS + Cascade</text>

    <rect x="420" y="70" width="130" height="60" rx="10" fill="#1E293B" stroke="#38BDF8" stroke-width="1.5"/>
    <text x="485" y="95" fill="#F8FAFC">L2: Grounding</text><text x="485" y="114" font-size="11" font-weight="400" fill="#94A3B8">NLI Verification</text>

    <rect x="620" y="70" width="130" height="60" rx="10" fill="#1E293B" stroke="#38BDF8" stroke-width="1.5"/>
    <text x="685" y="95" fill="#F8FAFC">L3: Action Gate</text><text x="685" y="114" font-size="11" font-weight="400" fill="#94A3B8">Intent Contracts</text>

    <rect x="820" y="70" width="130" height="60" rx="10" fill="#1E293B" stroke="#10B981" stroke-width="1.5"/>
    <text x="885" y="95" fill="#10B981">L4: Audit Log</text><text x="885" y="114" font-size="11" font-weight="400" fill="#94A3B8">SHA-256 Chain</text>
  </g>
</svg>
<p style="color:#94A3B8; text-align:center; margin-top:12px; font-size:13px;">
  The traveling packet flashes red when an edge security violation is detected, immediately short-circuiting with &lt;1ms latency.
</p>
</div>
""", height=220, scrolling=False)

st.markdown("<br>", unsafe_allow_html=True)

steps = [
    ("Stage 1: Block-Before-Send (< 15ms)", "Every prompt is scanned for PII (credit cards via Luhn checksum, SSN, emails, phone numbers) and prompt-injection markers before touching any LLM. Violations trigger an immediate edge BLOCK without incurring model latency."),
    ("Stage 2: Decide-Before-Inference (< 25ms)", "Compound SHA-256 semantic cache lookup (11.4ms). On MISS, cascades from Tier 0 (gpt-oss-20b) to Tier 1 on refusal."),
    ("Stage 3: Verify-In-Stream / After-Delivery (Async)", "Sentence-level ONNX NLI grounding verification against RAG source context chunks. Validates tool intent contracts for autonomous agent executions."),
    ("Stage 4: Continuous Governance & Cryptographic Audit", "Appends SHA256(prev_hash + payload) to tamper-evident audit ledger and updates Thompson-sampling bandit cache thresholds."),
]

for title, desc in steps:
    with st.expander(f"**{title}**", expanded=True):
        st.write(desc)
