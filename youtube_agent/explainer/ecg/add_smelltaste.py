"""Add 'How Do Smell and Taste Work?' - Mon 30 Nov 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_smelltaste.mp4, smelltaste_short1.mp4, smelltaste_short2.mp4 + smelltaste_thumb.jpg
SCR = json.load(open(HERE.parent / "smelltaste" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "smelltaste" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "Why does food lose its flavor?"), ("nose", "How smell works"), ("brain", "Smell, emotion & memory"), ("tongue", "Taste buds & the 5 basic tastes"),
      ("flavor", "Flavor = taste + smell"), ("care", "When to see a doctor + recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "How Do Smell and Taste Work? Taste Buds, Olfaction & Flavor Explained"
ABOUT = ("How do smell and taste work? Pinch your nose and eat a strawberry: it still tastes sweet, but the flavor almost disappears. "
         "Follow smell molecules to the olfactory epithelium and its sensory neurons, through the skull to the olfactory bulb and on to emotion and memory areas, "
         "then see how papillae and taste buds sense the five basic tastes (sweet, salty, sour, bitter and umami), why the tongue map is a myth, "
         "which three cranial nerves carry taste, how taste and smell cells are replaced, and why food tastes bland when your nose is blocked. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Nervous System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Sources: NIDCD (NIH), Cleveland Clinic, OpenStax Anatomy & Physiology, Britannica, StatPearls.

#smellandtaste #tastebuds #anatomy #physiology #medicalstudent #nursing"""
KEY = "How smell and taste work • Taste buds and the 5 basic tastes • Why food tastes bland with a blocked nose"
day = dt.date(2026, 11, 30)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("smelltaste")]
shutil.copy(OUT / "final_smelltaste.mp4", REPO / "smelltaste.mp4")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "smelltaste", "kind": "video", "file": "smelltaste.mp4", "thumbnail": "smelltaste_thumb.jpg", "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["smell and taste", "the anatomy unfolded"],
          "playlist": "Nervous System", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("Is The Tongue Map Real", "Some old textbooks show a tongue map, with sweet at the tip and bitter at the back. But it is a myth: taste buds all over your tongue sense every basic taste. So how many basic tastes are there? 👅"),
      ("Why Food Tastes Bland", "With a stuffy nose, your favorite food suddenly tastes bland, yet your taste buds still work fine. So what is really missing when food loses its flavor? 👃")]
for k, (title, cap) in enumerate(SH):
    f = f"smelltaste_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"smelltaste_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["smell and taste", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
