#!/usr/bin/env python3
"""Generate reusable branded overlays for an editor like CapCut or Premiere.

These are RGBA PNGs with a transparent middle, so they sit on a track above
footage and the footage shows through. Anything meant to go over video has to
carry alpha - a JPEG or a flattened PNG would black out the frame.

Both orientations are produced: 1920x1080 for YouTube and 1080x1920 for
Shorts, Reels and TikTok. Positions are derived from the canvas rather than
hard-coded, so the vertical set is not a stretched copy of the horizontal one.

Usage:
    python make_overlays.py [OUTPUT_DIR]
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

import common as c

SIZES = {"landscape": (1920, 1080), "portrait": (1080, 1920)}

PINK = c.BRAND["primary"]
PINK_SOFT = c.BRAND["primary_soft"]
TEXT = c.BRAND["secondary"]


def rgba(hex_color, alpha=255):
    hex_color = hex_color.lstrip("#")
    return (*tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4)), alpha)


def scaled(w, h):
    """One factor for every dimension, from the short edge, so weights and
    type stay proportional instead of thinning out on the taller canvas."""
    return min(w, h) / 1080


def wordmark(draw, xy, k, size=22, spacing=9):
    c.tracked_text(draw, xy, c.BRAND["wordmark"],
                   c.font(c.BOLD, int(size * k)), rgba(PINK), spacing * k)


def gradient_bar(img, y, height, w):
    bar = Image.new("RGBA", (w, height))
    pen = ImageDraw.Draw(bar)
    lr, lg, lb = rgba(PINK)[:3]
    rr, rg, rb = rgba(PINK_SOFT)[:3]
    for x in range(w):
        t = x / max(1, w - 1)
        pen.line([(x, 0), (x, height)],
                 fill=(int(lr + (rr - lr) * t), int(lg + (rg - lg) * t),
                       int(lb + (rb - lb) * t), 255))
    img.alpha_composite(bar, (0, y))


def frame_brackets(w, h):
    """Corner brackets and wordmark. Leaves the frame almost entirely clear,
    so it can sit over a whole video without competing with the content."""
    k = scaled(w, h)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    inset, arm, weight = int(44 * k), int(132 * k), max(3, int(7 * k))
    pink = rgba(PINK)

    for cx, cy, dx, dy in ((inset, inset, 1, 1), (w - inset, inset, -1, 1),
                           (inset, h - inset, 1, -1), (w - inset, h - inset, -1, -1)):
        draw.line([(cx, cy), (cx + arm * dx, cy)], fill=pink, width=weight)
        draw.line([(cx, cy), (cx, cy + arm * dy)], fill=pink, width=weight)

    wordmark(draw, (inset + int(34 * k), inset + int(22 * k)), k)
    gradient_bar(img, h - max(3, int(7 * k)), max(3, int(7 * k)), w)
    return img


def frame_border(w, h):
    """A continuous thin border. Heavier than the brackets; suits talking-head
    footage where a hard edge reads as intentional."""
    k = scaled(w, h)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    inset, weight = int(38 * k), max(3, int(6 * k))
    draw.rectangle([inset, inset, w - inset, h - inset],
                   outline=rgba(PINK), width=weight)

    plate = (int(470 * k), int(66 * k))
    draw.rectangle([inset, inset, inset + plate[0], inset + plate[1]],
                   fill=rgba(c.BRAND["background"], 235))
    wordmark(draw, (inset + int(26 * k), inset + int(22 * k)), k)
    gradient_bar(img, h - weight, weight, w)
    return img


def lower_third(w, h):
    """An empty title plate. Deliberately wordless so the editor types over
    it; baked-in text would mean regenerating this for every video.

    Sits higher on the portrait canvas, clear of the caption band and the
    interface controls that sit along the bottom of a phone screen.
    """
    k = scaled(w, h)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    plate_w = int(w * 0.62) if w > h else int(w * 0.84)
    plate_h = int(150 * k)
    x = int(110 * k)
    y = h - int(300 * k) if w > h else int(h * 0.62)

    draw.rectangle([x, y, x + plate_w, y + plate_h], fill=rgba(c.BRAND["panel"], 236))
    draw.rectangle([x, y, x + int(10 * k), y + plate_h], fill=rgba(PINK))
    draw.rectangle([x, y + plate_h, x + plate_w, y + plate_h + int(5 * k)],
                   fill=rgba(PINK_SOFT))
    wordmark(draw, (x + int(38 * k), y + plate_h + int(26 * k)), k, size=18, spacing=7)
    return img


def end_card(w, h):
    """A closing plate: solid brand ground with the middle left open for a
    thumbnail, a subscribe button, or whatever the editor drops in."""
    k = scaled(w, h)
    img = Image.new("RGBA", (w, h), rgba(c.BRAND["background"], 248))
    draw = ImageDraw.Draw(img)

    margin_x = int(w * 0.24) if w > h else int(w * 0.12)
    hole = (margin_x, int(210 * k), w - margin_x, h - int(250 * k))
    draw.rectangle(hole, fill=(0, 0, 0, 0))
    draw.rectangle(hole, outline=rgba(PINK), width=max(3, int(6 * k)))

    title = c.BRAND["title"]
    f_title = c.font(c.BOLD, int(56 * k))
    draw.text(((w - draw.textlength(title, font=f_title)) / 2, int(96 * k)),
              title, font=f_title, fill=rgba(PINK))

    tag = "Subscribe for the next module"
    f_tag = c.font(c.REGULAR, int(40 * k))
    draw.text(((w - draw.textlength(tag, font=f_tag)) / 2, h - int(172 * k)),
              tag, font=f_tag, fill=rgba(TEXT))
    gradient_bar(img, h - max(3, int(7 * k)), max(3, int(7 * k)), w)
    return img


BUILDERS = {
    "frame-brackets": frame_brackets,
    "frame-border": frame_border,
    "lower-third": lower_third,
    "end-card": end_card,
}


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "output/brand-overlays")

    for orientation, (w, h) in SIZES.items():
        folder = out / orientation
        folder.mkdir(parents=True, exist_ok=True)
        for name, build in BUILDERS.items():
            img = build(w, h)
            target = folder / f"{name}-{w}x{h}.png"
            img.save(target)
            clear = img.getchannel("A").histogram()[0] / (w * h) * 100
            print(f"{orientation:10} {name:16} {w}x{h}  {clear:5.1f}% clear")

    print(f"\nwrote {len(BUILDERS) * len(SIZES)} overlays to {out}")


if __name__ == "__main__":
    main()
