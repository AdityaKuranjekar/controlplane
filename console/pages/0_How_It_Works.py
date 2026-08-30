import streamlit as st
import streamlit.components.v1 as components
from theme import inject_global_css, render_sidebar, render_page_header, section, state_badge

st.set_page_config(page_title="ControlPlane | How It Works", page_icon="🔍", layout="wide")
inject_global_css()
render_sidebar(active="0_How_It_Works")

render_page_header("How a Request Actually Flows", "This is a live animation of the real architecture — not a mockup. Every stage shown here maps to real code you can inspect in the repo.")

svg_content = """
<svg viewBox="0 0 1160 620" style="width:100%; height:auto; background:transparent;" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#98A2B3"/>
    </marker>
    <marker id="arrow-danger" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#B42318"/>
    </marker>
  </defs>

  <rect x="180" y="20" width="960" height="120" fill="#FEF3F2" fill-opacity="0.22" rx="4"/>
  <text x="20" y="60" font-family="Inter" font-weight="600" font-size="13" fill="#1A1D21">Block-before-send</text>
  <text x="20" y="80" font-family="Inter" font-size="11" fill="#5C636E">&lt; 25 ms sync</text>

  <rect x="180" y="160" width="960" height="140" fill="#EFF8FF" fill-opacity="0.22" rx="4"/>
  <text x="20" y="210" font-family="Inter" font-weight="600" font-size="13" fill="#1A1D21">Decide-before-inference</text>
  <text x="20" y="230" font-family="Inter" font-size="11" fill="#5C636E">~ 15 ms sync</text>

  <rect x="180" y="320" width="960" height="140" fill="#ECFDF3" fill-opacity="0.22" rx="4"/>
  <text x="20" y="370" font-family="Inter" font-weight="600" font-size="13" fill="#1A1D21">Verify-after-generation</text>
  <text x="20" y="390" font-family="Inter" font-size="11" fill="#5C636E">&lt; 200 ms async</text>

  <rect x="180" y="480" width="960" height="120" fill="#F7F8FA" fill-opacity="1" rx="4"/>
  <text x="20" y="530" font-family="Inter" font-weight="600" font-size="13" fill="#1A1D21">Audit &amp; Optimization</text>
  <text x="20" y="550" font-family="Inter" font-size="11" fill="#5C636E">Offline</text>

  <rect x="200" y="40" width="120" height="30" rx="4" fill="#FFF" stroke="#D0D5DD" stroke-width="1"/>
  <text x="260" y="59" font-family="Inter" font-size="11" fill="#1A1D21" text-anchor="middle">Customer bot (100ms)</text>
  
  <rect x="200" y="75" width="120" height="30" rx="4" fill="#FFF" stroke="#D0D5DD" stroke-width="1"/>
  <text x="260" y="94" font-family="Inter" font-size="11" fill="#1A1D21" text-anchor="middle">Internal RAG (1.5s)</text>

  <rect x="200" y="110" width="120" height="30" rx="4" fill="#FFF" stroke="#D0D5DD" stroke-width="1"/>
  <text x="260" y="129" font-family="Inter" font-size="11" fill="#1A1D21" text-anchor="middle">Decision agent (3s)</text>

  <rect x="360" y="65" width="140" height="50" rx="8" fill="#FFF" stroke="#D0D5DD" stroke-width="1"/>
  <text x="430" y="90" font-family="Inter" font-weight="600" font-size="12" fill="#1A1D21" text-anchor="middle">Gateway API</text>
  <text x="430" y="105" font-family="Inter" font-size="10" fill="#5C636E" text-anchor="middle">/v1/chat/completions</text>

  <path d="M 320 55 L 340 55 L 340 90 L 360 90" fill="none" stroke="#98A2B3" stroke-width="1.5" marker-end="url(#arrow)"/>
  <path d="M 320 90 L 360 90" fill="none" stroke="#98A2B3" stroke-width="1.5" marker-end="url(#arrow)"/>
  <path d="M 320 125 L 340 125 L 340 90 L 360 90" fill="none" stroke="#98A2B3" stroke-width="1.5" marker-end="url(#arrow)"/>

  <rect x="540" y="65" width="140" height="50" rx="8" fill="#FFF" stroke="#B42318" stroke-width="2"/>
  <text x="610" y="85" font-family="Inter" font-weight="600" font-size="12" fill="#1A1D21" text-anchor="middle">PII tokenizer</text>
  <text x="610" y="100" font-family="Inter" font-size="10" fill="#5C636E" text-anchor="middle">regex + Luhn</text>

  <rect x="710" y="65" width="140" height="50" rx="8" fill="#FFF" stroke="#B42318" stroke-width="2"/>
  <text x="780" y="85" font-family="Inter" font-weight="600" font-size="12" fill="#1A1D21" text-anchor="middle">Injection scan</text>
  <text x="780" y="100" font-family="Inter" font-size="10" fill="#5C636E" text-anchor="middle">prompt defenses</text>

  <rect x="880" y="55" width="140" height="70" rx="8" fill="#FFF" stroke="#B54708" stroke-width="2"/>
  <text x="950" y="75" font-family="Inter" font-weight="600" font-size="12" fill="#1A1D21" text-anchor="middle">Policy resolver</text>
  <text x="950" y="90" font-family="Inter" font-size="10" fill="#5C636E" text-anchor="middle">RiskVector output</text>
  <text x="950" y="115" font-family="Inter" font-weight="700" font-size="10" fill="#067647" text-anchor="middle">ALLOW</text>

  <line x1="500" y1="90" x2="540" y2="90" stroke="#98A2B3" stroke-width="1.5" marker-end="url(#arrow)"/>
  <line x1="680" y1="90" x2="710" y2="90" stroke="#98A2B3" stroke-width="1.5" marker-end="url(#arrow)"/>
  <line x1="850" y1="90" x2="880" y2="90" stroke="#98A2B3" stroke-width="1.5" marker-end="url(#arrow)"/>

  <line x1="950" y1="55" x2="950" y2="35" stroke="#B42318" stroke-width="1.5" marker-end="url(#arrow-danger)"/>
  <rect x="910" y="20" width="80" height="15" fill="#FEF3F2" stroke="#FECDCA"/>
  <text x="950" y="31" font-family="Inter" font-weight="600" font-size="10" fill="#B42318" text-anchor="middle">[BLOCKED]</text>

  <line x1="950" y1="125" x2="950" y2="185" stroke="#98A2B3" stroke-width="1.5" marker-end="url(#arrow)"/>

  <rect x="880" y="185" width="140" height="50" rx="8" fill="#FFF" stroke="#D0D5DD" stroke-width="1"/>
  <text x="950" y="205" font-family="Inter" font-weight="600" font-size="12" fill="#1A1D21" text-anchor="middle">Semantic cache</text>
  <text x="950" y="220" font-family="Inter" font-size="10" fill="#5C636E" text-anchor="middle">embedding match</text>

  <line x1="880" y1="210" x2="800" y2="210" stroke="#98A2B3" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="840" y="205" font-family="Inter" font-size="10" fill="#B54708" text-anchor="middle">MISS</text>

  <rect x="660" y="185" width="140" height="50" rx="8" fill="#FFF" stroke="#D0D5DD" stroke-width="1"/>
  <text x="730" y="205" font-family="Inter" font-weight="600" font-size="12" fill="#1A1D21" text-anchor="middle">Frugal cascade</text>
  <text x="730" y="220" font-family="Inter" font-size="10" fill="#5C636E" text-anchor="middle">gpt-oss-20b (tier0)</text>

  <line x1="660" y1="210" x2="580" y2="210" stroke="#98A2B3" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="620" y="205" font-family="Inter" font-size="10" fill="#B54708" text-anchor="middle">rel &lt; 0.75</text>

  <rect x="440" y="185" width="140" height="50" rx="8" fill="#FFF" stroke="#D0D5DD" stroke-width="1"/>
  <text x="510" y="205" font-family="Inter" font-weight="600" font-size="12" fill="#1A1D21" text-anchor="middle">Escalation</text>
  <text x="510" y="220" font-family="Inter" font-size="10" fill="#5C636E" text-anchor="middle">gpt-oss-120b (tier1)</text>

  <path d="M 1020 210 Q 1100 210 1100 280 L 1100 600" fill="none" stroke="#067647" stroke-width="1.5" stroke-dasharray="4" marker-end="url(#arrow)"/>
  <text x="1060" y="230" font-family="Inter" font-size="10" fill="#067647">HIT ~11ms</text>

  <line x1="510" y1="235" x2="510" y2="340" stroke="#98A2B3" stroke-width="1.5" marker-end="url(#arrow)"/>
  <line x1="730" y1="235" x2="730" y2="340" stroke="#98A2B3" stroke-width="1.5" marker-end="url(#arrow)"/>

  <rect x="660" y="340" width="140" height="50" rx="8" fill="#FFF" stroke="#B54708" stroke-width="2"/>
  <text x="730" y="360" font-family="Inter" font-weight="600" font-size="12" fill="#1A1D21" text-anchor="middle">Streaming segmenter</text>
  <text x="730" y="375" font-family="Inter" font-size="10" fill="#5C636E" text-anchor="middle">OPEN→COMMITTED</text>

  <line x1="730" y1="390" x2="730" y2="410" stroke="#98A2B3" stroke-width="1.5" marker-end="url(#arrow)"/>
  <rect x="660" y="410" width="140" height="40" rx="8" fill="#FFF" stroke="#B54708" stroke-width="2"/>
  <text x="730" y="428" font-family="Inter" font-weight="600" font-size="12" fill="#1A1D21" text-anchor="middle">Conformal threshold λ</text>

  <rect x="440" y="340" width="140" height="50" rx="8" fill="#FFF" stroke="#B42318" stroke-width="2"/>
  <text x="510" y="360" font-family="Inter" font-weight="600" font-size="12" fill="#1A1D21" text-anchor="middle">Action Gateway</text>
  <text x="510" y="375" font-family="Inter" font-size="10" fill="#5C636E" text-anchor="middle">7 security checks</text>

  <line x1="510" y1="390" x2="510" y2="410" stroke="#98A2B3" stroke-width="1.5" marker-end="url(#arrow)"/>
  <rect x="440" y="410" width="140" height="40" rx="8" fill="#FFF" stroke="#B54708" stroke-width="2"/>
  <text x="510" y="428" font-family="Inter" font-weight="600" font-size="12" fill="#1A1D21" text-anchor="middle">Sandbox tools (no-op)</text>

  <line x1="510" y1="450" x2="510" y2="520" stroke="#98A2B3" stroke-width="1.5" stroke-dasharray="4" marker-end="url(#arrow)"/>
  <line x1="730" y1="450" x2="730" y2="520" stroke="#98A2B3" stroke-width="1.5" stroke-dasharray="4" marker-end="url(#arrow)"/>
  <line x1="950" y1="125" x2="950" y2="520" stroke="#98A2B3" stroke-width="1.5" stroke-dasharray="4" marker-end="url(#arrow)"/>

  <rect x="440" y="520" width="550" height="60" rx="8" fill="#FFF" stroke="#D0D5DD" stroke-width="1"/>
  <text x="715" y="545" font-family="Inter" font-weight="600" font-size="14" fill="#1A1D21" text-anchor="middle">Hash-chained audit log</text>
  <text x="715" y="565" font-family="Inter" font-size="12" fill="#5C636E" text-anchor="middle">SHA-256(row + prev_hash)</text>

  <rect x="1010" y="520" width="120" height="60" rx="8" fill="#FFF" stroke="#D0D5DD" stroke-width="1" stroke-dasharray="4"/>
  <text x="1070" y="545" font-family="Inter" font-weight="600" font-size="12" fill="#1A1D21" text-anchor="middle">Calibration &amp; Bandit</text>
  <text x="1070" y="565" font-family="Inter" font-size="10" fill="#5C636E" text-anchor="middle">Offline replay</text>
  
  <path d="M 1010 550 L 990 550" fill="none" stroke="#98A2B3" stroke-width="1.5" stroke-dasharray="4" marker-end="url(#arrow)"/>

  <!-- Legend -->
  <rect x="200" y="585" width="12" height="12" fill="none" stroke="#D0D5DD" stroke-width="1"/>
  <text x="216" y="595" font-family="Inter" font-size="11" fill="#5C636E">Neutral</text>

  <rect x="270" y="585" width="12" height="12" fill="none" stroke="#B54708" stroke-width="2"/>
  <text x="286" y="595" font-family="Inter" font-size="11" fill="#5C636E">Redact/Flag</text>

  <rect x="350" y="585" width="12" height="12" fill="none" stroke="#B42318" stroke-width="2"/>
  <text x="366" y="595" font-family="Inter" font-size="11" fill="#5C636E">Block</text>

  <line x1="420" y1="591" x2="440" y2="591" stroke="#98A2B3" stroke-width="1.5"/>
  <text x="446" y="595" font-family="Inter" font-size="11" fill="#5C636E">Sync path</text>
  
  <line x1="510" y1="591" x2="530" y2="591" stroke="#98A2B3" stroke-width="1.5" stroke-dasharray="4"/>
  <text x="536" y="595" font-family="Inter" font-size="11" fill="#5C636E">Async/Offline</text>
  
  <text x="960" y="595" font-family="Inter" font-size="11" fill="#8A929E">Every box maps to a module in gateway/</text>
  
  <!-- Subtle Dot Animation -->
  <circle r="5" fill="#6C2BD9">
    <animateMotion dur="6s" repeatCount="indefinite" path="M 360 90 L 540 90 L 710 90 L 880 90 L 950 90 L 950 185" keyPoints="0;0.2;0.4;0.6;0.8;1" keyTimes="0;0.2;0.4;0.6;0.8;1" calcMode="linear"/>
  </circle>
</svg>
"""

