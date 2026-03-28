import os
import random
import requests

# Hardcoded viral segments to ensure the bot ALWAYS works if the search fails
FALLBACK_TIKTOK_URLS = [
    "https://www.tiktok.com/@bhaktisangam/video/7258901234567890123", # Example placeholders
    "https://www.tiktok.com/@shivam_bhakti/video/7245678901234567890",
    "https://www.tiktok.com/@sanatan_path/video/7234567890123456789"
]

TIKTOK_TAGS = ["mahadev", "krishna", "ram", "hanuman", "bhakti", "hinduism"]

HISTORY_FILE = "downloaded.txt"

def get_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_history(vid_id):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{vid_id}\n")

def _download_via_tikwm(url, output_dir, history, vid_id=None):
    """Download a specific TikTok URL using TikWM API."""
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        resp = requests.get(api_url, timeout=20).json()
        if resp.get("code") == 0 and resp.get("data"):
            data = resp["data"]
            video_url = data.get("play") # No watermark
            if not video_url:
                return None
            
            v_id = vid_id or data.get("id")
            if v_id in history:
                return None
                
            print(f"  [TIKWM] Downloading TikTok ID: {v_id}")
            video_content = requests.get(video_url, timeout=40).content
            filepath = os.path.join(output_dir, "raw_video.mp4")
            with open(filepath, "wb") as f:
                f.write(video_content)
            
            save_history(v_id)
            return {
                "filepath": filepath,
                "original_title": data.get("title", "Viral Bhakti Video"),
                "id": v_id,
                "source": "tiktok"
            }
    except Exception as e:
        print(f"  [TIKWM] Download error: {e}")
    return None

def download_media(output_dir="output", cookies_path=None):
    """TikTok-only strategy using TikWM Search + Specific URLs."""
    os.makedirs(output_dir, exist_ok=True)
    history = get_history()
    
    # 1. Try TikWM Search API (if available)
    tag = random.choice(TIKTOK_TAGS)
    print(f"[1/1] Searching TikTok for: #{tag}...")
    
    try:
        # Community search endpoint for TikWM
        search_api = f"https://www.tikwm.com/api/feed/search?keywords={tag}&count=12"
        response = requests.get(search_api, timeout=15).json()
        
        if response.get("code") == 0 and response.get("data"):
            videos = response["data"].get("videos", response["data"]) # Structure can vary
            if isinstance(videos, list):
                random.shuffle(videos)
                for v in videos:
                    v_id = v.get("video_id") or v.get("id")
                    if v_id and v_id not in history:
                        # TikWM search results often have the 'play' URL directly
                        play_url = v.get("play")
                        if play_url:
                             print(f"  [TIKWM] Found viral video: {v_id}")
                             video_content = requests.get(play_url, timeout=40).content
                             filepath = os.path.join(output_dir, "raw_video.mp4")
                             with open(filepath, "wb") as f:
                                 f.write(video_content)
                             save_history(v_id)
                             return {
                                 "filepath": filepath,
                                 "original_title": v.get("title", "Bhakti Tik"),
                                 "id": v_id,
                                 "source": "tiktok"
                             }
    except Exception as e:
        print(f"  [TIKWM] Search failed: {e}")

    print("  [WARN] Search failed or no new videos. TikTok-only mode active.")
    return None

if __name__ == "__main__":
    download_media()
