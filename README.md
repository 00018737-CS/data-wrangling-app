LINK: https://data-wrangling-app-envvf2r4tfbadgk4sglyo6.streamlit.app/

TOKEN FOR AI: "AIzaSyBdEeFxpiyO7J0D-uKjBhNx-O9vyyl10DE"
If the API of the AI is outdated, please get new from the following website: https://aistudio.google.com/api-keys

# 🛠️ AI Data Wrangler & Visualizer

A comprehensive, Streamlit-based web application for automated data cleaning, transformation, and exploratory data analysis (EDA). This tool features an **AI-powered assistant** to handle natural language data cleaning requests safely and efficiently.

---

## 🌟 Key Features

### 📡 Page A: Upload & Overview

- **Multi-format Support:** Upload CSV or Excel files.
- **Smart Summary:** Automatic detection of data shapes, types, and memory usage.
- **Interactive Preview:** High-level statistics and raw data exploration.

### 🧹 Page B: Cleaning Studio

- **AI Assistant:** Perform complex cleaning (dropping duplicates, trimming spaces, filling nulls) using natural language prompts powered by Google Gemini.
- **Manual Toolset (8 Specialized Tabs):**
  - **Missing Values:** Imputation (Mean, Median, Mode) or row/column dropping.
  - **Duplicates:** Full-row or subset-based duplicate removal.
  - **Data Types:** Clean "dirty" numeric strings and parse dates.
  - **Categories:** UI-based mapping editor, rare category grouping, and One-Hot Encoding.
  - **Outliers:** Detection via IQR or Z-Score with Winsorization (capping).
  - **Scaling:** Min-Max and Z-score normalization with before/after stats.
  - **Column Ops:** Mathematical formula-based feature engineering and binning.
  - **Validation:** Custom rule definition to flag data violations.

### 📈 Page C: Visualization Builder

- **Global Filtering:** Slice data by numeric ranges or categories before plotting.
- **6 Professional Chart Types:** Scatter, Histogram, Box Plot, Line (Time Series), Bar (Aggregated), and Correlation Heatmaps.
- **Top-N Logic:** Automatically focus on the most important categories in bar charts.

### 💾 Page D: Export & Report

- **Transformation Log:** A chronological record of every change made to the data.
- **Secure Download:** Export the cleaned dataset back to CSV.
- **Session Reset:** One-click button to clear all memory and start fresh.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- A Google Gemini API Key (for AI features)
