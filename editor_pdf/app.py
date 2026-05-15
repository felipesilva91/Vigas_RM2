import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import zipfile
import io
from reportlab.pdfgen import canvas

# ================= CONFIGURAÇÃO =================
st.set_page_config(
    page_title="PDF ↔ Imagens (Alta Qualidade)",
    layout="centered"
)

st.title("PDF ↔ Imagens (Alta Qualidade)")

opcao = st.radio(
    "Escolha a função:",
    ["PDF → Imagens", "Imagens → PDF"]
)

# =================================================
# ========= PDF → IMAGENS =========================
# =================================================
if opcao == "PDF → Imagens":

    st.subheader("Converter PDF em Imagens")

    pdf_file = st.file_uploader("Upload do PDF", type=["pdf"])

    dpi = st.selectbox(
        "Qualidade da imagem (DPI)",
        options=[150, 300, 400, 600],
        index=1
    )

    if pdf_file:
        st.info("Convertendo PDF, aguarde...")

        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        imagens = []

        for page in doc:
            pix = page.get_pixmap(dpi=dpi)
            mode = "RGB" if pix.n < 4 else "RGBA"

            img = Image.frombytes(
                mode,
                (pix.width, pix.height),
                pix.samples
            )

            imagens.append(img)

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for i, img in enumerate(imagens):
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                zipf.writestr(f"pagina_{i+1}.png", img_bytes.getvalue())

        st.success(f"{len(imagens)} páginas convertidas com sucesso!")

        st.download_button(
            label="Baixar imagens (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="paginas_pdf_imagens.zip",
            mime="application/zip"
        )

# =================================================
# ========= IMAGENS → PDF =========================
# =================================================
if opcao == "Imagens → PDF":

    st.subheader("Converter Imagens em PDF (Sem Perda de Qualidade)")

    imagens_files = st.file_uploader(
        "Upload das imagens (PNG ou JPG)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if imagens_files:
        st.info("Gerando PDF em alta qualidade...")

        pdf_buffer = io.BytesIO()
        c = None

        for i, img_file in enumerate(imagens_files):
            img = Image.open(img_file).convert("RGB")

            largura, altura = img.size  # pixels

            # Cria o PDF com o tamanho EXATO da imagem
            if c is None:
                c = canvas.Canvas(pdf_buffer, pagesize=(largura, altura))

            c.setPageSize((largura, altura))
            c.drawInlineImage(img, 0, 0, largura, altura)
            c.showPage()

        c.save()

        st.success("PDF gerado com sucesso!")

        st.download_button(
            label="Baixar PDF",
            data=pdf_buffer.getvalue(),
            file_name="imagens_alta_qualidade.pdf",
            mime="application/pdf"
        )
