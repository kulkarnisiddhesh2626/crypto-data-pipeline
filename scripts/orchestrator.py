import schedule
import time
from datetime import datetime

# Import the functions we built in Phases 2, 3, and 4
from extract_api import extract_crypto_data
from transform_silver import transform_to_silver
from load_gold import load_to_gold

def run_pipeline():
    print(f"\n{'='*50}")
    print(f"🚀 PIPELINE RUN INITIATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    
    try:
        # Step 1: Bronze
        extract_crypto_data()
        
        # Step 2: Silver
        transform_to_silver()
        
        # Step 3: Gold
        load_to_gold()
        
        print(f"\n✅ PIPELINE RUN COMPLETE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
    except Exception as e:
        print(f"\n❌ PIPELINE FAILED: {e}")
        print(f"{'='*50}\n")

if __name__ == "__main__":
    # Run it once immediately
    run_pipeline()
    
    # Schedule it to run every 5 minutes automatically
    print("⏳ Orchestrator is running. Waiting for the next scheduled run in 5 minutes...")
    print("Press Ctrl+C to stop the orchestrator.")
    
    schedule.every(5).minutes.do(run_pipeline)
    
    # Keep the script running forever
    while True:
        schedule.run_pending()
        time.sleep(1)