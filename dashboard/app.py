import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import json
import glob

# --- Path Configuration ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.extract_api import extract_crypto_data
from scripts.transform_silver import transform_to_silver
from scripts.load_gold import load_to_gold

# --- Page Configuration ---
st.set_page_config(page_title="DE Pipeline Engine", page_icon="📊", layout="wide")

# --- CLEAN ENTERPRISE CSS ---
st.markdown("""
    <style>
    /* Professional Dark Blue Theme */
    .stApp {
        background-color: #0b1622;
        color: #f0f4f8;
    }
    [data-testid="stSidebar"] {
        background-color: #132235;
    }
    /* Safe text color overrides that won't break icons */
    h1, h2, h3, h4, h5, h6, p, label {
        color: #f0f4f8 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Metric Cards Styling */
    [data-testid="stMetric"] {
        background-color: #1a2a40;
        border-left: 5px solid #2196f3;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    [data-testid="stMetricValue"] {
        color: #64b5f6 !important;
    }
    /* Sleek Button Styling */
    .stButton>button {
        background-color: #2196f3;
        color: white !important;
        border-radius: 6px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #42a5f5;
        box-shadow: 0 4px 10px rgba(33, 150, 243, 0.3);
        color: white !important;
    }
    /* Clean Tab Styling */
    .stTabs [data-baseweb="tab"] {
        color: #8da1b9;
    }
    .stTabs [aria-selected="true"] {
        color: #2196f3 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def get_latest_file(folder, extension):
    files = glob.glob(f"{folder}/*{extension}")
    if not files: return None
    return max(files, key=os.path.getctime)

def load_gold_data():
    db_path = 'data/crypto_warehouse.db'
    if not os.path.exists(db_path): return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM gold_crypto_prices ORDER BY ingested_at ASC", conn)
    conn.close()
    return df

df = load_gold_data()

# --- HEADER ---
st.title("🚀 Enterprise Data Pipeline Architecture")
st.markdown("Automated ETL workflow transforming live API data into an analytical Data Warehouse.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Pipeline Controls")
    if st.button("🔄 Execute ETL Workflow"):
        with st.spinner("Extracting (Bronze) ➔ Transforming (Silver) ➔ Loading (Gold)..."):
            extract_crypto_data()
            transform_to_silver()
            load_to_gold()
        st.success("Pipeline Run Complete!")
        st.rerun()
        
    st.markdown("---")
    if not df.empty:
        latest_time = df['ingested_at'].max()
        st.metric("Total Warehouse Records", len(df))
        st.text(f"Last Synced:\n{latest_time}")

# --- MAIN CONTENT TABS ---
if df.empty:
    st.info("The Data Warehouse is currently empty. Click 'Execute ETL Workflow' in the sidebar to run the pipeline.")
else:
    latest_time = df['ingested_at'].max()
    latest_df = df[df['ingested_at'] == latest_time]

    tab_dash, tab_bronze, tab_silver, tab_gold = st.tabs([
        "📊 Executive Dashboard", 
        "🥉 Bronze Layer (Raw)", 
        "🥈 Silver Layer (Clean)", 
        "🥇 Gold Layer (Warehouse)"
    ])

    # --- TAB 1: DASHBOARD ---
    with tab_dash:
        st.subheader("Live Market Snapshot")
        cols = st.columns(len(latest_df))
        for index, row in latest_df.reset_index().iterrows():
            with cols[index]:
                price = f"${row['priceUsd']:,.2f}"
                st.metric(label=f"{row['symbol']}", value=price)
        
        st.markdown("---")
        st.subheader("Price History Trends")
        chart_data = df.pivot(index='ingested_at', columns='symbol', values='priceUsd')
        st.line_chart(chart_data)

    # --- TAB 2: BRONZE LAYER ---
    with tab_bronze:
        st.subheader("Data Extraction: Bronze Layer")
        st.markdown("*Ingests raw JSON payloads from the external API to maintain data lineage and historical backups.*")
        bronze_file = get_latest_file('data/bronze', '.json')
        if bronze_file:
            st.code(f"File Path: {bronze_file}", language='bash')
            with open(bronze_file, 'r') as f:
                raw_json = json.load(f)
            st.json(raw_json)

    # --- TAB 3: SILVER LAYER ---
    with tab_silver:
        st.subheader("Data Transformation: Silver Layer")
        st.markdown("*Flattens JSON structure, enforces schema datatypes, and compresses the output into columnar Parquet files.*")
        silver_file = get_latest_file('data/silver', '.parquet')
        if silver_file:
            st.code(f"File Path: {silver_file}", language='bash')
            df_silver = pd.read_parquet(silver_file)
            st.dataframe(df_silver, use_container_width=True)
            
            st.markdown("**Schema Enforcement (Data Types):**")
            dtypes_df = df_silver.dtypes.astype(str).reset_index().rename(columns={'index':'Column Name', 0:'Data Type'})
            st.dataframe(dtypes_df, hide_index=True)

    # --- TAB 4: GOLD LAYER ---
    with tab_gold:
        st.subheader("Data Warehouse: Gold Layer")
        st.markdown("*Loads cleaned data into a relational database, appending ingestion timestamps for time-series analytics.*")
        st.code("SELECT * FROM gold_crypto_prices ORDER BY ingested_at DESC", language='sql')
        
        conn = sqlite3.connect('data/crypto_warehouse.db')
        df_gold_desc = pd.read_sql("SELECT * FROM gold_crypto_prices ORDER BY ingested_at DESC", conn)
        conn.close()
        
        st.dataframe(df_gold_desc, use_container_width=True)
