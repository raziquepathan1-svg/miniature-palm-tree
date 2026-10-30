"""Swaps ONE wrong page of a daily video that is still waiting for approval (e.g. an anatomy clip that does not
match what is said) for one of our approved anatomy clips, keeping the sound and captions, and swaps the video in
on YouTube like fix_presenter does (same title, description, tags, playlists, our custom thumbnail; the Shorts
link to it; history.json follows it). The old video stays private (delete it in YouTube Studio).

python -m youtube_agent.fix_scene <run files folder> <old YouTube video ID> "<words said on that page>" <clip file>
"""

import json
import re
import sys
from pathlib import Path

from . import visuals
from .editor import _duration
from .fix_presenter import _parts, _swap_on_youtube
from .main import HERE, load_config, load_history, save_history


def main(run_dir: str, old: str, said: str, clip_name: str) -> None:
    config, history = load_config(), load_history()
    entry = next(h for h in history if h.get("youtube_id") == old)
    if not entry.get("awaiting_approval"):
        sys.exit("This video is already approved or public; not replacing it.")
    workdir = next(p.parent for p in Path(run_dir).rglob("narrated.txt"))
    final = workdir / "final.mp4"
    parts = _parts(workdir)
    start, idx = 0.0, None
    for i, p in enumerate(parts):  # the page whose captions say these words
        ass = p.with_suffix(".ass")
        words = " ".join(line.split(",", 9)[-1] for line in ass.read_text().splitlines()
                         if line.startswith("Dialogue:")) if ass.exists() else ""
        if said.lower() in " ".join(re.sub(r"\{[^}]*\}|\\N", " ", words).split()).lower():
            idx = i
            break
        start += _duration(p)
    if idx is None:
        sys.exit(f"No page says {said!r}; nothing was changed.")
    page = parts[idx]
    dur = _duration(page)
    total = sum(_duration(p) for p in parts)
    if abs(_duration(final) - total) > 0.3:  # the final video must line up with the pages
        sys.exit(f"final.mp4 ({_duration(final):.2f}s) does not line up with the pages ({total:.2f}s).")
    print(f"  Page {page.name}: {start:.2f}s to {start + dur:.2f}s")
    clip = HERE.parent / "branding/health-support-studio/footage" / clip_name
    visuals.ensure_fonts()
    from .anatomy_labels import _probe

    w, h, _ = _probe(final)
    new_page = visuals.render_anatomy_scene(clip, page, page.with_suffix(".ass"), dur, (w, h),
                                            workdir / "fixed_page.mp4")
    fixed = workdir / "final_fixed.mp4"
    enc = ["-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30", "-pix_fmt", "yuv420p"]
    a, b, c = (workdir / f"fix_{k}.mp4" for k in "abc")  # before, the new page, after (one at a time: low memory)
    visuals._run(["-y", "-i", str(final), "-t", f"{start:.3f}", *enc, str(a)])
    visuals._run(["-y", "-i", str(new_page), "-t", f"{dur:.3f}", *enc, str(b)])
    visuals._run(["-y", "-ss", f"{start + dur:.3f}", "-i", str(final), *enc, str(c)])
    lst = workdir / "fix_list.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in (a, b, c)))
    video = workdir / "fix_video.mp4"
    visuals._run(["-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(video)])
    visuals._run(["-y", "-i", str(video), "-i", str(final), "-map", "0:v", "-map", "1:a", "-c", "copy",
                  "-shortest", "-movflags", "+faststart", str(fixed)])
    print(f"  Fixed video: {_duration(fixed):.2f}s (was {_duration(final):.2f}s)")
    jobs = json.loads((HERE / "thumbnail_jobs.json").read_text())
    job = next((j for j in jobs if j["youtube_id"] == old), None)
    thumb = None
    if job and job.get("image"):  # our custom thumbnail, not the automatic one
        thumb = visuals.make_thumbnail(job["text"], config["channel"]["name"], workdir / "thumb_custom.jpg",
                                       HERE.parent / job["image"], style=job.get("style"),
                                       highlight=job.get("highlight"), own_picture=True)
    elif (workdir / "thumbnail.jpg").exists():
        thumb = workdir / "thumbnail.jpg"
    new = _swap_on_youtube(old, fixed, thumb, entry, config)
    entry["youtube_id"] = new
    entry.setdefault("replaced_ids", []).append(old)
    entry.pop("preview", None)
    save_history(history)
    Path("new_video_id.txt").write_text(new)
    Path("final_fixed_path.txt").write_text(str(fixed))
    print(f"Replaced {old} with {new} (page fixed). The old video stays private: delete it in YouTube Studio.")


if __name__ == "__main__":
    main(*sys.argv[1:5])
