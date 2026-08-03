import streamlit as st
import pandas as pd
import numpy as np
import os
import io
from PIL import Image
from dotenv import load_dotenv
from google import genai

# .env yükle
load_dotenv()

# Sayfa Ayarları
st.set_page_config(
    page_title="AI Veri Analiz Platformu",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern UI / Kart Stilleri
st.markdown("""
<style>
    /* Metrik Kartları */
    div[data-testid="stMetric"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-left: 5px solid #3b82f6 !important;
        border-radius: 12px;
        padding: 15px;
    }
    
    /* Sekme Tasarımı */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e293b !important;
        border-radius: 12px;
        padding: 5px;
        border: 1px solid #334155;
    }
    .stTabs [aria-selected="true"] {
        background: #2563eb !important;
        color: #ffffff !important;
        border-radius: 8px;
    }
    
    /* Başlık Vurgusu */
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #60a5fa;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Başlık Alanı
st.markdown('<div class="hero-title">⚡ AI Destekli Veri & Görsel Analiz Platformu</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Excel, CSV veya Fotoğraf/Ekran Görüntüsü yükleyin; Yapay Zekâ anında analiz etsin!</div>', unsafe_allow_html=True)

# Sohbet Geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Yan Menü (Sidebar)
with st.sidebar:
    st.image("https://img.icons8.com/fluent/96/brain.png", width=64)
    st.title("⚙️ Kontrol Paneli")
    st.markdown("---")
    
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input("🔑 Gemini API Key", value=env_key, type="password")
    
    st.markdown("---")
    st.subheader("📁 Veri Yükleme")
    upload_type = st.radio("Dosya Türü Seçin:", ["📊 Tablo (Excel/CSV)", "🖼️ Görsel / Fotoğraf"], horizontal=True)
    
    uploaded_file = None
    uploaded_image = None
    
    if upload_type == "📊 Tablo (Excel/CSV)":
        uploaded_file = st.file_uploader("Bir Excel veya CSV dosyası seçin", type=["csv", "xlsx"])
    else:
        uploaded_image = st.file_uploader("Tablo/Fatura/Belge Fotoğrafı Yükleyin", type=["png", "jpg", "jpeg"])
        
    st.markdown("---")
    if st.button("🗑️ Chat Geçmişini Temizle", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- MOD 1: EXCEL / CSV VERİ ANALİZİ ---
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Üst Metrik Kartları
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("📄 Dosya Adı", uploaded_file.name[:14] + "..." if len(uploaded_file.name)>14 else uploaded_file.name)
        m_col2.metric("📊 Toplam Satır", f"{df.shape[0]:,}")
        m_col3.metric("📐 Toplam Sütun", df.shape[1])
        m_col4.metric("⚠️ Boş Hücre Sayısı", df.isnull().sum().sum())
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Sekmeler
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Veri Önizleme & Temizleme", 
            "🔍 Dosya Karşılaştırma & Eşleştirme",
            "📂 Çoklu Dosya Birleştirici",
            "🧮 AI Formül Sihirbazı",
            "💬 AI Analiz Sohbeti & Hazır Komutlar"
        ])
        
        # TAB 1: VERİ ÖNİZLEME & TEMİZLEME
        with tab1:
            st.subheader("🔍 Akıllı Tablo İçi Arama")
            search_term = st.text_input("Aramak istediğiniz terimi veya sayıyı girin:", placeholder="Örn: Aktif, İstanbul, 5000...")
            
            if search_term:
                mask = np.column_stack([df[col].astype(str).str.contains(search_term, case=False, na=False) for col in df.columns])
                filtered_df = df[mask.any(axis=1)]
                st.info(f"Arama kriterine uyan **{len(filtered_df)}** kayıt listeleniyor.")
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("🧹 Veri Temizleme Araçları")
            col_clean1, col_clean2 = st.columns(2)
            
            with col_clean1:
                st.markdown("**Eksik Değer İşlemleri**")
                total_nulls = df.isnull().sum().sum()
                st.write(f"Boş Değer Sayısı: `{total_nulls}`")
                if total_nulls > 0:
                    clean_option = st.selectbox("İşlem seçin:", ["Seçiniz...", "Eksik Satırları Sil", "Boş Yerlere 0 Yaz", "Boş Yerlere 'Bilinmiyor' Yaz"])
                    if st.button("Eksik Verileri Temizle", type="primary"):
                        if clean_option == "Eksik Satırları Sil":
                            df = df.dropna()
                            st.success("Boş satırlar silindi!")
                        elif clean_option == "Boş Yerlere 0 Yaz":
                            df = df.fillna(0)
                            st.success("Boş yerlere 0 yazıldı!")
                        elif clean_option == "Boş Yerlere 'Bilinmiyor' Yaz":
                            df = df.fillna("Bilinmiyor")
                            st.success("Boş yerler 'Bilinmiyor' olarak dolduruldu!")

            with col_clean2:
                st.markdown("**Yinelenen Kayıt İşlemleri**")
                duplicates = df.duplicated().sum()
                st.write(f"Tekrar Eden Satır Sayısı: `{duplicates}`")
                if duplicates > 0:
                    if st.button("Çift Kayıtları Temizle", type="primary"):
                        df = df.drop_duplicates()
                        st.success(f"{duplicates} kayıt silindi!")

            st.markdown("---")
            st.subheader("📥 Dışa Aktar")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Temiz_Veri')
            buffer.seek(0)
            st.download_button(
                label="📥 Güncel Veriyi Excel (.xlsx) Olarak İndir",
                data=buffer,
                file_name=f"temizlenmis_{uploaded_file.name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

        # TAB 2: EŞLEŞTİRME
        with tab2:
            st.subheader("🔍 Dosya Karşılaştırma & Eşleştirme")
            compare_file = st.file_uploader("Karşılaştırılacak 2. Dosyayı Seçin", type=["csv", "xlsx"], key="comp_file")
            
            if compare_file is not None:
                df2 = pd.read_csv(compare_file) if compare_file.name.endswith('.csv') else pd.read_excel(compare_file)
                st.info(f"2. Dosya Yüklendi: **{compare_file.name}** ({df2.shape[0]} Satır)")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    key1 = st.selectbox("1. Dosyadaki Anahtar Sütun:", df.columns.tolist())
                with col_m2:
                    key2 = st.selectbox("2. Dosyadaki Anahtar Sütun:", df2.columns.tolist())
                
                if st.button("Dosyaları Eşleştir", type="primary"):
                    merged_df = pd.merge(df, df2, left_on=key1, right_on=key2, how="inner", suffixes=('_D1', '_D2'))
                    st.success(f"🎉 Ortak olan **{len(merged_df)}** kayıt bulundu!")
                    st.dataframe(merged_df, use_container_width=True)

        # TAB 3: BİRLEŞTİRİCİ
        with tab3:
            st.subheader("📂 Çoklu Dosya Birleştirici")
            multiple_files = st.file_uploader("Birleştirilecek Ek Dosyaları Seçin", type=["csv", "xlsx"], accept_multiple_files=True)
            if multiple_files:
                if st.button("Tüm Dosyaları Birleştir", type="primary"):
                    combined_dfs = [df] + [pd.read_csv(mf) if mf.name.endswith('.csv') else pd.read_excel(mf) for mf in multiple_files]
                    final_df = pd.concat(combined_dfs, ignore_index=True)
                    st.success(f"🎉 Toplam {len(combined_dfs)} dosya birleştirildi! ({final_df.shape[0]} Satır)")
                    st.dataframe(final_df, use_container_width=True)

        # TAB 4: FORMÜL
        with tab4:
            st.subheader("🧮 AI Formül Oluşturucu & Açıklayıcı")
            formula_type = st.radio("Formül Türü Seçin:", ["Excel Formülü", "DAX (Power BI)", "SQL Sorgusu"], horizontal=True)
            formula_need = st.text_area("İhtiyacınızı tarif edin:", placeholder="Örn: A sütunu 'Aktif' ise B sütununu topla...")
            
            if st.button("Formül Üret", type="primary"):
                if formula_need and api_key:
                    with st.spinner("Formül oluşturuluyor..."):
                        try:
                            client = genai.Client(api_key=api_key)
                            f_prompt = f"Sen uzman bir veritabanı ve Excel uzmanısın. Kullanıcı {formula_type} cinsinden şu işlemi yapmak istiyor: '{formula_need}'. Sadece çalışan tam formülü ver ve 2 satırda mantığını açıkla."
                            f_response = client.models.generate_content(model='gemini-2.5-flash', contents=f_prompt)
                            st.markdown(f_response.text)
                        except Exception as f_err:
                            st.error(f"Hata: {f_err}")

        # TAB 5: AI SOHBET
        with tab5:
            st.subheader("💬 Kesintisiz AI Analiz Sohbeti")
            st.markdown("**💡 Hazır Analiz Komutları:**")
            col_p1, col_p2, col_p3 = st.columns(3)
            
            quick_prompt = None
            if col_p1.button("📌 Genel Veri Özeti Çıkar", use_container_width=True):
                quick_prompt = "Bu verinin genel özetini ve öne çıkan noktalarını detaylıca analiz et."
            if col_p2.button("⚠️ Hatalı/Şüpheli Verileri Bul", use_container_width=True):
                quick_prompt = "Veri seti içinde tutarsız, eksik veya şüpheli görünen satırları ve sütunları tespit et."
            if col_p3.button("🎯 Stratejik Öneriler Ver", use_container_width=True):
                quick_prompt = "Bu verilere bakarak iş süreçlerimi geliştirmek için 5 tane stratejik öneri ver."

            if not api_key:
                st.warning("⚠️ Lütfen sol menüden Gemini API Key'inizi girin.")
            else:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                prompt = st.chat_input("Veriniz hakkında soru sorun...") or quick_prompt

                if prompt:
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner("Yapay Zekâ yanıt veriyor..."):
                            try:
                                client = genai.Client(api_key=api_key)
                                data_sample = df.head(50).to_string()
                                conversation_history = "".join([f"{msg['role']}: {msg['content']}\n" for msg in st.session_state.messages])

                                full_prompt = f"""
                                Sen uzman bir veri analistisin. Kullanıcı yüklediği veriler hakkında seninle sohbet yürütüyor.
                                Önceki konuşmaları ve veriyi dikkate alarak cevap ver.

                                Veri Örneği:
                                {data_sample}

                                Konuşma Geçmişi ve Son Soru:
                                {conversation_history}
                                """
                                response = client.models.generate_content(model='gemini-2.5-flash', contents=full_prompt)
                                st.markdown(response.text)
                                st.session_state.messages.append({"role": "assistant", "content": response.text})
                            except Exception as ai_err:
                                st.error(f"Hata oluştu: {ai_err}")

    except Exception as e:
        st.error(f"Dosya okunurken bir hata oluştu: {e}")

# --- MOD 2: GÖRSEL / FOTOĞRAF ANALİZİ ---
elif uploaded_image is not None:
    st.subheader("🖼️ Yapay Zekâ Görsel Analiz Modu")
    
    col_img1, col_img2 = st.columns([1, 1])
    
    with col_img1:
        st.write("#### Yüklenen Görsel Önizlemesi:")
        img = Image.open(uploaded_image)
        st.image(img, use_container_width=True)
        
    with col_img2:
        st.write("#### 🤖 Görsel İnceleme & Analiz:")
        img_prompt = st.text_area("Görsel hakkında ne öğrenmek istersiniz?", value="Bu görseldeki verileri, tabloyu veya metinleri detaylıca incele ve Türkçe özet çıkar. Eğer bir tablo/fatura ise sayıları ve toplamları hesapla.")
        
        if st.button("Görseli Analiz Et", type="primary"):
            if not api_key:
                st.warning("⚠️ Lütfen sol menüden Gemini API Key'inizi girin.")
            else:
                with st.spinner("Yapay Zekâ görseli inceliyor..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[img, img_prompt]
                        )
                        st.markdown("### 💡 AI Görsel Analiz Sonucu:")
                        st.markdown(response.text)
                    except Exception as vision_err:
                        st.error(f"Görsel analizi sırasında hata oluştu: {vision_err}")

else:
    st.info("👈 Lütfen başlamak için sol menüden bir Excel/CSV dosyası yükleyin veya bir Fotoğraf/Ekran Görüntüsü seçin.")
