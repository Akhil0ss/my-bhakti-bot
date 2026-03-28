import os
import yt_dlp
import random
import requests

TIKTOK_TAGS = [
    "https://www.tiktok.com/tag/mahadevstatus",
    "https://www.tiktok.com/tag/krishnabhajan",
    "https://www.tiktok.com/tag/rammandir",
    "https://www.tiktok.com/tag/hanumanchalisa"
]

YOUTUBE_TAGS = [
    "bhakti status shorts",
    "krishna clips shorts",
    "mahakal status shorts",
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

def _download_tiktok_alt(tag_url, output_dir, history):
    """Fallback: Try to get a TikTok video via a public API to bypass cloud blocks."""
    print("  [INFO] Trying TikWM API Fallback for TikTok...")
    try:
        # Extract tag name
        tag = tag_url.split("/")[-1]
        api_url = f"https://www.tikwm.com/api/feed/list?keywords={tag}&count=10"
        resp = requests.get(api_url, timeout=15).json()
        
        if resp.get("code") == 0 and resp.get("data"):
            videos = resp["data"]
            random.shuffle(videos)
            for v in videos:
                v_id = v.get("video_id")
                if v_id and v_id not in history:
                    dl_url = v.get("play") # No watermark URL
                    if dl_url:
                        fpath = os.path.join(output_dir, "raw_video.mp4")
                        v_data = requests.get(dl_url).content
                        with open(fpath, "wb") as f:
                            f.write(v_data)
                        save_history(v_id)
                        return {"filepath": fpath, "original_title": v.get("title", "Bhakti"), "id": v_id}
    except Exception as e:
        print(f"  [WARN] TikTok Alt API failed: {e}")
    return None

def _download_with_ytdlp(url, output_dir, history, is_search=False, cookies_path=None):
    """Download with the most compatible settings possible."""
    
    # Use the most basic 'best' format to avoid 'format not available' errors on cloud
    # We prefer MP4 for compatibility
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best[ext=mp4]/best',
        'socket_timeout': 30,
        'extractor_args': {'youtube': {'client': ['android', 'web']}}
    }

    if cookies_path and os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Flatten to find a unique one
            search_opts = {**ydl_opts, 'extract_flat': True, 'playlist_end': 10}
            with yt_dlp.YoutubeDL(search_opts) as ydl_s:
                info = ydl_s.extract_info(url, download=False)
            
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
            
            if not selected: return None

            v_url = selected.get('url') or selected.get('webpage_url') or f"https://www.youtube.com/watch?v={selected['id']}"
            print(f"  [YT-DLP] Downloading ID: {selected['id']}...")
            
            output_template = os.path.join(output_dir, "raw_video.%(ext)s")
            ydl_opts['outtmpl'] = output_template
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl_dl:
                dl_info = ydl_dl.extract_info(v_url, download=True)
                filename = ydl_dl.prepare_filename(dl_info)
                save_history(selected['id'])
                return {"filepath": filename, "original_title": dl_info.get('title', 'Bhakti'), "id": selected['id']}
        except Exception as e:
            print(f"  [ERROR] YT-DLP failed: {e}")
            return None

def download_media(output_dir="output", cookies_path=None):
    os.makedirs(output_dir, exist_ok=True)
    history = get_history()

    # 1. TikTok Tag
    print("[1/3] Scouring TikTok...")
    tag_url = random.choice(TIKTOK_TAGS)
    res = _download_with_ytdlp(tag_url, output_dir, history, cookies_path=cookies_path)
    if res: return res
    
    # 1.1 TikTok Alt API (Bypass)
    res = _download_tiktok_alt(tag_url, output_dir, history)
    if res: return res

    # 2. Instagram Fallback (Often blocked on Cloud, so we move fast to Failsafe)
    print("[2/3] Checking Fallbacks...")
    
    # 3. Final Fail-Safe: YouTube Search (Most Reliable)
    print("[3/3] Final Fail-Safe: YouTube Search...")
    query = random.choice(YOUTUBE_TAGS)
    return _download_with_ytdlp(f"ytsearch15:{query}", output_dir, history, is_search=True, cookies_path=cookies_path)

if __name__ == "__main__":
    download_media()
