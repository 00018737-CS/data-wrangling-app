import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="AI Data Wrangler", 
    page_icon="", 
    layout="wide"
)

if 'df' not in st.session_state:
    st.session_state.df = None
if 'original_filename' not in st.session_state:
    st.session_state.original_filename = "dataset"
if 'log' not in st.session_state:
    st.session_state.log = []

st.sidebar.title("Navigation")
st.sidebar.write("AI-Assisted Data Wrangler & Visualizer")

page = st.sidebar.radio(
    "Go to:", 
    [
        "Page A — Upload & Overview",
        "Page B — Cleaning Studio",
        "Page C — Visualization Builder",
        "Page D — Export & Report"
    ]
)

st.sidebar.markdown("---")

if st.sidebar.button("Reset Entire Session", type="primary", use_container_width=True):
    st.session_state.clear()
    st.cache_data.clear()
    st.rerun()


if page == "Page A — Upload & Overview":
    try:
        from modules import page_a
        page_a.render()
    except ImportError:
        st.error("Page A module is missing or could not be loaded.")

elif page == "Page B — Cleaning Studio":
    try:
        from modules import page_b
        page_b.render()
    except ImportError as e:
        st.error(f"Page B module error: {e}")

elif page == "Page C — Visualization Builder":
    try:
        from modules import page_c
        page_c.render()
    except ImportError:
        st.error("Page C module is missing.")

elif page == "Page D — Export & Report":
    try:
        from modules import page_d
        page_d.render()
    except ImportError:
        st.info("Page D (Export) module is under construction.")