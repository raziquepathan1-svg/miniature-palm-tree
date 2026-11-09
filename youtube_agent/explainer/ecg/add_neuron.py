"""Add 'How Do Brain Cells Talk?' - Wed 18 Nov 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_neuron.mp4, neurons_thumb.jpg, neuron_short1.mp4, neuron_short2.mp4
SCR = json.load(open(HERE.parent / "neuron" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "neuron" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "The hot pan mystery"), ("structure", "Neuron structure & myelin"), ("resting", "Resting state, spike & travel"),
      ("synapse", "The synapse & neurotransmitters"), ("payoff", "The reflex payoff & recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "How Do Brain Cells Talk? Neurons & Nerve Signals Explained (Action Potential & Synapse)"
ABOUT = ("How do brain cells talk? Start with a hot pan: your hand jumps back before you feel pain. Follow the message through a neuron: dendrites, cell body and axon, "
         "the myelin sheath that makes signals faster (up to about 120 meters per second), the resting state and the action potential (sodium in, potassium out), the all-or-nothing spike, "
         "the synapse and neurotransmitters such as dopamine, serotonin and acetylcholine, receptors like a key in a lock, and the spinal cord reflex that explains the hot pan. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Nervous System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Some illustrations: Servier Medical Art (smart.servier.com), licensed under CC BY 4.0.

#neurons #neuroscience #nervoussystem #anatomy #physiology #medicalstudent #nursing"""
KEY = "How neurons work • Action potential explained • Synapse and neurotransmitters"
day = dt.date(2026, 11, 18)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("neuron")]
shutil.copy(OUT / "final_neuron.mp4", REPO / "neuron.mp4")
shutil.copy(OUT / "neurons_thumb.jpg", REPO / "neuron_thumb.jpg")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "neuron", "kind": "video", "file": "neuron.mp4", "thumbnail": "neuron_thumb.jpg", "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["how neurons work", "the anatomy unfolded"],
          "playlist": "Nervous System", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("The Hot Pan Mystery", "You touch a hot pan and your hand jumps back before you feel any pain. How is that even possible? 🔥✋"),
      ("The Poison That Stops Every Muscle", "A poison that stops every muscle, yet never touches the brain or the muscles. What does it block? 🏹🧠")]
for k, (title, cap) in enumerate(SH):
    f = f"neuron_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"neuron_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["how neurons work", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
