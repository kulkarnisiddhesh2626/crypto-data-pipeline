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
st.set_page_config(page_title="Enterprise Intelligence Engine", page_icon="⚙️", layout="wide")

if 'pipeline_executed' not in st.session_state:
    st.session_state.pipeline_executed = False

# --- SYSTEM STYLING ---
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
    .signal-box { padding: 20px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; font-size: 16px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- PIPELINE FLOWCHART GENERATOR ---
flowchart_html = """
<div class="flow-container">
    <div class="flow-box" style="border-color: #4caf50;">
        <div style="font-size:30px;">🌐</div>
        <h4 style="color: #4caf50;">1. Ingestion</h4>
        <div class="flow-details">• CoinCap Crypto API<br>• YFinance S&P500 Macro<br>• Unified Ingestion</div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #cd7f32;">
        <div style="font-size:30px;">🥉</div>
        <h4 style="color: #cd7f32;">2. Bronze Lake</h4>
        <div class="flow-details">• Raw Array Payloads<br>• Immutable JSON Files<br>• Lineage Foundations</div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #c0c0c0;">
        <div style="font-size:30px;">🥈</div>
        <h4 style="color: #c0c0c0;">3. Silver Processing</h4>
        <div class="flow-details">• Multi-Schema Casts<br>• Text-to-Float Cleaning<br>• PyArrow Column Parquet</div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #ffd700;">
        <div style="font-size:30px;">🥇</div>
        <h4 style="color: #ffd700;">4. Gold Warehouse</h4>
        <div class="flow-details">• SQLite Relational Core<br>• Time-Series Appends<br>• Primary Key Audits</div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #9c27b0;">
        <div style="font-size:30px;">📊</div>
        <h4 style="color: #9c27b0;">5. serving Layer</h4>
        <div class="flow-details">• Pearson Math Core<br>• Dual Axis Charts<br>• Storage Analytics</div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #00bcd4;">
        <div style="font-size:30px;">🤖</div>
        <h4 style="color: #00bcd4;">6. Predictive ML</h4>
        <div class="flow-details">• Scikit-Learn Engine<br>• Regression Trends<br>• Trade Directives</div>
    </div>
</div>
"""

def get_latest_file(folder, extension):
    if not os.path.exists(folder): return None
    files = glob.glob(f"{folder}/*{extension}")
    if not files: return None
    return max(files, key=os.path.getctime)

def calculate_de_metrics():
    b_file = get_latest_file('data/bronze', '.json')
    s_file = get_latest_file('data/silver', '.parquet')
    if b_file and s_file:
        b_size = os.path.getsize(b_file)
        s_size = os.path.getsize(s_file)
        savings = ((b_size - s_size) / b_size) * 100 if b_size > 0 else 0
        return b_size, s_size, savings
    return 0, 0, 0

def execute_pipeline():
    extract_crypto_data()
    transform_to_silver()
    load_to_gold()
    st.session_state.pipeline_executed = True

# ==========================================
# SCREEN 1: ARCHITECTURE MAP
# ==========================================
if not st.session_state.pipeline_executed:
    st.title("🚀 Enterprise Data Platform & Predictive Intelligence")
    st.markdown("<h4 style='color: #a0b4c7;'>Cross-Asset Macro Integration, Storage Optimization & Scikit-Learn Regression Forecasting</h4>", unsafe_allow_html=True)
    st.markdown(flowchart_html, unsafe_allow_html=True)
    
    col1, _, _ = st.columns([2, 2, 1])
    with col1:
        if st.button("▶ EXECUTE INTELLIGENCE PIPELINE", use_container_width=True):
            with st.spinner("Running Multi-Source ETL & Tuning ML Models..."):
                time.sleep(1)
                execute_pipeline()
            st.rerun()

# ==========================================
# SCREEN 2: INTELLIGENCE PANEL
# ==========================================
else:
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    if st.button("⬅️ Back to Architecture Blueprint"):
        st.session_state.pipeline_executed = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Ingest Data from Database
    conn = sqlite3.connect('data/crypto_warehouse.db')
    df = pd.read_sql("SELECT * FROM gold_crypto_prices ORDER BY ingested_at ASC", conn)
    conn.close()
    
    latest_time = df['ingested_at'].max()
    latest_df = df[df['ingested_at'] == latest_time]

    tab1, tab2 = st.tabs(["🏗️ Pipeline Infrastructure State", "🧠 Advanced Analytics & ML Inference"])

    # --- TAB 1: DATA ENGINEERING LINEAGE & PERFORMANCE TRACKER ---
    with tab1:
        st.markdown("### 🔍 Enterprise Data State Inspector")
        
        # New Feature Visual: Data Engineering Optimization Cards
        b_size, s_size, savings = calculate_de_metrics()
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Raw Bronze Payload Size", f"{b_size} Bytes", help="Size of uncompressed unstructured JSON payload.")
        with col_m2:
            st.metric("Compressed Silver Size", f"{s_size} Bytes", help="Size of optimized pyarrow columnar storage.")
        with col_m3:
            st.metric("Storage Optimization Ratio", f"{savings:.1f}% Savings", delta=f"{savings:.1f}% Efficient", help="Disk optimization savings achieved by switching formats.")

        st.markdown("---")
        col_b, col_s, col_g = st.columns(3)
        with col_b:
            st.markdown("#### 🥉 Bronze Lake (Raw Source JSON)")
            bronze_file = get_latest_file('data/bronze', '.json')
            if bronze_file:
                with open(bronze_file, 'r') as f: st.json(json.load(f))
        with col_s:
            st.markdown("#### 🥈 Silver Lake (Cleaned Columnar Parquet)")
            silver_file = get_latest_file('data/silver', '.parquet')
            if silver_file:
                st.dataframe(pd.read_parquet(silver_file), hide_index=True)
        with col_g:
            st.markdown("#### 🥇 Gold Warehouse (Relational Store)")
            st.dataframe(latest_df[['symbol', 'priceUsd', 'ingested_at']], hide_index=True)

    # --- TAB 2: ADVANCED ANALYTICS & PREDICTIVE MACHINE LEARNING ---
    with tab2:
        st.markdown("### 🧠 AI Analytics & Macroeconomic Correlation")
        
        clean_df = df.drop_duplicates(subset=['ingested_at', 'symbol'])
        pivot_df = clean_df.pivot(index='ingested_at', columns='symbol', values='priceUsd')
        
        # Pearson Correlation Analytics
        correlation_msg = "Awaiting more time-series points to calculate correlation statistics..."
        corr_value = 0.0
        if 'BTC' in pivot_df.columns and 'S&P500' in pivot_df.columns and len(pivot_df) > 1:
            corr_value = pivot_df['BTC'].corr(pivot_df['S&P500'])
            if pd.isna(corr_value):
                correlation_msg = "Identical value states recorded. Sync fresh data in a few seconds to trigger variance."
            elif corr_value > 0.4:
                correlation_msg = f"Strong Positive Correlation ({corr_value:.2f}). Crypto and Equities are advancing symmetrically."
            elif corr_value < -0.4:
                correlation_msg = f"Strong Inverse Correlation ({corr_value:.2f}). Bitcoin is behaving as a macroeconomic safety hedge."
            else:
                correlation_msg = f"Neutral Decoupling Index ({corr_value:.2f}). The cryptocurrency assets are trading independently of global equity models."

        # Scikit-Learn Local Pipeline Forecast Core
        ml_prediction_msg = "Awaiting structural historic logging points..."
        trend_signal = "NEUTRAL STATE"
        signal_color = "#FFA500" # Orange
        
        btc_history = df[df['symbol'] == 'BTC'].sort_values('ingested_at')
        if len(btc_history) >= 2:
            X = np.array(range(len(btc_history))).reshape(-1, 1)
            y = btc_history['priceUsd'].values
            
            ml_model = LinearRegression()
            ml_model.fit(X, y)
            
            next_tick = np.array([[len(btc_history)]])
            predicted_price = ml_model.predict(next_tick)[0]
            current_price = y[-1]
            
            if predicted_price > current_price:
                trend_signal = "ACCELERATING BULLISH SYMMETRY"
                signal_color = "#2E7D32" # Dark Green
            else:
                trend_signal = "DEFENSIVE CONSOLIDATION SIGNAL"
                signal_color = "#C62828" # Dark Red
                
            ml_prediction_msg = f"trained a local **Linear Regression Predictive Core** on {len(btc_history)} historic ticks. Target value projection for next sync sequence: **${predicted_price:,.2f}**."

        # New Visual Feature: High-Impact AI Signal Box
        st.markdown(f'<div class="signal-box" style="background-color: {signal_color};">🤖 LIVE SYSTEM SIGNAL: {trend_signal}</div>', unsafe_allow_html=True)
        st.info(f"**💡 Machine Inferences Summary:**\n\n* **Macro Correlation Strategy:** {correlation_msg}\n\n* **Mathematical Modeling Core:** {ml_prediction_msg}")
        
        st.markdown("---")
        st.subheader("📊 Cross-Asset Multi-Axis Tracking Engine")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### Cryptocurrency Pricing Curves (USD)")
            crypto_chart = pivot_df[[c for c in pivot_df.columns if c != 'S&P500']]
            st.line_chart(crypto_chart)
        with col_c2:
            st.markdown("#### Macro Equity Benchmarks: S&P 500 Index (Points)")
            if 'S&P500' in pivot_df.columns:
                st.line_chart(pivot_df['S&P500'])

        st.markdown("---")
        st.subheader("⚡ Active Asset KPI Monitors")
        cols = st.columns(len(latest_df))
        for index, row in latest_df.reset_index().iterrows():
            with cols[index]:
                if row['symbol'] == 'S&P500':
                    st.metric(label="🇺🇸 S&P 500 Macro Index", value=f"{row['priceUsd']:,.2f} pts")
                else:
                    st.metric(label=f"🪙 {row['symbol']} Asset", value=f"${row['priceUsd']:,.2f}")

    # Sidebar Observability Module
    with st.sidebar:
        st.header("⚙️ Observability Engine")
        st.metric("Total Warehouse Database Rows", len(df))
        st.text(f"Last Execution Synced:\n{latest_time}")
        st.markdown("---")
        if st.button("🔄 Sync Fresh Data & Retrain Models"):
            with st.spinner("Re-running ETL Pipeline..."): execute_pipeline()
            st.rerun()
