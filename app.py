import streamlit as st
import pandas as pd
import io
import plotly.express as px
from difflib import SequenceMatcher
import os

st.set_page_config(page_title="Akıllı Excel & Veri İşleme Platformu", layout="wide", page_icon="⚡")

# ==========================================
# CACHING & PERFORMANCE
# ==========================================
@st.cache_data(ttl=3600)
def load_file(file_bytes, filename):
    """Dosya yükleme ve cache'leme"""
    try:
        if filename.endswith('.csv'):
            return pd.read_csv(io.BytesIO(file_bytes))
        else:
            return pd.read_excel(io.BytesIO(file_bytes))
    except Exception as e:
        st.error(f"❌ Dosya yükleme hatası: {e}")
        return None

@st.cache_data
def find_similar_columns(col_name, available_cols, threshold=0.7):
    """Benzer sütun adlarını bul (Fuzzy Matching)"""
    matches = []
    for col in available_cols:
        ratio = SequenceMatcher(None, col_name.lower(), col.lower()).ratio()
        if ratio >= threshold:
            matches.append((col, ratio))
    return sorted(matches, key=lambda x: x[1], reverse=True)

def safe_merge(df_left, df_right, left_key, right_key, how='left'):
    """Güvenli merge işlemi"""
    try:
        df_left[left_key] = df_left[left_key].astype(str).str.strip()
        df_right[right_key] = df_right[right_key].astype(str).str.strip()
        return pd.merge(df_left, df_right, left_on=left_key, right_on=right_key, how=how, suffixes=('_x', '_y'))
    except Exception as e:
        st.error(f"❌ Merge hatası: {e}")
        return None

def export_file(df, format_type="xlsx", filename="output"):
    """Çoklu format export"""
    output = io.BytesIO()
    
    try:
        if format_type == "xlsx":
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            return output.getvalue(), f"{filename}.xlsx"
        elif format_type == "csv":
            output.write(df.to_csv(index=False).encode())
            return output.getvalue(), f"{filename}.csv"
        elif format_type == "parquet":
            df.to_parquet(output)
            return output.getvalue(), f"{filename}.parquet"
    except Exception as e:
        st.error(f"❌ Export hatası: {e}")
        return None, None

st.title("⚡ Akıllı Excel & Raporlama Platformu (v2.0)")
st.markdown("**Yenilikler:** Fuzzy matching, Çoklu export formatlı, Claude AI, Caching ⚡")

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Excel Eşleştirme & Rapor", 
    "🔗 Esnek DÜŞEYARA / XLOOKUP", 
    "🛠️ Hızlı Veri Temizleme",
    "🤖 Yapay Zeka Veri Asistanı"
])

# ==========================================
# TAB 1: EXCEL EŞLEŞTİRME & ANKET RAPORU
# ==========================================
with tab1:
    st.header("📋 Şablon Eşleştirme ve Durum Raporlama")
    st.caption("Otomatik fuzzy matching ile sütun adlarını tanır, hatta %80 benzer ise de eşleştirir.")
    
    col1, col2 = st.columns(2)
    with col1:
        file_ana = st.file_uploader("Birinci Dosya / Ana Liste", type=["xlsx", "xls", "csv"], key="ana_dosya")
    with col2:
        file_gecis = st.file_uploader("İkinci Dosya", type=["xlsx", "xls", "csv"], key="gecis_dosya")

    if file_ana and file_gecis:
        df_ana = load_file(file_ana.read(), file_ana.name)
        df_gecis = load_file(file_gecis.read(), file_gecis.name)
        
        if df_ana is not None and df_gecis is not None:
            c_key1, c_key2 = st.columns(2)
            with c_key1:
                k_ana = st.selectbox("Birinci Dosyadaki Ortak Sütun", df_ana.columns, key="k1")
            with c_key2:
                # Fuzzy matching önerisi
                similar = find_similar_columns(k_ana, df_gecis.columns)
                if similar:
                    k_gecis_default = similar[0][0]
                    st.info(f"💡 Benzer sütun bulundu: **{k_gecis_default}** ({similar[0][1]:.0%} eşleşme)")
                else:
                    k_gecis_default = df_gecis.columns[0]
                
                k_gecis = st.selectbox("İkinci Dosyadaki Ortak Sütun", df_gecis.columns, 
                                      index=list(df_gecis.columns).index(k_gecis_default), key="k2")

            if st.button("🚀 Eşleştirmeyi ve Analizi Başlat", type="primary"):
                with st.spinner("⏳ Veriler işleniyor..."):
                    df_merged = safe_merge(df_ana.copy(), df_gecis.copy(), k_ana, k_gecis, how='left')
                    
                    if df_merged is not None:
                        st.success("✅ Veriler Başarıyla Eşleştirildi!")
                        
                        # Özet Kartlar
                        st.subheader("📊 Rapor Özet Göstergeleri")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Toplam Kayıt", len(df_merged))
                        
                        if 'ANKET_DURUM' in df_merged.columns:
                            c2.metric("TAM", (df_merged['ANKET_DURUM'] == 'TAM').sum())
                            c3.metric("KALAN", (df_merged['ANKET_DURUM'] == 'KALAN').sum())
                            c4.metric("Tanımsız", df_merged['ANKET_DURUM'].isna().sum())
                            
                            fig = px.pie(df_merged, names='ANKET_DURUM', title='Durum Dağılımı', hole=0.4)
                            st.plotly_chart(fig, use_container_width=True)

                        st.subheader("🔍 İşlenmiş Veri Önizleme")
                        st.dataframe(df_merged.head(15), use_container_width=True)

                        # Çoklu Export Seçeneği
                        st.subheader("📥 Dosyayı İndir")
                        exp_col1, exp_col2, exp_col3 = st.columns(3)
                        
                        with exp_col1:
                            data, fname = export_file(df_merged, "xlsx", "Guncellenmis_Veri")
                            if data:
                                st.download_button("📊 Excel (.xlsx)", data, fname, key="dl1")
                        
                        with exp_col2:
                            data, fname = export_file(df_merged, "csv", "Guncellenmis_Veri")
                            if data:
                                st.download_button("📄 CSV", data, fname, key="dl2")
                        
                        with exp_col3:
                            data, fname = export_file(df_merged, "parquet", "Guncellenmis_Veri")
                            if data:
                                st.download_button("⚡ Parquet", data, fname, key="dl3")

