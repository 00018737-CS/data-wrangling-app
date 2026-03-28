import streamlit as st
import pandas as pd

def render():
    df = st.session_state.df

    st.subheader("🧹 Missing Values Handling")
    st.write("Detect and resolve null or missing data points in your dataset.")

    # NOTIFICATION SYSTEM (FEEDBACK)
    if 'tab1_success' in st.session_state:
        st.success(st.session_state.tab1_success)
        del st.session_state.tab1_success

    # Count missing values
    missing_summary = pd.DataFrame({
        'Missing Count': df.isnull().sum(),
        'Missing (%)': (df.isnull().sum() / len(df) * 100).round(2)
    })
    missing_only = missing_summary[missing_summary['Missing Count'] > 0]

    if missing_only.empty:
        st.success("🎉 Great news! Your dataset has no missing values.")
        return

    with st.container(border=True):
        st.write("**Columns with Missing Data:**")
        st.dataframe(
            missing_only.style.background_gradient(subset=['Missing (%)'], cmap='Reds', vmin=0, vmax=100),
            use_container_width=True
        )

    st.write("### 🛠️ Resolution Actions")
    action_mode = st.radio(
        "Choose operation mode:", 
        [
            "1. Fill / Replace Values", 
            "2. Drop Rows (by selected columns)", 
            "3. Drop Columns (by threshold %)"
        ],
        horizontal=True
    )

    with st.container(border=True):
        
        # 1. FILL / REPLACE MODE (Smart filtering by data type)
        if action_mode == "1. Fill / Replace Values":
            selected_col = st.selectbox("Select a column to fill:", missing_only.index.tolist())
            
            # Check if column is numeric
            is_numeric = pd.api.types.is_numeric_dtype(df[selected_col])
            
            # Set options based on data type
            if is_numeric:
                st.info("🔢 Numeric column detected.")
                fill_options = [
                    "Constant value (user input)", 
                    "Mean (numeric)", 
                    "Median (numeric)", 
                    "Mode (numeric)", 
                    "Forward fill (time series)", 
                    "Backward fill (time series)"
                ]
            else:
                st.info("🔠 Categorical/Text column detected.")
                fill_options = [
                    "Constant value (user input)", 
                    "Most frequent (categorical)", 
                    "Forward fill (time series)", 
                    "Backward fill (time series)"
                ]
            
            action = st.selectbox("Choose replacement method:", fill_options)
            
            constant_val = None
            if action == "Constant value (user input)":
                constant_val = st.text_input("Enter the constant value:")

            st.write("---")
            st.write("📊 **Before / After Preview**")
            m_count = int(missing_only.loc[selected_col, 'Missing Count'])
            c1, c2 = st.columns(2)
            c1.metric("Current Missing Values", m_count)
            c2.metric("Missing Values After", 0, delta=f"-{m_count}", delta_color="inverse")

            if st.button("✨ Apply Fill", type="primary"):
                # Filling Logic
                if action == "Constant value (user input)" and constant_val is not None: 
                    val = float(constant_val) if is_numeric else constant_val
                    df[selected_col] = df[selected_col].fillna(val)
                elif action == "Mean (numeric)": 
                    df[selected_col] = df[selected_col].fillna(df[selected_col].mean())
                elif action == "Median (numeric)": 
                    df[selected_col] = df[selected_col].fillna(df[selected_col].median())
                elif action in ["Mode (numeric)", "Most frequent (categorical)"]: 
                    df[selected_col] = df[selected_col].fillna(df[selected_col].mode()[0])
                elif action == "Forward fill (time series)": 
                    df[selected_col] = df[selected_col].ffill()
                elif action == "Backward fill (time series)": 
                    df[selected_col] = df[selected_col].bfill()
                
                # Save changes and log
                st.session_state.df = df
                st.session_state.log.append(f"Filled nulls in '{selected_col}' using: {action}")
                st.session_state.tab1_success = f"✅ Successfully filled {m_count} missing values in '{selected_col}'!"
                st.rerun()

        # 2. DROP ROWS MODE
        elif action_mode == "2. Drop Rows (by selected columns)":
            st.write("Drop any row that has a missing value in the selected column(s).")
            cols_to_check = st.multiselect(
                "Select columns to check for nulls:", 
                missing_only.index.tolist(), 
                default=missing_only.index.tolist()
            )
            
            if cols_to_check:
                rows_before = df.shape[0]
                temp_df = df.dropna(subset=cols_to_check)
                rows_after = temp_df.shape[0]
                rows_lost = rows_before - rows_after

                st.write("---")
                st.write("📊 **Before / After Preview**")
                c1, c2 = st.columns(2)
                c1.metric("Current Rows", rows_before)
                c2.metric("Rows After Drop", rows_after, delta=f"-{rows_lost}", delta_color="inverse")

                if st.button("🚨 Drop Rows", type="primary"):
                    st.session_state.df = temp_df
                    st.session_state.log.append(f"Dropped {rows_lost} rows due to nulls in: {cols_to_check}")
                    st.session_state.tab1_success = f"✅ Successfully dropped {rows_lost} rows!"
                    st.rerun()
            else:
                st.warning("Please select at least one column.")

        # 3. DROP COLUMNS MODE
        else:
            threshold = st.slider("Drop columns with missing values above (%)", 1, 100, 50)
            cols_to_drop = missing_summary[missing_summary['Missing (%)'] > threshold].index.tolist()
            
            st.write("---")
            st.write("📊 **Before / After Preview**")
            c1, c2 = st.columns(2)
            c1.metric("Current Columns", df.shape[1])
            c2.metric("Columns After Drop", df.shape[1] - len(cols_to_drop), delta=f"-{len(cols_to_drop)}", delta_color="inverse")
            
            if len(cols_to_drop) > 0:
                st.write(f"**Target columns to drop:** `{', '.join(cols_to_drop)}`")
                if st.button("🚨 Drop Columns", type="primary"):
                    st.session_state.df = df.drop(columns=cols_to_drop)
                    st.session_state.log.append(f"Dropped columns with >{threshold}% nulls: {cols_to_drop}")
                    st.session_state.tab1_success = f"✅ Successfully dropped {len(cols_to_drop)} columns!"
                    st.rerun()
            else:
                st.warning("No columns meet this threshold to drop.")