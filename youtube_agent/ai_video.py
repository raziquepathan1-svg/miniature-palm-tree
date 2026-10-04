"""Free AI makeover clips made on Kaggle's free GPU, so nobody has to make them by hand.

Each run of the workflow:
  1. If the last Kaggle run has finished, downloads its clips into rrs_inbox/<date>-<name>/ (one folder per
     makeover). The clips workflow (clips.py) then turns each makeover into a Short and, every few
     makeovers, into the long compilation - exactly as with clips uploaded by hand.
  2. If fewer than `buffer_days` Shorts are waiting (scheduled on YouTube, in the inbox or being made),
     plans new makeovers and starts a Kaggle run for them, without waiting for it to finish.

A makeover is an abandoned space (from the `makeover.spaces` list) restored in one of the `makeover.styles`,
told as a satisfying time-lapse in 3 clips: clean up -> build -> reveal. Kaggle runs kaggle_kernel.py, which
makes the clips with the open LTX-Video model; each clip continues from the last frame of the one before.

Needs the KAGGLE_USERNAME and KAGGLE_KEY secrets (free account, phone verified so it may use the GPU and
internet). Free GPU time is about 30 hours a week; one makeover takes roughly 10-30 minutes.

Usage (from the repo root; the workflow sets CHANNEL=restore_remake):
    CHANNEL=restore_remake python -m youtube_agent.ai_video                # collect + start a run
    CHANNEL=restore_remake python -m youtube_agent.ai_video --wait         # also wait and collect
    CHANNEL=restore_remake python -m youtube_agent.ai_video --plan-only    # just print the prompts
"""

import argparse
import base64
import datetime as dt
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from . import clips, makeover
from .main import CHANNEL_DIR, load_config, load_history, slugify, write_summary

HERE = Path(__file__).resolve().parent
STATE_FILE = CHANNEL_DIR / "ai_video.json"
KERNEL_TEMPLATE = HERE / "kaggle_kernel.py"

DEFAULTS = {
    "kernel_slug": "rrs-video-maker",
    "makeovers_per_run": 2,
    "buffer_days": 3,
    "max_wait_hours": 10,       # a Kaggle run still not finished after this is given up on
    "models": ["a-r-r-o-w/LTX-Video-0.9.1-diffusers", "Lightricks/LTX-Video"],
    "width": 512, "height": 768,  # vertical; multiples of 32
    "frames": 121,              # 8k+1 frames: about 5 s at 24 fps
    "fps": 24,
    "steps": 40,
    "guidance": 3.0,
    "max_tokens": 160,
    "negative_prompt": ("worst quality, low quality, blurry, jittery, distorted, warped walls, inconsistent motion, "
                        "morphing, flicker, text, watermark, logo, cartoon, deformed hands, faces"),
}

OUTDOOR = ("yard", "backyard", "rooftop", "terrace", "balcony", "front yard", "garden", "porch", "patio")


# ---------------------------------------------------------------- state
def load_state() -> dict:
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {"pending": None, "made": []}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def settings(config: dict) -> dict:
    return {**DEFAULTS, **(config.get("ai_video") or {})}


# ---------------------------------------------------------------- prompts
def _fill(text: str, style: dict) -> str:
    return text.format(style=style["name"], look=style["look"], palette=style["palette"])


def _abandoned(space: dict) -> str:
    before = re.sub(r",?\s*(daytime|nothing (else )?(in|on) the [a-z ]+|no furniture)\s*", " ", space["before"])
    before = re.sub(r"\b(a completely empty|an empty|a small empty|a bare,? ?|a completely bare)\s*", "a ",
                    before).strip(" ,")
    outdoor = any(w in space["short"] for w in OUTDOOR)
    mess = ("overgrown with weeds, dead leaves, trash and old junk, grimy cracked surfaces" if outdoor else
            "thick dust, cobwebs, peeling paint, trash and broken junk everywhere")
    return f"{before[0].upper()}{before[1:]}, abandoned for years: {mess}"


