import streamlit as st

def inject_global_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Hide all Streamlit default chrome & clutter */
    header[data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }

    /* Single clean scrollbar */
    html, body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #FFFFFF !important;
        color: #111827 !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stAppViewContainer"], section.main {
        overflow-x: hidden !important;
        overflow-y: visible !important;
        background-color: #FFFFFF !important;
    }

    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 3rem !important;
        max-width: 1080px !important;
        margin: 0 auto !important;
    }

    iframe {
        border: none !important;
        overflow: hidden !important;
        width: 100% !important;
    }

    /* Top Google Antigravity Navigation Bar */
    .cp-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 0;
        border-bottom: 1px solid #E5E7EB;
        background: #FFFFFF;
        position: sticky;
        top: 0;
        z-index: 999;
        margin-bottom: 28px;
    }

    .cp-brand {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 19px;
        font-weight: 700;
        color: #111827 !important;
        text-decoration: none;
        letter-spacing: -0.02em;
        cursor: pointer;
    }

    .cp-brand-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        background: #111827;
        color: #FFFFFF;
        border-radius: 6px;
        font-size: 14px;
    }

    .cp-nav-links {
        display: flex;
        align-items: center;
        gap: 24px;
        list-style: none;
        margin: 0;
        padding: 0;
    }

    .cp-nav-item {
        position: relative;
        display: inline-block;
    }

    .cp-nav-link {
        color: #4B5563 !important;
        font-size: 14px;
        font-weight: 500;
        text-decoration: none;
        padding: 8px 4px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 4px;
        transition: color 0.15s ease;
    }

    .cp-nav-link:hover {
        color: #111827 !important;
    }

    .cp-dropdown-menu {
        display: none;
        position: absolute;
        top: 100%;
        left: -10px;
        background-color: #FFFFFF;
        min-width: 240px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04);
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 8px;
        z-index: 1000;
    }

    .cp-nav-item:hover .cp-dropdown-menu {
        display: block;
    }

    .cp-dropdown-item {
        color: #374151 !important;
        padding: 9px 14px;
        text-decoration: none;
        display: block;
        font-size: 13.5px;
        font-weight: 500;
        border-radius: 8px;
        transition: background-color 0.15s ease, color 0.15s ease;
    }

    .cp-dropdown-item:hover {
        background-color: #F3F4F6;
        color: #111827 !important;
    }

    .cp-nav-right {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .cp-status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        background: #ECFDF5;
        color: #065F46;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        border: 1px solid #A7F3D0;
    }

    .cp-status-dot {
        width: 7px;
        height: 7px;
        background-color: #10B981;
        border-radius: 50%;
    }

    .cp-btn-nav {
        background: #111827;
        color: #FFFFFF !important;
        padding: 8px 18px;
        border-radius: 9999px;
        font-size: 13.5px;
        font-weight: 600;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: opacity 0.15s ease;
    }

    .cp-btn-nav:hover {
        opacity: 0.9;
    }

    /* Google Antigravity Headings & Typography */
    .cp-page-title {
        font-size: 38px;
        font-weight: 800;
        color: #111827;
        letter-spacing: -0.03em;
        margin: 0 0 8px 0;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    .cp-cursor {
        display: inline-block;
        width: 3.5px;
        height: 34px;
        background-color: #38BDF8;
        margin-left: 4px;
        border-radius: 2px;
        animation: blink 1.2s infinite;
    }

    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }

    .cp-page-desc {
        color: #4B5563;
        font-size: 15.5px;
        line-height: 1.6;
        margin-bottom: 28px;
    }

    /* Cards & Containers */
    .cp-box {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }

    .cp-card-title {
        font-size: 17px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 8px;
    }

    /* Pill Buttons */
    .stButton > button {
        background: #111827 !important;
        color: #FFFFFF !important;
        border-radius: 9999px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        border: none !important;
        transition: opacity 0.15s ease, transform 0.15s ease !important;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
        transform: translateY(-1px) !important;
    }

    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #111827 !important;
        letter-spacing: -0.02em !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #6B7280 !important;
    }

    /* Dataframe Clean Styling */
    [data-testid="stDataFrame"] {
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_top_navbar(active_page=""):
    st.markdown("""
    <div class="cp-navbar">
      <div style="display: flex; align-items: center; gap: 32px;">
        <a href="/" target="_parent" class="cp-brand">
          <span class="cp-brand-icon">🛡️</span>
          ControlPlane
        </a>
        <ul class="cp-nav-links">
          <li class="cp-nav-item">
            <a class="cp-nav-link">Risk Stages ▾</a>
            <div class="cp-dropdown-menu">
              <a class="cp-dropdown-item" href="/#playground" target="_parent">L0: Pre-Gate (PII & Injection)</a>
              <a class="cp-dropdown-item" href="/#playground" target="_parent">L1: Semantic Cache & Cascade</a>
              <a class="cp-dropdown-item" href="/#playground" target="_parent">L2: NLI Grounding Gate</a>
              <a class="cp-dropdown-item" href="/How_It_Works" target="_parent">L3: Agent Intent Contracts</a>
              <a class="cp-dropdown-item" href="/Audit_Explorer" target="_parent">L4: Hash-Chained Audit Ledger</a>
            </div>
          </li>
          <li class="cp-nav-item">
            <a class="cp-nav-link">Governance Tools ▾</a>
            <div class="cp-dropdown-menu">
              <a class="cp-dropdown-item" href="/#playground" target="_parent">Live Request Playground</a>
              <a class="cp-dropdown-item" href="/Audit_Explorer" target="_parent">Cryptographic Audit Explorer</a>
              <a class="cp-dropdown-item" href="/Grounding_Calibration" target="_parent">Grounding Calibration</a>
              <a class="cp-dropdown-item" href="/Bandit_Curves" target="_parent">Bandit Cost Model</a>
              <a class="cp-dropdown-item" href="/Production_Scale" target="_parent">Production Scale Roadmap</a>
            </div>
          </li>
          <li class="cp-nav-item">
            <a class="cp-nav-link" href="/How_It_Works" target="_parent">How It Works</a>
          </li>
          <li class="cp-nav-item">
            <a class="cp-nav-link" href="/#benchmarks" target="_parent">Benchmarks</a>
          </li>
          <li class="cp-nav-item">
            <a class="cp-nav-link">Resources ▾</a>
            <div class="cp-dropdown-menu">
              <a class="cp-dropdown-item" href="http://localhost:8080/docs" target="_blank">FastAPI OpenAPI Swagger ↗</a>
              <a class="cp-dropdown-item" href="https://github.com/antrikshagalaxy/controlplane" target="_blank">GitHub Repository ↗</a>
            </div>
          </li>
        </ul>
      </div>
      <div class="cp-nav-right">
        <div class="cp-status-pill">
          <span class="cp-status-dot"></span> Gateway Active (8080)
        </div>
        <a href="/#playground" target="_parent" class="cp-btn-nav">Test Gateway ⚡</a>
      </div>
    </div>
    """, unsafe_allow_html=True)
