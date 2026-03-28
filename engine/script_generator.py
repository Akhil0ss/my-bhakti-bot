import os
import random
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
        "🕵️‍♂️ Comment 'TRUTH' if you want to see more hidden facts.",
        "⚠️ Share this with someone who needs to wake up.",
        "🧠 Did you know this? Let us know your thoughts in the comments.",
        "✨ Subscribe to AKONYMOUS to decode more reality."
    ]
}

def generate_rewrite_and_quote(original_title, config):
    """Generates niche-specific viral metadata."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Identify niche (default to bhakti if not found)
    hist_file = config.get("history_file", "bhakti")
    niche = "akonymous" if "akonymous" in hist_file.lower() else "bhakti"
    
    engagement_hook = random.choice(HOOKS.get(niche, HOOKS["bhakti"]))
    
    # Defaults from niche config fallbacks
    fallbacks = config.get("fallbacks", [])
    fallback = random.choice(fallbacks) if fallbacks else {"title": "Viral Video", "description": "Check this out!"}
    
    title = fallback["title"]
    description = f"{fallback['description']}\n\n{engagement_hook}\n\n#Viral #Trending #Shorts"
    tags = "#viral #trending #shorts"

    if not api_key:
        print(f"  [WARN] GEMINI_API_KEY not found. Using {niche} fallback.")
        return {"title": title, "tags": tags, "description": description}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash") 
        
        prompt = f"{config.get('ai_prompt', '')}\n\nOriginal video title: {original_title}\nEngagement Hook to include: {engagement_hook}\n\nPlease provide the response in this EXACT format:\nTITLE: [The Title]\nDESCRIPTION: [The Description]\nTAGS: [The Tags]"

        print(f"  [INFO] Generating {niche.upper()} Metadata via Gemini...")
        response = model.generate_content(prompt)
        output = response.text.strip()
        
        # Simple parser for Gemini output
        for line in output.split("\n"):
            line_up = line.upper()
            if line_up.startswith("TITLE:"):
                title = line.split(":", 1)[1].strip()
            elif line_up.startswith("TAGS:"):
                tags = line.split(":", 1)[1].strip()
            elif line_up.startswith("DESCRIPTION:"):
                parts = output.split("DESCRIPTION:", 1)
                if len(parts) > 1:
                    description = parts[1].split("TAGS:")[0].strip()
    except Exception as e:
        print(f"  [WARN] Gemini failed: {e}. using fallbacks.")

    return {
        "title": title,
        "tags": tags,
        "description": description
    }

if __name__ == "__main__":
    # Test
    dummy_config = {"history_file": "history_akonymous.txt", "ai_prompt": "Create mystery content."}
    result = generate_rewrite_and_quote("Ancient Egypt mystery", dummy_config)
    print(result)
