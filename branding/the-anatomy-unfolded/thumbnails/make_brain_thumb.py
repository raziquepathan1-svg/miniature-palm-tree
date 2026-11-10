"""Brain Anatomy thumbnail (owner's glowing blue brain picture): pill + white line + big colour line + footer."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "youtube_agent" / "explainer" / "heart"))
import render as R
F = lambda s, w=900: R.visuals.font(s, w)
IMG, OUT = sys.argv[1], Path(sys.argv[2])
pill, l1, l2, c2, pc = "BRAIN ANATOMY", "INSIDE YOUR", "BRAIN", (90, 200, 255), (30, 110, 200)
W, H = 1280, 720
def fit(d, text, maxw, start, w=900):
    s = start
    while d.textlength(text, font=F(s, w)) > maxw and s > 40:
        s -= 4
    return s
im = Image.open(IMG).convert("RGB")
sc = max(W / im.width, H / im.height)
im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H)).convert("RGBA")
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
for x in range(560, W):
    sd.line([(x, 0), (x, H)], fill=(0, 0, 0, int(110 * min(1, (x - 560) / 250))))
im.alpha_composite(sh)
d = ImageDraw.Draw(im)
cx, maxw = 945, 560
s1 = fit(d, l1, maxw, 92); s2 = fit(d, l2, maxw, 170)
ps = 34; pw = d.textlength(pill, font=F(ps, 800)) + 50
y0 = 360 - (s1 + s2 + 90) // 2
d.rounded_rectangle((cx - pw / 2, y0, cx + pw / 2, y0 + 58), radius=29, fill=pc)
d.text((cx, y0 + 29), pill, font=F(ps, 800), fill=(255, 255, 255), anchor="mm")
yl1 = y0 + 90 + s1 // 2; yl2 = yl1 + s1 // 2 + 15 + s2 // 2
for txt, y, s, col in ((l1, yl1, s1, (255, 255, 255)), (l2, yl2, s2, c2)):
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((cx, y), txt, font=F(s), fill=(0, 0, 0, 255), anchor="mm", stroke_width=14, stroke_fill=(0, 0, 0, 255))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    d.text((cx, y), txt, font=F(s), fill=col, anchor="mm", stroke_width=max(4, s // 22), stroke_fill=(10, 10, 20))
d.text((cx, 660), "THE ANATOMY UNFOLDED", font=F(26, 700), fill=(200, 210, 230), anchor="mm")
im.convert("RGB").save(OUT, quality=93)
print("ok", OUT)
