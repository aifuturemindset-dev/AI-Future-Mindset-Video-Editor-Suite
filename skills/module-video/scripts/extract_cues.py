#!/usr/bin/env python3
"""Pull a lesson's subtitle track out as a readable transcript.

Lessons exported from most narration tools carry a mov_text track. That track
is the only reliable way to know what the lesson says at each second, which is
what screenshot timing has to be built from. Guessing at even spacing puts
screenshots on the wrong sentence.

Usage:
    python extract_cues.py LESSON.mp4 [--srt out.srt] [--chunk 8]
"""

import argparse
import subprocess
import sys
from pathlib import Path


def to_seconds(stamp):
    hours, minutes, rest = stamp.split(":")
    seconds, millis = rest.split(",")
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000


def extract(video, srt_path):
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video), "-map", "0:s:0",
         "-f", "srt", str(srt_path), "-y"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        sys.exit("no subtitle track found in this video.\n"
                 "Without one there is no transcript to cue against. Either "
                 "supply a written script and use build_script_cut.py, or hand "
                 "the timings in directly as phase anchors.")
    return srt_path


def chunks(srt_path, window):
    blocks = Path(srt_path).read_text().strip().split("\n\n")
    out, start, buffer = [], None, []
    for block in blocks:
        lines = block.split("\n")
        if len(lines) < 3:
            continue
        at = to_seconds(lines[1].split(" --> ")[0])
        text = " ".join(lines[2:]).replace("  ", " ").strip()
        if start is None:
            start = at
        buffer.append(text)
        if at - start >= window:
            out.append((start, " ".join(buffer)))
            start, buffer = None, []
    if buffer:
        out.append((start, " ".join(buffer)))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("--srt", default=None,
                        help="where to keep the .srt (default: alongside the video)")
    parser.add_argument("--chunk", type=float, default=8.0,
                        help="seconds to merge per printed line")
    args = parser.parse_args()

    video = Path(args.video)
    srt_path = Path(args.srt) if args.srt else video.with_suffix(".srt")
    extract(video, srt_path)

    print(f"transcript: {srt_path}\n")
    for at, text in chunks(srt_path, args.chunk):
        print(f"{int(at // 60)}:{at % 60:05.2f}  {text}")

    print("\nRead the transcript and set one phase anchor per instruction the "
          "narration gives, then list that step's screenshots under it. "
          "build_overlay.py divides each phase evenly among its screenshots.")


if __name__ == "__main__":
    main()
