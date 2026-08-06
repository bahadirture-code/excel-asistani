import streamlit as st
import pandas as pd
import io
import json
import plotly.express as px

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
# OTURUM DURUMU
# ==========================
if 'file_data' not in st.session_state:
    st.session_state.file_data = {}  # {dosya_adı: {'bytes': ..., 'sheets': [...], 'selected_sheet': ..., 'df': ...}}
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'processing' not in st.session_state:
    st.session_state.processing = False

st.title("🤖 AI Veri Asistanı")
st.markdown("**Dosyaları yükleyin, sayfa seçin, AI ile doğal dilde konuşarak verilerinizi işleyin.**")

# ==========================
# DOSYA YÜKLEME
# ==========================
uploaded_files = st.file_uploader(
    "Dosyaları yükleyin (Excel veya CSV)",
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
                    selected_sheet = sheets[0]
            st.session_state.file_data[file.name] = {
                'bytes': file_bytes,
                'sheets': sheets,
                'selected_sheet': selected_sheet,
                'df': None
            }

# ==========================
# DOSYA KARTLARI (Önizleme + Sayfa Seçimi)
# ==========================
if st.session_state.file_data:
    st.subheader("📁 Yüklenen Dosyalar")
    for name, data in st.session_state.file_data.items():
        with st.expander(f"📄 {name}", expanded=False):
            # Sayfa seçimi
            if data['sheets']:
                current_sheet = data['selected_sheet'] if data['selected_sheet'] else data['sheets'][0]
                selected_sheet = st.selectbox(
                    f"Sayfa seçin ({name})",
                    options=data['sheets'],
                    index=data['sheets'].index(current_sheet) if current_sheet in data['sheets'] else 0,
                    key=f"sheet_{name}"
                )
                if data['selected_sheet'] != selected_sheet or data['df'] is None:
                    data['selected_sheet'] = selected_sheet
                    data['df'] = load_file(data['bytes'], name, sheet_name=selected_sheet)
                    if data['df'] is not None:
                        st.success(f"✅ {selected_sheet} yüklendi")
            else:
                if data['df'] is None:
                    data['df'] = load_file(data['bytes'], name)
                    if data['df'] is not None:
                        st.success(f"✅ {name} yüklendi")

            if data['df'] is not None:
                df = data['df']
                st.caption(f"{df.shape[0]} satır × {df.shape[1]} sütun")
                with st.expander("🔍 Önizleme"):
                    st.dataframe(df.head(5), use_container_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    excel_data, excel_fname = export_file(df, "xlsx", name.replace('.', '_'))
                    if excel_data:
                        st.download_button("📊 Excel İndir", excel_data, excel_fname, key=f"excel_{name}")
                with col2:
                    csv_data, csv_fname = export_file(df, "csv", name.replace('.', '_'))
                    if csv_data:
                        st.download_button("📄 CSV İndir", csv_data, csv_fname, key=f"csv_{name}")
            else:
                st.warning("⚠️ Veri yüklenemedi")

# ==========================
# AI ASİSTANI (SOHBET)
# ==========================
st.markdown("---")
st.header("💬 AI Veri Asistanı ile Sohbet")

if not HAS_GROQ:
    st.warning("Groq kütüphanesi yüklü değil. `pip install groq` ile yükleyin.")
else:
    # Mevcut dosyaları listele
    available_dfs = {name: data['df'] for name, data in st.session_state.file_data.items() if data['df'] is not None}
    if not available_dfs:
        st.info("Lütfen önce yukarıdan dosya yükleyin ve bir sayfa seçin.")
    else:
        # Sohbet geçmişini göster
        for msg in st.session_state.messages:
            role_class = "user" if msg["role"] == "user" else "assistant"
            st.markdown(f'''
                <div style="padding:0.75rem 1rem; border-radius:12px; margin-bottom:0.5rem; background-color:{"#dbeafe" if msg["role"]=="user" else "#f1f5f9"}; max-width:80%; {"margin-left:auto; border-bottom-right-radius:4px;" if msg["role"]=="user" else "margin-right:auto; border-bottom-left-radius:4px;"}">
                    <div style="font-weight:600; font-size:0.8rem; color:#475569;">{msg["role"].capitalize()}</div>
                    {msg["content"]}
                </div>
            ''', unsafe_allow_html=True)

        # Kullanıcı girişi
        prompt = st.chat_input("Ne yapmak istersiniz? (ör: 'df1'deki satış toplamını al')")
        if prompt and not st.session_state.processing:
            st.session_state.processing = True
            try:
                # Kullanıcı mesajını ekle
                st.session_state.messages.append({"role": "user", "content": prompt})

                # AI'den yanıt al
                api_key = st.secrets.get("GROQ_API_KEY")
                if not api_key:
                    st.error("❌ GROQ_API_KEY eksik")
                    st.session_state.processing = False
                    st.rerun()

                client = Groq(api_key=api_key)
                df_list_str = ", ".join([f"{k}: {list(v.columns)}" for k, v in available_dfs.items()])

                sys_msg = f"""Python/Pandas uzmanısın. Mevcut DataFrame'ler: {df_list_str}
Kullanıcının komutunu analiz et.
Eğer komut net değilse veya eksik bilgi varsa, JSON formatında cevap ver:
{{"status": "need_clarification", "question": "Açıklayıcı soru"}}

Eğer komut yeterliyse, çalışan Pandas kodunu oluştur ve JSON formatında döndür:
{{"status": "success", "code": "result_df = ...", "explanation": "Kısa açıklama"}}

Sadece JSON döndür. Kod içinde yorum satırları (#) kullanabilirsin. Sonucu her zaman 'result_df' değişkenine ata.
Örnek: {{"status": "success", "code": "result_df = df1.groupby('kategori').sum()", "explanation": "Kategoriye göre toplam"}}"""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": sys_msg},
                        {"role": "user", "content": f"Kullanıcı komutu: {prompt}"}
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                    response_format={"type": "json_object"}
                )
                raw_response = response.choices[0].message.content
                try:
                    data = json.loads(raw_response)
                except json.JSONDecodeError:
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Yanıt JSON değil: {raw_response[:200]}"})
                    st.session_state.processing = False
                    st.rerun()

                if data.get("status") == "need_clarification":
                    question = data.get("question", "Anlamadım, lütfen daha açıklayıcı olur musunuz?")
                    st.session_state.messages.append({"role": "assistant", "content": f"❓ {question}"})
                    st.session_state.processing = False
                    st.rerun()
                elif data.get("status") == "success":
                    code = data.get("code")
                    explanation = data.get("explanation", "İşlem tamamlandı")
                    # Kodu çalıştır
                    try:
                        local_vars = {k: v.copy() for k, v in available_dfs.items()}
                        local_vars["pd"] = pd
                        exec(code, {}, local_vars)
                        result_df = local_vars.get("result_df")

                        if result_df is not None and isinstance(result_df, pd.DataFrame):
                            st.session_state.messages.append({"role": "assistant", "content": f"✅ {explanation}"})
                            # Sonucu göster
                            with st.chat_message("assistant"):
                                st.write(f"**{explanation}**")
                                st.dataframe(result_df.head(10), use_container_width=True)
                                # Grafik
                                num_cols = result_df.select_dtypes(include=['number']).columns
                                if len(num_cols) >= 1 and len(result_df) > 0:
                                    fig = px.histogram(result_df, x=num_cols[0], title="Sonuç Dağılımı")
                                    st.plotly_chart(fig, use_container_width=True)
                                # İndir
                                col1, col2 = st.columns(2)
                                with col1:
                                    excel_data, excel_fname = export_file(result_df, "xlsx", "ai_sonuc")
                                    if excel_data:
                                        st.download_button("📊 Excel İndir", excel_data, excel_fname, key="ai_excel")
                                with col2:
                                    csv_data, csv_fname = export_file(result_df, "csv", "ai_sonuc")
                                    if csv_data:
                                        st.download_button("📄 CSV İndir", csv_data, csv_fname, key="ai_csv")
                            st.session_state.processing = False
                            st.rerun()
                        else:
                            st.session_state.messages.append({"role": "assistant", "content": "⚠️ Kod çalıştı ama 'result_df' oluşturulamadı."})
                            st.session_state.processing = False
                            st.rerun()
                    except Exception as e:
                        st.session_state.messages.append({"role": "assistant", "content": f"❌ Kod hatası: {str(e)[:200]}"})
                        st.session_state.processing = False
                        st.rerun()
                else:
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Beklenmeyen yanıt: {raw_response[:200]}"})
                    st.session_state.processing = False
                    st.rerun()
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"❌ Hata: {str(e)[:200]}"})
                st.session_state.processing = False
                st.rerun()

    # Sohbet temizleme
    if st.button("🗑️ Sohbet Geçmişini Temizle"):
        st.session_state.messages = []
        st.rerun()