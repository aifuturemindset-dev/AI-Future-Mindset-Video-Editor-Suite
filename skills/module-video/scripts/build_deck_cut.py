#!/usr/bin/env python3
"""Deck cut: a rendered slide deck as the visual, narrated by a recording.

Use when the module already has a designed PowerPoint or Keynote deck. The
slides carry their own design, so branding here stays light - a slide counter
and a base rule - rather than covering the deck with a second layer of chrome.

Slide timing comes from each slide's word weight. Denser slides get more of
the runtime, which tracks narration better than splitting the audio evenly.

Render the deck to images first:
    soffice --headless --convert-to pdf --outdir DIR deck.pptx
    pdftoppm -r 150 -png DIR/deck.pdf DIR/slide

A deck with embedded fonts may refuse to load; see references/troubleshooting.md.

Usage:
    python build_deck_cut.py config.json
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

import common as c


def slide_frame(path, slide_image, index, total, chrome):
    """Fit a rendered slide onto the video canvas with light branding."""
    img = Image.new("RGB", (c.W, c.H), c.BRAND["background"])
    slide = Image.open(slide_image).convert("RGB")

    scale = min(c.W / slide.width, c.H / slide.height)
    resized = slide.resize((int(slide.width * scale), int(slide.height * scale)),
                           Image.LANCZOS)
    img.paste(resized, ((c.W - resized.width) // 2, (c.H - resized.height) // 2))

    draw = ImageDraw.Draw(img)
    if chrome != "none":
        draw.rectangle([0, c.H - 5, c.W, c.H], fill=c.BRAND["primary"])
        marker = f"{index + 1} / {total}"
        f_mark = c.font(c.BOLD, 26)
        tw = draw.textlength(marker, font=f_mark)
        draw.rectangle([c.W - tw - 86, 22, c.W - 34, 68], fill=(14, 11, 31, 255))
        draw.text((c.W - tw - 60, 28), marker, font=f_mark, fill=c.BRAND["primary"])
    if chrome == "full":
        c.tracked_text(draw, (36, 28), c.BRAND["wordmark"],
                       c.font(c.BOLD, 18), c.BRAND["primary"])
    img.save(path)


def slide_spans(slides, total_seconds):
    """Resolve each slide to (start, end).

    A slide may carry "at", a second taken from listening to the narration.
    Those anchors are honoured exactly; slides between two anchors divide the
    gap evenly. Word weight is only a fallback for a deck with no anchors at
    all, and it is a poor one: narration pace has little to do with how much
    text a slide happens to carry.
    """
    anchors = {i: float(s["at"]) for i, s in enumerate(slides) if "at" in s}
    if not anchors:
        weights = [max(1, s.get("weight", 1)) for s in slides]
        total = sum(weights)
        spans, at = [], 0.0
        for w in weights:
            span = total_seconds * w / total
            spans.append((at, at + span))
            at += span
        return spans

    anchors.setdefault(0, 0.0)
    known = sorted(anchors)
    for a, b in zip(known, known[1:]):
        if anchors[b] <= anchors[a]:
            sys.exit(f"slide {b + 1} is anchored at {anchors[b]}s, which is not "
                     f"after slide {a + 1} at {anchors[a]}s")
    if anchors[known[-1]] >= total_seconds:
        sys.exit(f"slide {known[-1] + 1} is anchored at {anchors[known[-1]]}s "
                 f"but the narration is {total_seconds:.1f}s")

    starts = [None] * len(slides)
    for i, at in anchors.items():
        starts[i] = at
    for a, b in zip(known, known[1:]):
        gap = (anchors[b] - anchors[a]) / (b - a)
        for step, i in enumerate(range(a + 1, b), start=1):
            starts[i] = anchors[a] + gap * step
    # slides after the final anchor share the remaining time
    tail = known[-1]
    if tail < len(slides) - 1:
        gap = (total_seconds - anchors[tail]) / (len(slides) - tail)
        for step, i in enumerate(range(tail + 1, len(slides)), start=1):
            starts[i] = anchors[tail] + gap * step

    return [(starts[i], starts[i + 1] if i + 1 < len(slides) else total_seconds)
            for i in range(len(slides))]


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    config = c.load_config(sys.argv[1])

    narration = Path(config["narration"])
    if not narration.exists():
        sys.exit(f"narration not found: {narration}")

    slides_dir = Path(config["slides_dir"])
    shots_dir = Path(config.get("screenshots_dir", "."))
    out_dir = Path(config["output_dir"])
    build = out_dir / "build"
    build.mkdir(parents=True, exist_ok=True)

    chrome = config.get("chrome", "minimal")
    fade = config.get("fade", 0.35)
    card_x = config.get("card_right_margin", 60)
    card_y = config.get("card_top", 420)
    slides = config["slides"]

    total_seconds = c.duration(narration)
    spans = slide_spans(slides, total_seconds)
    print(f"narration {total_seconds:.1f}s over {len(slides)} slides")

    segments = []
    for index, slide in enumerate(slides):
        source = slides_dir / slide["image"]
        if not source.exists():
            sys.exit(f"slide image not found: {source}")

        start, end = spans[index]
        span = end - start
        frames = int(round(span * c.FPS))
        shots = slide.get("shots", [])
        anchored = " (anchored)" if "at" in slide else ""
        print(f"[{index + 1:2}/{len(slides)}] {slide['image']}  "
              f"{start:6.1f}-{end:6.1f}s ({span:5.1f}s)  "
              f"{len(shots)} shots{anchored}")

        page = build / f"frame_{index:02}.png"
        slide_frame(page, source, index, len(slides), chrome)

        cards = []
        for n, (filename, caption) in enumerate(shots):
            shot = shots_dir / filename
            if not shot.exists():
                sys.exit(f"screenshot not found: {shot}")
            card = build / f"card_{index:02}_{n}.png"
            c.screenshot_card(card, shot, n + 1, len(shots), caption,
                              max_w=config.get("card_max_w", 560),
                              max_h=config.get("card_max_h", 390))
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

        segment = build / f"seg_{index:02}.mp4"
        cmd += ["-filter_complex", ";".join(parts),
                "-map", f"[{stream}]", "-map", f"{len(cards) + 1}:a",
                "-frames:v", frames, *c.video_encode_args(), "-shortest",
                segment, "-y"]
        c.run(cmd, f"slide {index}")
        segments.append(segment)

    silent = build / "silent.mp4"
    c.concat(segments, silent, build)

    final = out_dir / config.get("output_name",
                                 f"Module_{config['module']}_Deck.mp4")
    c.run(["ffmpeg", "-i", silent, "-i", narration,
           "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
           "-c:a", "aac", "-b:a", c.AUDIO_BITRATE, "-ar", c.AUDIO_RATE, "-ac", "2",
           "-video_track_timescale", c.TIMESCALE, "-shortest",
           "-movflags", "+faststart", final, "-y"], "mux narration")
    c.verify(final)


if __name__ == "__main__":
    main()