components.html(f"<div style='background:var(--bg-app);'>{svg_content}</div>", height=560)
st.markdown("<br>", unsafe_allow_html=True)

# Step-by-step explainer as a stepper
section("Module Execution Order")
steps = [
    ("L0", "Pre-Gate", "< 25ms", "Every prompt is scanned for PII and prompt-injection markers before it goes anywhere near an LLM. Synchronous — request cannot proceed until this clears.", "1_Live_Inspector"),
    ("L1", "Semantic Cache + Cascade", "~ 15ms", "If a similar question was answered before, the cached answer returns in ~11ms. On miss, the cheapest capable model tries first, escalating only if unreliable.", "4_Bandit_Curves"),
    ("L2", "Grounding Gate", "< 200ms lag", "For RAG traffic, each sentence is checked against retrieved docs using an NLI model. Fabricated claims get flagged before the user finishes reading.", "3_Grounding_Calibration"),
    ("L3", "Action Gateway", "< 200ms lag", "For agents, every tool call is checked against an Intent Contract before execution — catching injected instructions hidden inside a tool's own return data.", "1_Live_Inspector"),
    ("L4", "Adaptive Optimization", "Batch", "Every decision writes to a SHA-256 hash-chained log. An offline learning loop re-evaluates whether current thresholds are optimal.", "2_Audit_Explorer"),
]

