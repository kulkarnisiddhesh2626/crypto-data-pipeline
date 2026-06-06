import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import json
import glob
import time

# --- Path Configuration ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.extract_api import extract_crypto_data
from scripts.transform_silver import transform_to_silver
from scripts.load_gold import load_to_gold

# --- Page Configuration ---
st.set_page_config(page_title="DE Pipeline Engine", page_icon="⚙️", layout="wide")

# --- SESSION STATE INITIALIZATION ---
# This acts as our "lock" to ensure we show the landing page first
if 'pipeline_executed' not in st.session_state:
    st.session_state.pipeline_executed = False

# --- ENTERPRISE CSS & FLOWCHART STYLING ---
st.markdown("""
    <style>
    /* Dark Theme */
    .stApp { background-color: #0b1622; color: #f0f4f8; }
    h1, h2, h3, h4, p, label { color: #f0f4f8 !important; font-family: 'Segoe UI', Tahoma, sans-serif; }
    
    /* Big Execute Button Styling */
    .execute-btn button {
        background-color: #00d2ff; background-image: linear-gradient(to right, #00d2ff 0%, #3a7bd5 100%);
        color: white !important; font-size: 24px !important; font-weight: 800; padding: 20px !important; 
        border-radius: 12px; border: none; box-shadow: 0 10px 20px rgba(0, 210, 255, 0.4); transition: all 0.3s;
    }
    .execute-btn button:hover { transform: scale(1.02); box-shadow: 0 15px 25px rgba(0, 210, 255, 0.6); }
    
    /* Architectural Flowchart CSS */
    .flow-container {
        display: flex; justify-content: space-between; align-items: center; 
        background-color: #132235; padding: 40px; border-radius: 16px; 
        border: 1px solid #1e3a5f; margin: 40px 0; box-shadow: 0 8px 30px rgba(0,0,0,0.5);
    }
    .flow-box {
        background: #1a2a40; border: 2px solid #3a7bd5; border-radius: 12px; 
        padding: 25px 15px; text-align: center; color: white; width: 22%; position: relative;
    }
    .flow-box h3 { margin: 0 0 10px 0; font-size: 22px; }
    .flow-box p { margin: 0; font-size: 14px; color: #a0b4c7 !important; line-height: 1.4; }
    .source { border-color: #4caf50; }
    .bronze { border-color: #cd7f32; }
    .silver { border-color: #c0c0c0; }
    .gold { border-color: #ffd700; }
    .flow-arrow { color: #3a7bd5; font-size: 35px; font-weight: bold; }
    
    /* KPI Cards */
    [data-testid="stMetric"] { background-color: #1a2a40; border-left: 5px solid #3a7bd5; padding: 15px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- THE ARCHITECTURAL FLOWCHART (HTML) ---
flowchart_html = """
<div class="flow-container">
    <div class="flow-box source">
        <h3 style="color: #4caf50;">🌐 Source API</h3>
        <p><b>Data:</b> Live Crypto Feed<br><b>Format:</b> Nested JSON<br><b>Tool:</b> Python Requests</p>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box bronze">
        <h3 style="color: #cd7f32;">🥉 Bronze Layer</h3>
        <p><b>Data:</b> Raw Extraction<br><b>Format:</b> Raw JSON Files<br><b>Goal:</b> Data Lineage / Backup</p>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box silver">
        <h3 style="color: #c0c0c0;">🥈 Silver Layer</h3>
        <p><b>Data:</b> Cleaned & Typed<br><b>Format:</b> Columnar Parquet<br><b>Tool:</b> Pandas & PyArrow</p>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box gold">
        <h3 style="color: #ffd700;">🥇 Gold Layer</h3>
        <p><b>Data:</b> Business Ready<br><b>Format:</b> SQLite Database<br><b>Goal:</b> Time-Series Analytics</p>
    </div>
</div>
"""

# --- HELPER FUNCTIONS ---
def get_latest_file(folder, extension):
    if not os.path.exists(folder): return None
    files = glob.glob(f"{folder}/*{extension}")
    if not files: return None
    return max(files, key=os.path.getctime)

def execute_pipeline():
    extract_crypto_data()
    transform_to_silver()
    load_to_gold()
    st.session_state.pipeline_executed = True

# ==========================================
# PAGE 1: THE LANDING PRESENTATION
# ==========================================
if not st.session_state.pipeline_executed:
    st.title("🚀 Enterprise Data Engineering Pipeline")
    st.markdown("<h4 style='color: #a0b4c7;'>End-to-End Automated Medallion Architecture (Bronze ➔ Silver ➔ Gold)</h4>", unsafe_allow_html=True)
    
    # 1. Show the Flowchart Design
    st.markdown(flowchart_html, unsafe_allow_html=True)
    
    # 2. Big Execute Button
    st.markdown("<div class='execute-btn'>", unsafe_allow_html=True)
    if st.button("▶ EXECUTE DE WORKFLOW", use_container_width=True):
        with st.spinner("Executing Data Pipeline: Extracting (Bronze) ➔ Transforming (Silver) ➔ Loading (Gold)..."):
            time.sleep(1) # Small pause for visual effect during presentation
            execute_pipeline()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PAGE 2: THE UNLOCKED DASHBOARD TABS
# ==========================================
else:
    # Load Data after execution
    conn = sqlite3.connect('data/crypto_warehouse.db')
    df = pd.read_sql("SELECT * FROM gold_crypto_prices ORDER BY ingested_at ASC", conn)
    conn.close()
    
    latest_time = df['ingested_at'].max()
    latest_df = df[df['ingested_at'] == latest_time]

    # Header and Tabs
    st.title("✅ Pipeline Execution Successful")
    tab1, tab2 = st.tabs(["🏗️ Real-Time ETL Data State", "📊 AI Analytics & KPI Dashboard"])

    # --- TAB 1: THE REAL-TIME DATA STATE (DE VIEW) ---
    with tab1:
        st.markdown("### Pipeline Architecture Overview")
        st.markdown(flowchart_html, unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("### 🔍 Real-Time Data Transformation State")
        st.markdown("Below is the exact state of the data as it moved through each stage of the pipeline just now.")
        
        col_b, col_s, col_g = st.columns(3)
        with col_b:
            st.markdown("#### 🥉 Bronze (Raw JSON)")
            bronze_file = get_latest_file('data/bronze', '.json')
            if bronze_file:
                with open(bronze_file, 'r') as f: st.json(json.load(f))
                    
        with col_s:
            st.markdown("#### 🥈 Silver (Parquet)")
            silver_file = get_latest_file('data/silver', '.parquet')
            if silver_file:
                df_silver = pd.read_parquet(silver_file)
                st.dataframe(df_silver, hide_index=True)
                st.caption("Flat schema, proper floats, columnar compression.")
                
        with col_g:
            st.markdown("#### 🥇 Gold (SQL Database)")
            st.dataframe(latest_df[['symbol', 'priceUsd', 'marketCapUsd', 'ingested_at']], hide_index=True)
            st.caption("Structured table with ingestion timestamps.")

    # --- TAB 2: KPIs & INFERENCES (ANALYTICS VIEW) ---
    with tab2:
        # AI Summary Generation
        top_coin = latest_df.loc[latest_df['priceUsd'].idxmax()]
        avg_price = latest_df['priceUsd'].mean()
        
        st.subheader("🤖 AI Data Inference Summary")
        st.info(f"**Automated Insights:** The Medallion pipeline completed its ingestion at **{latest_time}**. Data types were successfully enforced in the Silver layer and loaded into Gold. Currently, the highest value asset in the tracked portfolio is **{top_coin['symbol']}** at **${top_coin['priceUsd']:,.2f}**. The average asset price across the dataset is **${avg_price:,.2f}**.")
        
        st.markdown("---")
        st.subheader("Live Market KPIs")
        cols = st.columns(len(latest_df))
        for index, row in latest_df.reset_index().iterrows():
            with cols[index]:
                st.metric(label=f"{row['symbol']}", value=f"${row['priceUsd']:,.2f}")
        
        st.markdown("---")
        st.subheader("📈 Asset Price History (Time-Series)")
        chart_data = df.pivot(index='ingested_at', columns='symbol', values='priceUsd')
        st.line_chart(chart_data)
        
    # Sidebar allows user to run it again
    with st.sidebar:
        st.header("⚙️ Controls")
        if st.button("🔄 Rerun Pipeline"):
            with st.spinner("Running ETL..."): execute_pipeline()
            st.rerun()
