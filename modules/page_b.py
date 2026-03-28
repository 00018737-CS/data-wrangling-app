import streamlit as st
import pandas as pd
import json


import google.generativeai as genai

from modules.cleaning_tools import tab1_nulls
from modules.cleaning_tools import tab2_duplicates
from modules.cleaning_tools import tab3_dtypes
from modules.cleaning_tools import tab4_categories
from modules.cleaning_tools import tab5_outliers
from modules.cleaning_tools import tab6_scaling
from modules.cleaning_tools import tab7_col_ops
from modules.cleaning_tools import tab8_validation

# API KEY 
GEMINI_API_KEY = "AIzaSyBeEMQzQAo7poc3gcBYx2n65I-DChqM18k"

def render():
    st.header("Page B — Data Cleaning Studio")
    
    if 'df' not in st.session_state or st.session_state.df is None:
        st.warning("Please upload data on 'Page A — Upload & Overview' first!")
        return
        
    df = st.session_state.df
    st.write(f"**Current dataset size:** `{df.shape[0]} rows`, `{df.shape[1]} columns`")
    
    # AI ASSISTANT 
    st.write("---")
    ai_enabled = st.toggle("Enable AI Assistant (Natural Language Cleaning)")
    
    if ai_enabled:
        with st.container(border=True):
            st.caption("**Disclaimer:** AI outputs may be imperfect. Always review the suggested operations before approving.")
            
            user_prompt = st.text_input("What do you want to clean?", placeholder="Write a command or choose from the examples below...")
            
            
            st.write("**Quick Actions:**")
            q_cols = st.columns(5)
            
            quick_prompt = None
            if q_cols[0].button("Drop Duplicates", use_container_width=True):
                quick_prompt = "Drop all duplicate rows"
            if q_cols[1].button("Drop Null Rows", use_container_width=True):
                quick_prompt = "Drop rows that have missing values"
            if q_cols[2].button("Fill Nulls (Med)", use_container_width=True):
                quick_prompt = "Fill missing values using median"
            if q_cols[3].button("Trim Spaces", use_container_width=True):
                quick_prompt = "Trim spaces in all text columns"
            if q_cols[4].button("Parse Dates", use_container_width=True):
                quick_prompt = "Try to parse datetime columns"

            final_prompt = quick_prompt if quick_prompt else user_prompt
            
            if st.button("Ask AI", type="primary") or quick_prompt:
                if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
                    st.error("Please insert your Gemini API Key in the code first!")
                elif final_prompt:
                    with st.spinner("AI is analyzing your request..."):
                        try:
                            genai.configure(api_key=GEMINI_API_KEY)
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            
                            cols_info = df.dtypes.astype(str).to_dict()
                            
                            system_prompt = f"""
                            You are a data cleaning assistant. The dataset has these columns and types: {cols_info}.
                            The user wants to: "{final_prompt}".
                            Return ONLY a valid JSON array of objects representing the actions. 
                            Supported actions (MUST match exactly): 
                            1. {{"action": "drop_duplicates"}}
                            2. {{"action": "drop_null_rows", "columns": ["Col1", "Col2"]}} (if empty list, applies to all)
                            3. {{"action": "fill_nulls", "column": "ColName", "method": "median" or "mean" or "mode"}}
                            4. {{"action": "fill_constant", "column": "ColName", "value": "Unknown" or 0}}
                            5. {{"action": "drop_columns", "columns": ["Col1", "Col2"]}}
                            6. {{"action": "drop_empty_columns", "threshold_pct": 80}} (drops columns with > X% nulls)
                            7. {{"action": "rename_column", "old_name": "Old", "new_name": "New"}}
                            8. {{"action": "change_type", "column": "ColName", "type": "int" or "float" or "str"}}
                            9. {{"action": "parse_datetime", "column": "ColName"}}
                            10. {{"action": "trim_spaces", "column": "ColName"}}
                            11. {{"action": "change_case", "column": "ColName", "case": "lower" or "upper" or "title"}}
                            Do not write markdown, explanations, or python code. Just the JSON array.
                            """
                            
                            response = model.generate_content(system_prompt)
                            cleaned_json = response.text.replace('```json', '').replace('```', '').strip()
                            st.session_state.ai_suggestions = json.loads(cleaned_json)
                        except Exception as e:
                            st.error(f"AI Error: Could not process request. Make sure your prompt makes sense for this dataset. ({e})")

            
            if 'ai_suggestions' in st.session_state:
                st.write("### Here is what I plan to do:")
                
                for action in st.session_state.ai_suggestions:
                    act = action.get("action")
                    
                    if act == "drop_duplicates":
                        st.info("**Drop Duplicates:** Completely identical rows will be removed.")
                    elif act == "drop_null_rows":
                        cols = action.get('columns', [])
                        c_text = f"columns `{', '.join(cols)}`" if cols else "any column"
                        st.info(f"**Drop Null Rows:** Rows with missing values in {c_text} will be dropped.")
                    elif act == "fill_nulls":
                        st.info(f"**Fill Nulls (Math):** Missing values in column `{action.get('column')}` will be replaced with `{action.get('method')}`.")
                    elif act == "fill_constant":
                        st.info(f"**Fill Constant:** Missing values in column `{action.get('column')}` will be replaced with `{action.get('value')}`.")
                    elif act == "drop_columns":
                        st.info(f"**Drop Columns:** Columns `{', '.join(action.get('columns', []))}` will be permanently removed.")
                    elif act == "drop_empty_columns":
                        st.info(f"**Drop Empty Columns:** Columns with more than `{action.get('threshold_pct')}%` missing values will be dropped.")
                    elif act == "rename_column":
                        st.info(f"**Rename:** Column `{action.get('old_name')}` will be renamed to `{action.get('new_name')}`.")
                    elif act == "change_type":
                        st.info(f"**Change Type:** Column `{action.get('column')}` will be converted to `{action.get('type')}` format.")
                    elif act == "parse_datetime":
                        st.info(f"**Parse Datetime:** Column `{action.get('column')}` will be parsed as datetime (errors coerced to NaT).")
                    elif act == "trim_spaces":
                        st.info(f"**Trim Spaces:** Leading and trailing spaces will be removed in column `{action.get('column')}`.")
                    elif act == "change_case":
                        st.info(f"**Change Case:** Text in column `{action.get('column')}` will be converted to `{action.get('case')}` case.")
                    
                    with st.expander("View Technical JSON", expanded=False):
                        st.code(json.dumps(action, indent=2), language="json")

                st.write("**Are you sure you want to apply these changes to your data?**")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Yes, Approve & Apply", use_container_width=True):
                        
                        for action in st.session_state.ai_suggestions:
                            act = action.get("action")
                            col = action.get("column")
                            
                            try:
                                if act == "drop_duplicates":
                                    df = df.drop_duplicates()
                                    st.session_state.log.append("AI: Dropped duplicate rows")
                                    
                                elif act == "drop_null_rows":
                                    cols = action.get('columns', [])
                                    valid_cols = [c for c in cols if c in df.columns] if cols else df.columns
                                    df = df.dropna(subset=valid_cols)
                                    st.session_state.log.append(f"AI: Dropped rows with nulls in {valid_cols if cols else 'all columns'}")
                                    
                                elif act == "fill_nulls" and col in df.columns:
                                    method = action.get("method")
                                    if method == "median": df[col] = df[col].fillna(df[col].median())
                                    elif method == "mean": df[col] = df[col].fillna(df[col].mean())
                                    elif method == "mode": df[col] = df[col].fillna(df[col].mode()[0])
                                    st.session_state.log.append(f"AI: Filled nulls in '{col}' using {method}")
                                    
                                elif act == "fill_constant" and col in df.columns:
                                    val = action.get("value")
                                    df[col] = df[col].fillna(val)
                                    st.session_state.log.append(f"AI: Filled nulls in '{col}' with '{val}'")
                                    
                                elif act == "drop_columns":
                                    cols = action.get("columns", [])
                                    existing = [c for c in cols if c in df.columns]
                                    df = df.drop(columns=existing)
                                    st.session_state.log.append(f"AI: Dropped columns {existing}")
                                    
                                elif act == "drop_empty_columns":
                                    thresh = action.get("threshold_pct", 80) / 100
                                    missing_pct = df.isnull().mean()
                                    cols_to_drop = missing_pct[missing_pct > thresh].index
                                    df = df.drop(columns=cols_to_drop)
                                    st.session_state.log.append(f"AI: Dropped empty columns {list(cols_to_drop)}")
                                    
                                elif act == "rename_column":
                                    old_c, new_c = action.get("old_name"), action.get("new_name")
                                    if old_c in df.columns:
                                        df = df.rename(columns={old_c: new_c})
                                        st.session_state.log.append(f"AI: Renamed '{old_c}' to '{new_c}'")
                                        
                                elif act == "change_type" and col in df.columns:
                                    t = action.get("type")
                                    if t in ["int", "float"]:
                                        df[col] = pd.to_numeric(df[col], errors='coerce')
                                    elif t == "str":
                                        df[col] = df[col].astype(str)
                                    st.session_state.log.append(f"AI: Changed type of '{col}' to {t}")
                                    
                                elif act == "parse_datetime" and col in df.columns:
                                    df[col] = pd.to_datetime(df[col], errors='coerce')
                                    st.session_state.log.append(f"AI: Parsed '{col}' as datetime")
                                    
                                elif act == "trim_spaces" and col in df.columns:
                                    df[col] = df[col].astype(str).str.strip()
                                    st.session_state.log.append(f"AI: Trimmed spaces in '{col}'")
                                    
                                elif act == "change_case" and col in df.columns:
                                    c = action.get("case")
                                    if c == "lower": df[col] = df[col].astype(str).str.lower()
                                    elif c == "upper": df[col] = df[col].astype(str).str.upper()
                                    elif c == "title": df[col] = df[col].astype(str).str.title()
                                    st.session_state.log.append(f"AI: Changed case of '{col}' to {c}")
                            except Exception as apply_e:
                                
                                st.warning(f"Skipped action '{act}' due to warning/error: {apply_e}")
                        
                        st.session_state.df = df
                        del st.session_state.ai_suggestions
                        st.success("Actions applied successfully!")
                        st.rerun()
                
                with c2:
                    if st.button("No, Reject & Cancel", use_container_width=True):
                        del st.session_state.ai_suggestions
                        st.rerun()

    st.write("---")


    tabs = st.tabs([
        "Missing Values", "Duplicates", "Data Types", 
        "Categories", "Outliers", "Scaling", 
        "Column Ops", "Validation"
    ])

    with tabs[0]: tab1_nulls.render()
    with tabs[1]: tab2_duplicates.render()
    with tabs[2]: tab3_dtypes.render()
    with tabs[3]: tab4_categories.render()
    with tabs[4]: tab5_outliers.render()
    with tabs[5]: tab6_scaling.render()
    with tabs[6]: tab7_col_ops.render()
    with tabs[7]: tab8_validation.render()


    st.markdown("---")
    with st.expander("View Transformation Log", expanded=False):
        if 'log' in st.session_state and st.session_state.log:
            for i, entry in enumerate(st.session_state.log):
                st.write(f"`{i+1}.` {entry}")
        else:
            st.write("No transformations applied yet.")