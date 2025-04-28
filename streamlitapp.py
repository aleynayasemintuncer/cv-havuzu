import streamlit as st
import requests
from io import BytesIO
import fitz
from PIL import Image
import pytesseract
import re
from pdf2image import convert_from_bytes
from datetime import datetime

# 1. İlk olarak page config veriyoruz
st.set_page_config(page_title="HRDanışmanım.com", layout="wide")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Kullanıcı adı ve şifre verisi
kullanici_verisi = {
    "aleynayasemintuncer@gmail.com": "1119A",
    "musteri2@gmail.com": "abcd1234"
}

# Session State başlat
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "selected_page_redirect" not in st.session_state:
    st.session_state["selected_page_redirect"] = None
if "adaylar" not in st.session_state:
    st.session_state["adaylar"] = []
if "talepler" not in st.session_state:
    st.session_state["talepler"] = []
if "formlar" not in st.session_state:
    st.session_state["formlar"] = []

# Menü
selected_page = st.sidebar.radio("📂 Menü", [
    "🏠 Anasayfa",
    "📖 Hakkımızda",
    "👩‍💼 İK Portalı",
    "🏢 Şirket Portalı",
    "🚀 Whitepace - İş Arayanlar"
])


# Google Drive'daki CV Dosyaları
drive_files = {
    "2025110.pdf": "1l9SlldjVg1N1SJa4um2oTsm4J_3xnzEt",
    "2025111.pdf": "1dryftkCJi9wmG8yYj3SbUGKWFCMDFl_U",
    "2025112.pdf": "10mYPrRLDiKuHJzqdo_dLg_6Q2-Zz6_0U"
}

# Sayfalar
if selected_page == "🏠 Anasayfa":
    st.title("🏠 Hoş Geldiniz")
    st.markdown("""  
    İnsan Kaynakları ve Aday Portallarımıza hoş geldiniz!  
    Sol menüden istediğiniz bölüme geçiş yapabilirsiniz.
    """)

# İletişim Formu Başlığı
    st.subheader("İletişim Formu")
    
    # Formu başlatıyoruz
    with st.form(key='contact_form'):
        # Adı Soyadı
        name = st.text_input("Adı Soyadı")
        
        # Telefon Numarası
        phone = st.text_input("Telefon Numarası")
        
        # Mail Adresi
        email = st.text_input("E-posta Adresi")
        
        # Konu
        subject = st.text_area("Konu")
        
        # Formu gönder butonu
        submit_button = st.form_submit_button(label="Gönder")

    # Form gönderildiyse
    if submit_button:
        # Verileri st.session_state'de tutma
        if "formlar" not in st.session_state:
            st.session_state["formlar"] = []

        # Form verisini kaydet
        st.session_state["formlar"].append({
            "Adı Soyadı": name,
            "Telefon Numarası": phone,
            "E-posta Adresi": email,
            "Konu": subject
        })
        
        # Kullanıcıya teşekkür mesajı
        st.write("Form başarıyla gönderildi. Teşekkürler!")

# İK Portalı ve diğer sayfalarda sekme seçim kodu
if selected_page == "👩‍💼 İK Portalı":
    sekme = st.radio("Sekme Seçiniz", ["Adaylar", "Müşteriler", "Formlar"])

elif selected_page == "📖 Hakkımızda":
    st.title("📖 Hakkımızda")
    st.markdown("""  
    Biz, şirketlere ve adaylara özel İK çözümleri sunan bir danışmanlık platformuyuz.  
    İşe alım süreçlerinizi hızlandırmak ve doğru adaya ulaşmak için buradayız.

    ### Neden Biz?
    - Yılların tecrübesi
    - Özelleştirilmiş çözümler
    - Çalışan odaklı yaklaşım
    """)

# İK Portalı giriş kontrolü
if selected_page == "👩‍💼 İK Portalı":
    if "authenticated_ik" not in st.session_state:
        st.session_state["authenticated_ik"] = False

    if not st.session_state["authenticated_ik"]:
        st.title("🔐 İK Portalı Girişi")
        password = st.text_input("Şifre", type="password")
        if password == "1119A":
            st.session_state["authenticated_ik"] = True
            st.success("Giriş başarılı ✅")
            st.rerun()  # Yeniden yükle
        elif password != "":
            st.error("Şifre yanlış!")
        st.stop()  # Sayfada ilerlemeyi durdur

    st.title("👩‍💼 İK Portalı - CV Filtreleme ve Başvuran Adaylar")

