---
name: module-video
description: Build branded tutorial videos for course modules by combining a lesson recording, a voiceover track, and UI screenshots into a finished MP4 with consistent branding. Two pipelines - an overlay cut that floats screenshot cards over a lesson video timed to its narration, and a script cut that renders slides from a written voiceover script. Use this skill whenever the user wants to assemble, edit, merge, or re-cut course or tutorial videos, add screenshots or step callouts onto a video, sync screenshots to a voiceover, build slides from a script, or produce module videos for a course - including when they just say "merge these assets", "make a video from these screenshots", "the screenshots are out of sync", or name a module by number.
---

# Module tutorial videos

Turn a lesson recording, a voiceover, and a folder of UI screenshots into a
finished, branded MP4.

## Pick the pipeline first

The three pipelines are not variations on a theme. They answer different
questions, and choosing wrong costs a full re-render.

**Deck cut** (`scripts/build_deck_cut.py`) — there is a designed slide deck
plus a voiceover recording. The deck is the visual; screenshots overlay the
slides that teach them. This is the usual shape for a course module.

**Overlay cut** (`scripts/build_overlay.py`) — there is already a finished
lesson video with its own narration and visuals. Screenshot cards float over it
while it plays. The lesson keeps its own audio; nothing else is mixed in.

**Script cut** (`scripts/build_script_cut.py`) — there is a written script with
slides and bullets plus a voiceover recording, but no deck and no lesson video.
Slides are rendered from the script and the recording narrates them.

If several sources exist, they are usually different takes of the same
material rather than parts of one video. Check before assuming they pair:
compare a lesson's transcript, or a script's opening line, against the others.
Two recordings of the same lesson diverge in wording and pacing, and forcing
them together puts every visual on the wrong sentence. Build them as separate
cuts and let the user choose.

A written script's own chapter marks describe the take it was written for,
not necessarily the recording in hand. Divide the script's word count by the
recording's length: 110-150 wpm means they match, 40 wpm means they do not.

## Identify the source files before planning

Inputs are routinely mislabeled, and a wrong assumption here wastes the whole
build. Check each one:

```bash
ffprobe -v error -show_entries format=duration \
  -show_entries stream=codec_type,codec_name,width,height,bit_rate \
  -of csv=p=0 INPUT.mp4
```

What the numbers tell you:

- **Video bitrate near 20 kbps against normal audio** — this is an audio
  recording with a black video track, not a screen capture. It is narration.
  Sampling frames will return black and tell you nothing; read the bitrate.
- **A `mov_text` subtitle stream** — the lesson carries its own transcript.
  This is the single most useful thing you can find, because it is the only
  reliable way to know what is said at each second.
- **Duration against a script's word count** — a script divided by a
  recording's length gives words per minute. Normal narration is 110-150 wpm.
  If a pairing implies 40 wpm, that script does not belong to that recording.

## Timing is the whole job, and it cannot be inferred

Visuals spaced evenly across a recording land on the wrong sentence almost
everywhere. Viewers notice at once and it reads as carelessness. Neither is
word count a substitute: on Module 01 it gave one slide fourteen seconds where
the narration spends five, and another twenty-three where it spends
thirty-seven. How much text a slide carries says nothing about how long a
speaker dwells on it.

Timing has to come from the audio. In order of preference:

**A subtitle track**, if the source has one — the only fully automatic route:

```bash
python scripts/extract_cues.py LESSON.mp4
```

This prints the transcript with timestamps. Set one anchor per instruction the
narration gives and list that step's screenshots under it.

**Marks from whoever recorded it.** Ask for the second each step begins. Eight
marks time a fourteen-slide deck, because slides between two anchors divide
the gap. This takes them a couple of minutes and removes all the guesswork —
ask early rather than shipping a guess and iterating.

**What does not work**, so the time is not spent rediscovering it:

- *Silence detection.* A narrator reading continuously leaves no gap at slide
  boundaries. On Module 01 the whole first two minutes is one unbroken speech
  block at `-30dB`, so there is nothing to detect.
- *ASR.* Model hosts are blocked in many sandboxes even where PyPI is
  reachable. Test before promising it.
- *A script's stated chapter marks.* They describe the take it was written
  for. Verify against the recording's length first.

Say plainly when timing is a guess. A video that looks finished but drifts
costs more trust than one that is honestly labelled.

## Finding screenshots that "aren't there"

Screenshots pasted inline into a conversation may never reach the uploads
directory, while file attachments do. Before reporting an image as
unavailable, check the session transcript — embedded images are stored there
as base64 and can be recovered:

