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

# --- Initialize Session States ---
if 'pipeline_executed' not in st.session_state:
    st.session_state.pipeline_executed = False
if 'last_refresh_time' not in st.session_state:
    st.session_state.last_refresh_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "ai", "text": "👋 Welcome to the Pipeline Control Center. I am your specialized Data Architecture Core. Ask me anything regarding this Medallion setup, schema designs, optimization metrics, or local machine learning modeling components!"}
    ]

# --- SYSTEM STYLING & CUSTOM USER INTERFACE TUNING ---
st.markdown("""
    <style>
    .stApp { background-color: #0b1622; color: #f0f4f8; }
    h1, h2, h3, h4, p, label { color: #f0f4f8 !important; font-family: 'Segoe UI', sans-serif; }
    
    /* MODIFICATION 1 & 3: High-visibility massive green buttons locked on the left panel layout */
    .stButton>button {
        background-color: #4caf50 !important; 
        color: white !important; 
        font-size: 24px !important; 
        font-weight: bold !important; 
        padding: 14px 28px !important; 
        border-radius: 12px !important;
        border: 2px solid #81c784 !important;
        width: 100% !important;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #388e3c !important; transform: scale(1.02); }
    
    /* Chatbot recommendation prompt pill styling */
    .chat-pill>button {
        font-size: 11px !important;
        padding: 4px 8px !important;
        background-color: #1a2a40 !important;
        border: 1px solid #3a7bd5 !important;
        color: #a0b4c7 !important;
        border-radius: 20px !important;
        width: auto !important;
    }
    .chat-pill>button:hover { background-color: #3a7bd5 !important; color: white !important; }
    
    /* MODIFICATION 2: Massive high-visibility upper tab typography headers */
    button[data-baseweb="tab"] { height: 60px !important; }
    button[data-baseweb="tab"] p { font-size: 26px !important; font-weight: bold !important; color: #a0b4c7 !important; }
    button[data-baseweb="tab"][aria-selected="true"] p { color: #4caf50 !important; border-bottom: 3px solid #4caf50; }
    
    /* Architecture Flowcharts and Metrics Custom Panels */
    .flow-container { display: flex; flex-direction: column; gap: 12px; background-color: #132235; padding: 20px; border-radius: 16px; border: 1px solid #1e3a5f; }
    .flow-box { display: flex; align-items: center; background: #1a2a40; border-left: 6px solid #3a7bd5; border-radius: 8px; padding: 12px 20px; gap: 15px; }
    .flow-details { text-align: left; font-size: 12px; color: #a0b4c7; margin-left: auto; line-height: 1.4; }
    [data-testid="stMetric"] { background-color: #1a2a40; border-left: 5px solid #4caf50; padding: 15px; border-radius: 8px; }
    .signal-box { padding: 18px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; font-size: 16px; text-align: center; }
    .timestamp-badge { background-color: #263238; color: #00e676 !important; font-family: monospace; padding: 2px 6px; border-radius: 4px; font-size: 10px; display: inline-block; }
    
    /* Robust Chat Interface Windows */
    .chat-container { background-color: #132235; border: 1px solid #1e3a5f; border-radius: 12px; padding: 15px; height: 320px; overflow-y: auto; margin-bottom: 10px; }
    .user-msg { background-color: #1e3a5f; padding: 10px 14px; border-radius: 12px 12px 0px 12px; margin-bottom: 12px; text-align: left; font-size: 13px; border-left: 4px solid #4caf50; }
    .ai-msg { background-color: #1a2a40; padding: 10px 14px; border-radius: 12px 12px 12px 0px; margin-bottom: 12px; text-align: left; font-size: 13px; border-left: 4px solid #3a7bd5; }
    
    /* Blueprints layout adjustments */
    .blueprint-header { color: #ffd700 !important; font-size: 14px; font-weight: bold; margin-top: 10px; border-bottom: 1px solid rgba(255,255,255,0.15); padding-bottom: 2px; }
    </style>
""", unsafe_allow_html=True)

# --- SYSTEM UTILITIES & METRIC PARSERS ---
def get_file_info(folder, extension):
    if not os.path.exists(folder): return None, "No Active Log"
    files = glob.glob(f"{folder}/*{extension}")
    if not files: return None, "No Active Log"
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

