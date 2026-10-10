"""The small presenter in the corner: the host on a green screen, lip-synced to the narration, cut out.

    python -m youtube_agent.presenter lipsync CLIP.mp4 VOICE.wav OUT.mp4   # LatentSync on Kaggle (green kept)
"""

import shutil
import sys
import tempfile
from pathlib import Path

from . import talking

ROOT = Path(__file__).resolve().parent.parent


def lipsync(clip: Path, wav: Path, out: Path) -> Path | None:
    """The green-screen clip (looped as needed) with the mouth moved to the voice; None if Kaggle failed."""
    clip = clip.resolve()
    with tempfile.TemporaryDirectory() as tmp:
        made = talking.make_clips({"presenter": wav}, Path(tmp), {
            "moves": clip.parent.relative_to(ROOT).as_posix(), "moves_only": [clip.name], "any_shape": True,
            "job_clips": {"presenter": clip.name}, "job_ss": {"presenter": 0}})
        if "presenter" not in made:
            return None
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(made["presenter"], out)
    return out


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "lipsync":
        done = lipsync(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
        print(f"Lip-synced presenter: {done}" if done else "Lip-sync failed")
        sys.exit(0 if done else 1)
    print(__doc__)
