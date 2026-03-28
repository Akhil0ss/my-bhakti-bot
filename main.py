import os
import argparse
import sys
from engine.media_scraper import download_media
from engine.script_generator import generate_rewrite_and_quote
from engine.video_renderer import trim_video
from engine.youtube_uploader import upload_video

OUTPUT_DIR = "output"

def run(no_upload=False, cookies_path=None):
    print("==================================================")
    print("  AURA REPURPOSE ENGINE - TikTok Only Mode")
    print("==================================================\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 1: Scrape Viral Video (TikTok Only)
    print("[1/3] Scraping viral TikTok clip...")
    scraped_data = download_media(output_dir=OUTPUT_DIR, cookies_path=cookies_path)
    if not scraped_data or not scraped_data.get("filepath"):
        print("  [FATAL] Failed to scrape TikTok video. Exiting.")
        sys.exit(1)
        
    raw_video = scraped_data["filepath"]
    original_title = scraped_data["original_title"]

    # Step 2: Generate SEO Title & Tags
    print("\n[2/3] Generating SEO Title & Tags via Gemini...")
    script_data = generate_rewrite_and_quote(original_title)
    print(f"  Title: {script_data['title']}")

    # Step 3: Trim Video
    print("\n[3/3] Trimming video to Shorts length...")
    final_video_path = os.path.join(OUTPUT_DIR, "final_shorts.mp4")
    final_video = trim_video(
        input_path=raw_video,
        output_path=final_video_path
    )

    if not final_video:
        print("  [FATAL] Rendering failed. Exiting.")
        sys.exit(1)

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

    print("\n[INFO] Cleaning up storage...")
    try:
        if os.path.exists(raw_video):
            os.remove(raw_video)
        # Note: final_video is cleaned up only if not skipping upload
        if not no_upload and os.path.exists(final_video):
            os.remove(final_video)
        print("  [OK] Storage cleared!")
    except Exception as cleanup_err:
        print(f"  [WARN] Cleanup failed: {cleanup_err}")

    print("\n==================================================")
    print("  PIPELINE COMPLETE!")
    print("==================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aura YouTube Shorts Repurposer")
    parser.add_argument("--no-upload", action="store_true", help="Skip YouTube upload step")
    parser.add_argument("--cookies", type=str, help="Path to cookies file")
    args = parser.parse_args()
    
    run(no_upload=args.no_upload, cookies_path=args.cookies)
