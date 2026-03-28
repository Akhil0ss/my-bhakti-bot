import os
from gtts import gTTS

def generate_voice(text, output_dir="output", voice="male_en"):
    """Generates audio from text using Google TTS (Fallback)."""
    os.makedirs(output_dir, exist_ok=True)
    audio_path = os.path.join(output_dir, "voiceover.mp3")
    subtitle_path = os.path.join(output_dir, "subtitles.vtt")
    
    # Generate TTS in Hindi
    tts = gTTS(text=text, lang="hi", slow=False)
    tts.save(audio_path)
    
    # Create an empty subtitles file so MoviePy doesn't crash
    with open(subtitle_path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
    
    print(f"  [OK] Audio generated: {audio_path}")
    print(f"  [WARN] Using Google TTS Fallback (captions disabled for this run)")
    
    return {
        "audio": audio_path,
        "subtitles": subtitle_path
    }

if __name__ == "__main__":
    result = generate_voice("Welcome to the Aura Shorts automatic voice engine!")
    print(result)
