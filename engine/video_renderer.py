import os
import random
import subprocess
import textwrap
from datetime import datetime, timezone

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    from moviepy import VideoFileClip

def _render_with_ffmpeg(input_path, output_path, start_time, duration, watermark_text="", hook_text=""):
    """
    Renders the video using direct FFmpeg subprocess for 11-layer Digital DNA fingerprinting.
    This method is more robust than MoviePy for complex filter chains.
    """
    # 1. Random DNA Parameters
    speed = round(random.uniform(0.98, 1.02), 4)
    rot = round(random.uniform(-0.5, 0.5), 2)
    bright = round(random.uniform(-0.05, 0.05), 3)
    cont = round(random.uniform(0.95, 1.05), 2)
    sat = round(random.uniform(0.95, 1.1), 2)
    hue = round(random.uniform(-2, 2), 1)
    pitch = round(random.uniform(0.98, 1.02), 3)
    fps = random.choice([29.97, 30])
    zoom = round(random.uniform(1.01, 1.03), 3)

    print(f"  [RENDER] DNA applied: speed={speed}, rot={rot}°, pitch={pitch}, zoom={zoom}x")

    # Font path
    if os.name == 'nt':
        font_path = 'C\\\\:/Windows/Fonts/arial.ttf'
    else:
        font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        if not os.path.exists(font_path): font_path = 'sans'

    # 2. Build Video Filters (Resolution Independent)
    vf_chain = [
        f"setpts={1/speed}*PTS",
        # Scale to standard shorts size first to ensure crop works on any input
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        # Random edge crop (1-2%)
        f"crop=iw*0.98:ih*0.98:iw*0.01:ih*0.01",
        # Color & Hue
        f"eq=brightness={bright}:contrast={cont}:saturation={sat},hue=h={hue}",
        # Micro rotation
        f"rotate={rot}*PI/180:fillcolor=black:ow=iw:oh=ih",
        # Subtle Zoom & Re-scale
        f"scale=iw*{zoom}:ih*{zoom},crop=1080:1920",
        # Grain/Noise
        "noise=c0s=2:c0f=t+u",
        # FPS and Sharpening
        f"fps={fps},unsharp=5:5:0.8:5:5:0.0"
    ]

    # Add Hook Text
    if hook_text:
        safe_hook = hook_text.replace("'", "").replace(":", "").replace('"', "")
        wrapped_hook = "\\\n".join(textwrap.wrap(safe_hook, width=15))
        vf_chain.append(
            f"drawtext=text='{wrapped_hook}':fontfile='{font_path}':"
            f"fontcolor=yellow:fontsize=48:box=1:boxcolor=black@0.6:boxborderw=20:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,0,1.2)'"
        )

    # Add Watermark (Centered, 30% from bottom to stay above UI elements)
    if watermark_text:
        vf_chain.append(
            f"drawtext=text='{watermark_text}':fontfile='{font_path}':"
            f"fontcolor=white@0.4:fontsize=32:x=(w-text_w)/2:y=h*0.7"
        )

    # 3. Build Audio Filters
    af_chain = [
        f"atempo={speed}", # Match video speed
        f"asetrate=44100*{pitch},aresample=44100", # Pitch shift
        "bass=g=5:f=110:w=0.6", # Frequency fingerprint change
        "equalizer=f=120:t=h:w=200:g=1.5",
        "aecho=0.8:0.7:40:0.2", # Subtle depth
        "volume=1.1"
    ]

    # 4. Execute FFmpeg
    cmd = [
        'ffmpeg', '-y',
        '-ss', str(start_time),
        '-i', input_path,
        '-t', str(duration),
        '-vf', ",".join(vf_chain),
        '-af', ",".join(af_chain),
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
        '-c:a', 'aac', '-b:a', '128k',
        '-map_metadata', '-1', # Strip metadata
        '-fflags', '+bitexact', # Change binary hash
        output_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [ERROR] FFmpeg render failed: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"  [ERROR] Pro-Render failed: {e}")
        return False

def trim_video(input_path, output_path, min_duration=30, max_duration=60, watermark="", hook_line=""):
    """
    Trims with Smart Hook detection and applies 11-layer FFmpeg rendering.
    """
    print(f"  [RENDER] Pro-Rendering video: {input_path}")
    
    if not os.path.exists(input_path):
        return None

    try:
        with VideoFileClip(input_path) as video:
            duration = video.duration
            # Smart Hook logic
            start_point = _find_best_hook_time(video, min_duration)
            # Random jitter for temporal DNA
            jitter = random.uniform(0.1, 0.8)
            start = max(0, start_point + jitter)
            
            target_len = min(duration - start, random.uniform(min_duration, max_duration))
            
            print(f"  [RENDER] Smart Hook at {start_point:.1f}s (+{jitter:.2f}s jitter). Duration: {target_len:.1f}s")
            
            success = _render_with_ffmpeg(input_path, output_path, start, target_len, watermark, hook_line)
            
            if success and os.path.exists(output_path):
                return output_path
        return None
    except Exception as e:
        print(f"  [ERROR] Renderer wrap failed: {e}")
        return None

def split_video_into_parts(input_path, output_dir, part_min_duration=35, part_max_duration=45, min_source_duration=70, max_parts=3):
    """
    Splits long source into parts with loop-friendly cuts and 11-layer DNA.
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
                output_path = os.path.join(output_dir, f"{batch_id}_part_{part_index}.mp4")
                
                # Using part of the source title as hook for parts
                part_hook = f"Part {part_index}"
                
                # Apply 11-layer DNA even to parts
                success = _render_with_ffmpeg(input_path, output_path, start, part_duration, hook_text=part_hook)
                
                if success:
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

def _find_best_hook_time(video, min_duration):
    """Analyzes the video to find high motion segment."""
    try:
        duration = video.duration
        if duration < min_duration: return 0
        sample_step = 2
        best_time, max_motion = 0, 0
        for t in range(0, int(duration - min_duration), sample_step):
            f1 = video.get_frame(t).mean()
            f2 = video.get_frame(t + 0.5).mean()
            motion = abs(f2 - f1)
            if motion > max_motion:
                max_motion = motion
                best_time = t
        return best_time
    except: return 0
