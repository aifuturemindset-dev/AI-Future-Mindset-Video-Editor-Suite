#!/usr/bin/env python3
"""Build the complete Module 00 tutorial video.

Sources:
  - Module_00__Set_up_your_AI_content_studio.mp4  animated lesson, has visuals
  - Part_1_0629.mp4 / Part_2_0629.mp4             narration only (20 kbps black
                                                   video track, 195 kbps audio)
  - 10 tutorial screenshots

The narration plays over the screenshots. Every segment is encoded to identical
parameters so the final concat can stream-copy; mismatched parameters are what
produced the earlier unplayable file.
"""

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PRIMARY = "#4DD9E8"
SECONDARY = "#F3EEFF"
BACKGROUND = "#0E0B1F"
PANEL = "#141123"
POSTIT = "#FFE86B"
POSTIT_INK = "#2A2416"

W, H = 1920, 1080
FPS = 30
CRF = "20"
PRESET = "fast"
AUDIO_RATE = "48000"

# Comic Neue via apt; fonts.google.com is blocked by the proxy.
BOLD = "/usr/share/fonts/opentype/comic-neue/ComicNeue-Bold.otf"
REGULAR = "/usr/share/fonts/opentype/comic-neue/ComicNeue-Regular.otf"

ROOT = Path(__file__).parent
BUILD = ROOT / "build"
OUT = ROOT / "output" / "videos"

UPLOADS = Path("/root/.claude/uploads/7480ea35-ff60-5ba2-b5ab-d4a76ac8bb87")
LESSON = UPLOADS / "04bde690-Module_00__Set_up_your_AI_content_studio.mp4"
NARRATION = [UPLOADS / "8f2110fc-Part_1_0629.mp4", UPLOADS / "df510ece-Part_2_0629.mp4"]
SHOTS = Path("/tmp/claude-0/-home-user-AI-Future-Mindset-Video-Editor-Suite/"
             "7480ea35-ff60-5ba2-b5ab-d4a76ac8bb87/images")

COURSE_STEPS = [
    "Install Claude Desktop",
    "Create your Project",
    "Load brand voice",
    "Install 8 skills",
    "Upload to GitHub",
]

# (screenshot, caption, which COURSE_STEPS entry is active)
SCREENS = [
    ("30.png", "Sign in with Google", 1),
    ("33.png", "Open Projects", 2),
    ("31.png", "Click New project", 2),
    ("32.png", "Add project details", 2),
    ("34.png", "Open your brand voice file", 3),
    ("35.png", "Select brand-voice.txt", 3),
    ("36.png", "Click Customize", 4),
    ("37.png", "Open the Skills tab", 4),
    ("38.png", "Switch to Yours", 4),
    ("39.png", "Click Add to upload skills", 4),
]

INTRO_SECONDS = 3
OUTRO_SECONDS = 4


def run(cmd, label):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"[{label}] ffmpeg failed:\n{' '.join(map(str, cmd))}\n"
                 f"{result.stderr[-2500:]}")
    return result


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def font(path, size):
    return ImageFont.truetype(path, size)


def tracked(draw, xy, text, f, fill, spacing):
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=f, fill=fill)
        x += draw.textlength(char, font=f) + spacing


