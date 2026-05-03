import os
import random
import re
from datetime import datetime, timedelta, timezone
import requests
import numpy as np
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


def _is_valid_aspect_ratio(width, height):
    if width <= 0 or height <= 0:
        return False
    # User requested Square (1:1) up to 9:16.
    # Height must be greater than or equal to width (No horizontal).
    return height >= width


def _validate_downloaded_video(filepath, min_duration, max_duration=None):
    try:
        with VideoFileClip(filepath) as clip:
            width, height = clip.size
            duration = clip.duration or 0
        duration_valid = duration >= min_duration and (max_duration is None or duration <= max_duration)
        
        # Quality check: Bytes per second (Bitrate estimation)
        file_size = os.path.getsize(filepath)
        bytes_per_second = file_size / max(duration, 0.1)
        # We want at least 150KB/s (approx 1.2Mbps) for decent quality
        is_high_quality = bytes_per_second > 150000 
        
        rejection_reason = None
        if not _is_valid_aspect_ratio(width, height):
            rejection_reason = f"Invalid aspect ratio {width}x{height} (Must be Square or Vertical)"
        elif not duration_valid:
            rejection_reason = f"Bad duration {duration:.1f}s"
        elif not is_high_quality:
            rejection_reason = f"Low quality/bitrate ({bytes_per_second/1024:.1f} KB/s)"

        is_valid = rejection_reason is None
        return is_valid, width, height, duration, rejection_reason
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


