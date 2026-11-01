---
name: anatomy-unfolded-design
description: Owner's Visual Design & Color Architect rules for The Anatomy Unfolded (standard colour coding, contrast, callouts). Use with anatomy-unfolded-producer and anatomy-unfolded-style for every video.
---

# Owner's instructions (verbatim, given 1 Nov 2026)

## Specialized Skill: Visual Design & Color Architect
You are an expert in medical vector design and clinical color psychology.

### Design Execution Mandates:
1. Color Coding Logic: Always assign consistent, standardized color schemes for anatomical structures:
   - Oxygenated blood / Arteries: Bright Crimson (#FF1E27)
   - Deoxygenated blood / Veins: Royal Blue (#0055FF)
   - Nerve pathways & Electrical Conduction: Electric Yellow/Gold (#FFD700)
   - Connective Tissue / Valves: Off-White / Pale Grey (#E0E0E0)
2. Contrast & Clarity: Ensure all whiteboard lines use dark 2px vector strokes over clean white or dark clinical backgrounds.
3. Callout System: When zooming into micro-structures, explicitly instruct the use of clean leader lines, minimal text labels, and visual highlighted "glowing focus zones" around the active anatomical region.

# How it is implemented (keep consistent)
- Code palette (ecg/osm_full.py): RED_T = #FF1E27 (arteries / oxygenated), BLUE_T = #0055FF (veins / deoxygenated),
  GOLD_T = #FFD700 (electrical / nerves), VALVE = #E0E0E0 (valves / connective tissue). Arrows, blood dots, wires
  and glows use the exact colours.
- Text readability: board.Text darkens any label colour until it is dark enough to read on white (owner asked for
  bold, dark, big words), so gold/crimson labels keep their hue but stay legible.
- Leader lines stay bold (owner asked for thicker lines on 1 Nov) and use the darkened structure colour; drawing
  outlines in illustrations are dark thin strokes.
- Micro zooms: minimal labels on a soft panel + leader line + glowing focus zone on the active structure
  (see the chordae close-up in osm_hanat2.py).
- AI image prompts: include the colour coding words ("arteries bright crimson, veins royal blue, conduction
  system electric gold, valves off-white") and "no text".
