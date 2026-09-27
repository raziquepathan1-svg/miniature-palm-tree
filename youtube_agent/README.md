# YouTube Avatar Agent

Fully automatic educational YouTube channel presented by **your own AI avatar**.

This channel is set up as **Health Support Studio**, everyday health and medical education for a **US audience in American English**.

Every run it:
1. **Picks a topic.** It takes the next one from the `topic_queue` in `config.yaml` (20 starter topics are included), then invents new ones in your niche without repeating itself.
2. **Writes the script**, title, description, tags and thumbnail text (Claude), following strict health-content rules: no diagnosis, no personal medical advice, current US guidance, red-flag symptoms, and no invented patient stories.
3. **Fact-checks every health claim** (Claude + web search) against CDC, NIH, FDA, WHO, Mayo Clinic and other trusted sources. It fixes errors, adds the sources to the description, and **skips the video entirely** if it can't be made safe.
4. **Records the video with your avatar and voice** (HeyGen), with subtitles.
5. **Edits it**: adds your intro, outro and background music (ffmpeg), then makes a thumbnail.
6. **Uploads it to your channel** with a medical disclaimer and an AI-avatar disclosure in the description.

GitHub Actions runs it twice a day, so you get 2 videos/day without leaving your computer on.

---

## One-time setup (about 30-45 minutes)

### 1. Create your avatar in HeyGen
1. Sign up at heygen.com. API access needs a paid plan; check the API pricing there.
2. Create your avatar: **Avatars → Create Avatar**. Either record a short video of yourself (a *digital twin*, the most realistic option) or upload a photo (a *photo avatar*).
3. Optional: clone your voice under **Voices**.
4. Copy your API key from **Settings → API**.

### 2. Get a Claude API key
Create one at console.anthropic.com.

### 3. Create your YouTube channel and allow uploads
1. Create the channel at youtube.com, then verify it at youtube.com/verify. Verification is needed for custom thumbnails and videos longer than 15 minutes.
2. Go to console.cloud.google.com and create a project.
3. **APIs & Services → Library**: enable **YouTube Data API v3**.
4. **OAuth consent screen**: choose External, then add your Gmail as a test user.
   - **Important:** then click **Publish app** so the status is **In production**. If you leave it in *Testing*, your login expires every 7 days and the daily uploads stop.
5. **Credentials → Create credentials → OAuth client ID → Desktop app**. Download the JSON and save it as `youtube_agent/client_secret.json`.

### 4. Log in and pick your avatar (on your own computer)
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
export HEYGEN_API_KEY=...
python -m youtube_agent.main --list-avatars    # copy your avatar_id and voice_id
python -m youtube_agent.main --setup-youtube   # a browser opens: log in to the channel's Google account
```
The Google screen will say "Google hasn't verified this app". That's expected for your own personal app: click **Advanced → Go to (app name)**.

### 5. Configure your channel
Edit `youtube_agent/config.yaml`:
- `niche`, `audience`, `language`: what the channel teaches, and in which language
- `avatar_id`, `voice_id`: from step 4
- `format`: `landscape` for normal videos or `shorts` for vertical Shorts
- `topic_queue`: optional topics you want covered first

**US channel settings** (the config is already set to US English):
- In **YouTube Studio → Settings → Channel → Basic info**, set **Country of residence** to **United States**.
- For your voice, choose an **American English** voice in HeyGen (`--list-avatars` shows each voice's language), or clone your own.
- Upload times are set for US viewers: around 12 PM and 6 PM Eastern.

Optional: put `intro.mp4`, `outro.mp4` and `music.mp3` in `youtube_agent/assets/`.

### 6. Test it
```bash
python -m youtube_agent.main --script-only   # free-ish: writes a script only, check output/
python -m youtube_agent.main --dry-run       # makes the full video, doesn't upload
python -m youtube_agent.main                 # makes and uploads for real
```
**Strongly recommended for a health channel:** read each script (`output/.../script.txt` and `fact_check.json`) for the first week or two. You're the nurse, and your professional judgment is the final check. Set `privacy: "private"` in the meantime, and publish from YouTube Studio once you're happy.

**Tip:** for the first few days, set `privacy: "private"` and review each video in YouTube Studio before making it public.

### 7. Turn on daily automation
In your GitHub repo go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your Claude key |
| `HEYGEN_API_KEY` | your HeyGen key |
| `YOUTUBE_TOKEN_JSON` | the **entire contents** of `youtube_agent/youtube_token.json` |
| `HEYGEN_AVATAR_ID` / `HEYGEN_VOICE_ID` | optional, if you didn't put them in config.yaml |

Scheduled workflows only run from the repo's **default branch**, so merge this branch into it. The workflow `.github/workflows/daily-video.yml` then runs at 15:17 and 21:17 UTC (about 11 AM and 5 PM Eastern, so videos go live around noon and 6 PM). To run it now: **Actions → Daily YouTube video → Run workflow**. Every run's video files are kept as a downloadable artifact for 7 days.

---

## Costs (rough)
- **HeyGen**: the main cost. Charged per minute of avatar video, so 2 × 4-minute videos a day is about 240 minutes a month. Check your plan's API credits.
- **Claude**: a few cents per script.
- **YouTube API**: free. The default quota of 10,000 units/day allows about 6 uploads a day.
- **GitHub Actions**: free for public repos. Private repos get 2,000 free minutes a month (each run is about 10-40 min).

## Staying within YouTube's rules
- Health content: YouTube removes medical misinformation that contradicts health authorities (CDC/WHO) and can strike the channel. The fact-check step and content rules are there to prevent that. Don't turn them off.
- YouTube's "health source" label for licensed professionals: once the channel is established, you can apply to have your videos labelled as coming from a licensed nurse (search "YouTube health features for licensed professionals" to find it; eligibility requirements apply).
- AI disclosure: the agent marks every upload as **altered/synthetic content** (`contains_synthetic_media: true`), which YouTube requires for realistic AI people and voices. Keep it on.
- Monetization: YouTube demonetizes *mass-produced, repetitive* content. Make each video genuinely useful. Review scripts now and then, and add your own ideas to `topic_queue`. Quality beats quantity: 1 good video a day is better than 2 weak ones.
- Only use music you have rights to, such as the YouTube Audio Library.
