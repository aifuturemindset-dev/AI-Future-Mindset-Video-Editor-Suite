#!/usr/bin/env python3
"""Emit the Finish One timeline as TypeScript, from the measured alignment.

Scenes are declared by which script lines they cover, never by timestamp.
Every time in the output is read out of aligned.json, so the cut cannot drift
away from the narration through a typo - the one failure mode that has cost
this project the most.

Cuts land in the middle of the pause between two lines rather than on the
first word, which is how an editor would place them: the visual is already
there when the sentence starts.
"""
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
AL = json.loads((REPO / "assets/scripts/finish-one-aligned.json").read_text())
TOTAL = 302.23

# (kind, asset-or-None, first line, last line, beat grouping for text scenes)
# Beats are lists of line indices shown together; each beat replaces the last.
SCENES = [
    # Cold open on type alone - the folder is named before it is shown, so the
    # reveal on "an automation you started on a weekend" actually lands.
    ("text", None, 0, 3, [[0], [1, 2], [3]]),
    ("slide", "02-that-folder", 4, 7, None),
    ("slide", "01-finish-one", 8, 9, None),
    ("text", None, 10, 11, [[10], [11]]),
    ("slide", "03-starting-over", 12, 17, None),
    # The staccato list is the pattern interrupt; single lines hit hardest.
    ("text", None, 18, 27, [[18], [19], [20], [21], [22, 23], [24, 25], [26, 27]]),
    ("text", None, 28, 36, [[28, 29], [30, 31], [32], [33, 34], [35, 36]]),
    ("slide", "04-unfinished", 37, 39, None),
    ("slide", "05-everyone-elses-future", 40, 44, None),
    ("slide", "06-the-question", 45, 50, None),
    ("slide", "07-proof-timeline", 51, 55, None),
    ("text", None, 56, 59, [[56], [57, 58], [59]]),
    ("slide", "07-proof-timeline", 60, 66, None),
    ("slide", "08-breakthrough-funnel", 67, 69, None),
    ("text", None, 70, 73, [[70, 71], [72], [73]]),
    ("slide", "09-learner-finisher", 74, 77, None),
    ("slide", "10-hundred-day-lock-in", 78, 84, None),
    # The affiliate disclosure gets the screen to itself, in plain type.
    ("text", None, 85, 86, [[85], [86]]),
    ("slide", "11-day-thirty", 87, 95, None),
    ("text", None, 96, 101, [[96], [97], [98], [99], [100], [101]]),
    ("slide", "12-public-promise", 102, 111, None),
    ("end", None, 112, 112, None),
]

# Emphasis: lines carrying the argument, set in the display face.
# The affiliate disclosure (86) is deliberately not here - a disclosure wants
# to be plainly readable, not styled.
EMPHASIS = {9, 11, 27, 32, 36, 38, 49, 59, 71, 73, 98, 101}


def boundary(prev_last, next_first):
    """Put the cut in the pause, not on the word."""
    a, b = AL[prev_last]["end"], AL[next_first]["start"]
    return round((a + b) / 2, 2) if b > a else round(b, 2)


starts = [0.0]
for i in range(1, len(SCENES)):
    starts.append(boundary(SCENES[i - 1][3], SCENES[i][2]))
ends = starts[1:] + [TOTAL]

out = []
for (kind, asset, lo, hi, beats), s, e in zip(SCENES, starts, ends):
    if kind == "slide":
        out.append({
            "kind": "slide",
            "image": f"finish-one/slides/{asset}.png",
            "from": round(s, 2),
            "to": round(e, 2),
            "say": AL[lo]["text"],
        })
    elif kind == "end":
        # One sentence, three movements. Split evenly across its own span.
        span = AL[112]["end"] - AL[112]["start"]
        t0 = AL[112]["start"]
        out.append({
            "kind": "end",
            "from": round(s, 2),
            "to": round(e, 2),
            "beats": [
                {"at": round(t0, 2), "lines": ["Protect your peace."], "em": True},
                {"at": round(t0 + span * 0.34, 2), "lines": ["Vibrate your power."], "em": True},
                {"at": round(t0 + span * 0.63, 2),
                 "lines": ["And build what the future", "needs from you."], "em": True},
            ],
        })
    else:
        out.append({
            "kind": "text",
            "from": round(s, 2),
            "to": round(e, 2),
            "beats": [
                {
                    "at": round(AL[g[0]]["start"], 2),
                    "lines": [AL[i]["text"] for i in g],
                    "em": any(i in EMPHASIS for i in g),
                }
                for g in beats
            ],
        })

header = '''import type { FinishOneConfig } from "../FinishOne";

/**
 * "I Stopped Waiting to Feel Ready" - the 100-Day AI Finish Line.
 *
 * GENERATED from the measured alignment of Script 01 against the narration
 * recording; see skills/module-video/references/alignment.md. Every `from`
 * and `at` is a real timestamp taken off the audio, not an estimate, so edit
 * the generator rather than these numbers if a cue needs to move.
 *
 * The twelve storyboard stills carry the beats they were designed for; the
 * narration between them runs as animated type.
 */
export const finishOne: FinishOneConfig = {
  id: "finish-one",
  audio: "finish-one/narration.mp3",
  durationInSeconds: %s,
  scenes: %s,
};
''' % (TOTAL, json.dumps(out, indent=4, ensure_ascii=False).replace("\n", "\n  "))

target = REPO / "remotion/src/modules/finish-one.ts"
target.write_text(header)

slides = sum(1 for s in out if s["kind"] == "slide")
print(f"{len(out)} scenes: {slides} stills, {len(out)-slides} animated-text")
for s in out:
    tag = s.get("image", "").split("/")[-1] or s["kind"]
    print(f"  {s['from']:7.2f} - {s['to']:7.2f}  {s['kind']:6} {tag}")
