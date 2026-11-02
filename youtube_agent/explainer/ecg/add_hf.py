"""Add Heart Failure - Mon 9 Nov 2026: video 6 PM, Shorts 12 PM + 9 PM IST."""
import datetime as dt, json, shutil
import package as P
import growth_apply as G
import bridge

ep = {"id": "heart_failure", "focus": [0.5, 0.5], "video": P.HERE / "final_heart_failure.mp4", "dir": P.SP / "hf",
      "title": "What Is Heart Failure? Why the Heart Gets Weak (Symptoms, Causes & Treatment)",
      "about": "Heart failure explained simply: it does not mean the heart has stopped. It means the heart cannot pump enough blood for the body, because the muscle is too weak to squeeze or too stiff to fill. Learn the main causes (heart attack, high blood pressure, valve disease, cardiomyopathy, diabetes), what ejection fraction means, why left-sided heart failure causes breathlessness and fluid in the lungs, why right-sided heart failure causes swollen legs and ankles (pitting edema), the warning signs, how doctors diagnose it (BNP blood test, chest x-ray, echocardiogram) and how it is treated. Perfect for MBBS, nursing, pharmacy and biology students.",
      "short": [(["hook", "define"], "Heart Failure Doesn't Mean Your Heart Stopped"), (["left", "right"], "Why Heart Failure Makes You Breathless and Swollen")],
      "tags": ["heart failure", "congestive heart failure", "heart failure symptoms", "ejection fraction", "left sided heart failure", "right sided heart failure", "pitting edema", "bnp", "echocardiogram", "cardiomyopathy"]}
P.EPISODES.append(ep)
bridge.QUESTIONS[ep["id"]] = ["So what causes it?", "And how is it treated?"]
KEY = "Heart failure • Congestive heart failure • Heart failure symptoms"
CH = [("hook", "Heart failure is not a stopped heart"), ("causes", "Causes & ejection fraction"), ("left", "Left vs right heart failure"), ("symptoms", "Warning signs & diagnosis"), ("treat", "Treatment & summary")]
P.INTRO = 3.6
day = dt.date(2026, 11, 9)
REPO = G.REPO
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith(ep["id"])]
shutil.copy(ep["video"], REPO / "heart_failure.mp4")
shutil.copy(P.SP / "thumbs_ai" / "heart_failure_thumb.jpg", REPO / "heart_failure_thumb.jpg")
st = {i: t for i, t, _ in P.scene_times(ep)}
chap = "\n".join(f"{P.stamp(0 if n == 0 else st[i])} {name}" for n, (i, name) in enumerate(CH))
when = dt.datetime.combine(day, dt.time(12, 30), dt.timezone.utc)
q.append({"id": ep["id"], "kind": "video", "file": "heart_failure.mp4", "thumbnail": "heart_failure_thumb.jpg", "title": ep["title"],
          "description": f"{KEY}\n\n{ep['about']}\n\nCHAPTERS\n{chap}\n{P.FOOTER}", "tags": ep["tags"] + ["the anatomy unfolded"],
          "playlist": "Cardiovascular System", "publish_at": when.strftime("%Y-%m-%dT%H:%M:%SZ"), "youtube_id": None})
for k, hh in ((0, (6, 30)), (1, (15, 30))):
    sh = P.OUT / f"{ep['id']}_short{k + 1}.mp4"
    t = P.short(ep, sh, k)
    bridge.add_bridge(sh, ep["id"], k)
    shutil.copy(sh, REPO / sh.name)
    s_ = dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc)
    q.append({"id": f"{ep['id']}_short{k + 1}", "kind": "short", "file": sh.name, "thumbnail": None, "title": f"{t} #Shorts",
              "description": f"{ep['about']}\n\nFull video: \"{ep['title']}\" on The Anatomy Unfolded.\n{P.FOOTER} #shorts",
              "tags": ep["tags"] + ["shorts"], "playlist": None, "publish_at": s_.strftime("%Y-%m-%dT%H:%M:%SZ"), "youtube_id": None})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
