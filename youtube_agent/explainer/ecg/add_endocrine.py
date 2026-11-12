"""Add 'What Does the Endocrine System Do?' - Sat 21 Nov 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_endo.mp4, endo_short1.mp4, endo_short2.mp4 (thumbnail added later)
SCR = json.load(open(HERE.parent / "endocrine" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "endocrine" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "The pea-sized gland mystery"), ("overview", "Glands & hormones"), ("speed", "Nerves vs hormones"), ("map", "The main glands"), ("pituitary", "The pituitary"),
      ("thyroid", "The thyroid"), ("adrenal", "Adrenal glands: cortisol & adrenaline"), ("pancreas", "Pancreas: insulin & glucagon"), ("feedback", "Feedback loops"),
      ("payoff", "The real boss: hypothalamus"), ("recap", "Recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "What Does the Endocrine System Do? Hormones & Glands Explained (Pituitary, Thyroid, Adrenal, Pancreas)"
ABOUT = ("What does the endocrine system do? Start with a gland the size of a pea under your brain that sends orders to other glands. Learn what hormones are, why nerves are fast but hormones last longer, "
         "the main glands (hypothalamus, pituitary, thyroid, adrenal glands, pancreas, ovaries and testes), cortisol and adrenaline, insulin and glucagon, feedback loops like a thermostat, "
         "and why the hypothalamus is the real boss that links the nervous system to the endocrine system. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Nervous System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Some illustrations: Servier Medical Art (smart.servier.com), licensed under CC BY 4.0.

#endocrinesystem #hormones #anatomy #physiology #medicalstudent #nursing"""
KEY = "Endocrine system explained • Hormones and glands • Pituitary, thyroid, adrenal, pancreas"
day = dt.date(2026, 11, 21)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("endocrine")]
shutil.copy(OUT / "final_endo.mp4", REPO / "endocrine.mp4")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "endocrine", "kind": "video", "file": "endocrine.mp4", "thumbnail": None, "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["endocrine system", "the anatomy unfolded"],
          "playlist": "Nervous System", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("The Boss of the Pea", "A gland the size of a pea under your brain tells your other glands what to do and helps control how tall you grow. So it must be the boss... right? Not quite. 🫛🧠"),
      ("Why Are My Hands Still Shaking", "A car nearly hits you. You jump back and you are safe. But minutes later, your hands are still shaking. The nerves are done. So what is still shaking you? 🚗🤲")]
for k, (title, cap) in enumerate(SH):
    f = f"endo_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"endocrine_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["endocrine system", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
