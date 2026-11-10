"""Add Brain Anatomy - Tue 17 Nov 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_brain.mp4, brain_thumb.jpg, brain_short1.mp4, brain_short2.mp4
SCR = json.load(open(HERE.parent / "brain" / "script.json"))
INTRO = 3.6
dur = {}
for s in SCR:
    with wave.open(str(HERE.parent / "brain" / "audio" / f"{s['id']}.wav")) as w:
        dur[s["id"]] = w.getnframes() / w.getframerate()
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    t += dur[s["id"]]
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "The 1848 mystery"), ("overview", "The 3 main parts"), ("cerebrum", "Cerebrum & the 4 lobes"), ("hemispheres", "Left & right brain"),
      ("cerebellum", "Cerebellum & brainstem"), ("deep", "Deep structures & protection")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "What Does Your Brain Look Like Inside? Brain Anatomy Explained (Lobes, Cerebellum & Brainstem)"
ABOUT = ("Brain anatomy explained simply, starting with a real mystery: in 1848 an iron rod passed through a railroad worker's skull and he survived. "
         "Learn the 3 main parts of the brain (cerebrum, cerebellum, brainstem), the 4 lobes (frontal, parietal, temporal, occipital) and what each one does, "
         "the left and right halves joined by the corpus callosum, the cerebellum and balance, the brainstem that runs breathing and heart rate, the deep structures "
         "(thalamus, hypothalamus, hippocampus, amygdala), and how the skull, the 3 meninges and cerebrospinal fluid protect the brain. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Nervous System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Some illustrations: Servier Medical Art (smart.servier.com), licensed under CC BY 4.0.

#brain #neuroscience #nervoussystem #anatomy #physiology #medicalstudent #nursing"""
KEY = "Brain anatomy • Parts of the brain • Brain lobes explained"
day = dt.date(2026, 11, 17)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("brain")]
shutil.copy(OUT / "final_brain.mp4", REPO / "brain.mp4")
shutil.copy(OUT / "brain_thumb.jpg", REPO / "brain_thumb.jpg")
q.append({"id": "brain", "kind": "video", "file": "brain.mp4", "thumbnail": "brain_thumb.jpg", "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["brain anatomy", "the anatomy unfolded"],
          "playlist": "Nervous System", "publish_at": dt.datetime.combine(day, dt.time(10, 0), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "youtube_id": None})
SH = [("The Man Who Forgot Every Minute", "What does it take to lose every new memory? A seahorse-shaped part deep in the brain, the hippocampus. 🧠"),
      ("The Iron Rod Through His Head", "In 1848 an iron rod went through Phineas Gage's skull and he survived. Which part of the brain was damaged? 🧠")]
for k, (title, cap) in enumerate(SH):
    f = f"brain_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    hh = (6, 30) if k == 0 else (15, 30)
    q.append({"id": f"brain_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["brain anatomy", "shorts"], "playlist": None,
              "publish_at": dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
