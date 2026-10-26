---
name: yt-comment
description: >-
  Draft replies to YouTube comments in the creator's voice, triaged by which
  ones are worth answering. Use for "reply to my comments", "handle the
  comment section", "someone asked X", or a pasted comment thread.
---

# yt-comment

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
- HSS: questions are open and personal and never invite arguments about medical facts, vaccines or
  treatments; no "thanks for watching". RRS: keep the A-or-B vote plus one open question line.
  One pinned comment per video. Draft only; the owner posts or pins.


The comment section is a retention surface, not a chore. Replies in the first few hours are what
decide whether a thread becomes a conversation other people read.

## Before you write

1. Read `~/.claude/youtube/voice.md` if it exists. That is the user's voice profile: how they talk
   on camera, the words they never use, who they are talking to, what they will not claim. If it
   does not exist, ask for **three of their own videos**, read or transcribe them, infer the voice,
   and write the file. A script in the wrong voice is worse than no script, because they have to
   read it out loud.
2. Never invent a number, a result or a source. If a figure would strengthen it and you do not have
   one, ask for it or write the line without it.

## Triage first, always

Sort what the user pastes into four piles and say how many are in each before writing anything:

1. **Questions** - answer them. These are your next video's topics, so note the repeats.
2. **Corrections** - if they are right, say so plainly and thank them. Never argue a fact you
   cannot check.
3. **Praise** - reply to a few, briefly, with something specific from their comment. A wall of
   identical "thank you!" replies reads as automated because it is.
4. **Bait** - do not reply. Say so and move on. Never write a comeback, however deserved.

## Writing the reply

- Under 30 words. A long reply in a comment thread is a blog post nobody asked for.
- Answer the actual question in the first sentence.
- One question back, only when it is real.
- No emoji unless the user's own replies use them. Check their voice file.
- Never promise a video you have not agreed to make.

## The heart and the pin

Say which ONE comment to pin and why. Pin the question the most people also have, not the nicest
one. Heart generously - it costs nothing and it is visible.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
