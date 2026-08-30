import streamlit as st

def inject_global_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
    }

    :root {
        --bg-app: #FFFFFF;
        --bg-canvas: #F7F8FA;
        --bg-sunken: #F1F3F5;
        --surface: #FFFFFF;
        --border: #E6E8EB;
        --border-strong: #D0D5DD;
        --text-primary: #1A1D21;
        --text-secondary: #5C636E;
        --text-muted: #8A929E;
        --accent: #6C2BD9;
        --accent-hover: #5A21B6;
        --accent-tint: #F4F0FE;
        --success: #067647;
        --success-bg: #ECFDF3;
        --success-border: #ABEFC6;
        --warning: #B54708;
        --warning-bg: #FFFAEB;
        --danger: #B42318;
        --danger-bg: #FEF3F2;
        --danger-border: #FECDCA;
        --info: #175CD3;
        --info-bg: #EFF8FF;
        --shadow-sm: 0 1px 2px rgba(16,24,40,.06);
        --shadow-md: 0 4px 12px rgba(16,24,40,.08);
        --radius: 10px;
    }

    /* Hide Streamlit Chrome */
    #MainMenu {visibility: hidden;}
    header .css-1siy2j7, header [data-testid="stHeader"] {display: none;}
    footer {visibility: hidden;}
    .block-container { padding-top: 2.5rem; max-width: 1200px; margin: 0 auto; }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--bg-canvas) !important;
        border-right: 1px solid var(--border);
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        letter-spacing: -0.011em;
        line-height: 1.25;
        color: var(--text-primary);
    }
    p, span, div {
        line-height: 1.5;
        color: var(--text-secondary);
    }
    .cp-mono {
        font-family: 'IBM Plex Mono', 'ui-monospace', monospace !important;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        transition: opacity 0.15s ease-out;
    }
    .stButton>button[kind="primary"] {
        background-color: var(--accent) !important;
        color: white !important;
        border: none !important;
    }
    .stButton>button[kind="secondary"] {
        background-color: white !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-strong) !important;
    }
    .stButton>button:hover {
        opacity: 0.9;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 20px 24px;
        box-shadow: var(--shadow-sm);
    }
    [data-testid="stMetricValue"] {
        font-family: 'IBM Plex Mono', 'ui-monospace', monospace !important;
        color: var(--text-primary) !important;
        font-size: 30px !important;
    }
    
    /* DataFrame header styling */
    [data-testid="stDataFrame"] th {
        background-color: var(--bg-canvas) !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 0;
        color: var(--text-muted);
    }
    .stTabs [aria-selected="true"] {
        border-bottom-color: var(--accent) !important;
        color: var(--accent) !important;
    }

    /* Shared Utility Classes */
    .cp-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 20px 24px;
        box-shadow: var(--shadow-sm);
        margin-bottom: 16px;
    }
    .cp-section-label {
        font-size: 12px;
        text-transform: uppercase;
        color: var(--text-muted);
        font-weight: 600;
        margin-bottom: 12px;
        letter-spacing: 0.05em;
    }
    .cp-chip {
        display: inline-block;
        padding: 2px 6px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
    }
    .cp-chip.allow { background: var(--success-bg); color: var(--success); border: 1px solid var(--success-border); }
    .cp-chip.redact, .cp-chip.flag, .cp-chip.abstain { background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning); }
    .cp-chip.block { background: var(--danger-bg); color: var(--danger); border: 1px solid var(--danger-border); }
    
    .cp-status-dot {
        height: 8px; width: 8px; border-radius: 50%;
        display: inline-block; margin-right: 6px;
        background-color: var(--success);
    }
    .cp-status-dot.unreachable { background-color: var(--danger); }
    
    .cp-warning-callout {
        background-color: var(--warning-bg);
        border: 1px solid var(--warning);
        border-radius: var(--radius);
        padding: 16px 20px;
        color: var(--warning);
    }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar(active=None):
    from lib.gateway import health
    import streamlit as st
    st.sidebar.markdown("<h3 style='margin-bottom:4px;'>ControlPlane</h3>", unsafe_allow_html=True)
    
    is_up = health()
    status_class = "" if is_up else "unreachable"
    status_text = "connected" if is_up else "unreachable"
    st.sidebar.markdown(f"<div style='margin-bottom:24px;'><span class='cp-status-dot {status_class}'></span><span style='font-size:12px; color:var(--text-muted)'>Gateway: {status_text}</span></div>", unsafe_allow_html=True)
    
    pages = {
        "app": ("Home", "app"),
        "0_How_It_Works": ("How It Works", "pages/0_How_It_Works"),
        "1_Live_Inspector": ("Live Inspector", "pages/1_Live_Inspector"),
        "2_Audit_Explorer": ("Audit Explorer", "pages/2_Audit_Explorer"),
        "3_Grounding_Calibration": ("Grounding Calibration", "pages/3_Grounding_Calibration"),
        "4_Bandit_Curves": ("Threshold Optimization", "pages/4_Bandit_Curves"),
        "5_Production_Scale": ("Scaling", "pages/5_Production_Scale")
    }
    
    for key, (title, path) in pages.items():
        if st.sidebar.button(title, key=f"nav_{key}", use_container_width=True, type="primary" if active == key else "secondary"):
            st.switch_page(f"{path}.py")
            
    st.sidebar.markdown("---")
    st.sidebar.caption("Env: Production<br>Build: v1.0", unsafe_allow_html=True)

