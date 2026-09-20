#!/usr/bin/env python3
"""Shared rendering primitives for module tutorial videos.

Encoding parameters live here in one place because concat only works when
every segment matches exactly. See references/troubleshooting.md.
"""

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
FPS = 30
CRF = "20"
PRESET = "fast"
AUDIO_RATE = "48000"
AUDIO_BITRATE = "128k"
TIMESCALE = "90000"

BRAND = {
    "primary": "#4DD9E8",
    "secondary": "#F3EEFF",
    "background": "#0E0B1F",
    "panel": "#141123",
    "postit": "#FFE86B",
    "postit_ink": "#2A2416",
    "wordmark": "AI FUTURE MINDSET",
    "title": "AI CONTENT ENGINE",
}

# Comic Neue reads as handwriting without looking like a novelty font.
# Install with: apt-get install -y fonts-comic-neue
FONT_BOLD = "/usr/share/fonts/opentype/comic-neue/ComicNeue-Bold.otf"
FONT_REGULAR = "/usr/share/fonts/opentype/comic-neue/ComicNeue-Regular.otf"
FONT_FALLBACK_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_FALLBACK_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def fonts():
    """Comic Neue when installed, DejaVu otherwise, so a build never dies on fonts."""
    if Path(FONT_BOLD).exists():
        return FONT_BOLD, FONT_REGULAR
    return FONT_FALLBACK_BOLD, FONT_FALLBACK_REGULAR


BOLD, REGULAR = fonts()


def font(path, size):
    return ImageFont.truetype(path, size)


def run(cmd, label):
    result = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"[{label}] ffmpeg failed:\n{' '.join(str(c) for c in cmd)}\n\n"
                 f"{result.stderr[-2500:]}")
    return result


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True,
    )
    if not out.stdout.strip():
        sys.exit(f"could not read duration of {path}; is it a valid media file?")
    return float(out.stdout.strip())


def has_subtitles(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "s",
         "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return bool(out.stdout.strip())


def video_encode_args():
    return [
        "-c:v", "libx264", "-preset", PRESET, "-crf", CRF,
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", AUDIO_RATE, "-ac", "2",
        "-video_track_timescale", TIMESCALE,
    ]


def tracked_text(draw, xy, text, f, fill, spacing=8):
    """Letter-spaced text; drawtext has no letter-spacing option."""
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=f, fill=fill)
        x += draw.textlength(char, font=f) + spacing


