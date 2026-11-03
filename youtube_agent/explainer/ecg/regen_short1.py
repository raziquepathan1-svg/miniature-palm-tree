"""Owner (2 Nov): Shorts must not say 'link on screen' (Instagram/Facebook have no on-screen link). Remake every Short
not yet posted to Instagram/Facebook with the new ending: 'FULL VIDEO ON OUR CHANNEL'."""
import json, shutil, sys
import package as P
import bridge
for f, src_dir in (("add_bp.py", None), ("add_htn.py", None), ("add_hf.py", None), ("add_arr.py", None), ("add_valv.py", None)):
    src = open(P.HERE / f).read()
    ns = {"P": P, "bridge": bridge}
    exec(src[:src.index("P.EPISODES.append(ep)")], ns)
    ns["ep"]["video"] = P.HERE / ("final_" + ns["ep"]["id"] + ".mp4")
    P.EPISODES.append(ns["ep"])
    i = src.find("bridge.QUESTIONS[ep[\"id\"]] = ")
    if i >= 0:
        bridge.QUESTIONS[ns["ep"]["id"]] = eval(src[i:].split("=", 1)[1].split("\n")[0])
REPO = P.SP / "main" / "explainer_queue"
posted = json.load(open(REPO / "social_posted.json"))
done = []
ONLY = [a for a in sys.argv[1:] if not a.startswith("--")]
for ep in P.EPISODES:
    if not ep["video"].exists():
        print("missing video", ep["id"]); continue
    for k in ((0,) if "--short1" in sys.argv else (0, 1)):
        sid = f"{ep['id']}_short{k + 1}"
        if sid in posted or (ONLY and ep["id"] not in ONLY):
            continue
        sh = P.OUT / f"{sid}.mp4"
        P.short(ep, sh, k)
        bridge.add_bridge(sh, ep["id"], k)
        shutil.copy(sh, REPO / sh.name)
        done.append(sid)
        print("remade", sid, flush=True)
print(len(done))
