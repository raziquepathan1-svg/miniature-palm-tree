import math, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = Path(__file__).resolve().parent
exec(open(HERE / "thumb.py").read().split("y, x = np.mgrid")[0])   # reuse: builds `heart` (wired heart with halo)
W2, H2 = 1280, 720
F = lambda s, w=800: R.visuals.font(s, w)
def navy(cx=0.3):
    y, x = np.mgrid[0:H2, 0:W2]
    r = np.clip(np.sqrt(((x - W2 * cx) / W2) ** 2 + ((y - H2 * 0.5) / H2) ** 2) / 0.8, 0, 1)[..., None]
    return Image.fromarray((np.array(NAVY1) * (1 - r) + np.array(NAVY0) * r).astype("uint8"), "RGB").convert("RGBA")
WAVE = []
for i in range(201):
    x = i / 200; y = 0.0
    if 0.08 <= x <= 0.18: y = -0.13 * math.sin(math.pi * (x - 0.08) / 0.10)
    elif 0.26 <= x <= 0.28: y = 0.10 * (x - 0.26) / 0.02
    elif 0.28 < x <= 0.31: y = 0.10 - 1.10 * (x - 0.28) / 0.03
    elif 0.31 < x <= 0.34: y = -1.0 + 1.28 * (x - 0.31) / 0.03
    elif 0.34 < x <= 0.37: y = 0.28 - 0.28 * (x - 0.34) / 0.03
    elif 0.50 <= x <= 0.70: y = -0.26 * math.sin(math.pi * (x - 0.50) / 0.20)
    WAVE.append((x, y))

# ---- B: curiosity - "WHO STARTS YOUR HEARTBEAT?" with the SA node circled
t = navy(0.28)
h = heart.copy(); h.thumbnail((560, 700), Image.LANCZOS)
hx, hy = -6, (H2 - h.height) // 2 + 10
t.alpha_composite(h, (hx, hy))
d = ImageDraw.Draw(t)
sc = h.width / heart.width
sax = hx + ((598 + LA.DX) * SS - (520 + LA.DX) * SS) * sc
say = hy + (462 * SS - 30 * SS) * sc
for r_, w_, c_ in ((62, 12, (255, 60, 60)),):
    d.ellipse((sax - r_, say - r_, sax + r_, say + r_), outline=c_, width=w_)
d.line([(sax + 70, say - 40), (600, 175)], fill=(255, 60, 60), width=10)
d.polygon([(sax + 62, say - 30), (sax + 98, say - 38), (sax + 80, say - 64)], fill=(255, 60, 60))
d.text((620, 110), "WHO STARTS", font=F(96), fill=(255, 255, 255))
d.text((620, 220), "YOUR", font=F(96), fill=(255, 255, 255))
d.text((620, 330), "HEARTBEAT?", font=F(88), fill=GOLD)
d.rounded_rectangle((626, 490, 1150, 570), radius=40, fill=(255, 60, 60))
d.text((888, 530), "It's not your brain!", font=F(40, 700), fill=(255, 255, 255), anchor="mm")
t.convert("RGB").save(HERE / "thumb_B.png")

# ---- C: search-friendly - "ECG EXPLAINED" with a big labelled wave
t = navy(0.5)
d = ImageDraw.Draw(t)
X0, X1, Y0, A = 60, 1220, 560, 250
for gx in range(X0, X1 + 1, 40):
    d.line([(gx, 170), (gx, 640)], fill=(40, 70, 130), width=1)
for gy in range(170, 641, 40):
    d.line([(X0, gy), (X1, gy)], fill=(40, 70, 130), width=1)
pts = [(X0 + x * (X1 - X0), Y0 + y * A) for x, y in WAVE]
glow = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); ImageDraw.Draw(glow).line(pts, fill=(255, 210, 80, 255), width=22, joint="curve")
t.alpha_composite(glow.filter(ImageFilter.GaussianBlur(12)))
d = ImageDraw.Draw(t)
d.line(pts, fill=(255, 226, 120), width=9, joint="curve")
for lab, xx, col in (("P", 0.13, (120, 180, 255)), ("QRS", 0.31, (255, 90, 90)), ("T", 0.60, (120, 230, 170))):
    yy = Y0 + min(y for x, y in WAVE if abs(x - xx) < 0.03) * A - 22
    d.text((X0 + xx * (X1 - X0), yy), lab, font=F(64), fill=col, anchor="mb")
d.text((640, 30), "ECG EXPLAINED", font=F(110), fill=(255, 255, 255), anchor="ma")
d.rounded_rectangle((870, 560, 1240, 640), radius=40, fill=GOLD)
d.text((1055, 600), "in 3 minutes", font=F(40, 700), fill=(20, 30, 60), anchor="mm")
t.convert("RGB").save(HERE / "thumb_C.png")
print("ok")
