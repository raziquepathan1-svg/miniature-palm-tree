"""Runs on Kaggle's free GPU (pushed there by talking.py; not run on GitHub).

Makes the host talk: animates the host photo so the lips, head and eyes follow each narration audio, with the
open SadTalker model (face only; the body stays still). Writes <id>.mp4 per job and result.json to
/kaggle/working, where talking.py downloads them.

__JOBS__, __IMAGE__ and __SETTINGS__ are filled in by talking.py (base64).
"""

import base64
import json
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path

JOBS = json.loads(base64.b64decode("__JOBS__"))
SETTINGS = json.loads(base64.b64decode("__SETTINGS__"))
OUT = Path("/kaggle/working")
WORK = Path("/kaggle/temp")
REPO = WORK / "SadTalker"
RESULT = {"jobs": {}, "started": time.time()}

CHECKPOINTS = {
    "checkpoints": [
        "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar",
        "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar",
        "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors",
        "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors",
    ],
    "gfpgan/weights": [
        "https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth",
        "https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth",
        "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
        "https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth",
    ],
}


def save_result() -> None:
    (OUT / "result.json").write_text(json.dumps(RESULT, indent=2))


def sh(cmd: str, cwd: Path | None = None) -> None:
    print(f"+ {cmd}", flush=True)
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)


def patch(path: Path, *subs: tuple[str, str], regex: bool = False) -> None:
    text = path.read_text()
    for old, new in subs:
        text = re.sub(old, new, text) if regex else text.replace(old, new)
    path.write_text(text)


def setup() -> None:
    """SadTalker and its weights, patched for today's numpy / librosa / torchvision."""
    WORK.mkdir(parents=True, exist_ok=True)
    sh(f"git clone -q --depth 1 https://github.com/OpenTalker/SadTalker {REPO}")
    sh(f"{sys.executable} -m pip install -q 'numpy<2' face_alignment==1.3.5 imageio imageio-ffmpeg librosa==0.10.1 "
       "resampy pydub kornia==0.6.8 yacs safetensors facexlib==0.3.0 basicsr==1.4.2 gfpgan av")
    for folder, urls in CHECKPOINTS.items():
        (REPO / folder).mkdir(parents=True, exist_ok=True)
        for url in urls:
            sh(f"wget -q -nc {url}", cwd=REPO / folder)

    # basicsr imports a torchvision module that no longer exists
    out = subprocess.run([sys.executable, "-c", "import importlib.util as u; print(u.find_spec('basicsr').origin)"],
                         capture_output=True, text=True, check=True).stdout.strip()
    patch(Path(out).parent / "data" / "degradations.py",
          ("torchvision.transforms.functional_tensor", "torchvision.transforms.functional"))
    # numpy removed np.float / np.int; newer numpy refuses the ragged array in preprocess.py
    for py in (REPO / "src").rglob("*.py"):
        patch(py, (r"np\.float\b", "np.float64"), (r"np\.int\b", "int"), regex=True)
    patch(REPO / "src" / "face3d" / "util" / "preprocess.py",
          ("np.array([w0, h0, s, t[0], t[1]])", "np.array([w0, h0, s, float(t[0]), float(t[1])])"))
    # librosa 0.10 takes keyword arguments only
    patch(REPO / "src" / "utils" / "audio.py",
          ("librosa.filters.mel(hp.sample_rate, hp.n_fft,", "librosa.filters.mel(sr=hp.sample_rate, n_fft=hp.n_fft,"))


def talk(job: dict, image: Path) -> Path:
    """One talking clip: SadTalker writes <result_dir>/<time>.mp4."""
    jd = WORK / job["id"]
    jd.mkdir(parents=True, exist_ok=True)
    mp3, wav = jd / "voice.mp3", jd / "voice.wav"
    mp3.write_bytes(base64.b64decode(job["audio"]))
    sh(f"ffmpeg -y -loglevel error -i {mp3} -ar 16000 -ac 1 {wav}")
    extra = f" --enhancer {SETTINGS['enhancer']}" if SETTINGS.get("enhancer") else ""
    sh(f"{sys.executable} inference.py --driven_audio {wav} --source_image {image} --result_dir {jd / 'res'} "
       f"--still --preprocess {SETTINGS['preprocess']} --size {SETTINGS['size']} "
       f"--expression_scale {SETTINGS['expression_scale']}{extra}", cwd=REPO)
    made = sorted((jd / "res").glob("*.mp4"), key=lambda p: p.stat().st_mtime)
    if not made:
        raise RuntimeError("SadTalker made no video")
    dest = OUT / f"{job['id']}.mp4"
    made[-1].replace(dest)
    return dest


try:
    import torch

    RESULT["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none"
    print(f"GPU: {RESULT['gpu']}", flush=True)
    setup()
    image = WORK / "host.jpg"
    image.write_bytes(base64.b64decode("__IMAGE__"))
    RESULT["setup_seconds"] = round(time.time() - RESULT["started"])
    save_result()
    for job in JOBS:
        t = time.time()
        try:
            out = talk(job, image)
            RESULT["jobs"][job["id"]] = {"video": out.name, "seconds": round(time.time() - t)}
        except Exception:
            RESULT["jobs"][job["id"]] = {"error": traceback.format_exc()[-3000:]}
        print(f"{job['id']}: {RESULT['jobs'][job['id']]}", flush=True)
        save_result()
except Exception:
    RESULT["error"] = traceback.format_exc()[-3000:]
    print(RESULT["error"], flush=True)
RESULT["seconds"] = round(time.time() - RESULT["started"])
save_result()
