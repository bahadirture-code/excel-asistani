import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Excel & Raporlama Merkezi", layout="wide", page_icon="📊")

st.title("📊 Akıllı Excel & Raporlama Merkezi")
st.markdown("Formüllerle uğraşmadan tüm veri işlemlerinizi yapın veya Yapay Zekaya ne yapması gerektiğini Türkçe söyleyin.")

# Tab Yapısı (Yapay Zeka Asistanı Eklendi)
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Excel Eşleştirme", 
    "🔗 Genel DÜŞEYARA / Eşleştirme", 
    "🛠️ Veri Temizleme & Makrolar",
    "💬 Yapay Zeka Excel Asistanı"
])

# ==========================================
# TAB 1: EXCEL EŞLEŞTİRME MODÜLÜ
# ==========================================
with tab1:
    st.header("Anket Listesi ve Geçiş Dosyası Eşleştirme")
    st.caption("Birinci dosyaya ana anket listenizi, ikinci dosyaya sistemden aldığınız durum raporunu yükleyin.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        file_ana = st.file_uploader("Ana Anket Listesini Yükleyin (xlsx)", type=["xlsx", "xls"], key="ana_dosya")
    with col2:
        file_gecis = st.file_uploader("Geçiş / Durum Raporunu Yükleyin (xlsx)", type=["xlsx", "xls"], key="gecis_dosya")

    if file_ana and file_gecis:
        try:
            df_ana = pd.read_excel(file_ana)
            df_gecis = pd.read_excel(file_gecis)
            
            col_ana_key = [c for c in df_ana.columns if str(c).strip().lower() == 'birimno']
            col_gecis_key = [c for c in df_gecis.columns if str(c).strip().lower() == 'birimno']
            
            if col_ana_key and col_gecis_key:
                k_ana = col_ana_key[0]
                k_gecis = col_gecis_key[0]

                df_ana[k_ana] = df_ana[k_ana].astype(str).str.strip()
                df_gecis[k_gecis] = df_gecis[k_gecis].astype(str).str.strip()
                
                gecis_sub = df_gecis[[k_gecis, 'ANKET_DURUM', 'DETAY']].drop_duplicates(subset=[k_gecis])
                df_merged = pd.merge(df_ana, gecis_sub, left_on=k_ana, right_on=k_gecis, how='left', suffixes=('_eski', ''))
                
                if 'ANKET_DURUM_eski' in df_merged.columns:
                    df_merged.drop(columns=['ANKET_DURUM_eski'], inplace=True)
                if 'DETAY_eski' in df_merged.columns:
                    df_merged.drop(columns=['DETAY_eski'], inplace=True)
                if k_gecis != k_ana and k_gecis in df_merged.columns:
                    df_merged.drop(columns=[k_gecis], inplace=True)

                st.success("✅ Eşleştirme Başarıyla Tamamlandı!")
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Toplam Anket", len(df_merged))
                c2.metric("Tamamlanan (TAM)", (df_merged['ANKET_DURUM'] == 'TAM').sum())
                c3.metric("Kalan (KALAN)", (df_merged['ANKET_DURUM'] == 'KALAN').sum())
                c4.metric("Boş / Diğer", df_merged['ANKET_DURUM'].isna().sum())

                st.subheader("İşlenmiş Veri Önizleme")
                st.dataframe(df_merged.head(10), use_container_width=True)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_merged.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 Güncellenmiş Anket Dosyasını İndir",
                    data=output.getvalue(),
                    file_name="Anket_Durum_Guncellendi.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("Her iki dosyada da 'birimno' sütunu bulunamadı.")
        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# ==========================================
# TAB 2: GENEL VLOOKUP MODÜLÜ
# ==========================================
with tab2:
    st.header("Her Türlü İki Dosyayı Eşleştir (VLOOKUP / XLOOKUP)")
    
    file_main = st.file_uploader("Ana Dosyayı Yükleyin (Veri eklenecek olan)", type=["xlsx", "csv"], key="m_file")
    file_ref = st.file_uploader("Referans Dosyayı Yükleyin (Verinin alınacağı)", type=["xlsx", "csv"], key="r_file")
    
    if file_main and file_ref:
        df_m = pd.read_excel(file_main) if file_main.name.endswith('xlsx') else pd.read_csv(file_main)
        df_r = pd.read_excel(file_ref) if file_ref.name.endswith('xlsx') else pd.read_csv(file_ref)
        
        col_a, col_b = st.columns(2)
        with col_a:
            key_m = st.selectbox("Ana Dosyadaki Ortak Sütun (Anahtar)", df_m.columns)
        with col_b:
            key_r = st.selectbox("Referans Dosyadaki Ortak Sütun (Anahtar)", df_r.columns)
            
        target_cols = st.multiselect("Referans Dosyadan Aktarılacak Sütunları Seçin", [c for c in df_r.columns if c != key_r])
        
        if st.button("Eşleştirmeyi Yap"):
            df_m[key_m] = df_m[key_m].astype(str).str.strip()
            df_r[key_r] = df_r[key_r].astype(str).str.strip()
            
            sub_r = df_r[[key_r] + target_cols].drop_duplicates(subset=[key_r])
            res = pd.merge(df_m, sub_r, left_on=key_m, right_on=key_r, how='left')
            
            st.dataframe(res.head())
            
            out_gen = io.BytesIO()
            with pd.ExcelWriter(out_gen, engine='xlsxwriter') as writer:
                res.to_excel(writer, index=False)
                
            st.download_button("📥 Birleştirilmiş Dosyayı İndir", out_gen.getvalue(), "Birlestirilmis_Veri.xlsx")

# ==========================================
# TAB 3: VERİ TEMİZLEME MODÜLÜ
# ==========================================
with tab3:
    st.header("Otomatik Veri Temizleme Araçları")
    file_clean = st.file_uploader("İşlem Yapılacak Dosyayı Yükleyin", type=["xlsx", "csv"], key="c_file")
    
    if file_clean:
        df_c = pd.read_excel(file_clean) if file_clean.name.endswith('xlsx') else pd.read_csv(file_clean)
        st.write("Orijinal Veri Boyutu:", df_c.shape)
        
        op = st.selectbox("Yapılacak İşlemi Seçin", [
            "Mükerrer Satırları Sil",
            "Metin Sütunlarını Büyük Harfe Çevir",
            "Boş Satırları Temizle"
        ])
        
        if st.button("İşlemi Uygula"):
            if op == "Mükerrer Satırları Sil":
                df_c = df_c.drop_duplicates()
                st.success(f"Yeni Veri Boyutu: {df_c.shape}")
            elif op == "Metin Sütunlarını Büyük Harfe Çevir":
                for col in df_c.select_dtypes(include='object').columns:
                    df_c[col] = df_c[col].astype(str).str.upper()
                st.success("Tüm metinler büyük harfe dönüştürüldü.")
            elif op == "Boş Satırları Temizle":
                df_c = df_c.dropna(how='all')
                st.success("Tamamen boş satırlar silindi.")
                
            st.dataframe(df_c.head())
            
            out_cln = io.BytesIO()
            with pd.ExcelWriter(out_cln, engine='xlsxwriter') as writer:
                df_c.to_excel(writer, index=False)
            st.download_button("📥 Temizlenmiş Dosyayı İndir", out_cln.getvalue(), "Temizlenmis_Veri.xlsx")

# ==========================================
# TAB 4: YAPAY ZEKA EXCEL ASİSTANI
# ==========================================
with tab4:
    st.header("💬 Doğal Dille Excel İşleme (Yapay Zeka)")
    st.caption("Excel dosyanızı yükleyin ve ne yapılmasını istediğinizi kendi kelimelerinizle yazın.")
    
    api_key = st.text_input("OpenAI API Anahtarınızı Girin:", type="password")
    ai_file = st.file_uploader("Üzerinde Çalışılacak Excel Dosyasını Yükleyin", type=["xlsx", "csv"], key="ai_file")
    
    if ai_file:
        df_ai = pd.read_excel(ai_file) if ai_file.name.endswith('xlsx') else pd.read_csv(ai_file)
        st.write("Sütunlarınız:", list(df_ai.columns))
        
        user_prompt = st.text_area("Yapay Zekaya İsteğinizi Yazın:", placeholder="Örn: 'anketör' sütunundaki isimlerin baş harflerini büyük yap ve 'ANKET_DURUM' sütunu 'TAM' olanları getir.")
        
        if st.button("Yapay Zekaya Yaptır"):
            if not api_key:
                st.error("Lütfen bir API Anahtarı girin.")
            elif not user_prompt:
                st.warning("Lütfen bir komut yazın.")
            else:
                try:
                    import openai
                    client = openai.OpenAI(api_key=api_key)
                    
                    system_instructions = f"""
                    Sen bir Python Pandas veri işleme asistanısın. Kullanıcı sana bir veri seti (df) ve yapmak istediği işlemi söyleyecek.
                    Sadece çalıştırılabilir Python pandas kodu döndür. 
                    Mevcut sütunlar: {list(df_ai.columns)}
                    İşlenecek veri tablosu değişken adı 'df'dir. 
                    Kod blokları (```python ... ```) içinde yaz.
                    """
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_instructions},
                            {"role": "user", "content": user_prompt}
                        ]
                    )
                    
                    code_res = response.choices[0].message.content
                    
                    # Kod temizleme
                    code_clean = code_res.split("```python")[1].split("```")[0].strip() if "```python" in code_res else code_res.strip()
                    
                    # Kodu df üzerinde çalıştır
                    local_vars = {"df": df_ai.copy(), "pd": pd}
                    exec(code_clean, {}, local_vars)
                    df_res = local_vars["df"]
                    
                    st.success("✅ Yapay zeka isteğinizi başarıyla tamamladı!")
                    st.dataframe(df_res.head(10))
                    
                    out_ai = io.BytesIO()
                    with pd.ExcelWriter(out_ai, engine='xlsxwriter') as writer:
                        df_res.to_excel(writer, index=False)
                    st.download_button("📥 Sonuç Dosyasını İndir", out_ai.getvalue(), "AI_Islenmis_Veri.xlsx")
                    
                except Exception as e:
                    st.error(f"İşlem sırasında bir hata oluştu: {e}")