"""External (anterior) view of the heart in our line-art style: black outlines, flat colours.
Used for the channel logo / banner. Coordinates in screen px (lineart P() mapping)."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import lineart as LA
from lineart import tube_poly, blob, paint, cap, P, BLUE, RED, BLUE_CAP, RED_CAP, LINE
from render import SS, W, H

MUSCLE = (214, 96, 96)
MUSCLE_LIGHT = (232, 132, 126)
AURICLE = (200, 82, 86)
FAT = (246, 214, 140)

BODY = [(255, 400), (215, 520), (228, 650), (300, 780), (420, 885), (560, 955), (650, 975), (705, 940), (770, 850),
        (818, 730), (832, 610), (806, 492), (750, 418), (660, 392), (560, 410), (450, 392), (350, 382)]
R_AUR = [(240, 372), (290, 346), (340, 352), (380, 384), (392, 424), (366, 436), (350, 418), (330, 446), (306, 428),
         (282, 458), (258, 440), (236, 410)]
L_AUR = [(738, 410), (790, 398), (836, 420), (842, 462), (812, 480), (784, 470), (756, 456)]
AORTA = [(500, 470), (488, 360), (492, 260), (540, 180), (620, 150), (700, 178), (738, 250), (742, 340), (742, 430)]
BRANCHES = [[(548, 182), (512, 62)], [(612, 156), (606, 40)], [(676, 168), (712, 58)]]
SVC = [(330, 70), (330, 250), (330, 420)]
IVC = [(298, 960), (300, 860), (300, 760)]
TRUNK = [(585, 560), (580, 440), (604, 340), (660, 286), (740, 268), (830, 268)]
RPA = [(560, 318), (440, 312), (250, 300)]
RPV = [[(300, 368), (200, 360)], [(300, 410), (204, 412)]]
LPV = [[(780, 372), (890, 360)], [(790, 425), (894, 432)]]
LAD = [(612, 470), (640, 560), (676, 680), (700, 800), (690, 900)]          # anterior interventricular artery
LAD_V = [(596, 476), (622, 570), (652, 690), (672, 810), (664, 905)]        # great cardiac vein beside it
RCA = [(470, 470), (390, 500), (300, 590), (276, 700), (320, 800)]           # right coronary artery
DIAG = [[(650, 600), (740, 640), (790, 700)], [(684, 740), (760, 790)]]


def draw(bg=(255, 255, 255)):
    img = Image.new("RGB", (W * SS, H * SS), bg)
    img = paint(img, [tube_poly(v, 34) for v in RPV] + [tube_poly(v, 34) for v in LPV], RED)
    img = paint(img, [tube_poly(RPA, 46), tube_poly(IVC, 74)], BLUE)
    img = paint(img, [tube_poly(b, 34) for b in BRANCHES] + [tube_poly(AORTA, 86)], RED)
    img = paint(img, [tube_poly(SVC, 78)], BLUE)
    img = paint(img, [blob(L_AUR)], AURICLE)
    img = paint(img, [blob(BODY)], MUSCLE)
    # soft highlight on the ventricles for a little depth (stays flat-looking)
    hl = Image.new("L", img.size, 0)
    ImageDraw.Draw(hl).ellipse((P((360, 520))[0], P((360, 520))[1], P((560, 760))[0], P((560, 760))[1]), fill=70)
    from PIL import ImageFilter
    hl = hl.filter(ImageFilter.GaussianBlur(60 * SS))
    lighter = Image.new("RGB", img.size, MUSCLE_LIGHT)
    body_mask = Image.fromarray((LA.mask_of([blob(BODY)]) * 255).astype("uint8"))
    hl = Image.fromarray(np.minimum(np.array(hl), np.array(body_mask)))
    img = Image.composite(lighter, img, hl)
    img = paint(img, [blob(R_AUR)], AURICLE)
    # coronary vessels on the surface (fat-lined grooves)
    img = paint(img, [tube_poly(LAD, 26), tube_poly(RCA, 26)], FAT)
    img = paint(img, [tube_poly(LAD_V, 10)], BLUE)
    img = paint(img, [tube_poly(LAD, 11), tube_poly(RCA, 11)] + [tube_poly(dg, 8) for dg in DIAG], RED)
    # pulmonary trunk emerging from the right ventricle, in front of the aorta
    before = np.array(img)
    img = paint(img, [tube_poly(TRUNK, 70)], BLUE)
    cone = [(530, 640), (536, 520), (585, 508), (634, 520), (640, 640)]
    m = LA.mask_of([cone])
    a = np.array(img)
    a[m] = before[m]               # the trunk grows out of the ventricle wall
    img = Image.fromarray(a)
    d = ImageDraw.Draw(img)
    arc = [P(p) for p in LA.smooth([(536, 524), (585, 506), (634, 524)], False)]
    d.line(arc, fill=LINE, width=LA.STROKE, joint="curve")
    img = img.convert("RGBA")
    d = ImageDraw.Draw(img)
    cap(d, SVC[0], SVC[1], 78, BLUE_CAP)
    cap(d, IVC[0], IVC[1], 74, BLUE_CAP)
    cap(d, TRUNK[-1], TRUNK[-2], 70, BLUE_CAP)
    cap(d, RPA[-1], RPA[-2], 46, BLUE_CAP)
    for b in BRANCHES:
        cap(d, b[-1], b[-2], 34, RED_CAP)
    for v in RPV + LPV:
        cap(d, v[-1], v[-2], 34, RED_CAP)
    return img


if __name__ == "__main__":
    img = draw()
    img.resize((W, H), Image.LANCZOS).convert("RGB").save(Path(__file__).resolve().parent / "heart_ext.png")
    print("ok")
