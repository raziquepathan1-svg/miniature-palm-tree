"""Textbook line-art heart (frontal section): black outlines, flat colours, hollow white arrows, our own labels.
Each blood path (right side / left side) is one merged region, so vessels flow into chambers with one clean outline.
Coordinates are 1920x1080 screen pixels (before the DX shift)."""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import render as R
from render import SS, W, H, spline

HERE = Path(__file__).resolve().parent
DX, DY = 100, 0
LINE = (30, 30, 40)
BLUE, RED = (62, 112, 200), (206, 52, 62)
BLUE_CAP, RED_CAP = (120, 160, 228), (232, 118, 124)
WALL = (240, 176, 164)
import sys
if "--bw" in sys.argv:  # black-and-white textbook line art
    BLUE = RED = WALL = (255, 255, 255)
    BLUE_CAP = RED_CAP = (255, 255, 255)
STROKE = 7  # outline thickness in supersampled px


def P(p):
    return ((p[0] + DX) * SS, (p[1] + DY) * SS)


def smooth(pts, closed, n=16):
    return spline(pts, closed=closed, n=n) if len(pts) > 2 else list(pts)


def tube_poly(pts, w):
    """Polygon around a centreline (screen px) with width w (number or list per spline point)."""
    c = smooth(pts, False)
    ws = w if isinstance(w, list) else [w] * len(c)
    left, right = [], []
    for i, (x, y) in enumerate(c):
        a, b = c[max(i - 1, 0)], c[min(i + 1, len(c) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        hw = ws[min(i, len(ws) - 1)] / 2
        left.append((x + nx * hw, y + ny * hw))
        right.append((x - nx * hw, y - ny * hw))
    return left + right[::-1]


def blob(pts):
    return smooth(pts, True)


def mask_of(shapes):
    m = Image.new("L", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(m)
    for s in shapes:
        d.polygon([P(p) for p in s], fill=255)
    return np.array(m) > 127


def dilate(m, r):
    h, w = m.shape
    pad = np.zeros((h + 2 * r, w + 2 * r), bool)
    pad[r:r + h, r:r + w] = m
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                out |= pad[r + dy:r + dy + h, r + dx:r + dx + w]
    return out


def paint(img, shapes, fill):
    m = mask_of(shapes)
    a = np.array(img)
    a[m] = fill
    a[dilate(m, STROKE) & ~m] = LINE
    return Image.fromarray(a)


def cap(d, end, prev, w, fill):
    """Cut (open) vessel end drawn as a flat ellipse across the tube."""
    (x, y), (px, py) = P(end), P(prev)
    ang = math.atan2(y - py, x - px)
    r = w * SS / 2 + STROKE / 2
    size = int(4 * r)
    ell = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ed = ImageDraw.Draw(ell)
    c = size / 2
    ed.ellipse((c - r * 0.34, c - r, c + r * 0.34, c + r), fill=fill, outline=LINE, width=STROKE - 1)
    ell = ell.rotate(-math.degrees(ang), resample=Image.BICUBIC)
    d._image.alpha_composite(ell, (int(x - c), int(y - c)))


def arrow(d, a, b, w=12):
    (x0, y0), (x1, y1) = P(a), P(b)
    ang = math.atan2(y1 - y0, x1 - x0)
    ux, uy, nx, ny = math.cos(ang), math.sin(ang), -math.sin(ang), math.cos(ang)
    s = w * SS
    hl = 2.2 * s
    bx, by = x1 - ux * hl, y1 - uy * hl
    pts = [(x0 + nx * s / 2, y0 + ny * s / 2), (bx + nx * s / 2, by + ny * s / 2), (bx + nx * s * 1.3, by + ny * s * 1.3),
           (x1, y1), (bx - nx * s * 1.3, by - ny * s * 1.3), (bx - nx * s / 2, by - ny * s / 2),
           (x0 - nx * s / 2, y0 - ny * s / 2)]
    d.polygon(pts, fill=(255, 255, 255))
    d.line(pts + [pts[0]], fill=LINE, width=5, joint="curve")


def valve(d, c, angle, half):
    """Two leaflets hinged on the channel walls, pointing downstream (open valve)."""
    a = math.radians(angle)
    fx, fy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    x, y = c
    for s in (-1, 1):
        base1 = (x + s * nx * half - fx * 9, y + s * ny * half - fy * 9)
        base2 = (x + s * nx * half + fx * 7, y + s * ny * half + fy * 7)
        tip = (x + s * nx * half * 0.3 + fx * half * 1.15, y + s * ny * half * 0.3 + fy * half * 1.15)
        q = [P(base1), P(tip), P(base2)]
        d.polygon(q, fill=(255, 248, 236))
        d.line(q + [q[0]], fill=LINE, width=5, joint="curve")


# ---------------- geometry (screen px, before DX shift) ----------------
WALL_PTS = [(560, 430), (540, 560), (552, 700), (605, 830), (715, 940), (855, 1008), (930, 1020), (992, 990),
            (1062, 900), (1110, 770), (1122, 640), (1095, 520), (1045, 450), (965, 422), (880, 440), (770, 428),
            (655, 415)]
RA = [(585, 455), (690, 445), (735, 478), (746, 560), (730, 628), (690, 662), (622, 652), (582, 596), (575, 520)]
TRI = [(688, 596), (762, 738)]
RV = [(705, 705), (785, 682), (835, 705), (848, 785), (832, 880), (790, 948), (730, 925), (684, 860), (665, 780)]
LA = [(965, 458), (1040, 452), (1082, 482), (1088, 540), (1058, 582), (992, 592), (960, 562), (952, 505)]
MIT = [(985, 570), (1052, 566), (1050, 662), (988, 664)]
LV = [(902, 662), (962, 642), (1042, 646), (1082, 700), (1088, 800), (1054, 900), (994, 960), (944, 964), (912, 900),
      (888, 782), (882, 702)]
SVC = [(650, 40), (650, 300), (650, 500)]
IVC = [(612, 1100), (612, 800), (618, 600)]
TRUNK = [(812, 740), (803, 600), (814, 482), (845, 388), (905, 336), (990, 318), (1090, 315), (1172, 318)]
AORTA = [(905, 690), (898, 560), (890, 450), (885, 340), (902, 250), (952, 192), (1012, 186), (1056, 226),
         (1072, 300), (1072, 322)]
DESC = [(1072, 330), (1072, 400), (1072, 470)]
BRANCHES = [[(932, 205), (905, 62)], [(988, 190), (992, 56)], [(1038, 205), (1066, 72)]]
RPA = [(900, 330), (700, 330), (518, 330)]
RPV = [[(676, 375), (518, 375)], [(676, 413), (522, 413)]]
LPV = [[(1060, 470), (1176, 440)], [(1070, 545), (1180, 548)]]


def draw(bg=(255, 255, 255), arrows=True):
    img = Image.new("RGB", (W * SS, H * SS), bg)
    # back vessels: right pulmonary artery + right pulmonary veins pass behind the SVC
    img = paint(img, [tube_poly(RPA, 44)], BLUE)
    img = paint(img, [tube_poly(v, 32) for v in RPV], RED)
    img = paint(img, [tube_poly(DESC, 74)], RED)                 # descending aorta, behind the heart
    img = paint(img, [blob(WALL_PTS)], WALL)
    img = paint(img, [tube_poly(b, 30) for b in BRANCHES] + [tube_poly(AORTA, 74), blob(LA), MIT, blob(LV)]
                + [tube_poly(v, 32) for v in LPV], RED)
    img = paint(img, [tube_poly(SVC, 64), tube_poly(IVC, 70), blob(RA), tube_poly(TRI, 74), blob(RV), tube_poly(TRUNK, 60)], BLUE)
    img = img.convert("RGBA")
    d = ImageDraw.Draw(img)
    cap(d, SVC[0], SVC[1], 64, BLUE_CAP)
    cap(d, RPA[-1], RPA[-2], 44, BLUE_CAP)
    cap(d, TRUNK[-1], TRUNK[-2], 60, BLUE_CAP)
    for v in RPV:
        cap(d, v[-1], v[-2], 32, RED_CAP)
    for v in LPV:
        cap(d, v[-1], v[-2], 32, RED_CAP)
    for b in BRANCHES:
        cap(d, b[-1], b[-2], 30, RED_CAP)
    valve(d, (724, 667), 62, 35)       # tricuspid
    valve(d, (1018, 616), 90, 32)      # mitral
    valve(d, (805, 632), -92, 28)      # pulmonary
    valve(d, (900, 618), -94, 34)      # aortic
    for a, b in (((650, 110), (650, 235)), ((612, 1060), (612, 900)), ((650, 520), (712, 630)),
                 ((770, 890), (800, 775)), ((815, 560), (823, 440)), ((1040, 316), (1150, 318)),
                 ((835, 330), (700, 330)), ((540, 375), (610, 375)), ((540, 413), (610, 413)),
                 ((1160, 444), (1095, 461)), ((1165, 547), (1102, 546)), ((1018, 495), (1018, 590)),
                 ((990, 880), (918, 705)), ((945, 192), (1020, 192)), ((914, 150), (906, 90)),
                 ((990, 140), (991, 82)), ((1050, 150), (1062, 98))):
        if arrows:
            arrow(d, a, b)
    return img, d


LEFT = [("Superior vena cava", (650, 185)), ("Right pulmonary artery", (590, 330)),
        ("Right pulmonary veins", (548, 413)), ("Right atrium", (612, 565)), ("Pulmonary valve", (805, 612)),
        ("Tricuspid valve", (724, 680)), ("Right ventricle", (720, 840)), ("Inferior vena cava", (612, 975))]
RIGHT = [("Aortic arch", (1040, 160)), ("Pulmonary artery", (1112, 318)), ("Left pulmonary veins", (1150, 447)),
         ("Left atrium", (1060, 525)), ("Aortic valve", (900, 600)), ("Mitral valve", (1018, 630)),
         ("Left ventricle", (1010, 800)), ("Septum", (866, 860))]


def labels(d, size=26):
    f = R.F(size, 600)
    for side, items, x in (("L", LEFT, 470), ("R", RIGHT, 1205)):
        for i, (name, tgt) in enumerate(items):
            y = 140 + i * 120
            tx, ty = P(tgt)
            sx = (x + DX + (12 if side == "L" else -12)) * SS
            d.line([(sx, y * SS), (tx, ty)], fill=LINE, width=2 * SS)
            r = 4 * SS
            d.ellipse((tx - r, ty - r, tx + r, ty + r), fill=LINE)
            d.text(((x + DX) * SS, y * SS), name, font=f, fill=LINE, anchor="rm" if side == "L" else "lm")


if __name__ == "__main__":
    img, d = draw()
    labels(d)
    out = "lineart_heart_bw.png" if "--bw" in sys.argv else "lineart_heart.png"
    img.resize((W, H), Image.LANCZOS).convert("RGB").save(HERE / out)
    print("ok")
