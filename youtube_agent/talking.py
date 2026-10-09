"""The host on screen: turns narration audio into a video of the host talking, on Kaggle's free GPU.

With "moves" clips (Google Flow videos of the host talking with head, body and hand movement, in the
`moves` folder), lipsync_kernel.py joins them and lip-syncs the mouth to the narration (Wav2Lip). Without
them, talking_kernel.py animates the host photo (SadTalker: face only). This file sends Kaggle the audio,
waits, and downloads the clips.
Anything that goes wrong returns fewer (or no) clips, so the video simply keeps its normal visuals there.

Needs the KAGGLE_USERNAME and KAGGLE_KEY (or KAGGLE_API_TOKEN) secrets.

Test (from the repo root):  python -m youtube_agent.talking voice.wav  ->  writes talking_test.mp4
"""

import base64
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image

from .editor import ffmpeg_bin

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
KERNEL_TEMPLATE = HERE / "talking_kernel.py"
LIPSYNC_TEMPLATE = HERE / "lipsync_kernel.py"

DEFAULTS = {
    "moves": "branding/health-support-studio/avatar/moves",           # from the repo root
    "lipsync": "latentsync",            # "latentsync" (sharp, natural lips) or "wav2lip" (faster, blurrier)
    "lipsync_steps": 40,
    "lipsync_guidance": 2.0,            # higher = lips follow the words more closely
    "pads": "0 15 0 0",                 # Wav2Lip face box padding (top bottom left right): include the chin
    "landscape_crop": 1.0,              # landscape videos show this top part of a moves clip (1.0 = whole body)
    "image": "branding/health-support-studio/avatar/nurse_final.jpg",  # from the repo root
    "crop": [0.06, 0.02, 0.94, 0.54],   # waist-up part of the photo (left, top, right, bottom as fractions)
    "image_width": 768,
    "kernel_slug": "hss-talking-host",
    "preprocess": "full",               # animate the face inside the whole picture
    "size": 256,
    "expression_scale": 1.0,
    "enhancer": "gfpgan",               # sharper face
    "max_wait_minutes": 90,
}


def settings(cfg: dict | None) -> dict:
    return {**DEFAULTS, **(cfg or {})}


def kaggle_ready() -> bool:
    return bool(os.environ.get("KAGGLE_USERNAME") and (os.environ.get("KAGGLE_KEY") or os.environ.get("KAGGLE_API_TOKEN")))


def _kaggle(*args: str, check: bool = True) -> str:
    r = subprocess.run(["kaggle", *args], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if check and r.returncode:
        raise RuntimeError(f"kaggle {' '.join(args[:2])} failed: {out[-1500:]}")
    return out


def _status(kid: str) -> str:
    out = _kaggle("kernels", "status", kid, check=False)
    m = re.search(r'has status "?(?:KernelWorkerStatus\.)?(\w+)', out, re.I)
    word = (m.group(1) if m else "").lower()
    return "cancelled" if word.startswith("cancel") else (word or "unknown")


def host_image(s: dict) -> bytes:
    """The waist-up host picture as JPEG bytes (even width and height)."""
    img = Image.open(ROOT / s["image"]).convert("RGB")
    l, t, r, b = s["crop"]
    img = img.crop((int(img.width * l), int(img.height * t), int(img.width * r), int(img.height * b)))
    w = s["image_width"]
    h = int(img.height * w / img.width) // 2 * 2
    buf = io.BytesIO()
    img.resize((w, h), Image.LANCZOS).save(buf, "JPEG", quality=92)
    return buf.getvalue()


def _is_portrait(clip: Path) -> bool:
    out = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", str(clip)], capture_output=True, text=True).stderr
    m = re.search(r"Video:.*?(\d{3,5})x(\d{3,5})", out)
    return bool(m) and int(m.group(2)) > int(m.group(1))


def moves_clips(s: dict) -> list[str]:
    """The portrait (9:16) moves clips; landscape ones are skipped (cropping them zooms in far too much)."""
    folder = ROOT / s["moves"]
    clips = sorted(folder.glob("*.mp4")) if folder.exists() else []
    only = s.get("moves_only")  # optional: just these files
    return [c.name for c in clips if (_is_portrait(c) or s.get("any_shape")) and (not only or c.name in only)]


def _raw_base(s: dict) -> str:
    """Where Kaggle downloads the moves clips (the public GitHub repo)."""
    repo = os.environ.get("GITHUB_REPOSITORY", "raziquepathan1-svg/miniature-palm-tree")
    branch = os.environ.get("GITHUB_REF_NAME", "claude/kind-albattani-59hcns")
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{s['moves']}"


def _mp3(wav: Path) -> bytes:
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "a.mp3"
        subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(wav), "-ac", "1", "-b:a", "64k", str(out)],
                       check=True)
        return out.read_bytes()


