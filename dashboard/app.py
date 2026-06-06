import streamlit as st
import pandas as pd
import sqlite3
import os

# --- Page Configuration ---
st.set_page_config(page_title="Crypto Data Engine", page_icon="📈", layout="wide")

# --- Custom CSS for a cleaner look ---
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
    # Pull the data and sort by the exact time it was ingested
    df = pd.read_sql("SELECT * FROM gold_crypto_prices ORDER BY ingested_at ASC", conn)
    conn.close()
    return df

df = load_data()

# --- UI Layout ---
st.title("⚡ Live Crypto Data Warehouse")
st.markdown("Automated Medallion Pipeline: **CoinCap API ➔ JSON ➔ Parquet ➔ SQLite**")

if df.empty:
    st.warning("Awaiting first pipeline run. Please start your orchestrator.")
else:
    # Get the absolute latest data for our KPI cards
    latest_time = df['ingested_at'].max()
    latest_df = df[df['ingested_at'] == latest_time]
    
    # --- Sidebar: Pipeline Health ---
    with st.sidebar:
        st.header("🛠️ Pipeline Health")
        st.success("Status: ONLINE")
        st.metric(label="Total Records in Warehouse", value=len(df))
        st.text(f"Last Updated:\n{latest_time}")
        st.markdown("---")
        st.markdown("**Architecture:**")
        st.markdown("- 🥉 **Bronze:** Raw JSON")
        st.markdown("- 🥈 **Silver:** PyArrow/Parquet")
        st.markdown("- 🥇 **Gold:** SQLite DB")

    # --- Top Row: KPI Metrics ---
    st.subheader("Market Snapshots (Latest Run)")
    
    # Dynamically create columns based on how many coins we have
    cols = st.columns(len(latest_df))
    
    for index, row in latest_df.reset_index().iterrows():
        with cols[index]:
            # Format numbers to look like currency
            price = f"${row['priceUsd']:,.2f}"
            st.metric(label=f"{row['symbol']} Price", value=price)

    st.markdown("---")

    # --- Bottom Row: Charts and Tables ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📈 Price History (Time-Series)")
        # Pivot the data so Streamlit can easily draw a multi-line chart
        chart_data = df.pivot(index='ingested_at', columns='symbol', values='priceUsd')
        st.line_chart(chart_data)

    with col2:
        st.subheader("🥇 Gold Layer Audit Table")
        # Show the most recent rows to prove the data structure
        st.dataframe(latest_df[['symbol', 'rank', 'priceUsd', 'ingested_at']], hide_index=True)
