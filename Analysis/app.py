import streamlit as st
import pandas as pd
import plotly.express as px
import os
from groq import Groq
from dotenv import load_dotenv

# ==============================================================
# LOAD API KEY
# ==============================================================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("🚨 API Key is missing! Set it in .env or Streamlit Secrets!")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# ==============================================================
# STREAMLIT CONFIG
# ==============================================================
st.set_page_config(page_title="🌍 GDP Analyzer", layout="wide")
st.title("🌍 Global GDP Analytics – 195 Countries")
st.write("Upload file GDP Anda dan dapatkan visualisasi serta analisis AI otomatis.")

# ==============================================================
# FILE UPLOADER
# ==============================================================
uploaded_file = st.file_uploader("📂 Upload file (Excel/CSV)", type=["xlsx", "csv"])

if uploaded_file:
    # ==========================================================
    # READ DATA
    # ==========================================================
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    required_cols = ["Country Name", "Tahun", "GDP (Current US$)"]
    if not all(col in df.columns for col in required_cols):
        st.error("⚠️ Kolom wajib: Country Name, Tahun, GDP (Current US$)")
        st.stop()

    # Convert numeric
    df["GDP (Current US$)"] = pd.to_numeric(df["GDP (Current US$)"], errors="coerce")
    df["Tahun"] = pd.to_numeric(df["Tahun"], errors="coerce")
    
    # ==========================================================
    # FILTERS
    # ==========================================================
    countries = df["Country Name"].unique().tolist()
    selected_countries = st.multiselect("🌎 Pilih Negara", countries, default=["Indonesia"])
    
    years = sorted(df["Tahun"].unique())
    year_range = st.slider("📅 Pilih Rentang Tahun", min(years), max(years), (min(years), max(years)))

    df_filtered = df[
        (df["Country Name"].isin(selected_countries)) &
        (df["Tahun"].between(year_range[0], year_range[1]))
    ]

    st.subheader("📊 Data Preview")
    st.dataframe(df_filtered)

    # ==========================================================
    # LINE CHART – Trend GDP
    # ==========================================================
    st.subheader("📈 GDP Trend per Negara")
    fig_line = px.line(
        df_filtered,
        x="Tahun",
        y="GDP (Current US$)",
        color="Country Name",
        markers=True,
        title="GDP Trend by Country"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # ==========================================================
    # BAR CHART – Latest Ranking
    # ==========================================================
    st.subheader("🏆 Ranking GDP Negara (Tahun Terakhir)")
    latest_year = df["Tahun"].max()
    df_latest = df[df["Tahun"] == latest_year].sort_values("GDP (Current US$)", ascending=False)

    fig_bar = px.bar(
        df_latest.head(20),
        x="Country Name",
        y="GDP (Current US$)",
        title=f"Top 20 Countries by GDP ({latest_year})",
        text_auto=".2s"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ==========================================================
    # AI GDP ANALYSIS
    # ==========================================================
    st.subheader("🤖 AI Commentary – GDP Analysis")

    prompt = f"""
    Analyze GDP time-series data for the following filtered dataset:
    {df_filtered.to_string(index=False)}

    Provide:
    - Key growth insights
    - Trends for selected countries
    - Comparison between countries
    - Important anomalies or notable years
    """

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert macroeconomic analyst."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.1-8b-instant",
    )

    st.write(response.choices[0].message.content)

    # ==========================================================
    # AI CHAT – Ask Questions
    # ==========================================================
    st.subheader("💬 Tanya AI tentang GDP Anda")

    question = st.text_input("Apa yang ingin Anda tanyakan?")
    if question:
        chat_prompt = f"Dataset: {df_filtered.to_string(index=False)}\nUser question: {question}"
        answer = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a macroeconomic analyst."},
                {"role": "user", "content": chat_prompt}
            ],
            model="llama-3.1-8b-instant",
        )
        st.write(answer.choices[0].message.content)
