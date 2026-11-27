"""Add 'What Is a Cell?' (Foundation F1) - Wed 2 Dec 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_cell.mp4, cell_short1.mp4, cell_short2.mp4 + cell_thumb.jpg
SCR = json.load(open(HERE.parent / "cell" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "cell" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "How many cells make you?"), ("tissue", "From cells to tissue"), ("membrane", "The cell membrane"), ("nucleus", "The nucleus & DNA"),
      ("mito", "Mitochondria: the power plants"), ("factory", "Ribosomes, ER, Golgi, lysosomes + recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "What Is a Cell? Parts of a Cell & Their Functions Explained"
ABOUT = ("What is a cell, and what is inside it? Your body is built from about 30 trillion cells. Zoom from the whole body into the cells lining your cheek, "
         "see how cells join to form tissues, then open one cell and meet its organelles one by one: the cell membrane (phospholipids and protein channels), "
         "the nucleus with its DNA, pores and nucleolus, the mitochondria that make ATP energy, the ribosomes and rough endoplasmic reticulum that build proteins, "
         "the Golgi apparatus that packs and ships them, and the lysosomes that clean up. Every part is named and pointed out on the diagram. "
         "Foundation course, video 1: cells, tissues, organs, systems. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Foundation course (F1) on The Anatomy Unfolded: cell -> tissue -> organ -> system.
Next: inside the nucleus - how DNA makes proteins.

⚠️ Educational content only, not medical advice.
Sources: NIH (NIGMS), OpenStax Biology / Anatomy & Physiology, Britannica.

#cellbiology #partsofacell #anatomy #physiology #medicalstudent #nursing"""
KEY = "What is a cell • Parts of a cell and their functions • Cell organelles explained"
day = dt.date(2026, 12, 2)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("cell")]
shutil.copy(OUT / "final_cell.mp4", REPO / "cell.mp4")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "cell", "kind": "video", "file": "cell.mp4", "thumbnail": "cell_thumb.jpg", "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["cell", "the anatomy unfolded"],
          "playlist": "Foundation: Cells & Tissues", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("What Is Your Cell's Control Center", "Your body is built from about 30 trillion cells, and almost every one has a control center that holds your DNA and tells the cell what to do. What is it called? 🧬"),
      ("Your Cells Have Power Plants", "Every second your cells need energy. Inside them are tiny power plants that even carry a little DNA of their own. What are they called? ⚡")]
for k, (title, cap) in enumerate(SH):
    f = f"cell_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"cell_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["cell", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
