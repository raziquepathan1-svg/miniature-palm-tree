"""Add High Blood Pressure (hypertension) - Sat 8 Nov 2026: video 6 PM, Shorts 12 PM + 9 PM IST."""
import datetime as dt, json, shutil
import package as P
import growth_apply as G
import bridge

ep = {"id": "high_blood_pressure", "focus": [0.5, 0.5], "video": P.HERE / "final_high_blood_pressure.mp4", "dir": P.SP / "htn",
      "title": "Why Is High Blood Pressure Called the Silent Killer? Hypertension Explained",
      "about": "High blood pressure (hypertension) explained simply: what counts as high (130/80 or higher for adults), why it happens (primary vs secondary hypertension), and how constant high pressure quietly damages your arteries and makes the left ventricle thicken. You'll see why it's called the silent killer, the organs it harms (heart attack, stroke, heart failure, kidney damage and the eyes), the emergency warning signs above 180/120, and the lifestyle changes and medicines that keep it under control. Perfect for MBBS, nursing, pharmacy and biology students.",
      "short": [(["silent", "damage"], "Why High Blood Pressure Is the Silent Killer"), (["crisis", "control"], "When Is High Blood Pressure an Emergency?")],
      "tags": ["high blood pressure", "hypertension explained", "silent killer", "what is hypertension", "high blood pressure symptoms",
               "primary and secondary hypertension", "left ventricular hypertrophy", "hypertensive crisis", "how to lower blood pressure",
               "blood pressure 130/80", "cardiovascular physiology", "hypertension pathophysiology"]}
P.EPISODES.append(ep)
bridge.QUESTIONS[ep["id"]] = ["So how do you stop it?", "And what can lower it?"]
KEY = "High blood pressure • Hypertension explained • Silent killer"
CH = [("hook", "Why is it called the silent killer?"), ("define", "What counts as high & why it happens"), ("arteries", "What it does to arteries & the heart"),
      ("damage", "Organ damage & emergency signs"), ("control", "How to control it & summary")]
P.INTRO = 3.6
day = dt.date(2026, 11, 8)
REPO = G.REPO
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith(ep["id"])]
shutil.copy(ep["video"], REPO / "high_blood_pressure.mp4")
G.dark_thumb("coeur_10", ("SILENT", "KILLER"), (255, 30, 39), REPO / "high_blood_pressure_thumb.jpg")
st = {i: t for i, t, _ in P.scene_times(ep)}
chap = "\n".join(f"{P.stamp(0 if n == 0 else st[i])} {name}" for n, (i, name) in enumerate(CH))
when = dt.datetime.combine(day, dt.time(12, 30), dt.timezone.utc)
q.append({"id": ep["id"], "kind": "video", "file": "high_blood_pressure.mp4", "thumbnail": "high_blood_pressure_thumb.jpg", "title": ep["title"],
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
