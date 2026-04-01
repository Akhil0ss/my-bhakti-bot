import os
import random
import re
import requests
import numpy as np
import yt_dlp
from moviepy import VideoFileClip
from engine.performance_tracker import get_feedback_terms, get_topic_fatigue_terms

def get_history(history_file):
    if not os.path.exists(history_file):
        return set()
    with open(history_file, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_history(vid_id, history_file):
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(f"{vid_id}\n")


def _to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _is_vertical_video(width, height):
    if width <= 0 or height <= 0:
        return False
    return height > width and (height / width) >= 1.5


def _validate_downloaded_video(filepath, min_duration, max_duration):
    try:
        with VideoFileClip(filepath) as clip:
            width, height = clip.size
            duration = clip.duration or 0
        is_valid = _is_vertical_video(width, height) and min_duration <= duration <= max_duration
        return is_valid, width, height, duration
    except Exception as e:
        print(f"  [WARN] Download validation failed: {e}")
        return False, 0, 0, 0


def _sample_visual_quality(filepath):
    try:
        with VideoFileClip(filepath) as clip:
            duration = max(clip.duration or 0, 0.1)
            sample_points = sorted(set([
                0.3,
                min(1.0, duration - 0.01),
                min(2.0, duration - 0.01),
                min(duration / 2, duration - 0.01),
            ]))
            frames = [clip.get_frame(t) for t in sample_points]
        gray_frames = [frame.mean(axis=2) for frame in frames]
        brightness = float(np.mean([frame.mean() for frame in gray_frames]))
        contrast = float(np.mean([frame.std() for frame in gray_frames]))
        first_hook_motion = 0.0
        if len(gray_frames) >= 2:
            first_hook_motion = float(np.mean(np.abs(gray_frames[1] - gray_frames[0])))
        mid_motion = 0.0
        if len(gray_frames) >= 4:
            mid_motion = float(np.mean(np.abs(gray_frames[3] - gray_frames[2])))
        quality_score = (contrast * 1.5) + (first_hook_motion * 2.0) + mid_motion
        return {
            "brightness": brightness,
            "contrast": contrast,
            "first_hook_motion": first_hook_motion,
            "mid_motion": mid_motion,
            "quality_score": quality_score,
        }
    except Exception as e:
        print(f"  [WARN] Visual quality scoring failed: {e}")
        return {
            "brightness": 0.0,
            "contrast": 0.0,
            "first_hook_motion": 0.0,
            "mid_motion": 0.0,
            "quality_score": 0.0,
        }


def _extract_terms(text):
    return {
        word for word in re.findall(r"[a-z0-9']+", (text or "").lower())
        if len(word) >= 4
    }


def _build_search_pool(config, feedback_terms):
    base_queries = config.get("trending_keywords") or config.get("keywords", [])
    fallback_queries = config.get("keywords", [])
    series_formats = config.get("series_formats", [])
    feedback_seed = " ".join(feedback_terms[:3]) if feedback_terms else ""

    pool = list(dict.fromkeys(base_queries + fallback_queries))
    if feedback_seed:
        pool.extend(
            f"{query} {feedback_seed}".strip()
            for query in base_queries[:4]
        )
    if series_formats:
        pool.extend(
            f"{query} {series}".strip()
            for query in base_queries[:3]
            for series in series_formats[:2]
        )
    return list(dict.fromkeys(pool))


def _score_video(video, keyword, config, feedback_terms, fatigue_terms):
    title = video.get("title", "")
    likes = int(video.get("digg_count", 0))
    views = int(video.get("play_count", 0))
    shares = int(video.get("share_count", 0))
    comments = int(video.get("comment_count", 0))

    view_base = max(views, 1)
    engagement_rate = (likes + (shares * 3) + comments) / view_base

    keyword_terms = _extract_terms(keyword)
    title_terms = _extract_terms(title)
    overlap = len(keyword_terms & title_terms)

    trend_terms = _extract_terms(" ".join(config.get("trending_keywords", [])))
    trend_overlap = len(trend_terms & title_terms)
    feedback_overlap = len(set(feedback_terms) & title_terms)
    fatigue_overlap = len(set(fatigue_terms) & title_terms)

    return (
        (likes * 1.0)
        + (views * 0.03)
        + (shares * 30)
        + (comments * 12)
        + (engagement_rate * 20000)
        + (overlap * 4000)
        + (trend_overlap * 2000)
        + (feedback_overlap * 2500)
        - (fatigue_overlap * 2200)
    ), overlap + trend_overlap + feedback_overlap


def _download_from_youtube_shorts(search_pool, history, config, output_dir):
    min_duration = config.get("min_duration", 30)
    max_duration = config.get("max_duration", 60)
    min_topic_score = config.get("min_topic_score", 1)
    feedback_terms = []
    fatigue_terms = get_topic_fatigue_terms("akonymous" if "akonymous" in config.get("history_file", "").lower() else "bhakti")

    for query in random.sample(search_pool, min(len(search_pool), 5)):
        print(f'  [YT] Searching fallback source for "{query}"...')
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                results = ydl.extract_info(f"ytsearch12:{query} #shorts", download=False)
            entries = results.get("entries", []) if results else []
            candidates = []
            for entry in entries:
                vid_id = entry.get("id")
                if not vid_id or vid_id in history:
                    continue
                duration = _to_float(entry.get("duration"), default=0)
                if duration and not (min_duration <= duration <= max_duration):
                    continue
                score, topic_score = _score_video(
                    {
                        "title": entry.get("title", ""),
                        "digg_count": entry.get("like_count", 0) or 0,
                        "play_count": entry.get("view_count", 0) or 0,
                        "share_count": 0,
                        "comment_count": entry.get("comment_count", 0) or 0,
                    },
                    query,
                    config,
                    feedback_terms,
                    fatigue_terms,
                )
                if topic_score < min_topic_score:
                    continue
                candidates.append((score, entry))

            candidates.sort(key=lambda item: item[0], reverse=True)
            for score, entry in candidates[:4]:
                video_url = entry.get("webpage_url") or f"https://www.youtube.com/watch?v={entry['id']}"
                output_template = os.path.join(output_dir, "raw_video.%(ext)s")
                download_opts = {
                    "format": "bestvideo*+bestaudio/best",
                    "outtmpl": output_template,
                    "quiet": True,
                    "no_warnings": True,
                }
                with yt_dlp.YoutubeDL(download_opts) as ydl:
                    info = ydl.extract_info(video_url, download=True)
                    filename = ydl.prepare_filename(info)
                if not os.path.exists(filename):
                    for f in os.listdir(output_dir):
                        if f.startswith("raw_video"):
                            filename = os.path.join(output_dir, f)
                            break

                valid_file, file_w, file_h, file_duration = _validate_downloaded_video(
                    filename,
                    min_duration=min_duration,
                    max_duration=max_duration,
                )
                if not valid_file:
                    if os.path.exists(filename):
                        os.remove(filename)
                    continue

                quality = _sample_visual_quality(filename)
                if quality["quality_score"] < 28 or quality["first_hook_motion"] < 6:
                    if os.path.exists(filename):
                        os.remove(filename)
                    continue

                print(f"  [OK] YouTube Shorts fallback selected: {entry['id']} (Score: {int(score)})")
                save_history(entry["id"], config.get("history_file", "downloaded.txt"))
                return {
                    "filepath": filename,
                    "original_title": entry.get("title", "Shorts Video"),
                    "id": entry["id"],
                    "source": "youtube_shorts",
                    "duration": file_duration,
                    "width": file_w,
                    "height": file_h,
                    "quality_score": quality["quality_score"],
                }
        except Exception as e:
            print(f"  [YT] Fallback search failed: {e}")

    return None

def download_media(config, output_dir="output", cookies_path=None):
    """AI-First TikTok strategy using niche-specific configuration."""
    os.makedirs(output_dir, exist_ok=True)
    history_file = config.get("history_file", "downloaded.txt")
    history = get_history(history_file)
    niche = "akonymous" if "akonymous" in history_file.lower() else "bhakti"
    feedback_terms = get_feedback_terms(niche)
    fatigue_terms = get_topic_fatigue_terms(niche)
    
    # Select a high-quality keyword from niche config
    search_pool = _build_search_pool(config, feedback_terms)
    if not search_pool:
        print("  [ERROR] No keywords found in niche config.")
        return None
        
    keyword = random.choice(search_pool)
    print(f"  [TIKWM] Searching for \"{keyword}\"...")
    
    try:
        # TikWM search endpoint
        search_api = f"https://www.tikwm.com/api/feed/search?keywords={keyword}&count=20"
        response = requests.get(search_api, timeout=15).json()
        
        if response.get("code") == 0 and response.get("data"):
            videos = response["data"].get("videos", [])
            if not videos:
                print("  [WARN] No videos found for this keyword.")
                return None
                
            # Randomize to get fresh content every time
            random.shuffle(videos)

            # Quality thresholds from config
            min_likes = config.get("min_likes", 500)
            min_views = config.get("min_views", 5000)
            min_duration = config.get("min_duration", 30)
            max_duration = config.get("max_duration", 60)
            min_topic_score = config.get("min_topic_score", 1)
            blacklist = config.get("blacklist", [])
            candidates = []

            for v in videos:
                v_id = v.get("video_id") or v.get("id")
                title = v.get("title", "").lower()
                likes = int(v.get("digg_count", 0))
                views = int(v.get("play_count", 0))
                duration = _to_float(v.get("duration"), default=0)
                width = int(_to_float(v.get("width"), default=0))
                height = int(_to_float(v.get("height"), default=0))
                
                # 1. Deduplication check
                if not v_id or v_id in history:
                    continue
                
                # 2. Blacklist check (No narrators/vlogs/faces)
                is_blacklisted = any(word in title for word in blacklist)
                if is_blacklisted:
                    continue
                
                # 3. High Engagement check
                if likes < min_likes or views < min_views:
                    continue

                # 4. Strict source rules: vertical only, 30s-60s only
                if duration and not (min_duration <= duration <= max_duration):
                    continue
                if width and height and not _is_vertical_video(width, height):
                    continue
                score, topic_score = _score_video(v, keyword, config, feedback_terms, fatigue_terms)
                if topic_score < min_topic_score:
                    continue

                candidates.append((score, topic_score, v, duration, likes, views))

            candidates.sort(key=lambda item: item[0], reverse=True)

            for score, topic_score, v, duration, likes, views in candidates[:8]:
                play_url = v.get("play")
                v_id = v.get("video_id") or v.get("id")
                if not play_url:
                    continue

                print(
                    f"  [OK] Selected top-scoring vertical trend video: {v_id} "
                    f"(Score: {int(score)}, Topic: {topic_score}, Likes: {likes}, Views: {views}, Duration: {duration or 'unknown'}s)"
                )
                video_content = requests.get(play_url, timeout=40).content
                filepath = os.path.join(output_dir, "raw_video.mp4")
                with open(filepath, "wb") as f:
                    f.write(video_content)

                valid_file, file_w, file_h, file_duration = _validate_downloaded_video(
                    filepath,
                    min_duration=min_duration,
                    max_duration=max_duration,
                )
                if not valid_file:
                    print(
                        "  [WARN] Rejected downloaded file because it is not a true vertical 30s-60s clip "
                        f"({file_w}x{file_h}, {file_duration:.1f}s)."
                    )
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    continue

                quality = _sample_visual_quality(filepath)
                if quality["quality_score"] < 28 or quality["first_hook_motion"] < 6:
                    print(
                        "  [WARN] Rejected downloaded file due to weak first-hook/visual quality "
                        f"(score={quality['quality_score']:.1f}, hook_motion={quality['first_hook_motion']:.1f})."
                    )
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    continue

                save_history(v_id, history_file)
                return {
                    "filepath": filepath,
                    "original_title": v.get("title", "Cinematic Video"),
                    "id": v_id,
                    "source": "tiktok",
                    "duration": file_duration,
                    "width": file_w,
                    "height": file_h,
                    "quality_score": quality["quality_score"],
                }
    except Exception as e:
        print(f"  [TIKWM] Search/Download failed: {e}")

    youtube_fallback = _download_from_youtube_shorts(search_pool, history, config, output_dir)
    if youtube_fallback:
        return youtube_fallback

    print("  [FAIL] Could not find a fresh high-quality video in this niche. Retrying later.")
    return None

if __name__ == "__main__":
    download_media()
