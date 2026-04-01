import os
import random
from datetime import datetime, timezone
from moviepy import VideoFileClip


def _write_short_clip(clip, output_path):
    clip.write_videofile(
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
            _write_short_clip(final_clip, output_path)
            
        return output_path
    except Exception as e:
        print(f"  [ERROR] MoviePy error: {e}")
        return None


def split_video_into_parts(input_path, output_dir, part_min_duration=35, part_max_duration=40, min_source_duration=60, max_parts=3):
    print(f"  [RENDER] Preparing scheduled parts from: {input_path}")

    if not os.path.exists(input_path):
        print(f"  [ERROR] Input file not found: {input_path}")
        return []

    os.makedirs(output_dir, exist_ok=True)

    try:
        outputs = []
        batch_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        with VideoFileClip(input_path) as video:
            duration = video.duration or 0
            print(f"  [RENDER] Long-source duration: {duration:.1f}s")
            if duration < min_source_duration:
                print(f"  [INFO] Long-source queue skipped because source is under {min_source_duration}s.")
                return []

            start = 0.0
            part_index = 1
            while duration - start >= part_min_duration and part_index <= max_parts:
                remaining = duration - start
                part_duration = min(part_max_duration, remaining)
                leftover_after_cut = remaining - part_duration
                if 0 < leftover_after_cut < part_min_duration:
                    part_duration = remaining

                end = start + part_duration
                clip = video.subclipped(start, end)
                output_path = os.path.join(output_dir, f"{batch_id}_queued_part_{part_index}.mp4")
                print(f"  [RENDER] Queue Part {part_index}: {start:.1f}s - {end:.1f}s")
                _write_short_clip(clip, output_path)
                outputs.append(
                    {
                        "path": output_path,
                        "part_index": part_index,
                        "start": round(start, 1),
                        "end": round(end, 1),
                        "duration": round(part_duration, 1),
                    }
                )
                start = end
                part_index += 1

        return outputs
    except Exception as e:
        print(f"  [ERROR] Split render error: {e}")
        return []
