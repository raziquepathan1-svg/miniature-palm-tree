"""Runs on Kaggle's free GPU (pushed there by ai_video.py; not run on GitHub).

Makes the AI video clips of each makeover with the open LTX-Video model. The first clip is made from the
text prompt; every next clip starts from the last frame of the one before, so all clips of a makeover show
the same place. Clips and result.json are written to /kaggle/working, where ai_video.py downloads them.

__JOBS__ and __SETTINGS__ are filled in by ai_video.py (base64 JSON).
"""

import base64
import gc
import json
import subprocess
import sys
import time
import traceback
from pathlib import Path

JOBS = json.loads(base64.b64decode("__JOBS__"))
SETTINGS = json.loads(base64.b64decode("__SETTINGS__"))
OUT = Path("/kaggle/working")
RESULT = {"jobs": {}, "started": time.time(), "settings": SETTINGS}


def save_result() -> None:
    (OUT / "result.json").write_text(json.dumps(RESULT, indent=2))


subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers>=0.32", "accelerate", "sentencepiece",
                "imageio", "imageio-ffmpeg"], check=True)

import numpy as np  # noqa: E402
import torch  # noqa: E402
from diffusers import LTXImageToVideoPipeline, LTXPipeline  # noqa: E402
from diffusers.utils import export_to_video  # noqa: E402

# bf16 only where the GPU does it natively (Ampere and newer); Kaggle's P100/T4 run float32, which fits
# the 2B video model in 16 GB and never gives black (NaN) frames like float16 can.
dtype = torch.bfloat16 if torch.cuda.get_device_capability()[0] >= 8 else torch.float32
RESULT["gpu"] = torch.cuda.get_device_name(0)
RESULT["dtype"] = str(dtype)
print(f"GPU: {RESULT['gpu']}, {dtype}", flush=True)


def load(cls, **kw):
    """The first model in SETTINGS['models'] that loads."""
    last = None
    for model in SETTINGS["models"]:
        try:
            pipe = cls.from_pretrained(model, **kw)
            RESULT["model"] = model
            return pipe
        except Exception as e:  # wrong repo layout / not available: try the next one
            print(f"Could not load {model}: {e}", flush=True)
            last = e
    raise RuntimeError(f"No video model could be loaded: {last}")


# 1) All prompts encoded first, on the CPU (the T5 text encoder is too big for the GPU next to the video
#    model and unstable in float16), then the encoder is freed.
enc = load(LTXPipeline, transformer=None, vae=None, scheduler=None, torch_dtype=torch.bfloat16)
neg = SETTINGS["negative_prompt"]
embeds = {}
for job in JOBS:
    for k, prompt in enumerate(job["prompts"]):
        with torch.no_grad():
            pe, pm, ne, nm = enc.encode_prompt(prompt=prompt, negative_prompt=neg, do_classifier_free_guidance=True,
                                               max_sequence_length=SETTINGS["max_tokens"], device="cpu",
                                               dtype=torch.bfloat16)
        embeds[(job["id"], k)] = (pe, pm, ne, nm)
del enc
gc.collect()
print("Prompts encoded", flush=True)

# 2) The video model on the GPU.
pipe = load(LTXPipeline, text_encoder=None, tokenizer=None, torch_dtype=dtype).to("cuda")
pipe.vae.enable_tiling()
i2v = LTXImageToVideoPipeline(**pipe.components)


def make_clip(job_id: str, k: int, image, seed: int):
    pe, pm, ne, nm = embeds[(job_id, k)]
    args = dict(prompt_embeds=pe.to("cuda", dtype), prompt_attention_mask=pm.to("cuda"),
                negative_prompt_embeds=ne.to("cuda", dtype), negative_prompt_attention_mask=nm.to("cuda"),
                width=SETTINGS["width"], height=SETTINGS["height"], num_frames=SETTINGS["frames"],
                num_inference_steps=SETTINGS["steps"], guidance_scale=SETTINGS["guidance"],
                decode_timestep=0.03, decode_noise_scale=0.025,
                generator=torch.Generator("cuda").manual_seed(seed))
    with torch.no_grad():
        if image is None:
            return pipe(**args).frames[0]
        return i2v(image=image, **args).frames[0]


for job in JOBS:
    folder = OUT / job["id"]
    folder.mkdir(parents=True, exist_ok=True)
    res = RESULT["jobs"][job["id"]] = {"clips": [], "error": None}
    image = None
    try:
        for k in range(len(job["prompts"])):
            t = time.time()
            frames = make_clip(job["id"], k, image, job["seed"] + k)
            if float(np.asarray(frames[len(frames) // 2]).mean()) < 4:
                raise RuntimeError(f"clip {k + 1} came out black")
            name = f"{k + 1}.mp4"
            export_to_video(frames, str(folder / name), fps=SETTINGS["fps"])
            image = frames[-1]
            res["clips"].append(name)
            print(f"{job['id']} clip {k + 1}/{len(job['prompts'])} in {time.time() - t:.0f} s", flush=True)
            save_result()
    except Exception:
        res["error"] = traceback.format_exc()[-2000:]
        print(res["error"], flush=True)
    torch.cuda.empty_cache()
    save_result()

RESULT["finished"] = time.time()
save_result()
print("Done", flush=True)
