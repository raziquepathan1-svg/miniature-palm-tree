"""Runs on Kaggle's free GPU (pushed there by talking.py; not run on GitHub).

Makes the host talk with natural movement: joins the host's "moves" clips (Google Flow videos of the host
talking with head, body and hand movement) into one video as long as each narration, then lip-syncs the
mouth to the narration with LatentSync 1.5 (sharp, natural lips) or Wav2Lip (faster, blurrier mouth).
Writes <id>.mp4 per job and result.json to /kaggle/working.

__JOBS__ and __SETTINGS__ are filled in by talking.py (base64 JSON).
"""

import base64
import json
import re
import shutil
import subprocess
import sys
import time
import traceback
import urllib.parse
from pathlib import Path

JOBS = json.loads(base64.b64decode("__JOBS__"))
SETTINGS = json.loads(base64.b64decode("__SETTINGS__"))
OUT = Path("/kaggle/working")
WORK = Path("/kaggle/temp")
ENGINE = SETTINGS.get("engine", "latentsync")
REPO = WORK / ("LatentSync" if ENGINE == "latentsync" else "Wav2Lip")
VENV = WORK / "venv"
PY = VENV / "bin" / "python"
MOVES = WORK / "moves"
FPS = 25
XFADE = 0.4
RESULT = {"jobs": {}, "started": time.time()}

WEIGHTS = {
    "checkpoints/wav2lip_gan.pth": [
        "https://huggingface.co/camenduru/Wav2Lip/resolve/main/checkpoints/wav2lip_gan.pth",
        "https://huggingface.co/Nekochu/Wav2Lip/resolve/main/wav2lip_gan.pth",
        "https://huggingface.co/numz/wav2lip_studio/resolve/main/Wav2lip/wav2lip_gan.pth",
    ],
    "face_detection/detection/sfd/s3fd.pth": [
        "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth",
        "https://huggingface.co/camenduru/Wav2Lip/resolve/main/face_detection/detection/sfd/s3fd.pth",
        "https://huggingface.co/numz/wav2lip_studio/resolve/main/Wav2lip/s3fd.pth",
    ],
}


def save_result() -> None:
    (OUT / "result.json").write_text(json.dumps(RESULT, indent=2))


def sh(cmd: str, cwd: Path | None = None) -> str:
    print(f"+ {cmd}", flush=True)
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    print(r.stdout[-1500:] + r.stderr[-1500:], flush=True)
    if r.returncode:
        raise RuntimeError(f"Failed ({r.returncode}): {cmd}\n{(r.stdout + r.stderr)[-2500:]}")
    return r.stdout + r.stderr


def duration(path: Path) -> float:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def _venv() -> str:
    sh(f"{sys.executable} -m pip install -q uv")
    sh(f"{sys.executable} -m uv venv -q --python 3.10 {VENV}")
    return f"{sys.executable} -m uv pip install -q --python {PY}"


def setup_latentsync() -> None:
    """LatentSync 1.5 (256 px lips; fits Kaggle's 15 GB T4) in its own Python 3.10."""
    sh(f"git clone -q --depth 1 https://github.com/bytedance/LatentSync {REPO}")
    uv = _venv()
    reqs = [l for l in (REPO / "requirements.txt").read_text().splitlines() if l and not l.startswith("gradio")]
    (REPO / "requirements_kaggle.txt").write_text("\n".join(reqs) + "\n")
    sh(f"{uv} 'setuptools<70' wheel cython")
    sh(f"{uv} -r requirements_kaggle.txt --index-strategy unsafe-best-match", cwd=REPO)
    sh(f"{VENV}/bin/huggingface-cli download ByteDance/LatentSync-1.5 latentsync_unet.pt whisper/tiny.pt "
       f"--local-dir checkpoints", cwd=REPO)


def setup_wav2lip() -> None:
    sh(f"git clone -q --depth 1 https://github.com/Rudrabha/Wav2Lip {REPO}")
    (REPO / "temp").mkdir(exist_ok=True)
    uv = _venv()
    sh(f"{uv} 'setuptools<70' wheel")  # librosa 0.9 needs pkg_resources
    sh(f"{uv} torch==2.1.2 torchvision==0.16.2 --index-url https://download.pytorch.org/whl/cu121")
    sh(f"{uv} numpy==1.23.5 librosa==0.9.2 numba==0.58.1 scipy==1.10.1 opencv-python-headless==4.8.1.78 tqdm")
    for rel, urls in WEIGHTS.items():
        dest = REPO / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        for url in urls:
            if subprocess.run(["wget", "-q", "-O", str(dest), url]).returncode == 0 and dest.stat().st_size > 1_000_000:
                break
        else:
            raise RuntimeError(f"Could not download {rel}")


