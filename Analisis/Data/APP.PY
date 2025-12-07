import streamlit as st
import pandas as pd
import openai

# -----------------------------
# KONFIGURASI AWAL
# -----------------------------
openai.api_key = "ISI_API_KEY_MU"

st.set_page_config(page_title="AI Agent Demo", layout="wide")

st.title("🤖 AI Agent + Streamlit")
st.write("Contoh agent yang bisa chat dan menganalisis file CSV/XLSX.")

# -----------------------------
# MEMORY SEDERHANA
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------
# FITUR UPLOAD FILE
# -----------------------------
uploaded_file = st.file_uploader("Upload CSV atau Excel", type=["csv", "xlsx"])

df = None
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("📄 Data yang Diunggah")
        st.dataframe(df)
    except Exception as e:
        st.error("Error membaca file: " + str(e))


# -----------------------------
# FUNGSI AGENT
# -----------------------------
def agent_response(prompt, df=None):
    """
    Agent sederhana:
    - Jika ada file → bisa lakukan analisis statistik dasar
    - Jika tidak ada → chatbot biasa
    """

    if df is not None:
        data_description = {
            "columns": df.columns.tolist(),
            "row_count": len(df),
            "numeric_summary": df.describe().to_dict()
        }
    else:
        data_description = "Tidak ada data."

    system_prompt = f"""
    Kamu adalah AI Agent cerdas.
    Jika ada dataset, lakukan analisis berdasarkan:
    - Kolom apa saja
    - Statistik deskriptif
    - Insight dari angka
    Jika tidak ada dataset, jawab sebagai chatbot normal.
    """

    full_prompt = f"""
    DATASET:
    {data_description}

    USER ASKING:
    {prompt}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_prompt}
        ]
    )

    return response.choices[0].message["content"]


# -----------------------------
# INPUT USER
# -----------------------------
user_input = st.text_input("Tanyakan sesuatu kepada Agent:")

if st.button("Kirim"):
    if user_input.strip() == "":
        st.warning("Masukkan pertanyaan terlebih dahulu.")
    else:
        # Tambahkan ke history
        st.session_state.chat_history.append(("user", user_input))

        # Dapatkan jawaban agent
        ai_reply = agent_response(user_input, df=df)

        st.session_state.chat_history.append(("assistant", ai_reply))


# -----------------------------
# TAMPILKAN HISTORI CHAT
# -----------------------------
st.subheader("💬 Riwayat Chat")
for role, text in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"**🧑 Kamu:** {text}")
    else:
        st.markdown(f"**🤖 Agent:** {text}")
