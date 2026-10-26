"""Simple whiteboard drawings (black outlines + flat colors on white, no words), made in code so they cost
nothing. People always have real body proportions, modest clothes and a BLANK face (no eyes, nose or
mouth: the owner's rule). whiteboard.py's pen traces the outlines and then colors them in. Run:
    python -m youtube_agent.doodles   -> branding/health-support-studio/whiteboard/drawings/*.png
Keywords for each drawing are in drawings.yaml in the same folder."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "branding/health-support-studio/whiteboard/drawings"
S = 2  # drawn at twice the size, then smoothed down
LW = 11 * S
INK = (25, 25, 30)
RED, PINK, BLUE, LBLUE = (222, 60, 55), (240, 150, 160), (70, 130, 220), (160, 205, 245)
GREEN, LGREEN, YEL, ORANGE = (70, 170, 90), (150, 215, 140), (245, 205, 70), (240, 150, 60)
GRAY, SKIN, BROWN, PURPLE = (150, 150, 155), (240, 200, 165), (165, 110, 70), (160, 120, 200)


class Pad:
    def __init__(self, w=1000, h=800):
        self.img = Image.new("RGB", (w * S, h * S), "white")
        self.d = ImageDraw.Draw(self.img)

    @staticmethod
    def _p(pts):
        return [(x * S, y * S) for x, y in pts]

    def poly(self, pts, fill=None):
        pts = self._p(pts)
        if fill:
            self.d.polygon(pts, fill=fill)
        self.d.line(pts + pts[:2], fill=INK, width=LW, joint="curve")  # a smooth closed outline
        if len(pts) < 12:  # round the corners of simple shapes
            for x, y in pts:
                self.d.ellipse([x - LW / 2, y - LW / 2, x + LW / 2, y + LW / 2], fill=INK)

    def rect(self, x, y, w, h, fill=None, r=0):
        self.d.rounded_rectangle([x * S, y * S, (x + w) * S, (y + h) * S], radius=r * S, fill=fill, outline=INK,
                                 width=LW)

    def oval(self, cx, cy, rx, ry=None, fill=None):
        ry = rx if ry is None else ry
        self.d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=fill, outline=INK, width=LW)

    def line(self, pts, w=None):
        w = (w or 11) * S
        pts = self._p(pts)
        self.d.line(pts, fill=INK, width=w, joint="curve")
        for x, y in (pts[0], pts[-1]):
            self.d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=INK)

    def arc(self, cx, cy, r, a0, a1, w=None):
        self.line([(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
                   for a in range(int(a0), int(a1) + 1, 4)], w)

    def blob(self, cx, cy, rx, ry, fill, bumps=0, amp=0.0, rot=0.0):
        pts = []
        for k in range(72):
            a = 2 * math.pi * k / 72
            f = 1 + amp * math.sin(bumps * a + rot)
            pts.append((cx + rx * f * math.cos(a), cy + ry * f * math.sin(a)))
        self.poly(pts, fill)

    def save(self, name):
        OUT.mkdir(parents=True, exist_ok=True)
        self.img.resize((self.img.width // S, self.img.height // S), Image.LANCZOS).save(OUT / name)


def smooth(pts, n=8):
    """A smooth closed curve through the points (rounded shoulders, bodies)."""
    out = []
    for i in range(len(pts)):
        a, b, c, d = pts[i - 1], pts[i], pts[(i + 1) % len(pts)], pts[(i + 2) % len(pts)]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * b[j] + (-a[j] + c[j]) * t + (2 * a[j] - 5 * b[j] + 4 * c[j] - d[j]) * t * t
                                    + (-a[j] + 3 * b[j] - 3 * c[j] + d[j]) * t ** 3) for j in (0, 1)))
    return out


def _arm(p: Pad, shoulder, elbow, wrist, u, cloth):
    """A long-sleeved arm bent a little at the elbow, with the hand."""
    p.poly(_limb(shoulder, elbow, 0.44 * u, 0.34 * u), cloth)
    p.poly(_limb(elbow, wrist, 0.34 * u, 0.28 * u), cloth)
    p.d.ellipse([(elbow[0] - 0.15 * u) * S, (elbow[1] - 0.15 * u) * S, (elbow[0] + 0.15 * u) * S,
                 (elbow[1] + 0.15 * u) * S], fill=cloth)  # hides the seam at the elbow
    dx, dy = wrist[0] - elbow[0], wrist[1] - elbow[1]
    L = math.hypot(dx, dy) or 1
    p.oval(wrist[0] + dx / L * 0.2 * u, wrist[1] + dy / L * 0.2 * u, 0.16 * u, 0.22 * u, fill=SKIN)


def _limb(a, b, w0, w1):
    """A tapered limb from point a to point b (a 4-corner shape), w0/w1 = width at each end."""
    (ax, ay), (bx, by) = a, b
    L = math.hypot(bx - ax, by - ay) or 1
    nx, ny = -(by - ay) / L, (bx - ax) / L
    return [(ax + nx * w0 / 2, ay + ny * w0 / 2), (bx + nx * w1 / 2, by + ny * w1 / 2),
            (bx - nx * w1 / 2, by - ny * w1 / 2), (ax - nx * w0 / 2, ay - ny * w0 / 2)]


def _head(p: Pad, cx, cy, u, hair, long_hair=False, side=0):
    """A head with hair and NO face (no eyes, nose or mouth): the channel's style for people."""
    rx, ry = 0.40 * u, 0.52 * u
    if long_hair:  # behind the head, down to the shoulders
        p.poly([(cx - rx * 1.25, cy - ry * 0.2), (cx - rx * 1.35, cy + ry * 1.5), (cx + rx * 1.35, cy + ry * 1.5),
                (cx + rx * 1.25, cy - ry * 0.2), (cx, cy - ry * 1.15)], hair)
    p.oval(cx, cy, rx, ry, fill=SKIN)
    top = [(cx + rx * 1.06 * math.cos(math.radians(a)), cy + ry * 1.08 * math.sin(math.radians(a)))
           for a in range(185, 356, 10)]
    fringe = [(cx + rx * 0.95, cy - ry * 0.25), (cx + side * rx * 0.3, cy - ry * 0.55), (cx - rx * 0.95, cy - ry * 0.25)]
    p.poly(top + fringe, hair)


