import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Bandit Optimization Curves", layout="wide")

st.title("Bandit Optimization Curves")
st.markdown("""
**NOTE: Offline Replay Constraint**
The Thompson-sampling bandit (L4) for the cache threshold is configured as an **offline-replay mechanism** against an evaluation stream, not a live-wired production router.
""")

RESULTS_PATH = "eval/results/l4_bandit_metrics.json"

if os.path.exists(RESULTS_PATH):
    with open(RESULTS_PATH, "r") as f:
        data = json.load(f)
        
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
    st.warning(f"No data found at {RESULTS_PATH}. Run `suite_4_bandit.py` first.")
