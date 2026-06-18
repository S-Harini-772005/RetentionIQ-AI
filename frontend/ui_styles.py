import streamlit as st

def load_styles():
    st.markdown("""
    <style>
    /* 1. ENTERPRISE TYPOGRAPHY & RESET */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0B132B;
        color: #FFFFFF;
    }

    /* 2. MAIN TITLE (42px Extra Bold) */
    .main-title {
        font-size: 42px;
        font-weight: 900;
        color: #FFFFFF;
        letter-spacing: -1.5px;
        margin-bottom: 30px;
        background: -webkit-linear-gradient(#FFFFFF, #60A5FA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 3. SECTION HEADERS (28px Bold) */
    .section-header {
        font-size: 28px;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    /* 4. SIDEBAR REDESIGN (#111827) */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    .sidebar-logo {
        font-size: 26px;
        font-weight: 900;
        color: #2563EB;
        padding-bottom: 20px;
        text-align: left;
    }

    /* Sidebar Radio Highlights */
    div[data-testid="stSidebarUserContent"] label[data-baseweb="radio"] {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #60A5FA !important;
        padding: 12px 20px !important;
        border-radius: 12px;
        transition: all 0.3s ease;
    }

    div[data-testid="stSidebarUserContent"] label[data-baseweb="radio"]:hover {
        background-color: rgba(37, 99, 235, 0.1) !important;
    }

    div[data-testid="stSidebarUserContent"] label[data-baseweb="radio"]:has(input:checked) {
        background: linear-gradient(90deg, #2563EB, #1E40AF) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4);
    }

    /* 5. INPUT COMPONENT FIX (White background, Black text) */
    /* Forces typed text to be visible and prominent */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
        border: 2px solid #2563EB !important;
    }
    
    input, select, textarea {
        color: #000000 !important;
        font-weight: 700 !important;
        background-color: #FFFFFF !important;
    }

    /* 6. PREMIUM KPI CARDS (Glassmorphism + Gradients) */
    .kpi-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(37, 99, 235, 0.2);
        border-color: #2563EB;
    }

    .kpi-label {
        color: #94A3B8;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    .kpi-value {
        color: #FFFFFF;
        font-size: 32px;
        font-weight: 900;
        margin-top: 10px;
    }

    /* 7. SYSTEM HEALTH BADGES */
    .status-badge {
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 12px;
    }
    .status-up { background-color: #064e3b; color: #34d399; border: 1px solid #059669; }
    .status-down { background-color: #7f1d1d; color: #fca5a5; border: 1px solid #dc2626; }

    </style>
    """, unsafe_allow_html=True)

def render_kpi(label, value, color_top="#2563EB"):
    """Renders a Deluxe KPI Card with gradient top border."""
    st.markdown(f"""
        <div class="kpi-card" style="border-top: 5px solid {color_top};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)