---
name: yt-chapters
description: >-
  Write YouTube chapters from a transcript, validated against YouTube's own
  rules so they actually render. Use for "add chapters", "timestamps",
  "break this video into sections".
---

# yt-chapters

## Our channels come first (read this before anything below)

This repo runs **Health Support Studio** and **Restore Remake Studio**. For either channel, load
`hss-growth-director` or `rrs-growth-director` first (and `rrs-clip-prompts` for makeover prompts).
Their rules and their "Decisions on clashes" always win over anything in this file.

- This skill is an extra check or analysis only. Suggest; never change the pipeline, config, script
  bank, schedule or a live video unless the owner says so.
- Do not ask for `voice.md` or "three of your videos": the channel skill is the voice profile.
- Never invent a number. Health Support Studio: every claim and title must pass the fact check, no
  health clickbait. Restore Remake: narration only describes what is visible.
- Skip the "ship it, or change it?" closing line; answer the way the channel skill says.


```bash
python3 chapters.py transcript.srt --target 8
```

## The rules, which are not optional

A chapter list that breaks any of these silently does not become chapters at all - the block just
sits in the description doing nothing:

- The first entry must be **00:00**.
- There must be **at least three**.
- Each must be **at least 10 seconds** long.

The tool checks all three and tells you when a list is invalid rather than letting you paste it.

## Retitle every line

`chapters.py` finds the BOUNDARIES well - it scores the pauses you actually took by how much the
vocabulary shifts across them. The titles it emits are the topic words, and they are a draft. A
chapter called "Thumbnails Titles Packaging" is a placeholder. Rewrite each one as the promise of
that section, in the user's voice, three to five words.

Chapters are also a retention diagnostic: if a section cannot be named in five words, it is two
sections or it is filler.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
