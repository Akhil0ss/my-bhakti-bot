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
    engagement_hook = random.choice(ENGAGEMENT_HOOKS)
    
    # Defaults in case of API failure
    title = f"आज ये देख लो! भगवान का चमत्कार 😱🙏 #Shorts"
    description = f"🙏 जय श्री राम! भगवान हर पल आपके साथ हैं।\n\n{engagement_hook}\n\n#Bhakti #Mahadev #Krishna #Ram #Hanuman #Hindu #SanatanDharma #God #Devotional #Shorts #YouTubeShorts #HindiShorts #BhaktiStatus #JaiShreeRam #HarHarMahadev #Viral"
    tags = "#Bhakti #Mahadev #Krishna #Ram #Hanuman #Hindu #SanatanDharma #Shorts #YouTubeShorts #Devotional #BhaktiStatus #HindiShorts #JaiShreeRam #HarHarMahadev #Viral"

    if not api_key:
        print("  [WARN] GEMINI_API_KEY not found. Using defaults.")
        return {"title": title, "tags": tags, "description": description}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash") # Use stable model
        
        prompt = f"""You are an expert Hindu Devotional YouTube Shorts content strategist.
I have a viral Bhakti reel with this original title: "{original_title}"
Create MAXIMUM VIRAL YouTube Shorts metadata in Hindi.
TITLE: [Viral Hindi Title with emojis] #Shorts
DESCRIPTION: [Hindi Bhakti Quote] \n\n {engagement_hook} \n\n #Shorts #Bhakti #Viral
TAGS: #bhakti #viral #trending #shorts"""

        print("  [INFO] Generating VIRAL Hindi Bhakti Metadata via Gemini...")
        response = model.generate_content(prompt)
        output = response.text.strip()
        
        for line in output.split("\n"):
            if line.upper().startswith("TITLE:"):
                title = line.split(":", 1)[1].strip()
                if "#Shorts" not in title: title += " #Shorts"
            elif line.upper().startswith("TAGS:"):
                tags = line.split(":", 1)[1].strip()
            elif line.upper().startswith("DESCRIPTION:"):
                parts = output.split("DESCRIPTION:", 1)
                if len(parts) > 1:
                    raw_desc = parts[1].split("TAGS:")[0].strip()
                    if engagement_hook not in raw_desc:
                        raw_desc += f"\n\n{engagement_hook}"
                    description = raw_desc
    except Exception as e:
        print(f"  [WARN] Gemini Generation failed ({e}). Using viral defaults.")

    if "#Shorts" not in description:
        description += "\n#Shorts #YouTubeShorts"
    
    return {
        "title": title,
        "tags": tags,
        "description": description
    }

if __name__ == "__main__":
    result = generate_rewrite_and_quote("Beautiful Mahadev status #shiva")
    print(result)
