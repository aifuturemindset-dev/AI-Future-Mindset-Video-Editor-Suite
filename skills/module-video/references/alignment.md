# Timing a script against its narration

Timing is the part of this job that cannot be guessed, and getting it wrong
is the failure that has cost this project the most. Two methods live here.
**Use forced alignment.** The other is a fallback, and this page exists
largely to record why.

## Use forced alignment

```bash
python scripts/align_forced.py NARRATION.mov script.txt -o aligned.json
```

It is not ASR. aeneas synthesises the script with espeak and warps that
against the real recording (DTW over MFCCs), so it never has to *recognise* a
word — only to line up two readings of the same sentence. That is a far easier
problem, and it is why this works in a sandbox where every ASR model host is
blocked (HuggingFace, `openaipublic`, `alphacephei`, `download.pytorch.org`,
`ggml.ggerganov.com` — all refused; PyPI and npm are reachable).

The script then snaps aeneas's assignment onto the measured speech
boundaries, because the two methods know different things:

- **Forced alignment knows which line is being spoken.** Its seams float,
  since nothing pins a warped synthetic voice to an audible edge.
- **Energy segmentation knows exactly where speech stops and starts.** It has
  no idea which line owns which gap.

Take the assignment from the first and the boundaries from the second.

### Setup

aeneas is from 2017 and needs three fixes on a modern box. The setup block at
the top of `align_forced.py` has the commands; the reasons:

- **setuptools must be pinned to 59.8.0.** Modern setuptools dropped the
  `install_layout` option aeneas's `setup.py` sets, and the build dies in a
  way that names neither.
- **scipy must be installed.** Without it aeneas reports `Audio format not
  supported by scipywavread`, which sounds like a problem with your audio and
  is not.
- **`numpy.fromstring` → `numpy.frombuffer`** in aeneas's bundled
  `wavfile.py`. `fromstring` was removed in numpy 2, and it surfaces as the
  same misleading audio-format error.

The venv is not committed (~100 MB of wheels). Point `AENEAS_PYTHON` at it or
create it where the setup block says.

### Align the file you are going to ship

Run the aligner on the exact audio that goes into the video, after any
loudness normalisation. Aligning the raw `.mov` and the normalised `.mp3`
of the same read produced a median difference of 0.20s and a maximum of 5.16s
— enough to matter. The cue times belong to one file, not to "the recording".

## Verify with something the method did not use

Both checks the script prints are independent of the warping:

**The opening lines.** Confirm the narrator really says the first line first.
The most common mistake is leaving a title or a heading in the script file —
the narrator never reads it, it swallows the opening seconds, every cue after
it shifts, and the quality score stays healthy.

**The longest pauses.** A narrator pauses longest where the argument turns, so
the recording's big pauses should sit just before a line start. This is an
energy measurement, not an MFCC one, so agreement means two different methods
concur. On "Finish One" the section starts landed at −0.02s, −0.16s, −0.05s,
−0.23s, +0.02s and +0.52s against the measured pauses.

## The fallback, and why it is a fallback

`align_script.py` matches the script's lines to the recording's breath groups
as a shortest path, using only silence detection. It needs nothing but ffmpeg.
It is the right tool only when aeneas cannot run.

**It failed in production and the checks did not catch it.** On a five-minute
video it drifted up to **ten seconds** through the middle while looking
correct at both ends. The screen read "Now picture your unfinished project"
while the narration was still on "I'll do it this weekend". The person
watching found it; nothing in the pipeline did.

The reason is structural, so no amount of tuning fixes it. Pause matching
knows only where the gaps are. One mis-grouped line early shifts everything
after it, and **nothing in the audio contradicts the wrong answer** — the
result stays self-consistent, the cost stays low, and the drift is invisible
from the inside. The verification that passed it was weaker than it looked:
checking that long pauses land near *some* section boundary is close to
circular when the optimiser was already fitting the same gaps.

Forced alignment does not have this failure mode, because it is constrained by
what the words sound like.

## Then drive the edit from the alignment

Do not retype timestamps into a config — that is how cues drift back out of
sync. Generate the config from `aligned.json`, declaring scenes by which
*lines* they cover:

```python
SCENES = [
    ("slide", 2, 26, 34),    # slide 2 covers lines 26-34
    ("text", None, 11, 25),
]
```

Put each cut in the middle of the pause between the last line of one scene and
the first of the next, rather than on the first word. The visual is then
already on screen when the sentence starts, which is how an editor places it.

## A note on matching assets to slides

Where a deck has been animated clip by clip, do not trust the order the files
arrived in. Correlate each clip's first frame against the reference slides
instead — downscale both to a small greyscale patch, mean-centre, normalise,
and take the dot product. On thirty clips across two videos every match came
back above 0.99 with the runner-up below 0.61, which both confirms the order
and catches a swap immediately. It costs seconds and removes a whole class of
silent error.
