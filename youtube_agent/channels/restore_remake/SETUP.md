# Restore Remake Studio: one-time setup

Restore Remake Studio makes **visual makeover videos** with no narration: an empty or tired space (living
room, bedroom, backyard, rooftop terrace, balcony, kitchen, bathroom, garage, front yard, attic) is
transformed step by step into a style (Japandi, Boho, Coastal...), drawn by AI. 10 spaces × 9 styles =
90 different makeovers before anything repeats. It has its **own** history, logins and schedule; the two
channels never share an account.

| What | Where |
|---|---|
| Settings (niche, styles, colors, upload time) | `config.yaml` (this folder) |
| Spaces, styles, titles | `config.yaml` → `makeover:` |
| Video maker | `youtube_agent/makeover.py` |
| Logo, banner, bios | `branding/restore-remake-studio/` |
| Daily video workflow | **Actions → Restore Remake Studio - daily video** |
| Instagram/Facebook workflow | **Actions → Restore Remake Studio - post Short to Instagram and Facebook** |

## Every day, automatically
| Time (Saudi) | What happens |
|---|---|
| ~7 AM | AI draws the makeover; a ~30-40 s landscape video + a vertical Short are made and uploaded **scheduled** |
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

## Step 3: Add a Gemini key for the AI images (5 min, free)
Gemini keeps the **same room** between steps, so the makeovers look real. Without this key the agent uses
the free Pollinations service instead, where the room can change a little between steps.
1. Open **aistudio.google.com** and sign in with any Google account.
2. Click **Get API key** → **Create API key** (pick or create a project if asked) and copy the key.
3. In GitHub add the secret `GEMINI_API_KEY` with that key.

Google's free daily limit for image models changes from time to time. If the free limit is used up or a
call fails, that day's video is drawn with Pollinations instead, so a video is still made. To always use
Gemini, turn on billing for that Google project; one makeover is 5-6 images, about $0.20-$0.30 per video.

## Step 4: Test a video
**Actions → Restore Remake Studio - daily video → Run workflow**, tick **Make the video but don't upload**.
After ~20-30 minutes, download the `rr-video-…` file from the run page and watch it.

The run summary says which image service was used (Gemini or Pollinations).

---

## Recommended: real background music
Without music files the agent plays a soft generated background tune. Real music makes the videos much
better: download 5-10 calm, upbeat tracks from **YouTube Studio → Audio Library** (filter: "No attribution
required"), put the `.mp3` files in `assets/music/`, and each video picks one at random.

## More spaces and styles
After about 90 videos every space × style pair has been used and they start repeating. Ask Claude Code to
*"add more spaces and styles to Restore Remake Studio's makeover list"* any time.

## Honesty and YouTube rules
The images are AI-generated design concepts. Every upload is marked as altered/synthetic content, and the
description says the makeover is an AI concept, not a real renovation. Keep it that way: YouTube can
remove or demonetize AI videos that pretend to be real.
