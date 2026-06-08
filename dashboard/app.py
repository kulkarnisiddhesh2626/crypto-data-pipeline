import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import json
import glob
import time
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression

# --- Path Configuration ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.extract_api import extract_crypto_data
from scripts.transform_silver import transform_to_silver
from scripts.load_gold import load_to_gold

# --- Page Configuration ---
st.set_page_config(page_title="Enterprise Intelligence Engine", page_icon="⚙️", layout="wide")

# Initialize Session States
if 'pipeline_executed' not in st.session_state:
    st.session_state.pipeline_executed = False
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# --- SYSTEM STYLING & CUSTOM USER INTERFACE TUNING ---
st.markdown("""
    <style>
    .stApp { background-color: #0b1622; color: #f0f4f8; }
    h1, h2, h3, h4, p, label { color: #f0f4f8 !important; font-family: 'Segoe UI', sans-serif; }
    
    /* MODIFICATION 1: Green background, max text size, centered button behavior */
    .stButton>button {
        background-color: #4caf50 !important; 
        color: white !important; 
        font-size: 24px !important; /* Maximized text size */
        font-weight: bold !important; 
        padding: 16px 32px !important; 
        border-radius: 12px !important;
        border: 2px solid #81c784 !important;
        width: 100% !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #388e3c !important;
        transform: scale(1.02);
    }
    
    /* MODIFICATION 2: Massive, highly visible tab headers at the top */
    button[data-baseweb="tab"] {
        height: 60px !important;
    }
    button[data-baseweb="tab"] p {
        font-size: 26px !important; /* Large and visible headers */
        font-weight: bold !important;
        color: #a0b4c7 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #4caf50 !important; /* Active indicator match */
        border-bottom: 3px solid #4caf50;
    }
    
    /* Flowchart and Metric Styling */
    .flow-container {
        display: flex; flex-wrap: wrap; justify-content: center; align-items: flex-start; gap: 10px;
        background-color: #132235; padding: 30px 10px; border-radius: 16px; border: 1px solid #1e3a5f; margin-bottom: 30px;
    }
    .flow-box { background: #1a2a40; border-top: 5px solid #3a7bd5; border-radius: 8px; padding: 12px; text-align: center; width: 15%; min-width: 140px; }
    .flow-details { text-align: left; font-size: 11px; color: #a0b4c7; margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px; line-height: 1.5; }
    .flow-arrow { color: #3a7bd5; font-size: 20px; font-weight: bold; align-self: center; margin-top: 40px; }
    [data-testid="stMetric"] { background-color: #1a2a40; border-left: 5px solid #4caf50; padding: 15px; border-radius: 8px; }
    .signal-box { padding: 20px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; font-size: 18px; text-align: center; }
    .timestamp-badge { background-color: #263238; color: #00e676 !important; font-family: monospace; padding: 2px 6px; border-radius: 4px; font-size: 10px; display: inline-block; margin-top: 4px;}
    </style>
""", unsafe_allow_html=True)

# Helper function to capture modifications timestamps
def get_file_info(folder, extension):
    if not os.path.exists(folder): return None, "No Data"
    files = glob.glob(f"{folder}/*{extension}")
    if not files: return None, "No Data"
    latest = max(files, key=os.path.getctime)
    mod_time = datetime.fromtimestamp(os.path.getctime(latest)).strftime('%Y-%m-%d %H:%M:%S')
    return latest, mod_time

def calculate_de_metrics():
    b_file, _ = get_file_info('data/bronze', '.json')
    s_file, _ = get_file_info('data/silver', '.parquet')
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
    st.session_state.last_refresh_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Fetch processing metrics and timestamps to achieve real-time streaming feedback
_, bronze_ts = get_file_info('data/bronze', '.json')
_, silver_ts = get_file_info('data/silver', '.parquet')

# Try reading database to harvest gold lineage time stamp
gold_ts = "No Data"
try:
    conn = sqlite3.connect('data/crypto_warehouse.db')
    time_df = pd.read_sql("SELECT max(ingested_at) as mx FROM gold_crypto_prices", conn)
    if not time_df.empty and time_df['mx'].iloc[0]:
        gold_ts = time_df['mx'].iloc[0]
    conn.close()
