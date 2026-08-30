import streamlit as st
import pandas as pd
import json
import os
from theme import inject_global_css

st.set_page_config(page_title="Bandit Optimization Curves", layout="wide")
inject_global_css()

st.title("Bandit Optimization Curves")
st.markdown("""
**NOTE: Offline Replay Constraint**
The Thompson-sampling bandit (L4) for the cache threshold is configured as an **offline-replay mechanism** against an evaluation stream, not a live-wired production router.
""")

import os
import requests

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")

try:
    response = requests.get(f"{GATEWAY_URL}/v1/routing/bandit")
    if response.status_code == 200:
        data = response.json()
        if "error" in data:
            st.warning(f"No data found on gateway: {data['error']}")
        else:
            st.markdown("### Final State")
            col1, col2 = st.columns(2)
            col1.metric("Best Fixed Arm (Hindsight)", data["best_fixed_arm_in_hindsight"])
            col2.metric("Bandit Favored Arm", data["bandit_favored_arm"])
            
            match_str = "✅ MATCH" if data["best_fixed_arm_in_hindsight"] == data["bandit_favored_arm"] else "❌ NO MATCH"
            st.markdown(f"**Convergence Check:** {match_str} (Stream length limited to {len(data['regret_curve'])} rounds)")

            st.markdown("### Regret Curve")
            df_regret = pd.DataFrame(data["regret_curve"])
            st.line_chart(df_regret, x="round", y="regret")
            
            st.markdown("### Arm Distribution Stats")
            df_stats = pd.DataFrame(data["final_arm_stats"])
            st.dataframe(df_stats, use_container_width=True)
    else:
        st.error(f"Failed to fetch bandit metrics: {response.text}")
except Exception as e:
    st.error(f"Failed to connect to gateway: {e}")
