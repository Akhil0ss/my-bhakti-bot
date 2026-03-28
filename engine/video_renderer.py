import os
import random
import numpy as np
from moviepy import VideoFileClip

def get_loudest_segment(video, window_duration=18):
    """
    Analyzes audio energy to find the loudest/most energetic segment.
    Returns the start time of that segment.
    """
    try:
        duration = video.duration
        if duration <= window_duration:
            return 0
        
        # Access audio as array (downsample to 8kHz for speed)
        fps = 8000
        audio = video.audio.to_soundarray(fps=fps)
        
        # Convert to mono and absolute energy
        energy = np.abs(np.mean(audio, axis=1))
        
        # Calculate moving average energy for 'window_duration'
        window_size = int(window_duration * fps)
        kernel = np.ones(window_size) / window_size
        moving_avg = np.convolve(energy, kernel, mode='valid')
        
        # Find index of maximum energy
        max_idx = np.argmax(moving_avg)
        start_time = max_idx / fps
        
        # Add a small buffer (0.5s) if possible
        start_time = max(0, start_time - 0.5)
        
        print(f"  [RENDER] Smart Hook detected at {start_time:.1f}s (Energy Peak)")
        return start_time
    except Exception as e:
        print(f"  [WARN] Smart Hook analysis failed: {e}. Fallback to random.")
        return random.uniform(0, max(0, video.duration - window_duration))

def trim_video(input_path, output_path, max_duration=20):
    """
    Trims the video to the most energetic segment (18s).
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
            
            # Find the loudest segment (climax)
            target_len = 18
            if duration <= target_len:
                start = 0
                end = duration
            else:
                start = get_loudest_segment(video, window_duration=target_len)
                end = min(start + target_len, duration)
            
            print(f"  [RENDER] Final Trim: {start:.1f}s - {end:.1f}s")
            final_clip = video.subclipped(start, end)
            
            # High-speed write
            final_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                remove_temp=True,
                logger=None,
                preset="ultrafast" # Set to ultrafast for quick cloud rendering
            )
            
        return output_path
    except Exception as e:
        print(f"  [ERROR] MoviePy error: {e}")
        return None