except Exception:
    pass

sys_time = st.session_state.last_refresh_time.split(' ')[1] if ' ' in st.session_state.last_refresh_time else 'Active'
bronze_short = bronze_ts.split(' ')[1] if ' ' in bronze_ts else 'None'
silver_short = silver_ts.split(' ')[1] if ' ' in silver_ts else 'None'
gold_short = gold_ts.split(' ')[1] if ' ' in gold_ts else 'None'

# --- RESTORED 6-STEP FLOW DIAGRAM WITH LIVE TIMESTAMPS ---
flowchart_html = f"""
<div class="flow-container">
    <div class="flow-box" style="border-color: #4caf50;">
        <div style="font-size:30px;">🌐</div>
        <h4 style="color: #4caf50; font-size:14px; margin-bottom:0;">1. Ingestion</h4>
        <div class="flow-details">• CoinCap (Crypto)<br>• YFinance (Macro)<br><span class="timestamp-badge">🟢 Ping: {sys_time}</span></div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #cd7f32;">
        <div style="font-size:30px;">🥉</div>
        <h4 style="color: #cd7f32; font-size:14px; margin-bottom:0;">2. Bronze</h4>
        <div class="flow-details">• Raw JSON<br>• Lineage Backup<br><span class="timestamp-badge">📝 Saved: {bronze_short}</span></div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #c0c0c0;">
        <div style="font-size:30px;">🥈</div>
        <h4 style="color: #c0c0c0; font-size:14px; margin-bottom:0;">3. Silver</h4>
        <div class="flow-details">• Clean Schema<br>• Col. Parquet<br><span class="timestamp-badge">⚙️ Cast: {silver_short}</span></div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #ffd700;">
        <div style="font-size:30px;">🥇</div>
        <h4 style="color: #ffd700; font-size:14px; margin-bottom:0;">4. Gold</h4>
        <div class="flow-details">• Relational SQL<br>• Time-Series<br><span class="timestamp-badge">🗄️ Load: {gold_short}</span></div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #9c27b0;">
        <div style="font-size:30px;">📊</div>
        <h4 style="color: #9c27b0; font-size:14px; margin-bottom:0;">5. Serving UI</h4>
        <div class="flow-details">• Math Core<br>• Dual Charts<br><span class="timestamp-badge">🖥️ Sync: {sys_time}</span></div>
    </div>
    <div class="flow-arrow">➔</div>
    <div class="flow-box" style="border-color: #00bcd4;">
        <div style="font-size:30px;">🤖</div>
        <h4 style="color: #00bcd4; font-size:14px; margin-bottom:0;">6. Predictive AI</h4>
        <div class="flow-details">• Scikit-Learn ML<br>• Regression<br><span class="timestamp-badge">🧠 Train: {sys_time}</span></div>
    </div>
</div>
"""

# ==========================================
# SCREEN 1: ARCHITECTURE MAP & LANDING
# ==========================================
if not st.session_state.pipeline_executed:
    st.title("🚀 Enterprise Data Platform & Predictive Intelligence")
    st.markdown("<h4 style='color: #a0b4c7;'>Cross-Asset Macro Integration, Storage Optimization & Scikit-Learn Regression Forecasting</h4>", unsafe_allow_html=True)
    
    # 6-Step Flowchart is back!
    st.markdown(flowchart_html, unsafe_allow_html=True)
    
    st.write("### ")
    
    # MODIFICATION 1: Execute Button centered at bottom
    col_l, col_center, col_r = st.columns([1, 2, 1])
    with col_center:
        if st.button("▶ EXECUTE INTELLIGENCE PIPELINE", use_container_width=True):
            with st.spinner("Running Multi-Source ETL & Tuning ML Models..."):
                time.sleep(1)
                execute_pipeline()
            st.rerun()

