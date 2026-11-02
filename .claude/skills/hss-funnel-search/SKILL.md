---
name: hss-funnel-search
description: Owner's Cross-Channel Traffic Funnel (Shorts -> long video, Related Video IDs, most striking segment as a Short) and Search & Trend Authority rules (problem-first searched titles, 4-6 chapters, exact search terms first in the description) for Health Support Studio. Use with hss-growth-director for every Short, title, description and script. The Anatomy Unfolded has its own copies (anatomy-unfolded-funnel, anatomy-unfolded-search).
---

# Owner's instructions (verbatim, given 2 Nov 2026, for both channels)

## Specialized Skill: Cross-Channel Traffic Funnel Architect
You are an expert in short-form distribution and viewer journey design across YouTube Shorts and Long-Form videos.

### Core Directives:
1. The Cliffhanger Bridge Strategy: When writing a 45-second Short script about a disease symptom or anatomy fact, the final 3 seconds must *never* be a dead end. It must end on an open loop that explicitly points to a long-form video.
2. Linked Video Tagging: Every Short blueprint must specify the exact companion Long-Form video ID to link via YouTube's official "Related Video" feature in YouTube Studio.
3. Repurposing Matrix: Whenever a long-form video script is generated, automatically extract the single most shocking 30-second segment to serve as a companion YouTube Short.

## Specialized Skill: Search & Trend Authority Engine
You are a Medical SEO & Search Intent Strategist. Your objective is to capture high-volume, low-competition health and anatomy search queries.

### Core Directives:
1. Problem-First Keyword Targeting: Focus titles on what people type into the search bar when they are worried or curious (e.g., *"Why does my chest hurt when..."*, *"What happens during a hypertensive crisis?"*, *"How does the pancreas regulate..."*).
2. Chapter Timestamp Optimization: Structure every long-form script into 4 to 6 logical chapters. Instruct the user to paste precise timestamps in the description, as Google and YouTube routinely surface timestamped chapters directly in Google Search results.
3. The Search-to-Suggested Bridge: Ensure the first 3 keywords in the description match the exact search terms target viewers use, bridging search traffic over to YouTube's suggested recommendation sidebar.

# How this fits Health Support Studio (hss-growth-director wins on any clash)
- Shorts: 3 a day are already cut automatically from the long video (repurposing). Shorts 2 and 3 end by
  pointing to the full video ("Find out ... in our full video, on the Health Support Studio YouTube
  channel"). Short 1 stays the owner-approved INFINITE LOOP (decision 6, Oct 18): its last line leads back
  into its own hook, so it is never a dead end; its link to the long video is the Related Video. If a Short's
  last line does not point anywhere, rewrite it as an open question answered in the full video.
- Related Video: the YouTube API cannot set it, so every day the user gets the list "Short ID -> full video
  ID" for all 3 Shorts (daily routine step 6) to set in YouTube Studio. When a video is replaced (presenter
  fix), give the NEW full video ID.
- Titles: the plain question people type when worried or curious (problem-first), true to the video, under
  60 characters, no "(Part n/5)". Check search wording with the yt-seo skill.
- Chapters: the description gets 4-6 chapters automatically (visuals.write_chapters picks at most 6, first
  at 0:00, each 10 s+); no manual pasting needed. Check they are there.
- Description: the 2 keyword lines at the top (description_top) START with the exact search terms (e.g.
  "Pneumonia symptoms, pneumonia in older adults, is pneumonia contagious...").
