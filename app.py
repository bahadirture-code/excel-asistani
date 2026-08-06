import streamlit as st
import pandas as pd
import io
import plotly.express as px

st.set_page_config(page_title="Akıllı Excel & Veri İşleme Platformu", layout="wide", page_icon="⚡")

st.title("⚡ Akıllı Excel & Raporlama Platformu")
st.markdown("Karmaşık formüller ve makrolarla vakit kaybetmeyin. Verilerinizi yükleyin veya yapay zekaya Türkçe talimat verin.")

# Tab Yapısı
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
    st.caption("Ana listenizi ve sistemden aldığınız durum raporunu yükleyerek verileri anında birleştirin.")
    
    col1, col2 = st.columns(2)
    with col1:
        file_ana = st.file_uploader("Ana Dosya / Liste (xlsx, csv)", type=["xlsx", "xls", "csv"], key="ana_dosya")
    with col2:
        file_gecis = st.file_uploader("Durum / Geçiş Raporu (xlsx, csv)", type=["xlsx", "xls", "csv"], key="gecis_dosya")

    if file_ana and file_gecis:
        try:
            df_ana = pd.read_excel(file_ana) if not file_ana.name.endswith('.csv') else pd.read_csv(file_ana)
            df_gecis = pd.read_excel(file_gecis) if not file_gecis.name.endswith('.csv') else pd.read_csv(file_gecis)
            
            c_key1, c_key2 = st.columns(2)
            with c_key1:
                k_ana = st.selectbox("Ana Dosyadaki Ortak Sütun (Eşleşecek Anahtar)", df_ana.columns, key="k1")
            with c_key2:
                k_gecis = st.selectbox("Durum Raporundaki Ortak Sütun", df_gecis.columns, key="k2")

            if st.button("🚀 Eşleştirmeyi ve Analizi Başlat", type="primary"):
                df_ana[k_ana] = df_ana[k_ana].astype(str).str.strip()
                df_gecis[k_gecis] = df_gecis[k_gecis].astype(str).str.strip()
                
                # Sütun Yakalama (ANKET_DURUM ve DETAY var ise)
                target_cols = [c for c in ['ANKET_DURUM', 'DETAY'] if c in df_gecis.columns]
                if not target_cols:
                    target_cols = [c for c in df_gecis.columns if c != k_gecis]
                
                gecis_sub = df_gecis[[k_gecis] + target_cols].drop_duplicates(subset=[k_gecis])
                df_merged = pd.merge(df_ana, gecis_sub, left_on=k_ana, right_on=k_gecis, how='left', suffixes=('_eski', ''))

                st.success("✅ Veriler Başarıyla Eşleştirildi!")
                
                # Özet Kartlar
                st.subheader("📊 Rapor Özet Göstergeleri")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Toplam Kayıt", len(df_merged))
                
                if 'ANKET_DURUM' in df_merged.columns:
                    c2.metric("Tamamlanan (TAM)", (df_merged['ANKET_DURUM'] == 'TAM').sum())
                    c3.metric("Kalan (KALAN)", (df_merged['ANKET_DURUM'] == 'KALAN').sum())
                    c4.metric("Eksik / Tanımsız", df_merged['ANKET_DURUM'].isna().sum())
                    
                    # Görsel Grafik
                    fig = px.pie(df_merged, names='ANKET_DURUM', title='Anket Durum Dağılımı', hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)

                st.subheader("🔍 İşlenmiş Veri Önizleme")
                st.dataframe(df_merged.head(15), use_container_width=True)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_merged.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 Güncellenmiş Excel Dosyasını İndir",
                    data=output.getvalue(),
                    file_name="Guncellenmis_Veri.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# ==========================================
