import streamlit as st
import pandas as pd
import io
import json
import re
import plotly.express as px
import plotly.graph_objects as go

try:
    from groq import Groq
    HAS_GROQ = True
except Exception:
    HAS_GROQ = False

st.set_page_config(page_title="AI Veri Asistanı", layout="wide", page_icon="🤖")

st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .stApp { max-width: 1400px; margin: 0 auto; }
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
    }
    .card-title { font-weight: 600; font-size: 1.1rem; color: #1e293b; }
    .chat-message {
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        max-width: 80%;
    }
    .chat-message.user {
        background-color: #dbeafe;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }
    .chat-message.assistant {
        background-color: #f1f5f9;
        margin-right: auto;
        border-bottom-left-radius: 4px;
    }
    .chat-message .role {
        font-weight: 600;
        font-size: 0.8rem;
        color: #475569;
        margin-bottom: 0.25rem;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #2563eb;
        box-shadow: 0 4px 12px rgba(59,130,246,0.3);
    }
    .stDownloadButton>button {
        background-color: #10b981;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }
    .stDownloadButton>button:hover { background-color: #059669; }
</style>
""", unsafe_allow_html=True)

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

def generate_plots(df):
    figs = []
    num_cols = df.select_dtypes(include=['number']).columns
    for col in num_cols[:3]:
        if df[col].notna().sum() > 0:
            try:
                fig = px.histogram(df, x=col, title=f"{col} Dağılımı", color_discrete_sequence=['#3b82f6'])
                figs.append(fig)
            except:
                pass
    if len(num_cols) >= 2 and df[num_cols].shape[0] > 1:
        try:
            corr = df[num_cols].corr()
            fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns, colorscale='RdBu_r'))
            fig.update_layout(title="Korelasyon Matrisi")
            figs.append(fig)
        except:
            pass
    cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns
    for col in cat_cols[:2]:
        if df[col].notna().sum() > 0:
            try:
                vc = df[col].value_counts().reset_index()
                vc.columns = ['kategori', 'sayi']
                fig = px.bar(vc, x='kategori', y='sayi', title=f"{col} Dağılımı",
                             color_discrete_sequence=['#10b981'])
                figs.append(fig)
            except:
                pass
    return figs

def preprocess_prompt(prompt, file_names):
    """
    Kullanıcı komutundaki dosya tanımlarını df1, df2'ye çevirir.
    """
    replacements = {}
    # Dosya adlarını sırasıyla df1, df2 ile eşleştir
    for i, name in enumerate(file_names, start=1):
        replacements[name] = f"df{i}"
        replacements[f"{i}. dosya"] = f"df{i}"
        replacements[f"{i}.dosya"] = f"df{i}"
        if i == 1:
            replacements["birinci dosya"] = "df1"
            replacements["1. dosyadaki"] = "df1"
            replacements["1. dosyaya"] = "df1"
            replacements["ana dosya"] = "df1"
            replacements["HBA"] = "df1"  # Özel tanım
        elif i == 2:
            replacements["ikinci dosya"] = "df2"
            replacements["2. dosyadaki"] = "df2"
            replacements["2. dosyaya"] = "df2"
            replacements["geçiş dosyası"] = "df2"  # Özel tanım
            replacements["referans dosyası"] = "df2"
    # Büyük-küçük harf duyarsız değiştirme
    for old, new in replacements.items():
        prompt = prompt.replace(old, new)
    # Regex ile değiştirme
    prompt = re.sub(r'\b1\.\s*dosya\b', 'df1', prompt, flags=re.IGNORECASE)
    prompt = re.sub(r'\b2\.\s*dosya\b', 'df2', prompt, flags=re.IGNORECASE)
    return prompt

if 'file_data' not in st.session_state:
    st.session_state.file_data = {}
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'processing' not in st.session_state:
    st.session_state.processing = False

st.title("🤖 AI Veri Asistanı")
st.markdown("**Hiç Excel bilmeyenler için doğal dil ile veri işleme**")

# ==========================
# DOSYA YÜKLEME
# ==========================
with st.container():
    st.subheader("📂 Dosya Yükleme")
    uploaded_files = st.file_uploader(
        "Dosyaları sürükleyin veya seçin",
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
# DOSYA KARTLARI
# ==========================
if st.session_state.file_data:
    st.subheader("📁 Yüklenen Dosyalar")
    cols = st.columns(2)
    for idx, (name, data) in enumerate(st.session_state.file_data.items()):
        with cols[idx % 2]:
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f'<div class="card-title">📄 {name}</div>', unsafe_allow_html=True)
                with col2:
                    if st.button("🗑️", key=f"del_{name}"):
                        del st.session_state.file_data[name]
                        st.rerun()
                if data['sheets']:
                    current_sheet = data['selected_sheet'] if data['selected_sheet'] else data['sheets'][0]
                    selected_sheet = st.selectbox(
                        f"Sayfa seçin",
                        options=data['sheets'],
                        index=data['sheets'].index(current_sheet) if current_sheet in data['sheets'] else 0,
                        key=f"sheet_{name}"
                    )
                    if data['selected_sheet'] != selected_sheet or data['df'] is None:
                        data['selected_sheet'] = selected_sheet
                        data['df'] = load_file(data['bytes'], name, sheet_name=selected_sheet)
                        if data['df'] is not None:
                            st.success(f"✅ {selected_sheet} yüklendi ({data['df'].shape[0]} satır × {data['df'].shape[1]} sütun)")
                else:
                    if data['df'] is None:
                        data['df'] = load_file(data['bytes'], name)
                        if data['df'] is not None:
                            st.success(f"✅ {name} yüklendi")
                if data['df'] is not None:
                    df = data['df']
                    st.caption(f"{df.shape[0]} satır, {df.shape[1]} sütun")
                    with st.expander("🔍 Önizleme"):
                        st.dataframe(df.head(5), width='stretch')
                    with st.expander("📊 Özet İstatistikler"):
                        num_cols = df.select_dtypes(include=['number']).columns
                        if len(num_cols) > 0:
                            st.dataframe(df[num_cols].describe())
                        else:
                            st.info("Sayısal sütun yok")
                    with st.expander("📈 Grafikler"):
                        figs = generate_plots(df)
                        if figs:
                            for fig in figs:
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Grafik oluşturulamadı")
                    col1, col2 = st.columns(2)
                    with col1:
                        excel_data, excel_fname = export_file(df, "xlsx", name.replace('.', '_'))
                        if excel_data:
                            st.download_button("📊 Excel", excel_data, excel_fname, key=f"excel_{name}")
                    with col2:
                        csv_data, csv_fname = export_file(df, "csv", name.replace('.', '_'))
                        if csv_data:
                            st.download_button("📄 CSV", csv_data, csv_fname, key=f"csv_{name}")
                else:
                    st.warning("⚠️ Veri yüklenemedi")
                st.markdown('</div>', unsafe_allow_html=True)

# ==========================
# AI ASİSTANI (SOHBET)
# ==========================
st.markdown("---")
st.header("💬 AI Veri Asistanı ile Sohbet")

if not HAS_GROQ:
    st.warning("Groq kütüphanesi yüklü değil. `pip install groq` ile yükleyin.")
else:
    available_dfs = {name: data['df'] for name, data in st.session_state.file_data.items() if data['df'] is not None}
    if not available_dfs:
        st.info("Lütfen önce yukarıdan dosya yükleyin ve bir sayfa seçin.")
    else:
        # Sohbet geçmişi
        for msg in st.session_state.messages:
            role_class = "user" if msg["role"] == "user" else "assistant"
            st.markdown(f'''
                <div class="chat-message {role_class}">
                    <div class="role">{msg["role"].capitalize()}</div>
                    {msg["content"]}
                </div>
            ''', unsafe_allow_html=True)

        prompt = st.chat_input("Ne yapmak istersiniz? (ör: 'geçiş dosyasındaki anket durum ve detayları, birim numarasına göre HBA dosyasına ekle')")
        if prompt and not st.session_state.processing:
            st.session_state.processing = True
            try:
                file_names = list(available_dfs.keys())
                processed_prompt = preprocess_prompt(prompt, file_names)
                st.session_state.messages.append({"role": "user", "content": processed_prompt})

                api_key = st.secrets.get("GROQ_API_KEY")
                if not api_key:
                    st.error("❌ GROQ_API_KEY eksik")
                    st.session_state.processing = False
                    st.rerun()

                client = Groq(api_key=api_key)

                df_list_str = ", ".join([f"{k}: {list(v.columns)}" for k, v in available_dfs.items()])
                sys_msg = f"""Python/Pandas uzmanısın. Kullanıcının komutunu analiz et.
Mevcut DataFrame'ler:
{df_list_str}

**KULLANICI KOMUTUNDA GEÇEN 'df1', 'df2' DEĞİŞKENLERİNİ DOĞRUDAN KULLAN.**
- df1 = {file_names[0] if len(file_names)>0 else ''}
- df2 = {file_names[1] if len(file_names)>1 else ''}

**KULLANICI DOSYA ADLARINI DEĞİL, SADECE df1, df2, ... DEĞİŞKENLERİNİ KULLANACAK.**
**ASLA DOSYA ADLARINI DEĞİŞKEN OLARAK KULLANMA!**

Eğer komut net değilse veya hangi dosyayı kastettiğini anlamadıysan, JSON formatında:
{{"status": "need_clarification", "question": "Açıklayıcı soru"}}
döndür.

Eğer komut yeterliyse, çalışan Pandas kodunu oluştur ve JSON formatında döndür:
{{"status": "success", "code": "result_df = ...", "explanation": "Kısa açıklama"}}

Kod içinde yorum satırları (#) kullanabilirsin.
Sonucu her zaman 'result_df' değişkenine ata.
Sadece JSON döndür, başka metin yazma.
"""
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": sys_msg},
                        {"role": "user", "content": f"Kullanıcı komutu: {processed_prompt}"}
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                    response_format={"type": "json_object"}
                )
                raw_response = response.choices[0].message.content
                try:
                    data = json.loads(raw_response)
                except json.JSONDecodeError:
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Beklenmeyen yanıt: {raw_response[:200]}"})
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
                    try:
                        local_vars = {}
                        for i, (name, df) in enumerate(available_dfs.items(), start=1):
                            local_vars[f"df{i}"] = df.copy()
                        local_vars["pd"] = pd
                        exec(code, {}, local_vars)
                        result_df = local_vars.get("result_df")
                        if result_df is not None and isinstance(result_df, pd.DataFrame):
                            st.session_state.messages.append({"role": "assistant", "content": f"✅ {explanation}"})
                            with st.chat_message("assistant"):
                                st.write(f"**{explanation}**")
                                st.dataframe(result_df.head(10), width='stretch')
                                col1, col2 = st.columns(2)
                                with col1:
                                    excel_data, excel_fname = export_file(result_df, "xlsx", "ai_sonuc")
                                    if excel_data:
                                        st.download_button("📊 Excel İndir", excel_data, excel_fname, key="ai_excel")
                                with col2:
                                    csv_data, csv_fname = export_file(result_df, "csv", "ai_sonuc")
                                    if csv_data:
                                        st.download_button("📄 CSV İndir", csv_data, csv_fname, key="ai_csv")
                                num_cols = result_df.select_dtypes(include=['number']).columns
                                if len(num_cols) >= 1 and len(result_df) > 0:
                                    st.caption("📈 Otomatik Grafik")
                                    fig = px.histogram(result_df, x=num_cols[0], title="Sonuç Dağılımı")
                                    st.plotly_chart(fig, use_container_width=True)
                            st.session_state.processing = False
                            st.rerun()
                        else:
                            st.session_state.messages.append({"role": "assistant", "content": "⚠️ Kod çalıştı ama 'result_df' oluşturulamadı. Komutunuzu kontrol edin."})
                            st.session_state.processing = False
                            st.rerun()
                    except Exception as e:
                        st.session_state.messages.append({"role": "assistant", "content": f"❌ Kod hatası: {str(e)[:200]}"})
                        st.session_state.processing = False
                        st.rerun()
                else:
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Beklenmeyen yanıt formatı: {raw_response[:200]}"})
                    st.session_state.processing = False
                    st.rerun()
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"❌ Bir hata oluştu: {str(e)[:200]}"})
                st.session_state.processing = False
                st.rerun()

    if st.button("🗑️ Sohbet Geçmişini Temizle"):
        st.session_state.messages = []
        st.rerun()