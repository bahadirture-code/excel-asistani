import streamlit as st
import pandas as pd
import io
import plotly.express as px
from difflib import SequenceMatcher

# Optional libraries (guarded)
try:
    import ydata_profiling
    from streamlit_pandas_profiling import st_profile_report
    HAS_PROFILE = True
except Exception:
    HAS_PROFILE = False

try:
    from groq import Groq
    HAS_GROQ = True
except Exception:
    HAS_GROQ = False

st.set_page_config(page_title="Excel & Veri İşleme", layout="wide", page_icon="⚡")

# ==========================
# HELPERS / CACHE
# ==========================
@st.cache_data(ttl=3600)
def load_file(file_bytes, filename, header_row=0, sheet_name=0):
    try:
        if filename.lower().endswith('.csv'):
            return pd.read_csv(io.BytesIO(file_bytes), header=header_row)
        else:
            return pd.read_excel(io.BytesIO(file_bytes), header=header_row, sheet_name=sheet_name)
    except Exception as e:
        st.error(f"❌ Dosya hatası: {e}")
        return None

def get_excel_sheets(file_bytes):
    try:
        xl = pd.ExcelFile(io.BytesIO(file_bytes))
        return xl.sheet_names
    except Exception:
        return []

def find_similar_columns(col_name, available_cols, threshold=0.7):
    matches = []
    for col in list(available_cols):
        ratio = SequenceMatcher(None, str(col_name).lower(), str(col).lower()).ratio()
        if ratio >= threshold:
            matches.append((col, ratio))
    return sorted(matches, key=lambda x: x[1], reverse=True)

def safe_merge(df_left, df_right, left_key, right_key, how='left'):
    try:
        df_left[left_key] = df_left[left_key].astype(str).str.strip()
        df_right[right_key] = df_right[right_key].astype(str).str.strip()
        return pd.merge(df_left, df_right, left_on=left_key, right_on=right_key, how=how, suffixes=('_x', '_y'))
    except Exception as e:
        st.error(f"❌ Merge hatası: {e}")
        return None

def export_file(df, format_type="xlsx", filename="output"):
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
        st.error(f"❌ Export hatası: {e}")
        return None, None

st.title("⚡ Excel & Veri İşleme Platformu")
st.markdown("**Ücretsiz** - Merge, Temizleme, Profil Analizi, Groq AI")

# ==========================
# SEKMELER (TABS)
# ==========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Excel Eşleştirme",
    "🔗 DÜŞEYARA",
    "🛠️ Temizleme",
    "📑 Veri Profili",
    "🤖 Groq AI (Doğal Dil)"
])

# ==========================================
# TAB 1: EXCEL EŞLEŞTİRME + GRAFİK
# ==========================================
with tab1:
    st.header("📋 Excel Eşleştirme")
    col1, col2 = st.columns(2)
    with col1:
        file_ana = st.file_uploader("Dosya 1", type=["xlsx", "csv"], key="f1")
        if file_ana:
            header_ana = st.number_input("Dosya 1 Başlık Satırı (0'dan başlar)", min_value=0, value=0, step=1, key="h1")
            if file_ana.name.lower().endswith('.xlsx'):
                sheets = get_excel_sheets(file_ana.read())
                if sheets:
                    sheet_ana = st.selectbox("Dosya 1 Sayfa (Sheet)", sheets, index=0, key="s1")
                else:
                    sheet_ana = 0
            else:
                sheet_ana = 0
    with col2:
        file_gecis = st.file_uploader("Dosya 2", type=["xlsx", "csv"], key="f2")
        if file_gecis:
            header_gecis = st.number_input("Dosya 2 Başlık Satırı (0'dan başlar)", min_value=0, value=0, step=1, key="h2")
            if file_gecis.name.lower().endswith('.xlsx'):
                sheets = get_excel_sheets(file_gecis.read())
                if sheets:
                    sheet_gecis = st.selectbox("Dosya 2 Sayfa (Sheet)", sheets, index=0, key="s2")
                else:
                    sheet_gecis = 0
            else:
                sheet_gecis = 0

    if file_ana and file_gecis:
        df_ana = load_file(file_ana.read(), file_ana.name, header_row=header_ana, sheet_name=sheet_ana)
        df_gecis = load_file(file_gecis.read(), file_gecis.name, header_row=header_gecis, sheet_name=sheet_gecis)

        if df_ana is not None and df_gecis is not None:
            k_ana = st.selectbox("Dosya 1 Sütunu", df_ana.columns)
            similar = find_similar_columns(k_ana, df_gecis.columns)
            k_gecis_default = similar[0][0] if similar else df_gecis.columns[0]
            k_gecis = st.selectbox("Dosya 2 Sütunu", df_gecis.columns,
                                   index=list(df_gecis.columns).index(k_gecis_default))

            if st.button("🚀 Eşleştir"):
                df_merged = safe_merge(df_ana.copy(), df_gecis.copy(), k_ana, k_gecis, how='left')
                if df_merged is not None:
                    st.success("✅ Tamamlandı!")
                    st.dataframe(df_merged.head(20))

                    st.subheader("📊 Görselleştirme")
                    num_cols = df_merged.select_dtypes(include='number').columns
                    if len(num_cols) >= 2:
                        x_col = st.selectbox("X ekseni", num_cols, index=0, key="xcol")
                        y_col = st.selectbox("Y ekseni", num_cols, index=1, key="ycol")
                        color_col_options = [c for c in df_merged.columns]
                        color_col = st.selectbox("Renk (isteğe bağlı)", ["-"] + color_col_options, index=0, key="colorcol")
                        if color_col == "-":
                            fig = px.scatter(df_merged, x=x_col, y=y_col)
                        else:
                            fig = px.scatter(df_merged, x=x_col, y=y_col, color=color_col)
                        st.plotly_chart(fig, use_container_width=True)

                    c1, c2 = st.columns(2)
                    with c1:
                        data, fname = export_file(df_merged, "xlsx", "sonuc")
                        if data:
                            st.download_button("📊 Excel", data, fname, key="m_excel")
                    with c2:
                        data, fname = export_file(df_merged, "csv", "sonuc")
                        if data:
                            st.download_button("📄 CSV", data, fname, key="m_csv")

