"""Add COPD - Mon 16 Nov 2026 (full video 3:30 PM): video 6 PM, Shorts 12 PM + 9 PM IST."""
import datetime as dt, json, shutil
import package as P
import growth_apply as G
import bridge

ep = {"id": "copd", "focus": [0.5, 0.5], "video": P.HERE / "final_copd.mp4", "dir": P.SP / "copd",
      "title": "What Is COPD? What Smoke Does to Your Lungs (Emphysema & Chronic Bronchitis)",
      "about": "COPD (chronic obstructive pulmonary disease) explained simply: a long-term lung disease that blocks airflow and makes it hard to breathe out. Learn what happens in emphysema (damaged air sacs, trapped air) and chronic bronchitis (inflamed airways, mucus, long-term cough), the main causes (smoking, indoor cooking smoke, air pollution, dust and chemicals at work), the symptoms, how it is diagnosed with spirometry, how quitting smoking, inhalers, pulmonary rehabilitation, vaccines and oxygen help, and the emergency warning signs. Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.",
      "short": [(["emphysema"], "What Smoking Really Does to Your Air Sacs"), (["causes"], "Cooking Smoke Can Damage Your Lungs Too")],
      "tags": ["copd", "what is copd", "emphysema", "chronic bronchitis", "copd symptoms", "smoking and lungs", "chronic obstructive pulmonary disease", "spirometry", "copd treatment", "indoor air pollution"]}
P.EPISODES.append(ep)
bridge.QUESTIONS[ep["id"]] = ["So what else causes COPD?", "So how do you slow it down?"]
KEY = "COPD • Emphysema • Chronic bronchitis"
CH = [("hook", "What is COPD?"), ("emphysema", "Emphysema & chronic bronchitis"), ("causes", "Causes & symptoms"), ("diagnose", "Diagnosis & treatment"), ("emergency", "Warning signs & summary")]
P.INTRO = 3.6
day = dt.date(2026, 11, 16)
REPO = G.REPO
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith(ep["id"])]
shutil.copy(ep["video"], REPO / "copd.mp4")
shutil.copy(P.SP / "thumbs_ai" / "copd_thumb.jpg", REPO / "copd_thumb.jpg")
st = {i: t for i, t, _ in P.scene_times(ep)}
chap = "\n".join(f"{P.stamp(0 if n == 0 else st[i])} {name}" for n, (i, name) in enumerate(CH))
when = dt.datetime.combine(day, dt.time(10, 0), dt.timezone.utc)
q.append({"id": ep["id"], "kind": "video", "file": "copd.mp4", "thumbnail": "copd_thumb.jpg", "title": ep["title"],
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
