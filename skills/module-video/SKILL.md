---
name: module-video
description: Build branded tutorial videos for course modules by combining a lesson recording, a voiceover track, and UI screenshots into a finished MP4 with consistent branding. Two pipelines - an overlay cut that floats screenshot cards over a lesson video timed to its narration, and a script cut that renders slides from a written voiceover script. Use this skill whenever the user wants to assemble, edit, merge, or re-cut course or tutorial videos, add screenshots or step callouts onto a video, sync screenshots to a voiceover, build slides from a script, or produce module videos for a course - including when they just say "merge these assets", "make a video from these screenshots", "the screenshots are out of sync", or name a module by number.
---

# Module tutorial videos

Turn a lesson recording, a voiceover, and a folder of UI screenshots into a
finished, branded MP4.

## Pick the pipeline first

The two pipelines are not variations on a theme. They answer different
questions, and choosing wrong costs a full re-render.

**Overlay cut** (`scripts/build_overlay.py`) — there is already a finished
lesson video with its own narration and visuals. Screenshot cards float over it
while it plays. The lesson keeps its own audio; nothing else is mixed in.

**Script cut** (`scripts/build_script_cut.py`) — there is a written script with
slides and bullets plus a voiceover recording, but no finished lesson video.
Slides are rendered from the script and the recording narrates them.

If both a lesson video and a separate script exist, they are usually different
takes of the same material. Check before assuming they pair: compare the
lesson's transcript against the script's opening line. Two recordings of the
same lesson will diverge in wording and pacing, and forcing them together puts
every visual on the wrong sentence. Build them as separate cuts and let the
user choose.

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

## Timing is the whole job

Screenshots spaced evenly across a video will land on the wrong sentence almost
everywhere. Viewers notice immediately, and it reads as carelessness. Derive
timing from the audio instead.

**When the lesson has a subtitle track**, extract it and read it:

```bash
python scripts/extract_cues.py LESSON.mp4
```

This prints the transcript with timestamps. Set one phase anchor per
instruction the narration gives, then list that step's screenshots under it.
`build_overlay.py` divides each phase evenly among its screenshots, so the
group stays inside the sentence that describes it.

**When there is no subtitle track**, you need the written script. Allocate each
slide's time by word count, which `build_script_cut.py` does automatically.
Word-proportional allocation beats the script's own estimated chapter marks:
speech rate is near constant within a recording, while the estimates drift as
soon as the actual read runs longer or shorter than planned.

Transcribing audio yourself needs an ASR model, and model hosts are blocked in
many sandboxed environments. Test reachability before promising it, and fall
back to asking for the script.

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

## References

- `references/config-format.md` — config schema for both pipelines, with a
  worked example
- `references/troubleshooting.md` — the failures that produce unplayable
  files, and why each one happens. Read this before debugging ffmpeg output.
