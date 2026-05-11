import random
import os

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
            "Spiritual Soul Meditation AI",
            "Shiv tandav AI cinematic",
            "Bajrangbali power cinematic",
            "Krishna leela AI shorts",
            "Ram bhakti AI animation",
            "Bhagavad Gita verse shorts",
            "Sanatan truth shorts",
            "Durga mata divine visuals",
            "Radha Krishna devotion cinematic",
            "Temple energy AI reels",
            "Bhakti motivation shorts",
            "Hindu religious story shorts",
            "Ramayan short story AI",
            "Mahabharat story shorts",
            "Shiv puran story reels",
            "Krishna story shorts",
            "Hanuman story cinematic",
            "Vishnu avatar story shorts",
            "Ancient hindu story animation",
            "Sanatan kahani shorts",
            "Dharmik kahani viral shorts",
            "Hindu God status",
            "Mahadev status viral",
            "Krishna bhajan status",
            "Hanuman chalisa shorts",
            "Ram bhakti status trending",
            "Sanatan Dharma status",
            "Kedarnath status viral",
            "Ujjain Mahakal status",
            "Vrindavan Krishna status",
            "Ayodhya Ram Mandir status",
            "Bhakti reels viral",
            "Religious motivational shorts",
            "Hindu mythology stories",
            "Ramayan status",
            "Mahabharat status"
        ],
        "trending_keywords": [
            "hanuman bhakti status viral",
            "mahadev status trending",
            "krishna bhajan shorts viral",
            "jai shree ram shorts trending",
            "sanatan dharma reels viral",
            "bholenath edit trending",
            "radhe radhe shorts viral",
            "hindu devotional shorts trending",
            "hanuman chalisa shorts trending",
            "mahakal status viral",
            "shree ram bhakti reels trending",
            "krishna motivation shorts viral",
            "sanatan edit reels trending",
            "shiv bhakti shorts viral",
            "hindu god ai video trending",
            "ramayan story shorts viral",
            "mahabharat story trending",
            "shiv puran shorts viral",
            "krishna story reels trending",
            "dharmik kahani shorts viral"
        ],
        "query_modifiers": [
            "viral 2026", "trending 2026", "april 2026", "latest viral", "current month trending",
            "reels trending", "status viral", "devotional shorts", "4k edit", "cinematic viral",
            "religious story", "hindu story", "dharmik kahani", "puran story", "epic story"
        ],
        "min_likes": 150,
        "min_views": 1500,
        "min_duration": 30,
        "max_duration": 65,
        "enable_segment_queue": True,
        "queue_min_source_duration": 70,
        "queue_part_min_duration": 35,
        "queue_part_max_duration": 40,
        "queue_max_parts": 3,
        "queue_search_queries": 32,
        "max_age_days": 90,
        "max_queries_per_run": 150,
        "search_timeout_seconds": 25,
        "download_timeout_seconds": 50,
        "min_topic_score": 1,
        "preferred_hours_ist": [7, 13, 19],
        "drive_folder_id": os.getenv("DRIVE_FOLDER_ID_BHAKTI"),
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
        "ai_prompt": "You are an expert Hindu devotional YouTube Shorts strategist. Create highly clickable metadata in ROMANIZED HINDI (English script/alphabet) that matches the exact source video topic. Use emotionally strong hooks and optimize for repeat views. FOR THE HOOK_LINE: Create a 3-5 word ultra-curiosity-driven hook in ROMANIZED HINDI (e.g., 'Ye rahasya जानकर dang reh jayenge', 'Aakhir kyon hua aisa?', 'Bhagwan ka chamatkar'). DO NOT USE HINDI SCRIPT. USE ONLY ENGLISH ALPHABETS. INSTRUCTIONS FOR GLOBAL REACH: Metadata must be in Romanized Hindi/English to appeal to a global audience. Add 5 trending global devotional hashtags (e.g., #Spiritual #Divine #Meditation).",
        "fallbacks": [
            {"title": "Aaj ye dekh lo! Bhagwan ka chamatkar 😱🙏 #Shorts", "description": "🙏 Jai Shri Ram! Bhagwan ki kripa aap par sada bani rahe."},
            {"title": "⚠️ Ye galti kabhi mat karna! Mahadev dekh rahe hain 🔱 #Shorts", "description": "🔱 Har Har Mahadev! Shiv ji ke is rahasya ko jaaniye."},
            {"title": "Bhagwan Krishna ka ye sandesh aapka jeevan badal dega 🤯🕉️ #Shorts", "description": "💛 Radhe Radhe! Shri Krishna ki anmol vaani."}
        ],
        "history_file": "download_history_bhakti.txt",
        "token_file": "token_bhakti.json",
        "token_secret": "YOUTUBE_TOKEN_JSON",
        "client_secret_file": "client_secret_bhakti.json",
        "watermark": "@MANASVI"
    },
    "akonymous": {
        "keywords": [
            "Best movie clips 4K cinematic",
            "Emotional movie scenes vertical",
            "Action movie shorts HD",
            "Famous movie dialogues cinematic",
            "Mind-bending movie scenes",
            "Hollywood blockbuster clips",
            "Heart touching movie moments",
            "Intense cinema scenes",
            "Best movie shots 4K",
            "Iconic film scenes vertical",
            "Netflix series viral clips",
            "Movie quotes cinematic visuals",
            "Epic movie battle scenes",
            "Sad movie moments viral",
            "Thriller movie clips vertical"
        ],
        "trending_keywords": [
            "viral movie clips trending",
            "movie scenes 2026 trending",
            "cinema edit shorts viral",
            "hollywood status trending",
            "movie dialogue status reels",
            "intense movie scenes viral",
            "best movie scenes 4k shorts",
            "cinematic edit movie status",
            "epic movie clips trending",
            "hollywood movie shorts viral"
        ],
        "query_modifiers": [
            "viral 2026", "trending 2026", "april 2026", "latest viral", "current month trending",
            "shorts viral", "analysis", "documentary style", "hidden truth", "decoded", "evidence based"
        ],
        "min_likes": 200,
        "min_views": 2000,
        "min_duration": 45,
        "max_duration": 65,
        "enable_segment_queue": False,
        "max_age_days": 60,
        "max_queries_per_run": 150,
        "search_timeout_seconds": 20,
        "download_timeout_seconds": 45,
        "min_topic_score": 2,
        "preferred_hours_ist": [11, 18, 2],
        "drive_folder_id": os.getenv("DRIVE_FOLDER_ID_AKONYMOUS"),
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
        "ai_prompt": "You are a cinema expert and YouTube Shorts strategist. Create highly clickable English metadata for famous movie clips. Focus on emotional intensity and jaw-dropping moments. FOR THE HOOK_LINE: Create a 4-6 word jaw-dropping curiosity hook (e.g., 'He didn't see THIS coming...', 'The most illegal scene?', 'This changed everything'). INSTRUCTIONS FOR GLOBAL REACH: Your metadata must appeal to a global audience. Use common cinematic terms. In the description, include short hooks in 2 other languages (e.g., Spanish/Hindi) to capture international traffic. Use high-volume global cinema hashtags.",
        "fallbacks": [
            {"title": "This scene will give you chills... 🎬 #Shorts", "description": "Cinema at its absolute best. The emotion in this scene is unmatched.\n\n#MovieClips #Cinema #Epic"},
            {"title": "He didn't expect THIS to happen 😱 #Movie", "description": "One of the most intense moments in film history. Watch until the end.\n\n#Hollywood #Intense #Shorts"},
            {"title": "The most powerful dialogue ever? 🎤 #Cinema", "description": "Words that stayed with us forever. Pure cinematic gold.\n\n#Dialogues #BestScenes #Film"}
        ],
        "history_file": "download_history_akonymous.txt",
        "token_file": "token_akonymous.json",
        "token_secret": "YOUTUBE_TOKEN_JSON_AKONYMOUS",
        "client_secret_file": "client_secret.json",
        "watermark": "@AKONYMOUSS"
    },
    "motivation": {
        "keywords": [
            "motivational quotes AI voice",
            "discipline mindset stoic",
            "success secrets wealth",
            "productivity hacks morning routine",
            "inspirational speeches cinematic",
            "stoicism philosophy wisdom",
            "alpha mindset growth",
            "hard work motivation reels",
            "millionaire mindset shorts"
        ],
        "target_tiktok_users": [
            "mental_success", "motivation.mentor", "themotivationark", "mindset.vibe"
        ],
        "query_modifiers": [
            "cinematic", "viral 2026", "global trend", "4k edit", "epic", "mindset", "hustle"
        ],
        "min_likes": 500,
        "min_views": 5000,
        "min_duration": 30,
        "max_duration": 65,
        "series_formats": [
            "Grind Minds Elite",
            "Stoic Wisdom",
            "1% Mindset",
            "Daily Discipline"
        ],
        "comment_templates": [
            "🔥 Comment 'GRIND' if you are part of the 1%.",
            "🧠 Drop a 'STREAK' if you stayed disciplined today.",
            "🚀 Share this with someone who needs to wake up."
        ],
        "post_pinned_comment": True,
        "history_file": "download_history_motivation.txt",
        "token_file": "token_motivation.json",
        "token_secret": "YOUTUBE_TOKEN_JSON_MOTIVATION",
        "client_secret_file": "client_secret_motivation.json",
        "watermark": "@GrindMinds",
        "preferred_hours_ist": [9, 17, 1],
        "drive_folder_id": os.getenv("DRIVE_FOLDER_ID_MOTIVATION"),
        "fallbacks": [
            {"title": "Stop wasting your time. 🛑 #Shorts", "description": "Every second counts. Build the life you want.\n\n#Motivation #Discipline #Grind"},
            {"title": "The 1% mindset secret 🧠 #Success", "description": "This is what separates the winners from the rest.\n\n#Mindset #Stoic #Shorts"},
            {"title": "Stay disciplined when nobody is watching 🔱 #Grind", "description": "The work you do in the dark puts you in the light.\n\n#HardWork #Elite #Shorts"}
        ],
        "ai_prompt": "You are a world-class motivational strategist. Create intense, life-changing English metadata. Focus on discipline, stoicism, and elite performance. FOR THE HOOK_LINE: Create a 4-6 word 'aggressive mindset' hook that targets insecurity or ambition (e.g., '99% of people fail this', 'Stop being a loser', 'The secret to 1% mindset'). Targeted at a global audience (US/India). Use powerful hooks that make the viewer feel like they are falling behind if they don't watch. Add 5 trending global mindset hashtags."
    }
}

def get_config(niche_name):
    return NICHES.get(niche_name.lower(), NICHES["bhakti"])
