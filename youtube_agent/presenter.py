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


def _probe(path: Path) -> tuple[int, int, str]:
    import re
    import subprocess

    from .editor import ffmpeg_bin

    err = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    w, h = map(int, re.search(r"Video:.*?(\d{3,5})x(\d{3,5})", err).groups())
    return w, h, re.search(r"(\d+(?:\.\d+)?) fps", err).group(1)


def _key_frames(src: Path, height: int, sink, shows: list[tuple[float, float]] | None = None,
                fade: float = 0.35) -> tuple[int, int, str]:
    """Green screen -> transparent RGBA frames at the size shown on screen, written to `sink` (a pipe);
    nothing big is stored, so a whole video fits. Returns (width, height, fps)."""
    import subprocess

    import numpy as np

    from .editor import ffmpeg_bin

    w0, h0, fps = _probe(src)
    h = height // 2 * 2
    w = int(w0 * h / h0) // 2 * 2
    dec = subprocess.Popen([ffmpeg_bin(), "-loglevel", "error", "-i", str(src), "-vf",
                            f"scale={w}:{h}:flags=lanczos,unsharp=5:5:0.7:3:3:0.0",  # crisp at the small size
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    size = w * h * 3
    rate, n = float(fps), 0
    while True:
        buf = dec.stdout.read(size)
        if len(buf) < size:
            break
        a = np.frombuffer(buf, np.uint8).reshape(h, w, 3).astype(np.int16)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        green = g - np.maximum(r, b)
        alpha = np.clip((32 - green) * 255 // 18, 0, 255)  # >32 more green than red/blue: background
        if shows is not None:  # fade in and out instead of popping on and off
            t = n / rate
            vis = max((min(1.0, (t - a) / fade, (b - t) / fade) for a, b in shows if a <= t <= b), default=0.0)
            alpha = alpha * vis
        n += 1
        g = np.where(green > 0, np.maximum(r, b) + green // 7, g)  # no green glow on hair and edges
        try:
            sink.write(np.dstack([r, g, b, alpha]).astype(np.uint8).tobytes())
        except BrokenPipeError:  # the video ended first: the rest of the presenter is not needed
            break
    dec.kill()
    dec.wait()
    return w, h, fps


def add_presenter(video: Path, shows: list[tuple[float, float]], cfg: dict, workdir: Path) -> Path:
    """The lip-synced presenter in the bottom-right corner during `shows` (start, end seconds) of the video.
    Returns the original video if anything fails, so the day's video is never lost."""
    import subprocess

    from .editor import ffmpeg_bin

    try:
        clips = [ROOT / c for c in cfg["clips"]]
        wav = workdir / "presenter_voice.wav"
        # louder, evened-out voice for the lip-sync only: quiet syllables still move the mouth
        subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000",
                        "-af", "acompressor=threshold=-28dB:ratio=6:attack=5:release=80,loudnorm=I=-14:TP=-1",
                        str(wav)], check=True)
        print(f"    Corner presenter: lip-syncing {len(clips)} clips to the narration on Kaggle...")
        lip = lipsync(clips, wav, workdir / "presenter_lipsync.mp4", cfg.get("engine", "wav2lip"))
        if not lip:
            print("    (Corner presenter skipped: lip-sync did not come back)")
            return video
        height = int(cfg.get("height", 760)) // 2 * 2
        w0, h0, fps = _probe(lip)
        w = int(w0 * height / h0) // 2 * 2
        out = video.with_name(video.stem + "_presenter.mp4")
        mix = subprocess.Popen([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(video),
                                "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{height}", "-r", fps, "-i", "-",
                                "-filter_complex", "[0:v][1:v]overlay=W-w-20:H-h:eof_action=pass,format=yuv420p[v]",
                                "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "veryfast",
                                "-crf", "20", "-c:a", "copy", "-movflags", "+faststart", str(out)],
                               stdin=subprocess.PIPE)
        _key_frames(lip, height, mix.stdin, shows)
        try:
            mix.stdin.close()
        except BrokenPipeError:
            pass
        if mix.wait():
            raise RuntimeError("ffmpeg could not add the presenter")
        print(f"    Corner presenter added ({len(shows)} parts)")
        return out
    except Exception as e:  # never lose the video over the presenter
        print(f"    (Corner presenter skipped: {e})")
        return video
