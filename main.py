import os
import argparse
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
from engine.media_scraper import download_media
from engine.script_generator import generate_rewrite_and_quote
from engine.video_renderer import trim_video, split_video_into_parts
from engine.youtube_uploader import get_authenticated_service, upload_video
from engine.niche_config import get_config
from engine.performance_tracker import get_recommended_hours_ist, record_upload_result, sync_recent_video_stats
from engine.scheduled_queue import cleanup_missing_files, enqueue_rendered_parts, get_due_item, remove_queue_item

OUTPUT_DIR = "output"
QUEUE_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "scheduled_parts")


def _upload_with_metadata(niche_name, config, youtube, video_path, script_data, source_title, source_id="", quality_score=0.0):
    video_url = upload_video(
        video_path=video_path,
        title=script_data['title'],
        description=script_data['description'],
        tags_str=script_data['tags'],
        token_file=config["token_file"],
        token_secret_env=config.get("token_secret"),
        client_secret_file=config.get("client_secret_file", "client_secret.json"),
        default_language=config.get("default_language", "hi"),
        default_audio_language=config.get("default_audio_language", "hi"),
        pinned_comment_text=script_data.get("comment"),
        enable_pinned_comment=config.get("post_pinned_comment", False),
        youtube=youtube,
    )
    if video_url:
        print(f"  [SUCCESS] VIDEO LIVE: {video_url}")
        record_upload_result(
            niche_name,
            source_title=source_title,
            source_id=source_id,
            generated_title=script_data["title"],
            tags=script_data["tags"],
            quality_score=quality_score,
        )
    else:
        print("  [ERROR] Upload did not complete. No video ID returned.")
    return video_url

def run(niche_name, no_upload=False, cookies_path=None):
    load_dotenv()

    # Load niche configuration
    config = get_config(niche_name)
    
    print("==================================================")
    print(f"  AURA ENGINE - {niche_name.upper()} Mode")
    print("==================================================\n")
    try:
        youtube = get_authenticated_service(
            token_file=config["token_file"],
            token_secret_env=config.get("token_secret"),
            client_secret_file=config.get("client_secret_file", "client_secret.json"),
        )
        sync_recent_video_stats(niche_name, youtube)
    except Exception as analytics_err:
        print(f"  [STRATEGY] Stats sync skipped: {analytics_err}")
    recommended_hours = get_recommended_hours_ist(
        niche_name,
        default_hours=config.get("preferred_hours_ist", []),
    )
    if recommended_hours:
        print(f"  [STRATEGY] Recommended IST posting hours: {recommended_hours}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cleanup_missing_files(niche_name)

    due_item = get_due_item(niche_name, now=datetime.now(timezone.utc))
    if due_item:
        print("[0/4] Scheduled queue item is due. Priority upload will run and normal scraping will be skipped.")
        if no_upload:
            print(f"  [SKIP] Upload skipped. Queued video saved at: {due_item['video_path']}")
            return
        try:
            video_url = _upload_with_metadata(
                niche_name=niche_name,
                config=config,
                youtube=youtube,
                video_path=due_item["video_path"],
                script_data=due_item,
                source_title=due_item.get("source_title", "Scheduled Queue"),
                source_id=due_item.get("source_id", ""),
                quality_score=due_item.get("quality_score", 0.0),
            )
            if video_url:
                remove_queue_item(niche_name, due_item["queue_id"])
                if os.path.exists(due_item["video_path"]):
                    os.remove(due_item["video_path"])
            return
        except Exception as e:
            print(f"  [ERROR] Scheduled upload failed: {e}")
            return

    # Step 1: Scrape Viral Video
    print(f"[1/4] Scraping viral {niche_name} clip...")
    scraped_data = None
    if niche_name.lower() == "bhakti" and config.get("enable_segment_queue", False):
        print("  [INFO] Trying long-source queue mode for Bhakti before regular single-short mode...")
        scraped_data = download_media(
            config=config,
            output_dir=OUTPUT_DIR,
            cookies_path=cookies_path,
            min_duration_override=config.get("queue_min_source_duration", 70),
            max_duration_override=None,
            query_limit_override=config.get("queue_search_queries", 24),
        )
    if not scraped_data or not scraped_data.get("filepath"):
        scraped_data = download_media(config=config, output_dir=OUTPUT_DIR, cookies_path=cookies_path)
    if not scraped_data or not scraped_data.get("filepath"):
        print(f"  [SKIP] No usable {niche_name} video found in this run. Exiting without failure.")
        return
        
    raw_video = scraped_data["filepath"]
    original_title = scraped_data["original_title"]

    # Step 2: Generate SEO Title & Tags
    print("\n[2/4] Generating SEO Title & Tags via Gemini...")
    script_data = generate_rewrite_and_quote(original_title, config=config)
    print(f"  Title: {script_data['title']}")

    if niche_name.lower() == "bhakti" and config.get("enable_segment_queue", False) and scraped_data.get("duration", 0) >= config.get("queue_min_source_duration", 70):
        print("\n[3/4] Splitting long Bhakti source into scheduled queue parts...")
        os.makedirs(QUEUE_OUTPUT_DIR, exist_ok=True)
        queued_parts = split_video_into_parts(
            input_path=raw_video,
            output_dir=QUEUE_OUTPUT_DIR,
            part_min_duration=config.get("queue_part_min_duration", 35),
            part_max_duration=config.get("queue_part_max_duration", 40),
            min_source_duration=config.get("queue_min_source_duration", 70),
            max_parts=config.get("queue_max_parts", 3),
        )
        if queued_parts:
            first_part = queued_parts[0]
            final_video = first_part["path"]
            queued_metadata = []
            for part in queued_parts[1:]:
                part_script = generate_rewrite_and_quote(f"{original_title} Part {part['part_index']}", config=config)
                part_script["source_title"] = original_title
                part_script["source_id"] = scraped_data.get("id", "")
                part_script["quality_score"] = scraped_data.get("quality_score", 0.0)
                queued_metadata.append(part_script)
            if queued_metadata:
                enqueue_rendered_parts(
                    niche_name,
                    queued_parts[1:],
                    queued_metadata,
                    recommended_hours or config.get("preferred_hours_ist", []),
                )
                print(f"  [QUEUE] Stored {len(queued_metadata)} future Bhakti part(s) for scheduled upload.")
        else:
            print("  [INFO] Long-source queue split not available. Falling back to single-short trim.")
            final_video = None
    else:
        final_video = None

    # Step 3: Trim Video
    if not final_video:
        print("\n[3/4] Trimming video via Smart Hook peak detection...")
        final_video_path = os.path.join(OUTPUT_DIR, "final_shorts.mp4")
        final_video = trim_video(
            input_path=raw_video,
            output_path=final_video_path,
            watermark=config.get("watermark", ""),
            hook_line=script_data.get("hook_line", "")
        )

    if not final_video:
        print("  [SKIP] Rendering failed for this run. Exiting without failure.")
        return

    # Step 4: Upload and Cleanup
    print("\n[4/4] Uploading to YouTube Shorts & Cleaning Up...")
    if no_upload:
        print(f"  [SKIP] Upload skipped. Video saved at: {final_video}")
    else:
        try:
            _upload_with_metadata(
                niche_name=niche_name,
                config=config,
                youtube=youtube,
                video_path=final_video,
                script_data=script_data,
                source_title=original_title,
                source_id=scraped_data.get("id", ""),
                quality_score=scraped_data.get("quality_score", 0.0),
            )
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
