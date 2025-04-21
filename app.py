import streamlit as st
import fitz  # PyMuPDF

st.set_page_config(page_title="CV Filtreleme", layout="centered")

st.title("📄 CV Filtreleme Uygulaması")
st.write("PDF CV'leri yükleyin ve aşağıdaki alandan anahtar kelimelerle filtreleyin.")

# Anahtar kelime girişi alanı
anahtar = st.text_input("🔍 Anahtar kelimeleri virgül ile ayırarak girin (örn: photoshop, illustrator, sosyal medya)")

# Dosya yükleme alanı
uploaded_files = st.file_uploader("📂 Bir veya birden fazla PDF dosyası yükleyin", type="pdf", accept_multiple_files=True)

# PDF'ten metin çıkaran fonksiyon
def extract_text_from_pdf(pdf_file):
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        return "".join(page.get_text() for page in doc)

# Anahtar kelimeleri listeye çevir
anahtar_kelimeler = [k.strip().lower() for k in anahtar.split(",") if k.strip()]

# Dosyalar yüklendiyse
if uploaded_files:
    for dosya in uploaded_files:
        icerik = extract_text_from_pdf(dosya).lower()

        if not anahtar_kelimeler:
            st.subheader(f"📄 {dosya.name}")
            st.text_area("İçerik:", value=icerik, height=250)
        else:
            if all(kelime in icerik for kelime in anahtar_kelimeler):
                st.subheader(f"✅ {dosya.name} - EŞLEŞTİ")
                st.text_area("İçerik:", value=icerik, height=250)
            else:
                st.write(f"❌ {dosya.name} - eşleşmedi.")
