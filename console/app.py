import streamlit as st
import requests

@st.cache_resource
def warm_gateway_connection():
    try:
        requests.post("http://localhost:8080/v1/chat/completions",
                       json={"messages": [{"role": "user", "content": "warmup"}],
                             "cp_profile": "customer_bot", "stream": False},
                       timeout=10)
    except Exception:
        pass
    return True

warm_gateway_connection()
st.set_page_config(
    page_title="Control Plane Console",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ LLM Control Plane Console")
st.markdown("""
Welcome to the Control Plane Console.
Select a page from the sidebar to inspect live requests, explore the audit hash-chain, or view bandit optimization curves.
""")
