import streamlit as st
import fitz  # PyMuPDF
import requests
from io import BytesIO
from urllib.parse import unquote

st.set_page_config(page_title="CV Filtreleme", layout="centered")

# --- Şifreli Giriş ---
if "password" not in st.session_state:
    st.session_state["password"] = ""

if st.session_state["password"] != "1119A":
    st.text_input("🔒 Lütfen şifreyi girin", type="password", key="password")
    st.warning("Uygulamaya erişmek için şifre girmeniz gerekiyor.")
    st.stop()

st.title("📄 CV Filtreleme Uygulaması")
st.write("PDF CV'leri otomatik olarak yüklenecek. Aşağıdaki alandan anahtar kelimelerle filtreleyin.")
st.write("🔍 Anahtar kelimeleri virgül ile ayırarak girin (örn: photoshop, illustrator, sosyal medya)")

# Anahtar kelimeleri al
keywords = st.text_input("Filtrelemek istediğiniz anahtar kelimeleri virgülle ayırarak girin").lower()
filtered_keywords = [kw.strip() for kw in keywords.split(",") if kw.strip()]

# GitHub klasöründeki PDF dosyalarının bağlantıları
pdf_urls = [
    "https://github.com/aleynayasemintuncer/-zge-mi-havuzu/raw/main/pdfler/ZeynepTopal%20CV..pdf"
]

st.subheader("📁 GitHub'dan Otomatik Yüklenen PDF'ler")

# PDF’lerden metin çıkarma
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        pdf_stream = BytesIO(response.content)
        with fitz.open(stream=pdf_stream, filetype="pdf") as doc:
            return "".join([page.get_text() for page in doc])
    except Exception as e:
        return f"PDF okunamadı: {e}"

# PDF’leri listele ve filtrele
for i, url in enumerate(pdf_urls):
    filename = unquote(url.split("/")[-1])  # URL'den gerçek dosya adını çöz
    text = extract_text_from_url(url).lower()

    if not filtered_keywords or all(kw in text for kw in filtered_keywords):
        st.success(f"📄 {filename}")
        with st.expander("İçeriği Gör"):
            st.text_area(label="", value=text, height=300, key=f"text_{i}")
