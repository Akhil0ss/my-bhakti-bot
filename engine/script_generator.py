import os
import random
import re
from datetime import datetime, timezone
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Niche-specific engagement hooks
HOOKS = {
    "bhakti": [
        "🙏 कमेंट में लिखो 'जय श्री राम'!",
        "🔱 टाइप करो 'ॐ नमः शिवाय'!",
        "💛 'राधे राधे' लिखो कमेंट में!",
        "🕉️ 'हर हर महादेव' टाइप करो — शिव जी की कृपा बरसेगी!"
    ],
    "akonymous": [
        "🎬 Comment your favorite movie if you loved this!",
        "✨ Subscribe for more iconic movie moments!",
        "😱 Did you expect this to happen? Let us know in the comments!",
        "🔥 Share this with a movie buff!"
    ]
}

TREND_MONTH_LABEL = datetime.now(timezone.utc).strftime("%B %Y")
TREND_MONTH_TOKEN = datetime.now(timezone.utc).strftime("%b%Y").lower()

TREND_TAGS = {
    "bhakti": [
        "#shorts", "#foryou", "#viral", "#trending", "#bhakti", "#sanatan",
        "#mahadev", "#hanuman", "#krishna", "#jaishreeram", f"#{TREND_MONTH_TOKEN}"
    ],
    "akonymous": [
        "#shorts", "#foryou", "#viral", "#trending", "#movieclips", "#cinema",
        "#hollywood", "#bestscenes", "#film", "#movie", f"#{TREND_MONTH_TOKEN}"
    ],
}


def _pick_series_format(config, original_title):
    options = config.get("series_formats", [])
    if not options:
        return ""
    keywords = _extract_keywords(original_title, limit=2)
    if not keywords:
        return random.choice(options)
    return options[sum(len(word) for word in keywords) % len(options)]


def _extract_keywords(text, limit=5):
    words = re.findall(r"[A-Za-z0-9']+", text.lower())
    blocked = {
        "the", "and", "for", "with", "that", "this", "from", "into", "your", "you",
        "what", "when", "where", "they", "them", "about", "video", "shorts", "short",
        "viral", "status", "facts", "fact", "truth", "hindi", "english"
    }
    seen = []
    for word in words:
        if len(word) < 4 or word in blocked or word in seen:
            continue
        seen.append(word)
        if len(seen) == limit:
            break
    return seen


def _build_fallback_tags(original_title, niche):
    keywords = _extract_keywords(original_title, limit=4)
    base = list(TREND_TAGS.get(niche, TREND_TAGS["bhakti"]))
    base.extend(f"#{word}" for word in keywords)
    deduped = []
    for tag in base:
        if tag.lower() not in [existing.lower() for existing in deduped]:
            deduped.append(tag)
    return " ".join(deduped[:10])


def _clean_title(title):
    title = re.sub(r"\s+", " ", (title or "").strip())
    return title[:80].rstrip(" -|,")


def _clean_tags(tags, original_title, niche):
    raw_tags = re.findall(r"#?[A-Za-z0-9_]+", tags or "")
    cleaned = []
    for tag in raw_tags:
        normalized = "#" + tag.lstrip("#").lower()
        if len(normalized) <= 2:
            continue
        if normalized not in cleaned:
            cleaned.append(normalized)
    fallback_tags = _build_fallback_tags(original_title, niche).split()
    if not cleaned:
        return " ".join(fallback_tags[:10])
    if "#shorts" not in cleaned:
        cleaned.insert(0, "#shorts")
    if "#foryou" not in cleaned:
        cleaned.insert(1, "#foryou")
    for fallback_tag in fallback_tags:
        if fallback_tag not in cleaned:
            cleaned.append(fallback_tag)
        if len(cleaned) >= 10:
            break
    return " ".join(cleaned[:10])


