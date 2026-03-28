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
        "min_likes": 1000,
        "min_views": 10000,
        "blacklist": ["vlog", "podcast", "interview", "talking", "narrated", "reaction", "review", "story", "fact"],
        "ai_prompt": "You are an expert Hindu Devotional YouTube Shorts content strategist. Create MAXIMUM VIRAL YouTube Shorts metadata in Hindi.",
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
        "min_likes": 1500,
        "min_views": 15000,
        "blacklist": ["vlog", "podcast", "interview", "talking", "narrated", "vlogger", "setup", "tutorial", "face", "my story"],
        "ai_prompt": "You are the creator of AKONYMOUS, a research-driven channel for deep analysis and hidden facts. Create MYSTERIOUS, LOGICAL, and BRAIN-PICKING YouTube Shorts metadata in English.",
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
