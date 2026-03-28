import os
import random
from moviepy import VideoFileClip

def trim_video(input_path, output_path, max_duration=20):
    """
    Trims the video to a random segment between 15-20 seconds.
    Uses original audio.
    """
    print(f"  [RENDER] Trimming video: {input_path} -> {output_path}")
    
    if not os.path.exists(input_path):
        print(f"  [ERROR] Input file not found: {input_path}")
        return None

    try:
        with VideoFileClip(input_path) as video:
            duration = video.duration
            print(f"  [RENDER] Source duration: {duration:.1f}s")
            
            if duration <= 15:
                start = 0
                end = duration
            else:
                # Random start point, ensuring at least 15s duration
                max_start = max(0, duration - max_duration)
                start = random.uniform(0, max_start)
                end = min(start + 18, duration) # Aim for 18s
            
            print(f"  [RENDER] Trimming: {start:.1f}s - {end:.1f}s")
            final_clip = video.subclipped(start, end)
            
            # Simple write
            final_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                remove_temp=True,
                logger=None
            )
            
        return output_path
    except Exception as e:
        print(f"  [ERROR] MoviePy error: {e}")
        import traceback
        traceback.print_exc()
        return None