def sticky_note(text, size=38, angle=-2.5):
    """The caption as a tilted post-it with a shadow and a folded corner."""
    f = font(BOLD, size)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    pad_x, pad_y = 46, 28
    nw = int(probe.textlength(text, font=f) + pad_x * 2)
    nh = int(size + pad_y * 2)
    margin = 28

    canvas = Image.new("RGBA", (nw + margin * 2, nh + margin * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([margin + 8, margin + 10, margin + nw + 8, margin + nh + 10],
                   fill=(0, 0, 0, 120))
    draw.rectangle([margin, margin, margin + nw, margin + nh], fill=POSTIT)
    fold = 26
    draw.polygon([(margin + nw - fold, margin + nh), (margin + nw, margin + nh - fold),
                  (margin + nw, margin + nh)], fill="#E3CC55")
    draw.text((margin + pad_x, margin + pad_y - 6), text, font=f, fill=POSTIT_INK)
    return canvas.rotate(angle, resample=Image.BICUBIC, expand=True)


def chrome(img, draw, active_step=None):
    """The branded frame: top bar, wordmark, five-step lower third."""
    draw.rectangle([0, 0, W, 76], fill=PANEL)
    tracked(draw, (36, 26), "AI FUTURE MINDSET", font(BOLD, 18), PRIMARY, 8)

    title = "AI CONTENT ENGINE"
    f_title = font(BOLD, 50)
    tx = (W - draw.textlength(title, font=f_title)) / 2
    draw.text((tx, 90), title, font=f_title, fill="#FFFFFF",
              stroke_width=3, stroke_fill=PRIMARY)

    draw.rectangle([0, H - 220, W, H], fill=PANEL)
    draw.rectangle([0, H - 4, W, H], fill=PRIMARY)

    layout = [(0, 60, 110, H - 196), (1, 60, 110, H - 130), (2, 60, 110, H - 64),
              (3, 960, 1010, H - 196), (4, 960, 1010, H - 130)]
    for index, num_x, text_x, y in layout:
        is_active = active_step == index + 1
        num_color = PRIMARY
        text_color = "#FFFFFF" if is_active else SECONDARY
        if is_active:
            draw.rectangle([num_x - 18, y - 8, num_x - 12, y + 32], fill=PRIMARY)
        draw.text((num_x, y), f"{index + 1}.", font=font(BOLD, 22), fill=num_color)
        draw.text((text_x, y + 2), COURSE_STEPS[index],
                  font=font(BOLD if is_active else REGULAR, 20), fill=text_color)


def title_card(path, headline, subhead):
    img = Image.new("RGB", (W, H), BACKGROUND)
    draw = ImageDraw.Draw(img)
    chrome(img, draw)

    f_head = font(BOLD, 88)
    hx = (W - draw.textlength(headline, font=f_head)) / 2
    draw.text((hx, 420), headline, font=f_head, fill=PRIMARY)

    f_sub = font(REGULAR, 44)
    sx = (W - draw.textlength(subhead, font=f_sub)) / 2
    draw.text((sx, 540), subhead, font=f_sub, fill=SECONDARY)
    img.save(path)


def screen_card(path, shot, position, total, caption, active_step):
    img = Image.new("RGB", (W, H), BACKGROUND)
    draw = ImageDraw.Draw(img)
    chrome(img, draw, active_step)

    note = sticky_note(caption)
    note_y = 126
    img.paste(note, ((W - note.width) // 2, note_y), note)

    top = note_y + note.height + 4
    bottom = H - 232
    box_w, box_h = W - 320, bottom - top
    shot_img = Image.open(shot).convert("RGB")
    scale = min(box_w / shot_img.width, box_h / shot_img.height)
    resized = shot_img.resize(
        (int(shot_img.width * scale), int(shot_img.height * scale)), Image.LANCZOS)
    x = (W - resized.width) // 2
    y = top + (box_h - resized.height) // 2
    draw.rectangle([x - 3, y - 3, x + resized.width + 3, y + resized.height + 3],
                   fill=PRIMARY)
    img.paste(resized, (x, y))

    marker = f"{position} / {total}"
    draw.text((W - 60 - draw.textlength(marker, font=font(BOLD, 28)), 30),
              marker, font=font(BOLD, 28), fill=PRIMARY)

    bar_y = H - 232
    draw.rectangle([0, bar_y, W, bar_y + 5], fill=PANEL)
    draw.rectangle([0, bar_y, int(W * position / total), bar_y + 5], fill=PRIMARY)
    img.save(path)


def still_segment(png, dest, frames, zoom=True):
    """A still as video with a slow push-in, plus the silent audio concat needs."""
    if zoom:
        vf = (f"zoompan=z='min(1+0.00004*on,1.05)':d={frames}:"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    else:
        vf = f"scale={W}:{H},fps={FPS}"
    run([
        "ffmpeg", "-loop", "1", "-framerate", str(FPS), "-i", str(png),
        "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate={AUDIO_RATE}",
        "-frames:v", str(frames), "-vf", vf,
        "-c:v", "libx264", "-preset", PRESET, "-crf", CRF, "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-c:a", "aac", "-b:a", "128k", "-ar", AUDIO_RATE, "-ac", "2",
        "-video_track_timescale", "90000", "-shortest", str(dest), "-y",
    ], f"still {png.name}")


def concat(files, dest, copy=True):
    # Absolute paths: relative ones resolve against the listing's directory,
    # which is not the segments' directory when dest lives elsewhere.
    listing = dest.with_suffix(".txt")
    listing.write_text("".join(f"file '{f.resolve()}'\n" for f in files))
    codec = ["-c", "copy"] if copy else [
        "-c:v", "libx264", "-preset", PRESET, "-crf", CRF, "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-c:a", "aac", "-b:a", "128k", "-ar", AUDIO_RATE, "-ac", "2",
    ]
    run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", str(listing),
         *codec, "-movflags", "+faststart", str(dest), "-y"], f"concat {dest.name}")


def main():
    for path in [LESSON, *NARRATION]:
        if not path.exists():
            sys.exit(f"missing source: {path}")
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    print("[1/6] intro card")
    title_card(BUILD / "intro.png", "MODULE 00",
               "Set Up Your AI Content Studio")
    still_segment(BUILD / "intro.png", BUILD / "seg_0.mp4",
                  INTRO_SECONDS * FPS, zoom=False)

    print("[2/6] lesson video with burned-in overlay")
    # -sn drops the mov_text subtitle track; it is what broke the earlier concat.
    overlay = (
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x0E0B1F,"
        f"drawbox=x=0:y=0:w=iw:h=76:color=0x0E0B1F@0.90:t=fill,"
        f"drawtext=text='A I   F U T U R E   M I N D S E T':x=36:y=26:"
        f"fontsize=18:fontcolor=0x4DD9E8:fontfile={BOLD},"
        f"drawtext=text='AI CONTENT ENGINE':x=(w-text_w)/2:y=90:fontsize=50:"
        f"fontcolor=white:fontfile={BOLD}:borderw=3:bordercolor=0x4DD9E8,"
        f"drawbox=x=0:y=ih-220:w=iw:h=220:color=0x0E0B1F@0.91:t=fill,"
        f"drawbox=x=0:y=ih-4:w=iw:h=4:color=0x4DD9E8:t=fill"
    )
    for index, label in enumerate(COURSE_STEPS):
        num_x, text_x = (60, 110) if index < 3 else (960, 1010)
        y = [196, 130, 64, 196, 130][index]
        # drawtext exposes h, not ih; ih is drawbox-only.
        overlay += (
            f",drawtext=text='{index + 1}.':fontsize=22:fontcolor=0x4DD9E8:"
            f"fontfile={BOLD}:x={num_x}:y=h-{y}"
            f",drawtext=text='{label}':fontsize=20:fontcolor=0xF3EEFF:"
            f"fontfile={REGULAR}:x={text_x}:y=h-{y - 2}"
        )
    run([
        "ffmpeg", "-i", str(LESSON), "-sn", "-vf", overlay,
        "-c:v", "libx264", "-preset", PRESET, "-crf", CRF, "-pix_fmt", "yuv420p",
        "-r", str(FPS), "-c:a", "aac", "-b:a", "128k", "-ar", AUDIO_RATE, "-ac", "2",
        "-video_track_timescale", "90000", str(BUILD / "seg_1.mp4"), "-y",
    ], "lesson overlay")

    print("[3/6] narration track")
    narration_parts = []
    for index, source in enumerate(NARRATION):
        part = BUILD / f"narr_{index}.m4a"
        run(["ffmpeg", "-i", str(source), "-vn", "-c:a", "aac", "-b:a", "128k",
             "-ar", AUDIO_RATE, "-ac", "2", str(part), "-y"], f"narration {index}")
        narration_parts.append(part)
    narration = BUILD / "narration.m4a"
    listing = BUILD / "narration.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in narration_parts))
    run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-c", "copy", str(narration), "-y"], "narration concat")
    narration_seconds = duration(narration)
    print(f"      narration: {narration_seconds:.1f}s")

    print(f"[4/6] {len(SCREENS)} screenshot cards")
    total_frames = int(round(narration_seconds * FPS))
    per_card = total_frames // len(SCREENS)
    slides = []
    for index, (filename, caption, active) in enumerate(SCREENS):
        shot = SHOTS / filename
        if not shot.exists():
            sys.exit(f"missing screenshot: {shot}")
        png = BUILD / f"card_{index}.png"
        screen_card(png, shot, index + 1, len(SCREENS), caption, active)
        frames = per_card if index < len(SCREENS) - 1 else total_frames - per_card * (len(SCREENS) - 1)
        segment = BUILD / f"slide_{index}.mp4"
        still_segment(png, segment, frames)
        slides.append(segment)
        print(f"      {index + 1}/{len(SCREENS)} {caption} ({frames / FPS:.1f}s)")

    slideshow = BUILD / "slideshow.mp4"
    concat(slides, slideshow)
    run(["ffmpeg", "-i", str(slideshow), "-i", str(narration),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "128k", "-ar", AUDIO_RATE, "-ac", "2",
         "-video_track_timescale", "90000", "-shortest",
         str(BUILD / "seg_2.mp4"), "-y"], "mux narration")

    print("[5/6] outro card")
    title_card(BUILD / "outro.png", "YOU'RE SET UP",
               "Start creating with your AI Content Engine")
    still_segment(BUILD / "outro.png", BUILD / "seg_3.mp4",
                  OUTRO_SECONDS * FPS, zoom=False)

    print("[6/6] final assembly")
    segments = [BUILD / f"seg_{i}.mp4" for i in range(4)]
    expected = sum(duration(s) for s in segments)
    final = OUT / "Module_00_Complete_Tutorial.mp4"
    concat(segments, final)

    actual = duration(final)
    if abs(actual - expected) > 2.0:
        print(f"      stream-copy concat drifted "
              f"({actual:.1f}s vs {expected:.1f}s); re-encoding")
        concat(segments, final, copy=False)
        actual = duration(final)

    size_mb = final.stat().st_size / (1024 * 1024)
    with open(final, "rb") as handle:
        faststart = b"moov" in handle.read(4096)

    print(f"\n{final}")
    print(f"  Duration : {int(actual // 60)}m {actual % 60:04.1f}s")
    print(f"  Size     : {size_mb:.1f} MB")
    print(f"  faststart: {faststart}")
    if not faststart:
        sys.exit("moov atom is not at the start - the file will not stream")


if __name__ == "__main__":
    main()
