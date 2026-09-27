# Aligning a script to its narration

Timing is the part of this job that cannot be guessed, and this is the route
that works when there is no subtitle track, nobody supplied marks, and the
ASR hosts are blocked.

It needs nothing but ffmpeg and the script. It is not ASR: it never tries to
work out *what* was said. It uses the fact that a scripted read **pauses
between lines**, matches the pauses against the script you already have, and
recovers a start time for every line.

`scripts/align_script.py` implements it.

```bash
python scripts/align_script.py NARRATION.mov script.txt -o aligned.json
```

## When it works, and when it does not

It works on a delivered, scripted read — short clauses, a beat between them.
It does not work on a continuous read, and no tuning will change that.

Check before trusting it. The script prints the segment count against the
line count:

- **Segments ≈ lines (within about 30%)** — separable. Module 01's "Finish
  One" narration gave 140 segments for 113 lines.
- **Segments far below lines** — the reader does not pause at line
  boundaries. The script exits rather than returning a plausible-looking
  answer. Go and ask for marks.

Module 01's *other* recording is the counter-example: silence detection at
−30 dB found one unbroken 119-second block. Same project, same voice, an
unusable result — so run the check every time rather than assuming.

## How it works

1. **Segment.** `silencedetect` splits the audio into speech spans, roughly
   one per breath group. The audio is normalised to 16 kHz mono first,
   because `silencedetect` measures RMS and the same recording read from a
   `.mov` and from an extracted `.wav` otherwise yields different boundaries
   — cue times that depend on which file you pointed at are not reproducible.

2. **Align.** The counts never match one to one. Long lines are split across
   two or three breaths; short lines get run together in one. So a *run* of
   lines maps to a *run* of segments, in order, and the best such mapping is
   a shortest path. It is solved as one.

   Cost is the relative error between a group's measured duration and the
   duration its characters predict, so a two-word line is judged as strictly
   as a long one, plus a small penalty for grouping — groups form only where
   the timing demands them.

   A greedy left-to-right scan is the tempting shortcut and it is wrong: one
   bad pairing early shifts everything after it and it never recovers.

3. **Subdivide.** Within a group, lines split the span by character count.
   A group is at most three lines, so this only has to be roughly right.

## Verify before building on it

The script prints two checks. Read both — the cost figure alone will not
catch a wrong answer.

**The opening lines.** Confirm the narrator actually says the first line
first. The most common mistake is leaving a title or a section heading in
the script file: the narrator never reads it, it swallows the opening
seconds, every cue after it shifts, and the cost figure stays low enough to
look healthy. This happened on the first run of "Finish One".

**The longest pauses.** These should land on the script's structural breaks.
On "Finish One" they did, exactly:

| pause | line that follows | section |
|---|---|---|
| 2.03 s | "So finish this sentence with me:" | YOU — Your Turn |
| 1.55 s | "Now go back to your project." | YOU — Day 30 |
| 1.42 s | "The link is below." | the offer |
| 1.27 s | "I wasn't a developer." | I — What Changed |

A narrator pauses longest where the argument turns. If the long pauses land
on section starts, the alignment is not drifting. If one lands mid-sentence,
it is.

Mean cost under about 0.25 per line is good; above that, read the report
carefully before using the numbers.

## Then drive the edit from it

Do not retype the timestamps into a config — that is how cues drift back out
of sync. Generate the config from `aligned.json`, declaring scenes by which
*lines* they cover, and let the generator look the times up:

```python
SCENES = [
    ("slide", "02-that-folder", 4, 7),     # lines 4-7
    ("slide", "01-finish-one",  8, 9),
    ("text",  None,            10, 11),
]
```

Put each cut in the middle of the pause between the last line of one scene
and the first of the next, rather than on the first word. The visual is then
already on screen when the sentence starts, which is how an editor places it.
