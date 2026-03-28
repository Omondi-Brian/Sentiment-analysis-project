import streamlit as st
import requests
import plotly.graph_objects as go

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(
    page_title="Single Text Prediction",
    page_icon="📝",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .result-box { padding: 1rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

st.title("📝 Single Text Prediction")

# Input
user_input = st.text_area("✍️ Enter text to analyze:", height=150, placeholder="Type your tweet or message here... e.g., 'Safaricom bundles are amazing!'")

if st.button("🔍 Analyze Sentiment", type="primary"):
    if not user_input.strip():
        st.warning("⚠️ Please enter text.")
    else:
        with st.spinner("⏳ Analyzing..."):
            response = requests.post(API_URL, json={"text": user_input})

        if response.status_code == 200:
            result = response.json()
            sentiment = result["lstm_prediction"]
            confidence = result["confidence"]
            baseline = result["baseline_prediction"]

            # Color mapping
            color_map = {"positive": "#00A651", "negative": "#e74c3c", "neutral": "#95a5a6"}
            color = color_map.get(sentiment, "gray")

            # Results Section
            st.subheader("📊 Results")
            col1, col2 = st.columns([2,1])

            with col1:
                st.markdown(f"### LSTM Sentiment: <span style='color:{color};'>{sentiment.upper()}</span>", unsafe_allow_html=True)
                st.write(f"**Baseline Prediction:** {baseline}")
                st.success("✅ Analysis complete!")

            with col2:
                # Confidence Gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=confidence * 100,
                    title={'text': "Confidence (%)"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': color}}
                ))
                st.plotly_chart(fig, use_container_width=True)

            # History (persistent)
            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.append({"text": user_input, "sentiment": sentiment, "confidence": confidence})

            with st.expander("📜 Prediction History"):
                for entry in st.session_state.history:
                    st.write(f"- **Text:** {entry['text']}\n  **Sentiment:** {entry['sentiment']} ({entry['confidence']:.2f})")
        else:
            st.error("❌ API error.")