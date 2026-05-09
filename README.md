\# Crypto Data Pipeline (Medallion Architecture)



\## Overview

This is an automated, end-to-end Data Engineering pipeline built in Python. It extracts cryptocurrency data, processes it using the Medallion Architecture (Bronze, Silver, Gold), and visualizes the clean data in an interactive dashboard.



\## Tech Stack

\* \*\*Language:\*\* Python, SQL

\* \*\*Data Processing:\*\* Pandas, PyArrow (Parquet)

\* \*\*Database:\*\* SQLite (Data Warehouse)

\* \*\*Orchestration:\*\* Python `schedule` library

\* \*\*Visualization:\*\* Streamlit



\## Architecture

1\. \*\*Bronze Layer:\*\* Extracts raw JSON data from the CoinCap API. Includes fault-tolerance (mock data fallback).

2\. \*\*Silver Layer:\*\* Cleans data, formats numeric types, and compresses it into columnar Parquet files.

3\. \*\*Gold Layer:\*\* Loads the clean Parquet data into a structured SQLite database.

4\. \*\*Orchestration:\*\* Automates the pipeline to run continuously.

5\. \*\*Dashboard:\*\* Connects to the Gold layer to visualize live market capitalization.



\## How to Run Locally

1\. Clone the repository.

2\. Activate the virtual environment and install dependencies: `pip install -r requirements.txt`

3\. Run the orchestrator: `python scripts/orchestrator.py`

4\. In a separate terminal, run the dashboard: `streamlit run dashboard/app.py`

