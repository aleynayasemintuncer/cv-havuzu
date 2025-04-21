import streamlit as st
import fitz  # PyMuPDF

# Şifre Giriniz
SECRET_PASSWORD = "your_secret_password"  # Burada şifrenizi girin

# Uygulamanın başında kullanıcıdan şifre isteniyor
password = st.text_input("Şifrenizi girin", type="password")

# Şifre doğruysa içeriği gösteriyoruz, yanlışsa hata mesajı veriyoruz
if password == SECRET_PASSWORD: 1119A
    st.write("Şifre doğru! Uygulamaya erişiyorsunuz.")
    # Burada asıl uygulamanızın geri kalan kısmını ekleyebilirsiniz
else:
    if password:
        st.error("Yanlış şifre! Lütfen tekrar deneyin.")

st.set_page_config(page_title="CV Filtreleme", layout="centered")

st.title("📄 CV Filtreleme Uygulaması")
st.write("PDF CV'leri yükleyin ve aşağıdaki alandan anahtar kelimelerle filtreleyin.")
st.write("🔍 Anahtar kelimeleri virgül ile ayırarak girin (örn: photoshop, illustrator, sosyal medya)")

# Anahtar kelime giriş kutusu
keywords = st.text_input("Anahtar Kelimeler")

# Dosya yükleme alanı
uploaded_files = st.file_uploader("Bir veya birden fazla PDF dosyası yükleyin", type="pdf", accept_multiple_files=True)

# PDF'ten metin çıkarma fonksiyonu
def extract_text_from_pdf(pdf_file):
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        return "".join([page.get_text() for page in doc])

# Dosya varsa işle
if uploaded_files:
    filtered_keywords = [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]
    st.markdown("### 🔍 Eşleşen CV'ler:")

    for uploaded_file in uploaded_files:
        text = extract_text_from_pdf(uploaded_file).lower()
        if all(kw in text for kw in filtered_keywords):
            st.success(f"✅ {uploaded_file.name} eşleşti!")
            with st.expander("📄 İçeriği Göster"):
                st.text_area(label="", value=text, height=300)
        else:
            st.warning(f"❌ {uploaded_file.name} eşleşmedi.")
