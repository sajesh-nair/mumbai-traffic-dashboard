# src/nlp/fetch_tweets.py
import json
import pandas as pd
from pathlib import Path

def extract_tweets_omni(data):
    """Scans the entire JSON tree to cleanly parse standard and nested tweet structures."""
    extracted = []
    
    if isinstance(data, dict):
        # Format A: Standard direct layout
        if 'full_text' in data and 'created_at' in data and 'id_str' in data:
            extracted.append({
                'id': str(data['id_str']),
                'url': f"https://x.com/MTPHereToHelp/status/{data['id_str']}",
                'text': data['full_text'],
                'createdAt': data['created_at'],
                'retweetCount': data.get('retweet_count', 0),
                'replyCount': data.get('reply_count', 0),
                'likeCount': data.get('favorite_count', 0),
                'quoteCount': data.get('quote_count', 0),
                'isRetweet': 'retweeted_status' in data,
                'isQuote': data.get('is_quote_status', False)
            })
        # Format B: Deep GraphQL block containing inner tweet/legacy mapping
        elif 'tweet_results' in data and isinstance(data['tweet_results'], dict):
            res = data['tweet_results'].get('result', {})
            if res:
                # Resolve potential 'tweet' layer nests
                core_data = res.get('tweet', res) if 'tweet' in res else res
                legacy = core_data.get('legacy')
                rest_id = core_data.get('rest_id')
                
                if legacy and rest_id and 'full_text' in legacy:
                    extracted.append({
                        'id': str(rest_id),
                        'url': f"https://x.com/MTPHereToHelp/status/{rest_id}",
                        'text': legacy['full_text'],
                        'createdAt': legacy.get('created_at'),
                        'retweetCount': legacy.get('retweet_count', 0),
                        'replyCount': legacy.get('reply_count', 0),
                        'likeCount': legacy.get('favorite_count', 0),
                        'quoteCount': legacy.get('quote_count', 0),
                        'isRetweet': 'retweeted_status' in legacy,
                        'isQuote': legacy.get('is_quote_status', False)
                    })
                    
        for value in data.values():
            if isinstance(value, (dict, list)):
                extracted.extend(extract_tweets_omni(value))
                
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                extracted.extend(extract_tweets_omni(item))
            
    return extracted

def parse_local_json(reset_data=False):
    print("🚀 Running robust multi-schema profile parser...")
    
    json_path = Path("data/raw/mumbai_tweets_raw.json")
    output_path = Path("data/raw/mumbai_traffic_tweets.csv")
    
    if not json_path.exists() or json_path.stat().st_size == 0:
        print(f"❌ Raw JSON file is empty or missing at: {json_path}")
        return
        
    with open(json_path, "r", encoding="utf-8") as f:
        try:
            raw_data = json.load(f)
        except Exception as e:
            print(f"❌ Failed to read JSON file: {str(e)}")
            return

    discovered_tweets = extract_tweets_omni(raw_data)
    
    new_tweets = []
    seen_ids = set()
    for t in discovered_tweets:
        if not t['text'] or t['id'] in seen_ids:
            continue
        seen_ids.add(t['id'])
        new_tweets.append(t)

    if reset_data or not output_path.exists() or output_path.stat().st_size == 0:
        existing_df = pd.DataFrame()
        print("🧽 Clean Slate Mode: Building a fresh timeline dataset.")
    else:
        try:
            existing_df = pd.read_csv(output_path)
            if 'id' in existing_df.columns:
                existing_df['id'] = existing_df['id'].astype(str)
        except Exception:
            existing_df = pd.DataFrame()

    if new_tweets:
        new_df = pd.DataFrame(new_tweets)
        new_df['id'] = new_df['id'].astype(str)
        
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        final_df = combined_df.drop_duplicates(subset=['id'], keep='first')
        
        final_df = final_df[~final_df['createdAt'].str.contains('May', na=False, case=False)]
        final_df = final_df.sort_values(by='id', ascending=False)
    else:
        final_df = existing_df

    if final_df.empty:
        print("⚠️ No data compiled. Try grabbing a fresh large payload from the profile tab.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)
    
    print("-" * 60)
    print(f"📥 Processed this packet. Extracted {len(new_tweets)} total updates.")
    print(f"📊 RUNNING TOTAL DATASET COUNT: {len(final_df)} / 250 TWEETS")
    print("-" * 60)

if __name__ == "__main__":
    # Keeping it as False so you can stack new chunks cleanly!
    parse_local_json(reset_data=False)