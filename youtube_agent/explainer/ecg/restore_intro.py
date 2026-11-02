"""Owner (2 Nov): bring the logo intro back (with one soft chime) and replace the cropped Shorts.
Copies the full videos + new Shorts into the repo queue, recomputes chapters for the intro, and re-uploads
everything not yet public (old private uploads go to delete.json)."""
import json, re, shutil
import package as P
import growth_apply as G
src = open(P.HERE / "add_bp.py").read()
exec(src[:src.index("P.EPISODES.append(ep)")] + "P.EPISODES.append(ep)")
P.INTRO = 3.6
REPO = G.REPO
FINAL = {"heart_anatomy_v2": "final_heart_anatomy.mp4", "heart_physiology": "final_heart_physiology.mp4",
         "heart_electrical": "final_heart_electrical.mp4", "heart_attack": "final_heart_attack.mp4",
         "blood_vessels": "final_blood_vessels.mp4", "blood_pressure": "final_blood_pressure.mp4"}
PUBLIC = {"heart_anatomy_v2_short1"}          # already live - leave alone
eps = {e["id"]: e for e in P.EPISODES}
q = json.load(open(REPO / "queue.json"))
dele = json.load(open(REPO / "delete.json"))
for x in q:
    if x["id"] in PUBLIC:
        continue
    eid = x["id"].split("_short")[0]
    if x["kind"] == "video":
        shutil.copy(P.HERE / FINAL[eid], REPO / x["file"])
        if eid in G.CHAPTERS and eid not in ("heart_physiology",):   # these were cut for the no-intro version
            st = {i: t for i, t, _ in P.scene_times(eps[eid])}
            chap = "\n".join(f"{P.stamp(0 if n == 0 else st[i])} {name}" for n, (i, name) in enumerate(G.CHAPTERS[eid]))
            x["description"] = re.sub(r"CHAPTERS\n(?:\d+:\d\d [^\n]*\n)+", "CHAPTERS\n" + chap + "\n", x["description"])
    else:
        shutil.copy(P.OUT / x["file"], REPO / x["file"])
    if x.get("youtube_id"):
        dele.append(x["youtube_id"])
        x["youtube_id"] = None
    x.pop("update", None)
json.dump(q, open(REPO / "queue.json", "w"), indent=1, ensure_ascii=False)
json.dump(dele, open(REPO / "delete.json", "w"), indent=1)
print("delete:", dele)
for x in q:
    if x["kind"] == "video":
        print(x["id"], x["description"][x["description"].find("CHAPTERS"):].split("\n\n")[0].replace("\n", " | "))
