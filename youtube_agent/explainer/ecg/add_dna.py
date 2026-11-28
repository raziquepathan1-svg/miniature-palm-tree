"""Add 'How Does DNA Make Proteins?' (Foundation F2) - Thu 3 Dec 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_dna.mp4, dna_short1.mp4, dna_short2.mp4 + dna_thumb.jpg
SCR = json.load(open(HERE.parent / "dna" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "dna" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "2 meters of DNA in one cell"), ("pack", "Chromosomes & histones"), ("helix", "Double helix, base pairs & genes"), ("transcribe", "Transcription: DNA to mRNA"),
      ("translate", "Translation at the ribosome"), ("fold", "Protein folding + recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "How Does DNA Make Proteins? Transcription & Translation Explained"
ABOUT = ("How does DNA make proteins? The DNA in just one of your cells would stretch about 2 meters, yet it fits inside a tiny nucleus. "
         "See how DNA is packed into 46 chromosomes around histone spools, how the double helix pairs its bases (A with T, G with C), what a gene is, "
         "how RNA polymerase copies a gene into messenger RNA (transcription), how the mRNA leaves through a nuclear pore, how the ribosome reads codons "
         "while transfer RNA brings amino acids (translation), and how the chain folds into a working protein. Every part is named and pointed out on the diagram. "
         "Foundation course, video 2. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Foundation course (F2) on The Anatomy Unfolded: cell → tissue → organ → system.
Next: how cells make energy (mitochondria and ATP).

⚠️ Educational content only, not medical advice.
Sources: NIH (NIGMS, NHGRI), OpenStax Biology, Britannica.

#dna #proteinsynthesis #anatomy #physiology #medicalstudent #nursing"""
KEY = "How DNA makes proteins • Transcription and translation • Protein synthesis explained"
day = dt.date(2026, 12, 3)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("dna")]
shutil.copy(OUT / "final_dna.mp4", REPO / "dna.mp4")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "dna", "kind": "video", "file": "dna.mp4", "thumbnail": "dna_thumb.jpg", "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["dna", "the anatomy unfolded"],
          "playlist": "Foundation: Cells & Tissues", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("Two Meters Of DNA In Every Cell", "If you stretched out the DNA from just one of your cells, it would be about two meters long. Yet it fits inside a nucleus far too small to see. How does it fit? 🧬"),
      ("How The Recipe Leaves The Nucleus", "Your DNA stays inside the nucleus, but your proteins are built outside it. So how does the recipe get out? 🧬")]
for k, (title, cap) in enumerate(SH):
    f = f"dna_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"dna_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["dna", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