# İK Portalı sekme seçim kodu burada olmalı:
if selected_page == "👩‍💼 İK Portalı":
    sekme = st.radio("Sekme Seçiniz", ["Adaylar", "Müşteriler", "Formlar"])

if sekme == "Adaylar":

        st.title("🧑‍🎓 İş Arayanlar (Adaylar)")

        st.subheader("Başvuran Adaylar")
        if st.session_state["Adaylar"]:
            for idx, aday in enumerate(st.session_state["adaylar"], 1):
                st.write(f"**{idx}. {aday['Adı Soyadı']}**")
                st.write(f"Telefon: {aday['Telefon']}")
                st.write(f"Email: {aday['Email']}")
                st.write(f"Meslek: {aday['Meslek']}")
                st.write(f"Başvuru Tarihi: {aday['Başvuru Tarihi']}")
                st.write("----")
        else:
            st.write("Başvuru yapılmış aday bulunmamaktadır.")

        st.subheader("Google Drive'daki CV Dosyaları")
        for filename, fileid in drive_files.items():
            url = f"https://drive.google.com/uc?id={fileid}"
            st.markdown(f"[{filename}]({url})", unsafe_allow_html=True)

        # Filtreleme bölümü
        st.subheader("📄 CV Filtreleme")
        meslek_filter = st.text_input("🧑‍💻 Meslek filtresi (örn: grafiker, mimar)").strip().lower()
        adres_filter = st.text_input("🏠 Adres filtresi (örn: istanbul, ankara)").strip().lower()

        st.info("Bu alanlar ilerde PDF içerisinden veri çıkararak filtreleme yapacak şekilde geliştirilebilir.")

if sekme == "Müşteriler":
        st.title("📑 Müşteri Dosyaları")
        for filename, fileid in drive_files.items():
            url = f"https://drive.google.com/uc?id={fileid}"
            st.markdown(f"[{filename}]({url})", unsafe_allow_html=True)

elif sekme == "Formlar":
    st.title("📝 İletişim Formları")
    st.subheader("Gönderilen Formlar")
    
    if st.session_state["formlar"]:
        for form in st.session_state["formlar"]:
            st.write(f"**Adı Soyadı:** {form['Adı Soyadı']}")
            st.write(f"**Telefon Numarası:** {form['Telefon Numarası']}")
            st.write(f"**E-posta Adresi:** {form['E-posta Adresi']}")
            st.write(f"**Konu:** {form['Konu']}")
            st.write("---")  # Her formu ayıran bir çizgi
    else:
        st.write("Henüz bir form gönderilmedi.")
# Şirket Portalı
if selected_page == "🏢 Şirket Portalı":
    # Session State başlatma
    if "authenticated_sirket" not in st.session_state:
        st.session_state["authenticated_sirket"] = False
    if not st.session_state["authenticated_sirket"]:
        st.title("🔐 Şirket Portalı Girişi")
        password = st.text_input("Şifre", type="password")
        if password == "abcd1234":
            st.session_state["authenticated_sirket"] = True
            st.success("Giriş başarılı ✅")
            st.rerun()  # Yeniden yükle
        elif password != "":
            st.error("Şifre yanlış!")
        st.stop()  # Sayfada ilerlemeyi durdur

# İK Portalına giriş yapılmamışsa, uyarı göster
        st.warning("İK Portalına giriş yetkiniz yok!")
        st.stop()

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

    st.divider()
    st.header("📝 Yeni Talep Oluştur")
    with st.form("talep_formu"):
        pozisyon = st.text_input("Pozisyon Adı *")
        departman = st.text_input("Departman *")
        lokasyon = st.text_input("İş Lokasyonu *")
        aciliyet = st.selectbox("Aciliyet Durumu *", ["Acil", "Normal", "Uzun Vadeli"])
        detaylar = st.text_area("Pozisyon Detayları *")
        submit_button = st.form_submit_button("Talebi Gönder")

    if submit_button:
        yeni_talep = {
            "Pozisyon": pozisyon,
            "Departman": departman,
            "Lokasyon": lokasyon,
            "Aciliyet": aciliyet,
            "Detaylar": detaylar
        }
        st.session_state["talepler"].append(yeni_talep)
        st.success("✅ Talebiniz başarıyla iletildi!")

    st.divider()
    st.subheader("📜 Taleplerim")
    if st.session_state["talepler"]:
        for idx, talep in enumerate(st.session_state["talepler"], 1):
            st.write(f"{idx}. {talep['Pozisyon']} - {talep['Departman']} - {talep['Lokasyon']} ({talep['Aciliyet']})")

    
# Sayfalar
if selected_page == "🚀 Whitepace - İş Arayanlar":
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