#!/usr/bin/env python3
"""Re-render only the lesson segment and reassemble the narrated cut.

The narrated slideshow segment is expensive to produce and unaffected by
changes to the lesson's branded overlay, so it is reused from build/.
"""

import sys

import build_module_00 as b

SEGMENTS = [b.BUILD / f"seg_{i}.mp4" for i in range(4)]


def main():
    missing = [s for s in SEGMENTS if not s.exists()]
    if missing:
        sys.exit("missing cached segments, run build_module_00.py instead: "
                 + ", ".join(s.name for s in missing))

    print("re-rendering lesson segment")
    b.run([
        "ffmpeg", "-i", str(b.LESSON), "-sn", "-vf", b.lesson_chain(),
        "-c:v", "libx264", "-preset", b.PRESET, "-crf", b.CRF,
        "-pix_fmt", "yuv420p", "-r", str(b.FPS),
        "-c:a", "aac", "-b:a", "128k", "-ar", b.AUDIO_RATE, "-ac", "2",
        "-video_track_timescale", "90000", str(b.BUILD / "seg_1.mp4"), "-y",
    ], "lesson")

    print("reassembling")
    final = b.OUT / "Module_00_Complete_Tutorial.mp4"
    expected = sum(b.duration(s) for s in SEGMENTS)
    b.concat(SEGMENTS, final)
    actual = b.duration(final)
    if abs(actual - expected) > 2.0:
        print(f"  drift {actual:.1f}s vs {expected:.1f}s; re-encoding")
        b.concat(SEGMENTS, final, copy=False)
        actual = b.duration(final)

    size_mb = final.stat().st_size / (1024 * 1024)
    with open(final, "rb") as handle:
        faststart = b"moov" in handle.read(4096)

    print(f"\n{final}")
    print(f"  Duration : {int(actual // 60)}m {actual % 60:04.1f}s")
    print(f"  Size     : {size_mb:.1f} MB")
    print(f"  faststart: {faststart}")
    if not faststart:
        sys.exit("moov atom is not at the start")


if __name__ == "__main__":
    main()