# ==========================================
# TAB 2: ESNEK DÜŞEYARA MODÜLÜ
# ==========================================
with tab2:
    st.header("🔗 Esnek DÜŞEYARA / XLOOKUP Modülü")
    st.caption("Gelişmiş eşleştirme ve sütun seçimi.")
    
    file_main = st.file_uploader("Ana Dosyayı Yükleyin", type=["xlsx", "csv"], key="m_file")
    file_ref = st.file_uploader("Referans / Kaynak Dosyayı Yükleyin", type=["xlsx", "csv"], key="r_file")
    
    if file_main and file_ref:
        df_m = load_file(file_main.read(), file_main.name)
        df_r = load_file(file_ref.read(), file_ref.name)
        
        if df_m is not None and df_r is not None:
            col_a, col_b = st.columns(2)
            with col_a:
                key_m = st.selectbox("Ana Dosyadaki Eşleşme Sütunu", df_m.columns)
            with col_b:
                similar = find_similar_columns(key_m, df_r.columns)
                key_r_default = similar[0][0] if similar else df_r.columns[0]
                key_r = st.selectbox("Referans Dosyadaki Eşleşme Sütunu", df_r.columns,
                                    index=list(df_r.columns).index(key_r_default))
                
            target_cols = st.multiselect("Referans Dosyadan Aktarılacak Sütunları Seçin", 
                                        [c for c in df_r.columns if c != key_r])
            
            if st.button("🔗 Verileri Birleştir"):
                with st.spinner("⏳ Birleştiriliyor..."):
                    sub_r = df_r[[key_r] + target_cols].drop_duplicates(subset=[key_r])
                    res = safe_merge(df_m.copy(), sub_r, key_m, key_r, how='left')
                    
                    if res is not None:
                        st.dataframe(res.head(20), use_container_width=True)
                        st.metric("Toplam Satır", len(res))
                        
                        # Export
                        exp_col1, exp_col2 = st.columns(2)
                        with exp_col1:
                            data, fname = export_file(res, "xlsx", "Birlestirilmis_Veri")
                            if data:
                                st.download_button("📊 Excel İndir", data, fname, key="lookup_dl1")
                        with exp_col2:
                            data, fname = export_file(res, "csv", "Birlestirilmis_Veri")
                            if data:
                                st.download_button("📄 CSV İndir", data, fname, key="lookup_dl2")

