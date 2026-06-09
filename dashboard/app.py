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
st.set_page_config(page_title="Data Pipeline Dashboard", layout="wide")

# --- Initialize Session States ---
if 'pipeline_executed' not in st.session_state:
    st.session_state.pipeline_executed = False
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
if 'right_panel_view' not in st.session_state:
    st.session_state.right_panel_view = "about" 

# --- SYSTEM STYLING & CUSTOM USER INTERFACE TUNING ---
st.markdown("""
    <style>
    .stApp { background-color: #0b1622; color: #f0f4f8; }
    h1, h2, h3, h4, p, label { color: #f0f4f8 !important; font-family: 'Segoe UI', sans-serif; }
    
    /* Green Action Buttons */
    .stButton>button {
        background-color: #2e7d32 !important; 
        color: white !important; 
        font-size: 16px !important; 
        font-weight: bold !important; 
        padding: 15px !important; 
        border-radius: 4px !important;
        border: 1px solid #4caf50 !important;
        width: 100% !important;
        height: 60px !important;
        transition: 0.3s;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover { background-color: #1b5e20 !important; border-color: #81c784 !important; }
    
    /* Viewport UI Adjustments */
    button[data-baseweb="tab"] { height: 60px !important; }
    button[data-baseweb="tab"] p { font-size: 20px !important; font-weight: bold !important; color: #a0b4c7 !important; letter-spacing: 1px; }
    button[data-baseweb="tab"][aria-selected="true"] p { color: #4caf50 !important; border-bottom: 3px solid #4caf50; }
    
    /* Main Flowchart Styling */
    .flow-container { display: flex; flex-direction: column; gap: 12px; background-color: #132235; padding: 20px; border-radius: 8px; border: 1px solid #1e3a5f; }
    .flow-box { display: flex; align-items: center; background: #1a2a40; border-left: 6px solid #3a7bd5; border-radius: 4px; padding: 15px 20px; gap: 15px; }
    .flow-title { font-size: 16px; font-weight: bold; color: #f0f4f8; margin-bottom: 4px; }
    .flow-subtitle { font-size: 12px; color: #a0b4c7; }
    .flow-details { text-align: right; font-size: 12px; color: #a0b4c7; margin-left: auto; line-height: 1.4; }
    
    [data-testid="stMetric"] { background-color: #1a2a40; border-left: 5px solid #4caf50; padding: 15px; border-radius: 4px; }
    .signal-box { padding: 18px; border-radius: 4px; margin-bottom: 20px; font-weight: bold; font-size: 16px; text-align: center; letter-spacing: 1px; border: 1px solid rgba(255,255,255,0.2); }
    .timestamp-badge { background-color: #263238; color: #4caf50 !important; font-family: monospace; padding: 4px 8px; border-radius: 2px; font-size: 11px; display: inline-block; border: 1px solid #4caf50; }
    
    /* Diagram Blueprint Styling */
    .diagram-card {
        background-color: #1a2a40; border: 1px solid #3a7bd5; border-radius: 6px; padding: 15px; margin-bottom: 15px;
        position: relative;
    }
    .diagram-arrow {
        text-align: center; color: #3a7bd5; font-size: 24px; font-weight: bold; margin: -5px 0 10px 0;
    }
    .diagram-header { color: #4caf50; font-size: 15px; font-weight: bold; margin-bottom: 5px; text-transform: uppercase;}
    .diagram-text { color: #a0b4c7; font-size: 13px; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

# --- SYSTEM UTILITIES ---
def get_file_info(folder, extension):
    if not os.path.exists(folder): return None, "NO DATA"
    files = glob.glob(f"{folder}/*{extension}")
    if not files: return None, "NO DATA"
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

# --- POLLING TIMESTAMPS ---
_, bronze_ts = get_file_info('data/bronze', '.json')
_, silver_ts = get_file_info('data/silver', '.parquet')
gold_ts = "NO DATA"
try:
    conn = sqlite3.connect('data/crypto_warehouse.db')
    time_df = pd.read_sql("SELECT max(ingested_at) as mx FROM gold_crypto_prices", conn)
    if not time_df.empty and time_df['mx'].iloc[0]: gold_ts = time_df['mx'].iloc[0]
    conn.close()
except Exception: pass
sys_time = st.session_state.last_refresh_time.split(' ')[1] if ' ' in st.session_state.last_refresh_time else 'READY'
bronze_short = bronze_ts.split(' ')[1] if ' ' in bronze_ts else 'WAITING'
silver_short = silver_ts.split(' ')[1] if ' ' in silver_ts else 'WAITING'
gold_short = gold_ts.split(' ')[1] if ' ' in gold_ts else 'WAITING'

# ==============================================================================
# MAIN LAYOUT
# ==============================================================================
col_viewport, col_controls = st.columns([2.8, 1.2])

# ------------------------------------------------------------------------------
# RIGHT PANEL: CONTROL CENTER
# ------------------------------------------------------------------------------
with col_controls:
    st.markdown("<br>", unsafe_allow_html=True) 
    
    # CONTROL BUTTONS
    if st.button("ABOUT PROJECT"):
        st.session_state.right_panel_view = "about"
        
    if not st.session_state.pipeline_executed:
        if st.button("EXECUTE PIPELINE"):
            with st.spinner("Running Data Pipeline..."):
                time.sleep(1)
                execute_pipeline()
            st.rerun()
    else:
        if st.button("BACK TO HOME"):
            st.session_state.pipeline_executed = False
            st.rerun()
            
    st.markdown("---")

    # DYNAMIC CONTENT VIEWER (DIAGRAM BLUEPRINT)
    if st.session_state.right_panel_view == "about":
        st.markdown("### HOW THIS WORKS")
        
        st.markdown(f"""
        <div class="diagram-card" style="border-left: 5px solid #4caf50;">
            <div class="diagram-header">1. Extract (APIs)</div>
            <div class="diagram-text">Downloads live Crypto prices (CoinCap) and the Stock Market Index (Yahoo Finance).</div>
        </div>
        <div class="diagram-arrow">↓</div>
        
        <div class="diagram-card" style="border-left: 5px solid #cd7f32;">
            <div class="diagram-header">2. Bronze Layer (Raw Storage)</div>
            <div class="diagram-text">Saves the raw JSON data directly to a folder. This is a secure backup that acts as our "Data Lake".</div>
        </div>
        <div class="diagram-arrow">↓</div>
        
        <div class="diagram-card" style="border-left: 5px solid #c0c0c0;">
            <div class="diagram-header">3. Silver Layer (Clean Data)</div>
            <div class="diagram-text">Uses Python Pandas to clean the text, remove empty fields, and compress the file into Parquet format to save space.</div>
        </div>
        <div class="diagram-arrow">↓</div>
        
        <div class="diagram-card" style="border-left: 5px solid #ffd700;">
            <div class="diagram-header">4. Gold Layer (Database)</div>
            <div class="diagram-text">Loads the clean data into an SQLite Database and adds a timestamp so we can track price changes over time.</div>
        </div>
        <div class="diagram-arrow">↓</div>
        
        <div class="diagram-card" style="border-left: 5px solid #9c27b0;">
            <div class="diagram-header">5. Analytics & Predictions</div>
            <div class="diagram-text">Displays the data on this dashboard and uses a Machine Learning model to predict where the price might go next.</div>
        </div>
        """, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# LEFT PANEL: MAIN DASHBOARD VIEWPORT
# ------------------------------------------------------------------------------
with col_viewport:
    st.markdown("<h1 style='margin-top: 0px;'>DATA PIPELINE DASHBOARD</h1>", unsafe_allow_html=True)
    
    if not st.session_state.pipeline_executed:
        st.markdown("### ARCHITECTURE OVERVIEW")
        st.markdown("<p style='color: #a0b4c7; font-size: 15px;'>This diagram shows the step-by-step journey of our data. Click 'Execute Pipeline' to run the code and see the live results.</p>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="flow-container">
            <div class="flow-box">
                <div>
                    <div class="flow-title">1. Fetch Live Data</div>
                    <div class="flow-subtitle">Downloads Crypto & Stock Market Prices</div>
                </div>
                <div class="flow-details"><span class="timestamp-badge">STATUS: {sys_time}</span></div>
            </div>
            <div class="flow-box">
                <div>
                    <div class="flow-title">2. Save Raw Backup (Bronze Layer)</div>
                    <div class="flow-subtitle">Stores exact copies of downloaded files</div>
                </div>
                <div class="flow-details"><span class="timestamp-badge">SAVED: {bronze_short}</span></div>
            </div>
            <div class="flow-box">
                <div>
                    <div class="flow-title">3. Clean & Compress (Silver Layer)</div>
                    <div class="flow-subtitle">Formats text to numbers and compresses file size</div>
                </div>
                <div class="flow-details"><span class="timestamp-badge">CLEANED: {silver_short}</span></div>
            </div>
            <div class="flow-box">
                <div>
                    <div class="flow-title">4. Load into Database (Gold Layer)</div>
                    <div class="flow-subtitle">Saves to a database for easy reading</div>
                </div>
                <div class="flow-details"><span class="timestamp-badge">LOADED: {gold_short}</span></div>
            </div>
            <div class="flow-box">
                <div>
                    <div class="flow-title">5. Show Dashboard & Predict Prices</div>
                    <div class="flow-subtitle">Builds charts and runs a forecasting model</div>
                </div>
                <div class="flow-details"><span class="timestamp-badge">DONE: {sys_time}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Load Operational Data
        conn = sqlite3.connect('data/crypto_warehouse.db')
        df = pd.read_sql("SELECT * FROM gold_crypto_prices ORDER BY ingested_at ASC", conn)
        conn.close()
        latest_time = df['ingested_at'].max()
        latest_df = df[df['ingested_at'] == latest_time]

        tab1, tab2 = st.tabs(["DATA FILES (ETL STATE)", "CHARTS & PREDICTIONS"])

        # --- TAB 1: DATA LINEAGE ---
        with tab1:
            st.markdown(f"### FILE SIZES <span style='font-size:14px;' class='timestamp-badge'>LAST RUN: {st.session_state.last_refresh_time}</span>", unsafe_allow_html=True)
            
            b_size, s_size, savings = calculate_de_metrics()
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1: st.metric("Raw Bronze File Size", f"{b_size} Bytes")
            with col_m2: st.metric("Clean Silver File Size", f"{s_size} Bytes")
            with col_m3: st.metric("Storage Space Saved", f"{savings:.1f}%")

            st.markdown("---")
            col_b, col_s, col_g = st.columns(3)
            with col_b:
                st.markdown(f"#### BRONZE DATA (Raw)", unsafe_allow_html=True)
                bronze_file, _ = get_file_info('data/bronze', '.json')
                if bronze_file:
                    with open(bronze_file, 'r') as f: st.json(json.load(f))
            with col_s:
                st.markdown(f"#### SILVER DATA (Clean)", unsafe_allow_html=True)
                silver_file, _ = get_file_info('data/silver', '.parquet')
                if silver_file: st.dataframe(pd.read_parquet(silver_file), hide_index=True)
            with col_g:
                st.markdown(f"#### GOLD DATA (Database)", unsafe_allow_html=True)
                st.dataframe(latest_df[['symbol', 'priceUsd', 'ingested_at']], hide_index=True)

        # --- TAB 2: ANALYTICS & AI ---
        with tab2:
            st.markdown("### MARKET TRENDS AND PREDICTIONS")
            
            clean_df = df.drop_duplicates(subset=['ingested_at', 'symbol'])
            pivot_df = clean_df.pivot(index='ingested_at', columns='symbol', values='priceUsd')
            
            correlation_msg = "Waiting for more data to find a trend..."
            if 'BTC' in pivot_df.columns and 'S&P500' in pivot_df.columns and len(pivot_df) > 1:
                corr_value = pivot_df['BTC'].corr(pivot_df['S&P500'])
                if pd.isna(corr_value): correlation_msg = "Need more price changes. Run the pipeline again."
                elif corr_value > 0.4: correlation_msg = "Positive Trend: Crypto and Stock Market are moving up together."
                elif corr_value < -0.4: correlation_msg = "Negative Trend: Crypto is moving opposite to the Stock Market."
                else: correlation_msg = "Neutral: Crypto and Stocks are moving independently."

            ml_prediction_msg = "Waiting for more data to predict..."
            trend_signal, signal_color = "WAITING FOR DATA", "#FFA500" 
            
            btc_history = df[df['symbol'] == 'BTC'].sort_values('ingested_at')
            if len(btc_history) >= 2:
                X, y = np.array(range(len(btc_history))).reshape(-1, 1), btc_history['priceUsd'].values
                ml_model = LinearRegression().fit(X, y)
                predicted_price = ml_model.predict(np.array([[len(btc_history)]]))[0]
                
                if predicted_price > y[-1]:
                    trend_signal, signal_color = "UPWARD TREND PREDICTED", "#2E7D32" 
                else:
                    trend_signal, signal_color = "DOWNWARD TREND PREDICTED", "#C62828" 
                ml_prediction_msg = f"Machine Learning expects the next price to be around: ${predicted_price:,.2f}."

            st.markdown(f'<div class="signal-box" style="background-color: {signal_color};">PREDICTION: {trend_signal}</div>', unsafe_allow_html=True)
            st.info(f"QUICK SUMMARY:\n\nMarket Correlation: {correlation_msg}\n\nPrice Forecast: {ml_prediction_msg}")
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown("#### Crypto Prices")
                crypto_cols = [c for c in pivot_df.columns if c != 'S&P500']
                if crypto_cols: st.line_chart(pivot_df[crypto_cols].apply(pd.to_numeric))
            with col_c2:
                st.markdown("#### Stock Market (S&P 500)")
                if 'S&P500' in pivot_df.columns:
                    sp_data = pivot_df[['S&P500']].apply(pd.to_numeric)
                    if len(sp_data) == 1: st.dataframe(sp_data, use_container_width=True)
                    else: st.line_chart(sp_data)

            st.markdown("---")
            st.markdown("#### CURRENT PRICES")
            cols = st.columns(len(latest_df))
            for index, row in latest_df.reset_index().iterrows():
                with cols[index]:
                    if row['symbol'] == 'S&P500': st.metric(label="S&P 500 (Stock Market)", value=f"{float(row['priceUsd']):,.2f} PTS")
                    else: st.metric(label=f"{row['symbol']} (Crypto)", value=f"${float(row['priceUsd']):,.2f}")
