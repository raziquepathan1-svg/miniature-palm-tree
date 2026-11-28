---
name: anatomy-unfolded-cinematic
description: The owner-approved CINEMATIC style for every new The Anatomy Unfolded video (approved 15 Nov 2026 on the smell sample - "this sample video is good, make videos like this"). I act as director, director of photography, CGI director and animation director. Opens on a realistic whiteboard human, dives through the body into the organ and each part, real-looking images from the owner (Gemini/Flow) or Servier, animated motion on every shot. Use with anatomy-unfolded-director and the other anatomy-unfolded skills for every new episode, its image prompts and its thumbnail prompts.
---

# The Anatomy Unfolded - cinematic style (owner-approved 15 Nov 2026)

Reference build: `youtube_agent/explainer/ecg/osm_sample.py` + `youtube_agent/explainer/sample_smell/`
(the 2-minute smell sample the owner approved). Copy it for every new episode.

## My roles
- **Director**: story structure, decide without asking (fact-check first, then build).
- **Director of photography / cameraman**: every shot moves - zoom, pan, dive, push-in, reveal.
- **CGI director**: images look REAL (realistic medical illustration on a whiteboard), never cartoon shapes.
- **Animation director**: things inside the picture move - molecules, signals, blood, air, fluid, glows.

## Image workflow (owner's rule)
1. For each episode I write a numbered SHOT LIST of full image prompts (one per scene picture).
2. The owner generates them in Gemini or Flow and sends them (chat, or GitHub folder
   branding/the-anatomy-unfolded/thumbnails/incoming), saying which shot number each is.
3. I place them in `youtube_agent/explainer/art/<episode>/shotN.png` and build the video.
4. Until images arrive, Servier Medical Art (smart.servier.com, CC BY, credited) fills gaps; never
   Shutterstock/Getty/Google Images; never copy another channel's art (Osmosis etc.).
Every prompt ends with the same style line so all shots match:
"Style: realistic medical illustration drawn on a clean white whiteboard, soft semi-transparent skin,
organs in soft natural colours, thin dark outline, soft shading, pure white background, no text, no labels,
no arrows, no watermark, 16:9, ultra high resolution."
Each prompt: one subject, empty white space on one side (for my labels), no text in the image.

## Structure of every episode (the "journey into the body")
1. **Cold open on a whole human** (owner's whiteboard human, art/human_board.png - ask for a no-label
   version): hook text appears around him, then the camera DIVES into the organ (push-in to ~3.5-5x in
   ~2 s at the end of the hook scene).
2. **Match cut**: the next shot opens zoomed out (0.7) on the organ picture and settles to 1.0 - it feels
   like falling into the body.
3. Zoom deeper level by level (organ -> part -> tissue -> cell), each part described as the camera arrives.
4. Open loop at ~60 s ("about to take a route unlike...") then the payoff.
5. Real-life scene (why it matters), calm "see a doctor if..." scene, recap panels, next-episode bridge.

## Camera rules (DoP)
- `push(scene, point)`: slow push-in (zoom 1.0 -> 1.04) across every scene - no shot ever sits still.
- Dive between levels: `cam(end-1.6, target_x, target_y, 4.0, 1.5)` then next scene `cam(start, page, 0.7, 0)`
  + `cam(start+0.05, page, 1.0, 1.1)`.
- Board pictures are rasterised at BS=1.25, so real zooms above ~1.3x only happen during motion (dives);
  each new level gets its own full-size picture.

## Animation rules (animation director)
- `flow(points, t0, t1, period, colour, radius, count)`: particles travel along a path in a loop -
  scent molecules, air, blood cells, nerve signals (gold), food, urine, hormones.
- `glows.append((t, point, dur, radius))`: soft pulse on the part being named (amygdala, SA node...).
- Signals: gold dots; molecules/air: green; blood: red; drawn on top of the image, timed to the word.
- Labels write on at the word (Sc.t(word)); run overlap_check for video and Shorts.

## Thumbnail
Unchanged rule: 2 prompts per episode (dark cinematic 3D, the episode's palette, subject on the LEFT,
right 45% empty dark for text), owner generates, I compose with make_thumb.py. Colours never repeat on
neighbouring episodes (see anatomy-unfolded-director palette list).

## Facebook / Instagram cut (owner, 16 Nov 2026: "no followers, no views on FB")
After the Shorts are built, ALWAYS run `python3 youtube_agent/explainer/ecg/fb_cut.py <ep>_short1 <ep>_short2`
(needs the short's script.json + audio). It writes explainer_queue/<file>_fb.mp4: big burned-in captions
(Reels are watched muted), no YouTube-only "subscribe / 3:30 PM" ending, a FB/IG-native "FOLLOW" end card.
social_post.py posts the _fb file to Facebook + Instagram when it exists (YouTube keeps the normal Short).

## Smooth transitions + labels (owner, 27 Nov 2026: "I want smooth transition from picture to next picture")
- ONE page, no page slides or hard cuts: each new picture CROSS-FADES over the old one (~1.1 s) while the camera glides back to the
  full view; the old picture is removed only after the new one fully covers it. Labels fade out just before the dissolve.
- Before a dissolve the camera slowly pushes in (zoom ~1.35-1.5, up to ~2.6 for body -> cells) on the part we go into next.
- Organelle / organ close-ups: first show it glowing in its place on the bigger picture (location first), push in, dissolve to the close-up.
- Every named part: NAME on the right third + pointer line with arrow to the exact spot + a soft glow (Stage.label in ecg/osm_cell.py).
- Template: youtube_agent/explainer/ecg/osm_cell.py (Stage class: picture / label / say / clear / focus / drift).
- Never put "<" or ">" (e.g. "->") in a YouTube title/description: the upload fails with invalidDescription. Use "→".

## INFINITE ZOOM between levels (owner, 28 Nov 2026, with reference videos "zooming into my hand" / "zooming into a flower")
- Going deeper (body → organ → tissue → cell → organelle → molecule) is ONE continuous dive into the exact point we talk about:
  the camera pushes into that point (zoom ~2.4) while the next, deeper picture GROWS OUT of it (soft-edged, centred on the
  point), then takes over the full frame seamlessly. No cut, no slide.
- Then STOP: hold on the new level while we explain it with labels + pointers, then ZOOM AGAIN into the next point.
- Implemented in Stage.focus() + Stage.picture() (ecg/osm_cell.py: zoom_through). Any focus() followed by a new picture
  becomes a zoom-through automatically; a picture without a focus before it is a cross-fade (use for side-steps, not depth).
