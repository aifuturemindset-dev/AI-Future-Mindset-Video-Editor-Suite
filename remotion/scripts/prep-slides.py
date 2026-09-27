"""Upscale the 12 storyboard stills to 1080p.

They arrive at 480x270 - pasted into chat, which resamples - so a 4x upscale
is unavoidable until the originals turn up. Browser scaling would do this
bilinear and look mushy; LANCZOS with a light unsharp pass holds the type
edges much better. This is recovery, not resolution: it cannot invent detail
the 480px source never had.
"""
from pathlib import Path
from PIL import Image, ImageFilter

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "assets/finish-one/source-stills"
DST = REPO / "remotion/public/finish-one/slides"

# Storyboard order. Names are the slide's own headline, so a wrong mapping is
# obvious on sight rather than three minutes into a render.
# Storyboard order. The source files already carry these names, so a wrong
# mapping is obvious on sight rather than three minutes into a render.
ORDER = [p.stem for p in sorted(SRC.glob("*.webp"))]

DST.mkdir(parents=True, exist_ok=True)
for name in ORDER:
    src = SRC / f"{name}.webp"
    im = Image.open(src).convert("RGB")
    big = im.resize((1920, 1080), Image.LANCZOS)
    big = big.filter(ImageFilter.UnsharpMask(radius=2.0, percent=115, threshold=3))
    out = DST / f"{name}.png"
    big.save(out, optimize=True)
    print(f"{im.size[0]}x{im.size[1]} -> 1920x1080  {out.name}  {out.stat().st_size//1024}KB")
