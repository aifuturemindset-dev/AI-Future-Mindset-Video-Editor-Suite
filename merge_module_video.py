#!/usr/bin/env python3
"""Merge the Module 00 source video with the tutorial screenshots into one video.

Every segment is encoded to identical video/audio parameters and the source
subtitle track is dropped; concat fails silently on mismatched streams.
"""

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PRIMARY = "#4DD9E8"
SECONDARY = "#F3EEFF"
BACKGROUND = "#0E0B1F"

W, H = 1920, 1080
FPS = 30
VIDEO_BITRATE = "1250k"
AUDIO_BITRATE = "128k"

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

ROOT = Path(__file__).parent
BUILD = ROOT / "build"
OUT = ROOT / "output" / "videos"

SOURCE_VIDEO = Path(
    "/root/.claude/uploads/7480ea35-ff60-5ba2-b5ab-d4a76ac8bb87/"
    "04bde690-Module_00__Set_up_your_AI_content_studio.mp4"
)
SHOTS = Path("/tmp/claude-0/-home-user-AI-Future-Mindset-Video-Editor-Suite/"
             "7480ea35-ff60-5ba2-b5ab-d4a76ac8bb87/images")

STEPS = [
    ("1.png", "Sign in with Google"),
    ("4.png", "Open your Projects"),
    ("2.png", "Create a new project"),
    ("3.png", "Add your project details"),
]

INTRO_SECONDS = 3
STEP_SECONDS = 3
OUTRO_SECONDS = 4


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{' '.join(cmd)}\n{result.stderr[-2000:]}")
    return result


def font(path, size):
    return ImageFont.truetype(path, size)


def centered(draw, text, y, f, fill, max_width=1500):
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=f) <= max_width:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    for each in lines:
        width = draw.textlength(each, font=f)
        draw.text(((W - width) / 2, y), each, font=f, fill=fill)
        y += f.size + 16
    return y


def title_card(path, title, subtitle):
    img = Image.new("RGB", (W, H), BACKGROUND)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, 12], fill=PRIMARY)
    draw.rectangle([0, H - 12, W, H], fill=PRIMARY)
    y = centered(draw, title, 380, font(BOLD, 96), PRIMARY)
    centered(draw, subtitle, y + 40, font(REGULAR, 52), SECONDARY)
    img.save(path)


def step_card(path, shot, step_number, caption):
    img = Image.new("RGB", (W, H), BACKGROUND)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 110], fill="#141123")
    draw.rectangle([0, 108, W, 112], fill=PRIMARY)
    draw.text((60, 28), f"STEP {step_number}", font=font(BOLD, 52), fill=PRIMARY)
    label = caption.upper()
    draw.text((W - 60 - draw.textlength(label, font=font(REGULAR, 34)), 40),
              label, font=font(REGULAR, 34), fill=SECONDARY)

    screenshot = Image.open(shot).convert("RGB")
    box_w, box_h = W - 240, H - 300
    scale = min(box_w / screenshot.width, box_h / screenshot.height)
    resized = screenshot.resize(
        (int(screenshot.width * scale), int(screenshot.height * scale)),
        Image.LANCZOS,
    )
    x = (W - resized.width) // 2
    y = 110 + (H - 110 - resized.height) // 2
    draw.rectangle([x - 4, y - 4, x + resized.width + 4, y + resized.height + 4],
                   fill=PRIMARY)
    img.paste(resized, (x, y))
    img.save(path)


def still_to_video(png, dest, seconds):
    run([
        "ffmpeg", "-loop", "1", "-framerate", str(FPS), "-t", str(seconds), "-i", str(png),
        "-f", "lavfi", "-t", str(seconds), "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-c:v", "libx264", "-preset", "medium", "-b:v", VIDEO_BITRATE,
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-vf", f"scale={W}:{H}",
        "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", "44100", "-ac", "2",
        "-video_track_timescale", "90000",
        "-shortest", str(dest), "-y",
    ])


def normalize_source(dest):
    # -sn drops the mov_text subtitle track that breaks concat.
    run([
        "ffmpeg", "-i", str(SOURCE_VIDEO), "-sn",
        "-c:v", "libx264", "-preset", "medium", "-b:v", VIDEO_BITRATE,
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
               f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={BACKGROUND}",
        "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", "44100", "-ac", "2",
        "-video_track_timescale", "90000",
        str(dest), "-y",
    ])


def main():
    if not SOURCE_VIDEO.exists():
        sys.exit(f"source video missing: {SOURCE_VIDEO}")

    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    print("Building intro card...")
    title_card(BUILD / "intro.png", "AI CONTENT ENGINE",
               "Module 00: Set Up Your AI Content Studio")
    still_to_video(BUILD / "intro.png", BUILD / "seg_00.mp4", INTRO_SECONDS)

    print("Normalizing source video (dropping subtitle track)...")
    normalize_source(BUILD / "seg_01.mp4")

    segments = [BUILD / "seg_00.mp4", BUILD / "seg_01.mp4"]

    for index, (filename, caption) in enumerate(STEPS, start=1):
        shot = SHOTS / filename
        if not shot.exists():
            sys.exit(f"screenshot missing: {shot}")
        print(f"Building step {index}: {caption}")
        png = BUILD / f"step_{index}.png"
        step_card(png, shot, index, caption)
        segment = BUILD / f"seg_{index + 1:02d}.mp4"
        still_to_video(png, segment, STEP_SECONDS)
        segments.append(segment)

    print("Building outro card...")
    title_card(BUILD / "outro.png", "Ready to Build?",
               "Start creating with your AI Content Engine today")
    outro = BUILD / f"seg_{len(segments):02d}.mp4"
    still_to_video(BUILD / "outro.png", outro, OUTRO_SECONDS)
    segments.append(outro)

    concat_file = BUILD / "concat.txt"
    concat_file.write_text("".join(f"file '{s.name}'\n" for s in segments))

    final = OUT / "Module_00_Merged.mp4"
    print("Merging all segments...")
    run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c:v", "libx264", "-preset", "medium", "-b:v", VIDEO_BITRATE,
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", "44100", "-ac", "2",
        "-movflags", "+faststart",
        str(final), "-y",
    ])

    probe = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size", "-of", "json", str(final),
    ], capture_output=True, text=True)
    info = json.loads(probe.stdout)["format"]
    duration = float(info["duration"])
    size_mb = int(info["size"]) / (1024 * 1024)

    print(f"\nDone: {final}")
    print(f"  Duration: {int(duration // 60)}m {duration % 60:.1f}s")
    print(f"  Size: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
