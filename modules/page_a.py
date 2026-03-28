import streamlit as st
import pandas as pd
import re

@st.cache_data
def load_data(file):
    filename = file.name
    try:
        if filename.endswith('.csv'):
            return pd.read_csv(file)
        elif filename.endswith('.xlsx'):
            return pd.read_excel(file)
        elif filename.endswith('.json'):
            return pd.read_json(file)
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        return None

def convert_google_sheets_url(url: str) -> str | None:

    if "docs.google.com/spreadsheets" not in url:
        return None

    if "/export" in url and "format=csv" in url:
        return url

    id_match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url)
    if not id_match:
        return None
    spreadsheet_id = id_match.group(1)


    gid_match = re.search(r"[?&#]gid=(\d+)", url)
    gid = gid_match.group(1) if gid_match else "0"

    return (
        f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        f"/export?format=csv&gid={gid}"
    )

@st.cache_data
def load_google_sheet(export_url: str) -> pd.DataFrame | None:
    """Download a public Google Sheet as a CSV and return a DataFrame."""
    try:
        df = pd.read_csv(export_url)
        return df
    except Exception as e:
        st.error(
            f"Could not load Google Sheet. "
            f"Make sure the sheet is shared as 'Anyone with the link'. "
            f"\n\nDetails: {e}"
        )
        return None

def render():
    st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.04);
    }
    </style>
    """, unsafe_allow_html=True)

    col_title, col_reset = st.columns([4, 1])
    with col_title:
        st.title("Data Overview")
    with col_reset:
        st.write("")  
        if st.button("Reset Session", use_container_width=True):
            st.session_state.df = None
            st.session_state.log = []
            st.cache_data.clear()
            st.rerun()

    with st.container(border=True):
        st.subheader("1. Import Dataset")

        col_file, col_url = st.columns(2)
        with col_file:
            uploaded_file = st.file_uploader(
                "Upload local file (CSV, Excel, JSON)",
                type=["csv", "xlsx", "json"],
                label_visibility="collapsed",
            )
        with col_url:
            sheets_url = st.text_input(
                "Or paste Google Sheets link (must be public):",
                placeholder="https://docs.google.com/spreadsheets/d/...",
            )

        if sheets_url:
            export_url = convert_google_sheets_url(sheets_url)
            if export_url is None:
                st.warning(
                    "That doesn't look like a Google Sheets URL. "
                    "Paste the link from File → Share → Copy link inside Google Sheets.")
            else:
                st.caption(f"Resolved export URL: {export_url}")

    df = None

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        if df is not None:
            st.session_state.original_filename = uploaded_file.name.rsplit(".", 1)[0]

    elif sheets_url:
        export_url = convert_google_sheets_url(sheets_url)
        if export_url:
            with st.spinner("Fetching Google Sheet…"):
                df = load_google_sheet(export_url)
            if df is not None:
                st.session_state.original_filename = "google_sheet"

    if df is not None:
        st.session_state.df = df

        st.write("### Quick Stats")
        m1, m2, m3 = st.columns(3)
        m1.metric("Shape (Rows, Cols)", f"{df.shape[0]:,} x {df.shape[1]}")
        m2.metric("Duplicates", df.duplicated().sum())
        m3.metric("Missing Values", int(df.isnull().sum().sum()))

        st.write("") 

        st.write("### Data Inspector")
        tab_data, tab_meta, tab_num, tab_cat = st.tabs([
            "Raw Data",
            "Column Metadata",
            "Numeric Stats",
            "Categorical Stats",
        ])

        with tab_data:
            st.dataframe(df.head(100), use_container_width=True, hide_index=True)
            st.caption("Showing first 100 rows for performance.")

        with tab_meta:
            meta_df = pd.DataFrame({
                "Column Name": df.columns,
                "Data Type": df.dtypes.astype(str).values,
                "Missing Values": df.isnull().sum().values,
                "Missing (%)": (df.isnull().sum() / len(df) * 100).round(2).values,
            })
            styled_meta = meta_df.style.background_gradient(
                subset=["Missing (%)"], cmap="Reds", vmin=0, vmax=100
            )
            st.dataframe(styled_meta, use_container_width=True, hide_index=True)

        with tab_num:
            num_cols = df.select_dtypes(include=["number"]).columns
            if len(num_cols) > 0:
                st.dataframe(df[num_cols].describe().T, use_container_width=True)
            else:
                st.info("No numeric columns available.")

        with tab_cat:
            cat_cols = df.select_dtypes(include=["object", "category"]).columns
            if len(cat_cols) > 0:
                st.dataframe(df[cat_cols].describe().T, use_container_width=True)
            else:
                st.info("No categorical columns available.")

    else:
        st.info("Please upload a dataset or paste a public Google Sheets link to get started.")