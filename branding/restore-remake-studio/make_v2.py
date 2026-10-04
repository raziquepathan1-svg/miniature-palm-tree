"""Restore Remake Studio brand kit v2: logo, YouTube banner, Facebook cover and video watermark.

The look matches the channel's videos: abandoned places restored by a crew in safety-yellow shirts.
The banner and cover use real before/after frames from the channel's own makeovers.

    python3 make_v2.py FRAMES_DIR OUT_DIR
FRAMES_DIR holds <name>_before.jpg / <name>_after.jpg (first and last frame of a makeover clip).
"""

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
POPPINS = Path.home() / ".cache" / "yt-agent-fonts" / "Poppins-800.ttf"

CHAR = (20, 22, 26)
CHAR2 = (38, 42, 48)
SAFETY = (214, 245, 50)      # the crew's safety-yellow shirts
TEAL = (13, 148, 136)
TEAL_DARK = (8, 96, 90)
GOLD = (245, 158, 11)
WARM = (255, 214, 120)
WHITE = (255, 255, 255)
GREY = (120, 118, 112)
GREY_DARK = (78, 76, 72)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    if name == "anton":
        return ImageFont.truetype(str(FONTS / "Anton-Regular.ttf"), size)
    if name == "poppins" and POPPINS.exists():
        return ImageFont.truetype(str(POPPINS), size)
    f = ImageFont.truetype(str(FONTS / "Montserrat.ttf"), size)
    try:
        f.set_variation_by_name("ExtraBold")
    except Exception:
        pass
    return f


# ---------------------------------------------------------------- the icon
def house_icon(size: int) -> Image.Image:
    """A house split on the diagonal: left half weathered and boarded up, right half restored and lit."""
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    roof = [(0.12 * s, 0.50 * s), (0.50 * s, 0.14 * s), (0.88 * s, 0.50 * s)]
    body = (0.20 * s, 0.46 * s, 0.80 * s, 0.88 * s)
    chimney = (0.64 * s, 0.20 * s, 0.73 * s, 0.38 * s)

    def shape(fill_roof, fill_body, fill_chimney) -> Image.Image:
        layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.rectangle(chimney, fill=fill_chimney)
        d.polygon(roof, fill=fill_roof)
        d.rectangle(body, fill=fill_body)
        return layer

    before = shape(GREY_DARK, GREY, GREY_DARK)
    db = ImageDraw.Draw(before)
    # boarded-up window and cracks
    win = (0.29 * s, 0.56 * s, 0.45 * s, 0.70 * s)
    db.rectangle(win, fill=(30, 30, 30))
    for k in (0.59, 0.66):
        db.line([(win[0] - 0.02 * s, k * s), (win[2] + 0.02 * s, (k + 0.02) * s)], fill=(150, 112, 70), width=int(0.025 * s))
    db.line([(0.24 * s, 0.50 * s), (0.30 * s, 0.53 * s), (0.27 * s, 0.57 * s)], fill=(50, 50, 50), width=int(0.012 * s))
    db.line([(0.36 * s, 0.30 * s), (0.40 * s, 0.36 * s), (0.37 * s, 0.41 * s)], fill=(50, 50, 50), width=int(0.012 * s))

    after = shape(TEAL_DARK, TEAL, TEAL_DARK)
    da = ImageDraw.Draw(after)
    win2 = (0.57 * s, 0.52 * s, 0.73 * s, 0.65 * s)
    glow = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rectangle(win2, fill=(*WARM, 200))
    after.alpha_composite(glow.filter(ImageFilter.GaussianBlur(0.03 * s)))
    da.rectangle(win2, fill=WARM)
    da.line([((win2[0] + win2[2]) / 2, win2[1]), ((win2[0] + win2[2]) / 2, win2[3])], fill=TEAL_DARK, width=int(0.012 * s))
    da.line([(win2[0], (win2[1] + win2[3]) / 2), (win2[2], (win2[1] + win2[3]) / 2)], fill=TEAL_DARK, width=int(0.012 * s))
    door = (0.61 * s, 0.70 * s, 0.73 * s, 0.88 * s)
    da.rounded_rectangle(door, radius=int(0.05 * s), fill=GOLD)

    # diagonal split: after on the upper right
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).polygon([(0.30 * s, 0), (s, 0), (s, s), (0.70 * s, s)], fill=255)
    img.alpha_composite(before)
    img.paste(after, (0, 0), Image.composite(after.getchannel("A"), Image.new("L", (s, s), 0), mask))
    # the split line, only inside the house
    line = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(line).line([(0.30 * s, 0), (0.70 * s, s)], fill=SAFETY, width=int(0.024 * s))
    house_alpha = before.getchannel("A")
    img.paste(line, (0, 0), Image.composite(line.getchannel("A"), Image.new("L", (s, s), 0), house_alpha))
    d = ImageDraw.Draw(img)
    # sparkle on the restored side
    star(d, 0.83 * s, 0.24 * s, 0.075 * s, WHITE)
    star(d, 0.92 * s, 0.38 * s, 0.035 * s, WHITE)
    return img


