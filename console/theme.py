import streamlit as st

def inject_global_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    :root {
        --cp-accent: #A100FF;
        --cp-accent-light: #F5ECFF;
        --cp-black: #111111;
        --cp-gray: #6B6B6B;
        --cp-risk: #D62828;
        --cp-risk-light: #FBEAEA;
        --cp-good: #1a7f37;
    }

    .cp-hero {
        background: linear-gradient(135deg, #111111 0%, #2a0a3d 100%);
        padding: 48px 40px; border-radius: 16px; margin-bottom: 24px;
    }
    .cp-hero h1 { color: white; font-size: 42px; font-weight: 800; margin: 0; }
    .cp-hero p { color: #d0c0e0; font-size: 18px; margin-top: 8px; }

    .cp-card {
        background: #1a1a1a; border: 1px solid #2e2e2e; border-radius: 12px;
        padding: 20px; transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .cp-card:hover { border-color: var(--cp-accent); transform: translateY(-2px); }
    .cp-card h3 { color: white; margin: 0 0 8px 0; font-size: 18px; }
    .cp-card p { color: var(--cp-gray); font-size: 14px; margin: 0; }

    .cp-badge {
        display: inline-block; padding: 6px 14px; border-radius: 20px;
        font-weight: 700; font-size: 13px;
    }
    .cp-status-dot {
        height: 10px; width: 10px; border-radius: 50%;
        display: inline-block; margin-right: 6px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(26,127,55,0.5); }
        70% { box-shadow: 0 0 0 8px rgba(26,127,55,0); }
        100% { box-shadow: 0 0 0 0 rgba(26,127,55,0); }
    }
    </style>
    """, unsafe_allow_html=True)
