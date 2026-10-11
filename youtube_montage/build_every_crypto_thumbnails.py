"""Dark thumbnails for 'Every Crypto Explained in 12 Minutes', in the look of the dark edit (black, monospace, red as the only accent).
A = style A layout: 'EVERY CRYPTO' on the left panel, the 12 boxes on the right, arrow to the red 'scam coins' box.
B = a glitched BTC coin over a wall of tickers, most of them struck through in red."""
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
Cv, S = ns["Cv"], ns["S"]
BG, PANEL, FG, DIM, ERR = (9, 9, 11), (4, 4, 6), (238, 238, 238), (118, 118, 126), (232, 58, 64)
MONO, MONOB = "../../truetype/dejavu/DejaVuSansMono.ttf", "../../truetype/dejavu/DejaVuSansMono-Bold.ttf"
BLACK = "InterDisplay-Black.otf"
O = os.path.join(D, "thumbs")
os.makedirs(O, exist_ok=True)
rng = np.random.default_rng(5)


def fit(cv, txt, font, max_w, start):
    size = start
    while size > 40 and cv.tlen(txt, font, size) > max_w:
        size -= 4
    return size


def arrow(cv, pts, col, w=14):
    cv.line(pts, col, w)
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    ang = math.atan2(y2 - y1, x2 - x1)
    L = 46
    cv.poly([(x2 + 8 * math.cos(ang), y2 + 8 * math.sin(ang)),
             (x2 - L * math.cos(ang - 0.5), y2 - L * math.sin(ang - 0.5)),
             (x2 - L * math.cos(ang + 0.5), y2 - L * math.sin(ang + 0.5))], col)


def glitch_rgb(a, box, seed, amt=1.0):
    g = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    reg = a[y0:y1, x0:x1].copy()
    for _ in range(7):
        y, hh = int(g.integers(0, reg.shape[0] - 30)), int(g.integers(6, 30))
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


# ---------------------------------------------------------------- A: the 12 boxes, arrow to the red one
BOXES = [("BTC", "bitcoin"), ("ETH", "ethereum"), ("SOL", "other chains"), ("L2", "layer 2s"),
         ("USDT", "stablecoins"), ("BNB", "exchange"), ("UNI", "DeFi"), ("DOGE", "memecoins"),
         ("NFT", "NFTs"), ("XMR", "privacy"), ("???", "scam coins"), ("€", "not crypto")]
