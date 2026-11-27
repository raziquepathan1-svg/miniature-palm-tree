"""Add 'How Does Reproduction Work?' - Tue 1 Dec 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_repro.mp4, repro_short1.mp4, repro_short2.mp4 + repro_thumb.jpg
SCR = json.load(open(HERE.parent / "repro" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "repro" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "How does one cell start a new life?"), ("female", "Female organs"), ("ovulation", "Ovulation: releasing an egg"), ("male", "Male organs & sperm"),
      ("fertilize", "Fertilization & implantation"), ("cycle", "The period, when to see a doctor + recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "How Does Reproduction Work? Ovulation, Fertilization & Implantation"
ABOUT = ("How does reproduction work? Every one of us began as a single cell about a tenth of a millimeter wide. "
         "Follow the journey through the female reproductive system (ovaries, fallopian tubes, uterus and cervix), see how a follicle releases an egg at ovulation, "
         "how the testes make sperm in the seminiferous tubules, why only one sperm normally gets into the egg, how 23 plus 23 chromosomes make a new set of 46, "
         "how the blastocyst implants in the uterine lining, and why the lining sheds as the menstrual period when no egg is fertilized. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Reproductive System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Sources: Cleveland Clinic, Merck Manual, NIH (NIGMS), OpenStax Anatomy & Physiology.

#reproductivesystem #ovulation #anatomy #physiology #medicalstudent #nursing"""
KEY = "How reproduction works • Ovulation and fertilization • Reproductive system anatomy"
day = dt.date(2026, 12, 1)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("repro")]
shutil.copy(OUT / "final_repro.mp4", REPO / "repro.mp4")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "repro", "kind": "video", "file": "repro.mp4", "thumbnail": "repro_thumb.jpg", "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["reproductive system", "the anatomy unfolded"],
          "playlist": "Reproductive System", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("How Many Eggs Are Released", "A baby girl is born with all the eggs she will ever have, around one to two million. Most are never used. So how many eggs are actually released in a whole lifetime? 🥚"),
      ("Only One Sperm Gets In", "Many sperm can reach the egg at the same time, but normally only one gets inside. So what stops all the others from getting in? 🔬")]
for k, (title, cap) in enumerate(SH):
    f = f"repro_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"repro_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["reproductive system", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
