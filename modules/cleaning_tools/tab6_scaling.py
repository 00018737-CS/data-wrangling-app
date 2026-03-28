import streamlit as st
import pandas as pd
import numpy as np

def render():
    df = st.session_state.df

    st.subheader("Normalization / Scaling")
    st.write("Bring your numeric columns to a common scale without distorting differences in the ranges of values.")

    # NOTIFICATION SYSTEM
    if 'tab6_success' in st.session_state:
        st.success(st.session_state.tab6_success)
        del st.session_state.tab6_success

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not num_cols:
        st.warning("⚠️ No numeric columns found in the dataset.")
        return

    with st.container(border=True):
        st.write("### Scaling Settings")
        
        selected_cols = st.multiselect("Select columns to scale:", num_cols)

        if not selected_cols:
            st.info("Please select at least one numeric column to proceed.")
            return

        method = st.radio(
            "Choose Scaling Method:", 
            [
                "Min-Max Scaling (Transforms values to 0-1 range)",
                "Z-Score Standardization (Centers data: Mean=0, Std=1)"
            ]
        )

        st.write("---")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.write("**Stats BEFORE:**")
            st.dataframe(df[selected_cols].describe().T[['mean', 'std', 'min', 'max']], use_container_width=True)

        preview_df = df[selected_cols].copy()
        for col in selected_cols:
            if "Min-Max" in method:
                c_min, c_max = preview_df[col].min(), preview_df[col].max()
                if c_max != c_min: 
                    preview_df[col] = (preview_df[col] - c_min) / (c_max - c_min)
            else:
                c_mean, c_std = preview_df[col].mean(), preview_df[col].std()
                if c_std != 0: 
                    preview_df[col] = (preview_df[col] - c_mean) / c_std

        with c2:
            st.write("**Stats AFTER (Preview):**")
            st.dataframe(preview_df.describe().T[['mean', 'std', 'min', 'max']], use_container_width=True)

        if st.button("Apply Scaling", type="primary"):
            df[selected_cols] = preview_df
            
            st.session_state.df = df
            
            method_name = "Min-Max Scaling" if "Min-Max" in method else "Z-Score Standardization"
            st.session_state.log.append(f"Applied {method_name} to columns: {', '.join(selected_cols)}")
            st.session_state.tab6_success = f"Successfully applied {method_name} to {len(selected_cols)} columns!"
            st.rerun()