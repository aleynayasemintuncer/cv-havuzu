import streamlit as st
import requests
import fitz  # PyMuPDF
from io import BytesIO
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
import re
from datetime import datetime

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Sayfa ayarı
st.set_page_config(page_title="İK ve Aday Portalları", layout="wide")

# Session State başlat
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "adaylar" not in st.session_state:
    st.session_state["adaylar"] = []
if "selected_page_redirect" in st.session_state:
    selected_page = st.session_state.pop("selected_page_redirect")
else:
    selected_page = st.sidebar.radio("📂 Menü", [
        "🚀 Whitepace Landing Page",
        "🏠 Anasayfa",
        "📖 Hakkımızda",
        "👩‍💼 İK Portalı",
        "🏢 Şirket Portalı",
        "🧑‍🎓 Aday Portalı"
    ])

# Sayfalar
if selected_page == "🚀 Whitepace Landing Page":
    st.title("🚀 Whitepace - İşe Alım Danışmanlığı Platformu")
    st.markdown('''
    **Whitepace**, işe alım süreçlerinizi hızlandıran ve kolaylaştıran modern bir **SaaS platformudur**.  
    Yüksek kaliteli adaylara ulaşmak ve iş gücü ihtiyaçlarınızı en hızlı şekilde karşılamak için bizimle çalışın.
    ''')

    st.image("https://images.unsplash.com/photo-1606326608692-074e0b21bf00", use_container_width=True)

    st.markdown("## Hemen Başlayın!")

    if st.button("Başvurunuzu Yapın"):
        st.success("Başvuru formuna yönlendiriliyorsunuz...")
        st.session_state["selected_page_redirect"] = "🧑‍🎓 Aday Portalı"
        st.rerun()

    st.markdown("---")
    st.caption("© 2025 Whitepace. Tüm Hakları Saklıdır.")

elif selected_page == "🏠 Anasayfa":
    st.title("🏠 Hoş Geldiniz")
    st.markdown("""
    İnsan Kaynakları ve Aday Portallarımıza hoş geldiniz!  
    Sol menüden istediğiniz bölüme geçiş yapabilirsiniz.
    """)

elif selected_page == "📖 Hakkımızda":
    st.title("📖 Hakkımızda")
    st.markdown("""
    Biz, şirketlere ve adaylara özel İK çözümleri sunan bir danışmanlık platformuyuz.  
    İşe alım süreçlerinizi hızlandırmak ve doğru adaya ulaşmak için buradayız.
    """)

elif selected_page == "👩‍💼 İK Portalı":
    if not st.session_state["authenticated"]:
        st.title("🔐 İK Portalı Girişi")
        password = st.text_input("Şifre", type="password")
        if password == "1119A":
            st.session_state["authenticated"] = True
            st.success("Giriş başarılı ✅")
            st.rerun()
        elif password != "":
            st.error("Şifre yanlış!")
        st.stop()

    st.title("👩‍💼 İK Portalı - CV Filtreleme ve Başvuran Adaylar")

    st.subheader("📄 CV Filtreleme")
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
        filtre_uygun = (not meslek_filter or meslek_filter in text_lower) and (not adres_filter or adres_filter in text_lower)

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

    st.divider()
    st.subheader("🧑‍🎓 Özgeçmişini İleten Adaylar")

    if st.session_state["adaylar"]:
        for aday in st.session_state["adaylar"]:
            st.subheader(f"📄 {aday['Adı Soyadı']}")
            st.markdown("✅ **Özgeçmişini ileten aday**")
            st.write(f"**Başvuru Tarihi:** {aday['Başvuru Tarihi']}")
            st.write(f"**Telefon:** {aday['Telefon']}")
            st.write(f"**E-posta:** {aday['Email']}")
            st.write(f"**İl/İlçe:** {aday['İl']} / {aday['İlçe']}")
            st.write(f"**Okul/Bölüm:** {aday['Okul Adı']} / {aday['Bölüm']}")
            st.write(f"**Son İş Yeri:** {aday['İşyeri Adı']}")
            st.write(f"**Meslek:** {aday['Meslek']}")
            st.write(f"**Giriş Tarihi:** {aday['Giriş Tarihi']}")
            st.write(f"**Çıkış Tarihi:** {aday['Çıkış Tarihi']}")
            st.write(f"**Görev Tanımı:** {aday['Görev Tanımı']}")
            st.write(f"**Maaş Beklentisi:** {aday['Maaş Beklentisi']}")
            st.write(f"**Ön Yazı:** {aday['Ön Yazı']}")
    else:
        st.info("Henüz başvuran aday bulunmamaktadır.")

elif selected_page == "🏢 Şirket Portalı":
    st.title("🏢 Şirket Portalı")
    st.header("🚀 Hoşgeldiniz Paketleri")
    st.write("- Başlangıç Paketi")
    st.write("- Profesyonel Paket")
    st.write("- Kurumsal Paket")
    st.divider()
    st.header("📊 Dashboard")
    st.write("- İstihdam Edilenler")
    st.write("- Değerlendirmeye Alınanlar")
    st.write("- İşe Alım Maliyetleri")
    st.write("- Yeni Talep Oluştur")
    st.write("- Taleplerim")

elif selected_page == "🧑‍🎓 Aday Portalı":
    st.title("🧑‍🎓 Aday Başvuru Portalı")

    st.markdown("Aşağıdaki formu doldurarak iş başvurunuzu yapabilirsiniz.")

    with st.form(key="basvuru_formu"):
        adi_soyadi = st.text_input("Adı Soyadı")
        fotograf = st.file_uploader("Fotoğraf Yükle", type=["jpg", "jpeg", "png"])
        telefon = st.text_input("Telefon Numarası")
        email = st.text_input("E-posta")
        il = st.text_input("Yaşadığı İl")
        ilce = st.text_input("Yaşadığı İlçe")
        okul_adi = st.text_input("Mezun Olduğu Okul")
        bolum = st.text_input("Bölüm")
        isyeri_adi = st.text_input("Son İşyeri Adı")
        meslek = st.text_input("Mesleği")
        giris_tarihi = st.date_input("İşe Giriş Tarihi")
        cikis_tarihi = st.date_input("İşten Çıkış Tarihi")
        gorev_tanimi = st.text_area("Görev Tanımı")
        maas_beklentisi = st.text_input("Maaş Beklentisi")
        on_yazi = st.text_area("Ön Yazı")
        submit_button = st.form_submit_button("🚀 Başvuruyu Gönder")

    if submit_button:
        yeni_aday = {
            "Adı Soyadı": adi_soyadi,
            "Telefon": telefon,
            "Email": email,
            "İl": il,
            "İlçe": ilce,
            "Okul Adı": okul_adi,
            "Bölüm": bolum,
            "İşyeri Adı": isyeri_adi,
            "Meslek": meslek,
            "Giriş Tarihi": str(giris_tarihi),
            "Çıkış Tarihi": str(cikis_tarihi),
            "Görev Tanımı": gorev_tanimi,
            "Maaş Beklentisi": maas_beklentisi,
            "Ön Yazı": on_yazi,
            "Başvuru Tarihi": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        st.session_state["adaylar"].append(yeni_aday)
        st.success("✅ Başvurunuz alınmıştır. Teşekkür ederiz!")

        if fotograf:
            st.image(fotograf, width=150, caption="Yüklenen Fotoğraf")
