"""Video editing with ffmpeg: intro/outro, background music, and a thumbnail."""

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FPS = 30


def ffmpeg_bin() -> str:
    exe = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise RuntimeError("ffmpeg not found. Install it (e.g. `sudo apt install ffmpeg`).")


def _run(args: list[str]) -> subprocess.CompletedProcess:
    proc = subprocess.run([ffmpeg_bin(), "-hide_banner", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{proc.stderr[-3000:]}")
    return proc


def _has_audio(path: Path) -> bool:
    proc = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    return "Audio:" in proc.stderr


def _resolve(base: Path, rel: str | None) -> Path | None:
    if not rel:
        return None
    p = base / rel
    return p if p.exists() else None


def edit_video(main_video: Path, editing: dict, video: dict, base_dir: Path, out_path: Path) -> Path:
    """Add intro/outro clips and background music (each only if its file exists)."""
    intro = _resolve(base_dir, editing.get("intro_clip"))
    outro = _resolve(base_dir, editing.get("outro_clip"))
    music = _resolve(base_dir, editing.get("background_music"))

    if not (intro or outro or music):
        shutil.copyfile(main_video, out_path)
        return out_path

    w, h = (720, 1280) if video.get("format") == "shorts" else (1280, 720)
    clips = [c for c in (intro, main_video, outro) if c]

    inputs: list[str] = []
    filters: list[str] = []
    for i, clip in enumerate(clips):
        inputs += ["-i", str(clip)]
        filters.append(
            f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS},format=yuv420p[v{i}]"
        )
        if _has_audio(clip):
            filters.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}]")
        else:  # silent clip: generate silence matching its length
            filters.append(f"aevalsrc=0:s=48000:c=stereo:d={_duration(clip)}[a{i}]")
    n = len(clips)
    filters.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vout][aout]")

    audio_label = "aout"
    if music:
        inputs += ["-stream_loop", "-1", "-i", str(music)]
        vol = editing.get("music_volume", 0.08)
        filters.append(f"[{n}:a]volume={vol},aresample=48000,aformat=channel_layouts=stereo[music]")
        filters.append("[aout][music]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[amixed]")
        audio_label = "amixed"

    _run([
        "-y", *inputs,
        "-filter_complex", ";".join(filters),
        "-map", "[vout]", "-map", f"[{audio_label}]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        str(out_path),
    ])
    return out_path


def _duration(path: Path) -> float:
    proc = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    for line in proc.stderr.splitlines():
        line = line.strip()
        if line.startswith("Duration:"):
            hms = line.split(",")[0].split("Duration:")[1].strip()
            hh, mm, ss = hms.split(":")
            return int(hh) * 3600 + int(mm) * 60 + float(ss)
    raise RuntimeError(f"Could not read duration of {path}")


def make_thumbnail(video_path: Path, text: str, out_path: Path, shorts: bool = False) -> Path:
    """Grab a frame of the avatar and put big bold text on it (1280x720 JPG)."""
    frame = out_path.with_suffix(".frame.png")
    _run(["-y", "-ss", "3", "-i", str(video_path), "-frames:v", "1", str(frame)])

    img = Image.open(frame).convert("RGB")
    size = (720, 1280) if shorts else (1280, 720)
    img = _cover(img, size)

    # Darken the left side so the text pops
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw_o = ImageDraw.Draw(overlay)
    for x in range(size[0]):
        alpha = int(200 * max(0.0, 1 - x / (size[0] * 0.75)))
        draw_o.line([(x, 0), (x, size[1])], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(img)
    font = _font(96 if not shorts else 88)
    lines = textwrap.wrap(text.upper(), width=12)[:4]
    y = (size[1] - len(lines) * 110) // 2
    for line in lines:
        draw.text((50, y), line, font=font, fill="#FFD400", stroke_width=6, stroke_fill="black")
        y += 110
    img.save(out_path, "JPEG", quality=90)
    frame.unlink(missing_ok=True)
    return out_path


def _cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    scale = max(size[0] / img.width, size[1] / img.height)
    img = img.resize((int(img.width * scale) + 1, int(img.height * scale) + 1))
    left, top = (img.width - size[0]) // 2, (img.height - size[1]) // 2
    return img.crop((left, top, left + size[0], top + size[1]))


def _font(size: int) -> ImageFont.ImageFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)
