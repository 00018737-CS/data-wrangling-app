import streamlit as st
import pandas as pd
import numpy as np

def render():
    df = st.session_state.df

    st.subheader("Column Operations")
    st.write("Rename, drop, or engineer new features using formulas and binning.")

    # NOTIFICATION SYSTEM & SMART PREVIEW
    if 'tab7_success' in st.session_state:
        st.success(st.session_state.tab7_success)
        del st.session_state.tab7_success
        
    if 'tab7_error' in st.session_state:
        st.error(f"Error: {st.session_state.tab7_error}")
        del st.session_state.tab7_error

    if 'tab7_preview_col' in st.session_state:
        new_col = st.session_state.tab7_preview_col
        base_col = st.session_state.get('tab7_base_col')
        
        if new_col in df.columns:
            with st.container(border=True):
                st.write(f"**Result Preview for `{new_col}`:**")
                p1, p2 = st.columns(2)
                
                with p1:
                    st.write("**Sample Data (5 random rows):**")
                    if base_col and base_col in df.columns:
                        st.dataframe(df[[base_col, new_col]].dropna().sample(min(5, len(df))), use_container_width=True)
                    else:
                        st.dataframe(df[[new_col]].dropna().sample(min(5, len(df))), use_container_width=True)
                        
                with p2:
                    st.write("**Value Distribution:**")
                    st.dataframe(df[new_col].value_counts().head(10), use_container_width=True)
                    
        del st.session_state.tab7_preview_col
        if 'tab7_base_col' in st.session_state:
            del st.session_state.tab7_base_col

    with st.container(border=True):
        st.write("### 1. Rename & Drop Columns")
        c1, c2 = st.columns(2)
        
        with c1:
            st.write("**Rename Column**")
            col_to_rename = st.selectbox("Select column to rename:", df.columns.tolist(), key="rename_select")
            new_col_name = st.text_input("Enter new name:", placeholder="e.g., Client_Age")
            
            if st.button("Rename", use_container_width=True):
                if new_col_name.strip():
                    df = df.rename(columns={col_to_rename: new_col_name.strip()})
                    st.session_state.df = df
                    st.session_state.log.append(f"Renamed column '{col_to_rename}' to '{new_col_name.strip()}'")
                    st.session_state.tab7_success = f"Successfully renamed to '{new_col_name.strip()}'!"
                    st.rerun()
                else:
                    st.warning("Please enter a valid new name.")

        with c2:
            st.write("**Drop Columns**")
            cols_to_drop = st.multiselect("Select columns to remove:", df.columns.tolist(), key="drop_select")
            
            if st.button("Drop Selected", use_container_width=True):
                if cols_to_drop:
                    df = df.drop(columns=cols_to_drop)
                    st.session_state.df = df
                    st.session_state.log.append(f"Dropped columns: {', '.join(cols_to_drop)}")
                    st.session_state.tab7_success = f"Successfully dropped {len(cols_to_drop)} columns!"
                    st.rerun()
                else:
                    st.warning("Please select at least one column to drop.")

    # 2. CREATE NEW COLUMN (Feature Engineering)
    with st.container(border=True):
        st.write("### 2. Create New Column")
        create_mode = st.radio("Method:", ["Mathematical Formula", "Binning (Group numbers into categories)"], horizontal=True)
        st.write("---")

        if create_mode == "Mathematical Formula":
            st.info("**Hint:** Use exact column names. Example: `Salary / Age` or `Age - Age.mean()`")
            with st.expander("View available columns"):
                st.code(", ".join(df.columns.tolist()))

            f_col1, f_col2 = st.columns([1, 2])
            with f_col1:
                new_math_col = st.text_input("New Column Name:", placeholder="e.g., Profit_Margin")
            with f_col2:
                formula = st.text_input("Formula Expression:", placeholder="Revenue - Cost")

            if st.button("Calculate & Create", type="primary"):
                if new_math_col and formula:
                    try:
                        df[new_math_col] = df.eval(formula)
                        st.session_state.df = df
                        st.session_state.log.append(f"Created '{new_math_col}' using formula: {formula}")
                        st.session_state.tab7_success = f"Column '{new_math_col}' created successfully!"
                        
                        
                        st.session_state.tab7_preview_col = new_math_col
                        st.rerun()
                    except Exception as e:
                        st.session_state.tab7_error = str(e)
                        st.rerun()
                else:
                    st.warning("Please provide both a name and a formula.")

        else:
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if not num_cols:
                st.warning("No numeric columns available for binning.")
            else:
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    bin_col = st.selectbox("Numeric column to bin:", num_cols)
                    bin_name = st.text_input("New Binned Column Name:", value=f"{bin_col}_Group")
                with b_col2:
                    num_bins = st.number_input("Number of bins:", min_value=2, max_value=20, value=3)
                    bin_type = st.radio("Binning Strategy:", ["Equal-width (Standard bins)", "Quantile bins (Equal number of rows)"])

                if st.button("Create Bins", type="primary"):
                    try:
                        if "Equal-width" in bin_type:
                            df[bin_name] = pd.cut(df[bin_col], bins=num_bins)
                        else:
                            df[bin_name] = pd.qcut(df[bin_col], q=num_bins, duplicates='drop')
                            
                        st.session_state.df = df
                        st.session_state.log.append(f"Binned '{bin_col}' into {num_bins} {bin_type} categories as '{bin_name}'")
                        st.session_state.tab7_success = f"Successfully created binned column '{bin_name}'!"
                        
                        # Save for preview
                        st.session_state.tab7_preview_col = bin_name
                        st.session_state.tab7_base_col = bin_col
                        st.rerun()
                    except Exception as e:
                        st.session_state.tab7_error = f"Failed to create bins: {e}"
                        st.rerun()