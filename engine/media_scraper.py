import os
import yt_dlp
import random

TIKTOK_TAGS = [
    "https://www.tiktok.com/tag/mahadevstatus",
    "https://www.tiktok.com/tag/krishnabhajan",
    "https://www.tiktok.com/tag/rammandir",
    "https://www.tiktok.com/tag/hanumanchalisa",
    "https://www.tiktok.com/tag/sanatandharma"
]

INSTA_TAGS = [
    "https://www.instagram.com/explore/tags/bhaktireels/",
    "https://www.instagram.com/explore/tags/mahadevstatus/",
    "https://www.instagram.com/explore/tags/krishnavani/",
    "https://www.instagram.com/explore/tags/jaishreeram/"
]

YOUTUBE_TAGS = [
    "bhakti status short",
    "krishna mahadev shorts",
    "hinduism viral reels",
    "sanatan dharma status"
]

HISTORY_FILE = "downloaded.txt"

def get_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_history(vid_id):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{vid_id}\n")

def _download_with_ytdlp(url, output_dir, history, is_search=False):
    """Internal helper to download 1 random NEW video from a playlist/tag URL or search query."""
    ydl_opts_extract = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
        'playlist_end': 20, 
        'extractor_args': {'tiktok': {'api_hostname': 'api16-normal-c-useast1a.tiktokv.com'}}
    }
    
    with yt_dlp.YoutubeDL(ydl_opts_extract) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"  [ERROR] Extraction failed for {url}: {e}")
            return None
            
        if 'entries' not in info or not info['entries']:
            return None
        
        entries = list(info['entries'])
        random.shuffle(entries)
        
        selected = None
        for entry in entries:
            v_id = entry.get('id')
            if v_id and v_id not in history:
                selected = entry
                break
        
        if not selected:
            print(f"  [INFO] No new videos found in {url}")
            return None
            
        v_url = selected.get('url') or selected.get('webpage_url')
        if not v_url and selected.get('id'):
            if "tiktok" in url:
                v_url = f"https://www.tiktok.com/video/{selected['id']}"
            elif "instagram" in url:
                v_url = f"https://www.instagram.com/reels/{selected['id']}/"
            elif is_search:
                v_url = f"https://www.youtube.com/watch?v={selected['id']}"

        v_id = selected['id']
        print(f"  [YT-DLP] Selected UNIQUE video ID: {v_id}...")
        
        output_template = os.path.join(output_dir, "raw_video.%(ext)s")
        ydl_opts_dl = {
            'format': 'best', # Pre-merged for quality & speed
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'tiktok': {'api_hostname': 'api16-normal-c-useast1a.tiktokv.com'}}
        }
        
        with yt_dlp.YoutubeDL(ydl_opts_dl) as ydl_dl:
            dl_info = ydl_dl.extract_info(v_url, download=True)
            filename = ydl_dl.prepare_filename(dl_info)
            
            # Save history
            save_history(v_id)
            
            if not os.path.exists(filename):
                for f in os.listdir(output_dir):
                    if f.startswith("raw_video"):
                        filename = os.path.join(output_dir, f)
                        break
            
            return {
                "filepath": filename,
                "original_title": dl_info.get('title', 'Bhakti Status'),
                "id": v_id
            }

def download_media(output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    history = get_history()

    # --- PRIMARY: TIKTOK ---
    print("[1/2] Attempting TikTok Scrape (Primary)...")
    tiktok_url = random.choice(TIKTOK_TAGS)
    try:
        result = _download_with_ytdlp(tiktok_url, output_dir, history)
        if result:
            print(f"  [OK] TikTok video downloaded: {result['id']}")
            return result
    except Exception as e:
        print(f"  [WARN] TikTok attempt failed: {e}")

    # --- FALLBACK: INSTAGRAM ---
    print("[2/2] Attempting Instagram Scrape (Fallback)...")
    insta_url = random.choice(INSTA_TAGS)
    try:
        result = _download_with_ytdlp(insta_url, output_dir, history)
        if result:
            print(f"  [OK] Instagram video downloaded: {result['id']}")
            return result
    except Exception as e:
        print(f"  [WARN] Instagram attempt failed: {e}")

    # --- FINAL FAILSAFE: YOUTUBE SEARCH ---
    print("[Final Failsafe] Attempting YouTube Search...")
    query = random.choice(YOUTUBE_TAGS)
    try:
        result = _download_with_ytdlp(f"ytsearch20:{query}", output_dir, history, is_search=True)
        if result:
            print(f"  [OK] YouTube video downloaded: {result['id']}")
            return result
    except Exception as e:
        print(f"  [ERROR] All sources failed: {e}")
        return None

if __name__ == "__main__":
    download_media()
