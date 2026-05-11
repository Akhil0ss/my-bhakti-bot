import os
import re
import random
import requests
import gdown

def extract_folder_id(link_or_id):
    """Extracts folder ID from a full Google Drive URL or returns it if it's already an ID."""
    if "drive.google.com" in link_or_id:
        match = re.search(r'folders/([a-zA-Z0-9_-]+)', link_or_id)
        return match.group(1) if match else link_or_id
    return link_or_id

def list_public_folder_files(folder_id):
    """
    Scrapes a public Google Drive folder page to find video file IDs.
    No API key or OAuth required if folder is 'Anyone with link can view'.
    """
    url = f"https://drive.google.com/drive/folders/{folder_id}"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return []
        
        # This regex looks for 33-character Google Drive file IDs commonly found in the source
        # We specifically look for .mp4 or related signatures in the proximity if possible, 
        # but a broad ID extraction followed by a check is more robust.
        ids = re.findall(r'\"([a-zA-Z0-9_-]{33})\"', response.text)
        # Filter out the folder ID itself if it's 33 chars
        ids = [fid for fid in set(ids) if fid != folder_id]
        return ids
    except Exception as e:
        print(f"  [DRIVE] Scraping error: {e}")
        return []

def download_from_drive(folder_link_or_id, output_path, history_file="download_history.txt"):
    """
    Downloads a random MP4 from a public folder that hasn't been downloaded before.
    """
    folder_id = extract_folder_id(folder_link_or_id)
    if not folder_id:
        print("  [DRIVE] Invalid Folder ID/Link.")
        return None

    print(f"  [DRIVE] Sourcing from Public Folder: {folder_id}")
    
    file_ids = list_public_folder_files(folder_id)
    if not file_ids:
        print("  [DRIVE] No files found. Ensure folder is 'Public' (Anyone with link can view).")
        return None

    # Load history
    history = []
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = f.read().splitlines()

    # Filter out seen files
    available = [fid for fid in file_ids if fid not in history]
    
    if not available:
        print("  [DRIVE] All files in this folder have been used. Picking a random one anyway.")
        available = file_ids

    selected_id = random.choice(available)
    download_url = f"https://drive.google.com/uc?id={selected_id}"
    
    try:
        # Using gdown for robust download
        gdown.download(download_url, output_path, quiet=False)
        
        if os.path.exists(output_path):
            # Save to history
            with open(history_file, 'a') as f:
                f.write(f"{selected_id}\n")
            return output_path
    except Exception as e:
        print(f"  [DRIVE] Download failed: {e}")
    
    return None
