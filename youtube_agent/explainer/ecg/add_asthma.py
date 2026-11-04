"""Add Asthma - Sat 14 Nov 2026 (full video 3:30 PM): video 6 PM, Shorts 12 PM + 9 PM IST."""
import datetime as dt, json, shutil
import package as P
import growth_apply as G
import bridge

ep = {"id": "asthma", "focus": [0.5, 0.5], "video": P.HERE / "final_asthma.mp4", "dir": P.SP / "asthma",
      "title": "What Happens in an Asthma Attack? Asthma Explained (Symptoms, Triggers & Inhalers)",
      "about": "Asthma explained simply: what happens inside your airways during an asthma attack. Learn why the bronchi and bronchioles become inflamed and extra sensitive, the 3 things that narrow the airway (muscles tightening, swelling, mucus), why asthma causes wheezing and a tight chest, the main symptoms, common triggers, how asthma is diagnosed (spirometry, peak flow), the difference between a reliever and a preventer inhaler, and the emergency warning signs. Educational only: always follow your own doctor's asthma action plan. Perfect for MBBS, nursing, pharmacy and biology students.",
      "short": [(["attack", "wheeze"], "What Happens Inside Your Airways During an Asthma Attack"), (["inhalers"], "Reliever vs Preventer Inhaler: What's the Difference?")],
      "tags": ["asthma", "asthma attack", "asthma symptoms", "asthma triggers", "what is asthma", "asthma inhaler", "reliever vs preventer inhaler", "wheezing", "spirometry", "bronchospasm"]}
P.EPISODES.append(ep)
bridge.QUESTIONS[ep["id"]] = ["So what sets it off?", "So when is it an emergency?"]
KEY = "Asthma • Asthma attack • Asthma symptoms"
CH = [("hook", "What is asthma?"), ("attack", "Inside an asthma attack"), ("symptoms", "Symptoms & triggers"), ("diagnose", "Diagnosis & inhalers"), ("emergency", "Emergency signs & summary")]
P.INTRO = 3.6
day = dt.date(2026, 11, 14)
REPO = G.REPO
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith(ep["id"])]
shutil.copy(ep["video"], REPO / "asthma.mp4")
shutil.copy(P.SP / "thumbs_ai" / "asthma_thumb.jpg", REPO / "asthma_thumb.jpg")
st = {i: t for i, t, _ in P.scene_times(ep)}
chap = "\n".join(f"{P.stamp(0 if n == 0 else st[i])} {name}" for n, (i, name) in enumerate(CH))
when = dt.datetime.combine(day, dt.time(10, 0), dt.timezone.utc)
q.append({"id": ep["id"], "kind": "video", "file": "asthma.mp4", "thumbnail": "asthma_thumb.jpg", "title": ep["title"],
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
