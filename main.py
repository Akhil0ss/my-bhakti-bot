import os
import argparse
import sys
from engine.media_scraper import download_media
from engine.script_generator import generate_rewrite_and_quote
from engine.video_renderer import trim_video
from engine.youtube_uploader import upload_video

OUTPUT_DIR = "output"

def run(no_upload=False):
    print("==================================================")
    print("  AURA REPURPOSE ENGINE - Starting Pipeline")
    print("==================================================\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 1: Scrape Viral Video
    print("[1/4] Scraping viral clip...")
    scraped_data = download_media(output_dir=OUTPUT_DIR)
    if not scraped_data or not scraped_data.get("filepath"):
        print("  [FATAL] Failed to scrape video. Exiting.")
        sys.exit(1)
        
    raw_video = scraped_data["filepath"]
    original_title = scraped_data["original_title"]

    # Step 2: Generate SEO Title & Tags
    print("\n[2/4] Generating SEO Title & Tags via Gemini...")
    script_data = generate_rewrite_and_quote(original_title)
    print(f"  Title: {script_data['title']}")

    # Step 3: Trim Video to 15-30s (No edits, original quality)
    print("\n[3/4] Trimming video to Shorts length...")
    final_video = trim_video(
        raw_video_path=raw_video,
        output_dir=OUTPUT_DIR
    )

    # Step 4: Upload and Cleanup
    print("\n[4/4] Uploading to YouTube Shorts & Cleaning Up...")
    if no_upload:
        print(f"  [SKIP] Upload skipped. Video saved at: {final_video}")
    else:
        try:
            video_url = upload_video(
                video_path=final_video,
                title=script_data['title'],
                description=script_data['description'],
                tags_str=script_data['tags']
            )
            print(f"  [SUCCESS] VIDEO LIVE: {video_url}")
        except Exception as e:
            print(f"  [ERROR] Upload failed: {e}")

    print("\n[INFO] Cleaning up downloaded storage...")
    try:
        if os.path.exists(raw_video):
            os.remove(raw_video)
        if not no_upload and os.path.exists(final_video):
            os.remove(final_video)
        print("  [OK] Deleted scraped and temporary files!")
    except Exception as cleanup_err:
        print(f"  [WARN] Cleanup failed: {cleanup_err}")

    print("\n==================================================")
    print("  PIPELINE COMPLETE!")
    print("==================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aura YouTube Shorts Repurposer")
    parser.add_argument("--no-upload", action="store_true", help="Skip YouTube upload step")
    args = parser.parse_args()
    
    run(no_upload=args.no_upload)
