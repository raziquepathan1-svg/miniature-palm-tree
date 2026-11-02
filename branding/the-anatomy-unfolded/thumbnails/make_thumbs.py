import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "heart"))
import render as R
F = lambda s, w=900: R.visuals.font(s, w)
U = "/root/.claude/uploads/fd2a766b-3b0e-565b-bca7-71c7c642aa3a/"
OUT = Path(__file__).resolve().parent
JOBS = {  # id: (image, pill, line1, line2, colour of line2, pill colour)
 "high_blood_pressure": ("c37272d7-image.jpg", "HIGH BLOOD PRESSURE", "THE SILENT", "KILLER", (255, 45, 45), (200, 20, 30)),
 "blood_pressure": ("83cd54c3-image.jpg", "BLOOD PRESSURE", "WHAT IS", "120/80?", (255, 70, 60), (200, 20, 30)),
 "blood_vessels": ("8f90ce75-image.jpg", "ARTERIES vs VEINS", "THICK", "vs THIN", (80, 170, 255), (30, 90, 200)),
 "heart_attack": ("4606c106-image.jpg", "HEART ATTACK", "TIME IS", "MUSCLE", (255, 60, 50), (200, 20, 30)),
 "heart_electrical": ("4032255e-image.jpg", "HEART'S ELECTRICAL SYSTEM", "THE HEART'S", "SPARK", (255, 215, 0), (190, 140, 0)),
 "heart_physiology": ("2a2aaf28-image.jpg", "HEART PHYSIOLOGY", "WHAT MAKES", "LUB-DUB?", (90, 200, 255), (30, 110, 200)),
 "heart_anatomy_v2": ("996294d4-image.jpg", "HEART ANATOMY", "YOUR HEART HAS", "4 ROOMS?", (255, 205, 60), (190, 140, 0)),
}
W, H = 1280, 720
def fit(d, text, maxw, start, w=900):
    s = start
    while d.textlength(text, font=F(s, w)) > maxw and s > 40:
        s -= 4
    return s
for eid, (img, pill, l1, l2, c2, pc) in JOBS.items():
    im = Image.open(U + img).convert("RGB")
    sc = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H)).convert("RGBA")
    # darken the right side a little so the words pop
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for x in range(560, W):
        sd.line([(x, 0), (x, H)], fill=(0, 0, 0, int(110 * min(1, (x - 560) / 250))))
    im.alpha_composite(sh)
    d = ImageDraw.Draw(im)
    cx, maxw = 945, 560
    s1 = fit(d, l1, maxw, 92); s2 = fit(d, l2, maxw, 170)
    # pill
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
    im.convert("RGB").save(OUT / f"{eid}_thumb.jpg", quality=93)
print("ok")
