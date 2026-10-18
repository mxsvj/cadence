"""Channel avatar and banner for 'Euro Unboxed' in the doodle style of the videos: cream paper, marker ink, one orange hero.
Avatar: 800x800 (YouTube shows it as a circle, down to ~48 px, so one or two shapes only). Banner: 2560x1440 with the
wordmark inside the 1546x423 area every device shows; the doodles outside it only appear on wide screens and TVs."""
import os

import cairocffi as cairo
import numpy as np
from PIL import Image, ImageDraw

from doodle_video import *  # noqa: F401,F403
from doodle_video import stk

OUT = os.path.join(D, "branding_doodle")
os.makedirs(OUT, exist_ok=True)
paper, _parr, PW, PH = make_paper(seed=11)
d = lambda ops, seed=1: Dr(ops, 0, 0, seed=seed)


def render(name, els, size, virtual, t=9.0):
    """Draw in 'virtual' units (the 1920x1080 world of the videos) and scale to the output size."""
    w, h = size
    k = w / virtual[0]
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    ctx = cairo.Context(surf)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.scale(k, k)
    ctx.set_source_surface(paper, (virtual[0] - PW) / 2, (virtual[1] - PH) / 2)
    ctx.paint()
    for e in els:
        e(ctx, t)
    surf.flush()
    a = np.frombuffer(surf.get_data(), np.uint8).reshape(h, w, 4)[..., [2, 1, 0]].copy()
    im = Image.fromarray(a)
    im.save(os.path.join(OUT, name + ".png"))
    return im


def box(x, y, s=1.0):
    """An opened cardboard box, flaps up, seen slightly from above."""
    kraft, dark = (222, 184, 135), (196, 152, 104)
    fw, fh = 300 * s, 200 * s
    front = P_poly([(x - fw / 2, y), (x + fw / 2, y), (x + fw / 2, y + fh), (x - fw / 2, y + fh)], True)
    inside = P_poly([(x - fw / 2, y), (x - fw / 2 + 40 * s, y - 50 * s), (x + fw / 2 + 40 * s, y - 50 * s), (x + fw / 2, y)], True)
    side = P_poly([(x + fw / 2, y), (x + fw / 2 + 40 * s, y - 50 * s), (x + fw / 2 + 40 * s, y + fh - 50 * s), (x + fw / 2, y + fh)], True)
    fl = P_poly([(x - fw / 2, y), (x - fw / 2 - 70 * s, y - 120 * s), (x - fw / 2 - 20 * s, y - 150 * s), (x - fw / 2 + 40 * s, y - 50 * s)], True)
    fr = P_poly([(x + fw / 2 + 40 * s, y - 50 * s), (x + fw / 2 + 130 * s, y - 120 * s), (x + fw / 2 + 110 * s, y - 20 * s), (x + fw / 2, y)], True)
    return [Fl(inside, (120, 90, 60)), Fl(fl, dark), Fl(fr, dark), Fl(side, dark), Fl(front, kraft),
            stk(inside, 6 * s), stk(fl, 6 * s), stk(fr, 6 * s), stk(side, 6 * s), stk(front, 7 * s),
            stk(P_line(x - fw / 2 + 30 * s, y + 60 * s, x + fw / 2 - 30 * s, y + 60 * s, 0.02, 3), 4 * s, GREY)]


def pops(x, y, s=1.0):
    """Little motion strokes: the coin just jumped out."""
    return [stk(P_line(x - 150 * s, y - 40 * s, x - 205 * s, y - 70 * s, 0.05, 1), 7 * s), stk(P_line(x - 140 * s, y + 40 * s, x - 205 * s, y + 55 * s, 0.05, 2), 7 * s),
            stk(P_line(x + 150 * s, y - 40 * s, x + 205 * s, y - 70 * s, 0.05, 3), 7 * s), stk(P_line(x + 145 * s, y + 40 * s, x + 205 * s, y + 55 * s, 0.05, 4), 7 * s),
            stk(P_line(x, y - 150 * s, x + 6 * s, y - 210 * s, 0.05, 5), 7 * s)]


