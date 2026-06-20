# src/nlp/classify_traffic.py
import pandas as pd
import re
from pathlib import Path

def categorize_incident(text):
    text = str(text).lower()
    
    # Advanced matching tuned directly to MTP's real alert vocabulary
    if "clear" in text:
        return "Traffic Cleared / Normal"
    elif any(k in text for k in ["breakdown", "broken down", "dumper", "bus breakdown", "truck breakdown", "vehicle due to"]):
        return "Vehicle Breakdown"
    elif any(k in text for k in ["accident", "collision", "hit", "mishap", "injured"]):
        return "Accident"
    elif any(k in text for k in ["fire", "smoke"]):
        return "Fire Hazard"
    elif any(k in text for k in ["waterlogging", "flooding", "water logged", "subway closed", "heavy rain"]):
        return "Monsoon Waterlogging"
    elif any(k in text for k in ["vip", "vvip", "movement", "bandobast", "convoy", "security"]):
        return "VIP / Security Movement"
    elif any(k in text for k in ["metro work", "road work", "construction", "pothole", "piling work", "repair"]):
        return "Infrastructure / Road Work"
    elif any(k in text for k in ["slow movement", "heavy traffic", "congestion", "sluggish", "jam"]):
        return "General Congestion"
    else:
        return "General Traffic Alert"

def extract_mumbai_region(text):
    text = str(text)
    regions_map = {
        "Western Express Highway|weh|andheri|jogeshwari|borivali|bandra|santacruz|malad|goregaon|dahisar|vile parle|sahar|kupar": "Western Suburbs (WEH Axis)",
        "Eastern Express Highway|eeh|ghatkopar|vikhroli|mulund|bhandup|kurla|sion|chembur|kanjurmarg|vashi": "Eastern Suburbs (EEH Axis)",
        "jvlr|jogeshwari vikhroli link road|powai|seepz|gandhi nagar": "JVLR Corridor",
        "dadar|parel|byculla|cst|colaba|worli|prabhadevi|mahim|churchgate|mumbai central": "South Mumbai",
        "sakinaka|marol|lonavala|thane|navi mumbai|asalpha|kalwa|mumbra|panvel|mankhurd": "Extended Suburbs / Outskirts",
        "bkc|bandra kurla complex": "BKC Business District"
    }
    for pattern, region_name in regions_map.items():
        if re.search(pattern, text, re.IGNORECASE):
            return region_name
    return "Other Landmark"

def process_traffic_data():
    csv_path = Path("data/raw/mumbai_traffic_tweets.csv")
    output_path = Path("data/raw/mumbai_traffic_processed.csv")
    
    if not csv_path.exists():
        print("❌ Dataset missing. Please download the 1,000-item filtered CSV file first.")
        return
        
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['text'])
    
    # 🔥 PANDAS FILTER: Drop citizen replies starting with @ or standard template phrases
    df = df[~df['text'].str.startswith('@', na=False)]
    df = df[~df['text'].str.lower().str.contains("thanks for bringing this to our notice", na=False)]
    
    # Process dataset
    df['Traffic_Reason'] = df['text'].apply(categorize_incident)
    df['Mumbai_Region'] = df['text'].apply(extract_mumbai_region)
    
    # Save results
    df.to_csv(output_path, index=False)
    print(f"🎉 Analysis Complete! Data processed and saved to: {output_path}")
    print(f"📊 Actual Broadcast Rows Parsed: {len(df)}")
    print("\n🔍 Top Traffic Causes Detected:")
    print(df['Traffic_Reason'].value_counts())
    print("\n📍 Most Congested Operational Zones:")
    print(df['Mumbai_Region'].value_counts())

if __name__ == "__main__":
    process_traffic_data()