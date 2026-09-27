#!/usr/bin/env python3
"""Build the Finish One sound-effect bed from the storyboard's audio cues.

The storyboard names one effect per slide. Every sample library is blocked in
this environment - freesound, pixabay and archive.org all refuse - so the
effects are synthesised instead (see skills/module-video/scripts/soundbed.py).
That also makes them royalty-free and tunable to the cut.

Cue times come from the generated scene config, which comes from the measured
alignment, so an effect lands on the frame its slide does.

Usage:
    python build-fx-bed.py            # writes the bed and the mixed audio
"""
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "skills/module-video/scripts"))
from soundbed import render_bed  # noqa: E402

CONFIG = REPO / "remotion/src/modules/finish-one.ts"
NARRATION = REPO / "remotion/public/finish-one/narration.mp3"
BED = REPO / "remotion/public/finish-one/fx-bed.wav"
MIXED = REPO / "remotion/public/finish-one/narration-with-fx.mp3"

# Storyboard "Audio & NLP Sound Design" column, slide by slide.
# gain_db is per cue: a drone sitting under speech and a chime landing in a
# gap want very different levels, and one global number gets both wrong.
CUES = {
    "01-finish-one":            ("digital_pulse",      -24),
    "02-that-folder":           ("paper_shuffle",      -25),
    "03-starting-over":         ("ticking_clock",      -23),
    "04-unfinished":            ("synth_pad",          -27),
    "05-everyone-elses-future": ("metallic_click",     -24),
    "06-the-question":          ("whoosh",             -20),
    "07-proof-timeline":        ("mechanical_notches", -23),
    "08-breakthrough-funnel":   ("airflow_rings",      -23),
    "09-learner-finisher":      ("static_to_tone",     -26),
    "10-hundred-day-lock-in":   ("bass_riser",         -22),
    "11-day-thirty":            ("success_chime",      -21),
    "12-public-promise":        ("resonant_swell",     -25),
}


def load_scenes():
    """Read the generated config.

    Only the scenes array is JSON; the object around it is TypeScript with
    unquoted keys, so pull the two fields out rather than parsing the whole
    thing.
    """
    raw = CONFIG.read_text()
    scenes = re.search(r"scenes:\s*(\[.*\])", raw, re.S)
    duration = re.search(r"durationInSeconds:\s*([0-9.]+)", raw)
    if not scenes or not duration:
        sys.exit(f"could not read scenes or duration out of {CONFIG}")
    return {"scenes": json.loads(scenes.group(1).rstrip().rstrip(",")),
            "durationInSeconds": float(duration.group(1))}


def main():
    cfg = load_scenes()
    cues, seen = [], set()
    for scene in cfg["scenes"]:
        if scene["kind"] != "slide":
            continue
        name = pathlib.Path(scene["image"]).stem
        if name in seen:                      # slide 07 is used twice
            continue
        seen.add(name)
        fx, gain = CUES[name]
        # Land the effect a touch before the cut, the way an editor would,
        # so its transient sells the transition rather than trailing it.
        cues.append({"at": max(0.0, scene["from"] - 0.18), "fx": fx,
                     "gain_db": gain, "slide": name})

    cues.sort(key=lambda c: c["at"])
    render_bed(cues, cfg["durationInSeconds"], BED)

    # Mix under the narration. The narration is already at -14 LUFS and must
    # stay there, so the bed is added rather than the pair being normalised.
    subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(NARRATION), "-i", str(BED),
         "-filter_complex",
         "[1:a]highpass=f=35[fx];[0:a][fx]amix=inputs=2:duration=first:"
         "dropout_transition=0:normalize=0[out]",
         "-map", "[out]", "-c:a", "libmp3lame", "-q:a", "2", str(MIXED), "-y"],
        check=True)

    print(f"{len(cues)} cues -> {BED.name} and {MIXED.name}")
    for c in cues:
        print(f"  {c['at']:7.2f}  {c['fx']:<19} {c['gain_db']:>4} dB   {c['slide']}")


if __name__ == "__main__":
    main()
