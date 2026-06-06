import streamlit as st
import pandas as pd
import sqlite3
import os
import sys

# --- Path Configuration ---
# This allows the dashboard to find your scripts folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.extract_api import extract_crypto_data
from scripts.transform_silver import transform_to_silver
from scripts.load_gold import load_to_gold

# --- Page Configuration ---
st.set_page_config(page_title="Crypto Data Engine", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- Data Loading ---
def load_data():
    db_path = 'data/crypto_warehouse.db'
    if not os.path.exists(db_path):
        return pd.DataFrame()
        
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM gold_crypto_prices ORDER BY ingested_at ASC", conn)
    conn.close()
    return df

df = load_data()

# --- UI Layout ---
st.title("⚡ Live Crypto Data Warehouse")
st.markdown("Automated Medallion Pipeline: **CoinCap API ➔ JSON ➔ Parquet ➔ SQLite**")

# --- Sidebar: Pipeline Control ---
with st.sidebar:
    st.header("🛠️ Pipeline Control")
    
    # THE NEW DE FLEX: A button to trigger the pipeline from the web!
    if st.button("🔄 Trigger Data Pipeline Now", use_container_width=True):
        with st.spinner("Extracting (Bronze) ➔ Transforming (Silver) ➔ Loading (Gold)..."):
            extract_crypto_data()
            transform_to_silver()
            load_to_gold()
        st.success("Pipeline executed successfully!")
        st.rerun() # Refresh the page to show new data
        
    st.markdown("---")
    st.markdown("**Architecture:**")
    st.markdown("- 🥉 **Bronze:** Raw JSON")
    st.markdown("- 🥈 **Silver:** PyArrow/Parquet")
    st.markdown("- 🥇 **Gold:** SQLite DB")

if df.empty:
    st.warning("Database is currently empty. Click the 'Trigger Data Pipeline Now' button in the sidebar to run the Medallion Architecture!")
else:
    latest_time = df['ingested_at'].max()
    latest_df = df[df['ingested_at'] == latest_time]
    
    with st.sidebar:
        st.metric(label="Total Records in Warehouse", value=len(df))
        st.text(f"Last Updated:\n{latest_time}")

    st.subheader("Market Snapshots (Latest Run)")
    cols = st.columns(len(latest_df))
    
    for index, row in latest_df.reset_index().iterrows():
        with cols[index]:
            price = f"${row['priceUsd']:,.2f}"
            st.metric(label=f"{row['symbol']} Price", value=price)

    st.markdown("---")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📈 Price History (Time-Series)")
        chart_data = df.pivot(index='ingested_at', columns='symbol', values='priceUsd')
        st.line_chart(chart_data)

    with col2:
        st.subheader("🥇 Gold Layer Audit Table")
        st.dataframe(latest_df[['symbol', 'rank', 'priceUsd', 'ingested_at']], hide_index=True)
