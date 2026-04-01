import os
import argparse
import sys
from dotenv import load_dotenv
from engine.media_scraper import download_media
from engine.script_generator import generate_rewrite_and_quote
from engine.video_renderer import trim_video
from engine.youtube_uploader import upload_video
from engine.niche_config import get_config

OUTPUT_DIR = "output"

def run(niche_name, no_upload=False, cookies_path=None):
    load_dotenv()

    # Load niche configuration
    config = get_config(niche_name)
    
    print("==================================================")
    print(f"  AURA ENGINE - {niche_name.upper()} Mode")
    print("==================================================\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 1: Scrape Viral Video
    print(f"[1/4] Scraping viral {niche_name} clip...")
    scraped_data = download_media(config=config, output_dir=OUTPUT_DIR, cookies_path=cookies_path)
    if not scraped_data or not scraped_data.get("filepath"):
        print(f"  [FATAL] Failed to scrape {niche_name} video. Exiting.")
        sys.exit(1)
        
    raw_video = scraped_data["filepath"]
    original_title = scraped_data["original_title"]

    # Step 2: Generate SEO Title & Tags
    print("\n[2/4] Generating SEO Title & Tags via Gemini...")
    script_data = generate_rewrite_and_quote(original_title, config=config)
    print(f"  Title: {script_data['title']}")

    # Step 3: Trim Video
    print("\n[3/4] Trimming video via Smart Hook peak detection...")
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
            # Pass niche-specific token file to uploader
            video_url = upload_video(
                video_path=final_video,
                title=script_data['title'],
                description=script_data['description'],
                tags_str=script_data['tags'],
                token_file=config["token_file"],
                token_secret_env=config.get("token_secret")
            )
            if video_url:
                print(f"  [SUCCESS] VIDEO LIVE: {video_url}")
            else:
                print("  [ERROR] Upload did not complete. No video ID returned.")
        except Exception as e:
            print(f"  [ERROR] Upload failed: {e}")

    print("\n[INFO] Cleaning up storage...")
    try:
        if os.path.exists(raw_video):
            os.remove(raw_video)
        if not no_upload and os.path.exists(final_video):
            os.remove(final_video)
        print("  [OK] Storage cleared!")
    except Exception as cleanup_err:
        print(f"  [WARN] Cleanup failed: {cleanup_err}")

    print("\n==================================================")
    print(f"  PIPELINE COMPLETE ({niche_name})")
    print("==================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aura Multi-Channel YouTube Automation")
    parser.add_argument("--niche", type=str, default="bhakti", help="Niche to run (bhakti, akonymous)")
    parser.add_argument("--no-upload", action="store_true", help="Skip YouTube upload step")
    parser.add_argument("--cookies", type=str, help="Path to cookies file")
    args = parser.parse_args()
    
    run(niche_name=args.niche, no_upload=args.no_upload, cookies_path=args.cookies)
