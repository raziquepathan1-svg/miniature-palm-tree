"""Instagram + Facebook profile pictures and Facebook cover, same look as the approved YouTube logo/banner."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "heart"))
import render as R
OUT = Path(__file__).resolve().parent.parent / "social"
HERE = Path(__file__).resolve().parent
GOLD = (247, 190, 70); WHITE = (255, 255, 255); SOFT = (196, 210, 232)
F = lambda size, w=800: R.visuals.font(size, w)
src = Image.open(HERE / "ai" / "heart_ai.png").convert("RGB")
bgcol = tuple(int(v) for v in np.array(src)[5:40, 5:40].reshape(-1, 3).mean(0))

# profile picture 1080x1080 (Instagram & Facebook show it as a circle): heart fills the circle, gold ring, solid background
S = 1080
sq = src.crop((270, 0, 990, 720)).resize((S, S), Image.LANCZOS)
pp = Image.new("RGB", (S, S), bgcol)
h = sq.resize((int(S * 0.86), int(S * 0.86)), Image.LANCZOS)
pp.paste(h, ((S - h.width) // 2, (S - h.height) // 2 + 14))
ImageDraw.Draw(pp).ellipse((14, 14, S - 14, S - 14), outline=GOLD, width=22)
pp.save(OUT / "profile_picture_1080.png")
prev = pp.copy(); m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse((0, 0, S, S), fill=255)
circ = Image.new("RGB", (S, S), (255, 255, 255)); circ.paste(pp, (0, 0), m); circ.resize((400, 400)).save(OUT / "_preview_circle.png")

# Facebook cover 1640x624 (desktop 820x312 @2x). Phones crop the sides, so everything sits in the middle 1100 px.
W, H = 1640, 624
y, x = np.mgrid[0:H, 0:W]
r = np.clip(np.sqrt(((x - W * 0.45) / W) ** 2 + ((y - H * 0.5) / H) ** 2) / 0.75, 0, 1)[..., None]
b = Image.fromarray((np.array([24, 52, 110]) * (1 - r) + np.array(bgcol) * 0.8 * r).astype("uint8"), "RGB").convert("RGBA")
ecg = Image.new("RGBA", (W, H), (0, 0, 0, 0)); e = ImageDraw.Draw(ecg)
base = H // 2 + 120; pts = []; px = 0
while px < W:
    for dx, dy in ((0, 0), (100, 0), (120, -14), (140, 0), (175, 0), (188, 20), (205, -150), (222, 46), (235, 0), (280, 0), (305, -26), (335, 0)):
        pts.append((px + dx, base + dy))
    px += 350
e.line(pts, fill=GOLD + (60,), width=4, joint="curve")
b.alpha_composite(ecg)
hh = src.crop((300, 0, 960, 720)).resize((int(660 * 0.52), int(720 * 0.52)), Image.LANCZOS).convert("RGBA")
fm = Image.new("L", hh.size, 0)
ImageDraw.Draw(fm).ellipse((hh.width * 0.06, -hh.height * 0.12, hh.width * 0.94, hh.height * 0.97), fill=255)
hh.putalpha(fm.filter(ImageFilter.GaussianBlur(24)))
x0 = 285
b.alpha_composite(hh, (x0, (H - hh.height) // 2))
d = ImageDraw.Draw(b)
tx, ty = x0 + hh.width + 10, 160
d.text((tx, ty), "THE ANATOMY", font=F(78, 800), fill=WHITE)
d.text((tx, ty + 84), "UNFOLDED", font=F(78, 800), fill=GOLD)
d.text((tx, ty + 190), "How your body works, and what happens in disease", font=F(24, 500), fill=SOFT)
px = tx
for tag in ("Anatomy", "Physiology", "Diseases", "New videos daily"):
    tw = d.textlength(tag, font=F(20, 500))
    d.rounded_rectangle((px, ty + 235, px + tw + 28, ty + 273), radius=21, outline=GOLD, width=3)
    d.text((px + 14, ty + 254), tag, font=F(20, 500), fill=WHITE, anchor="lm")
    px += tw + 38
b = b.convert("RGB"); b.save(OUT / "facebook_cover_1640x624.png")
p = b.copy(); dd = ImageDraw.Draw(p)
mx = (W - int(H * 640 / 360)) // 2
dd.rectangle((mx, 0, W - mx, H - 1), outline=(255, 0, 0), width=4)   # what phones show
p.resize((820, 312)).save(OUT / "_preview_cover_phone_area.png")
print("text right edge", px, "phone area", mx, W - mx)
