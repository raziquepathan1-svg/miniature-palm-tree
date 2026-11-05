"""Add Pneumonia - Sun 15 Nov 2026 (full video 3:30 PM): video 6 PM, Shorts 12 PM + 9 PM IST."""
import datetime as dt, json, shutil
import package as P
import growth_apply as G
import bridge

ep = {"id": "pneumonia", "focus": [0.5, 0.5], "video": P.HERE / "final_pneumonia.mp4", "dir": P.SP / "pneu",
      "title": "What Happens in Pneumonia? How Lung Infection Fills Your Air Sacs (Symptoms & Treatment)",
      "about": "Pneumonia explained simply: an infection that inflames the air sacs (alveoli) and fills them with fluid and pus, so less oxygen reaches your blood. Learn the main causes (bacteria such as Streptococcus pneumoniae, viruses such as flu, RSV and COVID-19, and fungi), what happens inside the lung, the symptoms, who is at higher risk, how it is diagnosed (stethoscope, pulse oximeter, chest x-ray), how it is treated (antibiotics for bacterial pneumonia, rest and fluids for viral pneumonia), how vaccines help prevent it, and the emergency warning signs. Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.",
      "short": [(["inside"], "What Pneumonia Does Inside Your Lungs"), (["symptoms", "risk"], "Pneumonia Warning Signs You Shouldn't Ignore")],
      "tags": ["pneumonia", "pneumonia symptoms", "what is pneumonia", "lung infection", "bacterial pneumonia", "viral pneumonia", "alveoli infection", "chest x-ray pneumonia", "pneumonia treatment", "pneumococcal vaccine"]}
P.EPISODES.append(ep)
bridge.QUESTIONS[ep["id"]] = ["So how do you know you have it?", "So how is it treated?"]
KEY = "Pneumonia • Pneumonia symptoms • Lung infection"
CH = [("hook", "What is pneumonia?"), ("causes", "Causes & what happens inside"), ("symptoms", "Symptoms & who is at risk"), ("diagnose", "Diagnosis & treatment"), ("prevent", "Prevention, warning signs & summary")]
P.INTRO = 3.6
day = dt.date(2026, 11, 15)
REPO = G.REPO
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith(ep["id"])]
shutil.copy(ep["video"], REPO / "pneumonia.mp4")
shutil.copy(P.SP / "thumbs_ai" / "pneumonia_thumb.jpg", REPO / "pneumonia_thumb.jpg")
st = {i: t for i, t, _ in P.scene_times(ep)}
chap = "\n".join(f"{P.stamp(0 if n == 0 else st[i])} {name}" for n, (i, name) in enumerate(CH))
when = dt.datetime.combine(day, dt.time(10, 0), dt.timezone.utc)
q.append({"id": ep["id"], "kind": "video", "file": "pneumonia.mp4", "thumbnail": "pneumonia_thumb.jpg", "title": ep["title"],
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
