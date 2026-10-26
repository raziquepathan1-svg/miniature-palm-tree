"""Simple whiteboard drawings (black outlines + flat colors on white, no words), made in code so they cost
nothing. whiteboard.py's pen traces the outlines and then colors them in. Run:
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


def person(p: Pad, x, y, h, shirt, woman=False, cane=False, small=False):
    """A friendly simple person standing at (x, feet y), modestly dressed."""
    head = h * 0.13
    hy = y - h + head
    p.oval(x, hy, head, fill=SKIN)
    p.arc(x, hy + head * 0.1, head * 0.5, 30, 150, 7)  # a small smile
    p.oval(x - head * 0.35, hy - head * 0.15, 4, fill=INK)
    p.oval(x + head * 0.35, hy - head * 0.15, 4, fill=INK)
    top, waist = hy + head + 6, y - h * 0.42
    sw = h * 0.17
    if woman:  # a long dress
        p.poly([(x - sw * 0.8, top), (x + sw * 0.8, top), (x + sw * 1.25, y - h * 0.08), (x - sw * 1.25, y - h * 0.08)],
               shirt)
    else:
        p.rect(x - sw, top, sw * 2, waist - top, fill=shirt, r=12)
        p.rect(x - sw * 0.85, waist, sw * 1.7, y - h * 0.08 - waist, fill=BLUE if not small else GRAY, r=6)
        p.line([(x, waist + 10), (x, y - h * 0.08)], 7)
    p.line([(x - sw * 0.5, y - h * 0.08), (x - sw * 0.6, y)], 12)
    p.line([(x + sw * 0.5, y - h * 0.08), (x + sw * 0.6, y)], 12)
    p.line([(x - sw * (0.9 if not woman else 0.7), top + 12), (x - sw * 1.5, waist + 10)], 12)
    p.line([(x + sw * (0.9 if not woman else 0.7), top + 12), (x + sw * 1.5, waist + 10)], 12)
    if cane:
        p.line([(x + sw * 1.6, waist + 6), (x + sw * 1.9, y)], 10)
        p.arc(x + sw * 1.6 - 14, waist + 6, 14, 180, 360, 10)


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
    person(p, 170, 760, 560, PURPLE, woman=True, cane=True)  # grandmother
    person(p, 420, 760, 640, BLUE)  # father
    person(p, 680, 760, 610, RED, woman=True)  # mother
    person(p, 880, 760, 400, GREEN, small=True)  # boy
    person(p, 1060, 760, 380, YEL, woman=True)  # girl
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
    p.oval(270, 340, 70, fill=SKIN)
    p.arc(250, 330, 22, 20, 160, 7)
    p.arc(300, 330, 22, 20, 160, 7)
    p.rect(330, 380, 530, 130, fill=PURPLE, r=30)  # blanket
    moon = [(760 + 110 * math.cos(math.radians(a)), 150 + 110 * math.sin(math.radians(a))) for a in range(60, 301, 6)]
    moon += [(800 + 85 * math.cos(math.radians(a)), 150 + 85 * math.sin(math.radians(a))) for a in range(270, 89, -6)]
    p.poly(moon, YEL)
    for x, y in ((560, 110), (620, 230), (930, 80)):
        p.poly([(x, y - 30), (x + 9, y - 9), (x + 30, y), (x + 9, y + 9), (x, y + 30), (x - 9, y + 9), (x - 30, y),
                (x - 9, y - 9)], YEL)
    p.save("sleep.png")


def walking():
    p = Pad(800, 860)
    x, y, h = 400, 800, 720
    head = h * 0.12
    p.oval(x + 20, y - h + head, head, fill=SKIN)
    top, hip = y - h + 2 * head + 6, y - h * 0.42
    p.poly([(x - 55, top), (x + 75, top), (x + 70, hip), (x - 50, hip)], GREEN)
    p.line([(x, hip), (x - 120, y - 150), (x - 170, y - 20)], 18)
    p.line([(x + 20, hip), (x + 110, y - 170), (x + 190, y - 40)], 18)
    p.line([(x - 40, top + 20), (x - 130, hip - 40)], 14)
    p.line([(x + 60, top + 20), (x + 150, hip + 20)], 14)
    for k in range(3):
        p.line([(120, 300 + k * 70), (190, 300 + k * 70)], 9)
    p.save("walking.png")


ALL = [ambulance, phone, lungs, family, heart, globe, pills, clock, germ, thermometer, brain, house, water, food,
       sleep, walking]

if __name__ == "__main__":
    for f in ALL:
        f()
    print(sorted(p.name for p in OUT.glob("*.png")))
