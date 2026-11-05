"""The Anatomy Unfolded: comments as the channel, same way as Health Support Studio (owner, 3 Nov 2026).

    python -m youtube_agent.explainer.comments comment   # ONE comment on every public video + Short (pin it in Studio)
    python -m youtube_agent.explainer.comments inbox     # new viewer comments -> explainer_queue/comment_inbox.json
    python -m youtube_agent.explainer.comments reply     # posts explainer_queue/reply_jobs.json

Full videos: the day's question first, then the series playlist, the previous part and the subscribe link.
Shorts: the full-video link first (only once the full video is public), then the question.
Replies are written in the daily check (never personal medical advice; emergencies -> local emergency number;
spam/insults skipped) and posted by the 'reply' mode. The YouTube API cannot pin comments: pin them in Studio."""
import datetime as dt
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build

from .. import comment_replies as CR
from ..uploader import _credentials

QDIR = Path(__file__).resolve().parents[2] / "explainer_queue"
QUEUE, DONE = QDIR / "queue.json", QDIR / "comments_posted.json"
MAX_PER_DAY = 20
QUESTIONS = {
    "heart_anatomy_v2": "Your heart has 4 chambers and 4 valves. Which part surprised you most?",
    "heart_physiology": "Put your hand on your chest: that lub-dub is your valves snapping shut. Did you know that before?",
    "heart_electrical": "Did you know your heart has its own pacemaker? Which part of the ECG do you find hardest?",
    "heart_attack": "Do you know all the heart attack warning signs? Share this with someone who should.",
    "blood_vessels": "Arteries vs veins: which difference surprised you most?",
    "blood_pressure": "Do you know your own blood pressure numbers? When did you last check them?",
    "high_blood_pressure": "Why do you think so many people with high blood pressure don't know they have it?",
    "heart_failure": "Did you know heart failure doesn't mean the heart has stopped? What else would you like explained?",
    "arrhythmia": "Have you ever felt your heart skip a beat? Tell us below.",
    "heart_valves": "Have you ever been told you have a heart murmur? Ask us anything about heart valves.",
    "lung_anatomy": "Did you know your right lung has 3 lobes but your left has only 2? What surprised you most?",
    "asthma": "Do you or someone you know have asthma? What's your biggest trigger? (Educational only: always follow your doctor's asthma plan.)",
    "pneumonia": "Did you know pneumonia makes your air sacs fill with fluid, like a wet sponge? Have you had your flu or pneumonia vaccine? (Educational only, not medical advice.)",
    "copd": "Did you know smoke from indoor cooking fires is a major cause of COPD in many countries? Share this with someone who smokes. (Educational only, not medical advice.)",
    "how_breathing_works": "Put a hand on your belly and breathe in slowly. Feel it move out? That's your diaphragm moving down. What else should we explain?",
}
SERIES = {"Cardiovascular System": ["heart_anatomy_v2", "heart_physiology", "heart_electrical", "heart_attack", "blood_vessels",
                                    "blood_pressure", "high_blood_pressure", "heart_failure", "arrhythmia", "heart_valves"],
          "Respiratory System": ["lung_anatomy", "how_breathing_works", "asthma", "pneumonia", "copd"]}


def _q(eid):
    return f"💬 {QUESTIONS.get(eid, 'What would you like us to explain next?')} Tell us below 👇"


def texts(queue, sub, playlists):
    ids = {q["id"]: q.get("youtube_id") for q in queue}
    out = {}
    for q in queue:
        vid = q.get("youtube_id")
        if not vid:
            continue
        eid = q["id"].split("_short")[0]
        if q["kind"] == "video":
            lines = [_q(eid), ""]
            for name, eps in SERIES.items():
                if eid in eps:
                    n = eps.index(eid) + 1
                    lines.append(f"This is part {n} of our {name} series.")
                    if playlists.get(name.lower()):
                        lines.append(f"▶ Watch the whole series in order: https://www.youtube.com/playlist?list={playlists[name.lower()]}")
                    if n > 1 and ids.get(eps[n - 2]):
                        lines.append(f"⏮ Previous part: https://youtu.be/{ids[eps[n - 2]]}")
            lines += [f"🔔 Subscribe for a new body explainer every day: {sub}", "Educational only, not medical advice."]
            out[vid] = "\n".join(lines)
        elif ids.get(eid):
            out[vid] = (f"▶ Watch the full video here: https://youtu.be/{ids[eid]}\n\n{_q(eid)}\n\n"
                        f"🔔 Subscribe for a new body explainer every day: {sub}")
    return out


def comment():
    yt = build("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    channel = yt.channels().list(part="id", mine=True).execute()["items"][0]["id"]
    sub = f"https://www.youtube.com/channel/{channel}?sub_confirmation=1"
    queue = json.loads(QUEUE.read_text())
    done = json.loads(DONE.read_text()) if DONE.exists() else {}
    today = dt.datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
    budget = done.pop("_budget", {})
    used = budget.get("used", 0) if budget.get("day") == today else 0
    todo = {v: t for v, t in texts(queue, sub, CR_playlists(yt)).items() if v not in done}
    # a Short's comment waits until its full video is public, so the link works
    public = CR_public(yt, list(todo) + [q["youtube_id"] for q in queue if q["kind"] == "video" and q.get("youtube_id")])
    long_of = {q["youtube_id"]: next((x["youtube_id"] for x in queue if x["id"] == q["id"].split("_short")[0]), None)
               for q in queue if q["kind"] == "short" and q.get("youtube_id")}
    posted = 0
    for vid, text in todo.items():
        if vid not in public or (vid in long_of and long_of[vid] not in public):
            continue
        if used + posted >= MAX_PER_DAY:
            print("  (Today's comment budget is used; the rest go next run.)")
            break
        try:
            cid = yt.commentThreads().insert(part="snippet", body={"snippet": {
                "videoId": vid, "topLevelComment": {"snippet": {"textOriginal": text}}}}).execute()["id"]
            done[vid] = {"id": cid}
            posted += 1
            print(f"  Commented on https://youtu.be/{vid}")
        except Exception as e:
            print(f"  (Could not comment on {vid}: {e})")
    done["_budget"] = {"day": today, "used": used + posted}
    DONE.write_text(json.dumps(done, indent=2) + "\n")
    print(f"Posted {posted} comment(s); {len(todo) - posted} waiting (not public yet).")


def CR_public(yt, ids):
    from ..yt_comments import _public
    return _public(yt, ids)


def CR_playlists(yt):
    from ..yt_comments import _playlists
    return _playlists(yt)


def _setup_replies():
    CR.INBOX, CR.JOBS, CR.DONE = QDIR / "comment_inbox.json", QDIR / "reply_jobs.json", QDIR / "comments_replied.json"
    queue = json.loads(QUEUE.read_text())
    CR._titles = lambda: {q["youtube_id"]: q["title"] for q in queue if q.get("youtube_id")}


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "comment":
        comment()
    else:
        _setup_replies()
        {"inbox": CR.inbox, "reply": CR.reply}[mode]()
