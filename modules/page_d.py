import streamlit as st
import pandas as pd
import json
from datetime import datetime

def render():
    st.title("Page D — Export & Report")
    
    # Check if data exists
    if 'df' not in st.session_state or st.session_state.df is None:
        st.warning("⚠️ No data available to export. Please upload and clean data first!")
        return

    df = st.session_state.df
    log = st.session_state.log

    st.write("Congratulations! You've successfully wrangled your data. Review your final dataset and download the results below.")

    # 1. Final Dataset Preview
    with st.container(border=True):
        st.write("### Final Dataset Preview")
        c1, c2 = st.columns(2)
        c1.metric("Final Rows", df.shape[0])
        c2.metric("Final Columns", df.shape[1])
        
        st.dataframe(df.head(10), use_container_width=True)

    # 2. TRANSFORMATION LOG
    with st.container(border=True):
        st.write("### 📜 Transformation Log")
        st.write("Here is the history of all operations applied to this dataset during the current session:")
        
        if not log:
            st.info("No transformations applied yet. The dataset is in its original state.")
        else:
            for i, step in enumerate(log):
                st.write(f"`{i+1}.` {step}")
            if st.button("⚠️ Undo Last Step (Removes from log)", help="Note: To fully revert data, use Reset Session in the sidebar."):
                st.session_state.log.pop()
                st.rerun()
                
    # 3. Download Center
    st.markdown("### 💾 Download Center")
    
    d_col1, d_col2 = st.columns(2)

    # --- Button 1: Export Data To CSV ---
    with d_col1:
        st.write("**1. Download Cleaned Data**")
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Download Dataset (CSV)",
            data=csv_data,
            file_name="cleaned_dataset.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )

    # --- Button 2: Export Report To JSON Recipe ---
    with d_col2:
        st.write("**2. Download Transformation Recipe**")
        
        # Build The JSON Structure As Required
        report_dict = {
            "metadata": {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "final_rows": df.shape[0],
                "final_cols": df.shape[1]
            },
            "transformation_steps": log
        }
        
        # Convert The Dictionary To A Pretty JSON String
        json_recipe = json.dumps(report_dict, indent=4)
        
        st.download_button(
            label="⚙️ Download Recipe (JSON)",
            data=json_recipe,
            file_name="transformation_recipe.json",
            mime="application/json",
            type="primary",
            use_container_width=True
        )

    # Add A Preview Of How The JSON Recipe Looks
    with st.expander("👀 Peek at the JSON Recipe"):
        st.code(json_recipe, language="json")