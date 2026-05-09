import pandas as pd
import sqlite3
import os
import glob

def load_to_gold():
    print("Starting Gold Layer Data Warehouse Load...")
    
    # 1. Find the newest Parquet file in the silver folder
    list_of_files = glob.glob('data/silver/*.parquet')
    if not list_of_files:
        print("Error: No Silver files found to process.")
        return
        
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Reading clean Parquet data from: {latest_file}")
    
    # 2. Read the compressed Parquet file using Pandas
    df = pd.read_parquet(latest_file)
    
    # 3. Connect to our local "Data Warehouse" (SQLite)
    # This automatically creates a database file named crypto_warehouse.db in our data folder
    db_path = 'data/crypto_warehouse.db'
    conn = sqlite3.connect(db_path)
    
    # 4. Load the data into a SQL table named 'gold_crypto_prices'
    # 'replace' means if the table exists, drop it and recreate it with fresh data
    df.to_sql('gold_crypto_prices', conn, if_exists='replace', index=False)
    
    print(f"Success! Data loaded into SQL Database at {db_path}")
    
    # 5. Let's do a quick SQL query to prove the data is actually in the database!
    print("\n--- Verifying Data in SQL ---")
    query = "SELECT symbol, priceUsd, marketCapUsd FROM gold_crypto_prices LIMIT 3"
    query_result = pd.read_sql(query, conn)
    print(query_result)
    
    # Close the database connection
    conn.close()

if __name__ == "__main__":
    load_to_gold()