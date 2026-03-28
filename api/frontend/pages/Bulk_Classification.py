import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import BytesIO
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time

API_URL = "http://127.0.0.1:8000/bulk_predict"

st.set_page_config(
    page_title="Bulk CSV Classification",
    page_icon="📂",
    layout="wide"
)

# Sidebar
st.sidebar.title("⚙️ Options")
show_kpis = st.sidebar.checkbox("KPIs", value=True)
show_distribution = st.sidebar.checkbox("Distribution", value=True)
show_confidence = st.sidebar.checkbox("Confidence Histogram", value=True)
show_trend = st.sidebar.checkbox("Trend", value=True)
show_wordcloud = st.sidebar.checkbox("Word Cloud", value=False)
show_representative = st.sidebar.checkbox("Representative Tweets", value=True)

st.title("📂 Bulk CSV Classification")

uploaded = st.file_uploader("📤 Upload CSV ('text' column required)", type=['csv'])

if uploaded:
    if st.button("🔄 Process CSV", type="primary"):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)

        files = {"file": (uploaded.name, uploaded.getvalue(), "text/csv")}
        response = requests.post(API_URL, files=files)

        if response.status_code == 200:
            st.session_state.df = pd.read_csv(BytesIO(response.content))
            st.session_state.csv_content = response.content
            st.success("✅ Processed!")
        else:
            st.error("❌ Error.")

if "df" in st.session_state:
    df = st.session_state.df

    # Tabs for organization
    tab1, tab2 = st.tabs(["📋 Data Preview", "📈 Visualizations"])

    with tab1:
        st.subheader("Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        st.download_button("⬇️ Download Results", data=st.session_state.csv_content, file_name="classified.csv", mime="text/csv")

    with tab2:
        color_map = {"positive": "#00A651", "negative": "#e74c3c", "neutral": "#95a5a6"}

        if show_kpis:
            st.subheader("📌 KPIs")
            col1, col2, col3 = st.columns(3)
            col1.metric("Positive 😊", df["lstm_prediction"].eq("positive").sum())
            col2.metric("Negative 😡", df["lstm_prediction"].eq("negative").sum())
            col3.metric("Neutral 😐", df["lstm_prediction"].eq("neutral").sum())

        if show_distribution:
            counts = df["lstm_prediction"].value_counts()
            fig = px.bar(counts, x=counts.index, y=counts.values, color=counts.index, color_discrete_map=color_map)
            st.plotly_chart(fig, use_container_width=True)

        if show_confidence:
            fig2 = px.histogram(df, x="confidence", nbins=20, color_discrete_sequence=["#00A651"])
            st.plotly_chart(fig2, use_container_width=True)

        if show_trend and "created_at" in df.columns:
            df["date"] = pd.to_datetime(df["created_at"]).dt.date
            trend = df.groupby(["date", "lstm_prediction"]).size().reset_index(name="count")
            fig3 = px.line(trend, x="date", y="count", color="lstm_prediction", markers=True, color_discrete_map=color_map)
            st.plotly_chart(fig3, use_container_width=True)

        if show_wordcloud:
            sentiment_filter = st.selectbox("Word Cloud for Sentiment", ["positive", "negative", "neutral"])
            text = " ".join(df[df["lstm_prediction"] == sentiment_filter]["text"].astype(str))
            if text.strip():
                wc = WordCloud(width=800, height=400, background_color="white").generate(text)
                fig, ax = plt.subplots()
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)

        if show_representative:
            st.subheader("📝 Representative Tweets")
            col1, col2, col3 = st.columns(3)
            for sent, col in zip(["positive", "negative", "neutral"], [col1, col2, col3]):
                with col:
                    st.markdown(f"**{sent.capitalize()}**")
                    samples = df[(df["lstm_prediction"] == sent) & (df["confidence"] > 0.8)]["text"].head(5)
                    for t in samples:
                        st.write(f"- {t}")