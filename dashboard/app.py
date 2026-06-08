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
st.set_page_config(page_title="Enterprise Intelligence Engine", layout="wide")

# --- Initialize Session States ---
if 'pipeline_executed' not in st.session_state:
    st.session_state.pipeline_executed = False
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
if 'right_panel_view' not in st.session_state:
    st.session_state.right_panel_view = "chat" 
if 'chat_response' not in st.session_state:
    st.session_state.chat_response = "Welcome to the Pipeline Control Center. Select a predefined query below or type your own question regarding the architecture, machine learning models, or data processing."
if 'chat_input_val' not in st.session_state:
    st.session_state.chat_input_val = ""

# --- SYSTEM STYLING & CUSTOM USER INTERFACE TUNING ---
st.markdown("""
    <style>
    .stApp { background-color: #0b1622; color: #f0f4f8; }
    h1, h2, h3, h4, p, label { color: #f0f4f8 !important; font-family: 'Segoe UI', sans-serif; }
    
    /* Identical, massive, equal-sized Green Buttons for the Right Panel */
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
    
    /* Chat Query Buttons - Secondary Style */
    div[data-testid="stVerticalBlock"] div.stButton>button.chat-query-btn {
        height: 40px !important; font-size: 13px !important; background-color: #1a2a40 !important;
        border: 1px solid #3a7bd5 !important; border-radius: 4px !important; color: #a0b4c7 !important;
        text-transform: none; font-weight: normal !important; letter-spacing: 0px;
    }
    div[data-testid="stVerticalBlock"] div.stButton>button.chat-query-btn:hover { background-color: #3a7bd5 !important; color: white !important; }
    
    /* Viewport UI Adjustments */
    button[data-baseweb="tab"] { height: 60px !important; }
    button[data-baseweb="tab"] p { font-size: 20px !important; font-weight: bold !important; color: #a0b4c7 !important; letter-spacing: 1px; }
    button[data-baseweb="tab"][aria-selected="true"] p { color: #4caf50 !important; border-bottom: 3px solid #4caf50; }
    
    .flow-container { display: flex; flex-direction: column; gap: 12px; background-color: #132235; padding: 20px; border-radius: 8px; border: 1px solid #1e3a5f; }
    .flow-box { display: flex; align-items: center; background: #1a2a40; border-left: 6px solid #3a7bd5; border-radius: 4px; padding: 15px 20px; gap: 15px; }
    .flow-title { font-size: 16px; font-weight: bold; color: #f0f4f8; margin-bottom: 4px; }
    .flow-subtitle { font-size: 12px; color: #a0b4c7; }
    .flow-details { text-align: right; font-size: 12px; color: #a0b4c7; margin-left: auto; line-height: 1.4; }
    
    [data-testid="stMetric"] { background-color: #1a2a40; border-left: 5px solid #4caf50; padding: 15px; border-radius: 4px; }
    .signal-box { padding: 18px; border-radius: 4px; margin-bottom: 20px; font-weight: bold; font-size: 16px; text-align: center; letter-spacing: 1px; border: 1px solid rgba(255,255,255,0.2); }
    .timestamp-badge { background-color: #263238; color: #4caf50 !important; font-family: monospace; padding: 4px 8px; border-radius: 2px; font-size: 11px; display: inline-block; border: 1px solid #4caf50; }
    
    .blueprint-header { color: #4caf50 !important; font-size: 14px; font-weight: bold; margin-top: 20px; border-bottom: 1px solid rgba(255,255,255,0.15); padding-bottom: 4px; letter-spacing: 1px; text-transform: uppercase; }
    .blueprint-text { color: #a0b4c7 !important; font-size: 14px; line-height: 1.7; }
    .ai-response-box { background-color: #1a2a40; border-left: 4px solid #3a7bd5; padding: 20px; border-radius: 4px; color: #f0f4f8; font-size: 14px; line-height: 1.6; min-height: 150px; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# --- SYSTEM UTILITIES ---
def get_file_info(folder, extension):
    if not os.path.exists(folder): return None, "NO ACTIVE LOG"
    files = glob.glob(f"{folder}/*{extension}")
    if not files: return None, "NO ACTIVE LOG"
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

# --- STATELESS AI CHAT ENGINE ---
def advanced_ai_engine(query):
    q = query.lower().strip()
    weights = {
        "medallion": ["medallion", "architecture", "layer", "bronze", "silver", "gold", "design"],
        "bronze": ["bronze", "raw", "json", "ingest", "coincap", "immutable", "extraction"],
        "silver": ["silver", "parquet", "pyarrow", "clean", "transform", "compression", "pandas"],
        "gold": ["gold", "warehouse", "sqlite", "relational", "sql", "tables", "load"],
        "ml": ["ml", "machine learning", "predict", "regression", "scikit-learn", "forecast", "ols"],
        "macro": ["macro", "s&p500", "s&p", "correlation", "stock", "yfinance", "pearson"],
        "pipeline": ["orchestration", "refresh", "automate", "pipeline", "execution", "sync"]
    }
    scores = {k: sum(1 for word in v if word in q) for k, v in weights.items()}
    max_intent = max(scores, key=scores.get)
    
    if scores[max_intent] == 0:
        if any(g in q for g in ["hi", "hello", "help", "who"]): return "System Initialized. I am the embedded Data Architecture AI context engine. Select a predefined query or ask me technical details regarding the Bronze, Silver, Gold data layers, or the predictive Machine Learning integration."
        return "QUERY OUT OF BOUNDS: To safeguard precision guidelines, I only process queries regarding this project's Data Engineering architecture, Machine Learning models, or Macroeconomic data processing integrations."

    responses = {
        "medallion": "MEDALLION ARCHITECTURE: This system processes data through logical validation tiers. The Bronze layer serves as the immutable landing zone. The Silver layer handles schema enforcement and PyArrow Parquet compression. The Gold layer aggregates the refined data into an ACID-compliant SQLite warehouse for downstream analytics.",
        "bronze": "BRONZE LAYER (EXTRACTION): Operates as a fault-tolerant landing zone. The Python extraction script executes HTTP GET requests against the CoinCap and Yahoo Finance APIs, saving the raw payload responses as JSON files in the local data/bronze directory to guarantee absolute data lineage and replayability.",
        "silver": "SILVER LAYER (TRANSFORMATION): Reads the Bronze JSON files via Pandas, normalizes data types, casts strings to floats, and handles missing observations. The structured dataframe is then serialized using PyArrow into columnar Parquet files, achieving significant disk space compression and faster read I/O.",
        "gold": "GOLD WAREHOUSE (LOAD): The analytical layer maps the compressed Silver records into an embedded SQLite database (crypto_warehouse.db). It enforces a strict star schema and appends an 'ingested_at' timestamp to every transaction, enabling historical time-series analytics.",
        "ml": "MACHINE LEARNING CORE: Built upon the Scikit-Learn framework. It utilizes a Linear Regression (Ordinary Least Squares) algorithm to read historical price matrices from the Gold warehouse. By evaluating historical trajectories, it calculates velocity vectors to forecast the subsequent asset price movement.",
        "macro": "MACROECONOMIC TRACKING: Integrates the S&P 500 Index via the yfinance library. The system computes the Pearson Correlation Coefficient between digital assets and the S&P 500 to mathematically determine if cryptocurrencies act as independent alternative instruments or parallel legacy equities.",
        "pipeline": "PIPELINE ORCHESTRATION: Execution sequences run linearly: Extraction to Transformation to Loading. The Streamlit session-state interface provides manual execution triggers and background scheduler capabilities to simulate an automated production cron job."
    }
    return responses[max_intent]

def process_chat(query):
    if query:
        st.session_state.chat_response = advanced_ai_engine(query)

# --- POLLING TIMESTAMPS ---
_, bronze_ts = get_file_info('data/bronze', '.json')
_, silver_ts = get_file_info('data/silver', '.parquet')
gold_ts = "NO ACTIVE COMMIT"
try:
    conn = sqlite3.connect('data/crypto_warehouse.db')
    time_df = pd.read_sql("SELECT max(ingested_at) as mx FROM gold_crypto_prices", conn)
    if not time_df.empty and time_df['mx'].iloc[0]: gold_ts = time_df['mx'].iloc[0]
    conn.close()
except Exception: pass
sys_time = st.session_state.last_refresh_time.split(' ')[1] if ' ' in st.session_state.last_refresh_time else 'ACTIVE'
bronze_short = bronze_ts.split(' ')[1] if ' ' in bronze_ts else 'WAITING'
silver_short = silver_ts.split(' ')[1] if ' ' in silver_ts else 'WAITING'
gold_short = gold_ts.split(' ')[1] if ' ' in gold_ts else 'WAITING'

# ==============================================================================
# MAIN ASYMMETRIC LAYOUT
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
        
    if st.button("AI CHATBOT"):
        st.session_state.right_panel_view = "chat"
        
    if not st.session_state.pipeline_executed:
        if st.button("EXECUTE PIPELINE"):
            with st.spinner("Compiling ETL pipelines and initializing ML parameters..."):
                time.sleep(1)
                execute_pipeline()
            st.rerun()
    else:
        if st.button("BACK TO BLUEPRINT"):
            st.session_state.pipeline_executed = False
            st.rerun()
            
    st.markdown("---")

    # DYNAMIC CONTENT VIEWER
    if st.session_state.right_panel_view == "about":
        st.markdown("### PROJECT BLUEPRINT")
        
        st.markdown(f"""
        <div class="blueprint-text">
        This enterprise application demonstrates a complete end-to-end Lakehouse Architecture utilizing the Medallion design pattern. The platform merges live financial data streams with predictive machine learning algorithms.
        
        <div class="blueprint-header">INGESTION MECHANICS (EXTRACT)</div>
        • <b>CoinCap API (v2)</b>: Streaming cryptocurrency ticker payload arrays via REST requests with fault-tolerant try/except blocks.<br>
        • <b>Yahoo Finance Data</b>: Extraction of macro equity reference coordinates (S&P 500 Index) using the Python yfinance package.
        
        <div class="blueprint-header">BRONZE LAKE (RAW STORAGE)</div>
        • Implements an immutable storage layer landing unstructured JSON objects directly to local disk.<br>
        • Ensures full lineage preservation and provides deterministic dataset rebuild capabilities in the event of downstream corruption.
        
        <div class="blueprint-header">SILVER LAYER (TRANSFORMATION)</div>
        • Data normalized into tabular formats using Pandas.<br>
        • Applies strict schema mapping, clears null values, and converts text-based numeric fields into computational floats.<br>
        • Serialized as optimized columnar Parquet objects via the <b>PyArrow Engine</b> with Snappy compression, accelerating I/O bounds and reducing storage bloat.
        
        <div class="blueprint-header">GOLD WAREHOUSE (LOAD)</div>
        • Maps refined data to an <b>SQLite Star-Schema Database</b>.<br>
        • Appends records with strict 'ingested_at' timestamps for robust time-series aggregation and business intelligence reporting.
        
        <div class="blueprint-header">MACHINE LEARNING CORE</div>
        • Triggers a <b>Scikit-Learn OLS (Ordinary Least Squares) Regression</b> locally.<br>
        • Trains dynamically on historical time-series data to output target pricing vectors, forecasting the subsequent interval's trajectory.
        
        <div class="blueprint-header">MACRO CORRELATION ENGINE</div>
        • Calculates the Pearson Correlation Coefficient between digital assets and traditional equities to identify market hedging or decoupling behaviors.
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.right_panel_view == "chat":
        st.markdown("### AI ASSISTANT")
        
        # Display the stateless response
        st.markdown(f'<div class="ai-response-box">SYSTEM OUTPUT:<br><br>{st.session_state.chat_response}</div>', unsafe_allow_html=True)
        
        st.markdown("#### QUERY MATRIX")
        # Grid of preset questions
        q1, q2 = st.columns(2)
        with q1:
            if st.button("Medallion Architecture", key="q1"):
                process_chat("Explain Medallion Architecture")
                st.rerun()
            if st.button("Silver Layer Compression", key="q3"):
                process_chat("How does the Silver layer use Parquet?")
                st.rerun()
            if st.button("Machine Learning Model", key="q5"):
                process_chat("How does the ML regression work?")
                st.rerun()
        with q2:
            if st.button("Bronze Layer Extraction", key="q2"):
                process_chat("Explain the Bronze layer")
                st.rerun()
            if st.button("Gold Database Schema", key="q4"):
                process_chat("Explain the Gold layer SQLite warehouse")
                st.rerun()
            if st.button("Macro Correlation Math", key="q6"):
                process_chat("Explain Pearson Macro Correlation")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        user_input = st.text_input("CUSTOM QUERY INPUT:", key="custom_chat_input")
        if st.button("SUBMIT QUERY"):
            process_chat(user_input)
            st.rerun()

# ------------------------------------------------------------------------------
# LEFT PANEL: LIVE TELEMETRY VIEWPORT
# ------------------------------------------------------------------------------
with col_viewport:
    st.markdown("<h1 style='margin-top: 0px;'>ENTERPRISE INTELLIGENCE ENGINE</h1>", unsafe_allow_html=True)
    
    if not st.session_state.pipeline_executed:
        st.markdown("### PIPELINE TOPOGRAPHY MAP AND INFRASTRUCTURE LOGS")
        st.markdown("<p style='color: #a0b4c7; font-size: 15px;'>The architecture below outlines the exact lifecycle of data through the Medallion framework. Raw data is extracted from network APIs, stored securely in the Bronze layer, transformed and compressed in the Silver layer, and loaded into a relational Gold warehouse. Finally, it is served to the UI for correlation analytics and machine learning processing.</p>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="flow-container">
            <div class="flow-box">
                <div>
                    <div class="flow-title">STEP 1: DYNAMIC NETWORK INGESTION LAYER</div>
                    <div class="flow-subtitle">CoinCap HTTP API / Yahoo Finance Stream Processing Engines</div>
                </div>
                <div class="flow-details"><span class="timestamp-badge">NETWORK STATUS: {sys_time}</span></div>
            </div>
            <div class="flow-box">
                <div>
                    <div class="flow-title">STEP 2: IMMUTABLE BRONZE DATA LAKE TIER</div>
                    <div class="flow-subtitle">Raw Payload Ingestion / Fault Tolerant Logging Archive</div>
                </div>
                <div class="flow-details"><span class="timestamp-badge">LANDED: {bronze_short}</span></div>
            </div>
            <div class="flow-box">
                <div>
                    <div class="flow-title">STEP 3: CLEANSED SILVER OPTIMIZATION ARRAY</div>
                    <div class="flow-subtitle">PyArrow Engine Mapping / Snappy Columnar Parquet Generation</div>
                </div>
                <div class="flow-details"><span class="timestamp-badge">PARSED: {silver_short}</span></div>
            </div>
            <div class="flow-box">
                <div>
                    <div class="flow-title">STEP 4: RELATIONAL GOLD ENTERPRISE WAREHOUSE</div>
                    <div class="flow-subtitle">ACID Relational Storage / Historical Time-Series Indexing</div>
                </div>
                <div class="flow-details"><span class="timestamp-badge">COMMITTED: {gold_short}</span></div>
            </div>
            <div class="flow-box">
                <div>
                    <div class="flow-title">STEP 5: MULTI-AXIS SERVING OPTIMIZATION UI</div>
                    <div class="flow-subtitle">Pearson Matrix Correlation Math Module / Streamlit Visualizer</div>
                </div>
                <div class="flow-details"><span class="timestamp-badge">SYNCHRONIZED: {sys_time}</span></div>
            </div>
            <div class="flow-box">
                <div>
                    <div class="flow-title">STEP 6: LOCAL MACHINE LEARNING PREDICTIVE CORE</div>
                    <div class="flow-subtitle">Scikit-Learn Mathematical Linear Trajectory Processing</div>
                </div>
                <div class="flow-details"><span class="timestamp-badge">RETRAINED: {sys_time}</span></div>
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

        tab1, tab2 = st.tabs(["PIPELINE INFRASTRUCTURE STATE", "ADVANCED ANALYTICS AND ML INFERENCE"])

        # --- TAB 1: DATA LINEAGE ---
        with tab1:
            st.markdown(f"### SCHEMA OBSERVER <span style='font-size:14px;' class='timestamp-badge'>REFRESHED: {st.session_state.last_refresh_time}</span>", unsafe_allow_html=True)
            
            b_size, s_size, savings = calculate_de_metrics()
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1: st.metric("RAW BRONZE JSON SIZE", f"{b_size} Bytes")
            with col_m2: st.metric("COMPRESSED SILVER PARQUET", f"{s_size} Bytes")
            with col_m3: st.metric("STORAGE OPTIMIZATION RATIO", f"{savings:.1f}% Savings", delta=f"{savings:.1f}% Efficiency")

            st.markdown("---")
            col_b, col_s, col_g = st.columns(3)
            with col_b:
                st.markdown(f"#### BRONZE LAKE DATA", unsafe_allow_html=True)
                bronze_file, _ = get_file_info('data/bronze', '.json')
                if bronze_file:
                    with open(bronze_file, 'r') as f: st.json(json.load(f))
            with col_s:
                st.markdown(f"#### SILVER PARQUET DATA", unsafe_allow_html=True)
                silver_file, _ = get_file_info('data/silver', '.parquet')
                if silver_file: st.dataframe(pd.read_parquet(silver_file), hide_index=True)
            with col_g:
                st.markdown(f"#### GOLD SQLITE DATABASE", unsafe_allow_html=True)
                st.dataframe(latest_df[['symbol', 'priceUsd', 'ingested_at']], hide_index=True)

        # --- TAB 2: ANALYTICS & AI ---
        with tab2:
            st.markdown("### AI ANALYTICS AND MACRO CORRELATION")
            
            clean_df = df.drop_duplicates(subset=['ingested_at', 'symbol'])
            pivot_df = clean_df.pivot(index='ingested_at', columns='symbol', values='priceUsd')
            
            correlation_msg = "Awaiting historical data tracking parameters..."
            if 'BTC' in pivot_df.columns and 'S&P500' in pivot_df.columns and len(pivot_df) > 1:
                corr_value = pivot_df['BTC'].corr(pivot_df['S&P500'])
                if pd.isna(corr_value): correlation_msg = "Insufficient variance detected. Execute refresh loop to generate time-series matrices."
                elif corr_value > 0.4: correlation_msg = f"Strong Positive Correlation ({corr_value:.2f}). Cryptocurrencies and Equities are advancing symmetrically."
                elif corr_value < -0.4: correlation_msg = f"Inverse Tracking Asset ({corr_value:.2f}). Bitcoin is acting as a systematic market hedge."
                else: correlation_msg = f"Neutral Decoupling ({corr_value:.2f}). Digital assets are navigating independently of traditional indices."

            ml_prediction_msg = "Awaiting dataset volume to configure machine learning weights..."
            trend_signal, signal_color = "SYSTEM BALANCED", "#FFA500" 
            
            btc_history = df[df['symbol'] == 'BTC'].sort_values('ingested_at')
            if len(btc_history) >= 2:
                X, y = np.array(range(len(btc_history))).reshape(-1, 1), btc_history['priceUsd'].values
                ml_model = LinearRegression().fit(X, y)
                predicted_price = ml_model.predict(np.array([[len(btc_history)]]))[0]
                
                if predicted_price > y[-1]:
                    trend_signal, signal_color = "BULLISH TRAJECTORY SIGNAL DETECTED", "#2E7D32" 
                else:
                    trend_signal, signal_color = "DEFENSIVE CONSOLIDATION PREDICTED", "#C62828" 
                ml_prediction_msg = f"Scikit-Learn OLS Regression trained successfully on {len(btc_history)} historical records. Next expected target vector: ${predicted_price:,.2f}."

            st.markdown(f'<div class="signal-box" style="background-color: {signal_color};">ML PREDICTIVE SIGNAL: {trend_signal}</div>', unsafe_allow_html=True)
            st.info(f"CORE INFERENCE SUMMARY:\n\nMacro Correlation Matrix: {correlation_msg}\n\nMathematical Modeling Output: {ml_prediction_msg}")
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown("#### CRYPTOCURRENCY PRICING CURVES")
                crypto_cols = [c for c in pivot_df.columns if c != 'S&P500']
                if crypto_cols: st.line_chart(pivot_df[crypto_cols].apply(pd.to_numeric))
            with col_c2:
                st.markdown("#### S&P 500 INDEX BENCHMARK")
                if 'S&P500' in pivot_df.columns:
                    sp_data = pivot_df[['S&P500']].apply(pd.to_numeric)
                    if len(sp_data) == 1: st.dataframe(sp_data, use_container_width=True)
                    else: st.line_chart(sp_data)

            st.markdown("---")
            cols = st.columns(len(latest_df))
            for index, row in latest_df.reset_index().iterrows():
                with cols[index]:
                    if row['symbol'] == 'S&P500': st.metric(label="S&P 500 MACRO BENCHMARK", value=f"{float(row['priceUsd']):,.2f} PTS")
                    else: st.metric(label=f"{row['symbol']} ASSET TARGET", value=f"${float(row['priceUsd']):,.2f}")
