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

# Fallback Metadata Pool for varied uploads when API is down
FALLBACK_POOL = [
    {
        "title": "आज ये देख लो! भगवान का चमत्कार 😱🙏 #Shorts",
        "description": "🙏 जय श्री राम! भगवान की कृपा आप पर सदा बनी रहे।\n\n#Shorts #Bhakti #JaiShreeRam #Viral"
    },
    {
        "title": "⚠️ ये गलती कभी मत करना! महादेव देख रहे हैं 🔱 #Shorts",
        "description": "🔱 हर हर महादेव! शिव जी के इस रहस्य को जानिए।\n\n#Shorts #Mahadev #Shiva #Sanatan"
    },
    {
        "title": "भगवान कृष्ण का ये संदेश आपका जीवन बदल देगा 🤯🕉️ #Shorts",
        "description": "💛 राधे राधे! श्री कृष्ण की अनमोल वाणी जो हर किसी को सुननी चाहिए।\n\n#Shorts #Krishna #RadheRadhe #Bhakti"
    },
    {
        "title": "हनुमान जी ने दिया संकेत! ये देखो क्या हुआ... 😱🙏 #Shorts",
        "description": "🙏 जय बजरंगबली! हनुमान जी की रक्षा कवच आपके साथ है।\n\n#Shorts #Hanuman #Bajrangbali #Power"
    },
    {
        "title": "🔱 काशी के इस रहस्य को कोई नहीं जानता! 🕉️🔥 #Shorts",
        "description": "🕉️ हर हर महादेव! अध्यात्म की गहरी बातें और शिव की शक्ति।\n\n#Shorts #Kashi #Mahadev #Spiritual"
    },
    {
        "title": "💔 जब अकेला महसूस हो, तो बस ये सुनो... 🙏 #Shorts",
        "description": "✨ भगवान कभी आपको अकेला नहीं छोड़ते। खुद पर और उन पर भरोसा रखें।\n\n#Shorts #Motivation #God #Peace"
    },
    {
        "title": "😱 क्या आपने महादेव का ये चमत्कार देखा? 🔱 #Shorts",
        "description": "🔱 साक्षात महादेव! इस वीडियो को अंत तक जरूर देखें।\n\n#Shorts #Miracle #Mahakal #Shiv"
    },
    {
        "title": "ये मंत्र रोज़ सुबह सुनो, चमत्कार होगा! 🕉️✨ #Shorts",
        "description": "🕉️ शान्ति और शक्ति का अनुभव करें। इस मंत्र में बहुत ताकत है।\n\n#Shorts #Mantra #MorningVibes #Devotional"
    }
]

def generate_rewrite_and_quote(original_title):
    """Takes original metadata and generates VIRAL Hindi Bhakti YouTube metadata."""
    api_key = os.getenv("GEMINI_API_KEY")
    engagement_hook = random.choice(ENGAGEMENT_HOOKS)
    
    # Select a random fallback from the pool initially
    fallback = random.choice(FALLBACK_POOL)
    title = fallback["title"]
    # Ensure title ends with #Shorts
    if "#Shorts" not in title: title += " #Shorts"
    
    description = f"{fallback['description']}\n\n{engagement_hook}\n\n#Bhakti #Hindu #SanatanDharma #God #Devotional #YouTubeShorts #HindiShorts #BhaktiStatus #Viral"
    tags = "#Bhakti #Mahadev #Krishna #Ram #Hanuman #Hindu #SanatanDharma #Shorts #YouTubeShorts #Devotional #BhaktiStatus #HindiShorts #Viral"

    if not api_key:
        print("  [WARN] GEMINI_API_KEY not found. Using varied defaults.")
        return {"title": title, "tags": tags, "description": description}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash") 
        
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
        print(f"  [WARN] Gemini Generation failed ({e}). Using varied defaults from pool.")

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
