import os
import random
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
        "🕵️‍♂️ Comment 'TRUTH' if you want to see more hidden facts.",
        "⚠️ Share this with someone who needs to wake up.",
        "🧠 Did you know this? Let us know your thoughts in the comments.",
        "✨ Subscribe to AKONYMOUS to decode more reality."
    ]
}


def _parse_ai_output(output, title, description, tags):
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
    return title, description, tags


def _build_prompt(original_title, config, engagement_hook):
    return (
        f"{config.get('ai_prompt', '')}\n\n"
        f"Original video title: {original_title}\n"
        f"Engagement Hook to include: {engagement_hook}\n\n"
        "Please provide the response in this EXACT format:\n"
        "TITLE: [The Title]\n"
        "DESCRIPTION: [The Description]\n"
        "TAGS: [The Tags]"
    )


def _generate_with_groq(prompt, niche):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    print(f"  [INFO] Generating {niche.upper()} metadata via Groq...")
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
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


def _generate_with_gemini(prompt, niche):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    print(f"  [INFO] Groq unavailable. Generating {niche.upper()} metadata via Gemini...")
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_rewrite_and_quote(original_title, config):
    """Generates niche-specific viral metadata."""
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
    prompt = _build_prompt(original_title, config, engagement_hook)

    try:
        output = _generate_with_groq(prompt, niche)
        if output:
            title, description, tags = _parse_ai_output(output, title, description, tags)
    except Exception as e:
        print(f"  [WARN] Groq failed: {e}")
        try:
            output = _generate_with_gemini(prompt, niche)
            if output:
                title, description, tags = _parse_ai_output(output, title, description, tags)
        except Exception as gemini_error:
            print(f"  [WARN] Gemini failed: {gemini_error}. Using fallbacks.")
    else:
        if not output:
            try:
                output = _generate_with_gemini(prompt, niche)
                if output:
                    title, description, tags = _parse_ai_output(output, title, description, tags)
                else:
                    print("  [WARN] No Groq/Gemini API key found. Using fallbacks.")
            except Exception as gemini_error:
                print(f"  [WARN] Gemini failed: {gemini_error}. Using fallbacks.")

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
