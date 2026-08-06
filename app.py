import streamlit as st
import pandas as pd
import io
import plotly.express as px
from difflib import SequenceMatcher
import ydata_profiling
from streamlit_pandas_profiling import st_profile_report

st.set_page_config(page_title="Excel & Veri İşleme", layout="wide", page_icon="⚡")

# ==========================
# CACHE OPTİMİZASYONU
# ==========================
@st.cache_data(ttl=3600)
def load_file(file_bytes, filename):
    try:
        if filename.endswith('.csv'):
            return pd.read_csv(io.BytesIO(file_bytes))
        else:
            return pd.read_excel(io.BytesIO(file_bytes))
    except Exception as e:
        st.error(f"❌ Dosya hatası: {e}")
        return None

@st.cache_data
def find_similar_columns(col_name, available_cols, threshold=0.7):
    matches = []
    for col in available_cols:
        ratio = SequenceMatcher(None, col_name.lower(), col.lower()).ratio()
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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Excel Eşleştirme", 
    "🔗 DÜŞEYARA", 
    "🛠️ Temizleme",
    "📑 Veri Profili",
    "🤖 Groq AI"
])

# ==========================================
# TAB 1: EXCEL EŞLEŞTİRME + GRAFİK
# ==========================================
with tab1:
    st.header("📋 Excel Eşleştirme")
    col1, col2 = st.columns(2)
    with col1:
        file_ana = st.file_uploader("Dosya 1", type=["xlsx", "csv"], key="f1")
    with col2:
        file_gecis = st.file_uploader("Dosya 2", type=["xlsx", "csv"], key="f2")

    if file_ana and file_gecis:
        df_ana = load_file(file_ana.read(), file_ana.name)
        df_gecis = load_file(file_gecis.read(), file_gecis.name)
        
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

                    # 📊 Grafik Görselleştirme
                    st.subheader("📊 Görselleştirme")
                    num_cols = df_merged.select_dtypes(include='number').columns
                    if len(num_cols) >= 2:
                        fig = px.scatter(df_merged, x=num_cols[0], y=num_cols[1], color=k_ana)
                        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 2: DÜŞEYARA
# ==========================================
with tab2:
    st.header("🔗 DÜŞEYARA")
    file_main = st.file_uploader("Ana Dosya", type=["xlsx", "csv"], key="main")
    file_ref = st.file_uploader("Referans Dosya", type=["xlsx", "csv"], key="ref")
    
    if file_main and file_ref:
        df_m = load_file(file_main.read(), file_main.name)
        df_r = load_file(file_ref.read(), file_ref.name)
        
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
                    st.dataframe(res.head(20))

# ==========================================
# TAB 3: GELİŞMİŞ TEMİZLEME
# ==========================================
with tab3:
    st.header("🛠️ Veri Temizleme")
    file_clean = st.file_uploader("Temizlenecek Dosya", type=["xlsx", "csv"], key="clean")
    
    if file_clean:
        df_c = load_file(file_clean.read(), file_clean.name)
        if df_c is not None:
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
                            df_c[col] = pd.to_datetime(df_c[col], errors='ignore').dt.strftime('%Y-%m-%d')
                        except Exception:
                            pass

                st.success("✅ Tamamlandı!")
                st.dataframe(df_c.head(15))

# ==========================================
# TAB 4: VERİ PROFİLİ
# ==========================================
with tab4:
    st.header("📑 Veri Profili")
    file_profile = st.file_uploader("Profil Analizi Dosyası", type=["xlsx