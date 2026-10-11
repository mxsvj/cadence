"""Four more dark thumbnails for 'Every Crypto Explained in 12 Minutes' (black, monospace, red as the only accent):
D = terminal that 'explains' each box, the scam line in red; E = a giant '12' with 'TYPES OF CRYPTO';
F = three crash cards (LUNA, FTT, NFTs); G = 'ONE OF THESE ISN'T CRYPTO' with BTC, ETH, USDT and the euro."""
import math
import os

import numpy as np
from PIL import Image

D = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(D, "build_finance_demo.py")).read()
ns = {"__file__": os.path.join(D, "build_finance_demo.py")}
exec(src[: src.index("# --------------------------------------------------------------------------- script")], ns)
exec(src[src.index("# --------------------------------------------------------------------------- drawing helpers"):
         src.index("# --------------------------------------------------------------------------- scenes")], ns)
Cv, star_pts = ns["Cv"], ns["star_pts"]
BG, PANEL, FG, DIM, ERR = (9, 9, 11), (4, 4, 6), (238, 238, 238), (118, 118, 126), (232, 58, 64)
LINE = (78, 78, 86)
MONO, MONOB = "../../truetype/dejavu/DejaVuSansMono.ttf", "../../truetype/dejavu/DejaVuSansMono-Bold.ttf"
BLACK = "InterDisplay-Black.otf"
O = os.path.join(D, "thumbs")
os.makedirs(O, exist_ok=True)
rng = np.random.default_rng(21)


def fit(cv, txt, font, max_w, start):
    size = start
    while size > 40 and cv.tlen(txt, font, size) > max_w:
        size -= 4
    return size


def glitch_rgb(a, box, seed, amt=1.0):
    g = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    reg = a[y0:y1, x0:x1].copy()
    for _ in range(6):
        y, hh = int(g.integers(0, reg.shape[0] - 20)), int(g.integers(5, 20))
        reg[y:y + hh] = np.roll(reg[y:y + hh], int(g.integers(-60, 60) * amt), axis=1)
    k = int(12 * amt)
    out = reg.copy()
    out[..., 0] = np.roll(reg[..., 0], k, axis=1)
    out[..., 2] = np.roll(reg[..., 2], -k, axis=1)
    a[y0:y1, x0:x1] = out
    return a


def finish(im, name, vig_amt=0.16):
    a = np.asarray(im.convert("RGB"), dtype=np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    vig = (1 - vig_amt * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) ** 1.4).clip(0.82, 1)[..., None]
    a = a * vig + rng.normal(0, 4, (h, w, 1))
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8)).resize((1280, 720), Image.LANCZOS)
    out.save(os.path.join(O, name), quality=95)
    return out


def coin(cv, x, y, r, tick, col=FG, fill=(14, 14, 17), inner=(70, 70, 78)):
    cv.ellipse([x - r - 20, y - r - 20, x + r + 20, y + r + 20], BG)
    cv.ellipse([x - r, y - r, x + r, y + r], fill, outline=col, width=14)
    cv.ellipse([x - r + 30, y - r + 30, x + r - 30, y + r - 30], None, outline=inner, width=3)
    cv.text((x, y + r * 0.27), tick, BLACK, fit(cv, tick, BLACK, r * 1.45, int(r * 0.78)), col, anchor="ms")


def title_left(cv, kicker, red_line):
    cv.text((72, 150), kicker, MONO, 34, DIM, anchor="ls")
    s = fit(cv, "CRYPTO", BLACK, 680, 240)
    cv.text((64, 400), "EVERY", BLACK, s, FG, anchor="ls")
    cv.text((64, 620), "CRYPTO", BLACK, s, FG, anchor="ls")
    cv.text((72, 760), red_line, MONOB, 54, ERR, anchor="ls")


# ---------------------------------------------------------------- D: terminal explaining each box, the scam line in red
cv = Cv(BG)
title_left(cv, "> 12 boxes. 12 minutes.", "explained.")
TX0, TY0, TX1, TY1 = 860, 150, 1860, 930
cv.shadow([TX0, TY0, TX1, TY1], 14, blur=30, alpha=200, dy=0)
cv.rect([TX0, TY0, TX1, TY1], (10, 10, 13), r=14, outline=(90, 90, 98), width=2)
for k in range(3):
    cv.ellipse([TX0 + 30 + k * 30, TY0 + 24, TX0 + 46 + k * 30, TY0 + 40], (90, 90, 98))
cv.text((TX0 + 50, TY0 + 130), "> explain crypto --all", MONO, 44, DIM, anchor="ls")
ROWS = [("[ok] bitcoin", FG), ("[ok] ethereum", FG), ("[ok] stablecoins", FG), ("[??] memecoins", DIM)]
for k, (txt, col) in enumerate(ROWS):
    cv.text((TX0 + 50, TY0 + 240 + k * 92), txt, MONO, 58, col, anchor="ls")
cv.text((TX0 + 50, TY0 + 240 + 4 * 92 + 18), "[!!] scam coins", MONOB, 70, ERR, anchor="ls")
for k in range(12):
    x = TX0 + 52 + k * 58
    cv.rect([x, TY1 - 110, x + 44, TY1 - 66], ERR if k == 10 else FG)