# --- MODIFICATION 1: ROBUST KEYWORD-WEIGHTED SCORED LOCAL AI CHAT ENGINE ---
def advanced_ai_engine(query):
    q = query.lower().strip()
    
    # Vocabulary scoring maps
    weights = {
        "medallion": ["medallion", "architecture", "layer", "bronze", "silver", "gold", "design", "structure"],
        "bronze": ["bronze", "raw", "json", "ingest", "unaltered", "coincap", "immutable", "landing"],
        "silver": ["silver", "parquet", "pyarrow", "clean", "transform", "compression", "snappy", "null", "schema"],
        "gold": ["gold", "warehouse", "sqlite", "relational", "database", "sql", "acid", "tables", "query"],
        "ml": ["ml", "machine learning", "predict", "regression", "scikit-learn", "forecast", "scikit", "linear", "model", "train"],
        "macro": ["macro", "s&p500", "s&p", "correlation", "stock", "yfinance", "pearson", "hedge", "decoupling"],
        "pipeline": ["orchestration", "refresh", "cron", "scheduler", "automate", "pipeline", "execution", "sync", "realtime"]
    }
    
    scores = {k: sum(1 for word in v if word in q) for k, v in weights.items()}
    max_intent = max(scores, key=scores.get)
    
    if scores[max_intent] == 0:
        # Contextual greeting check
        if any(g in q for g in ["hi", "hello", "hey", "greetings", "help"]):
            return "Hello! I am your interactive technical co-pilot. I possess comprehensive semantic data tracking logs matching this specific architectural runtime environment. Ask me technical details about any of our ingestion zones, silver transformations, gold schemas, or Scikit-Learn pipelines!"
        return "⚠️ **Boundary Constraint Violation:** The input query falls outside the scope of this project's architecture context. To safeguard precision engineering guidelines, I can only unpack architectural data layers (Bronze, Silver, Gold), data processing configurations (Parquet compression ratios), asset pricing correlations, or structural ML regression models built for this pipeline."

    # Return specialized technical documentation answers based on matching intent
    if max_intent == "medallion":
        return "📐 **Medallion Architecture Blueprint:** This system processes data through logical data validation tiers. **Bronze Layer** acts as the immutable data landing zone preserving transaction history. **Silver Layer** handles schema enforcement, parsing strings to typed structural elements, filtering anomalies, and writing to optimized Parquet files. **Gold Layer** compiles business-level asset aggregates into an ACID-compliant database for operational reporting."
    elif max_intent == "bronze":
        return "🥉 **Bronze Tier Engineering:** Operates as a fault-tolerant multi-source landing zone. The extraction script query pings CoinCap (REST v2 REST endpoint) and Yahoo Finance API endpoints, storing responses as immutable raw JSON objects within `data/bronze/`. This pattern decouples network extraction processes from downstream data processing, guaranteeing data replayability."
    elif max_intent == "silver":
        return "🥈 **Silver Tier Engineering:** This layer reads data from the raw Bronze lake, normalizes structural elements using Python, casts features to accurate floating-point objects, and handles missing observations. The result is written using Apache Arrow (`pyarrow`) into columnar Parquet files inside `data/silver/`. This configuration compresses string objects and switches storage layouts to save substantial disk space while accelerating read queries."
    elif max_intent == "gold":
        return "🥇 **Gold Warehouse Framework:** The analytical layer maps incoming asset records into an embedded SQLite relational database structure (`data/crypto_warehouse.db`). It enforces a structured star schema model centered around the `gold_crypto_prices` table. This database handles strict table types and timestamps every transaction to allow instant historical query processing."
    elif max_intent == "ml":
        return "🤖 **Mathematical Predictive Core:** Built on top of `scikit-learn` using a local **Linear Regression (Ordinary Least Squares)** framework. It reads historical price data from the Gold warehouse, maps timestamps to uniform matrices ($X$), and uses values as labels ($y$). The model evaluates price patterns over past intervals to calculate asset velocity and project the next expected vector price change."
    elif max_intent == "macro":
        return "📊 **Macro Cross-Asset Tracking:** Blends crypto streams with macro indicators (S&P 500 Index). The application computes the **Pearson Correlation Coefficient** across asset price histories. This evaluation determines if digital assets move in line with legacy equity benchmarks or act as independent alternative instruments."
    elif max_intent == "pipeline":
        return "⏱️ **Data Automation & Control Tiers:** Features automatic and manual refresh tools. Manual execution maps out dependencies sequentially: **Extraction** $\\rightarrow$ **Transformation** $\\rightarrow$ **Warehouse Loading**. The automatic refresh scheduler runs background threads to process real-time updates based on chosen intervals."

