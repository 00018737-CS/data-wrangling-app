import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def render():
    st.title("📊 Page C — Visualization Builder")
    
    # Check if data is loaded in session state
    if 'df' not in st.session_state or st.session_state.df is None:
        st.warning("⚠️ Please upload data on 'Page A — Upload & Overview' first!")
        return
        
    df = st.session_state.df.copy()

    # 1. FILTERING SECTION
    st.markdown("### 🔍 Global Data Filters")
    with st.container(border=True):
        st.info("💡 **Hint:** Use these filters to slice your data **before** generating the chart.")
        f_col1, f_col2 = st.columns(2)
        
        # Numeric Filter
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            with f_col1:
                filter_num_col = st.selectbox("🔢 Numeric Filter Column:", ["None"] + num_cols)
                if filter_num_col != "None":
                    min_val, max_val = float(df[filter_num_col].min()), float(df[filter_num_col].max())
                    if min_val != max_val:
                        selected_range = st.slider(f"Range for {filter_num_col}:", min_val, max_val, (min_val, max_val))
                        df = df[(df[filter_num_col] >= selected_range[0]) & (df[filter_num_col] <= selected_range[1])]

        # Categorical Filter
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if cat_cols:
            with f_col2:
                filter_cat_col = st.selectbox("🔠 Categorical Filter Column:", ["None"] + cat_cols)
                if filter_cat_col != "None":
                    unique_cats = df[filter_cat_col].dropna().unique().tolist()
                    selected_cats = st.multiselect(f"Include categories for {filter_cat_col}:", unique_cats, default=unique_cats)
                    if selected_cats:
                        df = df[df[filter_cat_col].isin(selected_cats)]

    st.write("---") 

    # 2. BUILDER INTERFACE
    col_settings, col_plot = st.columns([1, 2.5])

    with col_settings:
        with st.container(border=True):
            st.write("### ⚙️ Chart Settings")
            
            # Chart Selection (All 6 required types)
            chart_type = st.selectbox(
                "1. Select Chart Type:",
                [
                    "Scatter Plot", 
                    "Histogram", 
                    "Box Plot", 
                    "Line Chart (Time Series)", 
                    "Bar Chart (Grouped/Aggregated)", 
                    "Heatmap (Correlation Matrix)"
                ]
            )

            st.write("---")

            # Axis Variables
            x_col = None
            y_col = None
            color_col = None

            # Heatmap uses all numeric columns automatically
            if chart_type == "Heatmap (Correlation Matrix)":
                st.info("Heatmap automatically uses all numeric columns to show correlations.")
            else:
                x_col = st.selectbox("2. X-Axis:", df.columns.tolist(), index=0)
                
                # Histogram doesn't need a Y axis
                if chart_type != "Histogram":
                    # Set default Y index to 1 if available
                    default_y_index = 1 if len(df.columns) > 1 else 0
                    y_col = st.selectbox("3. Y-Axis:", df.columns.tolist(), index=default_y_index)
                
                # Optional Grouping/Color
                color_col = st.selectbox("4. Color/Group (Optional):", ["None"] + df.columns.tolist())
                if color_col == "None": color_col = None

            # AGGREGATION SETTINGS (For Bar Chart)
            agg_func = None
            top_n = None
            
            if chart_type == "Bar Chart (Grouped/Aggregated)":
                st.write("---")
                st.write("**Bar Chart Options:**")
                agg_func = st.selectbox("Aggregation Method:", ["Mean", "Sum", "Median", "Count"])
                
                # Requirement: showing "top N" categories
                top_n = st.slider("Show Top N categories (on X-axis):", 5, 50, 10)

    # 3. PLOT RENDERING
    with col_plot:
        with st.container(border=True):
            st.write(f"### 📈 {chart_type}")
            
            if df.empty:
                st.error("⚠️ The dataset is empty after filtering! Please adjust your filters.")
                return

            # Set Seaborn theme
            sns.set_theme(style="whitegrid", palette="muted")
            
            # LOADING ANIMATION
            with st.spinner("⏳ Generating chart... This may take a moment."):
                fig, ax = plt.subplots(figsize=(10, 6))

                try:
                    # 1. SCATTER PLOT 
                    if chart_type == "Scatter Plot":
                        sns.scatterplot(data=df, x=x_col, y=y_col, hue=color_col, ax=ax, alpha=0.7)
                    
                    # 2. HISTOGRAM 
                    elif chart_type == "Histogram":
                        sns.histplot(data=df, x=x_col, hue=color_col, multiple="stack", kde=True, ax=ax)
                    
                    # 3. BOX PLOT
                    elif chart_type == "Box Plot":
                        sns.boxplot(data=df, x=x_col, y=y_col, hue=color_col, ax=ax)
                        plt.xticks(rotation=45, ha='right')
                    
                    # 4. LINE CHART
                    elif chart_type == "Line Chart (Time Series)":
                        temp_df = df.sort_values(by=x_col)
                        sns.lineplot(data=temp_df, x=x_col, y=y_col, hue=color_col, ax=ax)
                        plt.xticks(rotation=45, ha='right')
                    
                    # 5. BAR CHART (With Aggregation and Top N)
                    elif chart_type == "Bar Chart (Grouped/Aggregated)":
                        agg_dict = {"Mean": 'mean', "Sum": 'sum', "Median": 'median', "Count": 'size'}
                        pd_agg = agg_dict[agg_func]

                        # Aggregate data
                        if color_col:
                            bar_data = df.groupby([x_col, color_col])[y_col].agg(pd_agg).reset_index()
                        else:
                            bar_data = df.groupby(x_col)[y_col].agg(pd_agg).reset_index()

                        # Handle column naming for Count
                        val_col = y_col if agg_func != "Count" else 0
                        if agg_func == "Count": 
                            bar_data.rename(columns={0: 'Count'}, inplace=True)
                            val_col = 'Count'

                        # Filter for Top N categories
                        top_categories = bar_data.groupby(x_col)[val_col].sum().nlargest(top_n).index
                        bar_data = bar_data[bar_data[x_col].isin(top_categories)]

                        # Draw Plot
                        sns.barplot(data=bar_data, x=x_col, y=val_col, hue=color_col, ax=ax)
                        plt.xticks(rotation=45, ha='right')
                        ax.set_ylabel(f"{agg_func} of {y_col}")

                    # 6. HEATMAP (Correlation Matrix)
                    elif chart_type == "Heatmap (Correlation Matrix)":
                        corr_df = df.select_dtypes(include=[np.number])
                        if len(corr_df.columns) < 2:
                            st.error("⚠️ Need at least 2 numeric columns for a correlation heatmap.")
                        else:
                            corr_matrix = corr_df.corr()
                            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, ax=ax)

                    # Final layout adjustments
                    plt.tight_layout()
                    
                    # Display the matplotlib figure in Streamlit
                    st.pyplot(fig)

                except Exception as e:
                    st.error(f"❌ Error generating plot: {e}")
                    st.info("💡 Hint: Ensure you are selecting the right data types (e.g., trying to put Text on a Y-axis in a Scatter plot will cause an error).")