# TAB 2: ESNEK DÜŞEYARA MODÜLÜ
# ==========================================
with tab2:
    st.header("🔗 Esnek DÜŞEYARA / XLOOKUP Modülü")
    st.caption("Herhangi iki Excel dosyasını seçerek istediğiniz sütunları birbirine bağlayın.")
    
    file_main = st.file_uploader("Ana Dosyayı Yükleyin", type=["xlsx", "csv"], key="m_file")
    file_ref = st.file_uploader("Referans / Kaynak Dosyayı Yükleyin", type=["xlsx", "csv"], key="r_file")
    
    if file_main and file_ref:
        df_m = pd.read_excel(file_main) if not file_main.name.endswith('.csv') else pd.read_csv(file_main)
        df_r = pd.read_excel(file_ref) if not file_ref.name.endswith('.csv') else pd.read_csv(file_ref)
        
        col_a, col_b = st.columns(2)
        with col_a:
            key_m = st.selectbox("Ana Dosyadaki Eşleşme Sütunu", df_m.columns)
        with col_b:
            key_r = st.selectbox("Referans Dosyadaki Eşleşme Sütunu", df_r.columns)
            
        target_cols = st.multiselect("Referans Dosyadan Aktarılacak Sütunları Seçin", [c for c in df_r.columns if c != key_r])
        
        if st.button("🔗 Verileri Birleştir"):
            df_m[key_m] = df_m[key_m].astype(str).str.strip()
            df_r[key_r] = df_r[key_r].astype(str).str.strip()
            
            sub_r = df_r[[key_r] + target_cols].drop_duplicates(subset=[key_r])
            res = pd.merge(df_m, sub_r, left_on=key_m, right_on=key_r, how='left')
            
            st.dataframe(res.head(10))
            
            out_gen = io.BytesIO()
            with pd.ExcelWriter(out_gen, engine='xlsxwriter') as writer:
                res.to_excel(writer, index=False)
                
            st.download_button("📥 Birleştirilmiş Dosyayı İndir", out_gen.getvalue(), "Birlestirilmis_Veri.xlsx")

# ==========================================
# TAB 3: HIZLI VERİ TEMİZLEME MODÜLÜ
# ==========================================
with tab3:
    st.header("🛠️ Otomatik Veri Temizleme & Makrolar")
    file_clean = st.file_uploader("Temizlenecek Dosyayı Yükleyin", type=["xlsx", "csv"], key="c_file")
    
    if file_clean:
        df_c = pd.read_excel(file_clean) if not file_clean.name.endswith('.csv') else pd.read_csv(file_clean)
        st.write(f"Orijinal Veri Boyutu: **{df_c.shape[0]} Satır, {df_c.shape[1]} Sütun**")
        
        op = st.selectbox("Yapılacak Temizleme İşlemi", [
            "Mükerrer Satırları Sil (Tüm Kolonlar)",
            "Belirli Bir Sütuna Göre Mükerrerleri Sil",
            "Metin Sütunlarındaki Gereksiz Boşlukları Temizle (TRIM)",
            "Metinleri BÜYÜK HARFE Çevir",
            "Tamamen Boş Satırları Sil"
        ])
        
        selected_col = None
        if op == "Belirli Bir Sütuna Göre Mükerrerleri Sil":
            selected_col = st.selectbox("Hangi Sütuna Göre Mükerrer Kayıtlar Silinsin?", df_c.columns)
            
        if st.button("⚡ Temizlemeyi Uygula"):
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
                
            st.success(f"İşlem Tamamlandı! Yeni Boyut: {df_c.shape[0]} Satır")
            st.dataframe(df_c.head(10))
            
            out_cln = io.BytesIO()
            with pd.ExcelWriter(out_cln, engine='xlsxwriter') as writer:
                df_c.to_excel(writer, index=False)
            st.download_button("📥 Temizlenmiş Dosyayı İndir", out_cln.getvalue(), "Temizlenmis_Veri.xlsx")

