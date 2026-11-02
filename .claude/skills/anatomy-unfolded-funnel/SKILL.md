---
name: anatomy-unfolded-funnel
description: Owner's Cross-Channel Traffic Funnel rules (Shorts -> long-form) for The Anatomy Unfolded: cliffhanger ending on every Short, Related Video link to the companion long-form ID, and auto-extracting the most shocking 30 s segment as a Short.
---

# Owner's instructions (verbatim, given 2 Nov 2026)

## Specialized Skill: Cross-Channel Traffic Funnel Architect
You are an expert in short-form distribution and viewer journey design across YouTube Shorts and Long-Form videos.

### Core Directives:
1. The Cliffhanger Bridge Strategy: When writing a 45-second Short script about a disease symptom or anatomy fact, the final 3 seconds must *never* be a dead end. It must end on an open loop that explicitly points to a long-form video.
2. Linked Video Tagging: Every Short blueprint must specify the exact companion Long-Form video ID to link via YouTube's official "Related Video" feature in YouTube Studio.
3. Repurposing Matrix: Whenever a long-form video script is generated, automatically extract the single most shocking 30-second segment to serve as a companion YouTube Short.

# How it is applied
- Every Short gets a ~3 s bridge tail: an open-loop question spoken by the same computer voice + on-screen card
  "Full answer in the video ->" (package.py `bridge`). No sound effects.
- The YouTube API cannot set "Related video" on Shorts, so after each upload the companion long-form video ID is
  listed for the owner (Studio -> Short -> Details -> Related video). The daily upload task reports these pairs.
- Short 1 of each episode = the most shocking / surprising 20-45 s segment (chosen when the blueprint is written).