for tag, title, budget, desc, link in steps:
    st.markdown(f"""
    <div style="padding:16px 20px; border:1px solid var(--border); border-radius:8px; margin-bottom:12px; background:var(--surface);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div style="font-weight:600; color:var(--text-primary);"><span style="color:var(--accent); margin-right:8px;">{tag}</span> {title}</div>
            <span class="cp-chip cp-mono" style="background:var(--bg-sunken);">{budget}</span>
        </div>
        <div style="font-size:14px; color:var(--text-secondary); margin-bottom:8px;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
section("Example Request → Decision")

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("#### Incoming Request")
    st.markdown("""
    <div class="cp-card cp-mono" style="background:var(--bg-sunken); font-size:13px; color:var(--text-primary);">
    {
      "model": "controlplane-default",
      "messages": [
        {"role": "user", "content": "My card is 4111111111111111, refund me."}
      ],
      "cp_profile": "customer_bot"
    }
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("#### Gateway Output")
    st.markdown("""
    <div class="cp-card" style="font-size:14px;">
        <div style="margin-bottom:12px;">Decision: {state_badge("REDACT")}</div>
        <div class="cp-mono" style="background:var(--bg-sunken); padding:12px; border-radius:6px; margin-bottom:12px; color:var(--text-secondary);">
        RiskVector: { privacy: 1.0, safety: 0.0, grounding: 0.0, cost: 0.1 }<br>
        Trigger: regex(PII_CC)
        </div>
        <div style="color:var(--text-muted); font-size:12px;">Audit Log Hash: <span class="cp-mono">e3b0c44298fc1c14</span></div>
    </div>
    """.format(state_badge=state_badge), unsafe_allow_html=True)