# ==========================================
# TAB 4: YAPAY ZEKA VERİ ASİSTANI (GÜÇLENDİRİLMİŞ)
# ==========================================
with tab4:
    st.header("🤖 Yapay Zeka Excel & Analiz Asistanı")
    st.caption("İster 1 ister 2 dosya yükleyin ve Türkçe cümlelerle istediğinizi yaptırın.")
    
    ai_col1, ai_col2 = st.columns(2)
    with ai_col1:
        f1 = st.file_uploader("1. Dosya (df1)", type=["xlsx", "csv"], key="f1")
    with ai_col2:
        f2 = st.file_uploader("2. Dosya (df2 - Opsiyonel)", type=["xlsx", "csv"], key="f2")
        
    df1 = pd.read_excel(f1) if f1 and not f1.name.endswith('.csv') else (pd.read_csv(f1) if f1 else None)
    df2 = pd.read_excel(f2) if f2 and not f2.name.endswith('.csv') else (pd.read_csv(f2) if f2 else None)
    
    if df1 is not None:
        st.write("📌 **1. Dosya Sütunları (df1):**", list(df1.columns))
        if df2 is not None:
            st.write("📌 **2. Dosya Sütunları (df2):**", list(df2.columns))
            
        user_prompt = st.text_area(
            "Yapay Zekaya Komut Verin:", 
            placeholder="Örn: 'df1 dosyasındaki birimno ile df2 dosyasındaki BIRIMNO sütunlarını birleştirip ANKET_DURUM kalanları filtrele.'"
        )
        
        if st.button("🚀 Yapay Zekaya İşlet", type="primary"):
            if "OPENAI_API_KEY" not in st.secrets:
                st.error("⚠️ API Anahtarı Streamlit Secrets alanında tanımlı değil.")
            elif not user_prompt:
                st.warning("Lütfen yapay zekaya bir talimat verin.")
            else:
                try:
                    import openai
                    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                    
                    sys_msg = f"""
                    Sen profesyonel bir Python Pandas Veri İşleme Uzmanısın.
                    Kullanıcının talimatına göre verilen veri çerçeveleri (Dataframe) üzerinde işlem yap.
                    Yüklü Veriler:
                    - 'df1' mevcut (Sütunlar: {list(df1.columns)})
                    {"- 'df2' mevcut (Sütunlar: " + str(list(df2.columns)) + ")" if df2 is not None else ""}
                    
                    SADECE VE SADECE çalıştırılabilir geçerli Python pandas kodunu gönder.
                    Sonucu en son 'result_df' isimli değişkene ata.
                    Kod bloklarını ```python ... ``` içerisinde döndür.
                    """
                    
                    with st.spinner("Yapay zeka veri üzerinde çalışıyor..."):
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": sys_msg},
                                {"role": "user", "content": user_prompt}
                            ]
                        )
                        
                        code_res = response.choices[0].message.content
                        code_clean = code_res.split("```python")[1].split("```")[0].strip() if "```python" in code_res else code_res.strip()
                        
                        local_vars = {"df1": df1.copy(), "df2": df2.copy() if df2 is not None else None, "pd": pd}
                        exec(code_clean, {}, local_vars)
                        result_df = local_vars.get("result_df", local_vars.get("df1"))
                        
                        st.success("✅ İşlem Başarıyla Tamamlandı!")
                        st.dataframe(result_df.head(15), use_container_width=True)
                        
                        with st.expander("🛠️ Yapay Zekanın Arka Planda Çalıştırdığı Python Kodu"):
                            st.code(code_clean, language="python")
                        
                        out_ai = io.BytesIO()
                        with pd.ExcelWriter(out_ai, engine='xlsxwriter') as writer:
                            result_df.to_excel(writer, index=False)
                        st.download_button("📥 İşlenmiş Veriyi İndir", out_ai.getvalue(), "AI_Sonuc.xlsx")
                        
                except Exception as e:
                    st.error(f"İşlem yürütülürken hata oluştu: {e}")