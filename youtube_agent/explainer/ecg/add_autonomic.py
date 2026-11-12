"""Add 'Who Runs Your Heart Without Asking?' - Fri 20 Nov 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_auto.mp4, auto_short1.mp4, auto_short2.mp4 (thumbnail added later)
SCR = json.load(open(HERE.parent / "autonomic" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "autonomic" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "The sleeping heart mystery"), ("overview", "What 'autonomic' means"), ("two", "Sympathetic vs parasympathetic"), ("sympathetic", "Fight or flight"),
      ("parasympathetic", "Rest and digest"), ("balance", "Gas pedal and brake"), ("vagus", "The vagus nerve surprise"), ("chain", "Ganglia & neurotransmitters"),
      ("payoff", "The payoff"), ("faint", "Why people faint"), ("recap", "Recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "Who Runs Your Heart Without Asking? Autonomic Nervous System Explained (Sympathetic vs Parasympathetic)"
ABOUT = ("Who runs your heart while you sleep? Meet the autonomic nervous system: the automatic control of your heart, glands, blood vessels, gut and airways. "
         "Learn the sympathetic division (fight or flight) and the parasympathetic division (rest and digest), the gas pedal and brake idea, the vagus nerve that slows the heart's own pacemaker (about 100 beats a minute) to your resting rate, "
         "the two-neuron chain with a ganglion, acetylcholine and norepinephrine, and why standing up too fast can make some people faint. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Nervous System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Some illustrations: Servier Medical Art (smart.servier.com), licensed under CC BY 4.0.

#autonomicnervoussystem #nervoussystem #anatomy #physiology #medicalstudent #nursing"""
KEY = "Autonomic nervous system • Sympathetic vs parasympathetic • Vagus nerve"
day = dt.date(2026, 11, 20)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("autonomic")]
shutil.copy(OUT / "final_auto.mp4", REPO / "autonomic.mp4")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "autonomic", "kind": "video", "file": "autonomic.mp4", "thumbnail": None, "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["autonomic nervous system", "the anatomy unfolded"],
          "playlist": "Nervous System", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("The Hidden Brake", "You are asleep and your heart is beating. Its own pacemaker wants to beat about 100 times a minute, but yours is slower. What is holding it back? 💤❤️"),
      ("The Bang", "A loud bang. Your heart pounds and your pupils widen before you decide anything. A hidden system with two teams just took over. Which one won? 💥👁️")]
for k, (title, cap) in enumerate(SH):
    f = f"auto_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"autonomic_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["autonomic nervous system", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
