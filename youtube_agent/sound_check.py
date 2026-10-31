"""Last check before a Reel is posted: scans the whole video's sound, end included, for the harsh buzzing
take the cloned voice once produced (a carbon monoxide Reel went out with it, Oct 25). Speech-only 2-second
windows; the 5-8 kHz share of a broken take was 0.12-0.17 there, normal Reels stay under about 0.10.

    python -m youtube_agent.sound_check video.mp4    # exit 1 (do not post) when it looks wrong
"""
import subprocess
import sys

import numpy as np

LIMIT = 0.11


def _ffmpeg() -> str:
    """ffmpeg without the editor's picture libraries (the Instagram/Facebook job installs only numpy)."""
    import os
    import shutil

    exe = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def scan(path: str, sr: int = 24000) -> tuple[float, float]:
    raw = subprocess.run([_ffmpeg(), "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "s16le",
                          "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    win, hop, n = int(2.0 * sr), int(0.25 * sr), 1024
    worst = (0.0, 0.0)
    for i in range(0, max(1, len(a) - win), hop):
        x = a[i:i + win]
        f = x[:len(x) // 1200 * 1200].reshape(-1, 1200)
        if not len(f) or (20 * np.log10(np.sqrt((f ** 2).mean(1)) + 1e-9) > -40).mean() < 0.6:
            continue  # mostly silence: nothing to judge
        frames = np.array([x[j:j + n] * np.hanning(n) for j in range(0, len(x) - n, n // 2)])
        power = np.abs(np.fft.rfft(frames, axis=1)) ** 2
        freqs = np.fft.rfftfreq(n, 1 / sr)
        energy = power.sum(1)
        power = power[energy > np.percentile(energy, 40)]
        low = power[:, (freqs > 80) & (freqs < 4000)].sum()
        score = float(power[:, (freqs > 5000) & (freqs < 8000)].sum() / low) if low else 0.0
        worst = max(worst, (score, i / sr))
    return worst


if __name__ == "__main__":
    bad = False
    for p in sys.argv[1:]:
        score, at = scan(p)
        ok = score <= LIMIT
        bad |= not ok
        print(f"{'OK  ' if ok else 'STOP'} {p}: worst {score:.3f} at {at:.1f}s (limit {LIMIT})")
    sys.exit(1 if bad else 0)
