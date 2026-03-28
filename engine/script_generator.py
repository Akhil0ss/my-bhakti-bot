import os
import random
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Engagement hooks that force people to comment (comments = algorithm boost)
ENGAGEMENT_HOOKS = [
    "🙏 कमेंट में लिखो 'जय श्री राम' — भगवान तुम्हारी हर मनोकामना पूरी करेंगे!",
    "🔱 टाइप करो 'ॐ नमः शिवाय' — महादेव तुम्हें हर संकट से बचाएंगे!",
    "💛 'राधे राधे' लिखो — कृष्ण जी तुम्हारे जीवन में खुशियां भरेंगे!",
    "🙏 'जय बजरंगबली' लिखो कमेंट में — हनुमान जी तुम्हारी रक्षा करेंगे!",
    "⚡ शेयर करो इस वीडियो को — पुण्य मिलेगा! 🙏",
    "🕉️ 'हर हर महादेव' टाइप करो — शिव जी की कृपा बरसेगी!",
    "🙏 इस वीडियो को LIKE करो — भगवान देख रहे हैं!",
]

def generate_rewrite_and_quote(original_title):
    """Takes original metadata and generates VIRAL Hindi Bhakti YouTube metadata."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file!")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    engagement_hook = random.choice(ENGAGEMENT_HOOKS)
    
    prompt = f"""You are an expert Hindu Devotional YouTube Shorts content strategist.
I have a viral Bhakti reel with this original title/description: "{original_title}"

Your job is to create MAXIMUM VIRAL YouTube Shorts metadata in Hindi.

RULES FOR TITLE:
- Must be in Hindi (Devanagari) with 2-3 emojis
- Must create CURIOSITY or FEAR or EMOTION
- Use one of these PROVEN viral formulas:
  * "आज ये देख लो! [hook] 😱🙏"
  * "⚠️ मत करना ये गलती! [consequence] 🔱"
  * "भगवान [deity] का ये रहस्य कोई नहीं जानता 🤯🕉️"  
  * "💔 जब [situation], तो बस ये सुनो... 🙏"
  * "🔱 [deity] भक्तों के लिए बड़ी खबर! [hook] ✨"
  * "ये मंत्र सुनो, चमत्कार होगा! 🕉️🔥"
  * "😱 [deity] ने दिया संकेत! ये देखो क्या हुआ..."
- Keep title under 70 characters
- MUST include #Shorts at the end

RULES FOR DESCRIPTION:
- Line 1: A powerful 1-line Hindi Bhakti motivational quote
- Line 2: Empty line
- Line 3: This EXACT engagement hook: "{engagement_hook}"
- Line 4: Empty line
- Lines 5+: 15 trending SEO hashtags
- Last line: #Shorts #YouTubeShorts #Bhakti #Viral

RULES FOR TAGS:
- 15 tags mixing Hindi and English
- Must include: bhakti, mahadev, krishna, ram, hanuman, hindu, sanatan, shorts, viral

Format EXACTLY:
TITLE: [title] #Shorts
DESCRIPTION: [description]
TAGS: #tag1 #tag2 ... #tag15"""

    print("  [INFO] Generating VIRAL Hindi Bhakti Metadata via Gemini...")
    response = model.generate_content(prompt)
    output = response.text.strip()
    
    # Defaults with engagement hook baked in
    title = "आज ये देख लो! भगवान का चमत्कार 😱🙏 #Shorts"
    description = f"🙏 जय श्री राम! भगवान हर पल आपके साथ हैं।\n\n{engagement_hook}\n\n#Bhakti #Mahadev #Krishna #Ram #Hanuman #Hindu #SanatanDharma #God #Devotional #Shorts #YouTubeShorts #HindiShorts #BhaktiStatus #JaiShreeRam #HarHarMahadev #Viral"
    tags = "#Bhakti #Mahadev #Krishna #Ram #Hanuman #Hindu #SanatanDharma #Shorts #YouTubeShorts #Devotional #BhaktiStatus #HindiShorts #JaiShreeRam #HarHarMahadev #Viral"
    
    for line in output.split("\n"):
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
            if "#Shorts" not in title:
                title += " #Shorts"
        elif line.startswith("TAGS:"):
            tags = line.replace("TAGS:", "").strip()
        elif line.startswith("DESCRIPTION:"):
            raw_desc = output.split("DESCRIPTION:")[1].split("TAGS:")[0].strip()
            # Force engagement hook into description
            if engagement_hook not in raw_desc:
                raw_desc += f"\n\n{engagement_hook}"
            description = raw_desc
    
    if "#Shorts" not in description:
        description += "\n#Shorts #YouTubeShorts"
    
    print(f"  [OK] Title: {title}")
    
    return {
        "title": title,
        "tags": tags,
        "description": description
    }

if __name__ == "__main__":
    result = generate_rewrite_and_quote("Beautiful Mahadev status #shiva")
    print(result)
