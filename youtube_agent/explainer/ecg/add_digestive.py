"""Add 'How Does Digestion Work?' - Sun 22 Nov 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_dig.mp4, dig_short1.mp4, dig_short2.mp4 (thumbnail added later)
SCR = json.load(open(HERE.parent / "digestive" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "digestive" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "Why the stomach never digests itself"), ("overview", "The digestive tube & helper organs"), ("mouth", "Mouth: teeth & saliva"), ("swallow", "Swallowing & peristalsis"),
      ("stomach", "The stomach: acid & pepsin"), ("protect", "The mystery solved: mucus"), ("small", "Small intestine: bile & enzymes"), ("absorb", "Villi & absorption"),
      ("large", "Large intestine"), ("journey", "The full journey"), ("recap", "Recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "How Does Digestion Work? The Digestive System Explained (Stomach, Small Intestine & More)"
ABOUT = ("How does digestion work? Start with a mystery: stomach acid can digest meat, so why doesn't it digest the stomach itself? Follow a single bite through the mouth (teeth, saliva and amylase), "
         "the esophagus (peristalsis), the stomach (hydrochloric acid, pepsin, chyme), the mucus and bicarbonate that protect the stomach lining, the small intestine (bile from the liver and gallbladder, "
         "pancreatic enzymes, villi and absorption) and the large intestine (water absorption and gut bacteria). Food usually takes about one to three days to pass through. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Nervous System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Some illustrations: Servier Medical Art (smart.servier.com), licensed under CC BY 4.0.

#digestivesystem #digestion #anatomy #physiology #medicalstudent #nursing"""
KEY = "Digestive system explained • How digestion works • Stomach and small intestine"
day = dt.date(2026, 11, 22)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("digestive")]
shutil.copy(OUT / "final_dig.mp4", REPO / "digestive.mp4")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "digestive", "kind": "video", "file": "digestive.mp4", "thumbnail": None, "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["digestive system", "the anatomy unfolded"],
          "playlist": "Nervous System", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("Why It Never Digests Itself", "Stomach acid can digest meat, and your stomach wall is protein too. Yet it never digests itself, and the lining is replaced every few days. What protects it? 🔥🍖"),
      ("The Six Meter Tube", "Stretched out, your small intestine is about six to seven meters long, longer than a car. And it fits inside your belly. But length is not the secret. Its wall is covered with tiny fingers. What do they do? 🧬")]
for k, (title, cap) in enumerate(SH):
    f = f"dig_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"digestive_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["digestive system", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
