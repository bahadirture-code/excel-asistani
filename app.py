import streamlit as st
import pandas as pd
import io

# Groq kontrolü
try:
    from groq import Groq
    HAS_GROQ = True
except Exception:
    HAS_GROQ = False

st.set_page_config(page_title="Veri Asistanı (Groq)", layout="wide", page_icon="🤖")

# Yardımcı fonksiyonlar
@st.cache_data(ttl=3600)
def load_file(file_bytes, filename, sheet_name=0):
    try:
        if filename.lower().endswith('.csv'):
            return pd.read_csv(io.BytesIO(file_bytes))
        else:
            return pd.read_excel(io.BytesIO(file_bytes), header=0, sheet_name=sheet_name, engine='openpyxl')
    except Exception as e:
        st.error(f"❌ Dosya hatası: {e}")
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

st.title("🤖 Veri Asistanı (Groq ile Doğal Dil)")
st.markdown("""
**Nasıl çalışır?**  
1. Dosyanızı yükleyin (Excel veya CSV).  
2. İlgili sayfayı seçin (Excel ise).  
3. Veriniz üzerinde yapmak istediğiniz işlemi Türkçe veya İngilizce doğal dilde yazın.  
4. Groq, isteğinize uygun Pandas kodunu oluşturup çalıştıracak ve sonucu size gösterecektir.  
""")

if not HAS_GROQ:
    st.warning("Groq kütüphanesi yüklü değil. `requirements.txt`'e `groq` ekleyip yeniden deploy edin.")
    st.stop()

# Dosya yükleme
file = st.file_uploader("Dosya yükleyin", type=["xlsx", "csv"], key="dosya")

if file:
    file_bytes = file.read()
    sheet_name = 0
    if file.name.lower().endswith('.xlsx'):
        sheets = get_excel_sheets(file_bytes)
        if sheets:
            sheet_name = st.selectbox("Sayfa seçin", sheets, index=0)
        else:
            st.error("Sayfalar okunamadı.")
            st.stop()

    df = load_file(file_bytes, file.name, sheet_name=sheet_name)

    if df is not None:
        st.success(f"✅ Veri başarıyla yüklendi. Boyut: {df.shape[0]} satır × {df.shape[1]} sütun")
        st.write("**Sütunlar:**", list(df.columns))
        st.dataframe(df.head(10), use_container_width=True)

        # Kullanıcıdan doğal dil komutu
        user_prompt = st.text_area("📝 Ne yapmak istiyorsunuz? (örnek: 'ortalama satışı hesapla', 'yaşa göre grupla ve say')")

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
                            sys_msg = f"""Python Pandas uzmanısın.
df: {list(df.columns)}
Sadece çalışan Python kodu döndür. Sonucu 'result_df' değişkenine ata.
Kod bloğunu ```python ``` etiketleri arasına yaz.
Örnek:
```python
result_df = df.groupby('kategori').agg({'satis': 'sum'})
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

                            local_vars = {"df": df.copy(), "pd": pd}
                            exec(code_clean, {}, local_vars)
                            result_df = local_vars.get("result_df")

                            if result_df is not None and isinstance(result_df, pd.DataFrame):
                                st.success("✅ İşlem başarıyla tamamlandı!")
                                st.dataframe(result_df.head(20), use_container_width=True)
                                with st.expander("🛠️ Oluşturulan Kod"):
                                    st.code(code_clean, language="python")

                                col1, col2 = st.columns(2)
                                with col1:
                                    data, fname = export_file(result_df, "xlsx", "groq_sonuc")
                                    if data:
                                        st.download_button("📊 Excel İndir", data, fname, key="g_excel")
                                with col2:
                                    data, fname = export_file(result_df, "csv", "groq_sonuc")
                                    if data:
                                        st.download_button("📄 CSV İndir", data, fname, key="g_csv")
                            else:
                                st.error("❌ Kod çalıştı ama 'result_df' DataFrame'i oluşturulamadı. Lütfen komutunuzu kontrol edin.")
                except Exception as e:
                    st.error(f"❌ Bir hata oluştu: {str(e)[:300]}")