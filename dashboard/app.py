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
st.set_page_config(page_title="DE Pipeline Engine", page_icon="💻", layout="wide")

# --- ADVANCED CYBERPUNK / TECH GEEK CSS ---
st.markdown("""
    <style>
    /* Dark background and neon green text */
    .stApp {
        background-color: #0a0a0a;
        color: #39ff14;
    }
    h1, h2, h3, p, label, .stMarkdown {
        color: #39ff14 !important;
        font-family: 'Courier New', Courier, monospace;
    }
    /* Metric Cards Styling */
    .stMetric {
        background-color: #111111;
        border: 1px solid #39ff14;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(57, 255, 20, 0.2);
    }
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: bold;
    }
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 2px solid #39ff14;
    }
    /* Custom Button Animation */
    .stButton>button {
        border: 1px solid #39ff14;
        color: #39ff14;
        background-color: transparent;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        transition: 0.3s ease-in-out;
        width: 100%;
    }
    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(57, 255, 20, 0.8);
        background-color: #39ff14;
        color: #000000;
        border: 1px solid #ffffff;
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
st.title("💻 SYSTEM: DATA_ENGINEERING_PIPELINE")
st.markdown("> **STATUS: ONLINE | ARCHITECTURE: MEDALLION | DOMAIN: CRYPTO**")

# --- SIDEBAR ---
with st.sidebar:
    st.header("TERMINAL // CONTROL")
    if st.button("▶ EXECUTE_ETL_SEQUENCE()"):
        with st.spinner("INITIATING EXTRACT ➔ TRANSFORM ➔ LOAD..."):
            extract_crypto_data()
            transform_to_silver()
            load_to_gold()
        st.success("SEQUENCE COMPLETE. WAREHOUSE UPDATED.")
        st.rerun()
        
    st.markdown("---")
    if not df.empty:
        latest_time = df['ingested_at'].max()
        st.metric("TOTAL_DB_RECORDS", len(df))
        st.text(f"LAST_SYNC:\n{latest_time}")

# --- MAIN CONTENT TABS ---
if df.empty:
    st.warning("SYSTEM EMPTY. PLEASE EXECUTE PIPELINE FROM CONTROL TERMINAL.")
else:
    latest_time = df['ingested_at'].max()
    latest_df = df[df['ingested_at'] == latest_time]

    # Create the educational tabs!
    tab_dash, tab_bronze, tab_silver, tab_gold = st.tabs([
        "📊 EXECUTIVE_DASHBOARD", 
        "🥉 BRONZE_LAYER (Raw)", 
        "🥈 SILVER_LAYER (Clean)", 
        "🥇 GOLD_LAYER (Warehouse)"
    ])

    # --- TAB 1: DASHBOARD ---
    with tab_dash:
        st.subheader("MARKET_SNAPSHOT // LATEST")
        cols = st.columns(len(latest_df))
        for index, row in latest_df.reset_index().iterrows():
            with cols[index]:
                price = f"${row['priceUsd']:,.2f}"
                st.metric(label=f"TICKER: {row['symbol']}", value=price)
        
        st.markdown("---")
        st.subheader("TIME_SERIES_ANALYSIS")
        chart_data = df.pivot(index='ingested_at', columns='symbol', values='priceUsd')
        st.line_chart(chart_data)

    # --- TAB 2: BRONZE LAYER ---
    with tab_bronze:
        st.subheader("🥉 PHASE 1: DATA EXTRACTION (BRONZE)")
        st.markdown("*Purpose: Ingest raw, untyped, nested data from external APIs without modification. This ensures data lineage and provides a backup if downstream processes fail.*")
        bronze_file = get_latest_file('data/bronze', '.json')
        if bronze_file:
            st.code(f"READING RAW SOURCE: {bronze_file}", language='bash')
            with open(bronze_file, 'r') as f:
                raw_json = json.load(f)
            # Show exactly what the raw API data looks like
            st.json(raw_json)
        else:
            st.error("No Bronze files found.")

    # --- TAB 3: SILVER LAYER ---
    with tab_silver:
        st.subheader("🥈 PHASE 2: TRANSFORMATION (SILVER)")
        st.markdown("*Purpose: Flatten messy JSON, cast strings to floats/integers, drop unneeded columns, and compress into columnar Parquet files for high-speed processing.*")
        silver_file = get_latest_file('data/silver', '.parquet')
        if silver_file:
            st.code(f"READING PARQUET ENGINE: {silver_file}", language='bash')
            df_silver = pd.read_parquet(silver_file)
            st.dataframe(df_silver, use_container_width=True)
            
            st.markdown("**Data Types fixed by Python (Pandas) in this layer:**")
            # Show the data types to prove you cleaned them
            dtypes_df = df_silver.dtypes.astype(str).reset_index().rename(columns={'index':'Column Name', 0:'Data Type'})
            st.dataframe(dtypes_df, hide_index=True)
        else:
            st.error("No Silver files found.")

    # --- TAB 4: GOLD LAYER ---
    with tab_gold:
        st.subheader("🥇 PHASE 3: DATA WAREHOUSE (GOLD)")
        st.markdown("*Purpose: Load the cleaned data into a structured Relational Database. Append an `ingested_at` timestamp to track historical trends so Business Analysts can query time-series data.*")
        st.code("SQL QUERY: SELECT * FROM gold_crypto_prices ORDER BY ingested_at DESC", language='sql')
        
        # Load data descending so the newest stuff is at the top of the table
        conn = sqlite3.connect('data/crypto_warehouse.db')
        df_gold_desc = pd.read_sql("SELECT * FROM gold_crypto_prices ORDER BY ingested_at DESC", conn)
        conn.close()
        
        st.dataframe(df_gold_desc, use_container_width=True)
