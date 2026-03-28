import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Analytics Dashboard")

# Fetch Data
try:
    summary = requests.get(f"{API_BASE}/analytics/summary").json()
    ts = requests.get(f"{API_BASE}/analytics/timeseries").json()
    df_ts = pd.DataFrame(ts)
    perf = requests.get(f"{API_BASE}/analytics/model_compare").json()
except Exception as e:
    st.error(f"❌ API error: {e}")

# Sentiment Distribution (Pie with hover)
st.header("📈 Sentiment Distribution")
fig = px.pie(names=list(summary["counts"].keys()), values=list(summary["counts"].values()), 
             color_discrete_map={"positive": "#00A651", "negative": "#e74c3c", "neutral": "#95a5a6"},
             hole=0.3)  # Donut 
fig.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+percent+value')
st.plotly_chart(fig, use_container_width=True)

# Sentiment Trend (Interactive Line with range slider)
st.header("⏳ Sentiment Over Time")
fig2 = px.line(df_ts, x="date", y=["positive", "negative", "neutral"], 
               color_discrete_map={"positive": "#00A651", "negative": "#e74c3c", "neutral": "#95a5a6"},
               markers=True)
fig2.update_layout(xaxis_rangeslider_visible=True)  # Add slider
st.plotly_chart(fig2, use_container_width=True)

# Model Comparison (Heatmap)
st.header("🤖 Model Comparison")
metrics = ["accuracy", "precision", "recall", "f1"]

df_perf = pd.DataFrame({
    "Metric": metrics * 2,
    "Value": [perf["baseline"][m] for m in metrics] + [perf["lstm"][m] for m in metrics],
    "Model": ["Baseline"] * 4 + ["LSTM"] * 4
})

# Pivot for heatmap
heatmap_data = df_perf.pivot(index="Model", columns="Metric", values="Value")

fig3 = px.imshow(
    heatmap_data,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="Greens"
)
fig3.update_layout(
    title="Baseline vs LSTM Performance Heatmap",
    xaxis_title="Metric",
    yaxis_title="Model"
)

st.plotly_chart(fig3, use_container_width=True)

# Detailed Metrics in Expanders
st.subheader("📌 Detailed Metrics")
col1, col2 = st.columns(2)
with col1.expander("Baseline Model", expanded=True):
    for m in metrics:
        st.metric(m.capitalize(), f"{perf['baseline'][m]:.2f}")
with col2.expander("LSTM Model", expanded=True):
    for m in metrics:
        st.metric(m.capitalize(), f"{perf['lstm'][m]:.2f}")