import os
import random
import numpy as np
import textwrap
from datetime import datetime, timezone
from moviepy.editor import VideoFileClip

def _write_short_clip(clip, output_path, watermark_text="", hook_text=""):
    """
    Writes a high-quality video with custom overlays.
    Hook text is shown for the first 0.8 seconds to serve as a thumbnail.
    """
    ffmpeg_filters = [
        "unsharp=5:5:1.0:5:5:0.0", # Sharpening
        "eq=contrast=1.1:saturation=1.2", # Better colors
    ]
    
    # Determine font path based on OS
    if os.name == 'nt':
        font_path = 'C\\\\:/Windows/Fonts/arial.ttf'
    else:
        # Common path on Ubuntu
        font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        # Fallback if the specific path doesn't exist
        if not os.path.exists(font_path):
            font_path = 'sans'

    # Hook Line Overlay (Forced Thumbnail)
    if hook_text:
        # Sanitize for FFmpeg drawtext
        safe_hook = hook_text.replace("'", "").replace(":", "").replace('"', "")
        # Wrap text to avoid overflow (safer width for Square/Vertical)
        wrapped_hook = "\\\n".join(textwrap.wrap(safe_hook, width=15))
        ffmpeg_filters.append(
            f"drawtext=text='{wrapped_hook}':fontfile='{font_path}':"
            f"fontcolor=yellow:fontsize=60:box=1:boxcolor=black@0.6:boxborderw=10:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0,0.8)'"
        )

    if watermark_text:
        ffmpeg_filters.append(
            f"drawtext=text='{watermark_text}':fontfile='{font_path}':"
            f"fontcolor=white@0.4:fontsize=32:x=w-text_w-40:y=h-text_h-40"
        )

    clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        remove_temp=True,
        logger=None,
        preset="fast",
        bitrate="8000k",
        ffmpeg_params=[
            "-vf", ",".join(ffmpeg_filters),
            "-movflags", "+faststart",
            "-pix_fmt", "yuv420p",
        ]
    )

def _find_best_hook_time(video, min_duration):
    """
    Analyzes the video to find the segment with the most motion 
    to use as a high-engagement 'Smart Hook'.
    """
    try:
        duration = video.duration
        if duration < min_duration:
            return 0
        
        # Sample points across the video
        sample_step = 2
        best_time = 0
        max_motion = 0
        
        for t in range(0, int(duration - min_duration), sample_step):
            # Compare two frames 0.5s apart to detect motion
            f1 = video.get_frame(t).mean()
            f2 = video.get_frame(t + 0.5).mean()
            motion = abs(f2 - f1)
            
            if motion > max_motion:
                max_motion = motion
                best_time = t
                
        return best_time
    except:
        return 0

def trim_video(input_path, output_path, min_duration=30, max_duration=60, watermark="", hook_line=""):
    """
    Trims with Smart Hook detection and applies high-quality rendering.
    """
    print(f"  [RENDER] Pro-Rendering video: {input_path}")
    
    if not os.path.exists(input_path):
        return None

    try:
        with VideoFileClip(input_path) as video:
            duration = video.duration
            
            # Smart Hook logic
            start = _find_best_hook_time(video, min_duration)
            target_len = min(duration - start, random.uniform(min_duration, max_duration))
            end = start + target_len

            print(f"  [RENDER] Smart Hook detected at {start:.1f}s. Duration: {target_len:.1f}s")
            
            final_clip = video.subclipped(start, end)
            _write_short_clip(final_clip, output_path, watermark_text=watermark, hook_text=hook_line)
            
        return output_path
    except Exception as e:
        print(f"  [ERROR] Pro-Render failed: {e}")
        return None

def split_video_into_parts(input_path, output_dir, part_min_duration=35, part_max_duration=45, min_source_duration=70, max_parts=3):
    """
    Splits long source into parts with loop-friendly cuts.
    """
    print(f"  [RENDER] Preparing scheduled parts from long source...")
    os.makedirs(output_dir, exist_ok=True)

    try:
        outputs = []
        batch_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        with VideoFileClip(input_path) as video:
            duration = video.duration or 0
            if duration < min_source_duration:
                return []

            start = 0.0
            part_index = 1
            while duration - start >= part_min_duration and part_index <= max_parts:
                remaining = duration - start
                part_duration = min(part_max_duration, remaining)
                if 0 < (remaining - part_duration) < part_min_duration:
                    part_duration = remaining

                end = start + part_duration
                clip = video.subclipped(start, end)
                output_path = os.path.join(output_dir, f"{batch_id}_part_{part_index}.mp4")
                
                # Using part of the source title as hook for parts
                part_hook = f"Part {part_index}"
                _write_short_clip(clip, output_path, hook_text=part_hook)
                
                outputs.append({
                    "path": output_path,
                    "part_index": part_index,
                    "start": round(start, 1),
                    "end": round(end, 1),
                    "duration": round(part_duration, 1),
                })
                start = end
                part_index += 1

        return outputs
    except Exception as e:
        print(f"  [ERROR] Pro-Split failed: {e}")
        return []
