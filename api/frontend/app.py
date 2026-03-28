import streamlit as st

st.set_page_config(
    page_title="Safaricom Sentiment Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS 
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F6; }
    .hero { background-color: #00A651; color: white; padding: 2rem; border-radius: 8px; text-align: center; }
    .card { background-color: white; padding: 1rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1rem; }
    </style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown(
    '<div class="hero"><h1>📊 Safaricom Sentiment Analysis Dashboard</h1>'
    '<p>Powered by AI: TF-IDF + Logistic Regression & LSTM Models</p></div>',
    unsafe_allow_html=True
)

# Quick Intro
st.markdown("### Welcome! Analyze sentiments from tweets about Safaricom services like M-Pesa, bundles, and more.")

# Feature Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="card"><h3>Single Prediction</h3><p>Analyze one text instantly. 📝</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="card"><h3>Bulk CSV</h3><p>Process files & visualize trends. 📂</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="card"><h3>Analytics</h3><p>View stats & model performance. 📈</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="card"><h3>Live Analysis</h3><p>Monitor real-time sentiments from a Safaricom tweet dataset. </p></div>', unsafe_allow_html=True)

# Quick Start 
if st.button("🚀 Get Started", key="start_btn", type="primary"):
    st.switch_page("pages/Live_Analysis.py")  
st.write("Use the sidebar to explore tools.")
