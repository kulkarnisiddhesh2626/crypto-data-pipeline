import pandas as pd
import json
import os
import glob

def transform_to_silver():
    os.makedirs('data/silver', exist_ok=True)
    print("Starting Silver Layer Transformation...")
    
    # 1. Find the newest file in the bronze folder automatically
    list_of_files = glob.glob('data/bronze/*.json')
    if not list_of_files:
        print("Error: No Bronze files found to process.")
        return
        
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Reading raw data from: {latest_file}")
    
    # 2. Load the JSON data
    with open(latest_file, 'r') as f:
        raw_data = json.load(f)
        
    # 3. Extract the 'data' list from the JSON payload
    crypto_list = raw_data['data']
    
    # 4. Convert to a Pandas DataFrame
    df = pd.DataFrame(crypto_list)
    
    # 5. The Silver Transformation Rules:
    # A. Keep only the columns we actually need for business analytics
    df = df[['id', 'symbol', 'rank', 'priceUsd', 'volumeUsd24Hr', 'marketCapUsd']]
    
    # B. The API gives us prices as Text (Strings). We must convert them to Floats (Decimals).
    numeric_cols = ['priceUsd', 'volumeUsd24Hr', 'marketCapUsd']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # 6. Save as a highly-compressed Parquet file in the Silver folder
    filename = os.path.basename(latest_file).replace('.json', '.parquet')
    silver_path = f"data/silver/{filename}"
    
    df.to_parquet(silver_path, index=False)
    print(f"Success! Clean data saved as Parquet to {silver_path}")

if __name__ == "__main__":
    transform_to_silver()