def _human_presence_risk(filepath):
    try:
        with VideoFileClip(filepath) as clip:
            duration = max(clip.duration or 0, 0.1)
            sample_points = sorted(set([
                0.4,
                min(1.2, duration - 0.01),
                min(duration / 2, duration - 0.01),
            ]))
            frames = [clip.get_frame(t).astype(np.float32) for t in sample_points]

        risks = []
        for frame in frames:
            if frame.ndim != 3 or frame.shape[2] < 3:
                continue
            r = frame[:, :, 0]
            g = frame[:, :, 1]
            b = frame[:, :, 2]
            skin_mask = (
                (r > 95) & (g > 40) & (b > 20) &
                ((np.maximum.reduce([r, g, b]) - np.minimum.reduce([r, g, b])) > 15) &
                (np.abs(r - g) > 15) & (r > g) & (r > b)
            )
            h, w = skin_mask.shape
            center = skin_mask[h // 4: (3 * h) // 4, w // 4: (3 * w) // 4]
            frame_skin_ratio = float(np.mean(skin_mask))
            center_skin_ratio = float(np.mean(center)) if center.size else 0.0
            risks.append((frame_skin_ratio, center_skin_ratio))

        if not risks:
            return 0.0
        return max((skin * 0.8) + (center * 1.6) for skin, center in risks)
    except Exception as e:
        print(f"  [WARN] Human-presence heuristic failed: {e}")
        return 0.0


def _extract_terms(text):
    return {
        word for word in re.findall(r"[a-z0-9']+", (text or "").lower())
        if len(word) >= 4
    }


def _normalize_query(text):
    return re.sub(r"\s+", " ", (text or "").strip())


def _build_search_pool(config, feedback_terms):
    base_queries = config.get("trending_keywords") or config.get("keywords", [])
    fallback_queries = config.get("keywords", [])
    series_formats = config.get("series_formats", [])
    query_modifiers = config.get("query_modifiers", [])
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
    if query_modifiers:
        pool.extend(
            _normalize_query(f"{query} {modifier}")
            for query in (base_queries[:16] + fallback_queries[:32])
            for modifier in query_modifiers
        )
    if feedback_terms:
        pool.extend(
            _normalize_query(f"{query} {' '.join(feedback_terms[:2])}")
            for query in fallback_queries[:24]
        )
    return list(dict.fromkeys(query for query in pool if _normalize_query(query)))


def _extract_publish_timestamp(video):
    for field in ["create_time", "createTime", "create_time_ms", "createTimeMS", "timestamp"]:
        numeric = _to_float(video.get(field), default=0)
        if numeric <= 0:
            continue
        if numeric > 10_000_000_000:
            numeric /= 1000.0
        try:
            return datetime.fromtimestamp(numeric, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            continue
    return None


def _within_recent_window(video, max_age_days):
    published_at = _extract_publish_timestamp(video)
    if not published_at:
        return False, None
    return (datetime.now(timezone.utc) - published_at) <= timedelta(days=max_age_days), published_at


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
    recent_ok, published_at = _within_recent_window(video, config.get("max_age_days", 30))
    recency_bonus = 0.0
    if recent_ok and published_at:
        age_hours = max((datetime.now(timezone.utc) - published_at).total_seconds() / 3600.0, 1.0)
        recency_bonus = max(0.0, 2500 - (age_hours * 3.0))

    return (
        (likes * 1.0)
        + (views * 0.03)
        + (shares * 30)
        + (comments * 12)
        + (engagement_rate * 20000)
        + (overlap * 4000)
        + (trend_overlap * 2000)
        + (feedback_overlap * 2500)
        + recency_bonus
        - (fatigue_overlap * 2200)
    ), overlap + trend_overlap + feedback_overlap


def _select_candidate_from_keyword(
    keyword,
    config,
    history,
    feedback_terms,
    fatigue_terms,
    min_likes,
    min_views,
    min_duration,
    max_duration,
    min_topic_score,
):
    print(f'  [TIKWM] Searching for "{keyword}"...')
    try:
        response = requests.get(
            "https://www.tikwm.com/api/feed/search",
            params={"keywords": keyword, "count": 20},
            timeout=config.get("search_timeout_seconds", 25),
        ).json()
    except requests.RequestException as e:
        print(f'  [WARN] Search request failed for "{keyword}": {e}')
        return None

    if response.get("code") != 0 or not response.get("data"):
        return None

    videos = response["data"].get("videos", [])
    if not videos:
        return None

    random.shuffle(videos)
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
        is_recent, published_at = _within_recent_window(v, config.get("max_age_days", 30))

        if not v_id or v_id in history:
            continue
        if not is_recent:
            continue
        if any(word in title for word in blacklist):
            continue
        if likes < min_likes or views < min_views:
            continue
        if duration and not (duration >= min_duration and (max_duration is None or duration <= max_duration)):
            continue
        if width and height and not _is_valid_aspect_ratio(width, height):
            continue

        score, topic_score = _score_video(v, keyword, config, feedback_terms, fatigue_terms)
        if topic_score < min_topic_score:
            continue
        candidates.append((score, topic_score, v, duration, likes, views, published_at))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates


def download_media(
    config,
    output_dir="output",
    cookies_path=None,
    min_duration_override=None,
    max_duration_override=None,
    query_limit_override=None,
):
    """AI-First TikTok strategy using niche-specific configuration."""
    os.makedirs(output_dir, exist_ok=True)
    history_file = config.get("history_file", "downloaded.txt")
    history = get_history(history_file)
    niche = "akonymous" if "akonymous" in history_file.lower() else "bhakti"
    feedback_terms = get_feedback_terms(niche)
    fatigue_terms = get_topic_fatigue_terms(niche)
    
    # NEW: Prioritize specific TikTok target users if defined in niche config
    target_users = config.get("target_tiktok_users", [])
    if target_users:
        random.shuffle(target_users)
        for user in target_users:
            print(f"  [TIKWM] Checking priority feed for user: @{user}...")
            user_url = f"https://www.tikwm.com/api/user/posts?unique_id={user}&count=15&cursor=0"
            try:
                resp = requests.get(user_url, timeout=15).json()
                if resp.get("code") == 0 and resp.get("data", {}).get("videos"):
                    # Process these videos through existing selection logic
                    v_list = resp["data"]["videos"]
                    candidates = _process_raw_candidates(
                        v_list, "priority_user", config, history, feedback_terms, fatigue_terms,
                        config.get("min_likes", 500), config.get("min_views", 5000),
                        min_duration_override or config.get("min_duration", 30),
                        max_duration_override or config.get("max_duration", 60),
                        config.get("min_topic_score", 1)
                    )
                    if candidates:
                        best = candidates[0]
                        # Best is (score, topic_score, v, duration, likes, views, published_at)
                        v = best[2]
                        v_id = v.get("id") or v.get("video_id")
                        print(f"  [OK] Selected high-quality clip from @{user} feed: {v_id}")
                        # Proceed with download
                        video_url = v.get("play") or v.get("hdplay")
                        if video_url:
                            # Re-using internal download logic
                            resp_video = requests.get(video_url, timeout=30)
                            filepath = os.path.join(output_dir, "raw_video.mp4")
                            with open(filepath, "wb") as f:
                                f.write(resp_video.content)
                            
                            is_v, w, h, d, reason = _validate_downloaded_video(
                                filepath, min_duration_override or config.get("min_duration", 30), 
                                max_duration_override or config.get("max_duration", 60)
                            )
                            if is_v:
                                return {
                                    "filepath": filepath,
                                    "original_title": v.get("title", "Motivational Video"),
                                    "id": v_id,
                                    "source": "tiktok_user",
                                    "duration": d,
                                    "width": w,
                                    "height": h,
                                    "quality_score": best[0]
                                }
            except Exception as e:
                print(f"  [WARN] User feed priority check failed for @{user}: {e}")

    # Select a high-quality keyword from niche config (Fallback if no user video selected)
    search_pool = _build_search_pool(config, feedback_terms)
    if not search_pool:
        print("  [ERROR] No keywords found in niche config.")
        return None
    print(f"  [INFO] Search pool prepared with {len(search_pool)} queries and a {config.get('max_age_days', 30)}-day recency filter.")
        
    threshold_profiles = [
        {
            "min_likes": config.get("min_likes", 500),
            "min_views": config.get("min_views", 5000),
            "min_topic_score": config.get("min_topic_score", 1),
        },
        {
            "min_likes": max(500, int(config.get("min_likes", 500) * 0.6)),
            "min_views": max(5000, int(config.get("min_views", 5000) * 0.6)),
            "min_topic_score": max(1, config.get("min_topic_score", 1) - 1),
        },
        {
            "min_likes": 200,
            "min_views": 2000,
            "min_topic_score": 1,
        },
    ]
    random.shuffle(search_pool)
    keywords_to_try = search_pool[: min(len(search_pool), query_limit_override or config.get("max_queries_per_run", 80))]
    min_duration = min_duration_override if min_duration_override is not None else config.get("min_duration", 30)
    max_duration = max_duration_override if max_duration_override is not None else config.get("max_duration", 60)

    for idx, profile in enumerate(threshold_profiles, start=1):
        if idx > 1:
            print(
                f"  [INFO] Broadening search (pass {idx}) "
                f"likes>={profile['min_likes']} views>={profile['min_views']} topic>={profile['min_topic_score']}"
            )
        for keyword in keywords_to_try:
            candidates = _select_candidate_from_keyword(
                keyword=keyword,
                config=config,
                history=history,
                feedback_terms=feedback_terms,
                fatigue_terms=fatigue_terms,
                min_likes=profile["min_likes"],
                min_views=profile["min_views"],
                min_duration=min_duration,
                max_duration=max_duration,
                min_topic_score=profile["min_topic_score"],
            )
            if not candidates:
                continue

            for score, topic_score, v, duration, likes, views, published_at in candidates[:8]:
                play_url = v.get("play")
                v_id = v.get("video_id") or v.get("id")
                if not play_url:
                    continue

                print(
                    f"  [OK] Selected top-scoring vertical trend video: {v_id} "
                    f"(Score: {int(score)}, Topic: {topic_score}, Likes: {likes}, Views: {views}, "
                    f"Duration: {duration or 'unknown'}s, Published: {published_at.strftime('%Y-%m-%d') if published_at else 'unknown'})"
                )
                try:
                    video_content = requests.get(play_url, timeout=config.get("download_timeout_seconds", 45)).content
                except requests.RequestException as e:
                    print(f"  [WARN] Download failed for {v_id}: {e}")
                    continue
                filepath = os.path.join(output_dir, "raw_video.mp4")
                with open(filepath, "wb") as f:
                    f.write(video_content)

                is_v, w, h, d, reason = _validate_downloaded_video(
                    filepath, min_duration, max_duration
                )
                if not is_v:
                    print(
                        f"  [WARN] Rejected downloaded file: {reason}"
                    )
                    try:
                        if os.path.exists(filepath):
                            os.remove(filepath)
                    except:
                        pass
                    continue

                quality = _sample_visual_quality(filepath)
                if quality["quality_score"] < 16:
                    print(
                        f"  [WARN] Rejected downloaded file due to very weak visual quality (score={quality['quality_score']:.1f}, hook_motion={quality['first_hook_motion']:.1f})."
                    )
                    try:
                        if os.path.exists(filepath):
                            os.remove(filepath)
                    except:
                        pass
                    continue
                if quality["first_hook_motion"] < 1.0:
                    print(
                        "  [INFO] Low-motion opener detected but accepted because other quality checks passed "
                        f"(score={quality['quality_score']:.1f}, hook_motion={quality['first_hook_motion']:.1f})."
                    )

                human_risk = _human_presence_risk(filepath)
                if human_risk > 1.25:
                    print(
                        f"  [WARN] Rejected downloaded file because it looks like face-led / human-present content (risk={human_risk:.2f})."
                    )
                    try:
                        if os.path.exists(filepath):
                            os.remove(filepath)
                    except:
                        pass
                    continue

                save_history(v_id, history_file)
                return {
                    "filepath": filepath,
                    "original_title": v.get("title", "Cinematic Video"),
                    "id": v_id,
                    "source": "tiktok",
                    "duration": d,
                    "width": w,
                    "height": h,
                    "quality_score": quality["quality_score"],
                }

    print("  [FAIL] Could not find a fresh high-quality video in this niche. Retrying later.")
    return None

if __name__ == "__main__":
    download_media()
