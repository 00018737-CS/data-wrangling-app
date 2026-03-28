import streamlit as st
import pandas as pd
import numpy as np

def render():
    df = st.session_state.df

    st.subheader("🔄 Data Types & Parsing")
    st.write("Convert column types and clean dirty numeric strings (e.g., currency symbols).")

    # NOTIFICATION SYSTEM
    if 'tab3_success' in st.session_state:
        st.success(st.session_state.tab3_success)
        del st.session_state.tab3_success
    if 'tab3_error' in st.session_state:
        st.error(st.session_state.tab3_error)
        del st.session_state.tab3_error

    # 1. CURRENT DATA TYPES OVERVIEW
    with st.container(border=True):
        st.write("### 📋 Current Column Types")
        
        # Display a clean table showing dtypes and a sample value
        dtypes_df = pd.DataFrame({
            'Data Type': df.dtypes.astype(str),
            'Sample Value (Row 1)': df.iloc[0].astype(str) if not df.empty else "N/A"
        })
        st.dataframe(dtypes_df.T, use_container_width=True)

    # 2. CONVERSION TOOLS
    with st.container(border=True):
        st.write("### 🛠️ Conversion Tools")
        
        c1, c2 = st.columns([1, 1])
        
        with c1:
            col_to_fix = st.selectbox("1. Select column to convert:", df.columns.tolist())
            current_type = df[col_to_fix].dtype
            st.info(f"Current type: `{current_type}`")
            
            # Column preview
            st.write("**Data Preview (Top 3):**")
            st.code(df[col_to_fix].dropna().head(3).tolist())

        with c2:
            target_type = st.selectbox(
                "2. Convert to:", 
                ["Numeric (Float)", "Integer", "Datetime", "Category", "String"]
            )
            
            # Dynamic settings based on selection
            clean_dirty = False
            dt_format = "Auto-parse (Coerce errors)"
            
            if target_type in ["Numeric (Float)", "Integer"]:
                st.write("---")
                clean_dirty = st.checkbox("🧹 Clean 'dirty' strings?", help="Removes currency symbols ($), commas, and spaces before converting.")
            
            elif target_type == "Datetime":
                st.write("---")
                dt_format = st.radio(
                    "Datetime format:", 
                    ["Auto-parse (Coerce errors)", "Specify format (e.g., %Y-%m-%d)"]
                )
                if dt_format != "Auto-parse (Coerce errors)":
                    custom_format = st.text_input("Enter format string:", value="%Y-%m-%d")

            st.write("---")
            if st.button("🚀 Convert Type", type="primary", use_container_width=True):
                series = df[col_to_fix].copy()
                
                try:
                    # Step 1: Clean dirty strings (if enabled)
                    if clean_dirty and target_type in ["Numeric (Float)", "Integer"]:
                        # Regex keeps only digits, dots, and minus signs
                        series = series.astype(str).str.replace(r'[^\d.-]', '', regex=True)

                    # Step 2: Conversion
                    if target_type == "Numeric (Float)":
                        df[col_to_fix] = pd.to_numeric(series, errors='coerce')
                    
                    elif target_type == "Integer":
                        # Convert to numeric first to handle string-based numbers, then to nullable Int64
                        df[col_to_fix] = pd.to_numeric(series, errors='coerce').astype('Int64')
                    
                    elif target_type == "Datetime":
                        if dt_format == "Auto-parse (Coerce errors)":
                            df[col_to_fix] = pd.to_datetime(series, errors='coerce')
                        else:
                            df[col_to_fix] = pd.to_datetime(series, format=custom_format, errors='coerce')
                            
                    elif target_type == "Category":
                        df[col_to_fix] = series.astype('category')
                        
                    elif target_type == "String":
                        df[col_to_fix] = series.astype(str)

                    # Update session state and log
                    st.session_state.df = df
                    action_log = f"Converted '{col_to_fix}' to {target_type}"
                    if clean_dirty: action_log += " (with dirty numeric cleaning)"
                    st.session_state.log.append(action_log)
                    
                    st.session_state.tab3_success = f"✅ Successfully converted '{col_to_fix}' to {target_type}!"
                    st.rerun()
                    
                except Exception as e:
                    st.session_state.tab3_error = f"❌ Error converting data: {e}"
                    st.rerun()