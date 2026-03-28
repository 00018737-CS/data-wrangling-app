import streamlit as st
import pandas as pd

def render():
    df = st.session_state.df

    st.subheader("Duplicates Management")
    st.write("Identify and remove duplicate records from your dataset.")


    if 'tab2_success' in st.session_state:
        st.success(st.session_state.tab2_success)
        del st.session_state.tab2_success

    with st.container(border=True):
        st.write("### 1. Detection Strategy")
        
        dup_mode = st.radio(
            "How should we define a duplicate?",
            [
                "Full-row duplicates (All columns must match)", 
                "Duplicates by subset of columns (User-selected keys)"
            ]
        )

        subset_cols = None
        if dup_mode == "Duplicates by subset of columns (User-selected keys)":
            subset_cols = st.multiselect(
                "Select columns to check for duplicates:", 
                df.columns.tolist()
            )
            if not subset_cols:
                st.warning("Please select at least one column to check for duplicates.")
                return 

        all_duplicates_mask = df.duplicated(subset=subset_cols, keep=False)
        
        extra_duplicates_mask = df.duplicated(subset=subset_cols, keep='first')
        rows_to_drop_count = extra_duplicates_mask.sum()

        st.metric("Duplicate Rows Found (to drop)", rows_to_drop_count)

        if rows_to_drop_count == 0:
            st.success("No duplicates found with the current settings!")
            return

    with st.container(border=True):
        st.write("### 2. Duplicate Groups Preview")
        st.write("Below are the rows involved in duplication (all instances shown).")
        
        dup_df_preview = df[all_duplicates_mask]
        
        if subset_cols:
            dup_df_preview = dup_df_preview.sort_values(by=subset_cols)
        else:
            dup_df_preview = dup_df_preview.sort_values(by=df.columns.tolist())
            
        st.dataframe(dup_df_preview, use_container_width=True)

    with st.container(border=True):
        st.write("### 3. Resolution Actions")
        
        keep_action = st.radio(
            "Which version of the duplicate should we keep?",
            [
                "Keep First (delete subsequent copies)", 
                "Keep Last (delete earlier copies)", 
                "Drop All (delete ALL instances of the duplicate)"
            ]
        )
        
        if "Keep First" in keep_action:
            keep_val = 'first'
        elif "Keep Last" in keep_action:
            keep_val = 'last'
        else:
            keep_val = False 

        if keep_val is False:
            rows_lost = all_duplicates_mask.sum()
        else:
            rows_lost = df.duplicated(subset=subset_cols, keep=keep_val).sum()

        st.write("---")
        st.info("**Before / After Preview**")
        c1, c2 = st.columns(2)
        c1.metric("Current Rows", df.shape[0])
        c2.metric("Rows After Drop", df.shape[0] - rows_lost, delta=f"-{rows_lost}", delta_color="inverse")

        if st.button("Remove Duplicates", type="primary"):
            df_clean = df.drop_duplicates(subset=subset_cols, keep=keep_val)
            
            st.session_state.df = df_clean
            
            log_keys = subset_cols if subset_cols else "All Columns"
            st.session_state.log.append(f"Removed {rows_lost} duplicates (Subset: {log_keys}, Keep: {keep_val})")
            st.session_state.tab2_success = f"Successfully removed {rows_lost} duplicate rows!"
            st.rerun()