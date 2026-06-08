import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import json
import glob
import time
import numpy as np
from sklearn.linear_model import LinearRegression

# --- Path Configuration ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.extract_api import extract_crypto_data
from scripts.transform_silver import transform_to_silver
from scripts.load_gold import load_to_gold

# --- Page Configuration ---
st.set_page_config(page_title="Advanced DE Intelligence Engine", page_icon="⚙️", layout="wide")

if 'pipeline_executed' not in st.session_state:
    st.session_state.pipeline_executed = False

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #0b1622; color: #f0f4f8; }
    h1, h2, h3, h4, p, label { color: #f0f4f8 !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button {
        background-color: #2196f3 !important; color: white !important; font-size: 16px !important; 
        font-weight: bold !important; padding: 12px 24px !important; border-radius: 8px !important;
    }
    .back-btn button {
        background-color: transparent !important; color: #a0b4c7 !important; border: 1px solid #3a7bd5 !important; radius: 6px !important;
    }
    .flow-container {
        display: flex; flex-wrap: wrap; justify-content: center; align-items: flex-start; gap: 12px;
        background-color: #132235; padding: 30px 20px; border-radius: 16px; border: 1px solid #1e3a5f; margin-bottom: 30px;
    }
    .flow-box { background: #1a2a40; border-top: 5px solid #3a7bd5; border-radius: 8px; padding: 15px; text-align: center; width: 14.5%; min-width: 150px; }
    .flow-details { text-align: left; font-size: 11px; color: #a0b4c7; margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px; }
    .flow-arrow { color: #3a7bd5; font-size: 20px; font-weight: bold; align-self: center; margin-top: 40px; }
    [data-testid="stMetric"] { background-color: #1a2a40; border-left: 5px solid #2196f3; padding: 15px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- THE ARCHITECTURAL FLOWCHART ---
flowchart_html = """
<div class="flow-container">
    <div class="flow-box" style="border-color: #4caf50;">
        <div style="font-size:30px;">🌐</div>
        <h4 style="color: #4caf50;">1. Multi-Source Ingestion</h4>
        <div class="flow-details">• CoinCap API (Crypto)<br>• YFinance API (S&P500 Macro)<br>• Parallel Ingestion</div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #cd7f32;">
        <div style="font-size:30px;">🥉</div>
        <h4 style="color: #cd7f32;">2. Bronze Lake</h4>
        <div class="flow-details">• Combined Ingest payloads<br>• Immutable Raw JSON<br>• Pure Storage Isolation</div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #c0c0c0;">
        <div style="font-size:30px;">🥈</div>
        <h4 style="color: #c0c0c0;">3. Silver Processing</h4>
        <div class="flow-details">• Multi-Schema Mapping<br>• Text-to-Float Casts<br>• PyArrow Columnar Parquet</div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #ffd700;">
        <div style="font-size:30px;">🥇</div>
        <h4 style="color: #ffd700;">4. Gold Mart</h4>
        <div class="flow-details">• Unified SQLite Relational DB<br>• Time-Series Appends<br>• Data Observability Logs</div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #9c27b0;">
        <div style="font-size:30px;">📊</div>
        <h4 style="color: #9c27b0;">5. Correlation UI</h4>
        <div class="flow-details">• Pearson Math Engine<br>• Cross-Asset Plots<br>• Live Multi-Tab States</div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #00bcd4;">
        <div style="font-size:30px;">🤖</div>
        <h4 style="color: #00bcd4;">6. ML Predictive AI</h4>
        <div class="flow-details">• Scikit-Learn Engine<br>• Linear Regression Core<br>• Next-Tick Price Trend</div>
    </div>
</div>
"""

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
# SCREEN 1: LANDING PRESENTATION
# ==========================================
if not st.session_state.pipeline_executed:
    st.title("🚀 Advanced Intelligence Data Platform")
    st.markdown("<h4 style='color: #a0b4c7;'>Cross-Asset Macroeconomic Integration & Local ML Trend Prediction</h4>", unsafe_allow_html=True)
    st.markdown(flowchart_html, unsafe_allow_html=True)
    
    col1, _, _ = st.columns([2, 2, 1])
    with col1:
        if st.button("▶ EXECUTE INTELLIGENCE PIPELINE", use_container_width=True):
            with st.spinner("Running Multi-Source ETL & Training ML Models..."):
                time.sleep(1)
                execute_pipeline()
            st.rerun()

# ==========================================
# SCREEN 2: METRICS & INSIGHTS
# ==========================================
else:
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    if st.button("⬅️ Back to Engineering Flowchart"):
        st.session_state.pipeline_executed = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Database Pull
    conn = sqlite3.connect('data/crypto_warehouse.db')
    df = pd.read_sql("SELECT * FROM gold_crypto_prices ORDER BY ingested_at ASC", conn)
    conn.close()
    
    latest_time = df['ingested_at'].max()
    latest_df = df[df['ingested_at'] == latest_time]

    tab1, tab2 = st.tabs(["🏗️ Real-Time ETL Data State", "🧠 Advanced Analytics & ML Forecasting"])

    # --- TAB 1: THE DATA TRANSFORMATION STATE ---
    with tab1:
        st.markdown("### 🔍 Enterprise Multi-Schema Observer")
        col_b, col_s, col_g = st.columns(3)
        with col_b:
            st.markdown("#### 🥉 Bronze Lake (Combined Raw JSON)")
            bronze_file = get_latest_file('data/bronze', '.json')
            if bronze_file:
                with open(bronze_file, 'r') as f: st.json(json.load(f))
        with col_s:
            st.markdown("#### 🥈 Silver Lake (Typed Parquet)")
            silver_file = get_latest_file('data/silver', '.parquet')
            if silver_file:
                st.dataframe(pd.read_parquet(silver_file), hide_index=True)
        with col_g:
            st.markdown("#### 🥇 Gold Warehouse (Relational Records)")
            st.dataframe(latest_df[['symbol', 'priceUsd', 'ingested_at']], hide_index=True)

    # --- TAB 2: AI INSIGHTS, CORRELATION & MACHINE LEARNING ---
    with tab2:
        st.markdown("### 🧠 AI Analysis & Macro Correlation")
        
        # Mathematical Pearson Correlation Computation
        clean_df = df.drop_duplicates(subset=['ingested_at', 'symbol'])
        pivot_df = clean_df.pivot(index='ingested_at', columns='symbol', values='priceUsd')
        
        correlation_msg = "Awaiting more time-series points to calculate correlation..."
        corr_value = 0.0
        if 'BTC' in pivot_df.columns and 'S&P500' in pivot_df.columns and len(pivot_df) > 1:
            corr_value = pivot_df['BTC'].corr(pivot_df['S&P500'])
            if pd.isna(corr_value):
                correlation_msg = "Data points identical. Run the pipeline again in a few seconds to build historical variance."
            elif corr_value > 0.5:
                correlation_msg = f"Strong Positive Correlation ({corr_value:.2f}). Bitcoin is currently moving symmetrically with the S&P 500 Equity Market."
            elif corr_value < -0.5:
                correlation_msg = f"Strong Negative Correlation ({corr_value:.2f}). Bitcoin is acting as an inverse hedge to traditional equities."
            else:
                correlation_msg = f"Weak/Neutral Correlation ({corr_value:.2f}). The crypto market is decoupling from traditional assets."

        # Scikit-Learn Local Machine Learning Forecasting Engine
        ml_prediction_msg = "Collecting historical data for ML modeling..."
        btc_history = df[df['symbol'] == 'BTC'].sort_values('ingested_at')
        
        if len(btc_history) >= 2:
            X = np.array(range(len(btc_history))).reshape(-1, 1)
            y = btc_history['priceUsd'].values
            
            ml_model = LinearRegression()
            ml_model.fit(X, y)
            
            next_tick = np.array([[len(btc_history)]])
            predicted_price = ml_model.predict(next_tick)[0]
            current_price = y[-1]
            
            trend = "📈 UPWARD TREND" if predicted_price > current_price else "📉 DOWNWARD TREND"
            ml_prediction_msg = f"trained a local **Linear Regression Model** on {len(btc_history)} historical records. The AI predicts an **{trend}** for the next ingestion interval, target price projection: **${predicted_price:,.2f}**."

        # Display AI Logic Panel
        st.info(f"**🤖 Automated AI Inference Output:**\n\n* **Macro Correlation:** {correlation_msg}\n\n* **Predictive ML Analytics:** The engine {ml_prediction_msg}")
        
        st.markdown("---")
        st.subheader("📊 Macro vs. Crypto Time-Series Tracker")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### Crypto Assets (USD)")
            crypto_chart = pivot_df[[c for c in pivot_df.columns if c != 'S&P500']]
            st.line_chart(crypto_chart)
        with col_c2:
            st.markdown("#### Stock Market: S&P 500 Index (Points)")
            if 'S&P500' in pivot_df.columns:
                st.line_chart(pivot_df['S&P500'])

        st.markdown("---")
        st.subheader("⚡ Active Asset KPI Monitors")
        cols = st.columns(len(latest_df))
        for index, row in latest_df.reset_index().iterrows():
            with cols[index]:
                if row['symbol'] == 'S&P500':
                    st.metric(label="🇺🇸 S&P 500 Index", value=f"{row['priceUsd']:,.2f} pts")
                else:
                    st.metric(label=f"🪙 {row['symbol']}", value=f"${row['priceUsd']:,.2f}")

    # Sidebar Control Box
    with st.sidebar:
        st.header("⚙️ Engine Control")
        st.metric("Total Warehouse Rows", len(df))
        st.text(f"Last Execution:\n{latest_time}")
        st.markdown("---")
        if st.button("🔄 Sync Fresh Data & Retrain"):
            with st.spinner("Re-running ETL..."): execute_pipeline()
            st.rerun()
