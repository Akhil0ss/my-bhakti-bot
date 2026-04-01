import json
import os
from datetime import datetime, timedelta, timezone

QUEUE_DIR = "scheduled_queue"


def _queue_path(niche):
    os.makedirs(QUEUE_DIR, exist_ok=True)
    return os.path.join(QUEUE_DIR, f"{niche.lower()}_queue.json")


def load_queue(niche):
    path = _queue_path(niche)
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_queue(niche, items):
    with open(_queue_path(niche), "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=True, indent=2)


def _parse_iso(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def get_due_item(niche, now=None):
    now = now or datetime.now(timezone.utc)
    queue = load_queue(niche)
    queue.sort(key=lambda item: item.get("due_at_utc", ""))
    for item in queue:
        due_at = _parse_iso(item.get("due_at_utc", ""))
        if due_at and due_at <= now and os.path.exists(item.get("video_path", "")):
            return item
    return None


def remove_queue_item(niche, queue_id):
    queue = load_queue(niche)
    queue = [item for item in queue if item.get("queue_id") != queue_id]
    save_queue(niche, queue)


def cleanup_missing_files(niche):
    queue = load_queue(niche)
    filtered = [item for item in queue if os.path.exists(item.get("video_path", ""))]
    if len(filtered) != len(queue):
        save_queue(niche, filtered)


def _next_slot_after(now_utc, preferred_hours_ist, step_index):
    if not preferred_hours_ist:
        return now_utc + timedelta(hours=step_index * 6)

    ist_now = now_utc + timedelta(hours=5, minutes=30)
    hours = sorted(set(int(hour) for hour in preferred_hours_ist))
    day = ist_now.date()
    remaining_step = step_index

    while True:
        for hour in hours:
            candidate_ist = datetime(day.year, day.month, day.day, hour, 0, tzinfo=timezone.utc) - timedelta(hours=5, minutes=30)
            if candidate_ist <= now_utc:
                continue
            remaining_step -= 1
            if remaining_step == 0:
                return candidate_ist
        day = day + timedelta(days=1)


def enqueue_rendered_parts(niche, rendered_parts, metadata_items, preferred_hours_ist):
    now = datetime.now(timezone.utc)
    queue = load_queue(niche)
    for offset, (part, metadata) in enumerate(zip(rendered_parts, metadata_items), start=1):
        due_at = _next_slot_after(now, preferred_hours_ist, offset)
        queue.append(
            {
                "queue_id": f"{niche}-{int(now.timestamp())}-{part['part_index']}",
                "video_path": part["path"],
                "part_index": part["part_index"],
                "due_at_utc": due_at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "title": metadata["title"],
                "description": metadata["description"],
                "tags": metadata["tags"],
                "comment": metadata.get("comment"),
                "series_label": metadata.get("series_label", ""),
                "source_title": metadata.get("source_title", ""),
                "source_id": metadata.get("source_id", ""),
                "quality_score": metadata.get("quality_score", 0.0),
            }
        )
    save_queue(niche, queue)
