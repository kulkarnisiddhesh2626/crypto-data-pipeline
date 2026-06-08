import pandas as pd
import glob
import os

def transform_to_silver():
    # Enforce directory creation
    os.makedirs('data/silver', exist_ok=True)
    
    # Identify the latest raw extraction file
    bronze_files = glob.glob('data/bronze/*.json')
    if not bronze_files:
        print("No Bronze data found to transform.")
        return
    latest_file = max(bronze_files, key=os.path.getctime)
    
    # Read the raw multi-source JSON data
    df = pd.read_json(latest_file)
    
    # Standardize and clean schemas across macro and crypto assets
    df['priceUsd'] = pd.to_numeric(df['priceUsd'], errors='coerce')
    df['marketCapUsd'] = pd.to_numeric(df['marketCapUsd'], errors='coerce')
    
    # Clear invalid records
    df = df.dropna(subset=['symbol'])
    
    # Export to highly optimized columnar Parquet format
    filename = os.path.basename(latest_file).replace('raw_', 'clean_').replace('.json', '.parquet')
    df.to_parquet(f'data/silver/{filename}', engine='pyarrow', index=False)
    print(f"Successfully transformed {filename} to Silver Layer.")