def star(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float, color) -> None:
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.28
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=color)


def logo(size: int = 800) -> Image.Image:
    """Round badge: charcoal, safety-yellow ring, the split house."""
    S = size * 2
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    g = ImageDraw.Draw(bg)
    for r in range(S // 2, 0, -4):  # soft radial gradient
        t = r / (S / 2)
        c = tuple(int(CHAR2[i] * (1 - t) + CHAR[i] * t) for i in range(3))
        g.ellipse((S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r), fill=(*c, 255))
    img.alpha_composite(bg)
    d = ImageDraw.Draw(img)
    ring = int(S * 0.045)
    d.ellipse((ring / 2, ring / 2, S - ring / 2, S - ring / 2), outline=SAFETY, width=ring)
    d.ellipse((ring * 1.6, ring * 1.6, S - ring * 1.6, S - ring * 1.6), outline=(*WHITE, 60), width=max(2, ring // 8))
    icon = house_icon(int(S * 0.74))
    img.alpha_composite(icon, (int(S * 0.13), int(S * 0.03)))
    # name plate under the house
    f = font("anton", int(S * 0.115))
    text = "RESTORE"
    tw = d.textlength(text, font=f)
    y = S * 0.705
    d.rounded_rectangle((S / 2 - tw / 2 - S * 0.045, y, S / 2 + tw / 2 + S * 0.045, y + S * 0.145),
                        radius=int(S * 0.03), fill=SAFETY, outline=CHAR, width=int(S * 0.01))
    d.text((S / 2 - tw / 2, y + S * 0.002), text, font=f, fill=CHAR)
    return img.resize((size, size), Image.LANCZOS)


def watermark(size: int = 300) -> Image.Image:
    """YouTube video watermark: the badge, slightly transparent so it doesn't distract."""
    w = logo(size)
    a = w.getchannel("A").point(lambda v: int(v * 0.92))
    w.putalpha(a)
    return w


# ---------------------------------------------------------------- banner / cover
def cover_crop(img: Image.Image, w: int, h: int) -> Image.Image:
    r = max(w / img.width, h / img.height)
    im = img.resize((int(img.width * r + 1), int(img.height * r + 1)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def ba_card(before: Image.Image, after: Image.Image, h: int) -> Image.Image:
    """Two vertical frames side by side with BEFORE / AFTER tags and an arrow between."""
    fw = int(h * 9 / 16)
    gap = int(h * 0.06)
    W = fw * 2 + gap
    card = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    for k, (im, label, col) in enumerate(((before, "BEFORE", GREY_DARK), (after, "AFTER", TEAL))):
        ph = cover_crop(im.convert("RGB"), fw, h)
        if k == 0:
            ph = ImageEnhance.Color(ph).enhance(0.55)
        else:
            ph = ImageEnhance.Contrast(ImageEnhance.Color(ph).enhance(1.2)).enhance(1.06)
        m = Image.new("L", (fw, h), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, fw, h), radius=int(h * 0.05), fill=255)
        card.paste(ph, (k * (fw + gap), 0), m)
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((k * (fw + gap), 0, k * (fw + gap) + fw - 1, h - 1), radius=int(h * 0.05),
                            outline=SAFETY if k else (200, 200, 200), width=max(3, h // 90))
        f = font("anton", int(h * 0.075))
        tw = d.textlength(label, font=f)
        x = k * (fw + gap) + (fw - tw) / 2
        d.rounded_rectangle((x - h * 0.03, h * 0.04, x + tw + h * 0.03, h * 0.04 + h * 0.105), radius=int(h * 0.03),
                            fill=col)
        d.text((x, h * 0.045), label, font=f, fill=WHITE)
    # arrow between
    d = ImageDraw.Draw(card)
    cx, cy, r = fw + gap / 2, h / 2, gap * 0.95
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=SAFETY, outline=CHAR, width=max(3, h // 120))
    a = r * 0.55
    d.polygon([(cx - a * 0.7, cy - a * 0.25), (cx + a * 0.05, cy - a * 0.25), (cx + a * 0.05, cy - a * 0.6),
               (cx + a * 0.8, cy), (cx + a * 0.05, cy + a * 0.6), (cx + a * 0.05, cy + a * 0.25),
               (cx - a * 0.7, cy + a * 0.25)], fill=CHAR)
    return card


def background(afters: list[Image.Image], w: int, h: int) -> Image.Image:
    """Blurred, darkened collage of finished makeovers."""
    n = len(afters)
    bg = Image.new("RGB", (w, h), CHAR)
    cw = w // n + 1
    for i, im in enumerate(afters):
        bg.paste(cover_crop(im.convert("RGB"), cw, h), (i * cw, 0))
    bg = bg.filter(ImageFilter.GaussianBlur(max(w, h) // 90))
    bg = ImageEnhance.Brightness(bg).enhance(0.38)
    shade = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for x in range(w):  # darker in the middle where the text sits
        t = 1 - abs(x - w / 2) / (w / 2)
        sd.line([(x, 0), (x, h)], fill=(*CHAR, int(150 * t ** 1.5)))
    out = bg.convert("RGBA")
    out.alpha_composite(shade)
    return out


def title_block(w: int, h: int, scale: float, with_logo: bool = True) -> Image.Image:
    """Logo + RESTORE REMAKE / STUDIO + tagline, sized to fit w x h."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lg = logo(int(h * 0.92)) if with_logo else Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    f1 = font("anton", int(150 * scale))
    f2 = font("anton", int(70 * scale))
    f3 = font("poppins", int(40 * scale))
    l1, l2 = "RESTORE REMAKE", "STUDIO"
    tag = "ABANDONED  ->  AMAZING"
    w1 = d.textlength(l1, font=f1)
    total = lg.width + 50 * scale + w1
    x0 = (w - total) / 2
    img.alpha_composite(lg, (int(x0), int((h - lg.height) / 2)))
    tx = x0 + lg.width + 50 * scale
    y = h / 2 - 150 * scale
    d.text((tx + 6 * scale, y + 6 * scale), l1, font=f1, fill=(0, 0, 0, 160))
    d.text((tx, y), l1, font=f1, fill=WHITE)
    y2 = y + 165 * scale
    d.text((tx, y2), l2, font=f2, fill=SAFETY)
    sw = d.textlength(l2, font=f2)
    # tagline pill with a drawn arrow
    parts = ("ABANDONED", "AMAZING")
    pw = d.textlength(parts[0], font=f3) + d.textlength(parts[1], font=f3) + 120 * scale
    px = tx + sw + 34 * scale
    py = y2 + 10 * scale
    ph = 64 * scale
    if px + pw > w:
        px, py = tx, y2 + 95 * scale
    d.rounded_rectangle((px, py, px + pw + 40 * scale, py + ph), radius=int(ph / 2), fill=TEAL)
    d.text((px + 20 * scale, py + 8 * scale), parts[0], font=f3, fill=WHITE)
    ax = px + 20 * scale + d.textlength(parts[0], font=f3) + 22 * scale
    ay = py + ph / 2
    a = 22 * scale
    d.polygon([(ax, ay - a * 0.3), (ax + a * 1.4, ay - a * 0.3), (ax + a * 1.4, ay - a * 0.75), (ax + a * 2.4, ay),
               (ax + a * 1.4, ay + a * 0.75), (ax + a * 1.4, ay + a * 0.3), (ax, ay + a * 0.3)], fill=SAFETY)
    d.text((ax + a * 2.4 + 22 * scale, py + 8 * scale), parts[1], font=f3, fill=WHITE)
    f4 = font("poppins", int(34 * scale))
    sub = "A new satisfying makeover every day"
    d.text((tx, y2 + 105 * scale if py < y2 + 60 * scale else py + ph + 18 * scale), sub, font=f4,
           fill=(225, 225, 225))
    del tag
    return img


def banner(frames: dict, out: Path) -> None:
    """YouTube banner 2560x1440. Everything important sits in the 1546x423 safe area; the before/after cards
    fill the band that desktop viewers see (2560x423)."""
    W, H = 2560, 1440
    img = background([frames[k][1] for k in frames], W, H)
    band_y, band_h = (H - 423) // 2, 423
    cards = list(frames.items())
    left = ba_card(*cards[0][1], int(band_h * 0.9))
    right = ba_card(*cards[1 % len(cards)][1], int(band_h * 0.9))
    img.alpha_composite(left, (40, band_y + (band_h - left.height) // 2))
    img.alpha_composite(right, (W - right.width - 40, band_y + (band_h - right.height) // 2))
    blk = title_block(1500, 400, 1.0)
    img.alpha_composite(blk, ((W - 1500) // 2, band_y + 12))
    img.convert("RGB").save(out, "PNG", optimize=True)


def fb_cover(frames: dict, out: Path) -> None:
    """Facebook cover 1640x624 (phones crop the sides, so the title stays in the middle)."""
    W, H = 1640, 624
    img = background([frames[k][1] for k in frames], W, H)
    cards = list(frames.items())
    ch = int(H * 0.66)
    left = ba_card(*cards[2 % len(cards)][1], ch)
    right = ba_card(*cards[3 % len(cards)][1], ch)
    img.alpha_composite(left, (28, (H - ch) // 2))
    img.alpha_composite(right, (W - right.width - 28, (H - ch) // 2))
    bw = W - left.width - right.width - 90
    # the Page's profile picture already shows the logo, so the title stands alone and is sized to fit
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    scale = min(0.62, (bw - 20) / (probe.textlength("RESTORE REMAKE", font=font("anton", 150)) + 50))
    blk = title_block(bw, int(420 * scale), scale, with_logo=False)
    img.alpha_composite(blk, ((W - bw) // 2, (H - blk.height) // 2))
    img.convert("RGB").save(out, "PNG", optimize=True)


def main() -> None:
    frames_dir, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    order = ["rooftop", "gym", "backyard", "bedroom"]
    frames = {k: (Image.open(frames_dir / f"{k}_before.jpg"), Image.open(frames_dir / f"{k}_after.jpg"))
              for k in order if (frames_dir / f"{k}_before.jpg").exists()}
    logo(800).save(out / "logo.png")
    logo(800).convert("RGB").save(out / "logo_square.jpg", quality=95)  # for apps that don't like transparency
    watermark(300).save(out / "watermark.png")
    banner(frames, out / "banner.png")
    fb_cover(frames, out / "fb_cover.png")
    print("Saved to", out)


if __name__ == "__main__":
    main()
