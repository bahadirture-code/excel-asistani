import streamlit as st
import pandas as pd
import io
import re

try:
    from groq import Groq
    HAS_GROQ = True
except Exception:
    HAS_GROQ = False

st.set_page_config(page_title="AI Veri Asistanı", layout="wide", page_icon="🧠")

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

def extract_code(text):
    """Kod bloğunu ayıklar"""
    pattern = r"```python\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Eğer ```python yoksa, sadece kod olabilecek metni al
    return text.strip()

def ask_ai(client, prompt, df_dict):
    """AI'ya soru sor ve yanıt al"""
    df_list_str = ", ".join([f"{k}: {list(v.columns)}" for k, v in df_dict.items()])
    sys_msg = f"""Sen bir Python/Pandas uzmanısın. Kullanıcının doğal dildeki isteğini anla ve cevap ver.

Mevcut DataFrame'ler:
{df_list_str}

Kullanıcı net bir şekilde ne yapmak istediğini söylemediyse veya sütun isimlerinde emin olamadıysan, mutlaka soru sor. Örneğin:
- "Hangi sütunu kastediyorsunuz?"
- "df1 ve df2'yi hangi anahtarla birleştirelim?"
- "Ortalama mı, toplam mı almak istiyorsunuz?"

Eğer komut netse, cevabında sadece Python kodu döndür ve ```python``` blokları içine al.
Kodun sonucu 'result_df' değişkenine atanmalı.

Kullanıcıya hitap ederken Türkçe konuş.
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"HATA: {e}"

# ==========================
# OTURUM DURUMU
# ==========================
if 'file_data' not in st.session_state:
    st.session_state.file_data = {}  # {dosya_adı: {'bytes': bytes, 'sheets': list, 'selected_sheet': str, 'df': DataFrame}}
if 'conversation' not in st.session_state:
    st.session_state.conversation = []  # [{'role': 'user'/'assistant', 'content': str}]

st.title("🧠 AI Veri Asistanı")
st.markdown("Dosyalarını yükle, doğal dilde ne istediğini söyle, AI seni anlamadığında sana sorar ve sonucu oluşturur.")

# ==========================
# DOSYA YÜKLEME
# ==========================
uploaded_files = st.file_uploader(
    "Dosyaları yükleyin (Excel/CSV)",
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
                    selected_sheet = sheets[0]
            st.session_state.file_data[file.name] = {
                'bytes': file_bytes,
                'sheets': sheets,
                'selected_sheet': selected_sheet,
                'df': None
            }

# ==========================
# DOSYA GÖSTERİMİ VE SAYFA SEÇİMİ
# ==========================
if st.session_state.file_data:
    st.subheader("📁 Dosyalarım")
    for name, data in st.session_state.file_data.items():
        with st.expander(f"📄 {name}", expanded=False):
            if data['sheets']:
                current_sheet = data['selected_sheet'] if data['selected_sheet'] else data['sheets'][0]
                selected_sheet = st.selectbox(
                    f"Sayfa seç ({name})",
                    options=data['sheets'],
                    index=data['sheets'].index(current_sheet) if current_sheet in data['sheets'] else 0,
                    key=f"sheet_{name}"
                )
                if data['selected_sheet'] != selected_sheet or data['df'] is None:
                    data['selected_sheet'] = selected_sheet
                    data['df'] = load_file(data['bytes'], name, sheet_name=selected_sheet)
                    if data['df'] is not None:
                        st.success(f"✅ '{selected_sheet}' yüklendi ({data['df'].shape[0]} satır, {data['df'].shape[1]} sütun)")
            else:
                if data['df'] is None:
                    data['df'] = load_file(data['bytes'], name)
                    if data['df'] is not None:
                        st.success(f"✅ {name} yüklendi")

            if data['df'] is not None:
                st.dataframe(data['df'].head(5), use_container_width=True)

# ==========================
# AI SOHBET ALANI
# ==========================
st.markdown("---")
st.header("💬 Yapay Zeka ile Konuş")

if not HAS_GROQ:
    st.warning("Groq yüklü değil. `pip install groq`")
else:
    # Mevcut df'leri kontrol et
    available_dfs = {name: data['df'] for name, data in st.session_state.file_data.items() if data['df'] is not None}
    if not available_dfs:
        st.info("📂 Lütfen önce dosya yükleyin ve bir sayfa seçin.")
    else:
        # Kullanıcı hangi dosyaları kullanacağını seçsin
        secili_dosyalar = st.multiselect(
            "Hangi dosyaları kullanmak istersiniz?",
            options=list(available_dfs.keys()),
            default=list(available_dfs.keys())
        )

        if secili_dosyalar:
            # Kullanıcı sohbet geçmişini göster
            for msg in st.session_state.conversation:
                with st.chat_message(msg['role']):
                    st.write(msg['content'])

            # Yeni mesaj
            user_prompt = st.chat_input("Ne yapmak istediğini yaz (Türkçe veya İngilizce)")

            if user_prompt:
                # Kullanıcı mesajını ekle
                st.session_state.conversation.append({'role': 'user', 'content': user_prompt})
                with st.chat_message('user'):
                    st.write(user_prompt)

                # AI yanıtı
                with st.chat_message('assistant'):
                    with st.spinner("🤔 Düşünüyorum..."):
                        # Sadece seçili dosyaları df_dict'e ekle
                        df_dict = {}
                        for idx, name in enumerate(secili_dosyalar, start=1):
                            df_dict[f"df{idx}"] = available_dfs[name].copy()

                        # AI'ya sor
                        full_response = ask_ai(st.session_state.get('groq_client'), user_prompt, df_dict)

                        # AI yanıtını ekrana yaz
                        st.write(full_response)

                        # Eğer yanıtta kod varsa, çalıştırmayı dene
                        code = extract_code(full_response)
                        if code and "result_df" in code and not any(soru_kelime in full_response.lower() for soru_kelime in ["?", "hangi", "nedir", "nasıl"]):
                            # Soru yoksa ve kod varsa çalıştır
                            try:
                                local_vars = {**df_dict, "pd": pd}
                                exec(code, {}, local_vars)
                                result_df = local_vars.get("result_df")
                                if result_df is not None and isinstance(result_df, pd.DataFrame):
                                    st.success("✅ İşlem başarılı!")
                                    st.dataframe(result_df.head(10), use_container_width=True)
                                    # İndirme butonları
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        excel_data, excel_fname = export_file(result_df, "xlsx", "sonuc")
                                        if excel_data:
                                            st.download_button("📊 Excel indir", excel_data, excel_fname, key="ai_excel")
                                    with col2:
                                        csv_data, csv_fname = export_file(result_df, "csv", "sonuc")
                                        if csv_data:
                                            st.download_button("📄 CSV indir", csv_data, csv_fname, key="ai_csv")
                                else:
                                    st.warning("Kod çalıştı ama 'result_df' oluşmadı. Belki AI soru sormuş olabilir.")
                            except Exception as e:
                                st.error(f"❌ Kod çalıştırma hatası: {e}")
                                st.code(code, language="python")
                        elif code and any(soru_kelime in full_response.lower() for soru_kelime in ["?", "hangi", "nedir", "nasıl"]):
                            # AI soru sormuş, kod varsa da sadece soruyu göster, çalıştırma
                            st.info("AI soru sordu. Lütfen cevaplayın.")
                            with st.expander("Kod (sadece bilgi)"):
                                st.code(code, language="python")
                        else:
                            # Kod yok veya result_df yok, mesajı göster
                            st.info("AI cevabı yukarıda. Kod üretilmedi veya doğrudan yanıt verdi.")

                        # Yanıtı geçmişe ekle
                        st.session_state.conversation.append({'role': 'assistant', 'content': full_response})

            # Eğer API key yoksa, kullanıcıya söyle
            if 'groq_client' not in st.session_state:
                try:
                    api_key = st.secrets.get("GROQ_API_KEY")
                    if api_key:
                        st.session_state.groq_client = Groq(api_key=api_key)
                except:
                    st.warning("GROQ_API_KEY secrets'ta tanımlı değil veya geçersiz. Lütfen ekleyin.")