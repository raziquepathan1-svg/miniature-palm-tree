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

# Thumbnail colour plan (owner 13 Nov: "colours are coming the same pattern")
- Never two neighbouring episodes in the same palette. Used so far: heart = red/dark; lungs = ice blue, teal for Breathing;
  brain/neuron/spine = violet+gold; autonomic = red vs teal split; endocrine = teal+gold; digestive = orange+green;
  kidney = crimson+gold (recoloured from teal); immune = MAGENTA + LIME (prompts below).
- Upcoming plan: skin = warm coral/sand + cream-white; musculoskeletal = bone ivory + deep blue; senses/eye = electric blue +
  amber; reproductive = soft rose + deep plum; lymphatic = lime + indigo. Check this list before writing any prompt.

# Colour decision (14 Nov): blue
- Musculoskeletal = ivory bone + deep blue (kept; neighbours Skin = coral, next = non-blue).
- Blue already used by lungs (ice blue). Do NOT use blue/indigo for the next 3 episodes.
- Lymphatic = lime green + amber (changed from lime + indigo). Then: eyes/senses = amber + violet; reproductive = rose + plum.
- Hearing/ear = ROSE-PINK + silver-white on burgundy-black (no blue, no amber/violet since Eye just used it). Reproductive = plum + gold.

## Scene images from the owner + camera work (owner, 14 Nov 2026)
- The owner wants students to learn the easy way: pictures must be related to the narration, never boring, and
  look REAL but on a whiteboard (realistic see-through human, organs in colour) - not simple cartoon shapes
  (owner: the first cartoon person "looks like a joker").
- "Journey into the body": every episode opens on the whole human, then the camera zooms through the body into
  the organ, then into each part of it, describing each part as the camera arrives.
- Workflow: I write the image prompts (a shot list per episode); the owner generates them in Gemini or Flow and
  sends them (chat or branding/the-anatomy-unfolded/thumbnails/incoming); I use them in the clips and do all the
  camera work as director of photography (zoom, pan, different angles, reveals). No need to ask - just give prompts.
- Prompt rules: 16:9, highest resolution offered, NO text or labels in the image (I add sharp labels myself),
  plain white whiteboard background, the same style sentence in every prompt so all shots match, one subject per
  image with empty space on one side for labels.
- Never copy Osmosis (or any channel's) artwork or branding, and never use Shutterstock/Getty/Google-Images
  pictures. Free sources: Servier Medical Art (CC BY, credited), Wikimedia Commons (PD/CC0/CC BY), Bioicons,
  OpenStax, and the owner's own AI images.
