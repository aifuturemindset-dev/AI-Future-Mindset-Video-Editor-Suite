# Module videos in Remotion

Slide decks, voiceover and screenshot overlays as React components, so timing
is something you see and drag rather than something anyone guesses at.

## Why this exists

The ffmpeg pipeline in `skills/module-video/` renders the same videos without
a browser, and it is the right tool for a batch re-render. What it cannot do
is show you the result while you adjust it. Every timing error in Module 00
and Module 01 came from the same place: nobody could see the slides and hear
the voiceover at the same time until the render finished.

Here you scrub the timeline with both together. A slide that lands two
seconds late takes about five seconds to fix.

## Run it

```bash
cd remotion
npm install
npm start          # opens Remotion Studio at localhost:3000
```

Pick `module-01` in the sidebar. Press space to play, drag the playhead, use
the left and right arrows for single frames.

## Fix a slide that lands wrong

Every slide's cue lives in `src/modules/module-01.ts`:

```ts
{ image: "slide-07.png", at: 43, shots: [...] },
```

`at` is the second the voiceover reaches that slide. Note where the playhead
sits when the narration actually says it, change the number, save. The
preview reloads as you type.

Slides without `at` divide the gap between their anchored neighbours, so you
only need to mark the ones that matter — usually where the narration says
"Step N".

## Render

```bash
npx remotion render module-01 out/module-01.mp4
```

Add `--frames=1200-1500` to render a stretch while checking a change.

## Pointing at things in raw footage

A screen recording shows a cursor moving but not where attention belongs, so
a viewer following along misses the control being clicked. `Callout` marks it
the way the tutorial screenshots do — a box around the control, a curved
arrow, and a label naming the action — and `SkillNote` pins a post-it naming
the skill in use.

See the `demo-annotated` composition; its cues live in
`src/modules/demo-annotated.ts`:

```ts
{
  at: 1, until: 5,
  box: { x: 1180, y: 300, width: 420, height: 90 },
  label: "Click New project",
  side: "left",
  skill: "hook-writer",
}
```

Get the coordinates by exporting the frame you are annotating and reading
pixel positions off it:

```bash
ffmpeg -ss 4 -i public/demo/raw-clip.mp4 -frames:v 1 /tmp/frame.png
```

The composition is 1920x1080, so positions in that still are the numbers to
use directly. `side` is where the label sits (`left`, `right`, `above`,
`below`); the arrow always curves to the nearest edge of the box.

The box pulses gently while it is on screen. That is deliberate — it holds
the eye through a long step without the marker ever drifting off the control.

## Add a module

1. Put the assets in `public/module-02/` — `slides/`, `screenshots/`, `narration.mp3`
2. Copy `src/modules/module-01.ts` to `module-02.ts` and edit the slide list
3. Add it to `MODULES` in `src/Root.tsx`

Render the deck to slide images first:

```bash
soffice --headless --convert-to pdf --outdir /tmp deck.pptx
pdftoppm -r 96 -png /tmp/deck.pdf public/module-02/slides/slide
```

A deck whose fonts are embedded needs those fonts installed or the text
overflows its boxes — see `skills/module-video/references/troubleshooting.md`.

## Brand

`src/brand.ts` holds the tokens, taken from the course kit's own stylesheet:
pink `#FF1493` on `#0E0B1F`, Orbitron for display, Rajdhani for body. Change
them there and every composition follows.

Fonts are served from `public/fonts/` rather than a CDN, so renders do not
depend on network access.

## Rendering inside a restricted sandbox

Remotion normally downloads its own Chrome from `remotion.media`. Where that
host is blocked, point it at an existing browser:

```bash
npx remotion render module-01 out/module-01.mp4 \
  --browser-executable=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell \
  --chrome-mode=chrome-for-testing --gl=swangle
```

On an ordinary machine none of those flags are needed.
