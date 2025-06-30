import streamlit as st
import os

st.title("📖 API Reference")

md_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "docs", "API_REFERENCE.md")
try:
    with open(md_path, "r", encoding="utf-8") as f:
        md = f.read()
    st.markdown(md, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Could not load API_REFERENCE.md: {e}") 