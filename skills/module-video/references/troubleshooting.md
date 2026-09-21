# Troubleshooting

Failures that produce unplayable or wrong output, and why each happens. Every
one of these was hit in real use.

## The output has no moov atom and nothing will play it

Symptom: `ffprobe` reports `moov atom not found`. VLC shows only its cone,
Windows says the file is corrupt or unsupported, browsers show a dead player.
The file has a plausible size, which makes it look fine in a listing.

An MP4's `moov` atom is its index. Without one there is no video, only bytes.
Re-downloading cannot fix it because the file was written broken.

Causes, in the order worth checking:

**A subtitle track in the concat.** If one input carries a `mov_text` stream
and the others do not, concatenating with `-c copy` produces a file with no
index. This is the most common cause and the least obvious, since the subtitle
track is invisible in a player. Pass `-sn` when normalizing any source that
might have one.

**Segments with no audio track.** A still rendered from a PNG has no audio
unless you give it one. Concatenating a silent segment with a segment that has
audio produces the same failure. Feed every still an `anullsrc` source.

**Mismatched encode parameters.** Concat requires identical codec, resolution,
pixel format, frame rate and timebase across segments. `-c copy` cannot
reconcile differences; it writes garbage.

The fix is structural: encode every segment through the same parameter set, and
verify duration after concat. `common.assemble()` falls back to a re-encode
when the result drifts from the sum of its parts.

## drawtext fails to parse `ih`

```
[Parsed_drawtext_7] Undefined constant or missing '(' in 'ih-196'
```

`drawtext` exposes `w` and `h` for the input dimensions. `iw` and `ih` are
`drawbox` variables and do not exist in `drawtext`. Use `y=h-196`.

This one is easy to copy from a working `drawbox` line into a `drawtext` line
without noticing. The whole filter chain fails to configure, so the output is
empty rather than merely wrong.

## drawtext has no letter-spacing option

`letterSpacing` is not an ffmpeg option and is silently useless. To space a
wordmark, put the spaces in the string: `"A   I   F   U   T   U   R   E"`.

## Concat looks for segments in the wrong directory

Relative paths in a concat listing resolve against the **listing file's**
directory, not the current directory and not the segments' directory. If the
listing is written next to the output while the segments live in a build
folder, ffmpeg reports `Impossible to open 'seg_0.mp4'`.

Write absolute paths into the listing. `common.concat()` does this.

## The video plays but nothing is on screen at the right time

Screenshots spaced evenly will not match narration. Derive timing from the
audio — either the lesson's subtitle track or a script's per-slide word count.
See the timing section in SKILL.md.

If overlays fade at the wrong moment, check the `setpts` shift. A still loaded
with `-loop 1` starts its own clock at zero, so its `fade` offsets are relative
to itself. `setpts=PTS+START/TB` moves that clock onto the timeline so the
fades line up with the `enable` window.

## A source video shows only black frames

Sampling frames returns black at every timestamp. The file is almost certainly
an audio recording with a placeholder video track — check the video bitrate. A
value near 20 kbps for 1080p can only be a static frame. Treat the file as
narration; do not try to use it as footage.

## Lesson captions disappear behind the branded panel

A lower-third panel drawn over a lesson will cover burned-in captions, which
usually sit in exactly that band. Keep persistent panels off the lesson and put
the step list on title cards instead. If the panel must stay, scale the lesson
to fit above it — that pillarboxes the frame but hides nothing.

## Fonts will not download

Google Fonts and model hosts are blocked in many sandboxed environments (HTTP
403 through the proxy) even when PyPI is reachable. Test before depending on a
download.

`fonts-comic-neue` installs from the system package manager and gives a modern
handwriting face suitable for callouts:

```bash
apt-get install -y fonts-comic-neue
```

`common.fonts()` falls back to DejaVu automatically so a build never dies on a
missing font. Say which font was actually used when reporting the result.

## The download "fails" but the file is fine

A player reporting it cannot open the MRL, or a script reporting the file is
not found, is describing a **missing file** — not a corrupt one. Confirm the
file is on disk at the expected size before re-rendering anything:

```powershell
Get-ChildItem "$env:USERPROFILE\Downloads\*.mp4" |
  Select-Object Name, @{n='MB';e={[math]::Round($_.Length/1MB,1)}}
```

A truncated download shows a smaller size than the source. Compare against the
origin's `content-length` rather than guessing.

## LibreOffice says "source file could not be loaded"

A deck that is structurally valid — `unzip -t` clean, slide XML present — still
refuses to convert, and the error names no reason.

Check which LibreOffice packages are actually installed before blaming the
file:

```bash
dpkg -l | awk '/^ii  libreoffice/{print $2}'
```

`libreoffice-core` alone has no format importers. Without
`libreoffice-impress` there is nothing that can read a `.pptx`, so every deck
fails identically regardless of content. The giveaway is that a plain text
file fails too, which points at the installation rather than the document:

```bash
apt-get install -y libreoffice-impress
```

Embedded fonts (`ppt/fonts/*.fntdata`) are a plausible-looking suspect and are
usually innocent. Confirm the importer exists before stripping anything out of
a deck — an untouched deck renders with its intended typography.

The `javaldx` warning is unrelated noise; conversion does not need Java.

Rendering to frames, once conversion works:

```bash
soffice --headless --convert-to pdf --outdir DIR deck.pptx
pdftoppm -r 150 -png DIR/deck.pdf DIR/slide   # needs poppler-utils
```
