"""Add 'What Does Your Spinal Cord Do?' - Thu 19 Nov 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_spine.mp4, spinal_cord_thumb.jpg, spine_short1.mp4, spine_short2.mp4
SCR = json.load(open(HERE.parent / "spine" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "spine" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "The knee-tap mystery"), ("overview", "What the spinal cord is"), ("protect", "Bone, membranes & fluid"), ("regions", "The 4 regions & 31 pairs"),
      ("horsetail", "The surprise: cauda equina"), ("cross", "Gray & white matter"), ("roots", "Dorsal & ventral roots"), ("tracts", "Ascending & descending tracts"),
      ("payoff", "The reflex payoff"), ("injury", "Spinal cord injury"), ("recap", "Recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "What Does Your Spinal Cord Do? Spinal Cord Anatomy & Reflexes Explained"
ABOUT = ("What does your spinal cord do? Start with the knee-tap mystery: who gave the order? Follow the signal through the spinal cord: about 45 cm long, protected by the vertebral column, "
         "three meninges and cerebrospinal fluid, 31 pairs of spinal nerves in cervical, thoracic, lumbar and sacral regions, the cord ending at L1-L2 with the cauda equina, "
         "gray matter and white matter, dorsal (sensory) and ventral (motor) roots, ascending and descending tracts, the reflex arc that skips the brain, and why a higher spinal cord injury affects more of the body. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Nervous System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Some illustrations: Servier Medical Art (smart.servier.com), licensed under CC BY 4.0.

#spinalcord #nervoussystem #anatomy #physiology #medicalstudent #nursing"""
KEY = "Spinal cord anatomy • Spinal reflex explained • Cauda equina"
day = dt.date(2026, 11, 19)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("spine")]
shutil.copy(OUT / "final_spine.mp4", REPO / "spine.mp4")
shutil.copy(OUT / "spinal_cord_thumb.jpg", REPO / "spine_thumb.jpg")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "spine", "kind": "video", "file": "spine.mp4", "thumbnail": "spine_thumb.jpg", "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["spinal cord anatomy", "the anatomy unfolded"],
          "playlist": "Nervous System", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("The Knee Tap Mystery", "A doctor taps your knee and your leg kicks before you decide anything. Who gave the order? 🔨🦵"),
      ("The Needle in Your Back", "A needle goes into the lower back, right where the spinal cord should be. Why is it safe? 💉🧠")]
for k, (title, cap) in enumerate(SH):
    f = f"spine_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"spine_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["spinal cord anatomy", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
