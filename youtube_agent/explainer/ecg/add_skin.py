"""Add 'What Does Your Skin Do?' - Wed 25 Nov 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_skin.mp4, skin_short1.mp4, skin_short2.mp4 + skin_thumb.jpg (thumbnail added later)
SCR = json.load(open(HERE.parent / "skin" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "skin" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "Why dead cells protect you"), ("overview", "The 3 layers of skin"), ("epidermis", "The epidermis & keratin"), ("protect", "Mystery solved: the dead-cell barrier"), ("melanin", "Melanin: built-in sunscreen"),
      ("dermis", "The dermis"), ("glands", "Sweat & sebaceous glands"), ("hypo", "The hypodermis"), ("vitd", "Vitamin D"), ("recap", "Recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "What Does Your Skin Do? Skin Layers, Melanin & Anatomy Explained (Epidermis, Dermis, Hypodermis)"
ABOUT = ("What does your skin do? Start with a mystery: the part of your skin you can see and touch is made of dead cells, so how does it protect you? "
         "Learn the three layers of skin (epidermis, dermis and hypodermis), keratinocytes and keratin, why the outer dead layer is a protective barrier that is constantly replaced, "
         "melanocytes and melanin as a built-in sunscreen, collagen and elastin in the dermis, nerve endings, hair follicles, sweat glands and sebaceous glands, fat in the hypodermis, and how skin helps make vitamin D. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Nervous System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Some illustrations: Servier Medical Art (smart.servier.com), licensed under CC BY 4.0.

#skin #skinanatomy #anatomy #physiology #medicalstudent #nursing"""
KEY = "Skin anatomy explained • Layers of the skin • Melanin and keratin"
day = dt.date(2026, 11, 25)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("skin")]
shutil.copy(OUT / "final_skin.mp4", REPO / "skin.mp4")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "skin", "kind": "video", "file": "skin.mp4", "thumbnail": "skin_thumb.jpg", "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["skin", "the anatomy unfolded"],
          "playlist": "Nervous System", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("Dead Cells As A Shield", "The part of your skin that you can see and touch is made of dead cells. Yet it protects your body every day. So how can dead cells be a shield? 🛡️"),
      ("Your Built In Sunscreen", "Your skin has a built-in sunscreen that your own cells make, and sunlight tells them to make more of it. It is a pigment. What is it called? ☀️")]
for k, (title, cap) in enumerate(SH):
    f = f"skin_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"skin_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["skin", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
