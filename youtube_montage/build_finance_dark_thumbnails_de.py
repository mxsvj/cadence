"""Two more dark thumbnails for 'Can Europeans buy VOO?':
D = the €4 number (the only real difference), centred and huge; E = a dark-mode broker app with VOO locked, 'LOCKED OUT?'."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(D, "build_finance_demo.py")).read()
ns = {"__file__": os.path.join(D, "build_finance_demo.py")}
exec(src[: src.index("# --------------------------------------------------------------------------- script")], ns)
exec(src[src.index("# --------------------------------------------------------------------------- drawing helpers"):
         src.index("# --------------------------------------------------------------------------- scenes")], ns)
Cv, F, S = ns["Cv"], ns["F"], ns["S"]
BG, FG, DIM, ERR = (9, 9, 11), (238, 238, 238), (118, 118, 126), (232, 58, 64)
MONO, MONOB = "../../truetype/dejavu/DejaVuSansMono.ttf", "../../truetype/dejavu/DejaVuSansMono-Bold.ttf"
BLACK = "InterDisplay-Black.otf"
O = os.path.join(D, "thumbs")
rng = np.random.default_rng(21)


def finish(im, name):
    a = np.asarray(im.convert("RGB"), dtype=np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    vig = (1 - 0.18 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) ** 1.4).clip(0.8, 1)[..., None]
    a = a * vig + rng.normal(0, 4, (h, w, 1))
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8)).resize((1280, 720), Image.LANCZOS)
    out.save(os.path.join(O, name), quality=95)
    return out


def lock(cv, cx, cy, s, col, bg):
    cv.arc([cx - 34 * s, cy - 78 * s, cx + 34 * s, cy - 8 * s], 180, 360, col, 14 * s)
    cv.line([(cx - 34 * s, cy - 44 * s), (cx - 34 * s, cy - 10 * s)], col, 14 * s)
    cv.line([(cx + 34 * s, cy - 44 * s), (cx + 34 * s, cy - 10 * s)], col, 14 * s)
    cv.rect([cx - 52 * s, cy - 14 * s, cx + 52 * s, cy + 62 * s], col, r=12 * s)
    cv.ellipse([cx - 9 * s, cy + 10 * s, cx + 9 * s, cy + 28 * s], bg)
    cv.rect([cx - 4 * s, cy + 20 * s, cx + 4 * s, cy + 42 * s], bg)


# ---------------------------------------------------------------- D: €4 / year, the only difference
cv = Cv(BG)
cv.text((960, 200), "VOO  vs  EU TWIN", MONOB, 72, FG, anchor="ms")
cv.line([(660, 236), (1260, 236)], (70, 70, 78), 3)
w4 = cv.tlen("€4", BLACK, 560)
wy = cv.tlen(" / year", MONO, 96)
x = 960 - (w4 + wy) / 2
cv.text((x, 790), "€4", BLACK, 560, FG, anchor="ls")
cv.text((x + w4, 790), " / year", MONO, 96, DIM, anchor="ls")
cv.text((960, 950), "THE ONLY DIFFERENCE", MONOB, 64, ERR, anchor="ms")
d = finish(cv.out(), "thumb_D_voo_dark_4eur.jpg")

# ---------------------------------------------------------------- E: dark-mode broker app, VOO locked
cv = Cv(BG)
for i in range(-10, 30):
    cv.line([(i * 120, 1080), (i * 120 + 700, 0)], (255, 255, 255, 6), 2)
k = 1.42
p = Cv(None, size=(int(420 * k), int(800 * k)))
q = lambda *v: [z * k for z in v]
p.shadow(q(10, 10, 410, 790), 56 * k, blur=30, alpha=200, dy=0)
p.rect(q(10, 10, 410, 790), (40, 40, 46), r=56 * k)
p.rect(q(18, 18, 402, 782), (14, 14, 18), r=48 * k)
p.rect(q(165, 38, 255, 62), (40, 40, 46), r=12 * k)
p.text(q(46, 140), "Search", "Inter-ExtraBold.otf", 42 * k, FG, anchor="ls")
p.rect(q(44, 168, 376, 236), (30, 30, 36), r=34 * k)
p.text(q(80, 214), "VOO", "Inter-SemiBold.otf", 30 * k, FG, anchor="ls")
p.rect(q(44, 268, 376, 470), (24, 24, 30), r=22 * k, outline=(60, 30, 34), width=3)
p.text(q(70, 330), "VOO", "Inter-Black.otf", 44 * k, FG, anchor="ls")
p.text(q(72, 364), "S&P 500 ETF · USA", "Inter-SemiBold.otf", 19 * k, DIM, anchor="ls")
p.rect(q(66, 392, 354, 446), (60, 22, 26), r=27 * k)
p.text(q(210, 428), "NOT AVAILABLE", "Inter-ExtraBold.otf", 22 * k, ERR, anchor="ms")
for y, w in ((520, 330), (570, 220), (650, 330), (700, 260)):
    p.rect(q(44, y, 44 + w, y + 26), (28, 28, 34), r=13 * k)
ph = p.out().rotate(-6, expand=True, resample=Image.BICUBIC)
base = cv.out()
glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse([1150, 250, 1750, 850], fill=ERR + (60,))
base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
base.alpha_composite(ph, (1060, 0))
cv.im = base.resize((1920 * S, 1080 * S), Image.LANCZOS)
cv.d = ImageDraw.Draw(cv.im, "RGBA")
cv.ellipse([1560, 330, 1760, 530], ERR)
lock(cv, 1660, 430, 1.05, FG, ERR)
s2 = 210
cv.d.text((66 * S, 430 * S), "LOCKED", font=F(BLACK, s2 * S), fill=ERR, anchor="ls")
cv.d.text((66 * S, 640 * S), "OUT?", font=F(BLACK, s2 * S), fill=FG, anchor="ls")
pw = cv.tlen("EU INVESTORS", MONOB, 54) + 70
cv.rect([70, 730, 70 + pw, 830], FG, r=50)
cv.text((105, 798), "EU INVESTORS", MONOB, 54, BG, anchor="ls")
e = finish(cv.out(), "thumb_E_voo_dark_locked.jpg")

sheet = Image.new("RGB", (1280 + 20 + 320, 2 * 720 + 20), (255, 255, 255))
for i, img in enumerate((d, e)):
    sheet.paste(img, (0, i * 740))
    sheet.paste(img.resize((320, 180), Image.LANCZOS), (1300, i * 740))
    sheet.paste(img.resize((168, 94), Image.LANCZOS), (1300, i * 740 + 200))
sheet.save(os.path.join(O, "preview_dark3.png"))
print("ok")
