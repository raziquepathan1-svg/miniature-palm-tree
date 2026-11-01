# Explainer videos (anatomy & physiology / diseases)

Approved style (owner, 31 Oct 2026): **our own colour line-art diagrams** drawn in code, textbook look:
black outlines, flat colours (blue = oxygen-poor, red = oxygen-rich, pink = muscle), hollow white flow arrows,
gold glow + label tags timed to the narration, moving blood dots, text panel on the right.

- `heart/lineart.py` - the heart diagram (`python3 lineart.py` colour still, `--bw` black-and-white still).
- `heart/render4.py` - the approved sample video (`python3 render4.py`, or `stills` for one frame per scene).
- `heart/script.json` + `heart/audio/` - sample narration (Kokoro am_michael; real videos use the cloned voice).
- `heart/render.py`, `heart/render3.py` - shared helpers (fonts, scenes timed by word, zoom views).
- `ox/fig_1`, `ox/fig_3` - OpenStax Anatomy & Physiology 2e figures (CC BY 4.0). Any scene showing them must
  carry the on-screen credit "Figure: OpenStax, Anatomy & Physiology 2e (Rice University), CC BY 4.0".

Rules: labels and text are always drawn in code (never AI-generated text); scripts are fact-checked
(`youtube_agent/fact_check.py`) and approved by the owner before rendering.

## UPDATE 1 Nov 2026: Osmosis style is the approved style
The flat line-art version above was replaced. The approved recipe is in `.claude/skills/anatomy-unfolded-style/SKILL.md`
and the reference implementation is `ecg/osm_full.py` (engine `ecg/board.py`).