def person(p: Pad, x, y, h, shirt, pants=None, woman=False, cane=False, kid=False, hair=None):
    """A standing person with real body proportions, modestly dressed (long sleeves; trousers or a long
    dress), seen from the front, feet at (x, y). The face is left blank on purpose."""
    u = h / (6.0 if kid else 7.5)  # one head-height
    hair = hair or BROWN
    pants = pants or (GRAY if kid else BLUE)
    shoes = (90, 70, 60)
    hy = y - h + 0.55 * u
    ys = y - h + 1.45 * u  # shoulders
    sw = (0.80 if kid else 0.85 if woman else 1.0) * u
    waist = ys + (1.7 if kid else 2.0) * u
    p.rect(x - 0.14 * u, hy + 0.3 * u, 0.28 * u, 0.6 * u, fill=SKIN)  # neck
    shoulders = [(x - 0.22 * u, ys - 0.12 * u), (x - sw + 0.12 * u, ys - 0.02 * u), (x - sw, ys + 0.4 * u)]
    if woman:
        for sx in (-1, 1):  # shoes under the dress
            p.oval(x + sx * 0.26 * u, y - 0.13 * u, 0.26 * u, 0.13 * u, fill=shoes)
        left = shoulders + [(x - sw * 0.74, waist - 0.3 * u), (x - sw * 1.05, y - 1.2 * u), (x - sw * 1.2, y - 0.3 * u)]
        p.poly(smooth(left + [(x, y - 0.26 * u)] + [(2 * x - a, b) for a, b in reversed(left)] + [(x, ys - 0.05 * u)]),
               shirt)  # a long dress
        p.line([(x - sw * 0.72, waist - 0.3 * u), (x + sw * 0.72, waist - 0.3 * u)], 7)
    else:
        for sx in (-1, 1):  # legs and shoes
            p.poly([(x + sx * sw * 0.80, waist - 0.1 * u), (x + sx * 0.04 * u, waist - 0.1 * u),
                    (x + sx * 0.08 * u, y - 0.18 * u), (x + sx * 0.52 * u, y - 0.18 * u)], pants)
            p.oval(x + sx * 0.32 * u, y - 0.13 * u, 0.3 * u, 0.13 * u, fill=shoes)
        left = shoulders + [(x - sw * 0.86, ys + 1.2 * u), (x - sw * 0.82, waist + 0.05 * u)]
        p.poly(smooth(left + [(2 * x - a, b) for a, b in reversed(left)] + [(x, ys - 0.05 * u)]), shirt)
        p.line([(x - 0.18 * u, ys - 0.08 * u), (x, ys + 0.25 * u), (x + 0.18 * u, ys - 0.08 * u)], 7)  # collar
    arm = (1.0 if kid else 1.15) * u
    for sx in (-1, 1):  # long sleeves, a little bent, then the hands
        sh = (x + sx * (sw - 0.14 * u), ys + 0.22 * u)
        el = (x + sx * (sw + 0.18 * u), ys + 0.22 * u + arm)
        wr = (x + sx * (sw + 0.12 * u), ys + 0.22 * u + 1.95 * arm)
        _arm(p, sh, el, wr, u, shirt)
    if cane:
        hx, hy2 = x + sw + 0.2 * u, ys + 0.22 * u + 1.95 * arm + 0.2 * u
        p.line([(hx, hy2), (hx + 0.15 * u, y)], 10)
        p.arc(hx - 0.14 * u, hy2, 0.14 * u, 180, 360, 10)
    _head(p, x, hy, u, hair, long_hair=woman)


