"""Add 'How Do We Hear?' - Sun 29 Nov 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_ear.mp4, ear_short1.mp4, ear_short2.mp4 + ear_thumb.jpg (thumbnail added later)
SCR = json.load(open(HERE.parent / "ear" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "ear" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "How does sound become signals?"), ("overview", "Outer, middle & inner ear"), ("outer", "Pinna, ear canal & eardrum"), ("middle", "The three tiny bones"), ("inner", "The cochlea"),
      ("hair", "Hair cells: mystery solved"), ("balance", "Balance & dizziness"), ("care", "Protecting your hearing"), ("recap", "Recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "How Do We Hear? Ear Anatomy, Cochlea, Hair Cells & Balance Explained"
ABOUT = ("How do we hear? Start with a mystery: sound is just moving air, so how does your ear turn it into signals your brain understands, using the smallest bone in your body? "
         "Follow the sound through the outer ear (pinna, ear canal, eardrum), the middle ear (malleus, incus and stapes, and the Eustachian tube), and the inner ear (the snail-shaped cochlea), "
         "see how hair cells turn vibrations into electrical signals for the auditory nerve, why the semicircular canals make you feel dizzy after spinning, and why hair cell damage from loud noise is permanent. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Nervous System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Some illustrations: Servier Medical Art (smart.servier.com), licensed under CC BY 4.0.

#earanatomy #hearing #anatomy #physiology #medicalstudent #nursing"""
KEY = "How hearing works • Ear anatomy • Cochlea and hair cells"
day = dt.date(2026, 11, 29)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("ear")]
shutil.copy(OUT / "final_ear.mp4", REPO / "ear.mp4")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "ear", "kind": "video", "file": "ear.mp4", "thumbnail": "ear_thumb.jpg", "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["ear", "the anatomy unfolded"],
          "playlist": "Nervous System", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("The Smallest Bone", "The smallest bone in your whole body is hidden inside your ear. It is part of a chain of three tiny bones that carry sound. What is it called, and what does it do? 👂"),
      ("Why You Feel Dizzy", "After you spin around, the room keeps spinning even though you have stopped. Part of the answer is hidden in your ears. Which part of the ear makes you feel dizzy? 👂")]
for k, (title, cap) in enumerate(SH):
    f = f"ear_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"ear_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["ear", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