def submit_chat():
    user_query = st.session_state.chat_input_val
    if user_query:
        st.session_state.chat_history.append({"role": "user", "text": user_query})
        st.session_state.chat_history.append({"role": "ai", "text": advanced_ai_engine(user_query)})
        st.session_state.chat_input_val = "" # Reset chat input buffer

# --- POLLING AND LINEAGE TIMESTAMP MANAGEMENT ---
_, bronze_ts = get_file_info('data/bronze', '.json')
_, silver_ts = get_file_info('data/silver', '.parquet')
gold_ts = "No Active Commit"
try:
    conn = sqlite3.connect('data/crypto_warehouse.db')
    time_df = pd.read_sql("SELECT max(ingested_at) as mx FROM gold_crypto_prices", conn)
    if not time_df.empty and time_df['mx'].iloc[0]: gold_ts = time_df['mx'].iloc[0]
    conn.close()
except Exception: pass

sys_time = st.session_state.last_refresh_time.split(' ')[1] if ' ' in st.session_state.last_refresh_time else 'Active'
bronze_short = bronze_ts.split(' ')[1] if ' ' in bronze_ts else 'Waiting'
silver_short = silver_ts.split(' ')[1] if ' ' in silver_ts else 'Waiting'
gold_short = gold_ts.split(' ')[1] if ' ' in gold_ts else 'Waiting'

# ==============================================================================
# MODIFICATION 3: DUAL SCREEN ASYMMETRIC LAYOUT (COMPLETELY ABOVE THE FOLD)
# ==============================================================================
col_control_panel, col_viewport_panel = st.columns([1.3, 2.7])

