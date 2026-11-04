"""Add How Breathing Works - Fri 13 Nov 2026 (full video 3:30 PM): video 6 PM, Shorts 12 PM + 9 PM IST."""
import datetime as dt, json, shutil
import package as P
import growth_apply as G
import bridge

ep = {"id": "how_breathing_works", "focus": [0.5, 0.5], "video": P.HERE / "final_how_breathing_works.mp4", "dir": P.SP / "breath",
      "title": "How Do Your Lungs Breathe? How Breathing Works (Diaphragm & Pressure Explained)",
      "about": "How breathing works, explained simply. Your lungs have no muscles of their own, so how do you breathe? Learn how the diaphragm contracts and flattens and the external intercostal muscles lift the ribs to make the chest bigger, why lower pressure inside the lungs makes air rush in (Boyle's law), why breathing out at rest is passive, which muscles force air out when you exercise or cough, normal breathing rate and tidal volume, how the brainstem controls breathing using carbon dioxide, and how hemoglobin carries oxygen. Perfect for MBBS, nursing, pharmacy and biology students.",
      "short": [(["hook", "diaphragm", "inhale"], "Your Lungs Can't Breathe on Their Own"), (["control", "oxygen"], "What Actually Makes You Breathe? (It's Not Oxygen)")],
      "tags": ["how breathing works", "mechanism of breathing", "diaphragm", "inhalation and exhalation", "respiratory physiology", "intercostal muscles", "boyles law breathing", "control of breathing", "respiratory rate", "tidal volume"]}
P.EPISODES.append(ep)
bridge.QUESTIONS[ep["id"]] = ["So why does air rush in?", "So where does the oxygen go?"]
KEY = "How breathing works • Diaphragm breathing • Inhalation and exhalation"
CH = [("hook", "Lungs have no muscles"), ("inhale", "Breathing in & the pressure rule"), ("exhale", "Breathing out: passive vs forced"), ("numbers", "Breathing rate & what controls it"), ("oxygen", "Oxygen transport & summary")]
P.INTRO = 3.6
day = dt.date(2026, 11, 13)
REPO = G.REPO
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith(ep["id"])]
shutil.copy(ep["video"], REPO / "how_breathing_works.mp4")
shutil.copy(P.SP / "thumbs_ai" / "how_breathing_works_thumb.jpg", REPO / "how_breathing_works_thumb.jpg")
st = {i: t for i, t, _ in P.scene_times(ep)}
chap = "\n".join(f"{P.stamp(0 if n == 0 else st[i])} {name}" for n, (i, name) in enumerate(CH))
when = dt.datetime.combine(day, dt.time(10, 0), dt.timezone.utc)
q.append({"id": ep["id"], "kind": "video", "file": "how_breathing_works.mp4", "thumbnail": "how_breathing_works_thumb.jpg", "title": ep["title"],
          "description": f"{KEY}\n\n{ep['about']}\n\nCHAPTERS\n{chap}\n{P.FOOTER.replace('Cardiovascular System series', 'Respiratory System series')}", "tags": ep["tags"] + ["the anatomy unfolded"],
          "playlist": "Respiratory System", "publish_at": when.strftime("%Y-%m-%dT%H:%M:%SZ"), "youtube_id": None})
for k, hh in ((0, (6, 30)), (1, (15, 30))):
    sh = P.OUT / f"{ep['id']}_short{k + 1}.mp4"
    t = P.short(ep, sh, k)
    bridge.add_bridge(sh, ep["id"], k)
    shutil.copy(sh, REPO / sh.name)
    s_ = dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc)
    q.append({"id": f"{ep['id']}_short{k + 1}", "kind": "short", "file": sh.name, "thumbnail": None, "title": f"{t} #Shorts",
              "description": f"{ep['about']}\n\nFull video: \"{ep['title']}\" on The Anatomy Unfolded.\n{P.FOOTER.replace('Cardiovascular System series', 'Respiratory System series')} #shorts",
              "tags": ep["tags"] + ["shorts"], "playlist": None, "publish_at": s_.strftime("%Y-%m-%dT%H:%M:%SZ"), "youtube_id": None})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
