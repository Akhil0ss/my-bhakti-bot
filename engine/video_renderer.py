import os
import random
from moviepy import VideoFileClip


def trim_video(input_path, output_path, min_duration=30, max_duration=45):
    """
    Trims from the start only.
    Final duration stays between 30s and 45s whenever source length allows it.
    """
    print(f"  [RENDER] Trimming video: {input_path} -> {output_path}")
    
    if not os.path.exists(input_path):
        print(f"  [ERROR] Input file not found: {input_path}")
        return None

    try:
        with VideoFileClip(input_path) as video:
            duration = video.duration
            print(f"  [RENDER] Source duration: {duration:.1f}s")

            start = 0
            if duration <= min_duration:
                end = duration
            else:
                target_len = min(duration, random.uniform(min_duration, max_duration))
                end = target_len

            print(f"  [RENDER] Final Trim: {start:.1f}s - {end:.1f}s")
            final_clip = video.subclipped(start, end)
            
            # High-speed write
            final_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                remove_temp=True,
                logger=None,
                preset="ultrafast",
                bitrate="5000k",
                ffmpeg_params=[
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
                    "-movflags", "+faststart",
                    "-pix_fmt", "yuv420p",
                ]
            )
            
        return output_path
    except Exception as e:
        print(f"  [ERROR] MoviePy error: {e}")
        return None
