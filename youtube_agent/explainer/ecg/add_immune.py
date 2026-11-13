"""Add 'How Does the Immune System Work?' - Tue 24 Nov 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_imm.mp4, imm_short1.mp4, imm_short2.mp4 + immune_thumb.jpg (thumbnail added later)
SCR = json.load(open(HERE.parent / "immune" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "immune" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "The cut finger mystery"), ("overview", "Innate vs adaptive immunity"), ("barrier", "Barriers: skin & mucus"), ("innate", "Neutrophils, macrophages & NK cells"), ("inflammation", "Inflammation: the mystery solved"),
      ("adaptive", "Lymph nodes & the adaptive response"), ("tcells", "Helper & cytotoxic T cells"), ("bcells", "B cells & antibodies"), ("memory", "Memory cells & vaccines"), ("recap", "Recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "How Does the Immune System Work? Innate vs Adaptive Immunity, T Cells, B Cells & Inflammation"
ABOUT = ("How does the immune system work? Start with a cut finger: why does it turn red, warm and swollen? Learn the two lines of defense, innate and adaptive immunity, the skin and mucus barriers, "
         "neutrophils, macrophages and natural killer cells, inflammation (redness, heat, swelling and pain), dendritic cells and lymph nodes, helper and cytotoxic T cells, B cells and antibodies, "
         "and memory cells and vaccines. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Nervous System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Some illustrations: Servier Medical Art (smart.servier.com), licensed under CC BY 4.0.

#immunesystem #immunity #anatomy #physiology #medicalstudent #nursing"""
KEY = "Immune system explained • Innate vs adaptive immunity • T cells and B cells"
day = dt.date(2026, 11, 24)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("immune")]
shutil.copy(OUT / "final_imm.mp4", REPO / "immune.mp4")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "immune", "kind": "video", "file": "immune.mp4", "thumbnail": "immune_thumb.jpg", "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["immune system", "the anatomy unfolded"],
          "playlist": "Nervous System", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("Who Makes Your Finger Red", "You cut your finger. Germs slip in. Within hours it turns red, warm and swollen. Is that the infection itself? Not exactly. Something in your body is causing it on purpose. What? 🩹"),
      ("How Does Your Body Remember", "After some infections and vaccines, your protection may last months, years or even a lifetime. Yet there is no notebook inside you. So how does your body remember? 🧠")]
for k, (title, cap) in enumerate(SH):
    f = f"imm_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"immune_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["immune system", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
