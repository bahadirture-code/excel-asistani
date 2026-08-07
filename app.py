import io
import json
import traceback
from copy import deepcopy
import sys
import os

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

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

# Session state
if "current_df" not in st.session_state:
    st.session_state.current_df = None
if "ana_df" not in st.session_state:
    st.session_state.ana_df = None
if "kaynak_df" not in st.session_state:
    st.session_state.kaynak_df = None
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
if "ana_sheet" not in st.session_state:
    st.session_state.ana_sheet = None
if "kaynak_sheet" not in st.session_state:
    st.session_state.kaynak_sheet = None

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
    st.title("🤖 AI Excel Asistanı")
    
    # ANA DOSYA
    ana_dosya = st.file_uploader("📄 Ana Dosyayı Yükle (HBA)", type=["xlsx", "xls", "csv"], key="ana_upload")
    if ana_dosya is not None:
        if ana_dosya.name.endswith(".csv"):
            st.session_state.ana_df = pd.read_csv(ana_dosya)
            st.session_state.ana_sheet = None
            st.success(f"✅ Ana CSV dosyası yüklendi: {ana_dosya.name}")
            if st.session_state.current_df is None:
                st.session_state.current_df = st.session_state.ana_df.copy()
                st.session_state.uploaded_name = ana_dosya.name
        else:
            excel_file = pd.ExcelFile(ana_dosya)
            sheet_names = excel_file.sheet_names
            default_sheet = sheet_names[0] if sheet_names else None
            if st.session_state.ana_sheet is None or st.session_state.ana_sheet not in sheet_names:
                st.session_state.ana_sheet = default_sheet
            secilen_sheet = st.selectbox(
                "📑 Ana Dosya Sayfası Seç",
                sheet_names,
                index=sheet_names.index(st.session_state.ana_sheet) if st.session_state.ana_sheet in sheet_names else 0,
                key="ana_sheet_selector"
            )
            if secilen_sheet != st.session_state.ana_sheet:
                st.session_state.ana_sheet = secilen_sheet
                st.session_state.ana_df = pd.read_excel(ana_dosya, sheet_name=secilen_sheet)
                if st.session_state.current_df is None or st.session_state.uploaded_name == ana_dosya.name:
                    st.session_state.current_df = st.session_state.ana_df.copy()
                    st.session_state.uploaded_name = f"{ana_dosya.name} - {secilen_sheet}"
                st.success(f"✅ Ana dosya yüklendi: {ana_dosya.name} / Sayfa: {secilen_sheet}")
            else:
                if st.session_state.ana_df is None:
                    st.session_state.ana_df = pd.read_excel(ana_dosya, sheet_name=secilen_sheet)
                    if st.session_state.current_df is None:
                        st.session_state.current_df = st.session_state.ana_df.copy()
                        st.session_state.uploaded_name = f"{ana_dosya.name} - {secilen_sheet}"
                    st.success(f"✅ Ana dosya yüklendi: {ana_dosya.name} / Sayfa: {secilen_sheet}")
    
    # KAYNAK DOSYA
    kaynak_dosya = st.file_uploader("📄 Kaynak Dosyayı Yükle (geçiş)", type=["xlsx", "xls", "csv"], key="kaynak_upload")
    if kaynak_dosya is not None:
        if kaynak_dosya.name.endswith(".csv"):
            st.session_state.kaynak_df = pd.read_csv(kaynak_dosya)
            st.session_state.kaynak_sheet = None
            st.success(f"✅ Kaynak CSV dosyası yüklendi: {kaynak_dosya.name}")
        else:
            excel_file = pd.ExcelFile(kaynak_dosya)
            sheet_names = excel_file.sheet_names
            default_sheet = sheet_names[0] if sheet_names else None
            if st.session_state.kaynak_sheet is None or st.session_state.kaynak_sheet not in sheet_names:
                st.session_state.kaynak_sheet = default_sheet
            secilen_sheet = st.selectbox(
                "📑 Kaynak Dosya Sayfası Seç",
                sheet_names,
                index=sheet_names.index(st.session_state.kaynak_sheet) if st.session_state.kaynak_sheet in sheet_names else 0,
                key="kaynak_sheet_selector"
            )
            if secilen_sheet != st.session_state.kaynak_sheet:
                st.session_state.kaynak_sheet = secilen_sheet
                st.session_state.kaynak_df = pd.read_excel(kaynak_dosya, sheet_name=secilen_sheet)
                st.success(f"✅ Kaynak dosya yüklendi: {kaynak_dosya.name} / Sayfa: {secilen_sheet}")
            else:
                if st.session_state.kaynak_df is None:
                    st.session_state.kaynak_df = pd.read_excel(kaynak_dosya, sheet_name=secilen_sheet)
                    st.success(f"✅ Kaynak dosya yüklendi: {kaynak_dosya.name} / Sayfa: {secilen_sheet}")
    
    st.divider()
    
    c1, c2 = st.columns(2)
    if c1.button("↩ Undo", width='stretch'):
        undo()
        st.rerun()
    if c2.button("↪ Redo", width='stretch'):
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

    st.divider()
    st.subheader("💾 Dışa Aktar")
    if st.session_state.current_df is not None:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            st.session_state.current_df.to_excel(writer, index=False)
        st.download_button(
            "📥 Excel",
            excel_buffer.getvalue(),
            file_name="AI_EXCEL.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch'
        )
        st.download_button(
            "📥 CSV",
            st.session_state.current_df.to_csv(index=False).encode("utf-8"),
            file_name="AI_EXCEL.csv",
            mime="text/csv",
            width='stretch'
        )
        st.download_button(
            "📥 JSON",
            st.session_state.current_df.to_json(orient="records", force_ascii=False, indent=2),
            file_name="AI_EXCEL.json",
            mime="application/json",
            width='stretch'
        )

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
        st.info("Lütfen önce bir ana dosya yükleyin.")
    else:
        # HIZLI İŞLEM BUTONLARI
        st.markdown("⚡ **Hızlı Şablon İşlemleri:**")
        b1, b2, b3, b4 = st.columns(4)
        if b1.button("🧹 Otomatik Temizle", use_container_width=True):
            st.session_state.quick_command = "Otomatik temizle"
            st.rerun()
        if b2.button("📑 Mükerrerleri Sil", use_container_width=True):
            st.session_state.quick_command = "Aynı satırları sil"
            st.rerun()
        if b3.button("📊 Veri Profilini Çıkar", use_container_width=True):
            st.session_state.quick_command = "Veri profilini çıkar"
            st.rerun()
        if b4.button("🔗 Kolon İsimlerini Temizle", use_container_width=True):
            st.session_state.quick_command = "Kolon adlarını temizle"
            st.rerun()
        
        st.divider()

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.1)
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
                    if st.session_state.current_df is None and st.session_state.ana_df is not None:
                        st.session_state.current_df = st.session_state.ana_df.copy()
                    if st.session_state.current_df is None:
                        st.error("Lütfen önce bir ana dosya yükleyin.")
                        st.stop()
                    
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
        st.dataframe(st.session_state.current_df.astype(str), width='stretch', height=700)
    else:
        st.info("Veri bulunamadı. Lütfen dosya yükleyin.")

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
            st.dataframe(numeric.describe().T, width='stretch')
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
# FOOTER
# ======================================================

st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Versiyon", "1.0")
c2.metric("AI", "Groq Llama")
c3.metric("Motor", "Command Engine")
c4.metric("Durum", "🟢 Hazır")