# ==========================================
# TAB 2: DÜŞEYARA
# ==========================================
with tab2:
    st.header("🔗 DÜŞEYARA")
    col1, col2 = st.columns(2)
    with col1:
        file_main = st.file_uploader("Ana Dosya", type=["xlsx", "csv"], key="main")
        if file_main:
            header_main = st.number_input("Ana Dosya Başlık Satırı (0'dan başlar)", min_value=0, value=0, step=1, key="hm")
            if file_main.name.lower().endswith('.xlsx'):
                sheets = get_excel_sheets(file_main.read())
                if sheets:
                    sheet_main = st.selectbox("Ana Dosya Sayfa (Sheet)", sheets, index=0, key="sm")
                else:
                    sheet_main = 0
            else:
                sheet_main = 0
    with col2:
        file_ref = st.file_uploader("Referans Dosya", type=["xlsx", "csv"], key="ref")
        if file_ref:
            header_ref = st.number_input("Referans Dosya Başlık Satırı (0'dan başlar)", min_value=0, value=0, step=1, key="hr")
            if file_ref.name.lower().endswith('.xlsx'):
                sheets = get_excel_sheets(file_ref.read())
                if sheets:
                    sheet_ref = st.selectbox("Referans Dosya Sayfa (Sheet)", sheets, index=0, key="sr")
                else:
                    sheet_ref = 0
            else:
                sheet_ref = 0

    if file_main and file_ref:
        df_m = load_file(file_main.read(), file_main.name, header_row=header_main, sheet_name=sheet_main)
        df_r = load_file(file_ref.read(), file_ref.name, header_row=header_ref, sheet_name=sheet_ref)

        if df_m is not None and df_r is not None:
            key_m = st.selectbox("Ana Dosya Sütunu", df_m.columns)
            similar = find_similar_columns(key_m, df_r.columns)
            key_r_default = similar[0][0] if similar else df_r.columns[0]
            key_r = st.selectbox("Referans Sütunu", df_r.columns,
                                 index=list(df_r.columns).index(key_r_default))

            target_cols = st.multiselect("Çekilecek Sütunlar",
                                         [c for c in df_r.columns if c != key_r])

            if st.button("🔗 Birleştir"):
                sub_r = df_r[[key_r] + target_cols].drop_duplicates(subset=[key_r])
                res = safe_merge(df_m.copy(), sub_r, key_m, key_r, how='left')
                if res is not None:
                    st.success("✅ Birleştirme tamamlandı")
                    st.dataframe(res.head(20))
                    c1, c2 = st.columns(2)
                    with c1:
                        data, fname = export_file(res, "xlsx", "birlestirilmis")
                        if data:
                            st.download_button("📊 Excel", data, fname, key="v_excel")
                    with c2:
                        data, fname = export_file(res, "csv", "birlestirilmis")
                        if data:
                            st.download_button("📄 CSV", data, fname, key="v_csv")

