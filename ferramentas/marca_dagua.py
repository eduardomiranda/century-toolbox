import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import tempfile
import os

# ----------------------
# Função para criar PDF de marca d'água
# ----------------------
def create_watermark_pdf(path, text1="CONFIDENTIAL", text2="DO NOT SHARE", pagesize=letter):
    w, h = pagesize
    c = canvas.Canvas(path, pagesize=pagesize)
    c.saveState()
    try:
        c.setFillAlpha(0.05)
    except Exception:
        pass
    c.setFillColor(colors.Color(0.8, 0.8, 0.8))
    c.setFont("Helvetica-Bold", 30)
    c.translate(w/2.0, h/2.0)
    c.rotate(45)
    c.drawCentredString(0, 40, text1)
    c.drawCentredString(0, -40, text2)
    c.restoreState()
    c.showPage()
    c.save()

# ----------------------
# Função para adicionar marca d'água
# ----------------------
def add_watermark(input_pdf, watermark_pdf, output_pdf):
    reader_in = PdfReader(input_pdf)
    reader_wm = PdfReader(watermark_pdf)
    wm_page = reader_wm.pages[0]
    writer = PdfWriter()
    for page in reader_in.pages:
        page.merge_page(wm_page)
        writer.add_page(page)
    with open(output_pdf, "wb") as f:
        writer.write(f)

# ----------------------
# Função para criptografar PDF
# ----------------------
def encrypt_pdf(input_pdf, output_pdf, password):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    with open(output_pdf, "wb") as f:
        writer.write(f)

# ----------------------
# Streamlit App
# ----------------------
st.title("🔒 Marca d'água e senha")

uploaded_pdf = st.file_uploader("Escolha um arquivo PDF", type="pdf")
texto1 = st.text_input("Texto 1 da marca d'água", "CONFIDENCIAL")
texto2 = st.text_input("Texto 2 da marca d'água", "NÃO COMPARTILHE")
senha = st.text_input("Senha para criptografia", "", type="password")

if uploaded_pdf and st.button("Gerar PDF final"):
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, "input.pdf")
        watermark_path = os.path.join(tmpdir, "watermark.pdf")
        watermarked_path = os.path.join(tmpdir, "watermarked.pdf")
        encrypted_path = os.path.join(tmpdir, "final_encrypted.pdf")

        # Salva PDF enviado
        with open(input_path, "wb") as f:
            f.write(uploaded_pdf.read())

        # Cria marca d'água
        create_watermark_pdf(watermark_path, texto1, texto2)

        # Aplica marca d'água
        add_watermark(input_path, watermark_path, watermarked_path)

        # Aplica criptografia
        encrypt_pdf(watermarked_path, encrypted_path, senha)

        # Fornece download
        with open(encrypted_path, "rb") as f:
            st.download_button(
                label="Download do PDF final",
                data=f,
                file_name="PDF_final.pdf",
                mime="application/pdf"
            )
        st.success("PDF gerado com sucesso!")
