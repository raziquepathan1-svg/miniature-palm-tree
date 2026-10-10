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