def make_clips(audio: dict[str, Path], workdir: Path, cfg: dict | None = None) -> dict[str, Path]:
    """{id: narration wav} -> {id: talking-host mp4} for every clip Kaggle made in time."""
    s = settings(cfg)
    if not audio:
        return {}
    if not kaggle_ready():
        print("  (Host clips skipped: the Kaggle secrets are not set)")
        return {}
    user = os.environ["KAGGLE_USERNAME"].strip()
    kid = f"{user}/{s['kernel_slug']}"
    b64 = lambda data: base64.b64encode(data).decode()  # noqa: E731
    moves = moves_clips(s)
    jobs = [{"id": k, "audio": b64(_mp3(w)), "start": n} for n, (k, w) in enumerate(audio.items())]
    for job in jobs:  # optional: each job lip-syncs its own clip, from second `ss` (see dub_clips.py)
        if job["id"] in (s.get("job_clips") or {}):
            job.update(start=moves.index(s["job_clips"][job["id"]]), only=True, ss=s.get("job_ss", {}).get(job["id"], 0))
    if moves:  # natural movement: the moves clips, lip-synced
        print(f"  Host: {len(moves)} moves clips, lip-synced on Kaggle")
        settings_json = {"moves": moves, "raw_base": _raw_base(s), "pads": s["pads"], "engine": s["lipsync"],
                         "steps": s["lipsync_steps"], "guidance": s["lipsync_guidance"],
                         "keep_size": bool(s.get("any_shape"))}
        code = (LIPSYNC_TEMPLATE.read_text()
                .replace("__JOBS__", b64(json.dumps(jobs).encode()))
                .replace("__SETTINGS__", b64(json.dumps(settings_json).encode())))
    else:  # the photo, animated (face only)
        keys = ("preprocess", "size", "expression_scale", "enhancer")
        code = (KERNEL_TEMPLATE.read_text()
                .replace("__JOBS__", b64(json.dumps(jobs).encode()))
                .replace("__SETTINGS__", b64(json.dumps({k: s[k] for k in keys}).encode()))
                .replace("__IMAGE__", b64(host_image(s))))
    try:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "talk.py").write_text(code)
            (Path(d) / "kernel-metadata.json").write_text(json.dumps({
                "id": kid, "title": s["kernel_slug"], "code_file": "talk.py", "language": "python",
                "kernel_type": "script", "is_private": True, "enable_gpu": True, "enable_internet": True,
                "dataset_sources": [], "competition_sources": [], "kernel_sources": [], "model_sources": []}))
            print("  " + _kaggle("kernels", "push", "-p", d)[-300:])
        started = time.time()
        time.sleep(60)
        status = "unknown"
        while time.time() - started < s["max_wait_minutes"] * 60:
            status = _status(kid)
            if status in ("complete", "error", "cancelled"):
                break
            time.sleep(30)
        print(f"  Kaggle host run: {status} after {(time.time() - started) / 60:.0f} min")

        out_dir = workdir / "host"
        out_dir.mkdir(parents=True, exist_ok=True)
        print("  " + _kaggle("kernels", "output", kid, "-p", str(out_dir), check=False)[-500:])
        result_file = next(out_dir.rglob("result.json"), None)
        result = json.loads(result_file.read_text()) if result_file else {}
        if result.get("error"):
            print(f"  Kaggle host error:\n{result['error']}")
        got = {}
        for k in audio:
            res = (result.get("jobs") or {}).get(k) or {}
            if res.get("error"):
                print(f"  Host clip {k} failed:\n{res['error']}")
            clip = next(out_dir.rglob(f"{k}.mp4"), None)
            if clip and clip.stat().st_size > 20_000:
                got[k] = clip
        print(f"  Host clips ready: {len(got)} of {len(audio)} (GPU: {result.get('gpu', '?')})")
        return got
    except Exception as e:
        print(f"  (Host clips skipped: {e})")
        return {}


def landscape_crop(cfg: dict | None) -> float:
    """How much of the host clip (from the top) landscape videos show: tall moves clips are cropped to the waist."""
    s = settings(cfg)
    return s["landscape_crop"] if moves_clips(s) else 1.0


def broll_clips(cfg: dict | None) -> list[Path]:
    """The host's B-roll clips (walking, reading a chart, at the desk: no talking), in the `broll` folder."""
    folder = ROOT / (cfg or {}).get("broll", "branding/health-support-studio/avatar/broll")
    return sorted(folder.glob("*.mp4")) if folder.exists() else []


def pick_snippets(scenes: list[tuple[float, list]], cfg: dict | None) -> dict[int, float]:
    """About every `every_seconds` of video, the host says the start of a scene on screen.
    scenes: (duration, captions) per scene. Returns {scene index: seconds the host speaks}, ending the host
    part where a caption ends (5-10 s) so it stops between phrases, not mid-word."""
    cfg = cfg or {}
    every = float(cfg.get("every_seconds", 60))
    lo, hi = cfg.get("snippet_seconds", [5, 10])
    picks, t, next_at = {}, 0.0, float(cfg.get("first_at", 30))
    for i, (duration, captions) in enumerate(scenes):
        if t >= next_at and duration >= lo:
            ends = [end for _, end, _ in captions if lo <= end <= hi]
            picks[i] = ends[-1] if ends else min(hi, duration)
            next_at = t + every
        t += duration
    return picks


def pick_scenes(n: int, cfg: dict | None) -> list[int]:
    """Which scenes (0-based) the host presents: the first, every `every`-th in between, and the last."""
    every = int((cfg or {}).get("every", 3))
    picks = {0, n - 1} | set(range(every, n - 1, every))
    return sorted(i for i in picks if 0 <= i < n)


if __name__ == "__main__":
    wav = Path(sys.argv[1])
    clips = make_clips({"test": wav}, Path("talking_out"))
    if clips:
        Path("talking_test.mp4").write_bytes(clips["test"].read_bytes())
        print("Wrote talking_test.mp4")
    else:
        sys.exit("No talking clip was made")
