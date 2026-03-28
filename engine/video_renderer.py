import os
import random
from moviepy import VideoFileClip

def trim_video(raw_video_path, output_dir="output"):
    """Only trims video to 15-22 seconds (Algorithm sweet spot). No edits, original quality."""
    output_path = os.path.join(output_dir, "final_short.mp4")

    print("  [INFO] Trimming video to 15-22s (No edits, 100% original quality)...")
    try:
        raw_clip = VideoFileClip(raw_video_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load raw video: {e}")

    # ALGORITHM HACK: 15-22 seconds = maximum loop rate = more views
    if raw_clip.duration <= 22:
        target_duration = raw_clip.duration
    else:
        target_duration = random.randint(15, 22)
    
    final = raw_clip.subclipped(0, target_duration)

    print(f"  [INFO] Duration: {target_duration:.1f}s | Writing H.264 HD output...")
    final.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="ultrafast",
        logger=None
    )

    raw_clip.close()
    final.close()

    print(f"  [OK] Final video ready: {output_path}")
    return output_path

if __name__ == "__main__":
    print("Video renderer module loaded.")
