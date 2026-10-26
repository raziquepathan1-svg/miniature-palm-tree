---
name: yt-retention
description: >-
  Read a YouTube Studio audience-retention export and find where viewers
  actually leave, then say what to change. Use for "why do people stop
  watching", "my retention is bad", a pasted retention chart or CSV, or "fix
  my pacing".
---

# yt-retention

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


The retention graph is the only honest feedback YouTube gives you. Almost nobody exports it.

```bash
python3 retention.py retention.csv --duration 600
python3 retention.py retention.csv --transcript transcript.srt
```

Getting the file: Studio -> a video -> Analytics -> Engagement -> the audience-retention chart ->
the download icon -> "Audience retention".

## Three different problems

- **HOOK LEAK** - what is lost in the first 30 seconds. Under 25% is healthy. This is always the
  first thing to fix and it is always the first fifteen seconds of script, never the edit.
- **CLIFFS** - single steep drops. A cliff is a moment: a topic change with no signposting, a
  sponsor read, a long setup. With `--transcript` the tool prints what was being said there, which
  is what makes the report actionable instead of interesting.
- **SLIDE** - the steady bleed across the middle. A flat slide is pacing. The fix is cutting, not
  rewriting.

## What to hand back

Name the single biggest leak and one change for it. Not a list of five. Then, only if asked, the
rest. And if the hook leak is healthy and the slide is flat, say the video is fine and the problem
is packaging - send them to `/yt-package`.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