# ==========================================
# TAB 3: GELİŞMİŞ TEMİZLEME
# ==========================================
with tab3:
    st.header("🛠️ Veri Temizleme")
    file_clean = st.file_uploader("Temizlenecek Dosya", type=["xlsx", "csv"], key="clean")
    if file_clean:
        header_clean = st.number_input("Başlık Satırı (0'dan başlar)", min_value=0, value=0, step=1, key="hc")
        if file_clean.name.lower().endswith('.xlsx'):
            sheets = get_excel_sheets(file_clean.read())
            if sheets:
                sheet_clean = st.selectbox("Sayfa (Sheet)", sheets, index=0, key="sc")
            else:
                sheet_clean = 0
        else:
            sheet_clean = 0

        df_c = load_file(file_clean.read(), file_clean.name, header_row=header_clean, sheet_name=sheet_clean)

        if df_c is not None:
            st.write(f"Boyut: **{len(df_c)}** satır × **{len(df_c.columns)}** sütun")
            op = st.selectbox("İşlem", [
                "Mükerrer Satırları Sil",
                "Belirli Sütuna Göre Mükerrerleri Sil",
                "Boşlukları Temizle (TRIM)",
                "BÜYÜK HARFE Çevir",
                "Boş Satırları Sil",
                "Özel Karakterleri Sil",
                "Tarih Formatlarını Standartlaştır"
            ])

            selected_col = None
            if op == "Belirli Sütuna Göre Mükerrerleri Sil":
                selected_col = st.selectbox("Sütun Seç", df_c.columns)

            if st.button("⚡ Uygula"):
                if op == "Mükerrer Satırları Sil":
                    df_c = df_c.drop_duplicates()
                elif op == "Belirli Sütuna Göre Mükerrerleri Sil" and selected_col:
                    df_c = df_c.drop_duplicates(subset=[selected_col])
                elif op == "Boşlukları Temizle (TRIM)":
                    for col in df_c.select_dtypes(include=['object']).columns:
                        df_c[col] = df_c[col].astype(str).str.strip()
                elif op == "BÜYÜK HARFE Çevir":
                    for col in df_c.select_dtypes(include=['object']).columns:
                        df_c[col] = df_c[col].astype(str).str.upper()
                elif op == "Boş Satırları Sil":
                    df_c = df_c.dropna(how='all')
                elif op == "Özel Karakterleri Sil":
                    for col in df_c.select_dtypes(include=['object']).columns:
                        df_c[col] = df_c[col].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
                elif op == "Tarih Formatlarını Standartlaştır":
                    for col in df_c.select_dtypes(include=['object']).columns:
                        try:
                            parsed = pd.to_datetime(df_c[col], errors='coerce')
                            if parsed.notna().any():
                                df_c[col] = pd.to_datetime(df_c[col], errors='coerce').dt.strftime('%Y-%m-%d')
                        except Exception:
                            pass

                st.success("✅ Tamamlandı!")
                st.dataframe(df_c.head(15))

                c1, c2 = st.columns(2)
                with c1:
                    data, fname = export_file(df_c, "xlsx", "temizlenmis")
                    if data:
                        st.download_button("📊 Excel", data, fname, key="c1")
                with c2:
                    data, fname = export_file(df_c, "csv", "temizlenmis")
                    if data:
                        st.download_button("📄 CSV", data, fname, key="c2")

# ==========================================
# TAB 4: VERİ PROFİLİ
# ==========================================
with tab4:
    st.header("📑 Veri Profili")
    if not HAS_PROFILE:
        st.info("Profil analizi için 'ydata-profiling' ve 'streamlit-pandas-profiling' kütüphaneleri gerekli. requirements.txt'e ekleyip yükleyin.")
    file_profile = st.file_uploader("Profil Analizi Dosyası", type=["xlsx", "csv"], key="profile")
    if file_profile:
        header_profile = st.number_input("Başlık Satırı (0'dan başlar)", min_value=0, value=0, step=1, key="hp")
        if file_profile.name.lower().endswith('.xlsx'):
            sheets = get_excel_sheets(file_profile.read())
            if sheets:
                sheet_profile = st.selectbox("Sayfa (Sheet)", sheets, index=0, key="sp")
            else:
                sheet_profile = 0
        else:
            sheet_profile = 0

        df_p = load_file(file_profile.read(), file_profile.name, header_row=header_profile, sheet_name=sheet_profile)

        if df_p is not None:
            st.write(f"Boyut: **{len(df_p)}** satır × **{len(df_p.columns)}** sütun")
            if HAS_PROFILE:
                with st.spinner("Profil raporu oluşturuluyor..."):
                    profile = ydata_profiling.ProfileReport(df_p, title="Veri Profili", explorative=True)
                    st_profile_report(profile)
            else:
                st.warning("Profil raporu oluşturulamıyor. Gerekli paketler kurulu değil.")

