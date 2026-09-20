# Config format

Both pipelines take a single JSON config. Paths may be absolute or relative to
where the script runs.

## Shared keys

| Key | Required | Meaning |
|---|---|---|
| `module` | yes | Module number as a string, e.g. `"01"` |
| `output_dir` | yes | Where the finished MP4 and its `build/` folder go |
| `screenshots_dir` | yes | Folder holding the screenshot PNGs |
| `output_name` | no | Filename override; defaults to `Module_<module>_<Cut>.mp4` |
| `fade` | no | Overlay fade in/out seconds, default `0.35` |

## Overlay cut

Extra keys for `build_overlay.py`:

| Key | Required | Meaning |
|---|---|---|
| `lesson` | yes | The lesson video to composite onto |
| `phases` | yes | List of `{at, label, shots}` — see below |
| `phases_end` | yes | Second at which the last phase stops |
| `intro_headline` / `intro_subhead` | yes | Opening title card |
| `outro_headline` / `outro_subhead` | yes | Closing title card |
| `intro_seconds` / `outro_seconds` | no | Card durations, default 3 and 4 |
| `card_right_margin` | no | Card inset from the right edge, default 70 |
| `card_bottom_margin` | no | Card bottom above frame bottom, default 260 |

A phase is one instruction the narration gives. `at` is the second the
narration starts that instruction, taken from the transcript. `shots` are the
screenshots for that step, in the order a viewer performs them; the phase's
span is divided evenly among them.

```json
{
  "module": "01",
  "output_dir": "output",
  "screenshots_dir": "assets/screenshots",
  "lesson": "assets/module-01-lesson.mp4",
  "intro_headline": "MODULE 01",
  "intro_subhead": "Write Your First Hooks",
  "outro_headline": "NICE WORK",
  "outro_subhead": "On to Module 02",
  "phases": [
    {
      "at": 10.3,
      "label": "open the hook writer skill",
      "shots": [
        ["01-open-chat.png", "Open a new chat"],
        ["02-slash-hook.png", "Type /hook-writer"]
      ]
    },
    {
      "at": 24.8,
      "label": "paste your brief",
      "shots": [
        ["03-paste-brief.png", "Paste your brief"]
      ]
    }
  ],
  "phases_end": 41.5
}
```

Get the anchors by running `scripts/extract_cues.py` on the lesson and reading
where each instruction begins. Do not invent them — evenly spaced guesses put
screenshots on the wrong sentence.

## Script cut

Extra keys for `build_script_cut.py`:

| Key | Required | Meaning |
|---|---|---|
| `narration` | yes | The voiceover recording |
| `slides` | yes | List of `{title, bullets, voiceover, shots}` |
| `card_top` | no | Card top edge in pixels, default 250 |

`voiceover` is the script text for that slide. It is not rendered — its word
count sets the slide's share of the runtime, so paste the real text even
though viewers never see it. `shots` may be omitted for title-only slides.

```json
{
  "module": "01",
  "output_dir": "output",
  "screenshots_dir": "assets/screenshots",
  "narration": "assets/module-01-vo.mp4",
  "slides": [
    {
      "title": "Welcome to Module 01",
      "bullets": ["Hooks that stop the scroll", "One system, repeatable"],
      "voiceover": "Welcome to module one. In this module you will learn how to write hooks that stop the scroll.",
      "shots": []
    },
    {
      "title": "Step 1: Open the hook writer",
      "bullets": ["Start a new chat", "Type a forward slash"],
      "voiceover": "Open a new chat in your Content Engine project and type a forward slash to see your installed skills.",
      "shots": [
        ["01-open-chat.png", "Open a new chat"],
        ["02-slash-hook.png", "Type /hook-writer"]
      ]
    }
  ]
}
```

The build prints the implied words per minute. If it falls outside 80-200 it
warns, because that usually means the script and the recording are different
takes rather than a pair.

## Branding

Colors, wordmark and title live in `BRAND` in `scripts/common.py`. Change them
there and both pipelines follow. Encoding parameters sit alongside; keep them
identical across segments or concat produces an unplayable file.