def ambulance():
    p = Pad(1100, 720)
    p.rect(80, 200, 640, 360, fill=None, r=24)  # box
    p.poly([(720, 300), (900, 300), (1010, 430), (1010, 560), (720, 560)])  # cab
    p.poly([(745, 325), (885, 325), (965, 430), (745, 430)], LBLUE)  # window
    p.rect(80, 450, 930, 40, fill=RED)  # stripe
    p.rect(330, 250, 70, 180, fill=RED)  # cross
    p.rect(275, 305, 180, 70, fill=RED)
    p.rect(860, 250, 70, 50, fill=RED, r=10)  # light
    p.line([(895, 210), (895, 160)], 9)
    p.line([(840, 220), (810, 180)], 9)
    p.line([(950, 220), (980, 180)], 9)
    for wx in (240, 850):
        p.oval(wx, 580, 80, fill=GRAY)
        p.oval(wx, 580, 30, fill="white")
    for yy in (280, 360, 440):  # speed lines
        p.line([(20, yy), (55, yy)], 9)
    p.save("ambulance.png")


def phone():
    p = Pad(700, 900)
    p.rect(200, 60, 300, 600, fill=None, r=40)
    p.rect(225, 130, 250, 440, fill=LBLUE, r=10)
    p.oval(350, 615, 22)
    p.oval(350, 350, 85, fill=GREEN)  # call button
    p.poly([(315, 310), (335, 300), (350, 330), (338, 342), (360, 372), (375, 362), (395, 385), (380, 400),
            (330, 380), (305, 330)], "white")
    for r in (60, 100, 140):  # ringing
        p.arc(560, 200, r, -60, 30, 9)
        p.arc(140, 200, r, 150, 240, 9)
    p.save("phone_call.png")


