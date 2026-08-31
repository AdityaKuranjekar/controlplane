import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import json
import os
import requests
from theme import inject_global_css, render_top_navbar

st.set_page_config(page_title="Audit Explorer — ControlPlane", page_icon="📜", layout="wide", initial_sidebar_state="collapsed")
inject_global_css()
render_top_navbar("Audit_Explorer")

st.markdown("""
<div class="cp-page-title">
  📜 Cryptographic Audit Explorer<span class="cp-cursor"></span>
</div>
<p class="cp-page-desc">
  Inspect tamper-evident <code>audit.db</code> logs and verify the continuous SHA-256 cryptographic hash chain.
</p>
""", unsafe_allow_html=True)

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8080")

def load_data():
    try:
        response = requests.get(f"{GATEWAY_URL}/v1/audit/logs")
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

df = load_data()

if not df.empty:
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("Total Chained Records", len(df))
    col_stat2.metric("Latest Hash Status", "🔒 Sealed")
    col_stat3.metric("Storage Engine", "SQLite + SHA-256")

    st.markdown("<br>", unsafe_allow_html=True)

    emojis = {
        "ALLOW": "✅",
        "REDACT": "✂️",
        "FLAG": "🚩",
        "ABSTAIN_NEEDS_HUMAN": "🙋",
        "BLOCK": "🛑",
    }
    display_df = df.copy()
    display_df['action'] = display_df['action'].apply(lambda x: f"{emojis.get(x, '❔')} {x}")
    st.dataframe(display_df, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔒 Verify SHA-256 Hash Chain Integrity"):
        st.markdown("### Verification Result")
        valid = True
        broken_at = None
        
        for i in range(len(df)):
            row = df.iloc[i]
            
            payload = {
                "profile": row["profile"],
                "prompt_redacted": row["prompt_redacted"],
                "action": row["action"],
                "reason": row["reason"],
                "risk_vector": json.loads(row["risk_vector"]),
                "latency_ms": json.loads(row["latency_ms"]),
                "prev_hash": row["prev_hash"]
            }
            
            computed_hash = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
            
            if computed_hash != row["row_hash"]:
                valid = False
                broken_at = row["id"]
                st.error(f"Row {row['id']} hash mismatch!\nExpected: {row['row_hash']}\nComputed: {computed_hash}")
                break
                
            if i > 0:
                prev_row = df.iloc[i-1]
                if row["prev_hash"] != prev_row["row_hash"]:
                    valid = False
                    broken_at = row["id"]
                    st.error(f"Row {row['id']} prev_hash mismatch!\nExpected: {prev_row['row_hash']}\nFound: {row['prev_hash']}")
                    break
        
        if valid:
            st.success(f"✅ Cryptographic Integrity Verified: All {len(df)} hash links in the chain are 100% valid and unbroken!")
else:
    st.info("No audit logs found yet. Send a test query from the home playground to populate the audit ledger.")
