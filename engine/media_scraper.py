import os
import random
import requests

def get_history(history_file):
    if not os.path.exists(history_file):
        return set()
    with open(history_file, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_history(vid_id, history_file):
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(f"{vid_id}\n")

def download_media(config, output_dir="output", cookies_path=None):
    """AI-First TikTok strategy using niche-specific configuration."""
    os.makedirs(output_dir, exist_ok=True)
    history_file = config.get("history_file", "downloaded.txt")
    history = get_history(history_file)
    
    # Select a high-quality keyword from niche config
    keywords = config.get("keywords", [])
    if not keywords:
        print("  [ERROR] No keywords found in niche config.")
        return None
        
    keyword = random.choice(keywords)
    print(f"  [TIKWM] Searching for \"{keyword}\"...")
    
    try:
        # TikWM search endpoint
        search_api = f"https://www.tikwm.com/api/feed/search?keywords={keyword}&count=20"
        response = requests.get(search_api, timeout=15).json()
        
        if response.get("code") == 0 and response.get("data"):
            videos = response["data"].get("videos", [])
            if not videos:
                print("  [WARN] No videos found for this keyword.")
                return None
                
            # Randomize to get fresh content every time
            random.shuffle(videos)

            # Quality thresholds from config
            min_likes = config.get("min_likes", 500)
            min_views = config.get("min_views", 5000)
            blacklist = config.get("blacklist", [])

            for v in videos:
                v_id = v.get("video_id") or v.get("id")
                title = v.get("title", "").lower()
                likes = int(v.get("digg_count", 0))
                views = int(v.get("play_count", 0))
                
                # 1. Deduplication check
                if not v_id or v_id in history:
                    continue
                
                # 2. Blacklist check (No narrators/vlogs/faces)
                is_blacklisted = any(word in title for word in blacklist)
                if is_blacklisted:
                    continue
                
                # 3. High Engagement check
                if likes < min_likes or views < min_views:
                    continue
                
                # 4. Final attempt to download 'No Watermark' version
                play_url = v.get("play")
                if play_url:
                    print(f"  [OK] Found high-engagement video: {v_id} (Likes: {likes}, Views: {views})")
                    video_content = requests.get(play_url, timeout=40).content
                    filepath = os.path.join(output_dir, "raw_video.mp4")
                    with open(filepath, "wb") as f:
                        f.write(video_content)
                    
                    save_history(v_id, history_file)
                    return {
                        "filepath": filepath,
                        "original_title": v.get("title", "Cinematic Video"),
                        "id": v_id,
                        "source": "tiktok"
                    }
    except Exception as e:
        print(f"  [TIKWM] Search/Download failed: {e}")

    print("  [FAIL] Could not find a fresh high-quality video in this niche. Retrying later.")
    return None

if __name__ == "__main__":
    download_media()