# ==========================================
# SCREEN 2: METRICS & ANALYTICS MART
# ==========================================
else:
    # MODIFICATION 4: Refresh logic & Scheduled auto-refresh slider
    with st.sidebar:
        st.header("⚙️ Orchestration Control")
        
        # Manual Trigger Button
        if st.button("🔄 Manual Data Refresh"):
            with st.spinner("Executing pipeline sync..."):
                execute_pipeline()
            st.rerun()
            
        st.markdown("---")
        
        # Scheduled Auto Refresh Toggle Selector
        auto_refresh = st.toggle("⏱️ Enable Scheduled Auto-Refresh")
        refresh_rate = st.selectbox("Interval Cadence", options=[5, 10, 30, 60], format_func=lambda x: f"Every {x} Seconds")
        
        if auto_refresh:
            st.info(f"⏳ Auto-refresh scheduled active: Updating every {refresh_rate}s")
            time.sleep(refresh_rate)
            execute_pipeline()
            st.rerun()

        st.markdown("---")
        conn = sqlite3.connect('data/crypto_warehouse.db')
        row_count = pd.read_sql("SELECT count(*) as count FROM gold_crypto_prices", conn)['count'].iloc[0]
        conn.close()
        st.metric("Total Warehouse Rows", row_count)
        st.caption(f"Last Pipeline Sync Executed at:\n{st.session_state.last_refresh_time}")

    # Main Screen Content Load
    conn = sqlite3.connect('data/crypto_warehouse.db')
    df = pd.read_sql("SELECT * FROM gold_crypto_prices ORDER BY ingested_at ASC", conn)
    conn.close()
    
    latest_time = df['ingested_at'].max()
    latest_df = df[df['ingested_at'] == latest_time]

    # MODIFICATION 2: Massive Headers via Tab names
    tab1, tab2 = st.tabs(["🏗️ Pipeline Infrastructure State", "🧠 Advanced Analytics & ML Inference"])

    # --- TAB 1: THE DATA TRANSFORMATION STATE ---
    with tab1:
        st.markdown(f"### 🔍 Enterprise Multi-Schema Observer <span style='font-size:14px;' class='timestamp-badge'>Last Checked: {st.session_state.last_refresh_time}</span>", unsafe_allow_html=True)
        
        b_size, s_size, savings = calculate_de_metrics()
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Raw Bronze JSON Size", f"{b_size} Bytes", help="Lineage benchmark stamp.")
        with col_m2:
            st.metric("Compressed Silver Parquet", f"{s_size} Bytes", help="Columnar pyarrow array configuration.")
        with col_m3:
            st.metric("Storage Optimization Ratio", f"{savings:.1f}% Savings", delta=f"{savings:.1f}% Compression Efficiency")

        st.markdown("---")
        # MODIFICATION 3: Timestamps for Data Layers
        col_b, col_s, col_g = st.columns(3)
        with col_b:
            st.markdown(f"#### 🥉 Bronze Lake <br><span class='timestamp-badge'>File Update: {bronze_ts}</span>", unsafe_allow_html=True)
            bronze_file, _ = get_file_info('data/bronze', '.json')
            if bronze_file:
                with open(bronze_file, 'r') as f: st.json(json.load(f))
        with col_s:
            st.markdown(f"#### 🥈 Silver Lake <br><span class='timestamp-badge'>File Update: {silver_ts}</span>", unsafe_allow_html=True)
            silver_file, _ = get_file_info('data/silver', '.parquet')
            if silver_file:
                st.dataframe(pd.read_parquet(silver_file), hide_index=True)
        with col_g:
            st.markdown(f"#### 🥇 Gold Warehouse <br><span class='timestamp-badge'>DB Commit: {gold_ts}</span>", unsafe_allow_html=True)
            st.dataframe(latest_df[['symbol', 'priceUsd', 'ingested_at']], hide_index=True)

    # --- TAB 2: AI INSIGHTS, CORRELATION & MACHINE LEARNING ---
    with tab2:
        st.markdown("### 🧠 AI Analytics & Macroeconomic Correlation")
        
        clean_df = df.drop_duplicates(subset=['ingested_at', 'symbol'])
        pivot_df = clean_df.pivot(index='ingested_at', columns='symbol', values='priceUsd')
        
        correlation_msg = "Awaiting structural historical logging coordinates..."
        corr_value = 0.0
        if 'BTC' in pivot_df.columns and 'S&P500' in pivot_df.columns and len(pivot_df) > 1:
            corr_value = pivot_df['BTC'].corr(pivot_df['S&P500'])
            if pd.isna(corr_value):
                correlation_msg = "Identical value coordinates received. Run the update loop again to generate price variance."
            elif corr_value > 0.4:
                correlation_msg = f"Strong Positive Correlation ({corr_value:.2f}). Crypto and Traditional Equities are climbing in tandem."
            elif corr_value < -0.4:
                correlation_msg = f"Strong Negative Correlation ({corr_value:.2f}). Bitcoin acts as a direct inverse market hedge."
            else:
                correlation_msg = f"Neutral Market Decoupling ({corr_value:.2f}). Crypto tokens are navigating independently of stock models."

        # Scikit-Learn ML
        ml_prediction_msg = "Awaiting sufficient database volume logs to configure model weights..."
        trend_signal = "NEUTRAL SYSTEM INERTIA"
        signal_color = "#FFA500" 
        
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
                trend_signal = "ACCELERATING BULLISH SYMMETRY SIGNAL"
                signal_color = "#2E7D32" 
            else:
                trend_signal = "DEFENSIVE CONSOLIDATION PREDICTION"
                signal_color = "#C62828" 
                
            ml_prediction_msg = f"trained an active local **Linear Regression Mathematical Predictive Core** on {len(btc_history)} time-series data records. Expected target pricing trajectory for next sync sequence: **${predicted_price:,.2f}**."

        st.markdown(f'<div class="signal-box" style="background-color: {signal_color};">🤖 LIVE AI SYSTEM DIRECTION: {trend_signal}</div>', unsafe_allow_html=True)
        st.info(f"**💡 Machine Inferences Summary:**\n\n* **Macro Correlation Strategy:** {correlation_msg}\n\n* **Mathematical Modeling Core:** {ml_prediction_msg}")
        
        st.markdown("---")
        st.subheader("📊 Cross-Asset Multi-Axis Tracking Engine")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### Cryptocurrency Pricing Curves (USD)")
            crypto_cols = [c for c in pivot_df.columns if c != 'S&P500']
            if crypto_cols:
                crypto_chart_data = pivot_df[crypto_cols].apply(pd.to_numeric)
                st.line_chart(crypto_chart_data)
        with col_c2:
            st.markdown("#### Macro Equity Benchmarks: S&P 500 Index (Points)")
            
            # MODIFICATION 5: Fixed S&P 500 Blank Bug
            if 'S&P500' in pivot_df.columns:
                sp_chart_data = pivot_df[['S&P500']].apply(pd.to_numeric)
                if len(sp_chart_data) == 1:
                    st.write("##### Baseline Timepoint Initialized:")
                    st.dataframe(sp_chart_data, use_container_width=True)
                else:
                    st.line_chart(sp_chart_data)
            else:
                st.warning("Awaiting S&P 500 telemetry arrays...")

        st.markdown("---")
        st.subheader("⚡ Active Asset KPI Monitors")
        cols = st.columns(len(latest_df))
        for index, row in latest_df.reset_index().iterrows():
            with cols[index]:
                if row['symbol'] == 'S&P500':
                    st.metric(label="🇺🇸 S&P 500 Macro Index", value=f"{float(row['priceUsd']):,.2f} pts")
                else:
                    st.metric(label=f"🪙 {row['symbol']} Asset", value=f"${float(row['priceUsd']):,.2f}")

    st.write("### ")
    st.markdown("---")
    
    # MODIFICATION 1: Back button centered at bottom, styled green
    col_l2, col_center2, col_r2 = st.columns([1, 2, 1])
    with col_center2:
        if st.button("⬅️ BACK TO ARCHITECTURE BLUEPRINT", use_container_width=True):
            st.session_state.pipeline_executed = False
            st.rerun()
