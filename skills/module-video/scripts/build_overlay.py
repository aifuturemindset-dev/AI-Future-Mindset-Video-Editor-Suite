#!/usr/bin/env python3
"""Overlay cut: screenshot cards float over a lesson video as it plays.

Use when the lesson already has its own narration and visuals. The screenshots
support what is being said rather than replacing it, so the lesson keeps its
audio and nothing else is mixed in.

Usage:
    python build_overlay.py config.json

See references/config-format.md for the config schema.
"""

import sys
from pathlib import Path

import common as c


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    config = c.load_config(sys.argv[1])

    lesson = Path(config["lesson"])
    if not lesson.exists():
        sys.exit(f"lesson not found: {lesson}")

    shots_dir = Path(config["screenshots_dir"])
    out_dir = Path(config["output_dir"])
    build = out_dir / "build"
    build.mkdir(parents=True, exist_ok=True)

    intro_s = config.get("intro_seconds", 3)
    outro_s = config.get("outro_seconds", 4)
    fade = config.get("fade", 0.35)
    right_margin = config.get("card_right_margin", 70)
    card_bottom = config.get("card_bottom_margin", 260)

    lesson_seconds = c.duration(lesson)
    phases = config["phases"]
    phases_end = config["phases_end"]

    cues = []
    bounds = [p["at"] for p in phases] + [phases_end]
    for index, phase in enumerate(phases):
        shots = phase["shots"]
        span = (bounds[index + 1] - phase["at"]) / len(shots)
        for offset, (filename, caption) in enumerate(shots):
            cues.append((filename, caption,
                         round(phase["at"] + offset * span, 2),
                         round(phase["at"] + (offset + 1) * span, 2)))

    if cues[-1][3] > lesson_seconds:
        sys.exit(f"last cue ends {cues[-1][3]:.1f}s but the lesson is only "
                 f"{lesson_seconds:.1f}s long")

    print(f"lesson {lesson_seconds:.1f}s, {len(cues)} cues, "
          f"{cues[0][2]:.1f}s to {cues[-1][3]:.1f}s")

    print("[1/4] title cards")
    c.title_card(build / "intro.png", config["intro_headline"],
                 config["intro_subhead"])
    c.still_segment(build / "intro.png", build / "seg_0.mp4",
                    intro_s * c.FPS, build)
    c.title_card(build / "outro.png", config["outro_headline"],
                 config["outro_subhead"])
    c.still_segment(build / "outro.png", build / "seg_2.mp4",
                    outro_s * c.FPS, build)

    print(f"[2/4] {len(cues)} screenshot cards")
    cards = []
    for index, (filename, caption, start, end) in enumerate(cues):
        shot = shots_dir / filename
        if not shot.exists():
            sys.exit(f"screenshot not found: {shot}")
        card = build / f"card_{index}.png"
        c.screenshot_card(card, shot, index + 1, len(cues), caption)
        cards.append(card)
        print(f"      {index + 1:2}/{len(cues)} {start:6.1f}-{end:6.1f}s  {caption}")

    print("[3/4] compositing onto the lesson")
    cmd = ["ffmpeg", "-i", lesson]
    for card, (_, _, start, end) in zip(cards, cues):
        cmd += ["-loop", "1", "-t", f"{end - start:.2f}", "-i", card]

    # -sn matters: a mov_text track that survives into the segments makes the
    # final concat produce a file with no moov atom, which no player will open.
    parts = [f"[0:v]{lesson_chain()}[base]"]
    stream = "base"
    for index, (_, _, start, end) in enumerate(cues):
        hold = end - start
        # setpts shifts the still's own clock so its fades line up with enable.
        parts.append(
            f"[{index + 1}:v]format=rgba,"
            f"fade=t=in:st=0:d={fade}:alpha=1,"
            f"fade=t=out:st={hold - fade:.2f}:d={fade}:alpha=1,"
            f"setpts=PTS+{start}/TB[o{index}]"
        )
        nxt = f"b{index}"
        parts.append(
            f"[{stream}][o{index}]overlay="
            f"x=W-w-{right_margin}:y=H-{card_bottom}-h:"
            f"enable='between(t,{start},{end})'[{nxt}]"
        )
        stream = nxt

    cmd += ["-filter_complex", ";".join(parts),
            "-map", f"[{stream}]", "-map", "0:a:0", "-sn",
            *c.video_encode_args(), build / "seg_1.mp4", "-y"]
    c.run(cmd, "overlay composite")

    print("[4/4] assembling")
    segments = [build / "seg_0.mp4", build / "seg_1.mp4", build / "seg_2.mp4"]
    final = out_dir / config.get("output_name",
                                 f"Module_{config['module']}_Overlay.mp4")
    c.assemble(segments, final, build)
    c.verify(final)


def lesson_chain():
    """Brand frame burned onto the lesson.

    Deliberately no lower-third step list: lessons usually carry their own
    burned-in captions along the bottom, and a panel there hides them. Put the
    step list on the title cards instead, where it covers nothing.
    """
    return (
        f"scale={c.W}:{c.H}:force_original_aspect_ratio=decrease,"
        f"pad={c.W}:{c.H}:(ow-iw)/2:(oh-ih)/2:color=0x0E0B1F,"
        f"drawbox=x=0:y=0:w=iw:h=76:color=0x0E0B1F@0.90:t=fill,"
        f"drawtext=text='{spaced(c.BRAND['wordmark'])}':x=36:y=26:"
        f"fontsize=18:fontcolor=0x4DD9E8:fontfile={c.BOLD},"
        f"drawtext=text='{c.BRAND['title']}':x=(w-text_w)/2:y=90:fontsize=50:"
        f"fontcolor=white:fontfile={c.BOLD}:borderw=3:bordercolor=0x4DD9E8,"
        f"drawbox=x=0:y=ih-4:w=iw:h=4:color=0x4DD9E8:t=fill"
    )


def spaced(text):
    """drawtext has no letter-spacing option, so space the characters."""
    return "   ".join(text)


if __name__ == "__main__":
    main()