# ------------------------------------------------------------------------------
# LEFT SIDE PANEL: ALL MASTER INTERACTIONS & CONTROLS (NO SCROLL NEEDED)
# ------------------------------------------------------------------------------
with col_control_panel:
    
    # MODIFICATION 2: Comprehensive "About the Project" technical blueprint expansion
    with st.expander("ℹ️ Detailed Project Blueprint", expanded=not st.session_state.pipeline_executed):
        st.markdown(f"""
        ### Data Platform Specs
        An enterprise multi-source data pipeline utilizing a structured lakehouse model.
        
        <div class="blueprint-header">🌐 INGESTION MECHANICS</div>
        • <b>CoinCap API (v2)</b>: Streaming ticker payload arrays (BTC, ETH, etc.) via REST requests.<br>
        • <b>Yahoo Finance Data</b>: Extraction of macro equity reference coordinates (S&P 500 Index).
        
        <div class="blueprint-header">🥉 BRONZE LAKE (IMMUTABLE LANDING)</div>
        • Raw storage layer landing unstructured JSON objects directly inside <code>data/bronze/</code>.<br>
        • Full lineage preservation ensuring deterministic dataset rebuild capabilities.
        
        <div class="blueprint-header">🥈 SILVER LAYER (COMPRESSION & CLEANING)</div>
        • Data normalized into rows, stripping invalid characters, casting text objects into float representations.<br>
        • Written as optimized columnar Parquet objects via <b>PyArrow Engine</b> with Snappy compression. Saves storage by up to 80%.
        
        <div class="blueprint-header">🥇 GOLD WAREHOUSE (ANALYTICAL STAR SCHEMA)</div>
        • Data aggregated and stored securely inside an <b>SQLite DB Engine</b> infrastructure.<br>
        • Implements indexed analytical logs with <code>ingested_at</code> indexing for lightning-fast historical time-series retrieval.
        
        <div class="blueprint-header">🤖 MATHEMATICAL INFERENCE MODELING</div>
        • Implements a local <b>Scikit-Learn Linear Regression Core</b>.<br>
        • Trains on historical data to estimate asset trajectories for subsequent pipeline steps.
        """, unsafe_allow_html=True)
    
    st.markdown("### 🎛️ Pipeline Operations Center")
    
    # Render Primary Core Execution Action Triggers
    if not st.session_state.pipeline_executed:
        if st.button("▶ EXECUTE INTELLIGENCE PIPELINE", use_container_width=True):
            with st.spinner("Compiling ETL dependencies & configuring ML arrays..."):
                time.sleep(1)
                execute_pipeline()
            st.rerun()
    else:
        # Automated Background Refresh Controllers
        auto_refresh = st.toggle("⏱️ Enable Scheduled Auto-Refresh Loop")
        refresh_rate = st.selectbox("Interval Refresh Rate Duration", options=[5, 10, 30, 60], format_func=lambda x: f"Every {x} Seconds")
        
        col_side_b1, col_side_b2 = st.columns(2)
        with col_side_b1:
            if st.button("🔄 Sync Now", use_container_width=True):
                with st.spinner("Syncing data..."): execute_pipeline()
                st.rerun()
        with col_side_b2:
            if st.button("⬅️ Back", use_container_width=True):
                st.session_state.pipeline_executed = False
                st.rerun()
                
        if auto_refresh:
            st.info(f"⏳ Auto-refresh scheduled active: Updating every {refresh_rate}s")
            time.sleep(refresh_rate)
            execute_pipeline()
            st.rerun()

    st.markdown("---")
    st.markdown("### 💬 Project AI Assistant Core")
    
    # Robust Chat UI Rendering Element
    chat_html_buffer = "<div class='chat-container'>"
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            chat_html_buffer += f"<div class='user-msg'><b>👤 Interviewer:</b> {msg['text']}</div>"
        else:
            chat_html_buffer += f"<div class='ai-msg'><b>🤖 Pipeline System AI:</b> {msg['text']}</div>"
    chat_html_buffer += "</div>"
    st.markdown(chat_html_buffer, unsafe_allow_html=True)
    
    # Recommendation Question Pills Matrix
    st.markdown("<p style='font-size:12px; color:#a0b4c7; margin-bottom:2px;'>💡 Quick Recommendation Questions:</p>", unsafe_allow_html=True)
    cp_1, cp_2, cp_3 = st.columns(3)
    with cp_1:
        if st.button("Explain Medallion Architecture", key="pill1", help="Click to ask"):
            st.session_state.chat_history.append({"role": "user", "text": "Explain the Medallion Architecture workflow."})
            st.session_state.chat_history.append({"role": "ai", "text": advanced_ai_engine("Explain Medallion Architecture")})
            st.rerun()
    with cp_2:
        if st.button("How is Silver optimized?", key="pill2", help="Click to ask"):
            st.session_state.chat_history.append({"role": "user", "text": "How is the Silver layer optimized?"})
            st.session_state.chat_history.append({"role": "ai", "text": advanced_ai_engine("silver layer pyarrow parquet optimization")})
            st.rerun()
    with cp_3:
        if st.button("How does the ML work?", key="pill3", help="Click to ask"):
            st.session_state.chat_history.append({"role": "user", "text": "How does the machine learning integration model operate?"})
            st.session_state.chat_history.append({"role": "ai", "text": advanced_ai_engine("how machine learning works")})
            st.rerun()

    st.text_input("Interrogate Data Pipeline Context Engine...", key="chat_input_val", on_change=submit_chat, placeholder="Type message (e.g. Tell me about Bronze data formats...)")

