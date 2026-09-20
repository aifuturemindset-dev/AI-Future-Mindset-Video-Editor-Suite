#!/usr/bin/env python3
"""Transcribe the Part 1 / Part 2 narration so screenshots can be cued to it.

The lesson ships a mov_text subtitle track, but the narration recordings do
not, so their timeline has to be recovered with ASR.

This cannot run in the Claude Code web environment: PyPI is reachable but the
model host is blocked by the egress proxy (403), so the weights never download.
Run it somewhere with open network access to produce the transcript, then cue
the screenshots against it the way build_overlay_version.py does for the lesson.
"""

import json
import sys
from pathlib import Path

UPLOADS = Path("/root/.claude/uploads/7480ea35-ff60-5ba2-b5ab-d4a76ac8bb87")
PARTS = [
    ("part1", UPLOADS / "8f2110fc-Part_1_0629.mp4"),
    ("part2", UPLOADS / "df510ece-Part_2_0629.mp4"),
]
OUT = Path("/home/user/AI-Future-Mindset-Video-Editor-Suite/build/narration_transcript.json")


def main():
    from faster_whisper import WhisperModel

    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    result = {}
    offset = 0.0
    for name, source in PARTS:
        if not source.exists():
            sys.exit(f"missing: {source}")
        print(f"transcribing {name}", flush=True)
        segments, info = model.transcribe(str(source), vad_filter=True)
        rows = []
        for seg in segments:
            rows.append({
                "start": round(seg.start + offset, 2),
                "end": round(seg.end + offset, 2),
                "text": seg.text.strip(),
            })
            if len(rows) % 25 == 0:
                print(f"  {name} {seg.end:.0f}s", flush=True)
        result[name] = rows
        offset += info.duration
        print(f"  {name}: {len(rows)} segments, {info.duration:.1f}s", flush=True)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
