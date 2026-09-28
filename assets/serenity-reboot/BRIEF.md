# Video 2 — Serenity Reboot

*The Day I Said "I Need a Reset"* · overwhelm → identity · stated length ~7.3 min

**Status: waiting on assets. Do not begin assembly.**

## Have

- `slides/01.jpg` … `15.jpg` — 1920x1080, extracted from the supplied
  `Serenity_Reboot_AI_Reset.pptx`, which is actually a zip of numbered JPGs
  rather than a PowerPoint. Full resolution, so no upscaling is needed here
  (unlike Video 1, whose stills arrived at 480x270 through chat).
- `script02.txt` — 119 spoken lines, 684 words.
- 4 of 15 animations (1280x720, 24fps, 10.0s each).

## Missing

- The voiceover recording.
- 11 animations.

## Check on arrival

684 words against the stated 7.3 minutes implies about 94 wpm, where normal
narration runs 110-150 and Script 01 ran near 139. Divide the real recording's
length by the word count before trusting either number; if it comes out near
4.9 minutes the "7.3" was an estimate, and if it really is 7.3 the read carries
long pauses that the forced aligner will handle but that should not be mistaken
for drift.

## Distribution

| | |
| --- | --- |
| YouTube title | I Built an AI That Reschedules My Week When I Say "I Need a Reset" (It Won 1st Place) |
| TikTok hook | When your calendar makes your chest tight, say these three words. |
| Instagram hook | AI can sort your life. Only after you decide what your life is for. |
| Pull quote | AI can sort your life. Only after you decide what your life is for. |
| Thumbnail | Exhale expression · "I NEED A RESET" |

Keywords: AI calendar assistant · how to stop feeling overwhelmed · AI
hackathon winner · prioritize tasks with AI · AI for busy moms

Structure: feeling-first hook, midpoint turn, comment prompt as a fill-in rule.

## Method

Same pipeline as Video 1, with its corrections already in place: forced
alignment (`skills/module-video/scripts/align_forced.py`) for cue timing,
animations matched to slides by image correlation rather than upload order,
and the storyboard's sound design synthesised by `soundbed.py`.
