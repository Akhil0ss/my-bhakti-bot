import json
import os
import re
from collections import Counter
from datetime import datetime, timezone, timedelta

DATA_DIR = "strategy_data"


def _data_path(niche):
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{niche.lower()}_performance.json")


def _default_payload():
    return {"uploads": []}


def load_performance_data(niche):
    path = _data_path(niche)
    if not os.path.exists(path):
        return _default_payload()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return _default_payload()


def save_performance_data(niche, data):
    with open(_data_path(niche), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=True, indent=2)


def _extract_terms(text):
    stop = {
        "shorts", "short", "viral", "video", "facts", "truth", "mystery", "hindi",
        "english", "with", "that", "this", "from", "your", "have", "will", "about"
    }
    return [
        word for word in re.findall(r"[a-z0-9']+", (text or "").lower())
        if len(word) >= 4 and word not in stop
    ]


def record_upload_result(niche, source_title, source_id, generated_title, tags, quality_score=0.0):
    data = load_performance_data(niche)
    now = datetime.now(timezone.utc)
    ist_hour = int((now + timedelta(hours=5, minutes=30)).strftime("%H"))
    entry = {
        "timestamp_utc": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "posted_hour_ist": ist_hour,
        "source_title": source_title,
        "source_id": source_id,
        "generated_title": generated_title,
        "tags": tags,
        "quality_score": quality_score,
    }
    uploads = data.setdefault("uploads", [])
    uploads.append(entry)
    data["uploads"] = uploads[-100:]
    save_performance_data(niche, data)


def get_feedback_terms(niche, limit=20):
    data = load_performance_data(niche)
    counter = Counter()
    for upload in data.get("uploads", []):
        counter.update(_extract_terms(upload.get("source_title", "")))
        counter.update(_extract_terms(upload.get("generated_title", "")))
    return [term for term, _ in counter.most_common(limit)]


def get_topic_fatigue_terms(niche, limit=12, recent_count=12):
    data = load_performance_data(niche)
    counter = Counter()
    recent_uploads = data.get("uploads", [])[-recent_count:]
    for upload in recent_uploads:
        counter.update(_extract_terms(upload.get("source_title", "")))
    return [term for term, _ in counter.most_common(limit)]


def get_recommended_hours_ist(niche, default_hours=None):
    data = load_performance_data(niche)
    counter = Counter()
    for upload in data.get("uploads", []):
        hour = upload.get("posted_hour_ist")
        if isinstance(hour, int):
            counter[hour] += 1
    if counter:
        return [hour for hour, _ in counter.most_common(3)]
    return default_hours or []


def sync_recent_video_stats(niche, youtube, max_results=15):
    data = load_performance_data(niche)
    uploads = data.setdefault("uploads", [])
    try:
        channel_resp = youtube.channels().list(part="id", mine=True).execute()
        items = channel_resp.get("items", [])
        if not items:
            return
        channel_id = items[0]["id"]
        search_resp = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=max_results,
            order="date",
            type="video",
        ).execute()
        video_ids = [item["id"]["videoId"] for item in search_resp.get("items", []) if item.get("id", {}).get("videoId")]
        if not video_ids:
            return
        videos_resp = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids),
            maxResults=max_results,
        ).execute()
        stats_by_id = {}
        for item in videos_resp.get("items", []):
            stats = item.get("statistics", {})
            stats_by_id[item["id"]] = {
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "video_title": item.get("snippet", {}).get("title", ""),
            }
        for upload in uploads:
            source_id = upload.get("source_id")
            if source_id in stats_by_id:
                upload["latest_stats"] = stats_by_id[source_id]
    except Exception:
        return
    save_performance_data(niche, data)
