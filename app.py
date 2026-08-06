import streamlit as st
import pandas as pd
import io

try:
    from groq import Groq
    HAS_GROQ = True
except Exception:
    HAS_GROQ = False

st.set_page_config(page_title="Çoklu Dosya Yükleme + AI", layout="wide", page_icon="📂")

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
# OTURUM DURUMU (SESSION STATE)
# ==========================
if 'dfs' not in st.session_state:
    st.session_state.dfs = {}  # {dosya_adı: DataFrame}
if 'file_bytes' not in st.session_state:
    st.session_state.file_bytes = {}  # {dosya_adı: bytes}

st.title("📂 Çoklu Dosya Yükleme + 🤖 AI Asistanı")
st.markdown("Birden fazla Excel/CSV yükleyin, önizleyin ve yapay zeka ile sorgulayın.")

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
        if file.name not in st.session_state.dfs:
            file_bytes = file.read()
            st.session_state.file_bytes[file.name] = file_bytes

            # Excel ise ilk sayfayı al (isteğe bağlı: sheet seçimi eklenebilir)
            if file.name.lower().endswith('.xlsx'):
                sheets = get_excel_sheets(file_bytes)
                if sheets:
                    # Varsayılan olarak ilk sayfayı al
                    df = load_file(file_bytes, file.name, sheet_name=sheets[0])
                else:
                    df = None
            else:
                df = load_file(file_bytes, file.name)

            if df is not None:
                st.session_state.dfs[file.name] = df
                st.success(f"✅ {file.name} yüklendi (satır: {df.shape[0]}, sütun: {df.shape[1]})")
            else:
                st.error(f"❌ {file.name} yüklenemedi.")

# ==========================
# YÜKLENEN DOSYALARI LİSTELE VE ÖNİZLE
# ==========================
if st.session_state.dfs:
    st.subheader("📁 Yüklenen Dosyalar")
    for name, df in st.session_state.dfs.items():
        with st.expander(f"📄 {name} ({df.shape[0]} satır × {df.shape[1]} sütun)"):
            st.dataframe(df.head(10), use_container_width=True)
            col1, col2 = st.columns(2)
            with col1:
                excel_data, excel_fname = export_file(df, "xlsx", name.replace('.', '_'))
                if excel_data:
                    st.download_button(f"📊 {name} Excel indir", excel_data, excel_fname, key=f"excel_{name}")
            with col2:
                csv_data, csv_fname = export_file(df, "csv", name.replace('.', '_'))
                if csv_data:
                    st.download_button(f"📄 {name} CSV indir", csv_data, csv_fname, key=f"csv_{name}")

# ==========================
# GROQ AI ASİSTANI
# ==========================
st.markdown("---")
st.header("🤖 Veri Asistanı (Groq ile Doğal Dil)")

if not HAS_GROQ:
    st.warning("Groq kütüphanesi yüklü değil. `pip install groq` ile yükleyin.")
else:
    if not st.session_state.dfs:
        st.info("Önce yukarıdan dosya yükleyin.")
    else:
        # Kullanıcının hangi dosyaları kullanacağını seçmesi
        secili_dosyalar = st.multiselect(
            "Hangi dosyaları kullanmak istersiniz? (birden fazla seçebilirsiniz)",
            options=list(st.session_state.dfs.keys()),
            default=list(st.session_state.dfs.keys())[:2] if len(st.session_state.dfs) >= 2 else list(st.session_state.dfs.keys())
        )

        if secili_dosyalar:
            # Seçilen dosyaları df1, df2, ... olarak hazırla
            df_dict = {}
            for idx, name in enumerate(secili_dosyalar, start=1):
                df_dict[f"df{idx}"] = st.session_state.dfs[name].copy()

            # Kullanıcıya sütun bilgilerini göster
            st.write("**Seçilen dosyalar ve sütunları:**")
            for name in secili_dosyalar:
                st.write(f"- **{name}**: {list(st.session_state.dfs[name].columns)}")

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
                                # Sistem mesajında mevcut df'leri bildir
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

                                # Kod çalıştır
                                local_vars = {**df_dict, "pd": pd}
                                exec(code_clean, {}, local_vars)
                                result_df = local_vars.get("result_df")

                                if result_df is not None and isinstance(result_df, pd.DataFrame):
                                    st.success("✅ İşlem başarıyla tamamlandı!")
                                    st.dataframe(result_df.head(20), use_container_width=True)
                                    with st.expander("🛠️ Oluşturulan Kod"):
                                        st.code(code_clean, language="python")

                                    # Sonucu indir
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