cv = Cv(BG)
BW, BH, GX, GY, X0, Y0 = 228, 240, 18, 20, 930, 100
for k, (tick, lab) in enumerate(BOXES):
    x, y = X0 + (k % 4) * (BW + GX), Y0 + (k // 4) * (BH + GY)
    scam = tick == "???"
    cv.rect([x, y, x + BW, y + BH], (12, 12, 15) if not scam else (24, 8, 10), r=10,
            outline=ERR if scam else (78, 78, 86), width=6 if scam else 2)
    cv.text((x + 16, y + 34), f"{k + 1:02d}", MONO, 20, (74, 74, 82), anchor="ls")
    s = fit(cv, tick, BLACK, BW - 40, 84)
    cv.text((x + BW / 2, y + BH / 2 + 22), tick, BLACK, s, ERR if scam else FG, anchor="ms")
    cv.text((x + BW / 2, y + BH - 34), lab, MONO, 22, ERR if scam else DIM, anchor="ms")
cv.poly([(0, 0), (880, 0), (760, 1080), (0, 1080)], PANEL)
cv.line([(880, 0), (760, 1080)], (70, 70, 78), 3)
cv.text((72, 150), "> 12 boxes. every coin.", MONO, 34, DIM, anchor="ls")
s = fit(cv, "CRYPTO", BLACK, 680, 240)
cv.text((64, 400), "EVERY", BLACK, s, ERR, anchor="ls")
cv.text((64, 620), "CRYPTO", BLACK, s, FG, anchor="ls")
pw = cv.tlen("IN 12 MIN", MONOB, 58) + 76
cv.rect([72, 710, 72 + pw, 816], FG, r=53)
cv.text((110, 782), "IN 12 MIN", MONOB, 58, BG, anchor="ls")
xs, ys = X0 + 2 * (BW + GX), Y0 + 2 * (BH + GY)
arrow(cv, [(330, 880), (1430, 1012), (xs + BW / 2 - 14, ys + BH + 24)], FG)
a_img = finish(cv.out(), "thumb_A_crypto_dark.jpg")

# ---------------------------------------------------------------- B: glitched BTC coin over a wall of dying tickers
WALL = ["ETH", "SOL", "ADA", "XRP", "DOGE", "USDT", "USDC", "BNB", "TRX", "AVAX", "DOT", "LINK", "SHIB", "LTC", "BCH", "NEAR",
        "UNI", "XMR", "ZEC", "ATOM", "ALGO", "PEPE", "TON", "SUI", "APT", "ARB", "OP", "AAVE", "FIL", "ETC", "XLM", "HBAR",
        "ICP", "VET", "XTZ", "BONK", "WIF", "FLOKI", "MOG", "LUNA", "FTT", "SQUID", "MOONPUP", "FROGKING", "LAMBO", "FOMO",
        "PUPCOIN", "GIGAFROG"]
wall = Cv(BG)
k = 0
for r in range(10):
    for c in range(9):
        x, y = 780 + c * 136 + (r % 2) * 40, 70 + r * 104
        nm = WALL[k % len(WALL)]
        k += 1
        dead = rng.random() < 0.72
        wall.text((x, y), nm, MONO, 28, (54, 54, 62) if dead else (120, 120, 128), anchor="mm")
        if dead:
            w = wall.tlen(nm, MONO, 28) + 14
            wall.line([(x - w / 2, y), (x + w / 2, y)], (150, 40, 46), 3)
base = np.asarray(wall.out().convert("RGB"), dtype=np.float32)
ramp = np.clip((np.arange(base.shape[1]) - 760) / 380, 0.12, 1)[None, :, None]
base = (base - np.array(BG)) * ramp + np.array(BG)
im = Image.fromarray(base.clip(0, 255).astype(np.uint8))
lay = Cv(None)
cx, cy, R = 1360, 540, 290
lay.ellipse([cx - R - 30, cy - R - 30, cx + R + 30, cy + R + 30], BG)
lay.ellipse([cx - R, cy - R, cx + R, cy + R], None, outline=FG, width=20)
lay.ellipse([cx - R + 44, cy - R + 44, cx + R - 44, cy + R - 44], None, outline=(70, 70, 78), width=3)
lay.text((cx, cy + 72), "BTC", BLACK, 210, FG, anchor="ms")
lay.text((72, 150), "> every coin, explained", MONO, 34, DIM, anchor="ls")
s = fit(lay, "CRYPTO", BLACK, 680, 240)
lay.text((64, 400), "EVERY", BLACK, s, FG, anchor="ls")
lay.text((64, 620), "CRYPTO", BLACK, s, FG, anchor="ls")
lay.rect([72, 660, 72 + lay.tlen("CRYPTO", BLACK, s) - 8, 682], ERR)
lay.text((72, 800), "12 boxes · 12 minutes", MONOB, 46, ERR, anchor="ls")
im.paste(lay.out(), (0, 0), lay.out())
a = np.asarray(im.convert("RGB")).copy()
a = glitch_rgb(a, (cx - R - 40, cy - 120, cx + R + 40, cy + 150), 8, 0.45)
b_img = finish(Image.fromarray(a), "thumb_B_crypto_dark_coin.jpg")

# ---------------------------------------------------------------- comparison sheet (full size + YouTube sizes)
sheet = Image.new("RGB", (1280 * 2 + 20, 720 + 20 + 180), (255, 255, 255))
for j, t in enumerate((a_img, b_img)):
    sheet.paste(t, (j * 1300, 0))
    sheet.paste(t.resize((320, 180), Image.LANCZOS), (j * 1300, 740))
    sheet.paste(t.resize((168, 94), Image.LANCZOS), (j * 1300 + 340, 740))
sheet.save(os.path.join(O, "preview_crypto_dark.png"))
print("ok")
