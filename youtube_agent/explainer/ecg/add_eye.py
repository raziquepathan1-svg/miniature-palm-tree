"""Add 'How Does the Eye See?' - Sat 28 Nov 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_eye.mp4, eye_short1.mp4, eye_short2.mp4 + eye_thumb.jpg (thumbnail added later)
SCR = json.load(open(HERE.parent / "eye" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "eye" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "Why the retina image is upside down"), ("overview", "The eye like a camera"), ("iris", "Iris & pupil"), ("lens", "Cornea, lens & the inverted image"), ("retina", "Rods, cones & the fovea"),
      ("nerve", "The optic nerve"), ("mystery", "The upside-down mystery"), ("blindspot", "The blind spot"), ("recap", "Recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "How Does the Eye See? Eye Anatomy, Retina, Rods & Cones, Blind Spot Explained"
ABOUT = ("How does the eye see? Start with a mystery: the image that lands on the back of your eye is upside down, yet you see the world the right way up. "
         "Follow the light through the cornea, pupil, iris and lens to the retina, learn why the retinal image is inverted, what rods and cones do (dim light and color, with three cone types for red, green and blue), "
         "the fovea and sharp central vision, how the optic nerve carries signals to the brain, what scientists know about how the brain makes the world look upright, and why you have a blind spot you never notice. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Nervous System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Some illustrations: Servier Medical Art (smart.servier.com), licensed under CC BY 4.0.

#eyeanatomy #vision #anatomy #physiology #medicalstudent #nursing"""
KEY = "How the eye works • Retina, rods and cones • The blind spot"
day = dt.date(2026, 11, 28)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("eye")]
shutil.copy(OUT / "final_eye.mp4", REPO / "eye.mp4")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "eye", "kind": "video", "file": "eye.mp4", "thumbnail": "eye_thumb.jpg", "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["eye", "the anatomy unfolded"],
          "playlist": "Nervous System", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("Your Eye Sees Upside Down", "The image on the back of your eye is upside down. Yet you see the world the right way up. So what does your brain do with that image? 👁️"),
      ("Your Eye Has A Blind Spot", "In each of your eyes there is a spot where you cannot see. You have never noticed it, because your brain hides it from you. What is that spot, and how does your brain hide it? 👁️")]
for k, (title, cap) in enumerate(SH):
    f = f"eye_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"eye_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["eye", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
