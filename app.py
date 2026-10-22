import streamlit as st

st.set_page_config(page_title="Century Toolbox", page_icon="🧰", layout="wide")

st.navigation([
    st.Page("ferramentas/merge.py", title="Merge de PDFs", icon="📎", default=True),
    st.Page("ferramentas/marca_dagua.py", title="Marca d'água e senha", icon="🔒"),
]).run()