def sticky_note(text, size=32, angle=-3.0):
    """Caption as a tilted post-it: shadow, folded corner, handwriting face."""
    f = font(BOLD, size)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    pad_x, pad_y = 44, 26
    nw = int(probe.textlength(text, font=f) + pad_x * 2)
    nh = int(size + pad_y * 2)
    margin = 28

    canvas = Image.new("RGBA", (nw + margin * 2, nh + margin * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([margin + 8, margin + 10, margin + nw + 8, margin + nh + 10],
                   fill=(0, 0, 0, 120))
    draw.rectangle([margin, margin, margin + nw, margin + nh], fill=BRAND["postit"])
    fold = 24
    draw.polygon([(margin + nw - fold, margin + nh),
                  (margin + nw, margin + nh - fold),
                  (margin + nw, margin + nh)], fill="#E3CC55")
    draw.text((margin + pad_x, margin + pad_y - 6), text,
              font=f, fill=BRAND["postit_ink"])
    return canvas.rotate(angle, resample=Image.BICUBIC, expand=True)


def brand_chrome(draw, marker=None):
    """Top bar, wordmark, title and base rule, shared by every still."""
    draw.rectangle([0, 0, W, 76], fill=BRAND["panel"])
    tracked_text(draw, (36, 26), BRAND["wordmark"], font(BOLD, 18), BRAND["primary"])

    f_title = font(BOLD, 50)
    tx = (W - draw.textlength(BRAND["title"], font=f_title)) / 2
    draw.text((tx, 90), BRAND["title"], font=f_title, fill="#FFFFFF",
              stroke_width=3, stroke_fill=BRAND["primary"])

    if marker:
        f_mark = font(BOLD, 26)
        draw.text((W - 60 - draw.textlength(marker, font=f_mark), 26),
                  marker, font=f_mark, fill=BRAND["primary"])
    draw.rectangle([0, H - 5, W, H], fill=BRAND["primary"])


def title_card(path, headline, subhead):
    img = Image.new("RGB", (W, H), BRAND["background"])
    draw = ImageDraw.Draw(img)
    brand_chrome(draw)

    f_head = font(BOLD, 88)
    draw.text(((W - draw.textlength(headline, font=f_head)) / 2, 420),
              headline, font=f_head, fill=BRAND["primary"])
    f_sub = font(REGULAR, 44)
    draw.text(((W - draw.textlength(subhead, font=f_sub)) / 2, 545),
              subhead, font=f_sub, fill=BRAND["secondary"])
    img.save(path)


def screenshot_card(path, shot, position, total, caption,
                    max_w=620, max_h=430):
    """A framed screenshot with shadow, cyan edge, step badge and post-it."""
    shot_img = Image.open(shot).convert("RGB")
    scale = min(max_w / shot_img.width, max_h / shot_img.height)
    sw, sh = int(shot_img.width * scale), int(shot_img.height * scale)
    resized = shot_img.resize((sw, sh), Image.LANCZOS)

    note = sticky_note(caption, size=28, angle=-3.5)
    border, pad, header = 4, 20, 44
    card_w = sw + (border + pad) * 2
    card_h = sh + (border + pad) * 2 + header
    lift = note.height // 2
    margin = 36

    canvas = Image.new("RGBA", (card_w + margin * 2, card_h + margin * 2 + lift),
                       (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    x0, y0 = margin, margin + lift
    x1, y1 = x0 + card_w, y0 + card_h

    draw.rounded_rectangle([x0 + 12, y0 + 14, x1 + 12, y1 + 14], radius=16,
                           fill=(0, 0, 0, 135))
    draw.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=(18, 15, 32, 242))
    draw.rounded_rectangle([x0, y0, x1, y1], radius=16,
                           outline=BRAND["primary"], width=3)
    draw.text((x0 + pad + border, y0 + 12), f"STEP {position} OF {total}",
              font=font(BOLD, 22), fill=BRAND["primary"])

    ix, iy = x0 + pad + border, y0 + header + pad + border
    draw.rectangle([ix - border, iy - border, ix + sw + border, iy + sh + border],
                   fill=BRAND["primary"])
    canvas.paste(resized, (ix, iy))
    canvas.alpha_composite(note, (max(0, x0 - 26), 0))
    canvas.save(path)
    return canvas.size


def still_segment(png, dest, frames, build_dir, zoom=False):
    """A still as video. anullsrc supplies the silent audio concat requires."""
    vf = (f"zoompan=z='min(1+0.00004*on,1.05)':d={frames}:"
          f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}"
          if zoom else f"scale={W}:{H},fps={FPS}")
    run([
        "ffmpeg", "-loop", "1", "-framerate", FPS, "-i", png,
        "-f", "lavfi", "-i",
        f"anullsrc=channel_layout=stereo:sample_rate={AUDIO_RATE}",
        "-frames:v", frames, "-vf", vf,
        *video_encode_args(), "-shortest", dest, "-y",
    ], f"still {Path(png).name}")


def concat(files, dest, build_dir, copy=True):
    """Concat via the demuxer. Absolute paths: relative entries resolve
    against the listing's own directory, not the segments'."""
    listing = Path(build_dir) / f"{Path(dest).stem}_concat.txt"
    listing.write_text("".join(f"file '{Path(f).resolve()}'\n" for f in files))
    codec = ["-c", "copy"] if copy else video_encode_args()
    run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", listing,
         *codec, "-movflags", "+faststart", dest, "-y"], f"concat {Path(dest).name}")


def assemble(segments, dest, build_dir):
    """Concat with a duration check, falling back to a re-encode on drift."""
    expected = sum(duration(s) for s in segments)
    concat(segments, dest, build_dir)
    actual = duration(dest)
    if abs(actual - expected) > 2.0:
        print(f"  stream-copy drifted ({actual:.1f}s vs {expected:.1f}s); re-encoding")
        concat(segments, dest, build_dir, copy=False)
        actual = duration(dest)
    return actual


def verify(path):
    """Report what a reviewer would otherwise have to discover in a player."""
    seconds = duration(path)
    size_mb = Path(path).stat().st_size / (1024 * 1024)
    with open(path, "rb") as handle:
        faststart = b"moov" in handle.read(4096)

    print(f"\n{path}")
    print(f"  Duration : {int(seconds // 60)}m {seconds % 60:04.1f}s")
    print(f"  Size     : {size_mb:.1f} MB")
    print(f"  faststart: {faststart}")
    if not faststart:
        sys.exit("moov atom is not at the start: the file will not stream and "
                 "many players will refuse it entirely")
    return seconds, size_mb


def load_config(path):
    config = json.loads(Path(path).read_text())
    for key in ("module", "output_dir"):
        if key not in config:
            sys.exit(f"config is missing required key: {key}")
    return config
