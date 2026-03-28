import streamlit as st
import pandas as pd
import numpy as np

def render():
    df = st.session_state.df

    st.subheader("🛡️ Data Validation Rules")
    st.write("Define rules to catch invalid data. Violations will be shown below and can be exported.")

    with st.container(border=True):
        st.write("### 📐 1. Define Rule")
        
        rule_type = st.selectbox(
            "Select Validation Rule:", 
            [
                "Numeric Range Check (Min/Max)",
                "Allowed Categories List",
                "Non-Null Constraint (Must not be empty)"
            ]
        )

        # Variables to store results
        violations_df = None
        rule_desc = ""

        st.write("---")

        # RULE 1: NUMERIC RANGE CHECK
        if rule_type == "Numeric Range Check (Min/Max)":
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if not num_cols:
                st.warning("No numeric columns available in the current dataset.")
            else:
                col = st.selectbox("Select Numeric Column to check:", num_cols)
                
                c1, c2 = st.columns(2)
                # Use current min/max as default values for the inputs
                min_val = c1.number_input("Minimum Allowed Value:", value=float(df[col].min()))
                max_val = c2.number_input("Maximum Allowed Value:", value=float(df[col].max()))

                if st.button("🔍 Run Validation Check", type="primary", key="val_num"):
                    # Find rows where value < min OR value > max
                    violations_df = df[(df[col] < min_val) | (df[col] > max_val)]
                    rule_desc = f"Range check on '{col}' (Allowed: {min_val} to {max_val})"

        # RULE 2: ALLOWED CATEGORIES LIST
        elif rule_type == "Allowed Categories List":
            cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            if not cat_cols:
                st.warning("No categorical columns available in the current dataset.")
            else:
                col = st.selectbox("Select Categorical Column to check:", cat_cols)
                unique_vals = df[col].dropna().unique().tolist()
                
                st.write("Select values that are **ALLOWED** (others will be flagged as violations):")
                allowed_vals = st.multiselect("Allowed Values:", unique_vals, default=unique_vals)

                if st.button("🔍 Run Validation Check", type="primary", key="val_cat"):
                    # Find rows where value is NOT in allowed list AND is NOT null
                    violations_df = df[~df[col].isin(allowed_vals) & df[col].notna()]
                    rule_desc = f"Allowed categories validation on '{col}'"
                    
        # RULE 3: NON-NULL CONSTRAINT
        elif rule_type == "Non-Null Constraint (Must not be empty)":
            st.write("Select columns that are mandatory (must not contain missing values).")
            cols = st.multiselect("Select Mandatory Columns:", df.columns.tolist())
            
            if cols:
                if st.button("🔍 Run Validation Check", type="primary", key="val_null"):
                    # Find rows where AT LEAST ONE selected column has a null value
                    violations_df = df[df[cols].isnull().any(axis=1)]
                    rule_desc = f"Non-null constraint check on: {', '.join(cols)}"
            else:
                st.info("👆 Please select at least one column to validate.")

    # RESULTS & EXPORT (Violations Table)
    if violations_df is not None:
        st.write("---")
        st.write("### 🚨 Validation Results")
        
        if violations_df.empty:
            st.success(f"✅ **Pass!** No violations found for rule: `{rule_desc}`")
        else:
            v_count = len(violations_df)
            st.error(f"❌ **Failed!** Found **{v_count}** violation(s) for rule: `{rule_desc}`")
            
            # Show the violations table
            with st.container(border=True):
                st.write("**Violations Table:**")
                st.dataframe(violations_df, use_container_width=True)
                
                # Export Button for the specific violation report
                csv = violations_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Violations to CSV",
                    data=csv,
                    file_name="data_violations_report.csv",
                    mime="text/csv",
                    type="primary"
                )