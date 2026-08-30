import os
import requests
import sqlite3
import pandas as pd
import json
import streamlit as st

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:8080")
TIMEOUT = 3.0

def health():
    try:
        resp = requests.get(f"{GATEWAY_URL}/docs", timeout=TIMEOUT)
        return resp.status_code == 200
    except requests.RequestException:
        return False

@st.cache_data(ttl=5)
def get_audit_logs():
    try:
        conn = sqlite3.connect("audit.db")
        df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 100", conn)
        return df
    except Exception as e:
        st.error(f"Failed to fetch audit logs: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=5)
def get_calibration():
    try:
        with open("eval/results/l2_calibration.json", "r") as f:
            return json.load(f)
    except Exception:
        return {}

@st.cache_data(ttl=5)
def get_bandit():
    try:
        with open("eval/results/l4_bandit.json", "r") as f:
            return json.load(f)
    except Exception:
        return {}

def post_chat(payload):
    try:
        resp = requests.post(f"{GATEWAY_URL}/v1/chat/completions", json=payload, timeout=30.0)
        return resp
    except Exception as e:
        st.error(f"Gateway connection failed: {e}")
        return None
