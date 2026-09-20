#!/usr/bin/env python3
"""Build the Module 00 video with screenshots composited over the lesson.

The screenshots appear as framed cards on top of the lesson while it plays,
carrying the lesson's own audio. The Part 1 / Part 2 narration is not used.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

import build_module_00 as base
from build_module_00 import (BOLD, BUILD, H, LESSON, OUT, PRIMARY,
                             SHOTS, W, concat, duration, font, run,
                             sticky_note, title_card, still_segment,
                             lesson_chain, FPS, INTRO_SECONDS, OUTRO_SECONDS)

# Cued against the lesson's own narration, read from its mov_text subtitle
# track. Times are lesson-relative seconds. The lesson turns to GitHub at
# 51.3s and Google Sheets at 81.3s; screenshots for those steps never reached
# disk, so nothing is cued past 51.3s.
CUES = [
    ("30.png", "Sign in with Google", 10.3, 13.2),
    ("33.png", "Open Projects", 13.2, 16.0),
    ("31.png", "Click New project", 16.0, 18.4),
    ("32.png", "Add project details", 18.4, 22.5),
    ("34.png", "Open your brand voice file", 22.5, 27.0),
    ("35.png", "Select brand-voice.txt", 27.0, 32.4),
    ("36.png", "Click Customize", 32.4, 37.2),
    ("37.png", "Open the Skills tab", 37.2, 41.9),
    ("38.png", "Switch to Yours", 41.9, 46.5),
    ("39.png", "Click Add to upload skills", 46.5, 51.3),
]

FADE = 0.35

CARD_MAX_W = 620
CARD_MAX_H = 430
RIGHT_MARGIN = 70
ABOVE_LOWER_THIRD = 260


def overlay_card(path, shot, step_number, total, caption):
    """A framed screenshot with a shadow, cyan edge and a post-it caption."""
    shot_img = Image.open(shot).convert("RGB")
    scale = min(CARD_MAX_W / shot_img.width, CARD_MAX_H / shot_img.height)
    sw, sh = int(shot_img.width * scale), int(shot_img.height * scale)
    resized = shot_img.resize((sw, sh), Image.LANCZOS)

    note = sticky_note(caption, size=28, angle=-3.5)
    border, pad, header = 4, 20, 44

    card_w = sw + (border + pad) * 2
    card_h = sh + (border + pad) * 2 + header
    lift = note.height // 2
    margin = 36

    canvas = Image.new("RGBA", (card_w + margin * 2, card_h + margin * 2 + lift),
                       (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    x0, y0 = margin, margin + lift
    x1, y1 = x0 + card_w, y0 + card_h

    draw.rounded_rectangle([x0 + 12, y0 + 14, x1 + 12, y1 + 14], radius=16,
                           fill=(0, 0, 0, 135))
    draw.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=(18, 15, 32, 242))
    draw.rounded_rectangle([x0, y0, x1, y1], radius=16, outline=PRIMARY, width=3)

    badge = f"STEP {step_number} OF {total}"
    draw.text((x0 + pad + border, y0 + 12), badge, font=font(BOLD, 22), fill=PRIMARY)

    ix, iy = x0 + pad + border, y0 + header + pad + border
    draw.rectangle([ix - border, iy - border, ix + sw + border, iy + sh + border],
                   fill=PRIMARY)
    canvas.paste(resized, (ix, iy))

    canvas.alpha_composite(note, (max(0, x0 - 26), 0))
    canvas.save(path)
    return canvas.size


def main():
    if not LESSON.exists():
        sys.exit(f"missing lesson: {LESSON}")
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    lesson_seconds = duration(LESSON)
    if CUES[-1][3] > lesson_seconds:
        sys.exit(f"last cue ends {CUES[-1][3]:.1f}s but lesson is "
                 f"{lesson_seconds:.1f}s")
    for (_, caption, start, end), (_, nxt, nxt_start, _) in zip(CUES, CUES[1:]):
        if end > nxt_start:
            sys.exit(f"cue overlap: '{caption}' ends {end}s, "
                     f"'{nxt}' starts {nxt_start}s")

    print(f"lesson {lesson_seconds:.1f}s, {len(CUES)} cued overlays, "
          f"{CUES[0][2]:.1f}s to {CUES[-1][3]:.1f}s")

    print("[1/4] intro and outro cards")
    title_card(BUILD / "ov_intro.png", "MODULE 00",
               "Set Up Your AI Content Studio")
    still_segment(BUILD / "ov_intro.png", BUILD / "ov_seg_0.mp4",
                  INTRO_SECONDS * FPS, zoom=False)
    title_card(BUILD / "ov_outro.png", "YOU'RE SET UP",
               "Start creating with your AI Content Engine")
    still_segment(BUILD / "ov_outro.png", BUILD / "ov_seg_2.mp4",
                  OUTRO_SECONDS * FPS, zoom=False)

    print(f"[2/4] {len(CUES)} overlay cards")
    cards = []
    for index, (filename, caption, start, end) in enumerate(CUES):
        shot = SHOTS / filename
        if not shot.exists():
            sys.exit(f"missing screenshot: {shot}")
        card = BUILD / f"ov_card_{index}.png"
        size = overlay_card(card, shot, index + 1, len(CUES), caption)
        cards.append(card)
        print(f"      {index + 1}/{len(CUES)} {start:5.1f}-{end:5.1f}s "
              f"({end - start:.1f}s) {caption}")

    print("[3/4] compositing overlays onto the lesson")
    cmd = ["ffmpeg", "-i", str(LESSON)]
    for card, (_, _, start, end) in zip(cards, CUES):
        cmd += ["-loop", "1", "-t", f"{end - start:.2f}", "-i", str(card)]

    parts = [f"[0:v]{lesson_chain()}[base]"]
    stream = "base"
    for index, (_, _, start, end) in enumerate(CUES):
        hold = end - start
        # setpts shifts the still's clock so its fades line up with enable.
        parts.append(
            f"[{index + 1}:v]format=rgba,"
            f"fade=t=in:st=0:d={FADE}:alpha=1,"
            f"fade=t=out:st={hold - FADE:.2f}:d={FADE}:alpha=1,"
            f"setpts=PTS+{start}/TB[o{index}]"
        )
        nxt = f"b{index}"
        parts.append(
            f"[{stream}][o{index}]overlay="
            f"x=W-w-{RIGHT_MARGIN}:y=H-{ABOVE_LOWER_THIRD}-h:"
            f"enable='between(t,{start},{end})'[{nxt}]"
        )
        stream = nxt

    cmd += [
        "-filter_complex", ";".join(parts),
        "-map", f"[{stream}]", "-map", "0:a:0", "-sn",
        "-c:v", "libx264", "-preset", base.PRESET, "-crf", base.CRF,
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "128k", "-ar", base.AUDIO_RATE, "-ac", "2",
        "-video_track_timescale", "90000",
        str(BUILD / "ov_seg_1.mp4"), "-y",
    ]
    run(cmd, "overlay composite")

    print("[4/4] final assembly")
    segments = [BUILD / "ov_seg_0.mp4", BUILD / "ov_seg_1.mp4", BUILD / "ov_seg_2.mp4"]
    expected = sum(duration(s) for s in segments)
    final = OUT / "Module_00_Overlay.mp4"
    concat(segments, final)

    actual = duration(final)
    if abs(actual - expected) > 2.0:
        print(f"      drift {actual:.1f}s vs {expected:.1f}s; re-encoding")
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
        sys.exit("moov atom is not at the start")


if __name__ == "__main__":
    main()
