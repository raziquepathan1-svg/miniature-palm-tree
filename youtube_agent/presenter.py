"""The small presenter in the corner: the host on a green screen, lip-synced to the narration, cut out.

    python -m youtube_agent.presenter lipsync OUT.mp4 VOICE.wav CLIP.mp4 [CLIP2.mp4 ...] [--engine=wav2lip]
"""

import shutil
import sys
import tempfile
from pathlib import Path

from . import talking

ROOT = Path(__file__).resolve().parent.parent


def lipsync(clips: list[Path], wav: Path, out: Path, engine: str = "wav2lip") -> Path | None:
    """The green-screen clips one after another (as long as the voice) with the mouth moved to the voice.
    Wav2Lip is fast enough for a whole narration; LatentSync is sharper but far slower. None if Kaggle failed."""
    clips = [c.resolve() for c in clips]
    with tempfile.TemporaryDirectory() as tmp:
        made = talking.make_clips({"presenter": wav}, Path(tmp), {
            "moves": clips[0].parent.relative_to(ROOT).as_posix(), "moves_only": [c.name for c in clips],
            "any_shape": True, "lipsync": engine, "max_wait_minutes": 150})
        if "presenter" not in made:
            return None
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(made["presenter"], out)
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    engine = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--engine=")), "wav2lip")
    if len(args) >= 4 and args[0] == "lipsync":
        done = lipsync([Path(c) for c in args[3:]], Path(args[2]), Path(args[1]), engine)
        print(f"Lip-synced presenter: {done}" if done else "Lip-sync failed")
        sys.exit(0 if done else 1)
    print(__doc__)


def _key_frames(src: Path, out: Path, height: int) -> Path:
    """Green screen -> transparent, at the size shown on screen (fast enough for a whole video)."""
    import subprocess

    import numpy as np

    from .editor import ffmpeg_bin

    probe = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", str(src)], capture_output=True, text=True).stderr
    import re

    w0, h0 = map(int, re.search(r"Video:.*?(\d{3,5})x(\d{3,5})", probe).groups())
    fps = re.search(r"(\d+(?:\.\d+)?) fps", probe).group(1)
    h = height // 2 * 2
    w = int(w0 * h / h0) // 2 * 2
    dec = subprocess.Popen([ffmpeg_bin(), "-loglevel", "error", "-i", str(src), "-vf", f"scale={w}:{h}",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen([ffmpeg_bin(), "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
                            "-s", f"{w}x{h}", "-r", fps, "-i", "-", "-c:v", "qtrle", str(out)], stdin=subprocess.PIPE)
    size = w * h * 3
    while True:
        buf = dec.stdout.read(size)
        if len(buf) < size:
            break
        a = np.frombuffer(buf, np.uint8).reshape(h, w, 3).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        green = g - np.maximum(r, b)
        alpha = np.clip((32 - green) * 255 // 18, 0, 255)  # >32 more green than red/blue: background
        g = np.where(green > 0, np.maximum(r, b) + green // 7, g)  # no green glow on hair and edges
        enc.stdin.write(np.dstack([r, g, b, alpha]).astype(np.uint8).tobytes())
    enc.stdin.close()
    enc.wait()
    dec.wait()
    return out


def add_presenter(video: Path, shows: list[tuple[float, float]], cfg: dict, workdir: Path) -> Path:
    """The lip-synced presenter in the bottom-right corner during `shows` (start, end seconds) of the video.
    Returns the original video if anything fails, so the day's video is never lost."""
    import subprocess

    from .editor import ffmpeg_bin

    try:
        clips = [ROOT / c for c in cfg["clips"]]
        wav = workdir / "presenter_voice.wav"
        subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000",
                        str(wav)], check=True)
        print(f"    Corner presenter: lip-syncing {len(clips)} clips to the narration on Kaggle...")
        lip = lipsync(clips, wav, workdir / "presenter_lipsync.mp4", cfg.get("engine", "wav2lip"))
        if not lip:
            print("    (Corner presenter skipped: lip-sync did not come back)")
            return video
        keyed = _key_frames(lip, workdir / "presenter_keyed.mov", int(cfg.get("height", 760)))
        enable = "+".join(f"between(t,{a:.2f},{b:.2f})" for a, b in shows) or "0"
        out = video.with_name(video.stem + "_presenter.mp4")
        subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(video), "-i", str(keyed),
                        "-filter_complex", f"[1:v]format=rgba[p];[0:v][p]overlay=W-w-20:H-h:eof_action=pass:"
                        f"enable='{enable}',format=yuv420p[v]",
                        "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-c:a", "copy", "-movflags", "+faststart", str(out)], check=True)
        print(f"    Corner presenter added ({len(shows)} parts)")
        return out
    except Exception as e:  # never lose the video over the presenter
        print(f"    (Corner presenter skipped: {e})")
        return video