# ==========================================
# TAB 3: HIZLI VERİ TEMİZLEME MODÜLÜ
# ==========================================
with tab3:
    st.header("🛠️ Otomatik Veri Temizleme & Makrolar")
    file_clean = st.file_uploader("Temizlenecek Dosyayı Yükleyin", type=["xlsx", "csv"], key="c_file")
    
    if file_clean:
        df_c = load_file(file_clean.read(), file_clean.name)
        
        if df_c is not None:
            st.write(f"**Orijinal:** {df_c.shape[0]} Satır × {df_c.shape[1]} Sütun")
            
            op = st.selectbox("Yapılacak İşlem", [
                "Mükerrer Satırları Sil (Tüm Kolonlar)",
                "Belirli Bir Sütuna Göre Mükerrerleri Sil",
                "Metin Sütunlarındaki Gereksiz Boşlukları Temizle (TRIM)",
                "Metinleri BÜYÜK HARFE Çevir",
                "Tamamen Boş Satırları Sil",
                "Null/Boş Değerleri Belirli Değerle Doldur"
            ])
            
            selected_col = None
            fill_value = None
            
            if op == "Belirli Bir Sütuna Göre Mükerrerleri Sil":
                selected_col = st.selectbox("Hangi Sütuna Göre?", df_c.columns)
            elif op == "Null/Boş Değerleri Belirli Değerle Doldur":
                fill_col = st.selectbox("Hangi Sütun?", df_c.columns)
                fill_value = st.text_input("Doldurulacak Değer:")
                
            if st.button("⚡ Temizlemeyi Uygula"):
                try:
                    df_original_size = len(df_c)
                    
                    if op == "Mükerrer Satırları Sil (Tüm Kolonlar)":
                        df_c = df_c.drop_duplicates()
                    elif op == "Belirli Bir Sütuna Göre Mükerrerleri Sil" and selected_col:
                        df_c = df_c.drop_duplicates(subset=[selected_col])
                    elif op == "Metin Sütunlarındaki Gereksiz Boşlukları Temizle (TRIM)":
                        for col in df_c.select_dtypes(include='object').columns:
                            df_c[col] = df_c[col].astype(str).str.strip()
                    elif op == "Metinleri BÜYÜK HARFE Çevir":
                        for col in df_c.select_dtypes(include='object').columns:
                            df_c[col] = df_c[col].astype(str).str.upper()
                    elif op == "Tamamen Boş Satırları Sil":
                        df_c = df_c.dropna(how='all')
                    elif op == "Null/Boş Değerleri Belirli Değerle Doldur" and fill_value:
                        df_c[fill_col] = df_c[fill_col].fillna(fill_value)
                        
                    st.success(f"✅ Tamamlandı! {df_original_size - len(df_c)} satır işlendi. Yeni boyut: {len(df_c)} Satır")
                    st.dataframe(df_c.head(15), use_container_width=True)
                    
                    # Export
                    exp_col1, exp_col2 = st.columns(2)
                    with exp_col1:
                        data, fname = export_file(df_c, "xlsx", "Temizlenmis_Veri")
                        if data:
                            st.download_button("📊 Excel İndir", data, fname, key="clean_dl1")
                    with exp_col2:
                        data, fname = export_file(df_c, "csv", "Temizlenmis_Veri")
                        if data:
                            st.download_button("📄 CSV İndir", data, fname, key="clean_dl2")
                            
                except Exception as e:
                    st.error(f"❌ Hata: {e}")

