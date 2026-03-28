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
    "bhakti status shorts",
    "krishna mahadev shorts",
    "hinduism viral reels",
    "sanatan dharma status video"
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

def _download_with_ytdlp(url, output_dir, history, is_search=False, cookies_path=None):
    """Internal helper to download 1 random NEW video with ROBUST format selection."""
    
    # MOBILE CLIENT Spoofing for better bypass
    extractor_args = {
        'youtube': {'client': ['android', 'ios', 'web']},
        'tiktok': {'api_hostname': 'api16-normal-c-useast1a.tiktokv.com'}
    }

    # Best MP4 format selection (Most compatible for cloud/ffmpeg)
    # bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best
    format_selector = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

    ydl_opts_base = {
        'quiet': True,
        'no_warnings': True,
        'format': format_selector,
        'extractor_args': extractor_args,
        'socket_timeout': 30, # Handle cloud network jitters
    }

    if cookies_path and os.path.exists(cookies_path):
        ydl_opts_base['cookiefile'] = cookies_path

    ydl_opts_extract = {
        **ydl_opts_base,
        'extract_flat': True,
        'playlist_end': 15, 
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
            return None
            
        v_url = selected.get('url') or selected.get('webpage_url')
        if not v_url and selected.get('id'):
            if "tiktok" in url:
                v_url = f"https://www.tiktok.com/video/{selected['id']}"
            elif "instagram" in url:
                v_url = f"https://www.instagram.com/reels/{selected['id']}/"
            elif is_search:
                v_url = f"https://www.youtube.com/watch?v={selected['id']}"

        if not v_url: return None

        print(f"  [YT-DLP] Selected UNIQUE video ID: {selected['id']}. Downloading...")
        
        output_template = os.path.join(output_dir, "raw_video.%(ext)s")
        ydl_opts_dl = {
            **ydl_opts_base,
            'outtmpl': output_template,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts_dl) as ydl_dl:
            dl_info = ydl_dl.extract_info(v_url, download=True)
            filename = ydl_dl.prepare_filename(dl_info)
            
            # Save history
            save_history(selected['id'])
            
            if not os.path.exists(filename):
                for f in os.listdir(output_dir):
                    if f.startswith("raw_video"):
                        filename = os.path.join(output_dir, f)
                        break
            
            return {
                "filepath": filename,
                "original_title": dl_info.get('title', 'Bhakti Status'),
                "id": selected['id']
            }

def download_media(output_dir="output", cookies_path=None):
    os.makedirs(output_dir, exist_ok=True)
    history = get_history()

    # --- PRIMARY: TIKTOK (Direct URL) ---
    print("[1/3] Attempting TikTok Scrape (Primary)...")
    try:
        tiktok_url = random.choice(TIKTOK_TAGS)
        result = _download_with_ytdlp(tiktok_url, output_dir, history, cookies_path=cookies_path)
        if result: return result
    except Exception as e:
        print(f"  [WARN] TikTok Tag failed: {e}")

    # --- SECONDARY: INSTAGRAM (Direct URL) ---
    print("[2/3] Attempting Instagram Scrape (Secondary)...")
    try:
        insta_url = random.choice(INSTA_TAGS)
        result = _download_with_ytdlp(insta_url, output_dir, history, cookies_path=cookies_path)
        if result: return result
    except Exception as e:
        print(f"  [WARN] Instagram Tag failed: {e}")

    # --- FINAL FAILSAFE: YOUTUBE SEARCH & SCRAPE ---
    print("[3/3] Final Fail-Safe: YouTube Search Scrape...")
    try:
        query = random.choice(YOUTUBE_TAGS)
        result = _download_with_ytdlp(f"ytsearch20:{query}", output_dir, history, is_search=True, cookies_path=cookies_path)
        if result: return result
    except Exception as e:
        print(f"  [ERROR] All sources failed: {e}")
        return None

if __name__ == "__main__":
    download_media()