def plan_makeover(space: dict, style: dict, seed: int) -> dict:
    """Three time-lapse prompts that tell one makeover: clean up -> build -> reveal. Kept short: the video
    model reads only the first ~160 tokens."""
    works = [_fill(s["work"], style).split(",")[0] for s in space["stages"]]
    half = (len(works) + 1) // 2
    after = _fill(space["after_base"], style)
    cam = "Satisfying fast-motion time-lapse, static tripod wide shot."
    real = "Photorealistic, natural light, smooth realistic motion."
    prompts = [
        (f"{cam} {_abandoned(space)}. Workers in gloves, seen from behind, quickly haul out the junk, sweep the "
         f"dust and pressure wash the grime away, revealing clean surfaces. {real}"),
        (f"{cam} The same {space['short']}, now clean. Workers seen from behind work fast: "
         f"{'; '.join(works[:half])}. The space transforms step by step. {real}"),
        (f"{cam} The same {space['short']}: {'; '.join(works[half:])}. Then the workers leave and the camera "
         f"slowly pushes in on {after}, spotless and stunning, warm golden light. {real}"),
    ]
    name = f"Abandoned {space['short']} to {style['name']} {space['short']}"
    return {"id": f"{dt.datetime.now(dt.timezone.utc):%Y%m%d-%H%M}-{slugify(name)[:50]}",
            "name": name, "space": space["name"], "style": style["name"],
            "makeover_key": f"{space['name']}|{style['name']}", "seed": seed, "prompts": prompts}


def plan_jobs(config: dict, state: dict, n: int, rng: random.Random) -> list[dict]:
    done = list(state.get("made", []))
    jobs = []
    for _ in range(n):
        pick = makeover.pick_makeover(config["makeover"], done, rng)
        job = plan_makeover(pick["space"], pick["style"], rng.randrange(1, 2**31))
        job["id"] = f"{job['id']}-{len(jobs) + 1}"
        jobs.append(job)
        done.append({"makeover_key": job["makeover_key"], "space": job["space"]})
    return jobs


# ---------------------------------------------------------------- how many Shorts are waiting
def waiting_shorts(history: list[dict], state: dict) -> int:
    now = dt.datetime.now(dt.timezone.utc)
    scheduled = sum(1 for h in history if h.get("kind") == "clip_short" and h.get("publish_at")
                    and dt.datetime.fromisoformat(h["publish_at"].replace("Z", "+00:00")) > now)
    inbox = len(clips.inbox_groups(24))
    pending = len((state.get("pending") or {}).get("jobs", []))
    return scheduled + inbox + pending


# ---------------------------------------------------------------- Kaggle
def kaggle(*args: str, check: bool = True) -> str:
    r = subprocess.run(["kaggle", *args], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if check and r.returncode:
        raise RuntimeError(f"kaggle {' '.join(args[:2])} failed: {out[-1500:]}")
    return out


def kernel_id(s: dict) -> str:
    user = os.environ.get("KAGGLE_USERNAME", "").strip()
    if not user:
        raise SystemExit("KAGGLE_USERNAME is not set - add the KAGGLE_USERNAME and KAGGLE_KEY secrets.")
    return f"{user}/{s['kernel_slug']}"


def kernel_status(s: dict) -> str:
    """queued / running / complete / error / cancelled / unknown"""
    out = kaggle("kernels", "status", kernel_id(s), check=False)
    m = re.search(r'has status "?(?:KernelWorkerStatus\.)?(\w+)', out, re.I)
    word = m.group(1).lower() if m else ""
    if word.startswith("cancel"):
        return "cancelled"
    if word in ("complete", "error", "running", "queued"):
        return word
    print(f"  (Unexpected Kaggle status: {out[-300:]})")
    return "unknown"


def push_kernel(s: dict, jobs: list[dict]) -> None:
    b64 = lambda obj: base64.b64encode(json.dumps(obj).encode()).decode()  # noqa: E731
    keys = ("models", "width", "height", "frames", "fps", "steps", "guidance", "max_tokens", "negative_prompt")
    code = KERNEL_TEMPLATE.read_text().replace(
        "__JOBS__", b64([{k: j[k] for k in ("id", "seed", "prompts")} for j in jobs])).replace(
        "__SETTINGS__", b64({k: s[k] for k in keys}))
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "generate.py").write_text(code)
        (Path(d) / "kernel-metadata.json").write_text(json.dumps({
            "id": kernel_id(s), "title": s["kernel_slug"], "code_file": "generate.py", "language": "python",
            "kernel_type": "script", "is_private": True, "enable_gpu": True, "enable_internet": True,
            "dataset_sources": [], "competition_sources": [], "kernel_sources": [], "model_sources": []}))
        print(kaggle("kernels", "push", "-p", d))


