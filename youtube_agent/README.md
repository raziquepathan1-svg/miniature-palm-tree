# YouTube Video Agent: Health Support Studio

An automatic educational YouTube channel: **everyday health and medical topics for a US audience, in American English**.

No avatar is needed. Each video is a **natural AI voice** over **branded graphics and stock video clips**, with captions. It's free except for a few cents of Claude usage per video. A HeyGen talking-avatar mode is built in too, if you want it later (`video.mode: "avatar"`).

Every day it:
1. **Picks a topic.** It takes the next one from `topic_queue` in `config.yaml` (20 starter topics are included), then invents new ones without repeating itself.
2. **Writes the script and on-screen graphics** (Claude), following strict health-content rules: no diagnosis, no personal medical advice, current US guidance, red-flag symptoms, and no invented stories.
3. **Fact-checks every health claim**, in both the narration and the on-screen text (Claude + web search), against CDC, NIH, FDA, WHO, Mayo Clinic and other trusted sources. It fixes errors, lists the sources in the description, and **skips the video** if it can't be made safe.
4. **Narrates it** with a free AI voice (Kokoro, which allows commercial use).
5. **Builds the video**: branded slides (title, key points, big numbers, myth vs fact, warning signs, subscribe) over free Pexels stock footage, with captions. Then it adds your intro, outro and music if you have them, and makes a thumbnail.
6. **Uploads it as Private** to your channel, with a medical disclaimer and AI disclosure, for you to review.

### Your daily routine (optional, about 5 minutes, works on your phone)
Every day at about **6 AM Saudi time** the agent makes the video and uploads it **scheduled**. YouTube then makes it **public automatically at 12 PM New York time** (7 PM Saudi, or 8 PM in winter). You don't have to be online.

Any time before then:
1. Open the **YouTube Studio** app → **Content** and find the scheduled video.
2. Watch it. If it's fine, do nothing, because it publishes by itself. If something's wrong, set **Visibility → Private** or delete it.

To make an extra video on demand from your phone: in the **GitHub app**, open the repo → **Actions → Daily YouTube video → Run workflow** (you can type a topic).

### Free scripts: the script bank
The agent first uses the **pre-written, fact-checked scripts** in `script_bank/` (one per day, in order). These cost nothing, because they're written in a Claude chat, not through the paid API. Each run's summary shows how many are left.

**When they run out**, open Claude Code and say: *"write 30 more scripts for my YouTube channel's script bank"*. If the bank is empty, the agent falls back to the paid API (and stops when the credit is gone).

After adding scripts, the **Check script bank** workflow checks their length, on-screen text and source links.

### Instagram and Facebook Reels
Every day a ~45-second vertical Short on the same topic is also made and, after the YouTube video goes public, posted as a Reel to Instagram and Facebook. Setup: see [SOCIAL_SETUP.md](SOCIAL_SETUP.md).

### Video styles (they rotate, one per day)
**Explainer → Myth vs Fact → Quick Short (vertical) → Warning Signs → Top Questions**. Edit them under `video.styles` in `config.yaml`.

---

## One-time setup

### 1. Claude API key (writes and fact-checks the scripts)
Go to **console.anthropic.com**, add a small amount of credit ($5 lasts a long time), and create an API key.

### 2. Pexels API key (free stock video)
Sign up at **pexels.com/api** (free) and copy your API key. Without it, videos still work, using animated brand backgrounds instead of stock clips.

### 3. Allow uploads to your YouTube channel (browser only, nothing to install)
Do all of this signed in as **healthsupportstudio@gmail.com**.

**A. Create a Google Cloud project**
1. Go to **console.cloud.google.com**, then use the project picker (top left) → **New project** → name it `Health Support Studio` → **Create**, and select it.
2. **APIs & Services → Library**: search for **YouTube Data API v3** and click **Enable**.

**B. Consent screen**
1. **APIs & Services → OAuth consent screen** (it may be called **Google Auth Platform → Branding/Audience**). Choose **External**.
2. App name: `Health Support Studio Uploader`. Support email and developer email: healthsupportstudio@gmail.com. Save.
3. **Audience**: click **Publish app** so the status is **In production**. If you leave it in *Testing*, the login expires every 7 days.

