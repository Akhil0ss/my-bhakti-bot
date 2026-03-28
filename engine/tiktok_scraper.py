import os
import yt_dlp
import random

SOURCES = [
    "bhakti status",
    "mahakal shorts",
    "krishna quotes shorts",
    "ram bhajan shorts",
    "hanuman chalisa status",
    "sanatan dharma powerful shorts",
    "hindi devotional heart touching",
    "shiva bholenath reels",
    "radhe radhe status",
    "hinduism motivational shorts",
    "bhakti mantra status",
    "jaishreeram whatsapp status"
]

HISTORY_FILE = "downloaded.txt"

def get_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_history(vid_id):
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{vid_id}\n")

def download_tiktok_video(url=None, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    history = get_history()
    
    # Randomly pick a search query from our viral sources
    query = random.choice(SOURCES)
    print(f"  [INFO] Searching for BRAND NEW Bhakti content: {query}")

    output_template = os.path.join(output_dir, "raw_video.%(ext)s")
    
    # We will search for 20 videos and pick the best NEW one
    # This ensures we don't pick the same top video repeatedly
    ydl_opts = {
        'format': 'best', # Pre-merged for speed & avoiding ffmpeg errors
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True, # Only get info first to check history
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Step 1: Search for 20 videos
            # Use 'ytsearch20:' to get a list of results
            search_results = ydl.extract_info(f"ytsearch20:{query}", download=False)
            
            if 'entries' not in search_results or not search_results['entries']:
                raise RuntimeError("No search results found")

            entries = search_results['entries']
            random.shuffle(entries) # Randomize so it's not always the top ranking one
            
            selected_video = None
            for entry in entries:
                vid_id = entry.get('id')
                if vid_id and vid_id not in history:
                    selected_video = entry
                    break
            
            if not selected_video:
                print("  [WARN] All 20 results in this search were already downloaded. Picking first available at random.")
                selected_video = random.choice(entries)
            
            vid_id = selected_video['id']
            vid_url = selected_video.get('webpage_url') or f"https://www.youtube.com/watch?v={vid_id}"
            
            print(f"  [YT-DLP] Selected NEW video ID: {vid_id}. Downloading...")
            
            # Step 2: Now download the REAL file
            # Reset options for actual download
            ydl_opts['extract_flat'] = False
            with yt_dlp.YoutubeDL(ydl_opts) as ydl_downloader:
                info = ydl_downloader.extract_info(vid_url, download=True)
                filename = ydl_downloader.prepare_filename(info)
                
                # Check extension since yt-dlp might change it
                if not os.path.exists(filename):
                    for f in os.listdir(output_dir):
                        if f.startswith("raw_video"):
                            filename = os.path.join(output_dir, f)
                            break

                # Save to history immediately
                save_history(vid_id)
                
                print(f"  [OK] Downloaded Unique Video: {filename}")
                return {
                    "filepath": filename,
                    "original_title": info.get('title', 'Bhakti Status'),
                    "original_description": info.get('description', '')
                }
                
    except Exception as e:
        print(f"  [ERROR] Scraping failed: {e}")
        return None

if __name__ == "__main__":
    download_tiktok_video()