def render_page_header(title, subtitle, status=None):
    import streamlit as st
    pill_html = f"<div style='float:right;'><span style='background:var(--bg-sunken); border:1px solid var(--border); padding:4px 12px; border-radius:12px; font-size:12px; color:var(--text-secondary); font-weight:500;'>{status}</span></div>" if status else ""
    st.markdown(f"{pill_html}<h2 style='margin-bottom:4px;'>{title}</h2><p style='color:var(--text-secondary); margin-bottom:32px;'>{subtitle}</p>", unsafe_allow_html=True)

def kpi_card(label, value, sub=None, tone="neutral"):
    import streamlit as st
    tone_color = "var(--border)"
    if tone == "success": tone_color = "var(--success)"
    elif tone == "warning": tone_color = "var(--warning)"
    elif tone == "danger": tone_color = "var(--danger)"
    
    sub_html = f"<div style='font-size:12px; color:var(--text-muted); margin-top:4px;'>{sub}</div>" if sub else ""
    
    html = f"""
    <div class="cp-card" style="border-top: 3px solid {tone_color}; padding: 16px 20px; height:100%;">
        <div style="font-size:13px; color:var(--text-muted); text-transform:uppercase; font-weight:600; margin-bottom:8px; letter-spacing:0.05em;">{label}</div>
        <div class="cp-mono" style="font-size:30px; color:var(--text-primary); line-height:1; font-weight:500;">{value}</div>
        {sub_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def state_badge(action):
    action_lower = str(action).lower()
    return f"<span class='cp-chip {action_lower}'>{str(action).upper()}</span>"

def section(label):
    import streamlit as st
    st.markdown(f"<div class='cp-section-label'>{label}</div>", unsafe_allow_html=True)

def altair_theme():
    return {
        "config": {
            "view": {"stroke": "transparent"},
            "axis": {
                "labelColor": "#8A929E",
                "titleColor": "#8A929E",
                "gridColor": "#E6E8EB",
                "gridWidth": 0.5,
                "domainColor": "#E6E8EB",
                "tickColor": "#E6E8EB",
                "labelFont": "Inter",
                "titleFont": "Inter",
                "titleFontWeight": 500
            },
            "title": {"color": "#1A1D21", "subtitleColor": "#5C636E", "font": "Inter"},
            "legend": {"labelColor": "#5C636E", "titleColor": "#1A1D21", "labelFont": "Inter", "titleFont": "Inter"},
            "text": {"font": "Inter"}
        }
    }

import altair as alt
alt.themes.register("controlplane", altair_theme)
alt.themes.enable("controlplane")
