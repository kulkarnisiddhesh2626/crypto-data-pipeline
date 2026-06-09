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
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover { background-color: #1b5e20 !important; border-color: #81c784 !important; }
    
    /* Viewport UI Adjustments */
    button[data-baseweb="tab"] { height: 60px !important; }
    button[data-baseweb="tab"] p { font-size: 18px !important; font-weight: bold !important; color: #a0b4c7 !important; letter-spacing: 1px; }
    button[data-baseweb="tab"][aria-selected="true"] p { color: #4caf50 !important; border-bottom: 3px solid #4caf50; }
    
    [data-testid="stMetric"] { background-color: #1a2a40; border-left: 5px solid #4caf50; padding: 15px; border-radius: 4px; }
    .signal-box { padding: 18px; border-radius: 4px; margin-bottom: 20px; font-weight: bold; font-size: 16px; text-align: center; letter-spacing: 1px; border: 1px solid rgba(255,255,255,0.2); }
    .timestamp-badge { background-color: #263238; color: #4caf50 !important; font-family: monospace; padding: 4px 8px; border-radius: 2px; font-size: 11px; display: inline-block; border: 1px solid #4caf50; margin-top: 10px; }
    
    /* Horizontal Flowchart Diagram Styling */
    .pipeline-flow { 
        display: flex; flex-direction: row; flex-wrap: wrap; justify-content: center; align-items: stretch; 
        gap: 15px; background-color: #132235; padding: 30px; border-radius: 8px; border: 1px solid #1e3a5f; margin-top: 15px;
    }
    .pipeline-step { 
        background-color: #1a2a40; border-top: 5px solid #3a7bd5; border-radius: 6px; padding: 20px; 
        width: 17%; min-width: 180px; text-align: left; box-shadow: 0 4px 10px rgba(0,0,0,0.3); 
    }
    .step-title { font-size: 14px; font-weight: bold; color: #ffffff; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
    .step-desc { font-size: 12px; color: #a0b4c7; line-height: 1.6; }
    .step-arrow { color: #3a7bd5; font-size: 30px; font-weight: bold; align-self: center; }
    
    /* About Project Styling */
    .blueprint-header { color: #4caf50 !important; font-size: 14px; font-weight: bold; margin-top: 20px; border-bottom: 1px solid rgba(255,255,255,0.15); padding-bottom: 4px; letter-spacing: 1px; text-transform: uppercase; }
    .blueprint-text { color: #a0b4c7 !important; font-size: 13px; line-height: 1.6; }
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
sys_time = st.session_state.last_refresh_time

# ==============================================================================
# MAIN LAYOUT
# ==============================================================================
col_viewport, col_controls = st.columns([3.0, 1.0])

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
        if st.button("BACK TO OVERVIEW"):
            st.session_state.pipeline_executed = False
            st.rerun()
            
    st.markdown("---")

    # DYNAMIC CONTENT VIEWER (PROJECT DETAILS)
    if st.session_state.right_panel_view == "about":
        st.markdown("### PROJECT DETAILS")
        
        st.markdown(f"""
        <div class="blueprint-text">
        This platform represents a complete Data Engineering Lakehouse Pipeline, processing raw network streams into machine learning forecasts.
        
        <div class="blueprint-header">DATA INGESTION</div>
        Connects via HTTP REST requests to the CoinCap API for cryptocurrency arrays and the Yahoo Finance API for the S&P 500 macro equity index. Implements strict try/except fault tolerance.
        
        <div class="blueprint-header">BRONZE LAYER (LAKE)</div>
        An immutable local storage zone. Saves the exact JSON payload from the APIs to disk. This guarantees absolute data lineage and allows the pipeline to be rebuilt if downstream errors occur.
        
        <div class="blueprint-header">SILVER LAYER (CLEAN)</div>
        Powered by Python Pandas and PyArrow. It extracts the Bronze JSON, standardizes the schema, casts text fields into numeric floats, and compresses the output into columnar Parquet files to save disk space.
        
        <div class="blueprint-header">GOLD LAYER (DATABASE)</div>
        Maps the refined Parquet data into an SQLite relational database. It enforces a structured table schema and automatically appends execution timestamps for historical tracking.
        
        <div class="blueprint-header">MACHINE LEARNING</div>
        Executes a Scikit-Learn Linear Regression model. It reads the Gold database history, plots the price trajectory matrix, and predicts the target numerical value for the next pipeline execution.
        </div>
        """, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# LEFT PANEL: MAIN DASHBOARD VIEWPORT
# ------------------------------------------------------------------------------
with col_viewport:
    st.markdown("<h1 style='margin-top: 0px;'>DATA PIPELINE DASHBOARD</h1>", unsafe_allow_html=True)
    
    if not st.session_state.pipeline_executed:
        st.markdown("### ARCHITECTURE WORKFLOW")
        st.markdown("<p style='color: #a0b4c7; font-size: 15px;'>The diagram below illustrates the complete end-to-end data lifecycle. Data moves from external network APIs through structured storage layers, ultimately arriving at the analytics and predictive engine. Click Execute Pipeline on the right to trigger this sequence.</p>", unsafe_allow_html=True)
        
        # COMPLETE, DETAILED HORIZONTAL FLOWCHART
        st.markdown(f"""
        <div class="pipeline-flow">
            <div class="pipeline-step" style="border-top-color: #4caf50;">
                <div class="step-title">1. EXTRACT DATA</div>
                <div class="step-desc">Downloads live Crypto pricing and Stock Market indices via network APIs. Includes error handling to ensure continuous uptime.</div>
            </div>
            <div class="step-arrow">➔</div>
            <div class="pipeline-step" style="border-top-color: #cd7f32;">
                <div class="step-title">2. BRONZE LAYER</div>
                <div class="step-desc">Saves the exact raw JSON files directly to a local Data Lake. This preserves a complete historical backup with zero data loss.</div>
            </div>
            <div class="step-arrow">➔</div>
            <div class="pipeline-step" style="border-top-color: #c0c0c0;">
                <div class="step-title">3. SILVER LAYER</div>
                <div class="step-desc">Cleans structural errors, formats text to numbers, and compresses the data into a highly optimized columnar Parquet format.</div>
            </div>
            <div class="step-arrow">➔</div>
            <div class="pipeline-step" style="border-top-color: #ffd700;">
                <div class="step-title">4. GOLD LAYER</div>
                <div class="step-desc">Loads the finalized data into a relational SQLite database. Appends strict timestamps to enable time-series SQL analytics.</div>
            </div>
            <div class="step-arrow">➔</div>
            <div class="pipeline-step" style="border-top-color: #9c27b0;">
                <div class="step-title">5. ANALYTICS & ML</div>
                <div class="step-desc">Queries the database to generate live visual charts and runs a Machine Learning regression model to forecast future prices.</div>
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

        tab1, tab2 = st.tabs(["PIPELINE STORAGE STATE", "MARKET TRENDS AND PREDICTIONS"])

        # --- TAB 1: DATA LINEAGE ---
        with tab1:
            st.markdown(f"### FILE COMPRESSION METRICS", unsafe_allow_html=True)
            st.markdown(f"<span class='timestamp-badge'>LAST PIPELINE EXECUTION: {st.session_state.last_refresh_time}</span>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            b_size, s_size, savings = calculate_de_metrics()
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1: st.metric("RAW BRONZE FILE SIZE", f"{b_size} Bytes")
            with col_m2: st.metric("CLEAN SILVER FILE SIZE", f"{s_size} Bytes")
            with col_m3: st.metric("STORAGE SPACE SAVED", f"{savings:.1f}%")

            st.markdown("---")
            col_b, col_s, col_g = st.columns(3)
            with col_b:
                st.markdown(f"#### BRONZE DATA (RAW JSON)", unsafe_allow_html=True)
                bronze_file, _ = get_file_info('data/bronze', '.json')
                if bronze_file:
                    with open(bronze_file, 'r') as f: st.json(json.load(f))
            with col_s:
                st.markdown(f"#### SILVER DATA (PARQUET)", unsafe_allow_html=True)
                silver_file, _ = get_file_info('data/silver', '.parquet')
                if silver_file: st.dataframe(pd.read_parquet(silver_file), hide_index=True)
            with col_g:
                st.markdown(f"#### GOLD DATA (DATABASE)", unsafe_allow_html=True)
                st.dataframe(latest_df[['symbol', 'priceUsd', 'ingested_at']], hide_index=True)

        # --- TAB 2: ANALYTICS & AI ---
        with tab2:
            st.markdown("### MACHINE LEARNING FORECAST")
            
            clean_df = df.drop_duplicates(subset=['ingested_at', 'symbol'])
            pivot_df = clean_df.pivot(index='ingested_at', columns='symbol', values='priceUsd')
            
            correlation_msg = "Waiting for additional historical data to calculate trends."
            if 'BTC' in pivot_df.columns and 'S&P500' in pivot_df.columns and len(pivot_df) > 1:
                corr_value = pivot_df['BTC'].corr(pivot_df['S&P500'])
                if pd.isna(corr_value): correlation_msg = "Need more price variance. Execute the pipeline again."
                elif corr_value > 0.4: correlation_msg = "Positive Trend: Cryptocurrencies and the Stock Market are moving up together."
                elif corr_value < -0.4: correlation_msg = "Negative Trend: Cryptocurrencies are moving opposite to the Stock Market."
                else: correlation_msg = "Neutral: Cryptocurrencies and the Stock Market are moving independently."

            ml_prediction_msg = "Waiting for additional data points to generate prediction."
            trend_signal, signal_color = "WAITING FOR DATA", "#1e3a5f" 
            
            btc_history = df[df['symbol'] == 'BTC'].sort_values('ingested_at')
            if len(btc_history) >= 2:
                X, y = np.array(range(len(btc_history))).reshape(-1, 1), btc_history['priceUsd'].values
                ml_model = LinearRegression().fit(X, y)
                predicted_price = ml_model.predict(np.array([[len(btc_history)]]))[0]
                
                if predicted_price > y[-1]:
                    trend_signal, signal_color = "UPWARD MARKET TREND PREDICTED", "#2e7d32" 
                else:
                    trend_signal, signal_color = "DOWNWARD MARKET TREND PREDICTED", "#c62828" 
                ml_prediction_msg = f"The Linear Regression model anticipates the next price target to be: ${predicted_price:,.2f}"

            st.markdown(f'<div class="signal-box" style="background-color: {signal_color}; border-color: {signal_color};">{trend_signal}</div>', unsafe_allow_html=True)
            st.info(f"ANALYTICS SUMMARY:\n\nMarket Correlation: {correlation_msg}\n\nPrice Forecast: {ml_prediction_msg}")
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown("#### CRYPTOCURRENCY PRICES")
                crypto_cols = [c for c in pivot_df.columns if c != 'S&P500']
                if crypto_cols: st.line_chart(pivot_df[crypto_cols].apply(pd.to_numeric))
            with col_c2:
                st.markdown("#### STOCK MARKET (S&P 500)")
                if 'S&P500' in pivot_df.columns:
                    sp_data = pivot_df[['S&P500']].apply(pd.to_numeric)
                    if len(sp_data) == 1: st.dataframe(sp_data, use_container_width=True)
                    else: st.line_chart(sp_data)

            st.markdown("---")
            st.markdown("#### LATEST ASSET PRICES")
            cols = st.columns(len(latest_df))
            for index, row in latest_df.reset_index().iterrows():
                with cols[index]:
                    if row['symbol'] == 'S&P500': st.metric(label="S&P 500 INDEX", value=f"{float(row['priceUsd']):,.2f} PTS")
                    else: st.metric(label=f"{row['symbol']} ASSET", value=f"${float(row['priceUsd']):,.2f}")
