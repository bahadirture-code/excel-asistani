import io
import json
import traceback
from copy import deepcopy
import sys
import os

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Streamlit Cloud uyumluluğu için sys.path ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from engine.ai_parser import AIParser
    from engine.command_engine import CommandEngine
except ImportError as e:
    st.error(f"❌ Engine modülleri yüklenemedi: {str(e)}")
    st.stop()

st.set_page_config(
    page_title="AI Excel Asistanı",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "current_df" not in st.session_state:
    st.session_state.current_df = None

if "history" not in st.session_state:
    st.session_state.history = []

if "redo" not in st.session_state:
    st.session_state.redo = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_json" not in st.session_state:
    st.session_state.last_json = None

if "logs" not in st.session_state:
    st.session_state.logs = []

if "uploaded_name" not in st.session_state:
    st.session_state.uploaded_name = ""

if "quick_command" not in st.session_state:
    st.session_state.quick_command = ""

api_key = st.secrets["GROQ_API_KEY"]
parser = AIParser(api_key)
engine = CommandEngine()

def save_history():
    if st.session_state.current_df is None:
        return
    st.session_state.history.append(deepcopy(st.session_state.current_df))
    if len(st.session_state.history) > 20:
        st.session_state.history.pop(0)

def undo():
    if len(st.session_state.history) == 0:
        return
    st.session_state.redo.append(deepcopy(st.session_state.current_df))
    st.session_state.current_df = st.session_state.history.pop()

def redo():
    if len(st.session_state.redo) == 0:
        return
    st.session_state.history.append(deepcopy(st.session_state.current_df))
    st.session_state.current_df = st.session_state.redo.pop()

# ======================================================
# SOL MENÜ
# ======================================================

with st.sidebar:
    st.title("🤖 AI Excel")
    uploaded_file = st.file_uploader(
        "Excel Dosyası",
        type=["xlsx", "xls", "csv"]
    )
    if uploaded_file is not None:
        st.session_state.uploaded_name = uploaded_file.name
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.session_state.current_df = df

    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("↩ Undo", use_container_width=True):
        undo()
        st.rerun()
    if c2.button("↪ Redo", use_container_width=True):
        redo()
        st.rerun()

    st.divider()
    st.write("**Dosya**")
    st.write(st.session_state.uploaded_name)

    if st.session_state.current_df is not None:
        st.metric("Satır", len(st.session_state.current_df))
        st.metric("Sütun", len(st.session_state.current_df.columns))
        st.metric("Boş Hücre", int(st.session_state.current_df.isna().sum().sum()))
        st.metric("Tekrar Eden", int(st.session_state.current_df.duplicated().sum()))

# ======================================================
# ANA EKRAN
# ======================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["💬 AI", "📄 Veri", "📊 Dashboard", "🧠 JSON", "📜 Log"]
)

# ======================================================
# TAB 1 - AI SOHBET
# ======================================================

