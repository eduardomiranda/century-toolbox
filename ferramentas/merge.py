import io

import pypdfium2 as pdfium
import streamlit as st
from pypdf import PdfReader, PdfWriter

COLS = 4

st.title("📎 Merge de PDFs")
st.write("Envie dois ou mais PDFs, ajuste a ordem e baixe o arquivo combinado.")


@st.cache_data(show_spinner=False)
def cover(data: bytes):
    """Renderiza a primeira página como imagem e devolve (imagem, nº de páginas)."""
    pdf = pdfium.PdfDocument(data)
    page = pdf[0]
    image = page.render(scale=400 / page.get_width()).to_pil()
    return image, len(pdf)


def move(i: int, delta: int):
    order = st.session_state.order
    order[i], order[i + delta] = order[i + delta], order[i]


files = st.file_uploader("PDFs", type="pdf", accept_multiple_files=True)
by_id = {f.file_id: f for f in files or []}

# Mantém a ordem escolhida, removendo arquivos excluídos e anexando os novos no fim.
order = [fid for fid in st.session_state.get("order", []) if fid in by_id]
order += [fid for fid in by_id if fid not in order]
st.session_state.order = order

if files:
    st.subheader("Ordem")
    for row in range(0, len(order), COLS):
        for col, i in zip(st.columns(COLS), range(row, min(row + COLS, len(order)))):
            f = by_id[order[i]]
            with col.container(border=True):
                try:
                    image, pages = cover(f.getvalue())
                    st.columns([1, 2, 1])[1].image(image, use_container_width=True)
                    caption = f"{pages} página{'s' if pages > 1 else ''}"
                except Exception:
                    st.warning("Não foi possível gerar a prévia.")
                    caption = ""
                st.markdown(f"**{i + 1}.** {f.name}")
                st.caption(caption)
                left, right = st.columns(2)
                left.button("◀", key=f"l{f.file_id}", disabled=i == 0,
                            on_click=move, args=(i, -1), use_container_width=True)
                right.button("▶", key=f"r{f.file_id}", disabled=i == len(order) - 1,
                             on_click=move, args=(i, 1), use_container_width=True)

    output_name = st.text_input("Nome do arquivo final", "merged.pdf")

    if st.button("Combinar PDFs", type="primary", disabled=len(files) < 2):
        writer = PdfWriter()
        for fid in order:
            f = by_id[fid]
            try:
                writer.append(PdfReader(io.BytesIO(f.getvalue())))
            except Exception as e:
                st.error(f"Erro ao ler {f.name}: {e}")
                st.stop()

        buffer = io.BytesIO()
        writer.write(buffer)
        st.success(f"{len(writer.pages)} páginas combinadas.")
        st.download_button(
            "Baixar PDF",
            buffer.getvalue(),
            file_name=output_name if output_name.endswith(".pdf") else f"{output_name}.pdf",
            mime="application/pdf",
        )
