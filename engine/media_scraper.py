import os
import random
import requests

# Hardcoded viral segments to ensure the bot ALWAYS works if the search fails
FALLBACK_TIKTOK_URLS = [
    "https://www.tiktok.com/@bhaktisangam/video/7258901234567890123", # Example placeholders
    "https://www.tiktok.com/@shivam_bhakti/video/7245678901234567890",
    "https://www.tiktok.com/@sanatan_path/video/7234567890123456789"
]

# Updated for AI-Cinematic Content only
TIKTOK_KEYWORDS = [
    "Hindu God AI Animation", 
    "Mahadev 3D Cinematic", 
    "Lord Krishna AI Divine",
    "Sanatan Dharma AI Art",
    "Lord Ram 4K Cinematic AI",
    "Hanuman 3D Animation"
]

# Filtering thresholds for Quality Control
MIN_LIKES = 1000
MIN_VIEWS = 10000

# Exclude narrated / vlog style content
BLACKLIST_KEYWORDS = ["vlog", "podcast", "interview", "talking", "narrated", "reaction", "review", "story", "fact"]

HISTORY_FILE = "downloaded.txt"

def get_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_history(vid_id):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{vid_id}\n")

def download_media(output_dir="output", cookies_path=None):
    """AI-First TikTok strategy focusing only on high-engagement cinematic clips."""
    os.makedirs(output_dir, exist_ok=True)
    history = get_history()
    
    # Select a high-quality keyword
    keyword = random.choice(TIKTOK_KEYWORDS)
    print(f"  [TIKWM] Searching for high-quality AI content: \"{keyword}\"...")
    
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

            for v in videos:
                v_id = v.get("video_id") or v.get("id")
                title = v.get("title", "").lower()
                likes = int(v.get("digg_count", 0))
                views = int(v.get("play_count", 0))
                
                # 1. Deduplication check
                if not v_id or v_id in history:
                    continue
                
                # 2. Blacklist check (No narrators/vlogs)
                is_blacklisted = any(word in title for word in BLACKLIST_KEYWORDS)
                if is_blacklisted:
                    continue
                
                # 3. High Engagement check
                if likes < MIN_LIKES or views < MIN_VIEWS:
                    continue
                
                # 4. Final attempt to download 'No Watermark' version
                play_url = v.get("play")
                if play_url:
                    print(f"  [OK] Found high-engagement AI video: {v_id} (Likes: {likes}, Views: {views})")
                    video_content = requests.get(play_url, timeout=40).content
                    filepath = os.path.join(output_dir, "raw_video.mp4")
                    with open(filepath, "wb") as f:
                        f.write(video_content)
                    
                    save_history(v_id)
                    return {
                        "filepath": filepath,
                        "original_title": v.get("title", "Cinematic Bhakti"),
                        "id": v_id,
                        "source": "tiktok"
                    }
    except Exception as e:
        print(f"  [TIKWM] Search/Download failed: {e}")

    print("  [FAIL] Could not find a fresh high-quality AI video. Retrying later.")
    return None

if __name__ == "__main__":
    download_media()
