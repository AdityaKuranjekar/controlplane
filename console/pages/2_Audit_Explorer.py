import streamlit as st
import pandas as pd
import hashlib
import json
import os
import requests
from console.theme import inject_global_css, render_sidebar, render_page_header, section, state_badge

st.set_page_config(page_title="ControlPlane | Audit Explorer", layout="wide")
inject_global_css()
render_sidebar(active="2_Audit_Explorer")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8080")

@st.cache_data(ttl=5)
def load_data():
    try:
        response = requests.get(f"{GATEWAY_URL}/v1/audit/logs", timeout=5)
        if response.status_code == 200:
            data = response.json().get("logs", [])
            return pd.DataFrame(data)
        else:
            st.error(f"Failed to fetch audit logs: {response.text}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to connect to gateway: {e}")
        return pd.DataFrame()

def _canonical(payload: dict) -> str:
    return json.dumps(payload, separators=(',', ':'), sort_keys=True)

def verify_chain(df: pd.DataFrame):
    if df.empty: return True, None
    for i in range(len(df)):
        row = df.iloc[i]
        payload = {
            "profile": row["profile"],
            "prompt_redacted": row["prompt_redacted"],
            "action": row["action"],
            "reason": row["reason"],
            "risk_vector": json.loads(row["risk_vector"]) if isinstance(row["risk_vector"], str) else row["risk_vector"],
            "latency_ms": json.loads(row["latency_ms"]) if isinstance(row["latency_ms"], str) else row["latency_ms"],
            "prev_hash": row["prev_hash"]
        }
        computed_hash = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
        if computed_hash != row["row_hash"]:
            return False, row["id"]
        if i > 0:
            prev_row = df.iloc[i-1]
            # Since df is usually ordered by timestamp descending, index i-1 is newer, index i is older
            # Wait, chain.py usually writes them sequentially. Let's assume order is ascending for validation
            # Actually, the original script does: `row["prev_hash"] != prev_row["row_hash"]` 
            # so it assumes index 0 is oldest, index 1 is next. 
            if row["prev_hash"] != prev_row["row_hash"]:
                return False, row["id"]
    return True, None

df = load_data()

# Compute chain status on load
if not df.empty:
    valid, broken_at = verify_chain(df.sort_values(by="id").reset_index(drop=True))
    if valid:
        status_pill = f"✓ verified ({len(df)} rows)"
    else:
        status_pill = f"✗ broken at row {broken_at}"
else:
    status_pill = "No data"

render_page_header("Audit Explorer", "Verify the cryptographic hash chain.", status=status_pill)

if not df.empty:
    # Toolbar
    col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns([2, 2, 2, 2, 2])
    profiles = ["All"] + df['profile'].unique().tolist()
    actions = ["All"] + df['action'].unique().tolist()
    
    with col_t1: filter_prof = st.selectbox("Profile", profiles)
    with col_t2: filter_act = st.selectbox("Action", actions)
    with col_t3:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        if st.button("Re-verify Chain", use_container_width=True):
            st.rerun()
    with col_t4:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Export CSV", csv, "audit_log.csv", "text/csv", use_container_width=True)
    with col_t5:
        st.markdown("<div style='height:36px;'></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:right; font-size:13px; color:var(--text-muted);'>Showing {len(df)} rows</div>", unsafe_allow_html=True)

    # Filter df
    disp_df = df.copy()
    if filter_prof != "All": disp_df = disp_df[disp_df['profile'] == filter_prof]
    if filter_act != "All": disp_df = disp_df[disp_df['action'] == filter_act]
    
    # Sorting for display (newest first)
    disp_df = disp_df.sort_values("timestamp", ascending=False)

    section("Hash Chain")
    # Horizontal hash-chain visualization strip (small linked blocks)
    # Take latest 10 rows for visualizer
    chain_vis_df = disp_df.head(10).sort_values("id")
    chain_html = "<div style='display:flex; align-items:center; overflow-x:auto; padding-bottom:16px;'>"
    for i, (_, row) in enumerate(chain_vis_df.iterrows()):
        h = row['row_hash'][:8]
        is_valid = broken_at != row['id']
        border_color = "var(--success)" if is_valid else "var(--danger)"
        bg_color = "var(--success-bg)" if is_valid else "var(--danger-bg)"
        
        chain_html += f"<div class='cp-mono' style='background:{bg_color}; color:{border_color}; border:1px solid {border_color}; padding:4px 8px; border-radius:4px; font-size:12px;'>{h}</div>"
        if i < len(chain_vis_df) - 1:
            chain_html += f"<div style='color:{border_color}; margin:0 4px;'>→</div>"
    chain_html += "</div>"
    st.markdown(chain_html, unsafe_allow_html=True)
    
    section("Audit Records")
    
    st.dataframe(disp_df, use_container_width=True, hide_index=True, column_config={
        "id": st.column_config.NumberColumn("ID"),
        "timestamp": st.column_config.TextColumn("Time"),
        "profile": st.column_config.TextColumn("Profile"),
        "action": st.column_config.TextColumn("Action"),
        "prompt_redacted": st.column_config.TextColumn("Prompt (Redacted)"),
        "reason": st.column_config.TextColumn("Reason"),
        "row_hash": st.column_config.TextColumn("Row Hash"),
        "prev_hash": st.column_config.TextColumn("Prev Hash"),
        "risk_vector": st.column_config.TextColumn("Risk Vector"),
        "latency_ms": st.column_config.TextColumn("Latency (ms)")
    })

    section("Row Verification Detail")
    inspect_id = st.selectbox("Select Row ID to inspect", disp_df['id'].tolist())
    if inspect_id:
        row = df[df['id'] == inspect_id].iloc[0]
        payload = {
            "profile": row["profile"],
            "prompt_redacted": row["prompt_redacted"],
            "action": row["action"],
            "reason": row["reason"],
            "risk_vector": json.loads(row["risk_vector"]) if isinstance(row["risk_vector"], str) else row["risk_vector"],
            "latency_ms": json.loads(row["latency_ms"]) if isinstance(row["latency_ms"], str) else row["latency_ms"],
            "prev_hash": row["prev_hash"]
        }
        canonical_str = _canonical(payload)
        computed_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown("#### Canonical JSON")
            st.code(json.dumps(payload, indent=2), language="json")
        with col_d2:
            st.markdown("#### Hash Computation")
            st.markdown(f"**Expected (from DB):**<br><span class='cp-mono' style='font-size:12px;'>{row['row_hash']}</span>", unsafe_allow_html=True)
            st.markdown(f"**Computed (live):**<br><span class='cp-mono' style='font-size:12px; color:var(--{'success' if computed_hash == row['row_hash'] else 'danger'});'>{computed_hash}</span>", unsafe_allow_html=True)
            if computed_hash == row['row_hash']:
                st.markdown(state_badge("MATCH"), unsafe_allow_html=True)
            else:
                st.markdown(state_badge("MISMATCH"), unsafe_allow_html=True)

else:
    st.warning("No data found in audit.db")
