---
name: anatomy-unfolded-tags
description: Owner's rule (2 Nov 2026) for The Anatomy Unfolded - search keywords + tags on EVERY upload (long videos AND Shorts) and on every Instagram/Facebook Reel. Use whenever packaging, uploading or captioning any video for this channel.
---

# Owner's instruction (2 Nov 2026)
"add tags and search keywords when you upload shorts and video, also in Instagram and Facebook too"

# How to apply
YouTube (videos and Shorts), done by `youtube_agent/explainer/seo_tags.py` (add an `EP` entry for every new episode, then run it):
- Description line 1 = 3 exact search phrases joined by " • " (anatomy-unfolded-search rule), Shorts too.
- Tags: 10-13 topic search phrases first, then channel base tags; total <= 480 characters. Shorts add "shorts".
- One hashtag line at the end: (#shorts for Shorts) + 3 topic hashtags + #anatomy #physiology #medicalstudent #nursing.
  YouTube shows the first 3 hashtags above the title, so the topic ones go first.
- Already-uploaded items get `"update": true` so the uploader refreshes their metadata.

Instagram + Facebook Reels (CAPTIONS file sent to the owner every week):
- Caption line 1 = the same 3 search phrases (Instagram/Facebook search reads captions).
- Hook line + 1-line fact, then "Full video on YouTube: The Anatomy Unfolded (link in bio)".
- 10-12 hashtags: topic hashtags + keyword hashtags + #anatomy #physiology #medicalstudent #mbbs #nursingstudent #theanatomyunfolded.
- Tell the owner to paste the keywords into Instagram "Advanced settings > Alt text" too.
