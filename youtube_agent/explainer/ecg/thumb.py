import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "heart"))
import lineart as LA
import render as R
from render import SS, H
W2, H2 = 1280, 720
NAVY0, NAVY1 = (9, 22, 48), (24, 52, 110)
GOLD = (247, 190, 70); WIRE = (255, 196, 46); WIRE_D = (110, 64, 0)
KEY = (0, 255, 0)
img, _ = LA.draw(KEY, arrows=False)
a = np.array(img.convert("RGBA")); bg = (a[..., 0] == 0) & (a[..., 1] == 255) & (a[..., 2] == 0); a[bg, 3] = 0
heart = Image.fromarray(a)
d = ImageDraw.Draw(heart)
P = lambda p: ((p[0] + LA.DX) * SS, p[1] * SS)
segs = [[(598, 462), (650, 540), (705, 600), (752, 628)], [(752, 628), (800, 668), (866, 712)],
        [(866, 712), (858, 800), (846, 890), (812, 948), (760, 962), (708, 910), (676, 830)],
        [(866, 712), (878, 800), (894, 900), (930, 972), (995, 985), (1060, 915), (1098, 800), (1102, 700)]]
glow = Image.new("RGBA", heart.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
for sgm in segs:
    q = [P(p) for p in sgm]
    gd.line(q, fill=(255, 220, 90, 255), width=60, joint="curve")
glow = glow.filter(ImageFilter.GaussianBlur(28))
heart = Image.alpha_composite(heart, Image.new("RGBA", heart.size, (0, 0, 0, 0)))
base = heart.copy(); base.alpha_composite(glow)
d = ImageDraw.Draw(base)
for sgm in segs:
    q = [P(p) for p in sgm]
    d.line(q, fill=WIRE_D, width=30, joint="curve"); d.line(q, fill=WIRE, width=20, joint="curve")
for n in ((598, 462), (752, 628)):
    x, y = P(n); r = 30
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 245, 200), outline=WIRE_D, width=6)
heart = base.crop(((520 + LA.DX) * SS, 30 * SS, (1190 + LA.DX) * SS, 1040 * SS))
halo_a = heart.getchannel("A").filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(4))
halo = Image.new("RGBA", heart.size, (255, 255, 255, 0)); halo.putalpha(halo_a); halo.alpha_composite(heart); heart = halo
y, x = np.mgrid[0:H2, 0:W2]
r = np.clip(np.sqrt(((x - W2 * 0.3) / W2) ** 2 + ((y - H2 * 0.5) / H2) ** 2) / 0.8, 0, 1)[..., None]
t = Image.fromarray((np.array(NAVY1) * (1 - r) + np.array(NAVY0) * r).astype("uint8"), "RGB").convert("RGBA")
h = heart.copy(); h.thumbnail((560, 700), Image.LANCZOS)
t.alpha_composite(h, (-6, (H2 - h.height) // 2 + 10))
d = ImageDraw.Draw(t)
F = lambda s, w=800: R.visuals.font(s, w)
d.text((640, 150), "HEART'S", font=F(120), fill=(255, 255, 255))
d.text((640, 280), "WIRING", font=F(150), fill=GOLD)
d.rounded_rectangle((646, 480, 1210, 560), radius=40, fill=(255, 255, 255))
d.text((928, 520), "How every beat starts", font=F(40, 700), fill=(150, 42, 66), anchor="mm")
t.convert("RGB").save(HERE / "thumbnail.png")
print("ok")