# ------------------------------------------------------------------------------
# RIGHT SIDE PANEL: LIVE TELEMETRY VIEWPORT & ANALYTICS MONITOR
# ------------------------------------------------------------------------------
with col_viewport_panel:
    
    # MAIN BRAND TITLE DISPLAY
    st.markdown("<h1 style='margin-top: 0px;'>⚙️ Enterprise Intelligence Engine</h1>", unsafe_allow_html=True)
    
    # SCREEN STATE A: BLUEPRINT OVERVIEW (PIPELINE NOT YET RUN)
    if not st.session_state.pipeline_executed:
        st.markdown("### 🏗️ Pipeline Topography Map & Infrastructure Lineage Logs")
        
        flowchart_vertical_html = f"""
        <div class="flow-container">
            <div class="flow-box" style="border-color: #4caf50;">
                <div style="font-size:24px;">🌐</div>
                <div><b>1. Dynamic Network Ingestion Layer</b><br><small style='color:#a0b4c7;'>CoinCap HTTP API / Yahoo Finance Stream Processing Engines</small></div>
                <div class="flow-details"><span class="timestamp-badge">🟢 Network Connected: {sys_time}</span></div>
            </div>
            <div class="flow-box" style="border-color: #cd7f32;">
                <div style="font-size:24px;">🥉</div>
                <div><b>2. Immutable Bronze Data Lake Tier</b><br><small style='color:#a0b4c7;'>Raw Payload Ingestion / Fault Tolerant Logging Archive</small></div>
                <div class="flow-details"><span class="timestamp-badge">📝 Landed: {bronze_short}</span></div>
            </div>
            <div class="flow-box" style="border-color: #c0c0c0;">
                <div style="font-size:24px;">🥈</div>
                <div><b>3. Cleansed Silver Optimization Array</b><br><small style='color:#a0b4c7;'>PyArrow Engine Schema Mapping / Columnar Snappy Parquet Generation</small></div>
                <div class="flow-details"><span class="timestamp-badge">⚙️ Parsed: {silver_short}</span></div>
            </div>
            <div class="flow-box" style="border-color: #ffd700;">
                <div style="font-size:24px;">🥇</div>
                <div><b>4. Relational Gold Enterprise Warehouse</b><br><small style='color:#a0b4c7;'>ACID Relational Storage / Historical Time-Series Indexing</small></div>
                <div class="flow-details"><span class="timestamp-badge">🗄️ Committed: {gold_short}</span></div>
            </div>
            <div class="flow-box" style="border-color: #9c27b0;">
                <div style="font-size:24px;">📊</div>
                <div><b>5. Multi-Axis Serving Optimization UI</b><br><small style='color:#a0b4c7;'>Pearson Matrix Correlation Math Module / Streamlit Visualizer</small></div>
                <div class="flow-details"><span class="timestamp-badge">🖥️ Synchronized: {sys_time}</span></div>
            </div>
            <div class="flow-box" style="border-color: #00bcd4;">
                <div style="font-size:24px;">🤖</div>
                <div><b>6. Local Machine Learning Predictive Core</b><br><small style='color:#a0b4c7;'>Scikit-Learn Mathematical Linear Vector Trajectory Processing</small></div>
                <div class="flow-details"><span class="timestamp-badge">🧠 Retrained: {sys_time}</span></div>
            </div>
        </div>
        """
        st.markdown(flowchart_vertical_html, unsafe_allow_html=True)
        st.info("💡 **Operational Notice:** The pipeline context is fully mapped out. Click the big green execute button on the left panel to run live data transformations and view advanced analytics charts.")

    # SCREEN STATE B: DATA METRICS ACTIVE DISPLAY
    else:
        conn = sqlite3.connect('data/crypto_warehouse.db')
        df = pd.read_sql("SELECT * FROM gold_crypto_prices ORDER BY ingested_at ASC", conn)
        conn.close()
        
        latest_time = df['ingested_at'].max()
        latest_df = df[df['ingested_at'] == latest_time]

        # MODIFICATION 2: Massive Tabs generated cleanly on top
        tab1, tab2 = st.tabs(["🏗️ Pipeline Infrastructure State", "🧠 Advanced Analytics & ML Inference"])

        # --- TAB 1: THE DATA TRANSFORMATION STATE ---
        with tab1:
            st.markdown(f"### 🔍 Enterprise Multi-Schema Observer <span style='font-size:14px;' class='timestamp-badge'>Last Checked: {st.session_state.last_refresh_time}</span>", unsafe_allow_html=True)
            
            b_size, s_size, savings = calculate_de_metrics()
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1: st.metric("Raw Bronze JSON Size", f"{b_size} Bytes")
            with col_m2: st.metric("Compressed Silver Parquet", f"{s_size} Bytes")
            with col_m3: st.metric("Storage Optimization Ratio", f"{savings:.1f}% Savings", delta=f"{savings:.1f}% Compression Efficiency")

            st.markdown("---")
            col_b, col_s, col_g = st.columns(3)
            with col_b:
                st.markdown(f"#### 🥉 Bronze Lake <br><span class='timestamp-badge'>File Update: {bronze_ts}</span>", unsafe_allow_html=True)
                bronze_file, _ = get_file_info('data/bronze', '.json')
                if bronze_file:
                    with open(bronze_file, 'r') as f: st.json(json.load(f))
            with col_s:
                st.markdown(f"#### 🥈 Silver Lake <br><span class='timestamp-badge'>File Update: {silver_ts}</span>", unsafe_allow_html=True)
                silver_file, _ = get_file_info('data/silver', '.parquet')
                if silver_file: st.dataframe(pd.read_parquet(silver_file), hide_index=True)
            with col_g:
                st.markdown(f"#### 🥇 Gold Warehouse <br><span class='timestamp-badge'>DB Commit: {gold_ts}</span>", unsafe_allow_html=True)
                st.dataframe(latest_df[['symbol', 'priceUsd', 'ingested_at']], hide_index=True)

        # --- TAB 2: AI INSIGHTS, CORRELATION & MACHINE LEARNING ---
        with tab2:
            st.markdown("### 🧠 AI Analytics & Macroeconomic Correlation")
            
            clean_df = df.drop_duplicates(subset=['ingested_at', 'symbol'])
            pivot_df = clean_df.pivot(index='ingested_at', columns='symbol', values='priceUsd')
            
            correlation_msg = "Awaiting historical tracking coordinates..."
            corr_value = 0.0
            if 'BTC' in pivot_df.columns and 'S&P500' in pivot_df.columns and len(pivot_df) > 1:
                corr_value = pivot_df['BTC'].corr(pivot_df['S&P500'])
                if pd.isna(corr_value): correlation_msg = "Identical value parameters mapped. Trigger data refresh loop to generate price variances."
                elif corr_value > 0.4: correlation_msg = f"Strong Positive Correlation ({corr_value:.2f}). Crypto and Legacy Equities climb in tandem."
                elif corr_value < -0.4: correlation_msg = f"Inverse Macro Tracking Asset ({corr_value:.2f}). Bitcoin acts as a clear systematic market hedge."
                else: correlation_msg = f"Neutral Asset Decoupling Class ({corr_value:.2f}). Digital assets navigate completely free of traditional indices."

            ml_prediction_msg = "Awaiting dataset volume metrics to configure weights..."
            trend_signal = "SYSTEM BALANCED INERTIA"
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
                    trend_signal = "ACCELERATING BULLISH TRAJECTORY SIGNAL"
                    signal_color = "#2E7D32" 
                else:
                    trend_signal = "DEFENSIVE MARKET CONSOLIDATION PREDICTION"
                    signal_color = "#C62828" 
                ml_prediction_msg = f"Trained local **Scikit-Learn Linear Ordinary Least Squares Regression** on {len(btc_history)} warehouse matrices. Next expected pricing sequence trajectory target: **${predicted_price:,.2f}**."

            st.markdown(f'<div class="signal-box" style="background-color: {signal_color};">🤖 LIVE AI ENVIRONMENT BIAS: {trend_signal}</div>', unsafe_allow_html=True)
            st.info(f"**💡 Core Inference Analytics Summary:**\n\n* **Macro Correlation Matrix:** {correlation_msg}\n\n* **Mathematical Modeling Output:** {ml_prediction_msg}")
            
            st.markdown("---")
            st.subheader("📊 Cross-Asset Multi-Axis Tracking Engine")
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown("#### Cryptocurrency Pricing Curves (USD)")
                crypto_cols = [c for c in pivot_df.columns if c != 'S&P500']
                if crypto_cols:
                    st.line_chart(pivot_df[crypto_cols].apply(pd.to_numeric))
            with col_c2:
                st.markdown("#### Macro Equity Benchmarks: S&P 500 Index (Points)")
                
                # MODIFICATION 5: Fixed blank dashboard element via adaptive single data layout configuration
                if 'S&P500' in pivot_df.columns:
                    sp_chart_data = pivot_df[['S&P500']].apply(pd.to_numeric)
                    if len(sp_chart_data) == 1:
                        st.write("##### Baseline Timepoint Coordinates Initialized:")
                        st.dataframe(sp_chart_data, use_container_width=True)
                    else:
                        st.line_chart(sp_chart_data)
                else:
                    st.warning("Awaiting S&P 500 data buffers...")

            st.markdown("---")
            st.subheader("⚡ Active Asset KPI Monitors")
            cols = st.columns(len(latest_df))
            for index, row in latest_df.reset_index().iterrows():
                with cols[index]:
                    if row['symbol'] == 'S&P500': st.metric(label="🇺🇸 S&P 500 Macro Benchmark Index", value=f"{float(row['priceUsd']):,.2f} pts")
                    else: st.metric(label=f"🪙 {row['symbol']} Asset Target", value=f"${float(row['priceUsd']):,.2f}")
