import streamlit as st
import pandas as pd
import sqlite3
import os

# --- Page Configuration ---
st.set_page_config(page_title="Crypto Pipeline Dashboard", layout="wide")

# --- Title and Description ---
st.title("🚀 Automated Crypto Market Dashboard")
st.markdown("### Built with Python, SQLite, and the Medallion Architecture")
st.markdown("This dashboard reads live data directly from our **Gold Layer** Data Warehouse.")

# --- Data Loading Function ---
@st.cache_data(ttl=60) # Cache the data for 60 seconds
def load_data():
    db_path = 'data/crypto_warehouse.db'
    if not os.path.exists(db_path):
        return pd.DataFrame() 
        
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM gold_crypto_prices", conn)
    conn.close()
    return df

# --- Fetch Data ---
df = load_data()

# --- Dashboard Layout ---
if df.empty:
    st.error("No data found! Please run your orchestrator to populate the Data Warehouse.")
else:
    st.success("Successfully connected to the Gold Data Warehouse!")
    
    st.subheader("🪙 Gold Layer Table")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("📊 Market Capitalization (USD)")
    df_sorted = df.sort_values(by='marketCapUsd', ascending=False)
    st.bar_chart(data=df_sorted, x='symbol', y='marketCapUsd', color="#f2a900")