#!/usr/bin/env python3
"""Forced-align a script to its narration. Use this before anything else.

This is the most accurate timing route that needs no network and no model
download, and it should be the first thing tried whenever a written script
and its recording both exist.

It is not ASR. aeneas synthesises the script with espeak and warps that
against the real audio (DTW over MFCCs), so it never has to recognise a
word - it only has to line up two versions of the same sentence. That is a
much easier problem, and it is why this works where every ASR model host is
blocked.

Why this exists at all: the pause-matching aligner in align_script.py was
used to cut a five-minute video and drifted by up to ten seconds in the
middle while looking correct at both ends. The person watching caught it,
not the checks. Pause matching only ever knows where the gaps are, so a
single mis-grouped line early on shifts everything after it and nothing in
the audio contradicts it. Forced alignment knows what the words sound like.
Prefer it; keep align_script.py only for audio where aeneas cannot run.

Setup (aeneas is from 2017 and needs three fixes on a modern box):

    apt-get install -y espeak espeak-ng libespeak-dev
    python3 -m venv --system-site-packages .aeneas-venv
    .aeneas-venv/bin/pip install "setuptools==59.8.0" wheel scipy
    .aeneas-venv/bin/pip install aeneas
    sed -i 's/numpy\\.fromstring(/numpy.frombuffer(/g' \\
        .aeneas-venv/lib/python*/site-packages/aeneas/wavfile.py

The three fixes: setuptools must be pinned (modern setuptools drops the
install_layout option aeneas's setup.py sets), scipy must be present (without
it aeneas reports the misleading "Audio format not supported by scipywavread"),
and numpy.fromstring was removed in numpy 2 so aeneas's bundled wav reader
needs frombuffer.

Usage:
    python align_forced.py NARRATION.(mov|mp4|mp3|wav) script.txt -o aligned.json

script.txt is one spoken line per row. Blank rows are ignored; rows matching
--skip-pattern are treated as section labels. A title line the narrator never
reads must NOT be in the file - it swallows the opening seconds and shifts
everything after it.
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

VENV = Path(__file__).resolve().parent / ".aeneas-venv"


def aeneas_python():
    """The interpreter that has aeneas.

    AENEAS_PYTHON wins, then a venv beside this script, then the current
    interpreter. The venv is deliberately not committed - it is ~100 MB of
    compiled wheels - so set the variable or create it where the setup block
    says.
    """
    import os

    candidates = [Path(p) for p in (os.environ.get("AENEAS_PYTHON"),) if p]
    candidates += [VENV / "bin" / "python", Path(sys.executable)]
    for candidate in candidates:
        if not candidate.exists():
            continue
        ok = subprocess.run([str(candidate), "-c", "import aeneas"],
                            capture_output=True)
        if ok.returncode == 0:
            return str(candidate)
    sys.exit("aeneas is not installed - see the setup block at the top of "
             "this file. Falling back to align_script.py is a downgrade; it "
             "drifts on long reads.")


def to_wav(src, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vn",
                    "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
                    str(dst), "-y"], check=True)


def speech_segments(wav, noise_db=-33.0, min_silence=0.30):
    """Energy-based speech spans, used only to check and tidy the result."""
    log = subprocess.run(
        ["ffmpeg", "-i", str(wav), "-af",
         f"silencedetect=noise={noise_db}dB:d={min_silence}", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    starts = [float(m) for m in re.findall(r"silence_start: (-?[0-9.]+)", log)]
    ends = [float(m) for m in re.findall(r"silence_end: ([0-9.]+)", log)]
    total = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(wav)], capture_output=True, text=True).stdout)
    spans, cursor = [], 0.0
    for i, s in enumerate(starts):
        if s > cursor + 0.05:
            spans.append((cursor, s))
        cursor = ends[i] if i < len(ends) else total
    if cursor < total - 0.05:
        spans.append((cursor, total))
    return spans, total


def run_aeneas(python, wav, fragments, workdir):
    frag_file = workdir / "fragments.txt"
    frag_file.write_text("\n".join(fragments) + "\n")
    out = workdir / "sync.json"
    proc = subprocess.run(
        [python, "-m", "aeneas.tools.execute_task", str(wav), str(frag_file),
         "task_language=eng|is_text_type=plain|os_task_file_format=json",
         str(out)],
        capture_output=True, text=True)
    if not out.exists():
        sys.exit(f"aeneas failed:\n{proc.stderr[-1500:]}")
    return json.loads(out.read_text())["fragments"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("narration")
    ap.add_argument("script")
    ap.add_argument("-o", "--output", default="aligned.json")
    ap.add_argument("--skip-pattern", default=r"^(HOOK|RE-HOOK|I|WE|YOU)\s+[—-]\s+")
    args = ap.parse_args()

    skip = re.compile(args.skip_pattern)
    lines = [l.strip() for l in Path(args.script).read_text().splitlines()]
    lines = [l for l in lines if l and not skip.match(l)]

    python = aeneas_python()
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        wav = work / "mono16k.wav"
        to_wav(args.narration, wav)
        frags = run_aeneas(python, wav, lines, work)
        spans, total = speech_segments(wav)

    # aeneas returns contiguous fragments - each end is the next begin - so a
    # line's "end" is not where speech stops. Pull it back to the last speech
    # boundary inside the fragment, which is what a cut wants.
    stops = [b for _, b in spans]
    result = []
    for i, f in enumerate(frags):
        begin, end = round(float(f["begin"]), 2), float(f["end"])
        inside = [t for t in stops if begin + 0.25 < t <= end + 0.05]
        result.append({"index": i, "text": f["lines"][0],
                       "start": begin,
                       "end": round(inside[-1] if inside else end, 2)})

    Path(args.output).write_text(json.dumps(result, indent=1, ensure_ascii=False))

    # Verification: a narrator pauses longest where the argument turns, so the
    # recording's big pauses should sit just before a line start. This is an
    # independent measurement - energy, not MFCC warping - so agreement here
    # means two different methods concur.
    gaps = sorted(((b[0] - a[1], b[0]) for a, b in zip(spans, spans[1:])),
                  reverse=True)[:20]
    hits = 0
    print(f"\n{len(result)} lines aligned   first word {result[0]['start']:.2f}s"
          f"   last {result[-1]['end']:.2f}s of {total:.2f}s")
    print("\nLongest pauses vs the line that follows:\n")
    for d, resume in sorted(gaps, key=lambda g: g[1]):
        near = min(result, key=lambda r: abs(r["start"] - resume))
        err = near["start"] - resume
        if abs(err) < 0.6:
            hits += 1
        print(f"  {d:4.2f}s pause -> {err:+5.2f}s  {near['text'][:52]}")
    print(f"\n{hits}/{len(gaps)} big pauses land within 0.6s of a line start.")
    print("Confirm the first lines above are really the first thing said.")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
