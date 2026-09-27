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

### Your daily routine (about 10 minutes)
1. Open the **YouTube Studio** app → **Content**, and find the new private video.
2. Watch it. If you like, add a tip of your own in the description or a pinned comment.
3. Set **Visibility** to **Public** (or **Schedule** it for about 12 PM ET).

This human review keeps a health channel safe, and it's what YouTube looks for when deciding on monetization.

### Video styles (they rotate, one per day)
**Explainer → Myth vs Fact → Quick Short (vertical) → Warning Signs → Top Questions**. Edit them under `video.styles` in `config.yaml`.

---

## One-time setup

### 1. Claude API key (writes and fact-checks the scripts)
Go to **console.anthropic.com**, add a small amount of credit ($5 lasts a long time), and create an API key.

### 2. Pexels API key (free stock video)
Sign up at **pexels.com/api** (free) and copy your API key. Without it, videos still work, using animated brand backgrounds instead of stock clips.

### 3. Allow uploads to your YouTube channel
1. Go to **console.cloud.google.com**, signed in as **healthsupportstudio@gmail.com**, and create a project.
2. **APIs & Services → Library**: enable **YouTube Data API v3**.
3. **OAuth consent screen**: choose **External**, then add healthsupportstudio@gmail.com as a test user.
   - **Important:** then click **Publish app** so the status is **In production**. If you leave it in *Testing*, your login expires every 7 days and uploads stop.
4. **Credentials → Create credentials → OAuth client ID → Desktop app**. Download the JSON file and save it as `youtube_agent/client_secret.json`.

### 4. Log in once (on your own computer)
```bash
pip install -r requirements.txt
python -m youtube_agent.main --setup-youtube   # a browser opens: sign in as healthsupportstudio@gmail.com
```
Google will say "Google hasn't verified this app". That's normal for your own personal app: click **Advanced → Go to (app name)**.

### 5. Try it
```bash
export ANTHROPIC_API_KEY=sk-ant-...
export PEXELS_API_KEY=...
python -m youtube_agent.main --voice-sample   # listen to 7 free voices, then set voice.voice in config.yaml
python -m youtube_agent.main --script-only    # writes a script only: check output/.../script.txt
python -m youtube_agent.main --dry-run        # makes the full video without uploading: watch output/.../final.mp4
```

### 6. Turn on the daily automation (GitHub)
In the GitHub repo go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your Claude key |
| `PEXELS_API_KEY` | your Pexels key |
| `YOUTUBE_TOKEN_JSON` | the **entire contents** of `youtube_agent/youtube_token.json` (created in step 4) |

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
- **Claude** (script + fact-check): about $0.10-0.30 per video, so roughly **$3-10 a month** for one video a day
- **YouTube API, GitHub Actions:** free. Private repos get 2,000 free minutes a month; each run takes about 10-20 minutes.

## Staying within YouTube's rules
- **Health content:** YouTube removes medical misinformation and can strike the channel. The fact-check step and content rules exist to prevent this. Keep them on, and review each video before publishing.
- **AI disclosure:** every upload is marked as altered/synthetic content (`contains_synthetic_media: true`). Keep it on.
- **Monetization:** YouTube doesn't monetize *mass-produced, repetitive* content. Your daily review, your own added tips, the rotating styles and genuinely useful topics are what make the channel eligible. Quality beats quantity.
- **Music:** only use music you have rights to, such as the YouTube Audio Library.
- **Stock footage:** Pexels videos are free for commercial use.