def lungs():
    p = Pad(900, 860)
    p.line([(450, 60), (450, 330)], 26)  # windpipe
    for k in range(4):
        p.line([(425, 110 + k * 50), (475, 110 + k * 50)], 7)
    left = [(410, 330), (300, 220), (190, 280), (120, 470), (110, 680), (170, 760), (330, 740), (400, 650)]
    right = [(900 - x, y) for x, y in left]
    for side in (left, right):
        pts = []
        for i in range(len(side)):  # smooth closed curve through the points
            a, b, c, d = side[i - 1], side[i], side[(i + 1) % len(side)], side[(i + 2) % len(side)]
            for t in [k / 10 for k in range(10)]:
                t2, t3 = t * t, t * t * t
                pts.append(tuple(0.5 * (2 * b[j] + (-a[j] + c[j]) * t + (2 * a[j] - 5 * b[j] + 4 * c[j] - d[j]) * t2
                                        + (-a[j] + 3 * b[j] - 3 * c[j] + d[j]) * t3) for j in (0, 1)))
        p.poly(pts, PINK)
    p.line([(450, 330), (360, 420), (300, 520)], 14)
    p.line([(360, 420), (330, 600)], 10)
    p.line([(450, 330), (540, 420), (600, 520)], 14)
    p.line([(540, 420), (570, 600)], 10)
    p.save("lungs.png")


def family():
    p = Pad(1200, 800)
    person(p, 160, 770, 600, PURPLE, woman=True, cane=True, hair=(200, 200, 205))  # grandmother
    person(p, 420, 770, 700, LBLUE, pants=(70, 80, 110), hair=(60, 45, 35))  # father
    person(p, 670, 770, 660, RED, woman=True, hair=(40, 30, 25))  # mother
    person(p, 880, 770, 430, GREEN, kid=True, hair=(60, 45, 35))  # boy
    person(p, 1060, 770, 400, YEL, woman=True, kid=True, hair=(120, 70, 40))  # girl
    p.save("family.png")


def heart():
    p = Pad(800, 760)
    pts = [(400 + 21 * 16 * math.sin(t) ** 3,
            380 - 21 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)))
           for t in [k * 2 * math.pi / 120 for k in range(120)]]
    p.poly(pts, RED)
    p.line([(60, 700), (230, 700), (270, 620), (320, 760), (370, 560), (420, 700), (740, 700)], 10)  # heartbeat
    p.save("heart_beat.png")


def globe():
    p = Pad(800, 800)
    p.oval(400, 400, 330, fill=LBLUE)
    p.blob(300, 300, 120, 90, LGREEN, 5, 0.18)
    p.blob(470, 520, 110, 140, LGREEN, 4, 0.2, 1)
    p.blob(560, 250, 70, 50, LGREEN, 3, 0.2, 2)
    p.d.ellipse([(400 - 140) * S, 70 * S, (400 + 140) * S, 730 * S], outline=INK, width=6 * S)
    p.line([(70, 400), (730, 400)], 6)
    p.save("globe.png")


def pills():
    p = Pad(900, 760)
    p.rect(140, 230, 300, 470, fill=ORANGE, r=30)  # bottle
    p.rect(115, 120, 350, 120, fill="white", r=16)  # cap
    p.rect(175, 360, 230, 200, fill="white", r=10)  # label (no words)
    for yy in (410, 460, 510):
        p.line([(205, yy), (375, yy)], 7)
    p.rect(560, 420, 260, 100, fill=None, r=50)  # capsule
    p.d.rounded_rectangle([560 * S, 420 * S, 690 * S, 520 * S], radius=50 * S, fill=BLUE, outline=INK, width=LW)
    p.oval(640, 640, 70, fill=YEL)  # tablet
    p.line([(580, 640), (700, 640)], 7)
    p.save("pills.png")


def clock():
    p = Pad(800, 800)
    p.oval(400, 420, 320, fill=YEL)
    p.oval(400, 420, 270, fill="white")
    for k in range(12):
        a = math.radians(k * 30)
        r0 = 225 if k % 3 else 205
        p.line([(400 + r0 * math.cos(a), 420 + r0 * math.sin(a)), (400 + 250 * math.cos(a), 420 + 250 * math.sin(a))], 9)
    p.line([(400, 420), (400, 250)], 14)
    p.line([(400, 420), (510, 480)], 14)
    p.oval(400, 420, 18, fill=RED)
    p.rect(330, 50, 140, 50, fill=RED, r=12)
    p.save("clock.png")


