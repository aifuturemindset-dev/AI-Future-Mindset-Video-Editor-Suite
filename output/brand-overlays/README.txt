AI FUTURE MINDSET - BRAND OVERLAYS
==================================

Transparent PNG overlays for CapCut, Premiere, DaVinci or any editor with
layers. Drop one on a track above your footage; the clear areas let the video
through.

FILES
-----
landscape/  1920x1080 - YouTube, standard video
portrait/   1080x1920 - Shorts, Reels, TikTok

  frame-brackets   Corner brackets + wordmark. Leaves ~99% of the frame
                   clear. Use this over a whole video.
  frame-border     Continuous thin border + wordmark plate. Heavier; suits
                   talking-head footage.
  lower-third      Empty title plate. Type your own text over it in the
                   editor - it is deliberately wordless so you never have to
                   regenerate it per video.
  end-card         Closing plate with a cut-out for a thumbnail or subscribe
                   button.

USING IN CAPCUT
---------------
1. Import the PNG like any media file.
2. Drag it onto a track ABOVE your video clip.
3. Stretch it to the full length of the clip (or just the part you want).
4. Leave the blend mode on Normal - the transparency is already in the file.
   Do NOT use "Remove background" or a chroma key; there is nothing to key.
5. For lower-third, add a Text layer on top and position it inside the plate.

If the overlay appears with a black background, the file was flattened
somewhere in the chain - re-import the original PNG rather than a re-export.

BRAND
-----
Pink    #FF1493      Accent, borders, wordmark
Pink 2  #FF7AC6      Gradient end
Ground  #0E0B1F      Panels and end-card ground
Panel   #171331
Text    #F3EEFF
Display Orbitron
Body    Rajdhani

Regenerate any time, including after a brand change:
    python skills/module-video/scripts/make_overlays.py output/brand-overlays
Colours come from BRAND in skills/module-video/scripts/common.py.
