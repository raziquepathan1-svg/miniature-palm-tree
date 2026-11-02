import json, datetime as dt
import package as P
ep = {"id": "blood_pressure", "focus": [0.62, 0.62], "video": P.HERE / "blood_pressure.mp4", "dir": P.SP / "bp",
      "title": "Blood Pressure Explained: Systolic vs Diastolic (What 120/80 Means)",
      "thumb": ("WHAT", "120/80", "really means", "cuff_gauge"),
      "chapters": {"hook": "What 120/80 means", "what": "Blood pressure = push on artery walls", "systolic": "Systolic pressure",
                   "diastolic": "Diastolic pressure", "measure": "How a cuff measures it", "numbers": "Normal vs high numbers",
                   "formula": "BP = cardiac output x resistance", "baroreceptors": "Baroreceptors", "kidneys": "Kidneys & RAAS", "summary": "Summary"},
      "about": "Blood pressure explained simply: what systolic and diastolic pressure mean, what 120/80 mmHg tells you, and how your body controls blood pressure every second. We follow the blood from the left ventricle into the aorta to see where the top and bottom numbers come from, learn how a blood pressure cuff works, and break down the normal, elevated and high blood pressure ranges for adults. You'll learn the key formula, blood pressure = cardiac output x resistance, and how baroreceptors in the carotid arteries and aortic arch, plus the kidneys and the renin-angiotensin-aldosterone system (RAAS), keep your pressure in balance. Perfect for MBBS, nursing, pharmacy and biology students.",
      "short": [(["systolic", "diastolic"], "What Do 120/80 Actually Mean?"), (["baroreceptors"], "How Your Body Fixes Low Blood Pressure in Seconds")],
      "tags": ["blood pressure explained", "systolic and diastolic", "what does 120/80 mean", "blood pressure physiology", "normal blood pressure range",
               "how blood pressure is measured", "blood pressure cuff", "cardiac output and resistance", "baroreceptors", "baroreceptor reflex",
               "renin angiotensin aldosterone system", "RAAS explained", "hypertension basics", "cardiovascular physiology"]}
P.EPISODES.append(ep)
day = dt.date(2026, 11, 7)
q = json.load(open(P.REPO_Q))
q = [x for x in q if not x["id"].startswith("blood_pressure")]
vid = P.OUT / "blood_pressure.mp4"
import shutil; shutil.copy(ep["video"], vid)
P.thumbnail(ep, P.OUT / "blood_pressure_thumb.jpg")
when = dt.datetime.combine(day, dt.time(12, 30), dt.timezone.utc)
chap = "\n".join(["0:00 " + ep["chapters"]["hook"]] + [f"{P.stamp(t)} {ep['chapters'][i]}" for i, t, _ in P.scene_times(ep)[1:]])
q.append({"id": "blood_pressure", "kind": "video", "file": vid.name, "thumbnail": "blood_pressure_thumb.jpg", "title": ep["title"],
          "description": f"{ep['about']}\n\nCHAPTERS\n{chap}\n{P.FOOTER}", "tags": ep["tags"] + ["the anatomy unfolded"],
          "playlist": "Cardiovascular System", "publish_at": when.strftime("%Y-%m-%dT%H:%M:%SZ"), "youtube_id": None})
for k, hh in ((0, (6, 30)), (1, (15, 30))):
    sh = P.OUT / f"blood_pressure_short{k + 1}.mp4"
    t = P.short(ep, sh, k)
    st = dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc)
    q.append({"id": f"blood_pressure_short{k + 1}", "kind": "short", "file": sh.name, "thumbnail": None, "title": f"{t} #Shorts",
              "description": f"{ep['about']}\n\nFull video: \"{ep['title']}\" on The Anatomy Unfolded.\n{P.FOOTER} #shorts",
              "tags": ep["tags"] + ["shorts"], "playlist": None, "publish_at": st.strftime("%Y-%m-%dT%H:%M:%SZ"), "youtube_id": None})
json.dump(q, open(P.OUT / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
