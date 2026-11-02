---
name: anatomy-unfolded-style
description: The approved video style and production recipe for The Anatomy Unfolded (@theanatomyunfolded, formerly Restore Remake Studio). Use for every anatomy / physiology / disease explainer video for this channel.
---

# The Anatomy Unfolded: approved video style (owner approved 1 Nov 2026)

Reference: Osmosis videos (owner's examples). Approved sample: video 1 "The Heart's Electrical System",
code in `youtube_agent/explainer/ecg/osm_full.py` (engine: `board.py`).

## Owner rules
- Drawing / whiteboard teaching ONLY. No real human faces, no real-video clips. Drawn-style clips from Flow are OK
  for the hook (only if anatomically correct; cut before any wrong part).
- Things must COME AND GO: every idea in the narration gets its own picture that pops in, is labelled, then fades
  away. The camera zooms into details and slides to new boards. Never one static picture for the whole video.
- Light, soft colours like Osmosis. No dark/heavy colours, no black outlines.
- Fact-checked script (NIH/NHLBI, MedlinePlus, CDC, AHA, Mayo, Cleveland Clinic) -> owner approval -> video.
- Finish one thing completely before starting the next (Rule #1). Prompts must work first time.

## Look
- Pure white background. Intro: `render_ecg.intro_frame` (navy, ECG line, logo, "THE ANATOMY UNFOLDED") - 3.6 s with ONE smooth soft swell (no bell) (owner override, 2 Nov 2026); the hook starts right after it.
- Pictures: soft painted/pastel medical illustrations, coloured outlines. Sources in order:
  1. Servier Medical Art (smart.servier.com, CC BY 4.0) -> on-screen credit line + description credit (see servier/CREDITS.md).
  2. Text-free AI illustrations (gpt-image, prompt: "modern hand-drawn anatomy explainer style, soft pastel,
     painterly shading, thin coloured outlines (not black), watercolor texture, pure white background, no text").
     Check anatomy by eye before use; never use AI text.
  3. Simple code icons in the same pastel style (bolt, batteries) when nothing else fits.
- Text: Patrick Hand SC (small caps handwriting), UPPERCASE, written letter by letter. Colours: maroon (122,31,61)
  main, purple (91,45,130), teal, blue for right heart/deoxygenated, red for left/oxygenated, gold for electrical.
- Labels outside the drawing with thin leader lines that draw on; "└" sub-points drawn as small strokes.
- Soft rounded pastel panels behind note groups (pink, lilac, cream, mint, sky).
- Titles underlined with a thin hand line. Effects: white glows on parts, gold pulses along paths, rings.

## Layout & timing
- Drawing on the left, notes on the right (like Osmosis). Zoom 1.5-1.9 for small structures, labels placed outside
  the drawing and inside the visible view.
- Every visual event is timed to a word in the narration (`Sc.t(word, nth)`); erase the previous beat's items
  when the next idea starts (`bd.erase`).
- ~3 min per video, 10 scenes, 150 wpm. End with summary flowchart + "next video".

## Upload
- Category Education, not made for kids, disclaimer "Educational content only, not medical advice", Servier credit.

## Label overlap rule (owner, 2 Nov 2026: "word over writing another word")
Before rendering any video run `python3 overlap_check.py <module>` (youtube_agent/explainer/ecg/overlap_check.py).
It must report `overlaps: 0`. Also check end-of-scene frames so no label is still half-written when it is erased.
