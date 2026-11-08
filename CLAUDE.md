# YouTube automation repo
## Channels
- Health Support Studio: US English health explainers, 1 long video/day + ~45s Short
- The Anatomy Unfolded: anatomy/physiology/disease, "medical professor + animator" style
- Restore Remake Studio: US luxury home/garden makeovers (youtube_agent/channels/restore_remake/)
- Hidayah: Hindi Islamic channel (islamic_channel/, own upload + voice workflows)
## Key files
- Pipeline: youtube_agent/ main, planner, fact_check, voice, editor, uploader
- Packaging/comments: packaging.py, set_thumbnails.py, comment_replies.py; social: social.py
- Automation: .github/workflows/ (prefer running workflows over doing tasks by hand)
## Token rules
- Never read history.json, *_jobs.json or all of script_bank/; search for the one entry needed
- Never open .mp4, voice/ or image files unless I ask
- Don't explore the repo to get oriented; use this file
- Short answers; show only changed lines
## Content rules
- Hook in first 3s, no logo/intro; pattern interrupt every 10-15s; curiosity loop
- Titles: problem first + info gap; thumbnail text 2-4 words, never repeats title
- Shorts end on a cliffhanger and link to the long video
- Packaging: 3 titles, thumbnail concept, 150-word SEO description with chapters, 15 tags
- Pinned comment starts a conversation; viewer questions become next videos
- Health: accurate, no diagnosis, cite CDC/NIH/Mayo, end with "call your doctor vs go to ER"
- Visuals always modest