def big_coin(x, y, r):
    return [Fl(P_ell(x, y, r, r, 1, closed=True), ORANGE), stk(P_ell(x, y, r, r, 3, 0.06), r / 12),
            stk(P_ell(x, y, r * 0.8, r * 0.8, 2, 0.08), r / 30, (190, 98, 24)), ("g", "€", x - r * 0.02, y + r * 0.34, int(r * 1.05), INK, HAND, "m")]


# ---------------------------------------------------------------- avatars (virtual 1080 x 1080, shown as a circle)
V1 = (1080, 1080)
av1 = render("avatar_A_coin", [d(big_coin(540, 540, 330), 3), d(pops(540, 540, 2.3), 4)], (800, 800), V1)
av2 = render("avatar_B_box", [d(box(540, 690, 1.25), 5), d(big_coin(565, 380, 175), 6), d(pops(565, 380, 1.2), 7)], (800, 800), V1)

# ---------------------------------------------------------------- banner (virtual 1920 x 1080 -> 2560 x 1440)
# safe area in virtual units: x 380-1540, y 381-699; everything that carries meaning stays inside it
X0, X1 = 690, 1510
ws = min(150, (X1 - X0) / text_w("Euro Unboxed", 100) * 100)
t1, t2 = "money, explained simply.", "for Europeans."
ts = min(62, (1530 - X0 - 8 - 22) / (text_w(t1, 100) + text_w(t2, 100)) * 100)
w1 = text_w(t1, ts)
x2 = X0 + 8 + w1 + 22
els = [d(box(500, 580, 0.55), 8), d(big_coin(512, 500, 62), 9), d(pops(512, 500, 0.45), 10),
       T("Euro Unboxed", X0, 548, ws, INK, at=0, rot=-1.5),
       T(t1, X0 + 8, 640, ts, INK, at=0, rot=-1),
       T(t2, x2, 640 - 0.017 * (x2 - X0), ts, ORANGE, at=0, rot=-1),
       under(x2, x2 + text_w(t2, ts), 660 - 0.017 * (x2 - X0), 0, ORANGE, 7, 0.0, seed=4, wavy=True)]
assert x2 + text_w(t2, ts) < 1540, "tagline leaves the safe area"
# outside the safe area: quiet doodles for wide screens
els += [d(piggy(200, 600, 0.9), 20), d([stk(P_line(1620, 680, 1840, 680, 0.01, 1), 6)], 21),
        d([stk(P_rect(1640 + k * 55, 680 - hgt, 40, hgt, 4), 5) for k, hgt in enumerate((50, 80, 120, 175))], 22),
        d(coin(310, 470, 0.7), 23), d(coin(1720, 470, 0.6, HL), 24)]
banner = render("banner_2560x1440", els, (2560, 1440), (1920, 1080))

# ---------------------------------------------------------------- previews: avatar as YouTube crops it, banner safe areas
pv = Image.new("RGB", (820, 540), (255, 255, 255))
for k, im in enumerate((av1, av2)):
    for j, sz in enumerate((240, 88, 48)):
        c = im.resize((sz, sz), Image.LANCZOS)
        m = Image.new("L", (sz, sz), 0)
        ImageDraw.Draw(m).ellipse((0, 0, sz - 1, sz - 1), fill=255)
        pv.paste(c, (30 + j * 260, 20 + k * 260 + (240 - sz) // 2), m)
pv.save(os.path.join(OUT, "preview_avatars.png"))
b = banner.copy()
dr = ImageDraw.Draw(b)
dr.rectangle(((2560 - 1546) // 2, (1440 - 423) // 2, (2560 + 1546) // 2, (1440 + 423) // 2), outline=(220, 40, 40), width=6)
dr.rectangle((0, (1440 - 423) // 2, 2559, (1440 + 423) // 2), outline=(40, 90, 220), width=4)
b.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, "preview_banner_zones.png"))
print("ok")
