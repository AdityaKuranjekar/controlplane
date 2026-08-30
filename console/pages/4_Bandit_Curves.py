import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import math
import os
import requests
from theme import inject_global_css, render_sidebar, render_page_header, section, kpi_card

st.set_page_config(page_title="ControlPlane | Threshold Optimization", layout="wide")
inject_global_css()
render_sidebar(active="4_Bandit_Curves")

# Info ribbon
st.markdown("""
<div style="background:var(--info-bg); border:1px solid var(--info); padding:10px 16px; border-radius:6px; color:var(--info); font-size:13px; font-weight:500; margin-bottom:24px; display:inline-block;">
  <span style="margin-right:8px;">ℹ️</span> Offline replay — not in the live request path
</div>
""", unsafe_allow_html=True)

render_page_header("Threshold Optimization (Bandit)", "Thompson-sampling offline replay to continually optimize the semantic cache cosine threshold (τ).")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8080")

@st.cache_data(ttl=5)
def get_bandit():
    try:
        response = requests.get(f"{GATEWAY_URL}/v1/routing/bandit", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

data = get_bandit()
if data and "error" not in data:
    best_fixed = data.get("best_fixed_arm_in_hindsight", "N/A")
    favored = data.get("bandit_favored_arm", "N/A")
    match = best_fixed == favored
    
    col_k1, col_k2, col_k3 = st.columns([1.2, 1.2, 1.6])
    with col_k1: kpi_card("Best Fixed Arm", best_fixed, "Hindsight ideal")
    with col_k2: kpi_card("Bandit Favored", favored, "Learned dynamically")
    with col_k3:
        pill_color = "var(--success)" if match else "var(--danger)"
        pill_bg = "var(--success-bg)" if match else "var(--danger-bg)"
        pill_border = "var(--success-border)" if match else "var(--danger-border)"
        st.markdown(f"""
        <div class="cp-card" style="display:flex; flex-direction:column; justify-content:center; align-items:center; height:100%;">
            <div style="font-size:13px; color:var(--text-muted); text-transform:uppercase; font-weight:600; margin-bottom:12px;">Convergence Match</div>
            <div style="background:{pill_bg}; color:{pill_color}; border:1px solid {pill_border}; padding:6px 16px; border-radius:20px; font-weight:700; font-size:16px;">
                {'✓ MATCH' if match else '✗ MISMATCH'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_l, col_r = st.columns([6, 4], gap="large")
    
    with col_l:
        section("Cumulative Regret")
        if "regret_curve" in data:
            df_regret = pd.DataFrame(data["regret_curve"])
            line = alt.Chart(df_regret).mark_line(interpolate='step-after', color="var(--accent)", strokeWidth=2).encode(
                x=alt.X("round:Q", title="Round (Request Index)"),
                y=alt.Y("regret:Q", title="Cumulative Regret")
            ).properties(height=280)
            st.altair_chart(line, use_container_width=True)

    with col_r:
        section("Arm Choice Frequency")
        if "final_arm_stats" in data:
            df_stats = pd.DataFrame(data["final_arm_stats"])
            if 'count' not in df_stats.columns and 'alpha' in df_stats.columns:
                # Approximate count from alpha + beta - 2 if not provided explicitly
                df_stats['count'] = df_stats['alpha'] + df_stats['beta'] - 2
            
            bar = alt.Chart(df_stats).mark_bar(color="var(--bg-sunken)").encode(
                y=alt.Y("arm:N", sort="-x", title=None),
                x=alt.X("count:Q", title="Selections"),
                color=alt.condition(
                    alt.datum.arm == favored,
                    alt.value("var(--accent)"),
                    alt.value("var(--border-strong)")
                )
            ).properties(height=280)
            st.altair_chart(bar, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    section("Arm Posteriors: Beta(α, β)")
    
    def beta_pdf(x, a, b):
        if a <= 0 or b <= 0: return np.zeros_like(x)
        # Log Beta function: ln B(a,b) = ln Gamma(a) + ln Gamma(b) - ln Gamma(a+b)
        log_B = math.lgamma(a) + math.lgamma(b) - math.lgamma(a+b)
        # Avoid log(0)
        x_safe = np.clip(x, 1e-10, 1 - 1e-10)
        log_pdf = (a-1)*np.log(x_safe) + (b-1)*np.log(1-x_safe) - log_B
        return np.exp(log_pdf)

    if "final_arm_stats" in data:
        # Sort arms to display consistently
        for arm_data in data["final_arm_stats"]:
            if "arm" not in arm_data:
                arm_data["arm"] = f"tau_{arm_data.get('threshold', 0)}"
        arms = sorted(data["final_arm_stats"], key=lambda k: k["arm"])
        
        # Determine number of columns (up to 4)
        n_cols = min(4, len(arms))
        cols = st.columns(n_cols)
        
        x_vals = np.linspace(0, 1, 100)
        
        for i, arm_data in enumerate(arms[:4]):
            a, b = arm_data.get("alpha", 1), arm_data.get("beta", 1)
            arm_name = arm_data["arm"]
            mean_val = a / (a + b) if (a+b) > 0 else 0
            
            y_vals = beta_pdf(x_vals, a, b)
            df_beta = pd.DataFrame({"x": x_vals, "y": y_vals})
            
            with cols[i]:
                is_fav = arm_name == favored
                area_color = "var(--accent)" if is_fav else "var(--border-strong)"
                
                st.markdown(f"""
                <div style="font-size:13px; font-weight:600; margin-bottom:4px; color:var(--text-primary);">Arm {arm_name}</div>
                <div style="font-size:11px; color:var(--text-muted); margin-bottom:8px;">α={a:.1f}, β={b:.1f}, μ={mean_val:.2f}</div>
                """, unsafe_allow_html=True)
                
                chart = alt.Chart(df_beta).mark_area(opacity=0.6, color=area_color).encode(
                    x=alt.X("x:Q", title=None, axis=alt.Axis(labels=False, ticks=False)),
                    y=alt.Y("y:Q", title=None, axis=alt.Axis(labels=False, ticks=False, grid=False))
                ).properties(height=100)
                st.altair_chart(chart, use_container_width=True)

else:
    st.info("No bandit data available. Ensure the gateway is running and returning data at `/v1/routing/bandit`.")
