"""Add Lung Anatomy - Thu 12 Nov 2026 (full video 3:30 PM): video 6 PM, Shorts 12 PM + 9 PM IST."""
import datetime as dt, json, shutil
import package as P
import growth_apply as G
import bridge

ep = {"id": "lung_anatomy", "focus": [0.5, 0.5], "video": P.HERE / "final_lung_anatomy.mp4", "dir": P.SP / "lungs",
      "title": "What Do Your Lungs Look Like Inside? Lung Anatomy Explained (Trachea to Alveoli)",
      "about": "Lung anatomy explained simply: follow the air from the nose through the pharynx, larynx and epiglottis, down the trachea with its C-shaped cartilage rings, into the right and left main bronchi (and why inhaled objects usually go to the right lung), the 3 lobes of the right lung and 2 lobes of the left lung with the cardiac notch, the bronchial tree and bronchioles, the alveoli where gas exchange happens, the pleura and the diaphragm. Perfect for MBBS, nursing, pharmacy and biology students.",
      "short": [(["bronchi"], "Why Inhaled Objects Go to Your Right Lung"), (["alveoli", "exchange"], "Your Lungs Have Hundreds of Millions of Air Sacs")],
      "tags": ["lung anatomy", "respiratory system", "alveoli", "trachea", "bronchi", "bronchioles", "lobes of the lung", "cardiac notch", "pleura", "diaphragm"]}
P.EPISODES.append(ep)
bridge.QUESTIONS[ep["id"]] = ["So where does the air finally go?", "So how does air get in?"]
KEY = "Lung anatomy • Respiratory system • Alveoli"
CH = [("hook", "The path of air"), ("trachea", "Trachea & bronchi"), ("lobes", "Lobes & the bronchial tree"), ("alveoli", "Alveoli & gas exchange"), ("pleura", "Pleura, diaphragm & summary")]
P.INTRO = 3.6
day = dt.date(2026, 11, 12)
REPO = G.REPO
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith(ep["id"])]
shutil.copy(ep["video"], REPO / "lung_anatomy.mp4")
G.dark_thumb("poumons_01", ("YOUR AIR", "TREE"), (90, 170, 255), REPO / "lung_anatomy_thumb.jpg")
st = {i: t for i, t, _ in P.scene_times(ep)}
chap = "\n".join(f"{P.stamp(0 if n == 0 else st[i])} {name}" for n, (i, name) in enumerate(CH))
when = dt.datetime.combine(day, dt.time(10, 0), dt.timezone.utc)
q.append({"id": ep["id"], "kind": "video", "file": "lung_anatomy.mp4", "thumbnail": "lung_anatomy_thumb.jpg", "title": ep["title"],
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
