"""Dark version of the style A thumbnail for 'Can Europeans buy VOO?': same layout (left panel with the struck-through
hook, 2-word question with the first word in the accent colour, a pill, an arrow to the key element) in the black,
monospace look of the dark edit. Red is the only accent."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw

D = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(D, "build_finance_demo.py")).read()
ns = {"__file__": os.path.join(D, "build_finance_demo.py")}
exec(src[: src.index("# --------------------------------------------------------------------------- script")], ns)
exec(src[src.index("# --------------------------------------------------------------------------- drawing helpers"):
         src.index("# --------------------------------------------------------------------------- scenes")], ns)
Cv, F, S = ns["Cv"], ns["F"], ns["S"]
BG, PANEL, FG, DIM, ERR = (12, 12, 15), (5, 5, 7), (238, 238, 238), (118, 118, 126), (232, 58, 64)
MONO, MONOB = "../../truetype/dejavu/DejaVuSansMono.ttf", "../../truetype/dejavu/DejaVuSansMono-Bold.ttf"
O = os.path.join(D, "thumbs")
os.makedirs(O, exist_ok=True)


def fit(cv, txt, font, max_w, start):
    size = start
    while size > 40 and cv.tlen(txt, font, size) > max_w:
        size -= 4
    return size


def big(cv, xy, txt, size, fill, font="InterDisplay-Black.otf"):
    cv.d.text((xy[0] * S, xy[1] * S), txt, font=F(font, size * S), fill=fill, anchor="ls")


def arrow(cv, pts, col, w=14):
    cv.line(pts, col, w)
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    ang = math.atan2(y2 - y1, x2 - x1)
    L = 46
    cv.poly([(x2 + 8 * math.cos(ang), y2 + 8 * math.sin(ang)),
             (x2 - L * math.cos(ang - 0.5), y2 - L * math.sin(ang - 0.5)),
             (x2 - L * math.cos(ang + 0.5), y2 - L * math.sin(ang + 0.5))], col)


cv = Cv(BG)
# wall of "buy VOO." tiles behind the right side, as in the opening of the video
for r in range(9):
    for c in range(10):
        x, y = 820 + c * 116, 20 + r * 118
        cv.rect([x, y, x + 100, y + 58], None, r=7, outline=(46, 46, 54), width=2)
        cv.text((x + 50, y + 36), "buy VOO.", MONO, 13, (74, 74, 82), anchor="ms")
# terminal window with the error: the key element
cv.shadow([1010, 300, 1850, 780], 14, blur=30, alpha=200, dy=0)
cv.rect([1010, 300, 1850, 780], (10, 10, 13), r=14, outline=(90, 90, 98), width=2)
for k, col in enumerate(((90, 90, 98), (90, 90, 98), (90, 90, 98))):
    cv.ellipse([1040 + k * 30, 324, 1056 + k * 30, 340], col)
cv.text((1050, 430), "> buy VOO", MONO, 50, FG, anchor="ls")
cv.text((1046, 610), "ERROR", MONOB, 150, ERR, anchor="ls")
cv.text((1050, 700), "not available in your region", MONO, 33, ERR, anchor="ls")
# left panel
cv.poly([(0, 0), (900, 0), (760, 1080), (0, 1080)], PANEL)
cv.line([(900, 0), (760, 1080)], (70, 70, 78), 3)
s1 = fit(cv, "VOO", "InterDisplay-Black.otf", 560, 260)
big(cv, (70, 300), "VOO", s1, FG)
w1 = cv.tlen("VOO", "InterDisplay-Black.otf", s1)
cv.line([(56, 300 - s1 * 0.36 + 10), (84 + w1, 300 - s1 * 0.36 - 16)], ERR, 22)
s2 = fit(cv, "BLOCKED?", "InterDisplay-Black.otf", 650, 200)
big(cv, (66, 520), "WHY", s2, ERR)
big(cv, (66, 700), "BLOCKED?", s2, FG)
pw = cv.tlen("IN EUROPE", MONOB, 54) + 70
cv.rect([70, 790, 70 + pw, 890], FG, r=50)
cv.text((105, 858), "IN EUROPE", MONOB, 54, BG, anchor="ls")
arrow(cv, [(560, 430), (760, 380), (990, 470)], FG)

im = cv.out().convert("RGB")
a = np.asarray(im, dtype=np.float32)
H_, W_ = a.shape[:2]
yy, xx = np.mgrid[0:H_, 0:W_]
vig = (1 - 0.18 * (((xx - W_ / 2) / (W_ / 2)) ** 2 + ((yy - H_ / 2) / (H_ / 2)) ** 2) ** 1.4).clip(0.8, 1)[..., None]
a = a * vig + np.random.default_rng(3).normal(0, 4, (H_, W_, 1))
out = Image.fromarray(a.clip(0, 255).astype(np.uint8)).resize((1280, 720), Image.LANCZOS)
out.save(os.path.join(O, "thumb_A_voo_dark.jpg"), quality=95)
sheet = Image.new("RGB", (1280 + 20 + 320, 720), (255, 255, 255))
sheet.paste(out, (0, 0))
sheet.paste(out.resize((320, 180), Image.LANCZOS), (1300, 0))
sheet.paste(out.resize((168, 94), Image.LANCZOS), (1300, 200))
light = Image.open(os.path.join(O, "thumb_A_voo.jpg")).resize((320, 180), Image.LANCZOS)
sheet.paste(light, (1300, 320))
sheet.save(os.path.join(O, "preview_dark.png"))
print("ok")
