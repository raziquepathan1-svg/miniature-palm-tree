# Runs on a free Kaggle GPU (pushed there by .github/workflows/kaggle-video-test.yml).
# Makes short vertical AI video clips with the open Wan 2.1 text-to-video model (Apache-2.0).
# PROMPTS_JSON is replaced by the workflow with the list of prompts to make.
import json
import subprocess
import sys
import time

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers>=0.33", "transformers", "accelerate",
                "ftfy", "imageio[ffmpeg]"], check=True)

import torch  # noqa: E402
from diffusers import AutoencoderKLWan, WanPipeline  # noqa: E402
from diffusers.utils import export_to_video  # noqa: E402

PROMPTS = json.loads(r"""PROMPTS_JSON""")
MODEL = "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
NEGATIVE = ("blurry, low quality, distorted, deformed hands, extra limbs, text, watermark, logo, cartoon, "
            "static image, camera shake, jump cut")

t0 = time.time()
vae = AutoencoderKLWan.from_pretrained(MODEL, subfolder="vae", torch_dtype=torch.float32)
pipe = WanPipeline.from_pretrained(MODEL, vae=vae, torch_dtype=torch.float16)
pipe.enable_model_cpu_offload()
print(f"Model loaded in {time.time() - t0:.0f} s", flush=True)

for i, prompt in enumerate(PROMPTS, 1):
    t = time.time()
    frames = pipe(prompt=prompt, negative_prompt=NEGATIVE, height=832, width=480, num_frames=81,
                  num_inference_steps=30, guidance_scale=5.0,
                  generator=torch.Generator("cpu").manual_seed(1000 + i)).frames[0]
    export_to_video(frames, f"/kaggle/working/clip_{i}.mp4", fps=16)
    print(f"Clip {i}/{len(PROMPTS)} done in {time.time() - t:.0f} s", flush=True)
print(f"All done in {time.time() - t0:.0f} s")
