# ==========================================
# TAB 5: GROQ AI (DOĞAL DİL ASİSTANI)
# ==========================================
with tab5:
    st.header("🤖 Veri Asistanı (Groq ile Doğal Dil)")
    st.markdown("""
    **Nasıl çalışır?**  
    Verilerinizi yükleyin, ardından Türkçe veya İngilizce olarak ne yapmak istediğinizi yazın.  
    Örnek: *"Satış sütunundaki toplamı bul"*, *"Müşteri şehirlerine göre ortalama geliri hesapla"*, *"Yaş ve gelir arasındaki ilişkiyi scatter plot olarak göster"*.
    """)

    col1, col2 = st.columns(2)
    with col1:
        f1 = st.file_uploader("Dosya 1 (df1)", type=["xlsx", "csv"], key="ai1")
    with col2:
        f2 = st.file_uploader("Dosya 2 (df2) - İsteğe bağlı", type=["xlsx", "csv"], key="ai2")

    df1 = load_file(f1.read(), f1.name) if f1 else None
    df2 = load_file(f2.read(), f2.name) if f2 else None

    if df1 is not None:
        st.write("**df1 Sütunları ve Tipleri:**")
        st.write(df1.dtypes)

        if df2 is not None:
            st.write("**df2 Sütunları ve Tipleri:**")
            st.write(df2.dtypes)

        user_prompt = st.text_area("📝 Ne yapmak istiyorsunuz?", height=100,
                                   placeholder="Örn: df1'deki 'Fiyat' ve 'Adet' sütunlarını çarpıp 'Toplam' adında yeni bir sütun oluştur.")

        if st.button("🚀 Çalıştır") and user_prompt.strip():
            if not HAS_GROQ:
                st.error("❌ Groq kütüphanesi yüklü değil. `groq` paketini yükleyin.")
            else:
                api_key = st.secrets.get("GROQ_API_KEY")
                if not api_key:
                    st.error("❌ GROQ_API_KEY eksik. Secrets'a ekleyin.")
                else:
                    with st.spinner("🤔 Groq düşünüyor..."):
                        # 1. Adım: Veri bilgilerini hazırla
                        info_parts = [
                            f"df1 sütunları: {list(df1.columns)} (tipler: {df1.dtypes.to_dict()})",
                            f"df1 ilk 3 satır: \n{df1.head(3).to_string(index=False)}"
                        ]
                        if df2 is not None:
                            info_parts.append(f"df2 sütunları: {list(df2.columns)} (tipler: {df2.dtypes.to_dict()})")
                            info_parts.append(f"df2 ilk 3 satır: \n{df2.head(3).to_string(index=False)}")

                        data_info = "\n".join(info_parts)

                        # 2. System prompt (detaylı)
                        system_prompt = f"""Sen bir veri analizi asistanısın. Kullanıcı sana veriler üzerinde işlem yapması için doğal dilde komut verecek.
Görevin: Kullanıcının komutunu anlayıp, onu gerçekleştirecek **geçerli Python kodu** üretmek.

Kurallar:
- Sadece çalışan kod yaz, açıklama yapma.
- Kullanılabilir değişkenler: df1, df2 (eğer varsa), pd (pandas), px (plotly.express)
- Sonucu bir pandas DataFrame'ine `result_df` olarak ata.
- Eğer kullanıcı grafik istiyorsa, `fig` adında bir Plotly figürü oluştur (px kullanarak).
- Kodun sonunda `result_df` ve varsa `fig` tanımlı olmalı.
- Sütun isimlerini tam olarak kullan, hata yapma.
- DataFrame işlemleri için pandas fonksiyonlarını kullan.

Şu anki veri bilgileri:
{data_info}

Kullanıcının komutunu yerine getirecek kodu yaz. Kodun çalıştırılabilir olduğundan emin ol.
"""

                        # 3. Groq'ya ilk isteği gönder
                        client = Groq(api_key=api_key)
                        try:
                            response = client.chat.completions.create(
                                model="mixtral-8x7b-32768",
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_prompt}
                                ],
                                temperature=0.2,
                                max_tokens=2000
                            )
                            raw_code = response.choices[0].message.content

                            # 4. Kod temizliği
                            if "```python" in raw_code:
                                code = raw_code.split("```python")[1].split("```")[0].strip()
                            elif "```" in raw_code:
                                code = raw_code.split("```")[1].split("```")[0].strip()
                            else:
                                code = raw_code.strip()

                            st.code(code, language="python")

                            # 5. İlk çalıştırma denemesi
                            local_vars = {"df1": df1.copy(), "df2": df2.copy() if df2 is not None else None,
                                          "pd": pd, "px": px}
                            try:
                                exec(code, {}, local_vars)
                                result_df = local_vars.get("result_df")
                                fig = local_vars.get("fig")

                                if result_df is not None and isinstance(result_df, pd.DataFrame):
                                    st.success("✅ İşlem başarılı!")
                                    st.dataframe(result_df.head(20))
                                    if fig is not None:
                                        st.plotly_chart(fig, use_container_width=True)

                                    # İndirme butonları
                                    c1, c2 = st.columns(2)
                                    with c1:
                                        data, fname = export_file(result_df, "xlsx", "groq_sonuc")
                                        if data:
                                            st.download_button("📊 Excel", data, fname, key="g1")
                                    with c2:
                                        data, fname = export_file(result_df, "csv", "groq_sonuc")
                                        if data:
                                            st.download_button("📄 CSV", data, fname, key="g2")
                                else:
                                    st.error("❌ Kod çalıştı ama 'result_df' bulunamadı veya DataFrame değil.")

                            except Exception as exec_err:
                                # 6. Hata durumunda Groq'a hatayı gönder, düzeltmesini iste
                                st.warning(f"⚠️ İlk kod çalışmadı: {exec_err}. Düzeltme deneniyor...")
                                with st.spinner("🔄 Groq hatayı düzeltiyor..."):
                                    error_prompt = f"""Kodun çalıştırılması sırasında hata oluştu:
Hata: {exec_err}

Verilen kod:
{code}

Lütfen bu hatayı düzeltilmiş şekilde yeniden yaz. Yine sadece çalışan kodu ver.
"""
                                    retry_response = client.chat.completions.create(
                                        model="mixtral-8x7b-32768",
                                        messages=[
                                            {"role": "system", "content": "Sen bir veri analizi asistanısın. Hataları düzelt."},
                                            {"role": "user", "content": error_prompt}
                                        ],
                                        temperature=0.2,
                                        max_tokens=2000
                                    )
                                    retry_raw = retry_response.choices[0].message.content
                                    if "```python" in retry_raw:
                                        retry_code = retry_raw.split("```python")[1].split("```")[0].strip()
                                    elif "```" in retry_raw:
                                        retry_code = retry_raw.split("```")[1].split("```")[0].strip()
                                    else:
                                        retry_code = retry_raw.strip()

                                    st.code(retry_code, language="python")
                                    try:
                                        exec(retry_code, {}, local_vars)
                                        result_df = local_vars.get("result_df")
                                        fig = local_vars.get("fig")
                                        if result_df is not None and isinstance(result_df, pd.DataFrame):
                                            st.success("✅ Düzeltilmiş kod başarıyla çalıştı!")
                                            st.dataframe(result_df.head(20))
                                            if fig is not None:
                                                st.plotly_chart(fig, use_container_width=True)
                                            c1, c2 = st.columns(2)
                                            with c1:
                                                data, fname = export_file(result_df, "xlsx", "groq_sonuc")
                                                if data:
                                                    st.download_button("📊 Excel", data, fname, key="g1_retry")
                                            with c2:
                                                data, fname = export_file(result_df, "csv", "groq_sonuc")
                                                if data:
                                                    st.download_button("📄 CSV", data, fname, key="g2_retry")
                                        else:
                                            st.error("❌ Düzeltilmiş kod da çalışmadı. Lütfen komutunuzu daha açık yazın.")
                                    except Exception as retry_err:
                                        st.error(f"❌ Düzeltme de başarısız: {retry_err}")

                        except Exception as e:
                            st.error(f"❌ Groq ile iletişim hatası: {str(e)[:300]}")

    else:
        st.info("📂 Lütfen en az bir dosya yükleyin.")