# verify_data.py
import pandas as pd
from pathlib import Path

# Load the raw extracted dataset
raw_csv = Path("data/raw/mumbai_traffic_tweets.csv")
processed_csv = Path("data/raw/mumbai_traffic_processed.csv")

if processed_csv.exists():
    df_proc = pd.read_csv(processed_csv)
    df_raw = pd.read_csv(raw_csv)
    
    print("🔍 FETCHING TOP INCIDENT FROM YOUR DATASET:")
    print("-" * 60)
    top_processed = df_proc.iloc[0]
    print(f"📅 Timestamp: {top_processed['createdAt']}")
    print(f"📍 Region:    {top_processed['Mumbai_Region']}")
    print(f"🔧 Reason:    {top_processed['Traffic_Reason']}")
    
    # Match it back to the raw URL using the unique ID
    tweet_id = top_processed['id']
    raw_match = df_raw[df_raw['id'] == tweet_id].iloc[0]
    
    print(f"📝 Text:      {top_processed['text']}")
    print("-" * 60)
    print(f"🌐 LINK TO LIVE TWEET ON X:\n{raw_match['url']}")
    print("-" * 60)
else:
    print("❌ Processed file not found.")