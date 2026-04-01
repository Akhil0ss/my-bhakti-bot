import random

NICHES = {
    "bhakti": {
        "keywords": [
            "Hindu God AI Animation", 
            "Mahadev 3D Cinematic", 
            "Lord Krishna AI Divine",
            "Sanatan Dharma AI Art",
            "Lord Ram 4K Cinematic AI",
            "Hanuman 3D Animation",
            "Ganesha AI Cinematic",
            "Maa Durga AI Animation",
            "Vedic Stories Cinematic AI",
            "Spiritual Soul Meditation AI"
        ],
        "trending_keywords": [
            "hanuman bhakti status viral",
            "mahadev status trending",
            "krishna bhajan shorts viral",
            "jai shree ram shorts trending",
            "sanatan dharma reels viral",
            "bholenath edit trending",
            "radhe radhe shorts viral",
            "hindu devotional shorts trending"
        ],
        "min_likes": 1000,
        "min_views": 10000,
        "min_duration": 30,
        "max_duration": 60,
        "min_topic_score": 2,
        "preferred_hours_ist": [7, 18, 21],
        "default_language": "hi",
        "default_audio_language": "hi",
        "series_formats": [
            "Aaj Ka Bhakti Rahasya",
            "Divine Signal",
            "Sanatan Truth",
            "Bhakti Power Short"
        ],
        "comment_templates": [
            "🙏 Agar bhakti mehsoos hui ho to comment mein 'Jai Shri Ram' likho.",
            "🔱 Agar aise aur divine shorts chahiye to comment mein 'Har Har Mahadev' likho.",
            "💛 Is series ka next part chahiye ho to comment mein 'Radhe Radhe' likho."
        ],
        "post_pinned_comment": True,
        "blacklist": ["face", "facecam", "selfie", "man talking", "woman talking", "person talking", "front camera"],
        "ai_prompt": "You are an expert Hindu devotional YouTube Shorts strategist. Create highly clickable Hindi metadata that matches the exact source video topic, uses emotionally strong but believable hooks, and is optimized for watch time, curiosity, CTR, and repeat views.",
        "fallbacks": [
            {"title": "आज ये देख लो! भगवान का चमत्कार 😱🙏 #Shorts", "description": "🙏 जय श्री राम! भगवान की कृपा आप पर सदा बनी रहे।"},
            {"title": "⚠️ ये गलती कभी मत करना! महादेव देख रहे हैं 🔱 #Shorts", "description": "🔱 हर हर महादेव! शिव जी के इस रहस्य को जानिए।"},
            {"title": "भगवान कृष्ण का ये संदेश आपका जीवन बदल देगा 🤯🕉️ #Shorts", "description": "💛 राधे राधे! श्री कृष्ण की अनमोल वाणी।"}
        ],
        "history_file": "download_history_bhakti.txt",
        "token_file": "token_bhakti.json",
        "token_secret": "YOUTUBE_TOKEN_JSON"
    },
    "akonymous": {
        "keywords": [
            "Ancient history mysteries AI animation",
            "Hidden science facts cinematic AI",
            "Geopolitical secret documents animation",
            "Psychological dark facts cinematic AI",
            "Deep space mysteries 4K cinematic",
            "Unexplained anomalies document AI",
            "Forbidden archeology discoveries AI",
            "Mind-bending paradoxes animation",
            "Secret society symbols explained AI",
            "Lost civilizations 3D cinematic",
            "Future of humanity AI concept",
            "Parallel universe theory animation",
            "Digital simulation theory 4K AI",
            "Quantum physics mysteries cinematic"
        ],
        "trending_keywords": [
            "parallel universe theory viral",
            "simulation theory shorts trending",
            "dark psychology facts viral",
            "ancient civilization mystery trending",
            "hidden history facts viral",
            "forbidden archaeology trending",
            "space mystery shorts viral",
            "quantum physics mystery trending"
        ],
        "min_likes": 1500,
        "min_views": 15000,
        "min_duration": 30,
        "max_duration": 60,
        "min_topic_score": 2,
        "preferred_hours_ist": [15, 19, 22],
        "default_language": "en",
        "default_audio_language": "en",
        "series_formats": [
            "AKONYMOUS Decode",
            "Hidden Pattern",
            "Signal Drop",
            "Reality Glitch"
        ],
        "comment_templates": [
            "Comment 'TRUTH' if you want part 2.",
            "If this made you think, comment 'DECODED'.",
            "Drop 'MORE' if you want the next hidden fact."
        ],
        "post_pinned_comment": True,
        "blacklist": ["face", "facecam", "selfie", "man talking", "woman talking", "person talking", "front camera"],
        "ai_prompt": "You are the creator of AKONYMOUS, a research-driven YouTube Shorts channel. Create highly clickable English metadata that matches the exact source video topic, sounds intelligent and mysterious, and is optimized for CTR, retention, and shares without sounding generic.",
        "fallbacks": [
            {"title": "The world isn't what you think... 🕵️‍♂️ #AKONYMOUS", "description": "Think deeper. Question everything. Decode reality.\n\n#Mystery #Facts #Truth"},
            {"title": "5 Suppressed Facts the world ignores ⚠️ #Shorts", "description": "Mainstream narratives are built on assumptions. Here is the data.\n\n#Data #Logic #HiddenTruth"},
            {"title": "Ancient Knowledge vs Modern Lies 🏺 #Decode", "description": "Why were these patterns ignored for centuries?\n\n#History #Secret #Ancient"}
        ],
        "history_file": "download_history_akonymous.txt",
        "token_file": "token_akonymous.json",
        "token_secret": "YOUTUBE_TOKEN_JSON_AKONYMOUS"
    }
}

def get_config(niche_name):
    return NICHES.get(niche_name.lower(), NICHES["bhakti"])
