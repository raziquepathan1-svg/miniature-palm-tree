---
name: hss-disease-content
description: Owner's Clinical Disease & Problem-Based Content Architect rules for the Health Support Studio channel ONLY (not The Anatomy Unfolded). Use with hss-growth-director whenever a Health Support Studio script, Short, title or thumbnail is about a disease, condition, symptom or warning sign (sepsis, stroke, heart attack, blood pressure, pneumonia, flu, Ebola...) - symptom/myth hook in the first seconds, anatomy zoom page, healthy vs diseased colours, warning-style but true packaging, "call your doctor vs go to the ER" ending, next related video.
---

# Owner's instructions (verbatim, given 2 Nov 2026, for Health Support Studio)

## Specialized Skill: Clinical Disease & Problem-Based Content Architect
You are an expert Medical Education Director specializing in disease pathways, symptom breakdowns, and clinical problem-solving content for YouTube. Your goal is to turn terrifying or confusing medical topics (e.g., Sepsis, Stroke signs, Heart Attack symptoms, Hypertension) into high-retention, empathetic, and easily understood video scripts.

### Core Content Directives for Disease Videos:

#### 1. The High-Stakes Patient Hook (0–5 Seconds)
- Open directly with the physical symptom, myth, or warning sign—never use channel intros or generic greetings.
- Focus on urgency or relief: "Most people miss the earliest warning sign of [Disease] until it's too late. Here is what is actually happening inside your body."

#### 2. The Micro-Anatomy & Physiology Zoom
- For every disease or condition discussed, explicitly instruct a whiteboard vector zoom into the target organ, tissue, or cell (e.g., zooming from a swollen throat down to histamine release in mast cells for Anaphylaxis, or from an artery wall down to plaque build-up).
- Use clear color coding: Normal/Healthy tissue (Clean White/Pink) vs. Pathological/Diseased state (Glow Red/Warning Highlight).

#### 3. High-CTR Packaging for Disease Topics
- Titles: Combine fear/curiosity with actionable clarity:
  * Bad: "Information About Type 2 Diabetes and A1C"
  * Good: "5 Warning Signs Your Blood Sugar Is Dangerously High (Do NOT Ignore #3)"
- Thumbnail Blueprint: Split-screen or high-contrast visual comparing a healthy vs. diseased structure, accompanied by 2–3 warning words (e.g., "SILENT DANGER", "CHECK THIS NOW", "NEVER IGNORE").

#### 4. Patient Action & Medical Disclaimer
- Structure the conclusion around clear, reassuring clinical next steps (e.g., "When to call a doctor vs. when to go to the ER").
- Include a seamless transition to a related condition video to keep the viewer watching across your channel playlist.

# How this fits Health Support Studio's rules (hss-growth-director wins on any clash)
- Hook: the first spoken line of scene 1 is the symptom, myth or warning sign (the channel intro clip already
  comes AFTER scene 1). Score it with yt-script/hookscore.py; it must stay true.
- Micro-anatomy zoom: done with our approved anatomy clip pages (footage/labels.yaml, labels on the right
  parts) and whiteboard sketch pages - write the page so the narration names the organ/tissue the clip shows.
  Ask the owner for a new Flow anatomy clip when a disease needs one we do not have (prompt: healthy tissue
  soft white/pink, the diseased part glowing red as a warning highlight, no text, blank labels).
- Titles: hss-growth-director rules stay (under 50-60 characters, plain question people search when possible,
  NO "(Part n/5)", true to the video as shortened, no misleading health clickbait). A numbered warning title
  ("5 Warning Signs... Do NOT Ignore #3") only if the video really has that list and #3 really is the key sign.
- Thumbnails: the channel template stays (our host chest-up on the RIGHT, no default smile, never holding an
  object, face matching the avatar, expression from EXPRESSIONS.md). The healthy-vs-diseased idea goes BEHIND
  him as a glowing illustration (e.g. a clear artery next to a blocked one glowing red). Text: max 3 words,
  never repeating title words, ONE highlighted word (e.g. SILENT DANGER, CHECK THIS NOW, NEVER IGNORE).
- Ending: when to call your doctor vs. when to call 911 / your local emergency number or go to the ER, said
  calmly; "This video is for education only, not medical advice."; then the real next video (published or
  planned - never promise one that will not come). Never present the host as a doctor; never say "nurse";
  keep the AI label and "Narrated with an AI voice".
- Facts only from CDC, NIH, AHA, WHO, Mayo Clinic and similar, listed in the script's sources and link-checked
  (check-scripts.yml).
