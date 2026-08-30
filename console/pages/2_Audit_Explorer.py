import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import json

st.set_page_config(page_title="Audit Explorer", layout="wide")

st.title("Audit Explorer")
st.markdown("Inspect `audit.db` logs and manually verify the SHA-256 hash chain.")

DB_PATH = "audit.db"

def load_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY id ASC", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Failed to load DB: {e}")
        return pd.DataFrame()

def _canonical(payload: dict) -> str:
    return json.dumps(payload, separators=(',', ':'), sort_keys=True)

df = load_data()

if not df.empty:
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

    if st.button("Verify Hash Chain"):
        st.markdown("### Hash Chain Verification")
        valid = True
        broken_at = None
        
        # We must re-compute hashes exactly as chain.py does
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
            st.success(f"Hash chain verified successfully for all {len(df)} rows!")
else:
    st.warning("No data found in audit.db")