cv.text((TX0 + 52 + 12 * 58 + 20, TY1 - 72), "12/12", MONOB, 40, FG, anchor="ls")
a = np.asarray(cv.out().convert("RGB")).copy()
yr = TY0 + 240 + 4 * 92 + 18
reg = a[yr - 70:yr + 18, TX0 + 30:TX0 + 720]                  # red/cyan split only, the line stays readable
reg[..., 0], reg[..., 2] = np.roll(reg[..., 0], 6, axis=1), np.roll(reg[..., 2], -6, axis=1)
d_img = finish(Image.fromarray(a), "thumb_D_crypto_dark_terminal.jpg")

# ---------------------------------------------------------------- E: a giant 12, 'TYPES OF CRYPTO'
cv = Cv(BG)
cv.text((40, 900), "12", BLACK, 720, FG, anchor="ls")
w12 = cv.tlen("12", BLACK, 720)
XR = 40 + w12 + 50
cv.line([(XR - 25, 200), (XR - 25, 880)], LINE, 3)
cv.text((XR, 250), "> every coin fits in one", MONO, 34, DIM, anchor="ls")
s = fit(cv, "CRYPTO", BLACK, 1860 - XR, 220)
cv.text((XR - 6, 470), "TYPES OF", BLACK, int(s * 0.72), FG, anchor="ls")
cv.text((XR - 8, 680), "CRYPTO", BLACK, s, ERR, anchor="ls")
pw = cv.tlen("IN 12 MIN", MONOB, 58) + 76
cv.rect([XR, 760, XR + pw, 866], FG, r=53)
cv.text((XR + 38, 832), "IN 12 MIN", MONOB, 58, BG, anchor="ls")
e_img = finish(cv.out(), "thumb_E_crypto_dark_12.jpg")

# ---------------------------------------------------------------- F: three crash cards
cv = Cv(BG)
cv.text((75, 250), "EVERY CRYPTO", BLACK, fit(cv, "EVERY CRYPTO", BLACK, 1150, 190), FG, anchor="ls")
cv.text((80, 330), "> even the crashes", MONOB, 46, ERR, anchor="ls")
pw = cv.tlen("IN 12 MIN", MONOB, 58) + 76
cv.rect([1845 - pw, 150, 1845, 256], FG, r=53)
cv.text((1845 - pw + 38, 222), "IN 12 MIN", MONOB, 58, BG, anchor="ls")
CARDS = [("LUNA · 2022", "−99%", [30, 34, 42, 40, 52, 60, 70, 66, 78, 4, 2]),
         ("FTT · 2022", "−90%", [50, 54, 52, 60, 58, 64, 62, 66, 60, 12, 6]),
         ("NFTs · since 2021", "−95%", [10, 18, 40, 70, 80, 72, 50, 30, 14, 6, 4])]
CW, CY0, CY1 = 540, 400, 960
for j, (lab, pct, path) in enumerate(CARDS):
    x0 = 75 + j * (CW + 45)
    cv.rect([x0, CY0, x0 + CW, CY1], (13, 13, 16), r=12, outline=LINE, width=2)
    cv.text((x0 + 32, CY0 + 62), lab, MONO, 34, DIM, anchor="ls")
    gx0, gx1, gy0, gy1 = x0 + 40, x0 + CW - 40, CY0 + 100, CY0 + 300
    hi = max(path)
    pts = [(gx0 + k * (gx1 - gx0) / (len(path) - 1), gy1 - v / hi * (gy1 - gy0)) for k, v in enumerate(path)]
    cv.line(pts[:-2], FG, 8)
    cv.line(pts[-3:], ERR, 8)
    cv.text((x0 + CW / 2, CY1 - 60), pct, BLACK, fit(cv, pct, BLACK, CW - 60, 170), ERR, anchor="ms")
f_img = finish(cv.out(), "thumb_F_crypto_dark_crashes.jpg")

# ---------------------------------------------------------------- G: ONE OF THESE ISN'T CRYPTO
cv = Cv(BG)
s = fit(cv, "ONE OF THESE", BLACK, 1500, 170)
cv.text((70, 230), "ONE OF THESE", BLACK, s, FG, anchor="ls")
cv.text((70, 420), "ISN’T CRYPTO", BLACK, s, ERR, anchor="ls")
for tick, x in (("BTC", 270), ("ETH", 650), ("USDT", 1030)):
    coin(cv, x, 720, 165, tick)
ex, ey, er = 1500, 700, 185
for k in range(12):
    ang = math.radians(-90 + 30 * k)
    cv.poly(star_pts(ex + (er + 52) * math.cos(ang), ey + (er + 52) * math.sin(ang), 17), (205, 205, 212))
coin(cv, ex, ey, er, "€")
cv.text((1760, 400), "?", BLACK, 300, ERR, anchor="ms")
g_img = finish(cv.out(), "thumb_G_crypto_dark_euro.jpg")

# ---------------------------------------------------------------- comparison sheet (full size + YouTube sizes)
imgs = (d_img, e_img, f_img, g_img)
sheet = Image.new("RGB", (1280 * 2 + 20, (720 + 20 + 180 + 30) * 2), (255, 255, 255))
for j, t in enumerate(imgs):
    x, y = (j % 2) * 1300, (j // 2) * 950
    sheet.paste(t, (x, y))
    sheet.paste(t.resize((320, 180), Image.LANCZOS), (x, y + 740))
    sheet.paste(t.resize((168, 94), Image.LANCZOS), (x + 340, y + 740))
sheet.save(os.path.join(O, "preview_crypto_dark_dg.png"))
print("ok")
