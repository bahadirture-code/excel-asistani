import streamlit as st
import pandas as pd
import io
import json
import plotly.express as px
import plotly.graph_objects as go

try:
    from groq import Groq
    HAS_GROQ = True
except Exception:
    HAS_GROQ = False

st.set_page_config(page_title="AI Veri Asistanı", layout="wide", page_icon="🤖")

# ==========================
# YARDIMCI FONKSİYONLAR
# ==========================
@st.cache_data(ttl=3600)
def load_file(file_bytes, filename, sheet_name=0):
    try:
        if filename.lower().endswith('.csv'):
            return pd.read_csv(io.BytesIO(file_bytes))
        else:
            return pd.read_excel(io.BytesIO(file_bytes), header=0, sheet_name=sheet_name, engine='openpyxl')
    except Exception as e:
        st.error(f"❌ {filename} yüklenirken hata: {e}")
        return None

def get_excel_sheets(file_bytes):
    try:
        xl = pd.ExcelFile(io.BytesIO(file_bytes), engine='openpyxl')
        return xl.sheet_names
    except Exception:
        return []

def export_file(df, format_type="xlsx", filename="veri"):
    output = io.BytesIO()
    try:
        if format_type == "xlsx":
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            return output.getvalue(), f"{filename}.xlsx"
        elif format_type == "csv":
            output.write(df.to_csv(index=False).encode())
            return output.getvalue(), f"{filename}.csv"
    except Exception as e:
        st.error(f"❌ Dışa aktarma hatası: {e}")
        return None, None

# ==========================
# OTOMATİK EŞLEŞTİRME MOTORU
# ==========================
def auto_process_files(file_data_dict):
    gecis_df = None
    hba_df = None
    hba_filename = None

    for name, data in file_data_dict.items():
        if data['df'] is not None:
            cols_upper = [str(c).upper() for c in data['df'].columns]
            if 'ANKET_DURUM' in cols_upper and 'DETAY' in cols_upper:
                gecis_df = data['df'].copy()
            elif 'ADRESNO' in cols_upper or 'DOLULUK' in cols_upper or 'SAYFA1' in [s.upper() for s in data['sheets']]:
                hba_df = data['df'].copy()
                hba_filename = name

    if gecis_df is not None and hba_df is not None:
        try:
            gecis_col = [c for c in gecis_df.columns if 'birim' in str(c).lower()][0]
            hba_col = [c for c in hba_df.columns if 'birim' in str(c).lower()][0]

            gecis_df[gecis_col] = gecis_df[gecis_col].astype(str)
            hba_df[hba_col] = hba_df[hba_col].astype(str)

            durum_map = dict(zip(gecis_df[gecis_col], gecis_df['ANKET_DURUM']))
            detay_map = dict(zip(gecis_df[gecis_col], gecis_df['DETAY']))

            hba_df['ANKET_DURUM'] = hba_df[hba_col].map(durum_map)
            hba_df['DETAY'] = hba_df[hba_col].map(detay_map)

            return hba_df, hba_filename
        except Exception:
            return None, None
    return None, None

# ==========================
# OTURUM DURUMU
# ==========================
if 'file_data' not in st.session_state:
    st.session_state.file_data = {}
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'processing' not in st.session_state:
    st.session_state.processing = False

st.title("🤖 AI Veri Asistanı & Otomatik Eşleştirici")
st.markdown("**Dosyaları yükleyin; sistem geçiş ve HBA dosyalarını algıladığı an otomasyonu çalıştırır.**")

# ==========================
# DOSYA YÜKLEME
# ==========================
with st.container():
    st.subheader("📂 Dosya Yükleme")
    uploaded_files = st.file_uploader(
        "Dosyaları sürükleyin veya seçin (Excel/CSV)",
        type=["xlsx", "csv"],
        accept_multiple_files=True,
        key="file_uploader"
    )
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state.file_data:
                file_bytes = file.read()
                sheets = []
                selected_sheet = None
                if file.name.lower().endswith('.xlsx'):
                    sheets = get_excel_sheets(file_bytes)
                    if sheets:
                        selected_sheet = "Sayfa1" if "Sayfa1" in sheets else sheets[0]
                
                st.session_state.file_data[file.name] = {
                    'bytes': file_bytes,
                    'sheets': sheets,
                    'selected_sheet': selected_sheet,
                    'df': load_file(file_bytes, file.name, sheet_name=selected_sheet if selected_sheet else 0)
                }

# ==========================
# OTOMATİK İŞLEM KONTROLÜ
# ==========================
processed_df, target_file_name = auto_process_files(st.session_state.file_data)

if processed_df is not None:
    st.success(f"⚡ Otomatik Algılama Başarılı! `{target_file_name}` dosyası Anket Durum ve Detay verileriyle güncellendi.")
    st.markdown("### 🎯 Güncellenmiş Tam Dosya (Tüm Sütunlar Korundu)")
    st.dataframe(processed_df.head(10), use_container_width=True)
    
    excel_bytes, excel_name = export_file(processed_df, "xlsx", f"{target_file_name.split('.')[0]}_GUNCEL")
    if excel_bytes:
        st.download_button("📊 Otomatik Güncellenmiş Excel'i İndir", excel_bytes, excel_name, key="auto_download_btn")
    st.markdown("---")

# ==========================
# YÜKLENEN DOSYA KARTLARI
# ==========================
if st.session_state.file_data:
    st.subheader("📁 Yüklenen Ham Dosyalar")
    cols = st.columns(2)
    for idx, (name, data) in enumerate(st.session_state.file_data.items()):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f"**📄 {name}**")
                if data['sheets']:
                    current_sheet = data['selected_sheet']
                    selected_sheet = st.selectbox(
                        f"Sayfa seçin ({name})",
                        options=data['sheets'],
                        index=data['sheets'].index(current_sheet) if current_sheet in data['sheets'] else 0,
                        key=f"sheet_{name}"
                    )
                    if data['selected_sheet'] != selected_sheet:
                        data['selected_sheet'] = selected_sheet
                        data['df'] = load_file(data['bytes'], name, sheet_name=selected_sheet)
                        st.rerun()

# ==========================
# AI SOHBET (EKSTRA SORULAR İÇİN)
# ==========================
st.markdown("---")
st.header("💬 AI Asistanı (Diğer Analizler İçin)")

if HAS_GROQ and st.session_state.file_data:
    prompt = st.chat_input("Farklı bir veri analizi veya sorgu yazın...")
    if prompt and not st.session_state.processing:
        st.session_state.processing = True
        api_key = st.secrets.get("GROQ_API_KEY")
        if api_key:
            client = Groq(api_key=api_key)
            df_desc = [f"df{i+1}: '{n}' (Sütunlar: {list(d['df'].columns if d['df'] is not None else [])})" for i, (n, d) in enumerate(st.session_state.file_data.items())]
            
            sys_msg = f"""Sen bir Pandas analistisin. Mevcut veriler:\n{chr(10).join(df_desc)}\nSonucu `result_df` yap ve JSON ver: {{"status":"success","code":"..."}}"""
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            if data.get("status") == "success":
                local_vars = {f"df{i+1}": d['df'].copy() for i, (n, d) in enumerate(st.session_state.file_data.items()) if d['df'] is not None}
                local_vars["pd"] = pd
                exec(data.get("code"), {}, local_vars)
                res = local_vars.get("result_df")
                if res is not None:
                    st.dataframe(res.head(10), use_container_width=True)
        st.session_state.processing = False