import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import io
import random
from streamlit_autorefresh import st_autorefresh

API_URL = "http://127.0.0.1:8000/bulk_predict"  # FastAPI bulk endpoint

# Custom CSS
st.markdown("""
    <style>
    .live-box { background-color: #F0F2F6; padding: 1rem; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🔴 Live Analysis Tab")
st.write("Monitor real-time sentiments from Safaricom tweets (offline Kaggle dataset). Click 'Start Live Monitoring' to begin.")

# ✅ Initialize live_data with explicit dtypes
if "live_data" not in st.session_state:
    st.session_state.live_data = pd.DataFrame({
        "text": pd.Series(dtype="str"),
        "lstm_prediction": pd.Series(dtype="str"),
        "confidence": pd.Series(dtype="float"),
    })
if "running" not in st.session_state:
    st.session_state.running = False

# Start/Stop Buttons
col1, col2 = st.columns(2)
if col1.button("🚀 Start Live Monitoring", type="primary"):
    st.session_state.running = True
if col2.button("🛑 Stop Monitoring"):
    st.session_state.running = False

# Placeholders
live_container = st.container()
chart_placeholder = st.empty()
kpi_placeholder = st.empty()

# ✅ Load Kaggle dataset once
@st.cache_data
def load_dataset():
    df = pd.read_csv("backend/Data/processed/test.csv")
    # Ensure column is named 'text'
    if "text" not in df.columns:
        if "Content" in df.columns:
            df.rename(columns={"Content": "text"}, inplace=True)
        elif "Tweet" in df.columns:
            df.rename(columns={"Tweet": "text"}, inplace=True)
    return df

dataset = load_dataset()

def fetch_offline_tweets():
    """Simulate live tweets by sampling from Kaggle dataset."""
    sample = dataset.sample(n=random.randint(5, 10))
    return sample[["text"]]

# 🔄 Update section (only when running)
if st.session_state.running:
    st_autorefresh(interval=30000, key="live_refresh")

    with live_container:
        st.markdown('<div class="live-box">Fetching new tweets...</div>', unsafe_allow_html=True)

    new_df = fetch_offline_tweets()

    if not new_df.empty:
        # Send to FastAPI for prediction
        csv_buffer = io.StringIO()
        new_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        files = {"file": ("live_tweets.csv", csv_buffer.getvalue().encode(), "text/csv")}
        response = requests.post(API_URL, files=files)

        if response.status_code == 200:
            predicted_df = pd.read_csv(io.BytesIO(response.content))

            # ✅ Concat safely
            st.session_state.live_data = pd.concat(
                [st.session_state.live_data, predicted_df[["text", "lstm_prediction", "confidence"]]]
            ).tail(50)

# 📊 Display section (always shows last results if available)
if not st.session_state.live_data.empty:
    counts = st.session_state.live_data["lstm_prediction"].value_counts()
    with kpi_placeholder.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("Positive 😊", counts.get("positive", 0))
        col2.metric("Negative 😡", counts.get("negative", 0))
        col3.metric("Neutral 😐", counts.get("neutral", 0))

    fig = px.bar(
        counts, x=counts.index, y=counts.values, color=counts.index,
        color_discrete_map={"positive": "#00A651", "negative": "#e74c3c", "neutral": "#95a5a6"}
    )
    chart_placeholder.plotly_chart(fig, use_container_width=True)

    st.subheader("📜 Latest Tweets Being Analyzed")
    st.dataframe(st.session_state.live_data[["text", "lstm_prediction", "confidence"]])
else:
    if st.session_state.running:
        st.warning("No tweets found in dataset.")
    else:
        st.info("Press 'Start Live Monitoring' to begin.")
