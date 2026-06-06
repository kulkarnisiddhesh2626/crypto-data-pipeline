import pandas as pd
import sqlite3
import os
import glob
from datetime import datetime

def load_to_gold():
    os.makedirs('data', exist_ok=True)
    print("Starting Gold Layer Data Warehouse Load...")
    
    list_of_files = glob.glob('data/silver/*.parquet')
    if not list_of_files:
        print("Error: No Silver files found.")
        return
        
    latest_file = max(list_of_files, key=os.path.getctime)
    df = pd.read_parquet(latest_file)
    
    # NEW DE FLEX: Add an audit column for tracking when data arrived
    df['ingested_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    db_path = 'data/crypto_warehouse.db'
    conn = sqlite3.connect(db_path)
    
    # NEW DE FLEX: Change 'replace' to 'append' to build a historical time-series
    df.to_sql('gold_crypto_prices', conn, if_exists='append', index=False)
    
    print(f"Success! Data appended to SQL Database.")
    conn.close()

if __name__ == "__main__":
    load_to_gold()
