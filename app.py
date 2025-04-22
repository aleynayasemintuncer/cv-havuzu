import streamlit as st
import requests
import fitz  # PyMuPDF
from io import BytesIO
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
import re

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.set_page_config(page_title="CV Filtreleme", layout="centered")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    selected_tab = st.sidebar.radio("👋 Hoş Geldiniz", ["📘 Hakkımızda", "🔐 Giriş Yap"])

    if selected_tab == "📘 Hakkımızda":
        st.title("İşe Alım Danışmanlığına Hoş Geldiniz")
        st.markdown("""
        İşe alım danışmanlığı alanında profesyonel destek sağlıyoruz.  
        Bu uygulama, gelen özgeçmişleri filtrelemenizi kolaylaştırmak için tasarlanmıştır.  
        Lütfen sol menüden 'Giriş Yap' seçeneğini kullanarak şifre ile erişim sağlayın.
        """)

    elif selected_tab == "🔐 Giriş Yap":
        st.title("Giriş Yap")
        password = st.text_input("🔒 Lütfen şifreyi girin", type="password")
        if password == "1119A":
            st.session_state["authenticated"] = True
            st.success("Giriş başarılı ✅")
            st.rerun()
        elif password != "":
            st.error("❌ Şifre yanlış!")
    st.stop()

# Giriş başarılıysa filtreleme sayfası
st.title("📄 CV Filtreleme Uygulaması")

st.write("Google Drive'dan PDF dosyaları çekilecek.")
st.write("🔍 Aşağıdaki filtrelere göre CV'leri listeleyebilirsiniz:")

meslek_filter = st.text_input("🧑‍💻 Meslek filtresi (örn: grafiker, mimar)").strip().lower()
adres_filter = st.text_input("🏠 Adres filtresi (örn: istanbul, ankara)").strip().lower()

drive_files = {
    "2025110.pdf": "1l9SlldjVg1N1SJa4um2oTsm4J_3xnzEt",
    "2025111.pdf": "1dryftkCJi9wmG8yYj3SbUGKWFCMDFl_U",
    "2025112.pdf": "10mYPrRLDiKuHJzqdo_dLg_6Q2-Zz6_0U"
}

def download_pdf_from_drive(file_id):
    try:
        url = f"https://drive.google.com/uc?id={file_id}"
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        st.error(f"PDF indirilemedi: {e}")
        return None

def extract_text(pdf_bytes):
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            text = "".join([page.get_text() for page in doc])
        if not text.strip():
            pdf_bytes.seek(0)
            images = convert_from_bytes(pdf_bytes.read())
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return f"PDF okunamadı: {e}"

def analyze_text(text):
    result = {}

    name_match = re.search(r"(?i)(ad[ıi]\s*:?\s*)([a-zçğıöşü\s]+)", text)
    result["Adı Soyadı"] = name_match.group(2).strip().title() if name_match else "-"

    phone_match = re.search(r"(\+90|90)?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}", text)
    result["Telefon"] = phone_match.group() if phone_match else "-"

    address_match = re.search(r"(?i)(adres|ikamet|adres bilgisi)[^\n]*\n(.+)", text)
    result["Adres"] = address_match.group(2).strip() if address_match else "-"

    education_match = re.search(r"(?i)(lisans|önlisans|yüksek lisans|lise)", text)
    result["Eğitim Durumu"] = education_match.group(0).strip().title() if education_match else "-"

    graduation_match = re.search(r"(20[0-4][0-9]|19[8-9][0-9])", text)
    result["Mezuniyet Yılı"] = graduation_match.group(0) if graduation_match else "-"

    bolum_match = re.search(r"(?i)(bölüm[:\s]*)\s*([a-zçğıöşü\s]+)", text)
    result["Bölüm"] = bolum_match.group(2).title().strip() if bolum_match else "-"

    derece_match = re.search(r"(?i)(derece|not ortalaması|gano)[:\s]*([0-9][.,]?[0-9]*)", text)
    result["Derece"] = derece_match.group(2).replace(",", ".") if derece_match else "-"

    return result

uygun_cvler = []
uymayan_cvler = []

for name, file_id in drive_files.items():
    pdf_bytes = download_pdf_from_drive(file_id)
    if not pdf_bytes:
        continue

    text = extract_text(pdf_bytes)
    if not text or text.strip() == "":
        continue

    text_lower = text.lower()
    filtre_uygun = (not meslek_filter or meslek_filter in text_lower) and \
                   (not adres_filter or adres_filter in text_lower)

    data = {
        "name": name,
        "text": text,
        "analyzed": analyze_text(text_lower),
        "uygun": filtre_uygun
    }

    if filtre_uygun:
        uygun_cvler.append(data)
    else:
        uymayan_cvler.append(data)

for data in uygun_cvler + uymayan_cvler:
    st.subheader(f"📄 {data['name']}")
    if data["uygun"]:
        st.success("📋 Aşağıda çıkarılan bilgiler yer alıyor:")
        for key, value in data["analyzed"].items():
            st.write(f"**{key}:** {value}")
    else:
        st.info("❗ Bu CV filtrelere uymuyor.")
    with st.expander("📖 İçeriği Oku"):
        st.text_area(label="", value=data["text"], height=300)