def collect(s: dict, pending: dict) -> list[str]:
    """Downloads the finished run's clips into the inbox; returns the makeovers that came out whole."""
    got = []
    with tempfile.TemporaryDirectory() as d:
        print(kaggle("kernels", "output", kernel_id(s), "-p", d, check=False)[-1500:])
        result_file = next(Path(d).rglob("result.json"), None)
        result = json.loads(result_file.read_text()) if result_file else {"jobs": {}}
        for job in pending["jobs"]:
            res = result["jobs"].get(job["id"]) or {}
            if res.get("error"):
                print(f"  {job['name']}: Kaggle error\n{res['error']}")
            src = result_file.parent / job["id"] if result_file else None
            files = [src / c for c in res.get("clips", [])] if src else []
            files = [f for f in files if f.exists() and f.stat().st_size > 10_000]
            want = len(job["prompts"])
            if len(files) < want:
                print(f"  {job['name']}: only {len(files)} of {want} clips - skipped")
                continue
            dest = clips.INBOX / job["id"]
            dest.mkdir(parents=True, exist_ok=True)
            words = slugify(job["name"])
            for k, f in enumerate(files, 1):
                shutil.move(str(f), dest / f"{k}-{words}.mp4")
            got.append(job["name"])
    return got


# ---------------------------------------------------------------- one run
def run(wait: bool) -> None:
    config, history = load_config(), load_history()
    s = settings(config)
    state = load_state()
    report = ["## Restore Remake Studio - free AI clips (Kaggle)"]
    started = False

    while True:
        pending = state.get("pending")
        if pending:
            status = kernel_status(s)
            age_h = (time.time() - pending["started"]) / 3600
            print(f"Kaggle run from {age_h:.1f} h ago: {status}")
            if status in ("complete", "error", "cancelled") or age_h > s["max_wait_hours"]:
                got = collect(s, pending) if status != "cancelled" else []
                for job in pending["jobs"]:
                    if job["name"] in got:
                        state["made"].append({k: job[k] for k in ("id", "name", "space", "style", "makeover_key")})
                state["pending"] = None
                save_state(state)
                report.append(f"- Kaggle run {status}: {len(got)} of {len(pending['jobs'])} makeovers ready"
                              + (f" ({', '.join(got)})" if got else ""))
                if got and os.environ.get("GITHUB_OUTPUT"):
                    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                        f.write("new_clips=true\n")
                if started:
                    break
            elif wait:
                time.sleep(60)
                continue
            else:
                report.append(f"- Kaggle is still making {len(pending['jobs'])} makeovers ({status}).")
                break

        waiting = waiting_shorts(history, state)
        if waiting >= s["buffer_days"]:
            report.append(f"- {waiting} Shorts already waiting (target {s['buffer_days']}): nothing new started.")
            break
        rng = random.Random()
        jobs = plan_jobs(config, state, s["makeovers_per_run"], rng)
        print("Starting a Kaggle run for:\n" + "\n".join(f"  - {j['name']}" for j in jobs))
        push_kernel(s, jobs)
        state["pending"] = {"started": time.time(), "jobs": jobs}
        save_state(state)
        report.append(f"- Started a Kaggle run for: {', '.join(j['name'] for j in jobs)}")
        started = True
        if not wait:
            break
    print("\n".join(report))
    write_summary(report)


def main() -> None:
    parser = argparse.ArgumentParser(description="Free AI makeover clips made on Kaggle")
    parser.add_argument("--wait", action="store_true", help="Wait for the Kaggle run and collect its clips")
    parser.add_argument("--plan-only", action="store_true", help="Only print the prompts of the next makeovers")
    args = parser.parse_args()
    if args.plan_only:
        config = load_config()
        for job in plan_jobs(config, load_state(), settings(config)["makeovers_per_run"], random.Random()):
            print(f"\n=== {job['name']} ({job['id']})")
            for k, p in enumerate(job["prompts"], 1):
                print(f"{k}. {p}\n")
        return
    run(args.wait)


if __name__ == "__main__":
    main()
