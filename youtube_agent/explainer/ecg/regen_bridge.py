"""Owner (9 Nov 2026): every Short ending must give a REASON to watch the full video + subscribe.
Re-cut the ending of Shorts that are not public yet: cut the old bridge card (the static tail), add the new one.

    python3 regen_bridge.py heart_failure_short2 arrhythmia_short1 ...
Writes the new mp4 over explainer_queue/<id>.mp4 and prints the old YouTube id (for delete.json).
"""
import json, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # repo root (youtube_agent)
import bridge

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2] / "explainer_queue"
for f in HERE.glob("add_*.py"):   # the open-loop questions written when each episode was added
    src = f.read_text()
    m_id = re.search(r'ep = \{"id": "(\w+)"', src)
    m_q = re.search(r'bridge\.QUESTIONS\[ep\["id"\]\] = (\[.*?\])', src)
    if m_id and m_q:
        bridge.QUESTIONS[m_id.group(1)] = json.loads(m_q.group(1))


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)


def bridge_start(p):
    """start time of the final static card (the old bridge)."""
    out = subprocess.run(["ffmpeg", "-v", "info", "-i", str(p), "-vf", "freezedetect=n=0.003:d=1", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", out)]
    d = dur(p)
    for st in reversed(starts):
        if not [e for e in ends if e > st] or max(ends) >= d - 0.3:
            return st
    raise RuntimeError("no final static card found in " + str(p))


def main(ids):
    for sid in ids:
        eid, k = sid.rsplit("_short", 1)
        path = REPO / f"{sid}.mp4"
        t = bridge_start(path)
        body = HERE / f"_body_{sid}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-t", f"{t:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(body)], check=True)
        bridge.add_bridge(body, eid, int(k) - 1)
        body.replace(path)
        print(f"{sid}: old ending cut at {t:.1f}s, new length {dur(path):.1f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
