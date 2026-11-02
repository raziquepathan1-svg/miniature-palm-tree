"""Owner (2 Nov): Shorts showed a cropped board - remake every Short with the full frame, logo-intro videos back in the queue."""
import shutil, sys
import package as P
import bridge
src = open(P.HERE / "add_bp.py").read()
exec(src[:src.index("P.EPISODES.append(ep)")] + "P.EPISODES.append(ep)")
only = sys.argv[1:]
for ep in P.EPISODES:
    if only and ep["id"] not in only:
        continue
    for k in (0, 1):
        sh = P.OUT / f"{ep['id']}_short{k + 1}.mp4"
        P.short(ep, sh, k)
        bridge.add_bridge(sh, ep["id"], k)
        print("short", sh.name, flush=True)
    if not only or "--videos" in only:
        pass
