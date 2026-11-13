"""Add 'How Do Your Kidneys Work?' - Mon 23 Nov 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_kid.mp4, kid_short1.mp4, kid_short2.mp4 + kidney_thumb.jpg (thumbnail added later)
SCR = json.load(open(HERE.parent / "kidney" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "kidney" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "Where does 180 liters go?"), ("overview", "Where the kidneys are"), ("blood", "Blood supply"), ("nephron", "Nephrons"), ("filter", "Filtration in the glomerulus"),
      ("reabsorb", "Reabsorption: the mystery solved"), ("balance", "Water and salt balance"), ("urine", "Ureters, bladder, urethra"), ("jobs", "Renin, EPO & vitamin D"), ("recap", "Recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "How Do Your Kidneys Work? Kidney Anatomy, Nephron & Urine Formation Explained"
ABOUT = ("How do your kidneys work? Start with a mystery: your kidneys filter about 150 to 180 liters of fluid a day, yet you pass only about one to two liters of urine. Where does the rest go? "
         "Learn where the kidneys are, their blood supply (renal artery and vein), the nephron, filtration in the glomerulus, reabsorption in the tubule (about 99 percent of the filtrate), "
         "water and salt balance, the ureters, bladder and urethra, and the kidney hormones renin, erythropoietin and active vitamin D. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Nervous System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Some illustrations: Servier Medical Art (smart.servier.com), licensed under CC BY 4.0.

#kidneys #urinarysystem #anatomy #physiology #medicalstudent #nursing"""
KEY = "How kidneys work • Nephron and urine formation • Kidney anatomy"
day = dt.date(2026, 11, 23)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("kidney")]
shutil.copy(OUT / "final_kid.mp4", REPO / "kidney.mp4")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "kidney", "kind": "video", "file": "kidney.mp4", "thumbnail": "kidney_thumb.jpg", "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["kidney", "the anatomy unfolded"],
          "playlist": "Nervous System", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("Where Does 180 Liters Go", "Your kidneys filter about 150 to 180 liters of fluid from your blood every day, but you pass only about one to two liters of urine. So where does the rest go? 💧"),
      ("The Fist Sized Filter", "Each kidney is about the size of a fist, yet at rest they receive about a quarter of the blood your heart pumps. And they send a message to your bone marrow. What is it? 🩸")]
for k, (title, cap) in enumerate(SH):
    f = f"kid_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"kidney_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["kidney", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