```python
import base64, hashlib, json, pathlib
found = []
def walk(node):
    if isinstance(node, dict):
        if node.get("type") == "image":
            src = node.get("source", {})
            if src.get("type") == "base64" and src.get("data"):
                found.append((src.get("media_type", "image/png"), src["data"]))
        for v in node.values(): walk(v)
    elif isinstance(node, list):
        for v in node: walk(v)

for line in pathlib.Path(TRANSCRIPT_JSONL).open():
    try: walk(json.loads(line))
    except Exception: pass

seen = set()
for media, data in found:
    raw = base64.b64decode(data)
    h = hashlib.md5(raw).hexdigest()
    if h in seen: continue
    seen.add(h)
    ext = "jpg" if "jpeg" in media else "png"
    pathlib.Path(f"out/{h[:8]}.{ext}").write_bytes(raw)
```

Dedupe by hash, then separate the user's screenshots from your own preview
renders — source screenshots share a capture size, preview grids do not.
Copy what you recover into the project with ordered, descriptive names so the
build stops depending on session-scoped temp files.

## Workflow

1. **Inventory** every input with `ffprobe`. Name what each file actually is.
2. **Choose** the pipeline from what exists, not from what was asked for.
3. **Extract** the transcript, or count the script's words per slide.
4. **Map** each screenshot to the step it belongs to. Order matters more than
   dwell time — 3 seconds on the right sentence beats 12 on the wrong one.
5. **Write** the config (see `references/config-format.md`).
6. **Render**, then **verify** before handing anything over.

## Verify before delivering

A corrupt or misaligned video that reaches the user costs far more than the
minute spent checking. Every build prints duration, size and faststart state;
confirm the content too.

Sample frames at the moments that should differ and read them:

```bash
for t in 14 38 62 103; do
  ffmpeg -v error -ss $t -i OUT.mp4 -frames:v 1 -vf scale=470:-1 \
    -update 1 /tmp/f_$t.png -y
done
```

When the lesson has burned-in captions, this doubles as an alignment proof:
the caption on screen and the screenshot caption should be describing the same
action. That is the check worth reporting.

Confirm audio is actually present — silence reads as -91 dB:

```bash
ffmpeg -ss 60 -t 3 -i OUT.mp4 -af volumedetect -f null - 2>&1 | grep mean_volume
```

`volumedetect` logs at info level, so do not pass `-v error` here.

## Delivery

File size decides the route. Chat attachments typically cap around 30 MB and
GitHub warns above 50 MB. A static-slide cut compresses to a few MB; a
full-motion cut of the same length can be ten times that.

If a download fails or a player shows only its logo, check whether the file
actually arrived before re-rendering. A player that reports it "cannot open the
MRL" is describing a missing file, not a broken one.

## Brand

Colours, wordmark and fonts live in `BRAND` in `scripts/common.py`. Take them
from the project's own stylesheet rather than inventing them — a course kit,
site or deck usually defines CSS custom properties that are the real source of
truth. Guessing a palette produces work that looks finished and is wrong
throughout, which is expensive to discover late.

Fonts are bundled in `assets/fonts/`. Where Google Fonts is blocked, the npm
registry is often still reachable: `npm pack @fontsource/<family>` gives woff2,
and `fonttools` converts it to the TTF that PIL and ffmpeg need.

## Marking where to click

Three treatments, and they solve different problems:

**A screenshot that already has callouts baked in** — most capture tools draw
the box and arrow for you. Frame it and caption it; `screenshot_card()` gives
it a brand border, a shadow and a post-it naming the action. Do not draw a
second arrow over one that is already there.

**Raw screen footage** — nothing marks the control, and a cursor moving is not
enough: a viewer following along will miss the click. The target needs a box
around it, an arrow, and a label naming the action. ffmpeg can manage a static
`drawbox`, but an arrow that draws itself and a box that holds the eye through
a long step want a real renderer — that lives in the Remotion project's
`Callout` component.

**Naming the skill in use** — a post-it pinned to a corner, kept up for the
whole step rather than flashed, so a viewer joining mid-step still knows what
produced what they are seeing. `SkillNote` in the Remotion project.

Get box coordinates by exporting the frame being annotated and reading pixel
positions off it; at 1920x1080 they map one to one:

```bash
ffmpeg -ss 4 -i clip.mp4 -frames:v 1 /tmp/frame.png
```

## When to reach for Remotion instead

This pipeline renders without a browser and is right for a batch re-render.
What it cannot do is show the result while someone adjusts it, which is
exactly what timing needs. The companion Remotion project puts slides and
voiceover on one timeline, so a cue that lands late is a number edited with
the preview reloading live. It also does real motion — springs, cross-fades,
progress — which ffmpeg does clumsily.

Use this pipeline to render; use Remotion to decide the timing, then bring
the numbers back here. Both read the same anchor model.

## References

- `references/config-format.md` — config schema for all three pipelines, with
  worked examples
- `references/troubleshooting.md` — the failures that produce unplayable files
  or wrong-looking output, and why each happens. Read this before debugging
  ffmpeg, LibreOffice or font output; most of it is not guessable.