def germ():
    p = Pad(820, 820)
    for k in range(12):
        a = math.radians(k * 30 + 8)
        x0, y0 = 410 + 230 * math.cos(a), 410 + 230 * math.sin(a)
        x1, y1 = 410 + 330 * math.cos(a), 410 + 330 * math.sin(a)
        p.line([(x0, y0), (x1, y1)], 12)
        p.oval(x1, y1, 26, fill=RED)
    p.blob(410, 410, 240, 240, LGREEN, 7, 0.05)
    for x, y, r in ((340, 340, 40), (480, 380, 30), (400, 500, 50), (500, 520, 24)):
        p.oval(x, y, r, fill=GREEN)
    p.save("germ.png")


def thermometer():
    p = Pad(600, 900)
    p.rect(240, 60, 120, 620, fill="white", r=60)
    p.oval(300, 740, 110, fill=RED)
    p.d.rectangle([272 * S, 260 * S, 328 * S, 700 * S], fill=RED)
    p.line([(272, 260), (328, 260)], 7)
    for k in range(7):
        p.line([(360, 120 + k * 75), (410, 120 + k * 75)], 8)
    for r in (60, 100):  # heat lines
        p.arc(470, 200, r, -50, 50, 8)
    p.save("thermometer.png")


def brain():
    p = Pad(950, 760)
    p.blob(470, 360, 380, 270, PINK, 9, 0.07)
    p.line([(470, 100), (440, 220), (500, 340), (450, 470), (480, 620)], 10)  # the middle
    for pts in ([(170, 260), (260, 230), (300, 300), (380, 270)], [(130, 420), (230, 390), (290, 450), (360, 420)],
                [(200, 540), (290, 520), (350, 570)], [(580, 250), (660, 220), (700, 290), (790, 270)],
                [(560, 420), (650, 400), (700, 460), (810, 430)], [(590, 560), (680, 530), (750, 580)]):
        p.line(pts, 9)
    p.rect(420, 600, 110, 140, fill=PINK, r=30)  # brain stem
    p.save("brain.png")


def house():
    p = Pad(900, 820)
    p.rect(160, 360, 580, 400, fill=YEL)
    p.poly([(100, 380), (450, 80), (800, 380)], RED)
    p.rect(390, 540, 130, 220, fill=BROWN, r=8)
    p.oval(495, 650, 10, fill=INK)
    for x in (220, 600):
        p.rect(x, 440, 100, 100, fill=LBLUE)
        p.line([(x + 50, 440), (x + 50, 540)], 7)
        p.line([(x, 490), (x + 100, 490)], 7)
    p.rect(610, 140, 70, 140, fill=GRAY)
    p.save("house.png")


def water():
    p = Pad(800, 820)
    p.poly([(150, 160), (450, 160), (410, 760), (190, 760)])
    p.poly([(165, 340), (435, 340), (410, 760), (190, 760)], LBLUE)
    pts = [(620 + 100 * math.sin(t) * (1 - math.cos(t)) / 2 * 1.4, 520 - 150 * math.cos(t) * 1.0)
           for t in [k * 2 * math.pi / 80 for k in range(80)]]
    p.poly(pts, BLUE)
    p.save("water.png")


def food():
    p = Pad(1000, 760)
    p.blob(320, 450, 220, 210, RED, 2, 0.06, math.pi / 2)  # apple
    p.line([(320, 260), (340, 160)], 14)
    p.poly([(345, 200), (430, 150), (480, 190), (400, 240)], GREEN)
    for dx in (-60, 0, 60):  # carrot leaves
        p.poly([(760, 250), (760 + dx * 1.6 - 22, 90), (760 + dx * 1.6 + 22, 90)], GREEN)
    p.poly([(680, 240), (840, 240), (770, 700), (750, 700)], ORANGE)  # carrot
    for k in range(4):
        p.line([(705 + k * 12, 330 + k * 90), (745 + k * 6, 330 + k * 90)], 7)
    p.save("food.png")


