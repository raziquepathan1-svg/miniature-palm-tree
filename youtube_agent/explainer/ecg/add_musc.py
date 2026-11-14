"""Add 'How Do Bones and Muscles Work?' - Thu 26 Nov 2026 (full video 3:30 PM): video + 2 story Shorts (12 PM + 9 PM IST)."""
import datetime as dt, json, shutil, sys, wave
from pathlib import Path
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
OUT = Path(sys.argv[1])   # folder with final_musc.mp4, musc_short1.mp4, musc_short2.mp4 + musc_thumb.jpg (thumbnail added later)
SCR = json.load(open(HERE.parent / "musc" / "script.json"))
INTRO = 3.6
start, t = {}, INTRO
for s in SCR:
    start[s["id"]] = t
    with wave.open(str(HERE.parent / "musc" / "audio" / f"{s['id']}.wav")) as w:
        t += w.getnframes() / w.getframerate()
stamp = lambda x: f"{int(x) // 60}:{int(x) % 60:02d}"
CH = [("story", "Where did the extra bones go?"), ("overview", "The musculoskeletal system"), ("protect", "Skull & rib cage"), ("bones", "Bones are living tissue"), ("fusion", "Mystery solved: bones fuse"),
      ("joints", "Joints, ligaments & tendons"), ("types", "3 types of muscle"), ("pull", "Muscles only pull"), ("contraction", "Actin, myosin, calcium & ATP"), ("recap", "Recap")]
chap = "\n".join(f"{stamp(0 if n == 0 else start[i])} {name}" for n, (i, name) in enumerate(CH))
TITLE = "How Do Bones and Muscles Work? Musculoskeletal System Explained (Bones, Joints, Tendons & Muscle Contraction)"
ABOUT = ("How do bones and muscles work? Start with a mystery: a baby is born with roughly 270 to 300 bones, but an adult has only 206. Where did the extra bones go? "
         "Learn what the musculoskeletal system is, how the skeleton protects (skull and rib cage), why bone is living tissue that is constantly remodeled, calcium storage and bone marrow, "
         "how bones fuse as you grow, joints, ligaments (bone to bone) and tendons (muscle to bone), the three types of muscle (skeletal, smooth and cardiac), why muscles can only pull and work in pairs (biceps and triceps), "
         "and the basics of muscle contraction with actin, myosin, calcium and ATP. "
         "Educational only, not medical advice. Perfect for MBBS, nursing, pharmacy and biology students.")
FOOT = """Part of the Nervous System series on The Anatomy Unfolded.

⚠️ Educational content only, not medical advice. Always talk to a qualified doctor about your health.
Some illustrations: Servier Medical Art (smart.servier.com), licensed under CC BY 4.0.

#musculoskeletal #bones #anatomy #physiology #medicalstudent #nursing"""
KEY = "Musculoskeletal system explained • Bones and muscles • How muscles contract"
day = dt.date(2026, 11, 26)
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith("musc")]
shutil.copy(OUT / "final_musc.mp4", REPO / "musc.mp4")
iso = lambda hh: dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
q.append({"id": "musc", "kind": "video", "file": "musc.mp4", "thumbnail": "musc_thumb.jpg", "title": TITLE,
          "description": f"{KEY}\n\n{ABOUT}\n\nCHAPTERS\n{chap}\n\n{FOOT}", "tags": ["musculoskeletal system", "the anatomy unfolded"],
          "playlist": "Nervous System", "publish_at": iso((10, 0)), "youtube_id": None})
SH = [("Where Did The Bones Go", "A baby is born with roughly 270 to 300 bones. But an adult has only 206. Nothing was thrown away. So where did the extra bones go? 🦴"),
      ("Muscles Only Pull", "A muscle can only pull. It can never push. Yet you can bend your arm and straighten it again. So how does a muscle that only pulls straighten your elbow? 💪")]
for k, (title, cap) in enumerate(SH):
    f = f"musc_short{k + 1}.mp4"
    shutil.copy(OUT / f, REPO / f)
    q.append({"id": f"musc_short{k + 1}", "kind": "short", "file": f, "thumbnail": None, "title": f"{title} #Shorts",
              "description": f"{ABOUT}\n\nFull video: \"{TITLE}\" on The Anatomy Unfolded.\n{FOOT} #shorts", "tags": ["musculoskeletal system", "shorts"], "playlist": None,
              "publish_at": iso((6, 30) if k == 0 else (15, 30)), "youtube_id": None, "_cap": cap})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
