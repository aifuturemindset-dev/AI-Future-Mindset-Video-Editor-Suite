#!/usr/bin/env python3
"""Align a written script to its narration recording, line by line.

This is the third timing route, after a subtitle track and marks from whoever
recorded it, and it is the one that works when neither exists and ASR hosts
are blocked. It needs no model download - only ffmpeg and the script itself.

It works when the read pauses between lines, which a scripted delivery
usually does and a continuous read does not. Check before trusting it: the
report at the end prints how many segments were found against how many lines
there are. Roughly comparable numbers mean the read is separable. One long
segment means it is not, and no amount of tuning will change that - go back
and ask for marks.

How it works:

1. ffmpeg's silencedetect splits the audio into speech segments, one per
   breath group.
2. The counts never match one to one - long lines are split across breaths,
   short ones are run together. So a run of lines maps to a run of segments,
   monotonically, and the best such mapping is a shortest path. Solving it
   beats any greedy scan, which drifts and never recovers.
3. Inside a group, lines divide the span by character count.

Cost is relative error against each line's predicted duration, so a
two-word line is judged as strictly as a long one.

Usage:
    python align_script.py NARRATION.(mp4|mov|mp3|wav) SCRIPT.txt [-o out.json]

SCRIPT.txt is one spoken line per row. Blank rows are ignored. Rows that are
section labels rather than speech (``HOOK - The Folder``) are skipped when
they match --skip-pattern.

Verify the result before building on it. The report prints the longest
pauses and the line each one precedes: those should land on the script's
structural breaks. If they do, the alignment is not drifting. If a pause
lands mid-sentence, it is.
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

MAX_LINES_PER_GROUP = 3
MAX_SEGS_PER_GROUP = 4


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True).stdout.strip()
    return float(out)


def speech_segments(path, noise_db, min_silence):
    """Speech spans, as the complement of the detected silences.

    The audio is normalised to 16 kHz mono first. silencedetect measures RMS,
    so the same recording read from a .mov and from an extracted .wav gives
    slightly different boundaries otherwise, and the cue times then depend on
    which file you happened to point at.
    """
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "mono16k.wav"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(path), "-vn",
             "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav), "-y"],
            check=True, capture_output=True)
        proc = subprocess.run(
            ["ffmpeg", "-i", str(wav), "-af",
             f"silencedetect=noise={noise_db}dB:d={min_silence}", "-f", "null", "-"],
            capture_output=True, text=True)
        log = proc.stderr

    starts = [float(m) for m in re.findall(r"silence_start: (-?[0-9.]+)", log)]
    ends = [float(m) for m in re.findall(r"silence_end: ([0-9.]+)", log)]
    total = probe_duration(path)

    segments, cursor = [], 0.0
    for i, s in enumerate(starts):
        if s > cursor + 0.05:
            segments.append((cursor, s))
        cursor = ends[i] if i < len(ends) else total
    if cursor < total - 0.05:
        segments.append((cursor, total))
    return segments, total


def weight(line):
    """Predicted spoken length. Characters track duration better than words
    for scripts written as short clauses."""
    return max(4, len(re.sub(r"[^A-Za-z0-9' ]", "", line)))


def align(lines, segments):
    weights = [weight(l) for l in lines]
    durations = [b - a for a, b in segments]
    rate = sum(durations) / sum(weights)
    expected = [w * rate for w in weights]

    n_lines, n_segs = len(lines), len(segments)
    if n_segs < n_lines:
        sys.exit(f"only {n_segs} speech segments for {n_lines} lines - the read "
                 "does not pause between lines, so it cannot be split this way. "
                 "Ask for timing marks instead.")

    pre_seg, pre_exp = [0.0], [0.0]
    for d in durations:
        pre_seg.append(pre_seg[-1] + d)
    for e in expected:
        pre_exp.append(pre_exp[-1] + e)

    INF = float("inf")
    dp = [[INF] * (n_segs + 1) for _ in range(n_lines + 1)]
    back = [[None] * (n_segs + 1) for _ in range(n_lines + 1)]
    dp[0][0] = 0.0

    for i in range(1, n_lines + 1):
        for j in range(1, n_segs + 1):
            best, chosen = INF, None
            for a in range(1, MAX_LINES_PER_GROUP + 1):
                pi = i - a
                if pi < 0:
                    continue
                for b in range(1, MAX_SEGS_PER_GROUP + 1):
                    pj = j - b
                    if pj < 0 or dp[pi][pj] == INF:
                        continue
                    span = pre_seg[j] - pre_seg[pj]
                    want = pre_exp[i] - pre_exp[pi]
                    # Nudged toward the simple one-to-one reading, so groups
                    # form only where the timing really demands them.
                    cost = abs(span - want) / want + 0.10 * (a - 1) + 0.10 * (b - 1)
                    if dp[pi][pj] + cost < best:
                        best, chosen = dp[pi][pj] + cost, (pi, pj)
            dp[i][j], back[i][j] = best, chosen

    if dp[n_lines][n_segs] == INF:
        sys.exit("no alignment found - try a different --noise threshold.")

    i, j, groups = n_lines, n_segs, []
    while i > 0:
        pi, pj = back[i][j]
        groups.append((pi, i, pj, j))
        i, j = pi, pj
    groups.reverse()

    result = []
    for lo, hi, si, sj in groups:
        t0, t1 = segments[si][0], segments[sj - 1][1]
        total_w = sum(weights[lo:hi]) or 1
        cursor = t0
        for k in range(lo, hi):
            share = (t1 - t0) * weights[k] / total_w
            result.append({"index": k, "text": lines[k],
                           "start": round(cursor, 2),
                           "end": round(cursor + share, 2)})
            cursor += share
    return result, dp[n_lines][n_segs] / n_lines


def report(result, segments, total):
    """Print the checks that tell you whether to trust this."""
    print(f"\n{len(result)} lines aligned over {len(segments)} speech segments")
    print(f"first word {result[0]['start']:.2f}s   "
          f"last word ends {result[-1]['end']:.2f}s   of {total:.2f}s")

    # The opening lines catch the most common mistake by far: a title or a
    # heading left in the script file, which the narrator never reads. It
    # swallows the first seconds and shifts every cue after it, and the cost
    # figure stays low enough to look fine. Read these and check the first
    # line really is the first thing said.
    print("\nOpening lines - confirm the narrator actually says these, in this "
          "order:\n")
    for r in result[:5]:
        print(f"  {r['start']:7.2f} - {r['end']:7.2f}  {r['text'][:62]}")
    print("  ...")
    for r in result[-2:]:
        print(f"  {r['start']:7.2f} - {r['end']:7.2f}  {r['text'][:62]}")

    gaps = sorted(((b[0] - a[1], a[1], b[0])
                   for a, b in zip(segments, segments[1:])), reverse=True)
    print("\nLongest pauses, and the line each precedes. These should land on "
          "the script's\nsection breaks - if they do, the alignment is not "
          "drifting.\n")
    for d, _, resume in gaps[:12]:
        after = [r for r in result if r["start"] >= resume - 0.35]
        text = after[0]["text"][:62] if after else "(end)"
        print(f"  {d:4.2f}s  ->  {text}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("narration")
    ap.add_argument("script")
    ap.add_argument("-o", "--output", default="aligned.json")
    ap.add_argument("--noise", type=float, default=-33.0,
                    help="silence threshold in dB (default -33)")
    ap.add_argument("--min-silence", type=float, default=0.30,
                    help="shortest gap counted as a pause, seconds")
    ap.add_argument("--skip-pattern", default=r"^(HOOK|RE-HOOK|I|WE|YOU)\s+[—-]\s+",
                    help="rows matching this are labels, not speech")
    args = ap.parse_args()

    rows = [l.strip() for l in Path(args.script).read_text().splitlines()]
    skip = re.compile(args.skip_pattern)
    lines = [l for l in rows if l and not skip.match(l)]

    segments, total = speech_segments(args.narration, args.noise, args.min_silence)
    result, mean_cost = align(lines, segments)

    Path(args.output).write_text(json.dumps(result, indent=1, ensure_ascii=False))
    report(result, segments, total)
    print(f"\nmean cost {mean_cost:.2f} per line "
          f"({'good' if mean_cost < 0.25 else 'loose - check the report above'})")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