def sleep():
    p = Pad(1000, 760)
    p.rect(80, 420, 840, 160, fill=LBLUE, r=20)  # bed
    p.rect(80, 300, 60, 400, fill=BROWN, r=10)
    p.rect(860, 380, 60, 320, fill=BROWN, r=10)
    p.rect(160, 360, 200, 90, fill="white", r=40)  # pillow
    _head(p, 270, 345, 135, (60, 45, 35))  # no face
    p.rect(330, 380, 530, 130, fill=PURPLE, r=30)  # blanket
    moon = [(760 + 110 * math.cos(math.radians(a)), 150 + 110 * math.sin(math.radians(a))) for a in range(60, 301, 6)]
    moon += [(800 + 85 * math.cos(math.radians(a)), 150 + 85 * math.sin(math.radians(a))) for a in range(270, 89, -6)]
    p.poly(moon, YEL)
    for x, y in ((560, 110), (620, 230), (930, 80)):
        p.poly([(x, y - 30), (x + 9, y - 9), (x + 30, y), (x + 9, y + 9), (x, y + 30), (x - 9, y + 9), (x - 30, y),
                (x - 9, y - 9)], YEL)
    p.save("sleep.png")


def walking():
    """A person walking, seen from the side (no face)."""
    p = Pad(760, 900)
    u, x, y = 112, 380, 860
    ys, hip = y - 6.05 * u, y - 3.55 * u
    back_leg = [(x - 0.1 * u, hip), (x - 0.8 * u, y - 1.7 * u), (x - 1.25 * u, y - 0.2 * u)]
    front_leg = [(x + 0.1 * u, hip), (x + 0.6 * u, y - 1.8 * u), (x + 1.05 * u, y - 0.2 * u)]
    for leg, shade in ((back_leg, (55, 65, 95)), (front_leg, (70, 80, 110))):
        p.poly(_limb(leg[0], leg[1], 0.62 * u, 0.42 * u), shade)
        p.poly(_limb(leg[1], leg[2], 0.42 * u, 0.32 * u), shade)
        p.oval(leg[2][0] + 0.18 * u, y - 0.12 * u, 0.36 * u, 0.13 * u, fill=(90, 70, 60))
    _arm(p, (x - 0.05 * u, ys + 0.3 * u), (x - 0.55 * u, ys + 1.3 * u), (x - 0.7 * u, ys + 2.2 * u), u,
         (50, 140, 75))  # back arm
    p.rect(x - 0.13 * u, ys - 0.75 * u, 0.3 * u, 0.6 * u, fill=SKIN)  # neck
    p.poly(smooth([(x - 0.25 * u, ys - 0.12 * u), (x - 0.55 * u, ys + 0.2 * u), (x - 0.55 * u, ys + 1.3 * u),
                   (x - 0.5 * u, hip + 0.1 * u), (x + 0.5 * u, hip + 0.1 * u), (x + 0.6 * u, ys + 1.2 * u),
                   (x + 0.45 * u, ys + 0.1 * u), (x + 0.2 * u, ys - 0.12 * u)]), GREEN)  # body
    _arm(p, (x + 0.05 * u, ys + 0.3 * u), (x + 0.35 * u, ys + 1.3 * u), (x + 0.85 * u, ys + 2.0 * u), u,
         GREEN)  # front arm
    _head(p, x + 0.05 * u, ys - 1.05 * u, u, (60, 45, 35), side=1)
    for k in range(3):
        p.line([(60, 330 + k * 70), (130, 330 + k * 70)], 9)
    p.save("walking.png")


ALL = [ambulance, phone, lungs, family, heart, globe, pills, clock, germ, thermometer, brain, house, water, food,
       sleep, walking]

if __name__ == "__main__":
    for f in ALL:
        f()
    print(sorted(p.name for p in OUT.glob("*.png")))
