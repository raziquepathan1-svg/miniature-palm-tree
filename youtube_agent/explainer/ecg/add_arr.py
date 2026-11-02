"""Add Arrhythmia - Tue 10 Nov 2026: video 6 PM, Shorts 12 PM + 9 PM IST."""
import datetime as dt, json, shutil
import package as P
import growth_apply as G
import bridge

ep = {"id": "arrhythmia", "focus": [0.5, 0.5], "video": P.HERE / "final_arrhythmia.mp4", "dir": P.SP / "arr",
      "title": "What Is an Arrhythmia? Why Your Heart Skips a Beat (AFib, Tachycardia & Bradycardia)",
      "about": "Arrhythmia explained simply: what it means when your heart skips a beat, races or beats irregularly. Learn how a normal heartbeat starts in the SA node, the normal resting heart rate (60 to 100 beats per minute), tachycardia vs bradycardia, why extra early beats (premature beats) feel like a skipped beat, how atrial fibrillation (AFib) can cause clots and stroke, why ventricular fibrillation causes cardiac arrest and needs CPR and a defibrillator (AED), common causes, warning signs, and how arrhythmias are diagnosed (ECG, Holter monitor) and treated (medicines, blood thinners, pacemaker, ablation). Perfect for MBBS, nursing, pharmacy and biology students.",
      "short": [(["hook", "skipped"], "Why Does Your Heart Skip a Beat?"), (["vfib"], "The Most Dangerous Heart Rhythm")],
      "tags": ["arrhythmia", "heart arrhythmia", "heart skipping beats", "atrial fibrillation", "afib", "tachycardia", "bradycardia", "ventricular fibrillation", "palpitations", "premature beats"]}
P.EPISODES.append(ep)
bridge.QUESTIONS[ep["id"]] = ["So when is it dangerous?", "So what causes it?"]
KEY = "Arrhythmia • Heart skipping beats • Atrial fibrillation"
CH = [("hook", "Why does your heart skip a beat?"), ("what", "Tachycardia, bradycardia & skipped beats"), ("afib", "Atrial fibrillation & ventricular fibrillation"), ("causes", "Causes & warning signs"), ("treat", "Diagnosis, treatment & summary")]
P.INTRO = 3.6
day = dt.date(2026, 11, 10)
REPO = G.REPO
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith(ep["id"])]
shutil.copy(ep["video"], REPO / "arrhythmia.mp4")
shutil.copy(P.SP / "thumbs_ai" / "arrhythmia_thumb.jpg", REPO / "arrhythmia_thumb.jpg")
st = {i: t for i, t, _ in P.scene_times(ep)}
chap = "\n".join(f"{P.stamp(0 if n == 0 else st[i])} {name}" for n, (i, name) in enumerate(CH))
when = dt.datetime.combine(day, dt.time(12, 30), dt.timezone.utc)
q.append({"id": ep["id"], "kind": "video", "file": "arrhythmia.mp4", "thumbnail": "arrhythmia_thumb.jpg", "title": ep["title"],
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