def _score_title(title, original_title):
    title_l = (title or "").lower()
    source_words = set(_extract_keywords(original_title, limit=6))
    overlap = sum(1 for word in source_words if word in title_l)
    score = overlap * 8
    score += 10 if 35 <= len(title) <= 75 else 0
    score += 4 if any(char.isdigit() for char in title) else 0
    score += 7 if any(token in title_l for token in ["?", "why", "how", "secret", "truth", "real", "hidden", "shocking", "viral", "exposed", "revealed", "mystery"]) else 0
    hashtag_count = len(re.findall(r"#\w+", title))
    score += 6 if 1 <= hashtag_count <= 2 else 0
    score -= 6 if hashtag_count > 2 else 0
    return score


def _pick_best_title(candidates, fallback_title, original_title):
    options = [title.strip() for title in candidates if title and title.strip()]
    if not options:
        return fallback_title
    return max(options, key=lambda title: _score_title(_clean_title(title), original_title))


def _is_weak_title(title, original_title):
    return _score_title(_clean_title(title), original_title) < 18


def _parse_ai_output(output, title, description, tags, comment):
    title_candidates = []
    hook_line = ""
    for line in output.split("\n"):
        line_up = line.upper()
        if line_up.startswith("TITLE_") or line_up.startswith("TITLE "):
            title_candidates.append(line.split(":", 1)[1].strip())
        elif line_up.startswith("TITLE:"):
            title_candidates.append(line.split(":", 1)[1].strip())
        elif line_up.startswith("HOOK_LINE:"):
            hook_line = line.split(":", 1)[1].strip().strip('"').strip("'")
        elif line_up.startswith("TAGS:"):
            tags = line.split(":", 1)[1].strip()
        elif line_up.startswith("DESCRIPTION:"):
            parts = output.split("DESCRIPTION:", 1)
            if len(parts) > 1:
                description = parts[1].split("TAGS:")[0].split("COMMENT:")[0].split("HOOK_LINE:")[0].strip()
        elif line_up.startswith("COMMENT:"):
            comment = line.split(":", 1)[1].strip()
    return title_candidates or [title], description, tags, comment, hook_line


def _build_prompt(original_title, config, engagement_hook, series_label):
    return (
        f"{config.get('ai_prompt', '')}\n\n"
        f"Current trend window: {TREND_MONTH_LABEL}\n"
        f"Original source video title/topic: {original_title}\n"
        f"Engagement Hook to include naturally: {engagement_hook}\n\n"
        f"Recurring series identity to preserve: {series_label}\n\n"
        "Rules:\n"
        "1. Metadata must match the exact source topic, not generic channel themes.\n"
        "2. Title must be ultra-clickable, emotionally strong, curiosity-driven, recent/trending in tone, use tasteful clickbait, stay under 80 characters, and must include #shorts and #foryou.\n"
        "3. Description must feel native to the topic, add intrigue/value, support retention, mention recent trend energy when natural, and end with exactly 10 relevant hashtags.\n"
        "4. Tags must be high-intent YouTube Shorts hashtags directly relevant to the source topic and aligned to the current trend window.\n"
        "5. Avoid generic filler, keyword stuffing, or misleading claims.\n\n"
        "Please provide the response in this EXACT format:\n"
        "TITLE_1: [Best option]\n"
        "TITLE_2: [Alternative option]\n"
        "TITLE_3: [Alternative option]\n"
        "HOOK_LINE: [Ultra-short curiosity hook, max 6 words]\n"
        "DESCRIPTION: [The Description]\n"
        "TAGS: [The Tags]\n"
        "COMMENT: [Pinned comment text]"
    )


def _split_tag_list(tags_str):
    return [tag for tag in (tags_str or "").split() if tag.startswith("#")]


def _rotate_tags(tag_list, seed_text):
    if not tag_list:
        return tag_list
    offset = sum(ord(char) for char in (seed_text or "")) % len(tag_list)
    return tag_list[offset:] + tag_list[:offset]


def _enforce_title_hashtags(title, tags_str):
    cleaned = _clean_title(title)
    base_title = re.sub(r"\s*#\w+\b", "", cleaned).strip()
    mandatory = ["#shorts", "#foryou"]
    rotated = _rotate_tags(mandatory, base_title)
    final_title = f"{base_title} {' '.join(rotated)}".strip()
    return final_title[:80].rstrip(" -|,")


