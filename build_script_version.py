#!/usr/bin/env python3
"""Build Module 00 from the written voiceover script.

Slides, bullets and chapter order come from the script. Timing is allocated by
word count rather than the script's estimated chapter marks, since speech rate
is near constant within one recording and the estimates drift.

Audio is Part 2. The script runs 311 words: against Part 2's 169s that is
110 wpm, a normal narration rate. Against Part 1's 486s it would be 38 wpm,
which nobody speaks, so Part 1 is a different recording. Swap NARRATION if
that turns out to be wrong.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

import build_module_00 as base
from build_module_00 import (BACKGROUND, BOLD, BUILD, H, OUT, PANEL, PRIMARY,
                             REGULAR, SECONDARY, W, concat, duration, font,
                             run, sticky_note)
from build_overlay_version import overlay_card

NARRATION = base.UPLOADS / "df510ece-Part_2_0629.mp4"
SCREENSHOTS = base.ROOT / "assets" / "screenshots"

FPS = base.FPS
FADE = 0.35
CARD_X_MARGIN = 60
CARD_Y = 250

# (title, bullets, voiceover, screenshots). Word counts in the voiceover set
# each slide's share of the runtime.
SLIDES = [
    (
        "Welcome to the AI Content Engine",
        ["You direct, Claude drafts, you approve",
         "8 modules, one weekly system",
         "Built for beginners"],
        """Welcome to the AI Content Engine. In this course you are the director
        and Claude is your crew. Claude drafts, researches, and organizes. You
        decide, approve, and publish. We go step by step, and you do not need to
        be technical. By the end, you'll have a weekly system you can actually
        run.""",
        [],
    ),
    (
        "What you'll build",
        ["A Claude Project with 8 skills",
         "A GitHub repo for your files",
         "A content calendar and funnel"],
        """Here's what you'll walk away with. A Claude Project that already knows
        your brand. Eight skills that write hooks, scripts, carousels,
        thumbnails, research, and emails. A GitHub repo that keeps your files
        organized. And a content calendar connected to a simple funnel.""",
        [],
    ),
    (
        "Step 1: Create your Claude Project",
        ["Click Projects, then Create project",
         "Name it Content Engine",
         "Paste your brand voice into instructions"],
        """Let's set up. Open claude dot ai. In the left sidebar, click Projects,
        then Create project. Name it Content Engine. Now click the instructions
        area and paste in your brand voice file. This is how Claude remembers who
        you are, who you serve, and how you sound, every time you open a new chat
        in this project.""",
        [("01-sign-in.png", "Open claude.ai"),
         ("02-projects.png", "Click Projects"),
         ("03-new-project.png", "Click Create project"),
         ("04-project-details.png", "Name it Content Engine"),
         ("05-brand-voice-file.png", "Open your brand voice"),
         ("06-select-brand-voice.png", "Paste it into instructions")],
    ),
    (
        "Step 2: Install your skills",
        ["Click Customize, then Skills",
         "Click +, then upload",
         "Upload all 8 skill zips"],
        """Next, skills. Click Customize in the left sidebar, then the Skills tab.
        Click the plus button, choose the upload option, and select the first zip
        from the skills-zips folder. Repeat until all eight are installed. Type a
        forward slash in a chat or in Cowork to see them. Menu names can shift as
        the app updates, so if a button looks different, look for the closest
        match.""",
        [("07-customize.png", "Click Customize"),
         ("08-skills-tab.png", "Open the Skills tab"),
         ("09-yours-tab.png", "Switch to Yours"),
         ("10-add.png", "Click the plus"),
         ("11-upload-skill.png", "Choose Upload skill"),
         ("12-browse-files.png", "Click Browse files"),
         ("13-open-zips.png", "Select all 8 zips")],
    ),
    (
        "Step 3: Create your repo",
        ["github.com, click New repository",
         "Name it content-engine",
         "Upload the kit, click Commit changes"],
        """Now your file home. Go to github dot com and click New repository. Name
        it content-engine and click Create. Click uploading an existing file, drag
        in the course kit, and click Commit changes. Your repo is now your single
        source of truth for skills, templates, and scripts.""",
        [("14-github-signup.png", "Go to github.com"),
         ("15-create-repository.png", "Click New repository"),
         ("16-upload-files.png", "Click uploading an existing file"),
         ("17-choose-file.png", "Choose your files"),
         ("18-course-kit.png", "Drag in the course kit"),
         ("19-commit-changes.png", "Click Commit changes")],
    ),
    (
        "Your first task",
        ["Fill in brand-voice.md",
         "Import the content calendar",
         "Introduce yourself in Skool"],
        """Your task for this module. Fill in the brand voice template. Import the
        content calendar into Google Sheets. Then head to the Skool community and
        post your niche and one content goal. Pause this video, finish these three
        things, and meet me in Module One.""",
        [("20-sheets-file.png", "Open Google Sheets"),
         ("21-import.png", "Click Import"),
         ("22-browse.png", "Click Browse"),
         ("23-open-csv.png", "Pick content-calendar.csv"),
         ("24-import-data.png", "Click Import data")],
    ),
]


def slide_png(path, title, bullets, index, total, has_card):
    img = Image.new("RGB", (W, H), BACKGROUND)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 76], fill=PANEL)
    x = 36
    for char in "AI FUTURE MINDSET":
        draw.text((x, 26), char, font=font(BOLD, 18), fill=PRIMARY)
        x += draw.textlength(char, font=font(BOLD, 18)) + 8
    marker = f"{index + 1} / {total}"
    draw.text((W - 60 - draw.textlength(marker, font=font(BOLD, 26)), 24),
              marker, font=font(BOLD, 26), fill=PRIMARY)
    draw.rectangle([0, H - 5, W, H], fill=PRIMARY)

    text_w = 900 if has_card else W - 320
    left = 120 if has_card else (W - text_w) // 2

    f_title = font(BOLD, 62 if has_card else 76)
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
        tx = left if has_card else (W - draw.textlength(each, font=f_title)) / 2
        draw.text((tx, y), each, font=f_title, fill=PRIMARY)
        y += f_title.size + 14

    y += 40
    f_bullet = font(REGULAR, 40 if has_card else 46)
    for bullet in bullets:
        bx = left if has_card else (W - draw.textlength(bullet, font=f_bullet)) / 2 + 30
        draw.ellipse([bx - 34, y + 14, bx - 18, y + 30], fill=PRIMARY)
        draw.text((bx, y), bullet, font=f_bullet, fill=SECONDARY)
        y += f_bullet.size + 34

    img.save(path)


def main():
    if not NARRATION.exists():
        sys.exit(f"missing narration: {NARRATION}")
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    total_seconds = duration(NARRATION)
    weights = [len(slide[2].split()) for slide in SLIDES]
    total_words = sum(weights)
    print(f"narration {total_seconds:.1f}s, {total_words} words "
          f"({total_words / total_seconds * 60:.0f} wpm)")

    segments = []
    for index, (title, bullets, _vo, shots) in enumerate(SLIDES):
        span = total_seconds * weights[index] / total_words
        frames = int(round(span * FPS))
        print(f"[{index + 1}/{len(SLIDES)}] {title}  {span:.1f}s  "
              f"{len(shots)} screenshots")

        page = BUILD / f"sc_slide_{index}.png"
        slide_png(page, title, bullets, index, len(SLIDES), bool(shots))

        cards = []
        for n, (filename, caption) in enumerate(shots):
            shot = SCREENSHOTS / filename
            if not shot.exists():
                sys.exit(f"missing screenshot: {shot}")
            card = BUILD / f"sc_card_{index}_{n}.png"
            overlay_card(card, shot, n + 1, len(shots), caption)
            cards.append(card)

        segment = BUILD / f"sc_seg_{index}.mp4"
        cmd = ["ffmpeg", "-loop", "1", "-framerate", str(FPS), "-i", str(page)]
        for card in cards:
            cmd += ["-loop", "1", "-i", str(card)]
        cmd += ["-f", "lavfi", "-i",
                f"anullsrc=channel_layout=stereo:sample_rate={base.AUDIO_RATE}"]

        parts = [f"[0:v]scale={W}:{H},fps={FPS}[base]"]
        stream = "base"
        if cards:
            each = span / len(cards)
            for n in range(len(cards)):
                start, end = n * each, (n + 1) * each
                parts.append(
                    f"[{n + 1}:v]format=rgba,"
                    f"fade=t=in:st=0:d={FADE}:alpha=1,"
                    f"fade=t=out:st={each - FADE:.2f}:d={FADE}:alpha=1,"
                    f"setpts=PTS+{start:.2f}/TB[o{n}]"
                )
                nxt = f"b{n}"
                parts.append(
                    f"[{stream}][o{n}]overlay="
                    f"x=W-w-{CARD_X_MARGIN}:y={CARD_Y}:"
                    f"enable='between(t,{start:.2f},{end:.2f})'[{nxt}]"
                )
                stream = nxt

        cmd += [
            "-filter_complex", ";".join(parts),
            "-map", f"[{stream}]", "-map", f"{len(cards) + 1}:a",
            "-frames:v", str(frames),
            "-c:v", "libx264", "-preset", base.PRESET, "-crf", base.CRF,
            "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "128k", "-ar", base.AUDIO_RATE, "-ac", "2",
            "-video_track_timescale", "90000", "-shortest",
            str(segment), "-y",
        ]
        run(cmd, f"slide {index}")
        segments.append(segment)

    silent = BUILD / "sc_silent.mp4"
    concat(segments, silent)

    final = OUT / "Module_00_Script.mp4"
    run(["ffmpeg", "-i", str(silent), "-i", str(NARRATION),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "128k", "-ar", base.AUDIO_RATE, "-ac", "2",
         "-video_track_timescale", "90000", "-shortest",
         "-movflags", "+faststart", str(final), "-y"], "mux narration")

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
