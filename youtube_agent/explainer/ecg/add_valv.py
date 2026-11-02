"""Add Heart Valves - Wed 11 Nov 2026: video 6 PM, Shorts 12 PM + 9 PM IST."""
import datetime as dt, json, shutil
import package as P
import growth_apply as G
import bridge

ep = {"id": "heart_valves", "focus": [0.5, 0.5], "video": P.HERE / "final_heart_valves.mp4", "dir": P.SP / "valv",
      "title": "What Happens When a Heart Valve Fails? Stenosis vs Regurgitation Explained",
      "about": "Heart valve disease explained simply. Your heart has 4 valves (tricuspid, pulmonary, mitral and aortic) that work as one-way doors. Learn the 2 ways a valve fails: stenosis (narrow and stiff, does not open fully) and regurgitation (leaky, does not close tightly), what each does to the heart, why aortic stenosis is common in older adults, the main causes (age and calcium, rheumatic fever after untreated strep throat, valves you are born with, endocarditis, heart attack), what a heart murmur is, why the echocardiogram is the key test, the warning signs, and treatment from check-ups and medicines to valve repair or replacement. Perfect for MBBS, nursing, pharmacy and biology students.",
      "short": [(["two", "stenosis"], "Stiff vs Leaky: 2 Ways a Heart Valve Fails"), (["causes"], "How a Sore Throat Can Damage Your Heart Valves")],
      "tags": ["heart valve disease", "heart valves", "aortic stenosis", "mitral regurgitation", "valve stenosis", "valve regurgitation", "heart murmur", "rheumatic heart disease", "valve replacement", "echocardiogram"]}
P.EPISODES.append(ep)
bridge.QUESTIONS[ep["id"]] = ["So what does a leaky valve do?", "So how is it found?"]
KEY = "Heart valve disease • Valve stenosis and regurgitation • Heart murmur"
CH = [("hook", "The 4 heart valves"), ("two", "Stenosis vs regurgitation"), ("causes", "What damages heart valves"), ("murmur", "Heart murmur, echo & warning signs"), ("treat", "Treatment & summary")]
P.INTRO = 3.6
day = dt.date(2026, 11, 11)
REPO = G.REPO
q = json.load(open(REPO / "queue.json"))
q = [x for x in q if not x["id"].startswith(ep["id"])]
shutil.copy(ep["video"], REPO / "heart_valves.mp4")
shutil.copy(P.SP / "thumbs_ai" / "heart_valves_thumb.jpg", REPO / "heart_valves_thumb.jpg")
st = {i: t for i, t, _ in P.scene_times(ep)}
chap = "\n".join(f"{P.stamp(0 if n == 0 else st[i])} {name}" for n, (i, name) in enumerate(CH))
when = dt.datetime.combine(day, dt.time(12, 30), dt.timezone.utc)
q.append({"id": ep["id"], "kind": "video", "file": "heart_valves.mp4", "thumbnail": "heart_valves_thumb.jpg", "title": ep["title"],
          "description": f"{KEY}\n\n{ep['about']}\n\nCHAPTERS\n{chap}\n{P.FOOTER}", "tags": ep["tags"] + ["the anatomy unfolded"],
          "playlist": "Cardiovascular System", "publish_at": when.strftime("%Y-%m-%dT%H:%M:%SZ"), "youtube_id": None})
for k, hh in ((0, (6, 30)), (1, (15, 30))):
    sh = P.OUT / f"{ep['id']}_short{k + 1}.mp4"
    t = P.short(ep, sh, k)
    bridge.add_bridge(sh, ep["id"], k)
    shutil.copy(sh, REPO / sh.name)
    s_ = dt.datetime.combine(day, dt.time(*hh), dt.timezone.utc)
    q.append({"id": f"{ep['id']}_short{k + 1}", "kind": "short", "file": sh.name, "thumbnail": None, "title": f"{t} #Shorts",
              "description": f"{ep['about']}\n\nFull video: \"{ep['title']}\" on The Anatomy Unfolded.\n{P.FOOTER} #shorts",
              "tags": ep["tags"] + ["shorts"], "playlist": None, "publish_at": s_.strftime("%Y-%m-%dT%H:%M:%SZ"), "youtube_id": None})
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
print(chap)