def _enforce_description_hashtags(description, tags_str, engagement_hook, series_label, niche, original_title):
    description = re.sub(r"\n{3,}", "\n\n", (description or "").strip())
    tag_list = _rotate_tags(_split_tag_list(tags_str), description)
    if not tag_list:
        tag_list = ["#shorts", "#foryou"]
    curated = []
    for tag in tag_list:
        if tag not in curated:
            curated.append(tag)
        if len(curated) >= 10:
            break
    while len(curated) < 10:
        for fallback_tag in _build_fallback_tags(original_title, niche).split():
            if fallback_tag not in curated:
                curated.append(fallback_tag)
            if len(curated) >= 10:
                break

    if engagement_hook and engagement_hook not in description:
        description = f"{description}\n\n{engagement_hook}".strip()
    if series_label and f"Series: {series_label}" not in description:
        description = f"{description}\nSeries: {series_label}".strip()

    description_no_tags = re.sub(r"(?:\n|\s)*(#\w+\s*)+$", "", description).strip()
    return f"{description_no_tags}\n\n{' '.join(curated[:10])}".strip()


def _generate_with_groq(prompt, niche):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    requested_model = os.getenv("GROQ_MODEL", "").strip()
    candidate_models = [model for model in [
        requested_model,
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
    ] if model]

    last_error = None
    for model_name in dict.fromkeys(candidate_models):
        print(f"  [INFO] Generating {niche.upper()} metadata via Groq ({model_name})...")
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model_name,
                    "temperature": 0.8,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You generate viral YouTube Shorts metadata and must follow the requested output format exactly.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=45,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            last_error = e
            print(f"  [WARN] Groq model {model_name} failed: {e}")

    if last_error:
        raise last_error
    return None




def generate_rewrite_and_quote(original_title, config):
    """Generates niche-specific viral metadata."""
    # Identify niche (default to bhakti if not found)
    hist_file = config.get("history_file", "bhakti")
    niche = "akonymous" if "akonymous" in hist_file.lower() else "bhakti"
    
    engagement_hook = random.choice(HOOKS.get(niche, HOOKS["bhakti"]))
    series_label = _pick_series_format(config, original_title)
    comment_templates = config.get("comment_templates", [])
    
    # Defaults from niche config fallbacks
    fallbacks = config.get("fallbacks", [])
    fallback = random.choice(fallbacks) if fallbacks else {"title": "Viral Video", "description": "Check this out!"}
    
    title = fallback["title"]
    description = f"{fallback['description']}\n\nSeries: {series_label}\n\n{engagement_hook}" if series_label else f"{fallback['description']}\n\n{engagement_hook}"
    tags = _build_fallback_tags(original_title, niche)
    comment = random.choice(comment_templates) if comment_templates else engagement_hook
    prompt = _build_prompt(original_title, config, engagement_hook, series_label)

    for attempt in range(2):
        output = None
        try:
            output = _generate_with_groq(prompt, niche)
            if output:
                title_candidates, description, tags, comment, hook_line = _parse_ai_output(output, title, description, tags, comment)
                title = _pick_best_title(title_candidates, title, original_title)
        except Exception as e:
            print(f"  [WARN] Groq failed: {e}")
            break
        else:
            if not output:
                print("  [WARN] No Groq API output found. Using fallbacks.")
                break

        if not _is_weak_title(title, original_title):
            break
        if attempt == 0:
            print("  [INFO] Metadata reroll triggered because title score was weak.")

    cleaned_tags = _clean_tags(tags, original_title, niche)

    return {
        "title": _enforce_title_hashtags(title, cleaned_tags),
        "tags": cleaned_tags,
        "description": _enforce_description_hashtags(description, cleaned_tags, engagement_hook, series_label, niche, original_title),
        "comment": comment,
        "series_label": series_label,
        "hook_line": hook_line or title.split("#")[0].strip()[:30],
    }

if __name__ == "__main__":
    # Test
    dummy_config = {"history_file": "history_akonymous.txt", "ai_prompt": "Create mystery content."}
    result = generate_rewrite_and_quote("Ancient Egypt mystery", dummy_config)
    print(result)
