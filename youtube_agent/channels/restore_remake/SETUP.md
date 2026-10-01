# Restore Remake Studio: one-time setup

Restore Remake Studio runs on the same free agent as Health Support Studio, but it has its **own**
script bank, history, logins and schedule. The two channels never share an account.

| What | Where |
|---|---|
| Settings (niche, styles, colors, upload time) | `config.yaml` (this folder) |
| Free pre-written scripts | `script_bank/` (12 included, one per day) |
| Logo, banner, bios | `branding/restore-remake-studio/` |
| Daily video workflow | **Actions → Restore Remake Studio - daily video** |
| Instagram/Facebook workflow | **Actions → Restore Remake Studio - post Short to Instagram and Facebook** |

## Every day, automatically
| Time (Saudi) | What happens |
|---|---|
| ~7 AM | A ~3-4 minute video + a vertical Short are made and the video is uploaded **scheduled** |
| 8 PM (9 PM in winter) | The video goes public on YouTube (1 PM New York) |
| 2 AM next day | The Short goes public on YouTube Shorts |
| ~9:25 PM | The Short is posted as a Reel on Instagram and Facebook (only if the YouTube video is public) |

You can watch each video in the **YouTube Studio app** before it goes public. If something is wrong, set it
to **Private** and the Instagram/Facebook post is skipped too.

---

## Step 1: Connect YouTube (10 min, browser only)
You can reuse the Google Cloud app you made for Health Support Studio. You only need a **new login**
for the new channel.

1. Make sure the Health Support Studio Google Cloud app is **In production** (Google Cloud Console →
   **Google Auth Platform → Audience**). If it still says *Testing*, add `restoreremakestudio@gmail.com` as a
   **test user** there.
2. Open **developers.google.com/oauthplayground**.
3. Click the ⚙️ gear (top right) → tick **Use your own OAuth credentials** → paste the **same** Client ID and
   Client secret you used for Health Support Studio → close.
4. In "Input your own scopes" paste:
   `https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube`
   and click **Authorize APIs**.
5. Sign in as **restoreremakestudio@gmail.com** and pick the **Restore Remake Studio** channel. On the
   "Google hasn't verified this app" screen click **Advanced → Go to …**, then allow.
6. Click **Exchange authorization code for tokens** and copy the **Refresh token**.
7. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**:
   - Name: `RRS_YOUTUBE_REFRESH_TOKEN`, Value: the refresh token.
8. Verify the channel's phone number at **youtube.com/verify** (needed for custom thumbnails).
9. Optional but recommended: find the channel ID (YouTube Studio → **Settings → Channel → Advanced
   settings**, starts with `UC`) and put it in `config.yaml` under `youtube.channel_id`. Then uploads stop
   if the wrong account is ever logged in.

## Step 2: Connect Instagram and Facebook (15 min)
Requirements: the Instagram account is a **professional** account and is **linked to the Restore Remake
Studio Facebook Page** (Facebook Page → **Settings → Linked accounts → Instagram → Connect**).

Use the **same Meta developer app** as Health Support Studio and follow `youtube_agent/SOCIAL_SETUP.md`,
**Part 3, step B**, with these differences:
- In step B4, allow access to the **Restore Remake Studio** Page and Instagram account.
- In step B7, copy the `id` and `access_token` listed under **Restore Remake Studio**.

Then add 3 GitHub secrets (the names start with `RRS_`, so they never replace the health channel's):

| Name | Value |
|---|---|
| `RRS_META_PAGE_ID` | Restore Remake Studio Page ID |
| `RRS_META_PAGE_TOKEN` | Restore Remake Studio Page token |
| `RRS_IG_USER_ID` | Restore Remake Studio Instagram user ID |

⚠️ Never paste these tokens in a chat or anywhere public.

Test it: **Actions → Restore Remake Studio - post Short to Instagram and Facebook → Run workflow**, tick
**Only test the Facebook/Instagram connection**. Nothing is posted.

## Step 3: Test a video
**Actions → Restore Remake Studio - daily video → Run workflow**, tick **Make the video but don't upload**.
After ~20-30 minutes, download the `rr-video-…` file from the run page and watch it.

The free Pexels key (`PEXELS_API_KEY`) is shared with Health Support Studio, so the stock clips work
right away.

---

## When the free scripts run out
Each run's summary shows how many pre-written scripts are left. When it gets low, open Claude Code and say:
*"write 30 more scripts for Restore Remake Studio's script bank"*. If the bank is empty, the agent writes
scripts with the paid Claude API instead (a few cents per video).

## Optional: background music
Put a royalty-free `music.mp3` (YouTube Studio → **Audio Library**, "no attribution required") in
`assets/`, and every video gets quiet background music.
