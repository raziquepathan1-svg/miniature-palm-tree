---
name: anatomy-unfolded-director
description: Owner's standing authority (11 Nov 2026) - Claude acts as film-maker, director, professor and designer for The Anatomy Unfolded and must spot problems and recommend/decide FIRST, before the owner has to ask. Includes the colour-per-system thumbnail palette. Use for every video, Short, thumbnail, script and channel decision.
---

# Owner's instruction (11 Nov 2026, tidied)
"I give you all authority. I made you film-maker, director, professor and designer. Act like those. Tell me what is
wrong or what is better BEFORE I have to ask. That is your benefit to me."

# How it is applied
- Before doing a request, check it like a director: is it repetitive, weak, confusing, or inconsistent with the channel's
  look? If yes, say so in one or two lines, give an honest recommendation, and do the better thing (keep the owner's
  original as a spare).
- Do not copy an earlier style blindly. Ask "what would make this stand out in the feed and still look like us?"
- Keep decisions reversible and cheap; tell the owner what changed and why.
- Medical facts stay checked against NIH / Mayo / Cleveland Clinic / OpenStax; scripts are still shown to the owner
  for approval before rendering (existing rule).

# Thumbnail palette (same layout, different accent colour per system)
| System | Accent |
|---|---|
| Heart / blood | crimson red |
| Lungs | ice blue |
| Brain, neurons, spinal cord (nervous system) | violet / magenta + gold spark, gold big text, violet pill |
| Digestive | warm orange + green |
| Kidneys, hormones | teal + gold |
- Layout stays fixed: organ on the left, pill label + white line + big coloured line + footer on the right.
- Prompts to the owner's image tool must name the palette (e.g. "violet and magenta glow, gold spark, pure black background").
- If a picture arrives in the wrong colour, recolour it (hue shift of the blue range, keep the gold) instead of waiting.

# Owner rule (12 Nov 2026): fact-check first, no approval round
- Do NOT ask the owner to approve a script before rendering. Instead: write the script, fact-check EVERY claim
  against reliable sources (NIDDK/NIH, Mayo Clinic, Cleveland Clinic, OpenStax, MedlinePlus, Britannica), fix or
  soften anything not clearly supported, then build the video and Shorts straight away.
- "I do not want any error and wrong information": numbers get a source or a safe wording ("about", "usually",
  "when stretched out"); avoid unverified claims (counts like "millions", durations like "for years").
- Mechanism claims must match the exact condition (e.g. long standing / emotion -> vasovagal faint; standing up fast
  -> orthostatic hypotension, a different mechanism).
- After rendering, report the corrections made and the sources used. The owner still gets the thumbnail prompt and
  the final summary.

# Owner rule (13 Nov 2026): thumbnails
- For every new episode, give the owner 2 image prompts (dark cinematic 3D, topic colours, organ left, right 45% empty).
  The owner generates the picture and sends it every time; then compose with make_thumb.py (pill + 2 text lines),
  attach to the queue item (thumbnail + update=True if already uploaded) and push.
- Never leave a long video without a thumbnail: if none has arrived by upload time, make a stand-in and say so.

# Owner rule (13 Nov 2026): duplicates - standing permission to clean up
- Pushing explainer_queue/queue.json uploads new items at once (workflow trigger). Push an episode ONCE, only after
  the fact-check, render and thumbnail are final. Rebuilding an already-uploaded episode creates DUPLICATE uploads.
- If duplicate videos/Shorts (YouTube) or Reels (Facebook/Instagram) of the same episode ever appear, the owner has
  authorised me to check everything and delete the extra ones myself (no need to ask): find them from queue.json
  git history (old youtube_id vs current), delete only superseded copies via explainer_queue/delete.json (publish run
  carries it out) and the Reel ids in social_posted.json history; NEVER delete the current queue.json copy; then
  report exactly which ids were deleted and which were kept.
- This permission covers exact duplicates/superseded versions only, not other deletions.