**C. Create the login keys**
1. **Credentials → Create credentials → OAuth client ID**, with application type **Web application**.
2. Under **Authorized redirect URIs** add exactly: `https://developers.google.com/oauthplayground`
3. Click **Create**, then copy the **Client ID** and **Client secret**.

**D. Get the permanent login (refresh token)**
1. Open **developers.google.com/oauthplayground**.
2. Click the ⚙️ gear (top right) → tick **Use your own OAuth credentials** → paste the Client ID and Client secret → close.
3. On the left, in "Input your own scopes", paste:
   `https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.force-ssl`
   (the last one lets the agent post the question comment under each video)
   then click **Authorize APIs**.
4. Sign in as **healthsupportstudio@gmail.com**, choose the **Health Support Studio** channel if asked, and allow access. On the "Google hasn't verified this app" screen, click **Advanced → Go to …**.
5. Click **Exchange authorization code for tokens**, then copy the **Refresh token**.

**E. Add them to GitHub Secrets**: `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`.

(Alternative for developers: put a Desktop-app `client_secret.json` in `youtube_agent/` and run `python -m youtube_agent.main --setup-youtube`.)

### 4. Try it (optional, on a computer with Python)
```bash
export ANTHROPIC_API_KEY=sk-ant-...
export PEXELS_API_KEY=...
python -m youtube_agent.main --voice-sample   # listen to 7 free voices, then set voice.voice in config.yaml
python -m youtube_agent.main --script-only    # writes a script only: check output/.../script.txt
python -m youtube_agent.main --dry-run        # makes the full video without uploading: watch output/.../final.mp4
```

### 5. Turn on the daily automation (GitHub)
In the GitHub repo go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your Claude key |
| `PEXELS_API_KEY` | your Pexels key |
| `YOUTUBE_CLIENT_ID` | from step 3C |
| `YOUTUBE_CLIENT_SECRET` | from step 3C |
| `YOUTUBE_REFRESH_TOKEN` | from step 3D |

Scheduled runs only work from the repo's **default branch**, so merge this branch into it. It then runs every day at 15:17 UTC (about 11 AM Eastern, 7 PM UAE). To run it right away: **Actions → Daily YouTube video → Run workflow**. Each run's page shows the review link, and the video files are kept for 7 days.

### Settings (`config.yaml`)
- `voice.voice`: `af_heart` (default, warm female), `af_bella`, `af_nicole`, `af_sarah`, `am_michael`, `am_fenrir`, `am_puck`
- `video.mode`: `voice_slides` (free) or `avatar` (HeyGen, paid)
- `video.target_minutes`: length of normal videos (default 4)
- `channel.topic_queue`: topics to cover first
- `youtube.review_before_publish`: `true` uploads as Private for your review
- Optional: put `intro.mp4`, `outro.mp4` and `music.mp3` in `youtube_agent/assets/`

**YouTube Studio → Settings → Channel → Country of residence:** set this to the country where you **actually live**. It controls payments and taxes, not your audience. The videos still target US viewers.

---

## Costs (rough)
- **Voice, graphics, stock footage, captions:** free
- **Claude** (script + fact-check with Claude Sonnet 5): about **$0.80 per video** with web-search fact-checking, or roughly **$0.25** in budget mode (`fact_check_searches: 0`, the current setting). Each run log shows the tokens used. Set a monthly spend limit and keep auto-reload OFF in console.anthropic.com. When the credit runs out, that day's run just fails, with no extra charges.
- **YouTube API, GitHub Actions:** free. Private repos get 2,000 free minutes a month; each run takes about 10-20 minutes.

## Staying within YouTube's rules
- **Health content:** YouTube removes medical misinformation and can strike the channel. The fact-check step and content rules exist to prevent this. Keep them on, and review each video before publishing.
- **AI disclosure:** every upload is marked as altered/synthetic content (`contains_synthetic_media: true`). Keep it on.
- **Monetization:** YouTube doesn't monetize *mass-produced, repetitive* content. Your daily review, your own added tips, the rotating styles and genuinely useful topics are what make the channel eligible. Quality beats quantity.
- **Music:** only use music you have rights to, such as the YouTube Audio Library.
- **Stock footage:** Pexels videos are free for commercial use.
