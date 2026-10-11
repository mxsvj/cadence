"""Two more dark thumbnails for 'Can Europeans buy VOO?', to compare with the dark style A:
B = glitched VOO inside the EU ring of stars, red 'BLOCKED' stamp; C = VOO (blocked) -> ??? (its European twin), 'SAME 500 STOCKS'."""
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
Cv, F, S, star_pts = ns["Cv"], ns["F"], ns["S"], ns["star_pts"]
BG, FG, DIM, ERR = (9, 9, 11), (238, 238, 238), (118, 118, 126), (232, 58, 64)
MONO, MONOB = "../../truetype/dejavu/DejaVuSansMono.ttf", "../../truetype/dejavu/DejaVuSansMono-Bold.ttf"
BLACK = "InterDisplay-Black.otf"
O = os.path.join(D, "thumbs")
rng = np.random.default_rng(11)


def finish(im, name, vig_amt=0.18):
    a = np.asarray(im.convert("RGB"), dtype=np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    vig = (1 - vig_amt * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) ** 1.4).clip(0.8, 1)[..., None]
    a = a * vig + rng.normal(0, 4, (h, w, 1))
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8)).resize((1280, 720), Image.LANCZOS)
    out.save(os.path.join(O, name), quality=95)
    return out


def glitch_rgb(a, box, seed, amt=1.0):
    """Slice displacement + red/cyan split inside box (x0, y0, x1, y1) of an RGB array."""
    g = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    reg = a[y0:y1, x0:x1].copy()
    for _ in range(6):
        y, hh = int(g.integers(0, reg.shape[0] - 30)), int(g.integers(6, 30))
        reg[y:y + hh] = np.roll(reg[y:y + hh], int(g.integers(-60, 60) * amt), axis=1)
    k = int(12 * amt)
    out = reg.copy()
    out[..., 0] = np.roll(reg[..., 0], k, axis=1)
    out[..., 2] = np.roll(reg[..., 2], -k, axis=1)
    a[y0:y1, x0:x1] = out
    return a


# ---------------------------------------------------------------- B: glitched VOO in the EU ring, BLOCKED stamp
cv = Cv(BG)
for j in range(12):
    ang = math.radians(-90 + 30 * j)
    cv.poly(star_pts(960 + 455 * math.cos(ang), 540 + 455 * math.sin(ang), 30), (205, 205, 212))
cv.text((960, 265), "location = EUROPE", MONO, 34, DIM, anchor="ms")
cv.text((960, 650), "VOO", BLACK, 320, FG, anchor="ms")
base = np.asarray(cv.out().convert("RGB")).copy()
base = glitch_rgb(base, (380, 380, 1540, 700), 4, 0.4)
im = Image.fromarray(base)
st = Cv(None, size=(620, 220))
st.rect([14, 14, 606, 206], BG, r=10, outline=ERR, width=12)
st.text((310, 148), "BLOCKED", MONOB, 104, ERR, anchor="ms")
st = st.out().rotate(9, expand=True, resample=Image.BICUBIC)
im.paste(st, (1010, 640), st)
b = finish(im, "thumb_B_voo_dark_ring.jpg")

# ---------------------------------------------------------------- C: VOO (blocked) -> ??? , SAME 500 STOCKS
cv = Cv(BG)


def grid(cx, cy, col, r=7, sp=26, cols=16, rows=12):
    for rr in range(rows):
        for c in range(cols):
            x, y = cx + (c - (cols - 1) / 2) * sp, cy + (rr - (rows - 1) / 2) * sp
            cv.ellipse([x - r, y - r, x + r, y + r], col)


cv.text((500, 300), "VOO", BLACK, 200, (150, 150, 158), anchor="ms")
grid(500, 560, (88, 88, 96))
cv.line([(330, 420), (670, 700)], ERR, 30, caps=True)
cv.line([(670, 420), (330, 700)], ERR, 30, caps=True)
cv.text((1420, 300), "???", BLACK, 200, FG, anchor="ms")
grid(1420, 560, FG)
cv.line([(800, 560), (1080, 560)], FG, 14)
cv.poly([(1112, 560), (1064, 530), (1064, 590)], FG)
cv.text((960, 960), "SAME 500 STOCKS", MONOB, 92, FG, anchor="ms")
c = finish(cv.out(), "thumb_C_voo_dark_twin.jpg")

# ---------------------------------------------------------------- preview: full size + phone size, next to the dark A
a = Image.open(os.path.join(O, "thumb_A_voo_dark.jpg"))
sheet = Image.new("RGB", (1280 + 20 + 320, 3 * 720 + 40), (255, 255, 255))
for i, img in enumerate((b, c, a)):
    sheet.paste(img, (0, i * 740))
    sheet.paste(img.resize((320, 180), Image.LANCZOS), (1300, i * 740))
    sheet.paste(img.resize((168, 94), Image.LANCZOS), (1300, i * 740 + 200))
sheet.save(os.path.join(O, "preview_dark2.png"))
print("ok")