# ==========================================
# TAB 5: GROQ AI (DOĞAL DİL ASİSTANI)
# ==========================================
with tab5:
    st.header("🤖 Veri Asistanı (Groq ile Doğal Dil)")
    st.markdown("""
    **Nasıl çalışır?**  
    1. Dosyalarınızı yükleyin (isteğe bağlı, bir veya iki dosya).  
    2. Ne yapmak istediğinizi Türkçe veya İngilizce doğal dilde yazın.  
    3. Groq, isteğinize uygun Pandas kodunu oluşturup çalıştıracak ve sonucu size sunacaktır.  
    """)

    if not HAS_GROQ:
        st.warning("Groq kütüphanesi yüklü değil. `requirements.txt`'e `groq` ekleyip yeniden deploy edin.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            f1 = st.file_uploader("Dosya 1 (df1)", type=["xlsx", "csv"], key="ai1")
            if f1:
                h1 = st.number_input("df1 Başlık Satırı", min_value=0, value=0, step=1, key="aih1")
                if f1.name.lower().endswith('.xlsx'):
                    sheets = get_excel_sheets(f1.read())
                    if sheets:
                        sheet1 = st.selectbox("df1 Sayfa (Sheet)", sheets, index=0, key="ais1")
                    else:
                        sheet1 = 0
                else:
                    sheet1 = 0
        with col2:
            f2 = st.file_uploader("Dosya 2 (df2)", type=["xlsx", "csv"], key="ai2")
            if f2:
                h2 = st.number_input("df2 Başlık Satırı", min_value=0, value=0, step=1, key="aih2")
                if f2.name.lower().endswith('.xlsx'):
                    sheets = get_excel_sheets(f2.read())
                    if sheets:
                        sheet2 = st.selectbox("df2 Sayfa (Sheet)", sheets, index=0, key="ais2")
                    else:
                        sheet2 = 0
                else:
                    sheet2 = 0

        df1 = load_file(f1.read(), f1.name, header_row=h1, sheet_name=sheet1) if f1 else None
        df2 = load_file(f2.read(), f2.name, header_row=h2, sheet_name=sheet2) if f2 else None

        if df1 is not None:
            st.write("**df1 Sütunları:**", list(df1.columns))
            if df2 is not None:
                st.write("**df2 Sütunları:**", list(df2.columns))

            user_prompt = st.text_area("📝 Ne yapmak istiyorsunuz? (örn: 'df1'deki satışların ortalamasını al, 'df2' ile birleştir ve 'toplam' sütunu ekle)")

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
df1: {list(df1.columns)}{f", df2: {list(df2.columns)}" if df2 is not None else ""}
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

                                local_vars = {"df1": df1.copy(), "df2": df2.copy() if df2 is not None else None, "pd": pd}
                                exec(code_clean, {}, local_vars)
                                result_df = local_vars.get("result_df")

                                if result_df is not None and isinstance(result_df, pd.DataFrame):
                                    st.success("✅ İşlem başarıyla tamamlandı!")
                                    st.dataframe(result_df.head(20))
                                    with st.expander("🛠️ Oluşturulan Kod"):
                                        st.code(code_clean, language="python")

                                    col1, col2 = st.columns(2)
                                    with col1:
                                        data, fname = export_file(result_df, "xlsx", "groq_sonuc")
                                        if data:
                                            st.download_button("📊 Excel İndir", data, fname, key="g1")
                                    with col2:
                                        data, fname = export_file(result_df, "csv", "groq_sonuc")
                                        if data:
                                            st.download_button("📄 CSV İndir", data, fname, key="g2")
                                else:
                                    st.error("❌ Kod çalıştı ama 'result_df' DataFrame'i oluşturulamadı. Lütfen komutunuzu kontrol edin.")
                    except Exception as e:
                        st.error(f"❌ Bir hata oluştu: {str(e)[:300]}")