# ==========================================
# TAB 4: YAPAY ZEKA VERİ ASİSTANI
# ==========================================
with tab4:
    st.header("🤖 Yapay Zeka Excel & Analiz Asistanı")
    st.caption("**Groq (Ücretsiz)** 🎉 | OpenAI | Claude")
    
    ai_provider = st.radio("Hangi AI kullanmak istiyorsunuz?", [
        "🎉 Groq (Ücretsiz & Hızlı)", 
        "OpenAI (GPT-4o-mini)", 
        "Claude (Anthropic)"
    ])
    
    ai_col1, ai_col2 = st.columns(2)
    with ai_col1:
        f1 = st.file_uploader("1. Dosya (df1)", type=["xlsx", "csv"], key="f1")
    with ai_col2:
        f2 = st.file_uploader("2. Dosya (df2 - Opsiyonel)", type=["xlsx", "csv"], key="f2")
        
    df1 = load_file(f1.read(), f1.name) if f1 else None
    df2 = load_file(f2.read(), f2.name) if f2 else None
    
    if df1 is not None:
        st.write("📌 **1. Dosya Sütunları (df1):**", list(df1.columns))
        if df2 is not None:
            st.write("📌 **2. Dosya Sütunları (df2):**", list(df2.columns))
            
        user_prompt = st.text_area(
            "Yapay Zekaya Komut Verin:", 
            placeholder="Örn: 'df1 ile df2'yi BIRIMNO sütununa göre birleştir ve ANKET_DURUM='KALAN' olanları filtrele.'"
        )
        
        if st.button("🚀 Yapay Zekaya İşlet", type="primary"):
            if not user_prompt.strip():
                st.warning("Lütfen bir talimat verin.")
            else:
                api_key = None
                if ai_provider == "🎉 Groq (Ücretsiz & Hızlı)":
                    api_key = st.secrets.get("GROQ_API_KEY")
                    if not api_key:
                        st.error("⚠️ GROQ_API_KEY tanımlı değil. https://console.groq.com/keys adresinden key alın (ücretsiz).")
                elif ai_provider == "OpenAI (GPT-4o-mini)":
                    api_key = st.secrets.get("OPENAI_API_KEY")
                    if not api_key:
                        st.error("⚠️ OPENAI_API_KEY tanımlı değil.")
                else:
                    api_key = st.secrets.get("ANTHROPIC_API_KEY")
                    if not api_key:
                        st.error("⚠️ ANTHROPIC_API_KEY tanımlı değil.")
                
                if api_key:
                    try:
                        with st.spinner("🤖 Yapay zeka çalışıyor..."):
                            sys_msg = f"""Sen profesyonel Python Pandas uzmanısın.
Veri çerçeveleri: df1 ({list(df1.columns)}){f", df2 ({list(df2.columns)})" if df2 is not None else ""}
SADECE çalıştırılabilir geçerli Python pandas kodu gönder.
Sonucu 'result_df' isimli değişkene ata.
Kodu ```python ... ``` içerisinde döndür."""
                            
                            if ai_provider == "🎉 Groq (Ücretsiz & Hızlı)":
                                from groq import Groq
                                client = Groq(api_key=api_key)
                                
                                response = client.chat.completions.create(
                                    model="mixtral-8x7b-32768",
                                    messages=[
                                        {"role": "system", "content": sys_msg},
                                        {"role": "user", "content": user_prompt}
                                    ],
                                    temperature=0.3,
                                    max_tokens=1500
                                )
                                code_res = response.choices[0].message.content
                                
                            elif ai_provider == "OpenAI (GPT-4o-mini)":
                                import openai
                                client = openai.OpenAI(api_key=api_key)
                                
                                response = client.chat.completions.create(
                                    model="gpt-4o-mini",
                                    messages=[
                                        {"role": "system", "content": sys_msg},
                                        {"role": "user", "content": user_prompt}
                                    ],
                                    temperature=0.3
                                )
                                code_res = response.choices[0].message.content
                                
                            else:  # Claude
                                import anthropic
                                client = anthropic.Anthropic(api_key=api_key)
                                
                                response = client.messages.create(
                                    model="claude-opus-4-1",
                                    max_tokens=1500,
                                    system=sys_msg,
                                    messages=[
                                        {"role": "user", "content": user_prompt}
                                    ]
                                )
                                code_res = response.content[0].text
                            
                            # Kod çıkarımı
                            code_clean = code_res.split("```python")[1].split("```")[0].strip() if "```python" in code_res else code_res.strip()
                            
                            # Kod çalıştırma
                            local_vars = {"df1": df1.copy(), "df2": df2.copy() if df2 is not None else None, "pd": pd}
                            exec(code_clean, {}, local_vars)
                            result_df = local_vars.get("result_df")
                            
                            if result_df is not None:
                                st.success("✅ İşlem Başarıyla Tamamlandı!")
                                st.dataframe(result_df.head(20), use_container_width=True)
                                st.metric("Sonuç Satır Sayısı", len(result_df))
                                
                                with st.expander("🛠️ Arka Planda Çalıştırılan Python Kodu"):
                                    st.code(code_clean, language="python")
                                
                                # Export
                                exp_col1, exp_col2, exp_col3 = st.columns(3)
                                with exp_col1:
                                    data, fname = export_file(result_df, "xlsx", "AI_Sonuc")
                                    if data:
                                        st.download_button("📊 Excel İndir", data, fname, key="ai_dl1")
                                with exp_col2:
                                    data, fname = export_file(result_df, "csv", "AI_Sonuc")
                                    if data:
                                        st.download_button("📄 CSV İndir", data, fname, key="ai_dl2")
                                with exp_col3:
                                    data, fname = export_file(result_df, "parquet", "AI_Sonuc")
                                    if data:
                                        st.download_button("⚡ Parquet İndir", data, fname, key="ai_dl3")
                            else:
                                st.error("❌ Yapay zeka kod çalıştırılamadı. Lütfen taLimatınızı gözden geçirin.")
                                
                    except Exception as e:
                        st.error(f"❌ Hata: {str(e)[:200]}")