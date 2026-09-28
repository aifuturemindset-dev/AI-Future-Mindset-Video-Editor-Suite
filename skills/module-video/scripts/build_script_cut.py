#!/usr/bin/env python3
"""Script cut: slides built from a written voiceover script, narrated by audio.

Use when there is a script with slides and bullets plus a voiceover recording,
but no finished lesson video. Each slide's share of the runtime comes from its
word count rather than the script's estimated chapter marks, because speech
rate is near constant within one recording while the estimates drift.

Usage:
    python build_script_cut.py config.json

See references/config-format.md for the config schema.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

import common as c


def slide_png(path, title, bullets, index, total, has_card):
    img = Image.new("RGB", (c.W, c.H), c.BRAND["background"])
    draw = ImageDraw.Draw(img)
    c.brand_chrome(draw, marker=f"{index + 1} / {total}")

    text_w = 900 if has_card else c.W - 320
    left = 120 if has_card else (c.W - text_w) // 2

    f_title = c.font(c.BOLD, 62 if has_card else 76)
    words, lines, line = title.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=f_title) <= text_w:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)

    y = 210 if has_card else 360
    for each in lines:
        tx = left if has_card else (c.W - draw.textlength(each, font=f_title)) / 2
        draw.text((tx, y), each, font=f_title, fill=c.BRAND["primary"])
        y += f_title.size + 14

    y += 40
    f_bullet = c.font(c.REGULAR, 40 if has_card else 46)
    for bullet in bullets:
        bx = (left if has_card
              else (c.W - draw.textlength(bullet, font=f_bullet)) / 2 + 30)
        draw.ellipse([bx - 34, y + 14, bx - 18, y + 30], fill=c.BRAND["primary"])
        draw.text((bx, y), bullet, font=f_bullet, fill=c.BRAND["secondary"])
        y += f_bullet.size + 34

    img.save(path)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    config = c.load_config(sys.argv[1])

    narration = Path(config["narration"])
    if not narration.exists():
        sys.exit(f"narration not found: {narration}")

    shots_dir = Path(config["screenshots_dir"])
    out_dir = Path(config["output_dir"])
    build = out_dir / "build"
    build.mkdir(parents=True, exist_ok=True)

    fade = config.get("fade", 0.35)
    card_x = config.get("card_right_margin", 60)
    card_y = config.get("card_top", 250)
    slides = config["slides"]

    total_seconds = c.duration(narration)
    weights = [len(slide["voiceover"].split()) for slide in slides]
    total_words = sum(weights)
    rate = total_words / total_seconds * 60
    print(f"narration {total_seconds:.1f}s, {total_words} words ({rate:.0f} wpm)")
    if not 80 <= rate <= 200:
        print(f"  warning: {rate:.0f} wpm is outside normal speech. This script "
              f"and this recording may not be the same take.")

    segments = []
    for index, slide in enumerate(slides):
        shots = slide.get("shots", [])
        span = total_seconds * weights[index] / total_words
        frames = int(round(span * c.FPS))
        print(f"[{index + 1}/{len(slides)}] {slide['title']}  "
              f"{span:.1f}s  {len(shots)} screenshots")

        page = build / f"slide_{index}.png"
        slide_png(page, slide["title"], slide["bullets"], index, len(slides),
                  bool(shots))

        cards = []
        for n, (filename, caption) in enumerate(shots):
            shot = shots_dir / filename
            if not shot.exists():
                sys.exit(f"screenshot not found: {shot}")
            card = build / f"card_{index}_{n}.png"
            c.screenshot_card(card, shot, n + 1, len(shots), caption)
            cards.append(card)

        cmd = ["ffmpeg", "-loop", "1", "-framerate", c.FPS, "-i", page]
        for card in cards:
            cmd += ["-loop", "1", "-i", card]
        cmd += ["-f", "lavfi", "-i",
                f"anullsrc=channel_layout=stereo:sample_rate={c.AUDIO_RATE}"]

        parts = [f"[0:v]scale={c.W}:{c.H},fps={c.FPS}[base]"]
        stream = "base"
        if cards:
            each = span / len(cards)
            for n in range(len(cards)):
                start, end = n * each, (n + 1) * each
                parts.append(
                    f"[{n + 1}:v]format=rgba,"
                    f"fade=t=in:st=0:d={fade}:alpha=1,"
                    f"fade=t=out:st={each - fade:.2f}:d={fade}:alpha=1,"
                    f"setpts=PTS+{start:.2f}/TB[o{n}]"
                )
                nxt = f"b{n}"
                parts.append(
                    f"[{stream}][o{n}]overlay=x=W-w-{card_x}:y={card_y}:"
                    f"enable='between(t,{start:.2f},{end:.2f})'[{nxt}]"
                )
                stream = nxt

        segment = build / f"seg_{index}.mp4"
        cmd += ["-filter_complex", ";".join(parts),
                "-map", f"[{stream}]", "-map", f"{len(cards) + 1}:a",
                "-frames:v", frames, *c.video_encode_args(), "-shortest",
                segment, "-y"]
        c.run(cmd, f"slide {index}")
        segments.append(segment)

    silent = build / "silent.mp4"
    c.concat(segments, silent, build)

    final = out_dir / config.get("output_name",
                                 f"Module_{config['module']}_Script.mp4")
    c.run(["ffmpeg", "-i", silent, "-i", narration,
           "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
           "-c:a", "aac", "-b:a", c.AUDIO_BITRATE, "-ar", c.AUDIO_RATE, "-ac", "2",
           "-video_track_timescale", c.TIMESCALE, "-shortest",
           "-movflags", "+faststart", final, "-y"], "mux narration")
    c.verify(final)


if __name__ == "__main__":
    main()