def setup() -> None:
    """The lip-sync model in its own Python 3.10 (Kaggle's Python is too new for its libraries)."""
    WORK.mkdir(parents=True, exist_ok=True)
    setup_latentsync() if ENGINE == "latentsync" else setup_wav2lip()


def get_moves() -> list[Path]:
    """The moves clips from the GitHub repo, as 720x1280 25 fps videos without sound."""
    MOVES.mkdir(parents=True, exist_ok=True)
    clips = []
    for k, name in enumerate(SETTINGS["moves"]):
        url = f"{SETTINGS['raw_base']}/{urllib.parse.quote(name)}"
        raw = MOVES / f"raw{k}.mp4"
        sh(f"wget -q -O {raw} '{url}'")
        clip = MOVES / f"m{k}.mp4"
        vf = ("scale=trunc(iw/2)*2:trunc(ih/2)*2" if SETTINGS.get("keep_size")  # spoken clips: keep 16:9 as it is
              else "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280")
        sh(f"ffmpeg -y -loglevel error -i {raw} -an -vf '{vf},fps={FPS},setsar=1' "
           f"-c:v libx264 -preset veryfast -crf 18 {clip}")
        clips.append(clip)
    return clips


def base_video(clips: list[Path], start: int, need: float, out: Path) -> None:
    """Moves clips one after another (starting at clip `start`) with short crossfades, at least `need` s long."""
    lengths = [duration(c) for c in clips]
    order, total = [], 0.0
    k = start
    while total < need + 0.5 or not order:
        order.append(k % len(clips))
        total += lengths[k % len(clips)] - (XFADE if len(order) > 1 else 0)
        k += 1
    if len(order) == 1:
        shutil.copy(clips[order[0]], out)
        return
    inputs = " ".join(f"-i {clips[i]}" for i in order)
    chain, last, t = [], "[0:v]", lengths[order[0]]
    for n in range(1, len(order)):
        label = f"[x{n}]"
        chain.append(f"{last}[{n}:v]xfade=transition=fade:duration={XFADE}:offset={t - XFADE:.3f}{label}")
        last, t = label, t + lengths[order[n]] - XFADE
    sh(f"ffmpeg -y -loglevel error {inputs} -filter_complex '{';'.join(chain)}' -map '{last}' "
       f"-c:v libx264 -preset veryfast -crf 18 -r {FPS} {out}")


def talk(job: dict, clips: list[Path]) -> Path:
    jd = WORK / job["id"]
    jd.mkdir(parents=True, exist_ok=True)
    mp3, wav = jd / "voice.mp3", jd / "voice.wav"
    mp3.write_bytes(base64.b64decode(job["audio"]))
    sh(f"ffmpeg -y -loglevel error -i {mp3} -ar 16000 -ac 1 {wav}")
    base = jd / "base.mp4"
    if job.get("only"):  # re-lip-sync one clip (from second `ss`) to new speech, e.g. the intro in the cloned voice
        seg = jd / "seg.mp4"
        sh(f"ffmpeg -y -loglevel error -ss {job.get('ss', 0)} -i {clips[job['start']]} -c:v libx264 -preset veryfast "
           f"-crf 18 {seg}")
        base_video([seg], 0, duration(wav), base)
    else:
        base_video(clips, job.get("start", 0), duration(wav), base)
    out = jd / "talk.mp4"
    if ENGINE == "latentsync":
        sh(f"{PY} -m scripts.inference --unet_config_path configs/unet/stage2.yaml "
           f"--inference_ckpt_path checkpoints/latentsync_unet.pt --inference_steps {SETTINGS.get('steps', 20)} "
           f"--guidance_scale {SETTINGS.get('guidance', 1.5)} --enable_deepcache --video_path {base} --audio_path {wav} --video_out_path {out}",
           cwd=REPO)
    else:
        sh(f"{PY} inference.py --checkpoint_path checkpoints/wav2lip_gan.pth --face {base} --audio {wav} "
           f"--outfile {out} --pads {SETTINGS['pads']} --face_det_batch_size 8 --wav2lip_batch_size 64", cwd=REPO)
    dest = OUT / f"{job['id']}.mp4"
    shutil.copy(out, dest)
    return dest


try:
    import torch

    RESULT["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none"
    print(f"GPU: {RESULT['gpu']}", flush=True)
    setup()
    clips = get_moves()
    RESULT["setup_seconds"] = round(time.time() - RESULT["started"])
    save_result()
    for job in JOBS:
        t = time.time()
        try:
            out = talk(job, clips)
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
