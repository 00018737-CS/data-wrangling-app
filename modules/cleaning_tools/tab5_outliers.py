import streamlit as st
import pandas as pd
import numpy as np

def render():
    df = st.session_state.df

    st.subheader("📈 Numeric Cleaning (Outliers)")
    st.write("Detect and handle extreme values that can skew your charts and models.")

    # NOTIFICATION SYSTEM
    if 'tab5_success' in st.session_state:
        st.success(st.session_state.tab5_success)
        del st.session_state.tab5_success

    # Filter for numeric columns only
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not num_cols:
        st.warning("⚠️ No numeric columns found in the dataset.")
        return

    # 1. DETECTION SETTINGS
    with st.container(border=True):
        st.write("### 🔍 1. Detection Settings")
        
        col_to_check = st.selectbox("Select numeric column to analyze:", num_cols)
        series = df[col_to_check].dropna() # Analyze non-null values only
        
        method = st.radio(
            "Detection Method:", 
            ["IQR (Interquartile Range - standard)", "Z-Score (Standard deviation)"], 
            horizontal=True
        )

        outliers_mask = pd.Series(False, index=df.index)

        # OUTLIER DETECTION LOGIC
        if "IQR" in method:
            st.caption("IQR finds values that fall unusually far from the middle 50% of your data.")
            multiplier = st.slider("IQR Multiplier (Higher = less strict):", 1.0, 3.0, 1.5, 0.1)
            
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - (multiplier * IQR)
            upper_bound = Q3 + (multiplier * IQR)
            
        else: # Z-Score
            st.caption("Z-Score finds values that are too many standard deviations away from the mean.")
            z_thresh = st.slider("Z-Score Threshold (Higher = less strict):", 2.0, 5.0, 3.0, 0.5)
            
            mean_val = series.mean()
            std_val = series.std()
            if std_val > 0:
                lower_bound = mean_val - (z_thresh * std_val)
                upper_bound = mean_val + (z_thresh * std_val)
            else:
                lower_bound, upper_bound = mean_val, mean_val

        # Apply mask to the full dataframe
        outliers_mask = (df[col_to_check] < lower_bound) | (df[col_to_check] > upper_bound)
        outlier_count = outliers_mask.sum()

        st.write("---")
        st.write("**Detection Summary**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Lower Bound", round(lower_bound, 2))
        c2.metric("Upper Bound", round(upper_bound, 2))
        c3.metric("🚨 Outliers Found", outlier_count)

        # VISUAL PROOF: Show rows identified as outliers
        if outlier_count > 0:
            with st.expander("👀 View Outlier Rows (What are we changing?)"):
                st.dataframe(df[outliers_mask].sort_values(by=col_to_check, ascending=False).head(50), use_container_width=True)

    if outlier_count == 0:
        st.success("✅ No outliers detected with the current settings. You can move to the next step!")
        return

    # 2. RESOLUTION ACTION
    with st.container(border=True):
        st.write("### 🛠️ 2. Resolution Action")
        action = st.radio(
            "How to handle these outliers?",
            [
                "Cap/Winsorize at boundaries (Recommended)",
                "Remove outlier rows entirely",
                "Do nothing"
            ]
        )

        st.write("---")
        st.info("📊 **Impact Preview**")
        p1, p2 = st.columns(2)

        if "Remove" in action:
            p1.metric("Current Rows", df.shape[0])
            p2.metric("Rows After Drop", df.shape[0] - outlier_count, delta=f"-{outlier_count}", delta_color="inverse")
            st.write("💡 *Warning: This will delete the entire row for any detected outlier, leading to data loss in other columns.*")
        
        elif "Cap" in action:
            p1.metric("Values to Cap", outlier_count)
            p2.metric("Remaining Outliers", 0, delta=f"-{outlier_count}", delta_color="inverse")
            st.write(f"💡 *Extreme values will be replaced by the boundaries: min **`{round(lower_bound, 2)}`** or max **`{round(upper_bound, 2)}`**.*")

        if action != "Do nothing":
            if st.button("✨ Apply Action", type="primary"):
                if "Remove" in action:
                    st.session_state.df = df[~outliers_mask].copy()
                    action_msg = f"Removed {outlier_count} outlier rows"
                
                elif "Cap" in action:
                    df_clean = df.copy()
                    df_clean[col_to_check] = df_clean[col_to_check].clip(lower=lower_bound, upper=upper_bound)
                    st.session_state.df = df_clean
                    action_msg = f"Capped (Winsorized) {outlier_count} outliers"

                # Log and Refresh
                method_name = "IQR" if "IQR" in method else "Z-Score"
                st.session_state.log.append(f"{action_msg} in '{col_to_check}' using {method_name}")
                st.session_state.tab5_success = f"✅ Successfully {action_msg.lower()}!"
                st.rerun()