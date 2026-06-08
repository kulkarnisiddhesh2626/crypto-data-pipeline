import pandas as pd
import sqlite3
import glob
import os
from datetime import datetime

def load_to_gold():
    os.makedirs('data', exist_ok=True)
    
    # Identify the latest cleaned transformation file
    silver_files = glob.glob('data/silver/*.parquet')
    if not silver_files:
        print("No Silver data found to load.")
        return
    latest_file = max(silver_files, key=os.path.getctime)
    
    # Read optimized parquet data
    df = pd.read_parquet(latest_file)
    
    # Add historical tracking time-stamp for relational analysis
    df['ingested_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Append the record into the primary SQLite Data Warehouse
    conn = sqlite3.connect('data/crypto_warehouse.db')
    df.to_sql('gold_crypto_prices', conn, if_exists='append', index=False)
    conn.close()
    print(f"Successfully loaded {os.path.basename(latest_file)} into Gold Warehouse database.")
