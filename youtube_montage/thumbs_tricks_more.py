"""More thumbnail options for '7 Tricks Shops Use to Make You Spend More' (B4-B7), same paper, ink frame and rules as
thumbs_doodle.py: one idea per image, readable at feed size, nothing important in the bottom-right corner (duration badge).
Every claim is one the video makes: milk at the back (trick 7), the €199 -> €99 'half price' (trick 4), 4 x €25 (trick 6)."""
import os

import cairocffi as cairo
import numpy as np
from PIL import Image

from doodle_video import *  # noqa: F401,F403
from doodle_video import stk, tag, gift
from build_tricks import bag, candy, dress

OUT = os.path.join(D, "thumbs_doodle")
os.makedirs(OUT, exist_ok=True)
paper, _parr, PW, PH = make_paper(seed=8)


def render(name, ops_list, t=9.0):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_surface(paper, (W - PW) / 2, (H - PH) / 2)
    ctx.paint()
    ctx.set_source_rgba(0.42, 0.36, 0.28, 0.10)
    ctx.paint()
    for e in ops_list:
        e(ctx, t)
    Dr([stk(P_rect(22, 22, W - 44, H - 44, 14, r=10), 13)], 0, 0, seed=len(name))(ctx, t)
    surf.flush()
    a = np.frombuffer(surf.get_data(), np.uint8).reshape(H, W, 4)[..., [2, 1, 0]].copy()
    im = Image.fromarray(a).resize((1280, 720), Image.LANCZOS)
    im.save(os.path.join(OUT, name + ".jpg"), quality=92)
    return im


d = lambda ops, seed=1: Dr(ops, 0, 0, seed=seed)


def milk(x, y, s=1.0):
    """A milk carton with a gable top, standing on (x, y)."""
    w, h, r = 110 * s, 170 * s, 60 * s
    body = P_rect(x - w / 2, y - h, w, h, 0)
    roof = P_poly([(x - w / 2, y - h), (x - w / 2 + 12 * s, y - h - r), (x + w / 2 - 12 * s, y - h - r), (x + w / 2, y - h)], True)
    return [Fl(body, (250, 248, 242)), Fl(roof, (150, 186, 214)), stk(P_rect(x - w / 2, y - h, w, h, 5 * s), 6 * s), stk(roof, 6 * s),
            stk(P_line(x - w / 2 + 14 * s, y - h - r - 18 * s, x + w / 2 - 14 * s, y - h - r - 18 * s, 0, 1), 6 * s),
            ("g", "MILK", x, y - h * 0.38, int(40 * s), INK, HAND, "m")]


ims = []
# ---------------------------------------------------------------- B4: the cart that came for milk (trick 7, the store map)
cx, cy, cs = 1260, 720, 3.0                 # basket rim at y = cy - 80 cs = 480: everything in the pile starts below it
stuff = [d(gift(1180, 330, 0.85, PINK), 39), d(coffee(1440, 360, 0.75), 36),
         d(gift(1060, 450, 1.1), 31), d(bag(1290, 420, 1.3, HL), 32), d(dress(1540, 400, 1.0), 33),
         d(candy(1170, 480, 1.2, PINK), 34), d(candy(1430, 490, 1.1, (150, 186, 214)), 35)]
els = stuff + [d(cart(cx, cy, cs), 30), d(milk(1320, 255, 0.7), 38), circ(1320, 180, 95, 120, 0, ORANGE, 8, seed=3),
               Fig(380, 990, 1.2, poses=[("shrug", 0)], moods=[("worried", 0)], seed=5, enter="none", idle=0),
               T("I came", 110, 250, 200, INK, at=0, rot=-3), T("for milk.", 130, 460, 200, ORANGE, at=0, rot=-3)]
assert 130 + text_w("for milk.", 200) < 940, "B4 text runs into the cart"
ims.append(render("B4_came_for_milk", els))
# ---------------------------------------------------------------- B5: 'half price!' that never was (trick 4, the fake discount)
els = [d(tag(660, 360, 3.0, "€199", HL, 200)), strike(430, 380, 920, 310, 0, RED, 16),
       T("€99", 230, 900, 300, ORANGE, at=0, rot=-5), T("-50%", 1180, 420, 250, RED, at=0, rot=8),
       T("really?", 1200, 680, 170, INK, at=0, rot=-3),
       Fig(940, 1000, 1.1, poses=[("think", 0)], moods=[("smug", 0)], seed=4, enter="none", idle=0)]
ims.append(render("B5_half_price_really", els))
# ---------------------------------------------------------------- B6: the shopper on strings (shops pull your strings)
fx, fy, fs = 1250, 990, 2.05
PUP = dict(la=(-130, -150), ra=(130, 150), ll=(-10, -5), rl=(10, 5), lean=0, tilt=0)
hand_dx, hand_y, head_top = 68.9 * fs, fy - 304.1 * fs, fy - 325 * fs      # from Fig's limb geometry for this pose
bar = [stk(P_line(960, 150, 1540, 150, 0.01, 1), 14), stk(P_line(1250, 90, 1252, 230, 0.01, 2), 14)]
strings = [stk(P_line(990, 150, fx - hand_dx, hand_y, 0.0, 3), 6, GREY), stk(P_line(1510, 150, fx + hand_dx, hand_y, 0.0, 4), 6, GREY),
           stk(P_line(1250, 230, 1250, head_top, 0.0, 5), 6, GREY)]
ts = min(170, 900 / text_w("your strings.", 1))
els = [d(strings, 40), d(bar, 41), d(tag(1713, 234, 1.05, "SHOP", ORANGE, 56), 42),
       Fig(fx, fy, fs, poses=[(PUP, 0)], moods=[("worried", 0)], seed=6, enter="none", idle=0),
       T("shops pull", 110, 420, ts, INK, at=0, rot=-4), T("your strings.", 130, 640, ts, ORANGE, at=0, rot=-4)]
ims.append(render("B6_on_strings", els))
# ---------------------------------------------------------------- B7: pay later, spend more (trick 6, buy now pay later)
px, py, ps = 1400, 560, 3.2
els = [d(phone(px, py, ps)), d([Fl(P_rect(px - 230, py - 40, 460, 230, 0, r=40), ORANGE), stk(P_rect(px - 230, py - 40, 460, 230, 9, r=40), 9)], 4),
       T("4 × €25", px, py - 210, 96, INK, at=0, anchor="m"), T("PAY\nLATER", px, py + 55, 104, INK, at=0, anchor="m", lh=0.95),
       T("pay later,", 110, 380, 170, INK, at=0, rot=-3), T("spend", 140, 600, 200, RED, at=0, rot=-3),
       T("more.", 170, 810, 200, RED, at=0, rot=-3), arrow(P_bez((800, 700), (980, 720), (1140, 640)), 0, RED, 11, 0.0, head=36)]
ims.append(render("B7_pay_later", els))

sheet = Image.new("RGB", (1280 * 2 + 30, 730 * 2 + 10), (60, 60, 60))
for k, im in enumerate(ims):
    sheet.paste(im, (10 + (k % 2) * 1290, 10 + (k // 2) * 730))
sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(os.path.join(OUT, "sheet_B4_B7.jpg"), quality=88)
small = Image.new("RGB", (4 * 178 + 10, 114), (255, 255, 255))
for k, im in enumerate(ims):
    small.paste(im.resize((168, 94), Image.LANCZOS), (10 + k * 178, 10))
small.save(os.path.join(OUT, "feed_size_B4_B7.png"))
print("ok")
