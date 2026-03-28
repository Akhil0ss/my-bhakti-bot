import os
import requests
import random
from dotenv import load_dotenv

load_dotenv()

def fetch_videos(query, count=5, output_dir="output"):
    """Fetches portrait videos from Pexels API."""
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        raise ValueError("PEXELS_API_KEY not found in .env file!")

    clips_dir = os.path.join(output_dir, "clips")
    os.makedirs(clips_dir, exist_ok=True)
    
    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "per_page": min(count * 3, 30),
        "orientation": "portrait",
    }
    
    print(f"  Search term: '{query}'")
    resp = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()

    videos = data.get("videos", [])
    if not videos:
        print("  [WARN] No videos found for query. Switching to default: 'nature cinema'")
        return fetch_videos("nature cinema", count, output_dir)
        
    random.shuffle(videos)
    downloaded = []

    for i, video in enumerate(videos[:count]):
        # Find the best portrait file
        files = video.get("video_files", [])
        best_file = None
        for f in files:
            w, h = f.get("width", 0), f.get("height", 0)
            if h >= w and h >= 720:  # Priority to HD portrait
                if not best_file or h > best_file.get("height", 0):
                    best_file = f
                    
        if not best_file and files:
            best_file = files[0]  # Fallback to whatever is available
            
        if not best_file:
            continue

        url = best_file["link"]
        clip_path = os.path.join(clips_dir, f"clip_{i}.mp4")
        
        print(f"  Downloading clip {i+1}/{count}...")
        try:
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()
            with open(clip_path, "wb") as out:
                for chunk in r.iter_content(chunk_size=8192):
                    out.write(chunk)
            downloaded.append(clip_path)
        except Exception as e:
            print(f"  [ERROR] Failed to download clip: {e}")

    print(f"  [OK] {len(downloaded)} clips downloaded successfully.")
    return downloaded

if __name__ == "__main__":
    clips = fetch_videos("space facts cinematic", count=3)
    print(clips)
