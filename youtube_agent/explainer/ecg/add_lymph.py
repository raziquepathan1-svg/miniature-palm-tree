"""Add 'What Does the Lymphatic System Do?' - Fri 27 Nov 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_lym.mp4, lym_short1.mp4, lym_short2.mp4 + lymph_thumb.jpg (thumbnail added later)
SCR = json.load(open(HERE.parent / "lymph" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "lymph" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "Where does the leaked fluid go?"), ("overview", "The lymphatic system & lymph"), ("drain", "Mystery solved: draining the tissues"), ("vessels", "Lymph vessels & valves"), ("nodes", "Lymph nodes"),
      ("organs", "Spleen, thymus & tonsils"), ("lacteals", "Lacteals & fat absorption"), ("edema", "Lymphedema"), ("recap", "Recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "What Does the Lymphatic System Do? Lymph, Lymph Nodes & Drainage Explained"
ABOUT = ("What does the lymphatic system do? Start with a mystery: fluid slips out of your tiniest blood vessels all day long, so where does it go? "
         "Learn what lymph is (interstitial fluid), how lymphatic capillaries and vessels return it to the blood through the subclavian veins, why valves keep lymph moving one way, "
         "lymph nodes (about 600) that filter lymph and house lymphocytes, the spleen, thymus and tonsils, lacteals that help absorb dietary fats, and lymphedema. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Nervous System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Some illustrations: Servier Medical Art (smart.servier.com), licensed under CC BY 4.0.

#lymphaticsystem #lymphnodes #anatomy #physiology #medicalstudent #nursing"""
KEY = "Lymphatic system explained • Lymph nodes • How lymph drains"
day = dt.date(2026, 11, 27)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("lymph")]
shutil.copy(OUT / "final_lym.mp4", REPO / "lymph.mp4")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "lymph", "kind": "video", "file": "lymph.mp4", "thumbnail": "lymph_thumb.jpg", "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["lymphatic system", "the anatomy unfolded"],
          "playlist": "Nervous System", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("Your Second Drainage System", "All day long, fluid leaks out of your smallest blood vessels into your tissues. If it never drained away, you would swell up. So where does it go? Your body has a second drainage network. What is it? 💧"),
      ("Lumps In Your Neck", "When you are sick, you can sometimes feel small lumps swelling in your neck. Those lumps are filters, part of a network that runs through your whole body. What are they called? 🔍")]
for k, (title, cap) in enumerate(SH):
    f = f"lym_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"lymph_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["lymphatic system", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
