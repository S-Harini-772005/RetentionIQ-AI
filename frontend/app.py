import streamlit as st
import pandas as pd
import plotly.express as px
from ui_styles import load_styles, render_kpi

# --- INITIALIZATION ---
st.set_page_config(page_title="RetentionIQ AI | Deloitte Digital", layout="wide")
load_styles()

if 'last_prediction' not in st.session_state:
    st.session_state.last_prediction = None

# --- SIDEBAR REDESIGN ---
with st.sidebar:
    st.markdown('<div class="sidebar-logo">RetentionIQ AI</div>', unsafe_allow_html=True)
    
    menu = {
        "📊 Executive Dashboard": "Dashboard",
        "🎯 Churn Prediction": "Prediction",
        "🧠 SHAP Explainability": "SHAP",
        "📋 Retention Playbook": "Playbook",
        "🛡️ System Health": "Health"
    }
    
    selection = st.radio("Navigation", list(menu.keys()), label_visibility="collapsed")
    page = menu[selection]
    
    st.markdown("---")
    if st.button("🚪 System Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- PAGE: EXECUTIVE DASHBOARD ---
if page == "Dashboard":
    st.markdown('<div class="main-title">Executive Overview</div>', unsafe_allow_html=True)
    
    res = st.session_state.last_prediction
    
    # 1. Top KPI Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi("Total Customers", "5,881", "#60A5FA")
    with col2:
        rev_risk = f"${res['revenue_at_risk']:,.0f}" if res else "$0"
        render_kpi("Revenue at Risk", rev_risk, "#EF4444")
    with col3:
        churn_rate = f"{res['churn_probability']*100:.1f}%" if res else "0.0%"
        render_kpi("Predicted Churn", churn_rate, "#F59E0B")
    with col4:
        roi = f"{res['roi']}x" if res else "0.0x"
        render_kpi("Retention ROI", roi, "#22C55E")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Analytics Row
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="section-header">Customer Retention Trend</div>', unsafe_allow_html=True)
        df = pd.DataFrame({'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'], 'Retention': [98, 97, 99, 96, 97]})
        fig = px.line(df, x='Month', y='Retention', markers=True, color_discrete_sequence=['#2563EB'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.markdown('<div class="section-header">Segment Risk</div>', unsafe_allow_html=True)
        df_seg = pd.DataFrame({'Segment': ['Champions', 'At Risk', 'Loyal'], 'Value': [40, 25, 35]})
        fig_pie = px.pie(df_seg, values='Value', names='Segment', hole=0.5, color_discrete_sequence=['#2563EB', '#EF4444', '#60A5FA'])
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- PAGE: CHURN PREDICTION ---
elif page == "Prediction":
    st.markdown('<div class="main-title">Churn Prediction Engine</div>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.markdown('<div class="section-header">Customer Behavioral Input</div>', unsafe_allow_html=True)
        rev = st.number_input("Annual Revenue", value=1000, key="rev")
        ord_count = st.number_input("Total Orders", value=5, key="ord")
        rec = st.slider("Recency (Days)", 0, 365, 45, key="rec")
        freq = st.number_input("Frequency", value=2, key="freq")
        monet = st.number_input("Monetary Value", value=500, key="monet")
        seg = st.selectbox("Segment", ["Champions", "Loyal", "At Risk", "Lost"], key="seg")
        
        if st.button("🚀 Run AI Analysis", use_container_width=True):
            # Simulation of API Call
            st.session_state.last_prediction = {
                "churn_probability": 0.85, "risk_level": "High", "revenue_at_risk": 850,
                "roi": 4.2, "recommended_action": "Personal Outreach", "offer": "20% Discount"
            }
            st.toast("Intelligence Report Generated")

    with col_b:
        if st.session_state.last_prediction:
            st.markdown('<div class="section-header">AI Risk Result</div>', unsafe_allow_html=True)
            res = st.session_state.last_prediction
            st.markdown(f"""
            <div class="kpi-card" style="border-left: 5px solid #EF4444;">
                <h3 style="margin:0; color:#EF4444;">{res['risk_level'].upper()} RISK</h3>
                <p style="font-size:40px; font-weight:900; margin:10px 0;">{res['churn_probability']*100}%</p>
                <p style="color:#94A3B8;">Probability of churn detected by Random Forest model.</p>
            </div>
            """, unsafe_allow_html=True)

# --- PAGE: SHAP EXPLAINABILITY ---
elif page == "SHAP":
    st.markdown('<div class="main-title">Explainable AI (SHAP)</div>', unsafe_allow_html=True)
    if not st.session_state.last_prediction:
        st.markdown("""
        <div style="text-align:center; padding:100px; background:#1E293B; border-radius:20px; border:2px dashed #60A5FA;">
            <h2 style="color:#60A5FA;">🧠 Ready for Analysis</h2>
            <p style="color:#94A3B8;">Run a churn prediction to generate explainability insights.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-header">Top Churn Drivers</div>', unsafe_allow_html=True)
        # Bar chart code...
        st.info("Insights: Recency is the primary factor increasing churn risk for this customer.")

# --- PAGE: RETENTION PLAYBOOK ---
elif page == "Playbook":
    st.markdown('<div class="main-title">Retention Playbook</div>', unsafe_allow_html=True)
    if st.session_state.last_prediction:
        res = st.session_state.last_prediction
        st.markdown(f"""
        <div class="kpi-card">
            <h4 style="color:#60A5FA;">RECOMMENDED ACTION</h4>
            <h2 style="margin:5px 0;">{res['recommended_action']}</h2>
            <hr style="opacity:0.1">
            <p><b>Strategic Offer:</b> {res['offer']}</p>
            <p><b>Priority:</b> <span class="status-badge status-down">CRITICAL</span></p>
            <p><b>Projected ROI:</b> {res['roi']}x</p>
        </div>
        """, unsafe_allow_html=True)

# --- PAGE: SYSTEM HEALTH ---
elif page == "Health":
    st.markdown('<div class="main-title">Node Health & Monitoring</div>', unsafe_allow_html=True)
    
    nodes = {
        "FastAPI Service": "UP",
        "PostgreSQL DB": "UP",
        "Redis Cache": "UP",
        "Random Forest Model": "UP",
        "SHAP Engine": "UP"
    }
    
    for name, status in nodes.items():
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding:15px; background:#1E293B; border-radius:10px; margin-bottom:10px;">
            <span style="font-weight:600;">{name}</span>
            <span class="status-badge status-up">● {status}</span>
        </div>
        """, unsafe_allow_html=True)