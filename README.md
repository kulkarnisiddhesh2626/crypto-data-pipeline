# 🚀 Enterprise Data Engineering Pipeline (Medallion Architecture)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458.svg)
![SQLite](https://img.shields.io/badge/SQLite-Data_Warehouse-lightgrey.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Interactive_UI-FF4B4B.svg)

## 📖 Executive Summary
This repository contains an end-to-end, automated Data Engineering pipeline that extracts live cryptocurrency market data, processes it using the industry-standard **Medallion Architecture (Bronze, Silver, Gold)**, and serves it through a highly interactive Streamlit application. 

The project goes beyond a standard dashboard by including a **"Presentation Mode"** that visualizes the exact structural changes of the data as it moves through the pipeline, making it an excellent demonstration of data lineage, schema enforcement, and ETL workflows.

## 🏗️ Architecture & Data Flow
The pipeline follows a strict 6-step ETL/ELT sequence:

1. 🌐 **API Source:** Live data extraction from the CoinCap API using Python `requests` with built-in fault tolerance and mock-data fallbacks.
2. 🥉 **Bronze Layer (Raw Data):** Ingests raw, nested JSON payloads. Saved locally to preserve absolute data lineage and act as a recovery backup.
3. 🥈 **Silver Layer (Cleaned Data):** Flattens the JSON, enforces strict data types (strings to floats), and compresses the output into highly optimized, columnar `.parquet` files using `PyArrow` and `Pandas`.
4. 🥇 **Gold Layer (Business-Ready):** Loads the clean Parquet data into a structured `SQLite` database. Appends an `ingested_at` timestamp to enable historical time-series analytics.
5. 📊 **Serving UI:** A multi-page Streamlit application that acts as the front-end interface.
6. 🤖 **AI/Logic Layer:** Uses Pandas aggregations to automatically generate text-based inferences and business summaries based on the live data.

## 🌟 Key Features
* **Interactive Architecture Diagram:** A custom HTML/CSS flowchart built directly into the app to explain the ETL workflow to non-technical stakeholders.
* **Real-Time Data Inspector (DE View):** An interface that displays the actual `.json`, `.parquet`, and SQL data side-by-side, allowing users to visually inspect schema changes across the Medallion layers.
* **Automated AI Summaries:** Dynamic Python logic that reads the Gold layer and generates natural language business summaries.
* **One-Click Orchestration:** A web-based trigger that allows users to execute the entire Python ETL extraction and transformation sequence directly from their browser.

## 📂 Project Structure
```text
crypto-data-pipeline/
├── data/
│   ├── bronze/               # Raw JSON data (Auto-generated)
│   ├── silver/               # Cleaned Parquet files (Auto-generated)
│   └── crypto_warehouse.db   # Gold Layer SQLite Database (Auto-generated)
├── scripts/
│   ├── extract_api.py        # Bronze layer extraction script
│   ├── transform_silver.py   # Silver layer transformation script
│   └── load_gold.py          # Gold layer data warehouse load script
├── dashboard/
│   └── app.py                # Streamlit visualization & orchestration app
├── requirements.txt          # Pinned Python dependencies
└── README.md                 # Project documentation
