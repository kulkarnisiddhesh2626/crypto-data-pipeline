import requests
import json
from datetime import datetime
import os

def extract_crypto_data():
    os.makedirs('data/bronze', exist_ok=True)
    url = "https://api.coincap.io/v2/assets"
    print(f"Attempting to fetch live crypto data from {url}...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/bronze/crypto_raw_{timestamp}.json"
    
    try:
        # We add a 'User-Agent' so the API thinks we are a web browser, not a bot
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # This forces an error if the website is down
        data = response.json()
        print("Success: API is online!")
        
    except requests.exceptions.RequestException as e:
        print(f"Warning: API Connection Failed ({e}).")
        print("DE PRO TIP: Falling back to Mock Data so our pipeline testing can continue!")
        
        # This is fake data structured exactly like the real API
        data = {
            "data": [
                {"id": "bitcoin", "symbol": "BTC", "rank": "1", "priceUsd": "64230.50", "volumeUsd24Hr": "12000000000", "marketCapUsd": "1200000000000"},
                {"id": "ethereum", "symbol": "ETH", "rank": "2", "priceUsd": "3450.75", "volumeUsd24Hr": "8000000000", "marketCapUsd": "400000000000"},
                {"id": "solana", "symbol": "SOL", "rank": "3", "priceUsd": "145.20", "volumeUsd24Hr": "1500000000", "marketCapUsd": "65000000000"}
            ]
        }
    
    # Save the data (whether real or mocked) into our Bronze folder
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
        
    print(f"Success! Raw data saved to {filename}")

if __name__ == "__main__":
    extract_crypto_data()
