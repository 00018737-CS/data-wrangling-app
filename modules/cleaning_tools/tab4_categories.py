import streamlit as st
import pandas as pd
import numpy as np

def render():
    df = st.session_state.df

    st.subheader("🔠 Categorical Data Tools")
    st.write("Clean, standardize, map, and encode text/categorical columns.")

    # NOTIFICATION SYSTEM
    if 'tab4_success' in st.session_state:
        st.success(st.session_state.tab4_success)
        del st.session_state.tab4_success

    # Filter for text and categorical columns only
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if not cat_cols:
        st.warning("⚠️ No categorical or text columns found in the dataset.")
        return

    selected_col = st.selectbox("🎯 Select a column to transform:", cat_cols)
    
    # PREVIEW: Show top 10 unique values for context
    unique_count = df[selected_col].nunique()
    st.write(f"**Current Unique Values (Top 10 out of {unique_count}):**")
    st.code(df[selected_col].value_counts().head(10).to_dict())

    # 1. VALUE STANDARDIZATION
    with st.container(border=True):
        st.write("### 🧹 1. Value Standardization")
        st.write("Fix formatting issues like invisible spaces or messy casing.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Trim Whitespace** (e.g., `' Apple '` → `'Apple'`)")
            if st.button("✂️ Trim Spaces", use_container_width=True):
                df[selected_col] = df[selected_col].astype(str).str.strip()
                st.session_state.df = df
                st.session_state.log.append(f"Trimmed whitespace in '{selected_col}'")
                st.session_state.tab4_success = f"✅ Successfully trimmed whitespace in '{selected_col}'!"
                st.rerun()
        
        with c2:
            st.write("**Change Text Case**")
            case_action = st.selectbox("Format:", ["lowercase", "UPPERCASE", "Title Case"], label_visibility="collapsed")
            if st.button("🔤 Apply Case", use_container_width=True):
                if case_action == "lowercase": df[selected_col] = df[selected_col].astype(str).str.lower()
                elif case_action == "UPPERCASE": df[selected_col] = df[selected_col].astype(str).str.upper()
                else: df[selected_col] = df[selected_col].astype(str).str.title()
                
                st.session_state.df = df
                st.session_state.log.append(f"Changed '{selected_col}' casing to {case_action}")
                st.session_state.tab4_success = f"✅ Converted '{selected_col}' to {case_action}!"
                st.rerun()

    # 2. MAPPING & REPLACEMENT (UI Table Editor)
    with st.container(border=True):
        st.write("### 🗺️ 2. Mapping & Replacement")
        st.info("💡 **How to use:** Edit the `New Value` column in the table below. If you want a value to remain unchanged, leave the `New Value` identical to the `Original Value`.")
        
        # Limit to top 100 values to prevent browser lag
        unique_vals = df[selected_col].dropna().unique()
        if len(unique_vals) > 100:
            st.warning(f"Showing the top 100 most frequent values out of {len(unique_vals)} to prevent UI lag.")
            unique_vals = df[selected_col].value_counts().head(100).index
            
        # Create mapping dataframe
        map_df = pd.DataFrame({'Original Value': unique_vals, 'New Value': unique_vals})
        
        # Streamlit Data Editor (Fulfills 'UI table editor' requirement)
        edited_df = st.data_editor(map_df, hide_index=True, use_container_width=True, num_rows="fixed")
        
        unmatched_action = st.radio(
            "What should happen to values NOT shown/edited in the table?", 
            ["Remain unchanged", "Set to 'Other'"], 
            horizontal=True
        )
        
        if st.button("🔄 Apply Custom Mapping"):
            # Map changes
            mapping_dict = dict(zip(edited_df['Original Value'], edited_df['New Value']))
            actual_changes = {k: v for k, v in mapping_dict.items() if k != v}
            
            if unmatched_action == "Set to 'Other'":
                df[selected_col] = df[selected_col].map(mapping_dict).fillna("Other")
            else:
                if actual_changes:
                    df[selected_col] = df[selected_col].replace(actual_changes)
            
            st.session_state.df = df
            st.session_state.log.append(f"Applied custom mapping to '{selected_col}'. Unmatched handling: {unmatched_action}")
            st.session_state.tab4_success = f"✅ Successfully applied custom mapping to '{selected_col}'!"
            st.rerun()

    # 3. RARE CATEGORY GROUPING
    with st.container(border=True):
        st.write("### 📦 3. Rare Category Grouping")
        st.write("Group tiny, noisy categories into a single 'Other' group to clean up your analysis.")
        
        threshold = st.slider("Group categories appearing less than (%)", 1.0, 50.0, 5.0, step=0.5)
        
        # Calculate frequencies
        freq = df[selected_col].value_counts(normalize=True) * 100
        rare_cats = freq[freq < threshold].index.tolist()
        
        if rare_cats:
            st.warning(f"⚠️ **{len(rare_cats)} categories** will be renamed to **'Other'**.")
            with st.expander("👀 See categories to be grouped"):
                st.write(", ".join(rare_cats))
                
            if st.button("🗜️ Group Rare Categories"):
                df[selected_col] = df[selected_col].replace(rare_cats, 'Other')
                st.session_state.df = df
                st.session_state.log.append(f"Grouped {len(rare_cats)} rare categories in '{selected_col}' (<{threshold}%)")
                st.session_state.tab4_success = f"✅ Grouped {len(rare_cats)} categories into 'Other'!"
                st.rerun()
        else:
            st.success(f"No categories fall below the {threshold}% threshold.")

    # 4. ONE-HOT ENCODING (OHE)
    with st.container(border=True):
        st.write("### 🔢 4. One-Hot Encoding (OHE)")
        st.error("🚨 **Warning:** This will remove the original text column and create multiple binary (0/1) columns. Use this ONLY for Machine Learning preparation.")
        
        st.write(f"💡 *Action will create **{unique_count}** new columns (e.g., `{selected_col}_Value1`).*")
        
        if st.button("⚡ Apply One-Hot Encoding", type="primary"):
            df = pd.get_dummies(df, columns=[selected_col], prefix=selected_col)
            st.session_state.df = df
            st.session_state.log.append(f"Applied One-Hot Encoding to '{selected_col}' ({unique_count} new columns)")
            st.session_state.tab4_success = f"✅ Encoded '{selected_col}'! Check the results in Page A."
            st.rerun()