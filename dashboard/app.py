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
if 'right_panel_view' not in st.session_state:
    st.session_state.right_panel_view = "chat" # Defaults to Chatbot view
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "text": "👋 Welcome to the Pipeline Control Center. Ask me about the Medallion setup, schema designs, or local machine learning components!"}
    ]

# --- SYSTEM STYLING & CUSTOM USER INTERFACE TUNING ---
st.markdown("""
    <style>
    .stApp { background-color: #0b1622; color: #f0f4f8; }
    h1, h2, h3, h4, p, label { color: #f0f4f8 !important; font-family: 'Segoe UI', sans-serif; }
    
    /* MODIFICATION: Identical, massive, equal-sized Green Buttons for the Right Panel */
    .stButton>button {
        background-color: #4caf50 !important; 
        color: white !important; 
        font-size: 18px !important; 
        font-weight: bold !important; 
        padding: 15px !important; 
        border-radius: 8px !important;
        border: 2px solid #81c784 !important;
        width: 100% !important;
        height: 65px !important;
        transition: 0.3s;
        margin-bottom: 5px;
    }
    .stButton>button:hover { background-color: #388e3c !important; transform: scale(1.02); }
    
    /* Quick Action Chat Pills */
    .chat-pill-container { display: flex; gap: 8px; margin-bottom: 15px; flex-wrap: wrap; }
    div[data-testid="stVerticalBlock"] div.stButton>button.chat-pill-btn {
        height: 35px !important; font-size: 12px !important; background-color: #1a2a40 !important;
        border: 1px solid #3a7bd5 !important; border-radius: 20px !important; color: #a0b4c7 !important;
    }
    div[data-testid="stVerticalBlock"] div.stButton>button.chat-pill-btn:hover { background-color: #3a7bd5 !important; color: white !important; }
    
    /* Viewport UI Adjustments */
    button[data-baseweb="tab"] { height: 60px !important; }
    button[data-baseweb="tab"] p { font-size: 26px !important; font-weight: bold !important; color: #a0b4c7 !important; }
    button[data-baseweb="tab"][aria-selected="true"] p { color: #4caf50 !important; border-bottom: 3px solid #4caf50; }
    
    .flow-container { display: flex; flex-direction: column; gap: 12px; background-color: #132235; padding: 20px; border-radius: 16px; border: 1px solid #1e3a5f; }
    .flow-box { display: flex; align-items: center; background: #1a2a40; border-left: 6px solid #3a7bd5; border-radius: 8px; padding: 12px 20px; gap: 15px; }
    .flow-details { text-align: left; font-size: 12px; color: #a0b4c7; margin-left: auto; line-height: 1.4; }
    [data-testid="stMetric"] { background-color: #1a2a40; border-left: 5px solid #4caf50; padding: 15px; border-radius: 8px; }
    .signal-box { padding: 18px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; font-size: 16px; text-align: center; }
    .timestamp-badge { background-color: #263238; color: #00e676 !important; font-family: monospace; padding: 2px 6px; border-radius: 4px; font-size: 10px; display: inline-block; }
    
    /* Project Blueprint Text Color Fix */
    .blueprint-header { color: #ffd700 !important; font-size: 14px; font-weight: bold; margin-top: 15px; border-bottom: 1px solid rgba(255,255,255,0.15); padding-bottom: 4px; }
    .blueprint-text { color: #a0b4c7 !important; font-size: 13px; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

# --- SYSTEM UTILITIES ---
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

# --- MODIFICATION: ROBUST AI CHAT ENGINE ---
def advanced_ai_engine(query):
    q = query.lower().strip()
    weights = {
        "medallion": ["medallion", "architecture", "layer", "bronze", "silver", "gold", "design"],
        "bronze": ["bronze", "raw", "json", "ingest", "coincap", "immutable"],
        "silver": ["silver", "parquet", "pyarrow", "clean", "transform", "compression"],
        "gold": ["gold", "warehouse", "sqlite", "relational", "sql", "tables"],
        "ml": ["ml", "machine learning", "predict", "regression", "scikit-learn", "forecast"],
        "macro": ["macro", "s&p500", "s&p", "correlation", "stock", "yfinance"],
        "pipeline": ["orchestration", "refresh", "automate", "pipeline", "execution"]
    }
    scores = {k: sum(1 for word in v if word in q) for k, v in weights.items()}
    max_intent = max(scores, key=scores.get)
    
    if scores[max_intent] == 0:
        if any(g in q for g in ["hi", "hello", "hey", "help"]): return "Hello! I am your technical co-pilot. Ask me details about our Bronze/Silver/Gold layers or our ML predictive core!"
        return "⚠️ **Out of Scope:** To safeguard precision guidelines, I only answer questions regarding this project's Data Engineering architecture (Medallion Layers), Machine Learning models, or Macroeconomic data processing."

    responses = {
        "medallion": "📐 **Medallion Architecture:** This system processes data through logical validation tiers. **Bronze** is the immutable landing zone. **Silver** handles schema enforcement and PyArrow Parquet compression. **Gold** aggregates the data into an ACID-compliant SQLite warehouse.",
        "bronze": "🥉 **Bronze Layer:** Operates as a fault-tolerant landing zone. The script fetches CoinCap and Yahoo Finance APIs, saving responses as raw JSON in `data/bronze/` to guarantee absolute data lineage.",
        "silver": "🥈 **Silver Layer:** Reads the Bronze JSON, normalizes types, casts to floats, and handles missing observations. Writes using PyArrow into columnar Parquet files to save up to 80% disk space.",
        "gold": "🥇 **Gold Warehouse:** The analytical layer maps records into an embedded SQLite database (`crypto_warehouse.db`). It enforces a star schema and timestamps every transaction for historical time-series analytics.",
        "ml": "🤖 **Machine Learning Core:** Built on `scikit-learn`. It uses **Linear Regression** to read historical price matrices from the Gold warehouse, evaluating trajectories to forecast the next asset price movement.",
        "macro": "📊 **Macro Tracking:** Integrates the S&P 500 Index. We compute the **Pearson Correlation Coefficient** to mathematically determine if digital assets act as independent alternative instruments or follow legacy equities.",
        "pipeline": "⏱️ **Automation:** Execution sequences run sequentially: Extraction ➔ Transformation ➔ Loading. It features a session-state managed UI and background scheduler capabilities."
    }
    return responses[max_intent]

def inject_chat(query):
    st.session_state.chat_history.append({"role": "user", "text": query})
    st.session_state.chat_history.append({"role": "assistant", "text": advanced_ai_engine(query)})

# --- POLLING TIMESTAMPS ---
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
# MAIN ASYMMETRIC LAYOUT (VIEWPORT ON LEFT, CONTROLS ON RIGHT)
# ==============================================================================
col_viewport, col_controls = st.columns([2.7, 1.3])

# ------------------------------------------------------------------------------
# RIGHT PANEL: CONTROL CENTER (EQUAL SIZE BUTTONS & ROBUST CHAT)
# ------------------------------------------------------------------------------
with col_controls:
    st.markdown("<br>", unsafe_allow_html=True) # Alignment padding
    
    # 1. THE THREE IDENTICAL BUTTONS
    if st.button("ℹ️ ABOUT PROJECT"):
        st.session_state.right_panel_view = "about"
        
    if st.button("💬 AI CHATBOT"):
        st.session_state.right_panel_view = "chat"
        
    if not st.session_state.pipeline_executed:
        if st.button("▶ EXECUTE PIPELINE"):
            with st.spinner("Compiling ETL pipelines..."):
                time.sleep(1)
                execute_pipeline()
            st.rerun()
    else:
        if st.button("⬅️ BACK TO BLUEPRINT"):
            st.session_state.pipeline_executed = False
            st.rerun()
            
    st.markdown("---")

    # 2. DYNAMIC CONTENT VIEWER (Driven by buttons above)
    if st.session_state.right_panel_view == "about":
        st.markdown("### ℹ️ Project Blueprint")
        about_container = st.container(height=500)
        with about_container:
            st.markdown(f"""
            <div class="blueprint-text">
            This enterprise application demonstrates a complete end-to-end Lakehouse Architecture.
            
            <div class="blueprint-header">🌐 INGESTION MECHANICS</div>
            • <b>CoinCap API</b>: Crypto Array JSON Payload.<br>
            • <b>YFinance</b>: S&P 500 Macroeconomic Index.
            
            <div class="blueprint-header">🥉 BRONZE LAKE</div>
            • Preserves pure unaltered JSON lineage backups directly to local storage.
            
            <div class="blueprint-header">🥈 SILVER LAYER</div>
            • Applies schema mapping, clears null values, and converts to <b>PyArrow Parquet</b>.
            
            <div class="blueprint-header">🥇 GOLD WAREHOUSE</div>
            • Maps optimized data to an <b>SQLite Star-Schema Database</b> for time-series aggregation.
            
            <div class="blueprint-header">🤖 ML CORE</div>
            • Triggers <b>Scikit-Learn OLS Regression</b> locally to output target pricing vectors.
            </div>
            """, unsafe_allow_html=True)

    elif st.session_state.right_panel_view == "chat":
        st.markdown("### 💬 AI Assistant")
        
        # Native Streamlit Scrollable Chat Container (Robust UI fix)
        chat_container = st.container(height=400)
        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["text"])
        
        # Recommendation Pills Layout
        p1, p2 = st.columns(2)
        with p1:
            st.markdown('<div class="chat-pill-container">', unsafe_allow_html=True)
            if st.button("Explain Medallion Arch?", key="p1"):
                inject_chat("Explain Medallion Architecture")
                st.rerun()
        with p2:
            if st.button("How does the ML work?", key="p2"):
                inject_chat("How does Machine learning work?")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Native Chat Input
        if prompt := st.chat_input("Ask about the architecture..."):
            inject_chat(prompt)
            st.rerun()

# ------------------------------------------------------------------------------
# LEFT PANEL: LIVE TELEMETRY VIEWPORT
# ------------------------------------------------------------------------------
with col_viewport:
    st.markdown("<h1 style='margin-top: 0px;'>⚙️ Enterprise Intelligence Engine</h1>", unsafe_allow_html=True)
    
    if not st.session_state.pipeline_executed:
        st.markdown("### 🏗️ Pipeline Topography Map & Infrastructure Lineage Logs")
        
        st.markdown(f"""
        <div class="flow-container">
            <div class="flow-box" style="border-color: #4caf50;">
                <div style="font-size:24px;">🌐</div>
                <div><b>1. Dynamic Network Ingestion Layer</b><br><small style='color:#a0b4c7;'>CoinCap HTTP API / Yahoo Finance Stream Processing Engines</small></div>
                <div class="flow-details"><span class="timestamp-badge">🟢 Network: {sys_time}</span></div>
            </div>
            <div class="flow-box" style="border-color: #cd7f32;">
                <div style="font-size:24px;">🥉</div>
                <div><b>2. Immutable Bronze Data Lake Tier</b><br><small style='color:#a0b4c7;'>Raw Payload Ingestion / Fault Tolerant Logging Archive</small></div>
                <div class="flow-details"><span class="timestamp-badge">📝 Landed: {bronze_short}</span></div>
            </div>
            <div class="flow-box" style="border-color: #c0c0c0;">
                <div style="font-size:24px;">🥈</div>
                <div><b>3. Cleansed Silver Optimization Array</b><br><small style='color:#a0b4c7;'>PyArrow Engine Mapping / Snappy Columnar Parquet Generation</small></div>
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
                <div class="flow-details"><span class="timestamp-badge">🖥️ Synced: {sys_time}</span></div>
            </div>
            <div class="flow-box" style="border-color: #00bcd4;">
                <div style="font-size:24px;">🤖</div>
                <div><b>6. Local Machine Learning Predictive Core</b><br><small style='color:#a0b4c7;'>Scikit-Learn Mathematical Linear Trajectory Processing</small></div>
                <div class="flow-details"><span class="timestamp-badge">🧠 Retrained: {sys_time}</span></div>
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

        tab1, tab2 = st.tabs(["🏗️ Pipeline Infrastructure State", "🧠 Advanced Analytics & ML Inference"])

        # --- TAB 1: DATA LINEAGE ---
        with tab1:
            st.markdown(f"### 🔍 Schema Observer <span style='font-size:14px;' class='timestamp-badge'>Refreshed: {st.session_state.last_refresh_time}</span>", unsafe_allow_html=True)
            
            b_size, s_size, savings = calculate_de_metrics()
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1: st.metric("Raw Bronze JSON Size", f"{b_size} Bytes")
            with col_m2: st.metric("Compressed Silver Parquet", f"{s_size} Bytes")
            with col_m3: st.metric("Storage Optimization Ratio", f"{savings:.1f}% Savings", delta=f"{savings:.1f}% Efficiency")

            st.markdown("---")
            col_b, col_s, col_g = st.columns(3)
            with col_b:
                st.markdown(f"#### 🥉 Bronze Lake", unsafe_allow_html=True)
                bronze_file, _ = get_file_info('data/bronze', '.json')
                if bronze_file:
                    with open(bronze_file, 'r') as f: st.json(json.load(f))
            with col_s:
                st.markdown(f"#### 🥈 Silver Parquet", unsafe_allow_html=True)
                silver_file, _ = get_file_info('data/silver', '.parquet')
                if silver_file: st.dataframe(pd.read_parquet(silver_file), hide_index=True)
            with col_g:
                st.markdown(f"#### 🥇 Gold SQLite DB", unsafe_allow_html=True)
                st.dataframe(latest_df[['symbol', 'priceUsd', 'ingested_at']], hide_index=True)

        # --- TAB 2: ANALYTICS & AI ---
        with tab2:
            st.markdown("### 🧠 AI Analytics & Macro Correlation")
            
            clean_df = df.drop_duplicates(subset=['ingested_at', 'symbol'])
            pivot_df = clean_df.pivot(index='ingested_at', columns='symbol', values='priceUsd')
            
            correlation_msg = "Awaiting historical data tracking..."
            if 'BTC' in pivot_df.columns and 'S&P500' in pivot_df.columns and len(pivot_df) > 1:
                corr_value = pivot_df['BTC'].corr(pivot_df['S&P500'])
                if pd.isna(corr_value): correlation_msg = "No variance detected. Execute refresh loop."
                elif corr_value > 0.4: correlation_msg = f"Strong Positive Correlation ({corr_value:.2f}). Crypto and Equities climb in tandem."
                elif corr_value < -0.4: correlation_msg = f"Inverse Tracking Asset ({corr_value:.2f}). Bitcoin acts as a market hedge."
                else: correlation_msg = f"Neutral Decoupling ({corr_value:.2f}). Digital assets navigate independently."

            ml_prediction_msg = "Awaiting dataset volume to configure ML..."
            trend_signal, signal_color = "SYSTEM BALANCED", "#FFA500" 
            
            btc_history = df[df['symbol'] == 'BTC'].sort_values('ingested_at')
            if len(btc_history) >= 2:
                X, y = np.array(range(len(btc_history))).reshape(-1, 1), btc_history['priceUsd'].values
                ml_model = LinearRegression().fit(X, y)
                predicted_price = ml_model.predict(np.array([[len(btc_history)]]))[0]
                
                if predicted_price > y[-1]:
                    trend_signal, signal_color = "BULLISH TRAJECTORY SIGNAL", "#2E7D32" 
                else:
                    trend_signal, signal_color = "DEFENSIVE CONSOLIDATION", "#C62828" 
                ml_prediction_msg = f"Scikit-Learn OLS Regression trained on {len(btc_history)} records. Next target: **${predicted_price:,.2f}**."

            st.markdown(f'<div class="signal-box" style="background-color: {signal_color};">🤖 ML SIGNAL: {trend_signal}</div>', unsafe_allow_html=True)
            st.info(f"**💡 Core Inference Summary:**\n\n* **Macro Correlation:** {correlation_msg}\n\n* **Math Model:** {ml_prediction_msg}")
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown("#### Crypto Pricing Curves")
                crypto_cols = [c for c in pivot_df.columns if c != 'S&P500']
                if crypto_cols: st.line_chart(pivot_df[crypto_cols].apply(pd.to_numeric))
            with col_c2:
                st.markdown("#### S&P 500 Index Benchmark")
                if 'S&P500' in pivot_df.columns:
                    sp_data = pivot_df[['S&P500']].apply(pd.to_numeric)
                    if len(sp_data) == 1: st.dataframe(sp_data, use_container_width=True)
                    else: st.line_chart(sp_data)

            st.markdown("---")
            cols = st.columns(len(latest_df))
            for index, row in latest_df.reset_index().iterrows():
                with cols[index]:
                    if row['symbol'] == 'S&P500': st.metric(label="🇺🇸 S&P 500", value=f"{float(row['priceUsd']):,.2f} pts")
                    else: st.metric(label=f"🪙 {row['symbol']}", value=f"${float(row['priceUsd']):,.2f}")
