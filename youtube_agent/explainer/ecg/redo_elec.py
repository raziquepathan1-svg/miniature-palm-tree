import json, subprocess, shutil
from pathlib import Path
import package as P
import osm_full
HERE = Path(__file__).resolve().parent
osm_full.render()                       # -> heart_electrical_osmosis.mp4 (clip overlay + video)
# narration-only audio (same as clean_audio.py)
import clean_audio  # noqa: F401  (re-runs all 5 cleanly; cheap)
ep = [e for e in P.EPISODES if e["id"] == "heart_electrical"][0]
shutil.copy(ep["video"], P.OUT / "heart_electrical.mp4")
for k in (0, 1):
    P.short(ep, P.OUT / f"heart_electrical_short{k + 1}.mp4", k)
print("electrical redone")