with tab1:
    st.subheader("🤖 AI Excel Asistanı")
    if st.session_state.current_df is None:
        st.info("Lütfen önce bir Excel dosyası yükleyin.")
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.1)
        max_tokens = st.slider("Max Token", 256, 4096, 2048, 256)

        prompt = None
        if st.session_state.quick_command:
            prompt = st.session_state.quick_command
            st.session_state.quick_command = ""
        else:
            prompt = st.chat_input("AI'ya ne yapmak istediğini yaz...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.spinner("AI düşünüyor..."):
                try:
                    save_history()
                    data = parser.parse(
                        prompt,
                        st.session_state.current_df,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    st.session_state.last_json = data
                    result = engine.execute(data, st.session_state.current_df)
                    st.session_state.current_df = result
                    st.session_state.logs.append({"prompt": prompt, "json": data})
                    st.session_state.messages.append({"role": "assistant", "content": "✅ İşlem tamamlandı."})
                    st.rerun()
                except Exception as e:
                    st.session_state.messages.append({"role": "assistant", "content": "❌ İşlem başarısız."})
                    st.session_state.logs.append(traceback.format_exc())
                    st.error(f"Hata: {str(e)}")
                    st.rerun()

# ======================================================
# TAB 2 - VERİ
# ======================================================

with tab2:
    st.subheader("📄 Veri")
    if st.session_state.current_df is not None:
        st.dataframe(st.session_state.current_df, use_container_width=True, height=700)
    else:
        st.info("Veri bulunamadı.")

# ======================================================
# TAB 3 - DASHBOARD
# ======================================================

with tab3:
    st.subheader("📊 Dashboard")
    if st.session_state.current_df is None:
        st.info("Veri bulunamadı.")
    else:
        df = st.session_state.current_df
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Satır", len(df))
        c2.metric("Sütun", len(df.columns))
        c3.metric("Boş Hücre", int(df.isna().sum().sum()))
        c4.metric("Tekrar Eden", int(df.duplicated().sum()))

        numeric = df.select_dtypes(include="number")
        if len(numeric.columns) > 0:
            column = st.selectbox("Grafik Kolonu", numeric.columns, key="dashboard_numeric")
            fig = go.Figure()
            fig.add_bar(x=df.index, y=df[column], name=column)
            fig.update_layout(height=450, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("İstatistik")
            st.dataframe(numeric.describe().T, use_container_width=True)
        else:
            st.warning("Sayısal kolon bulunamadı.")

# ======================================================
# TAB 4 - AI JSON
# ======================================================

with tab4:
    st.subheader("🧠 AI JSON")
    if st.session_state.last_json is None:
        st.info("Henüz AI çalıştırılmadı.")
    else:
        st.json(st.session_state.last_json)
        st.download_button(
            "📥 JSON İndir",
            json.dumps(st.session_state.last_json, indent=4, ensure_ascii=False),
            file_name="ai_response.json",
            mime="application/json"
        )

# ======================================================
# TAB 5 - LOG
# ======================================================

with tab5:
    st.subheader("📜 AI İşlem Geçmişi")
    if len(st.session_state.logs) == 0:
        st.info("Henüz işlem yapılmadı.")
    else:
        for i, log in enumerate(reversed(st.session_state.logs), start=1):
            with st.expander(f"İşlem {i}", expanded=False):
                if isinstance(log, dict):
                    st.markdown("### Kullanıcı")
                    st.code(log["prompt"])
                    st.markdown("### AI JSON")
                    st.json(log["json"])
                else:
                    st.markdown("### Hata")
                    st.code(log)

# ======================================================
# EXPORT
# ======================================================

if st.session_state.current_df is not None:
    with st.sidebar:
        st.divider()
        st.subheader("💾 Dışa Aktar")
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            st.session_state.current_df.to_excel(writer, index=False)
        st.download_button(
            "📥 Excel",
            excel_buffer.getvalue(),
            file_name="AI_EXCEL.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.download_button(
            "📥 CSV",
            st.session_state.current_df.to_csv(index=False).encode("utf-8"),
            file_name="AI_EXCEL.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.download_button(
            "📥 JSON",
            st.session_state.current_df.to_json(orient="records", force_ascii=False, indent=2),
            file_name="AI_EXCEL.json",
            mime="application/json",
            use_container_width=True
        )

# ======================================================
# AI HIZLI KOMUTLAR
# ======================================================

with st.sidebar:
    st.divider()
    st.subheader("⚡ Hazır Komutlar")
    commands = [
        "Veriyi analiz et",
        "Boş satırları sil",
        "Tekrar eden kayıtları kaldır",
        "Kolonları analiz et",
        "En uygun grafiği öner",
        "Dashboard oluştur",
        "Veri kalitesini analiz et",
        "Eksik verileri göster",
        "İstatistikleri çıkar",
        "Veriyi optimize et"
    ]
    for cmd in commands:
        if st.button(cmd, use_container_width=True, key=f"btn_{cmd}"):
            st.session_state.quick_command = cmd
            st.rerun()

# ======================================================
# FOOTER
# ======================================================

st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Versiyon", "1.0")
c2.metric("AI", "Groq Llama")
c3.metric("Motor", "Command Engine")
c4.metric("Durum", "🟢 Hazır")