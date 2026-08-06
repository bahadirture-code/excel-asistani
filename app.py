import streamlit as st
import pandas as pd
import io

try:
    from groq import Groq
    HAS_GROQ = True
except Exception:
    HAS_GROQ = False

st.set_page_config(page_title="Çoklu Excel + AI", layout="wide", page_icon="📂")

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
        # ExcelFile'a BytesIO olarak ver
        xl = pd.ExcelFile(io.BytesIO(file_bytes), engine='openpyxl')
        return xl.sheet_names
    except Exception as e:
        st.error(f"Sayfalar okunamadı: {e}")
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
    st.session_state.file_data = {}  # {dosya_adı: {'bytes': bytes, 'sheets': list, 'selected_sheet': str, 'df': DataFrame}}

st.title("📂 Çoklu Dosya Yükleme + 🤖 AI Asistanı")
st.markdown("Excel/CSV yükleyin, sayfa seçin, veriyi inceleyin ve AI ile sorgulayın.")

# ==========================
# DOSYA YÜKLEME
# ==========================
uploaded_files = st.file_uploader(
    "Dosyaları yükleyin",
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
                    selected_sheet = sheets[0]  # varsayılan ilk sayfa
                else:
                    st.warning(f"⚠️ {file.name} için sayfa bulunamadı veya okunamadı.")
            st.session_state.file_data[file.name] = {
                'bytes': file_bytes,
                'sheets': sheets,
                'selected_sheet': selected_sheet,
                'df': None
            }

# ==========================
# HER DOSYA İÇİN SAYFA SEÇİMİ VE VERİ YÜKLEME
# ==========================
if st.session_state.file_data:
    st.subheader("📁 Yüklenen Dosyalar - Her dosyanın altından sayfa seçin")
    for name, data in st.session_state.file_data.items():
        with st.expander(f"📄 {name}", expanded=True):  # expanded=True ile otomatik aç
            # Sayfa seçimi (sadece Excel için)
            if data['sheets']:
                # Mevcut seçili sayfayı bul
                current_sheet = data['selected_sheet'] if data['selected_sheet'] else data['sheets'][0]
                selected_sheet = st.selectbox(
                    f"📑 Sayfa seçin ({name})",
                    options=data['sheets'],
                    index=data['sheets'].index(current_sheet) if current_sheet in data['sheets'] else 0,
                    key=f"sheet_{name}"
                )
                # Eğer seçili sayfa değiştiyse veya df henüz yüklenmemişse yeniden yükle
                if data['selected_sheet'] != selected_sheet or data['df'] is None:
                    data['selected_sheet'] = selected_sheet
                    data['df'] = load_file(data['bytes'], name, sheet_name=selected_sheet)
                    if data['df'] is not None:
                        st.success(f"✅ {name} - '{selected_sheet}' sayfası yüklendi ({data['df'].shape[0]} satır × {data['df'].shape[1]} sütun)")
                    else:
                        st.error(f"❌ {name} - '{selected_sheet}' yüklenemedi.")
            else:
                # CSV dosyası veya Excel'de sayfa yoksa direkt yükle
                if data['df'] is None:
                    data['df'] = load_file(data['bytes'], name)
                    if data['df'] is not None:
                        st.success(f"✅ {name} yüklendi ({data['df'].shape[0]} satır × {data['df'].shape[1]} sütun)")

            # Veriyi göster
            if data['df'] is not None:
                st.dataframe(data['df'].head(10), use_container_width=True)
                col1, col2 = st.columns(2)
                with col1:
                    excel_data, excel_fname = export_file(data['df'], "xlsx", name.replace('.', '_'))
                    if excel_data:
                        st.download_button(f"📊 {name} Excel indir", excel_data, excel_fname, key=f"excel_{name}")
                with col2:
                    csv_data, csv_fname = export_file(data['df'], "csv", name.replace('.', '_'))
                    if csv_data:
                        st.download_button(f"📄 {name} CSV indir", csv_data, csv_fname, key=f"csv_{name}")
            else:
                st.warning(f"⚠️ {name} için veri yüklenemedi. Lütfen başka bir sayfa seçmeyi deneyin.")

# ==========================
# GROQ AI ASİSTANI
# ==========================
st.markdown("---")
st.header("🤖 Veri Asistanı (Groq ile Doğal Dil)")

if not HAS_GROQ:
    st.warning("Groq kütüphanesi yüklü değil. `pip install groq` ile yükleyin.")
else:
    # Yüklenmiş ve df'i olan dosyaları filtrele
    available_dfs = {name: data['df'] for name, data in st.session_state.file_data.items() if data['df'] is not None}
    if not available_dfs:
        st.info("Önce yukarıdan dosya yükleyin ve bir sayfa seçin.")
    else:
        secili_dosyalar = st.multiselect(
            "Hangi dosyaları kullanmak istersiniz? (birden fazla seçebilirsiniz)",
            options=list(available_dfs.keys()),
            default=list(available_dfs.keys())[:2] if len(available_dfs) >= 2 else list(available_dfs.keys())
        )

        if secili_dosyalar:
            # Seçilen dosyaları df1, df2, ... olarak hazırla
            df_dict = {}
            for idx, name in enumerate(secili_dosyalar, start=1):
                df_dict[f"df{idx}"] = available_dfs[name].copy()

            # Kullanıcıya sütun bilgilerini göster
            st.write("**Seçilen dosyalar ve sütunları:**")
            for name in secili_dosyalar:
                sheet_name = st.session_state.file_data[name].get('selected_sheet', 'CSV')
                st.write(f"- **{name}** (sayfa: {sheet_name}): {list(available_dfs[name].columns)}")

            user_prompt = st.text_area(
                "📝 Ne yapmak istiyorsunuz? (Türkçe veya İngilizce)",
                placeholder="Örnek: df1'deki 'satis' sütununun ortalamasını al, df2 ile birleştir ve sonucu göster."
            )

            if st.button("🚀 Çalıştır"):
                if not user_prompt.strip():
                    st.warning("Lütfen bir komut yazın.")
                else:
                    try:
                        api_key = st.secrets.get("GROQ_API_KEY")
                        if not api_key:
                            st.error("❌ GROQ_API_KEY eksik. Streamlit Secrets'a ekleyin.")
                        else:
                            with st.spinner("⏳ Groq ile iletişim kuruluyor..."):
                                client = Groq(api_key=api_key)
                                df_list_str = ", ".join([f"{k}: {list(v.columns)}" for k, v in df_dict.items()])
                                sys_msg = f"""Python Pandas uzmanısın.
Mevcut DataFrame'ler:
{df_list_str}

Sadece çalışan Python kodu döndür. Sonucu 'result_df' değişkenine ata.
Kod bloğunu ```python ``` etiketleri arasına yaz.
Örnek:
```python
result_df = df1.groupby('kategori').agg({'satis': 'sum'})
```"""
                                response = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=[
                                        {"role": "system", "content": sys_msg},
                                        {"role": "user", "content": user_prompt}
                                    ],
                                    temperature=0.3,
                                    max_tokens=1500
                                )
                                code_res = response.choices[0].message.content
                                if "```python" in code_res:
                                    code_clean = code_res.split("```python")[1].split("```")[0].strip()
                                else:
                                    code_clean = code_res.strip()

                                local_vars = {**df_dict, "pd": pd}
                                exec(code_clean, {}, local_vars)
                                result_df = local_vars.get("result_df")

                                if result_df is not None and isinstance(result_df, pd.DataFrame):
                                    st.success("✅ İşlem başarıyla tamamlandı!")
                                    st.dataframe(result_df.head(20), use_container_width=True)
                                    with st.expander("🛠️ Oluşturulan Kod"):
                                        st.code(code_clean, language="python")

                                    col1, col2 = st.columns(2)
                                    with col1:
                                        data, fname = export_file(result_df, "xlsx", "ai_sonuc")
                                        if data:
                                            st.download_button("📊 Excel İndir", data, fname, key="ai_excel")
                                    with col2:
                                        data, fname = export_file(result_df, "csv", "ai_sonuc")
                                        if data:
                                            st.download_button("📄 CSV İndir", data, fname, key="ai_csv")
                                else:
                                    st.error("❌ Kod çalıştı ama 'result_df' DataFrame'i oluşturulamadı. Lütfen komutunuzu kontrol edin.")
                    except Exception as e:
                        st.error(f"❌ Bir hata oluştu: {str(e)[:300]}")