"""Louder thumbnail options for '7 Tricks Shops Use to Make You Spend More' (B8-B11). Same paper, ink and frame as the
others, pushed for the feed: a big flat block of colour behind half the frame (cream alone melts into YouTube's light mode),
a shocked face big enough to read at 168 px, two to four words, objects cropped by the frame. No glow, no outlines on text.
Every number is one the video uses: €9.99 -> €10 (trick 1), 'half price' that is really about 17% off (trick 4)."""
import os
import random

import cairocffi as cairo
import numpy as np
from PIL import Image

from doodle_video import *  # noqa: F401,F403
from doodle_video import stk, tag

OUT = os.path.join(D, "thumbs_doodle")
os.makedirs(OUT, exist_ok=True)
paper, _parr, PW, PH = make_paper(seed=8)
WHITE = (250, 248, 242)


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


def block(pts, col):
    """A flat slab of colour with a hand-drawn edge, bleeding off the frame."""
    return d([Fl(P_poly(pts, True), col), stk(P_poly(pts), 9)], 90)


def shock(x, y, r, look=0.0, hands=True):
    """Big head-and-shoulders stick figure, eyes wide, mouth open, hands thrown up."""
    head = P_ell(x, y, r, r * 1.03, 2, 0.08, closed=True)
    o = []
    if hands:
        sx, sy = x, y + 1.45 * r                                # hands thrown up and out, clear of the head
        for side in (-1, 1):
            o.append(stk(P_poly([(sx, sy), (x + side * 1.0 * r, y + 1.25 * r), (x + side * 1.45 * r, y + 0.45 * r)]), r / 19))
    o += [stk(P_line(x, y + r, x, H + 40, 0.01, 1), r / 19), Fl(head, WHITE), stk(head, r / 19)]
    for k, ex in enumerate((x - 0.34 * r, x + 0.34 * r)):
        ey = y - 0.08 * r
        o += [Fl(P_ell(ex, ey, 0.17 * r, 0.19 * r, k, closed=True), (255, 255, 255)), stk(P_ell(ex, ey, 0.17 * r, 0.19 * r, k + 3, 0.08), r / 40),
              Fl(P_ell(ex + look * 0.07 * r, ey + 0.02 * r, 0.075 * r, 0.08 * r, k + 5, closed=True), INK),
              stk(P_arc(ex, ey - 0.33 * r, 0.17 * r, 0.09 * r, 200, 340), r / 32)]
    o += [Fl(P_ell(x, y + 0.45 * r, 0.14 * r, 0.2 * r, 7, closed=True), INK)]
    for side in (-1, 1):                                       # little shock strokes next to the head
        for k, (a0, a1) in enumerate(((1.18, 1.42), (1.25, 1.55))):
            ang = (-0.75 + k * 0.45)
            o.append(stk(P_line(x + side * a0 * r * np.cos(ang), y + a0 * r * np.sin(ang), x + side * a1 * r * np.cos(ang),
                                y + a1 * r * np.sin(ang), 0.0, k), r / 30))
    return o


def receipt(x0, y0, x1, y1, n, seed=3):
    rr = random.Random(seed)
    zig = [(x1, y1)] + [(x1 - (k + 1) * (x1 - x0) / 12, y1 + (18 if k % 2 == 0 else 0)) for k in range(12)]
    pts = [(x0, y0), (x1, y0)] + zig
    o = [Fl(P_poly(pts, True), WHITE), stk(P_poly(pts, True), 7)]
    step = (y1 - y0 - 260) / n
    for k in range(n):
        yy = y0 + 70 + k * step
        o += [stk(P_line(x0 + 40, yy, x0 + 40 + rr.uniform(110, 220), yy, 0.02, k), 6, GREY),
              stk(P_line(x1 - 120, yy, x1 - 40, yy, 0.02, k + 20), 6, GREY)]
    return o


ims = []
# ---------------------------------------------------------------- B8: for MILK?! (trick 7, the store map)
els = [block([(1060, -20), (1940, -20), (1940, 1100), (1230, 1100)], ORANGE),
       d(receipt(1250, -30, 1730, 860, 9)),
       T("TOTAL", 1285, 795, 64, INK, at=0), T("€187", 1475, 810, 130, RED, at=0, rot=-4),
       d(shock(560, 690, 200, look=1.0), 5),
       T("I came for", 90, 200, 140, INK, at=0, rot=-3), T("MILK?!", 140, 430, 230, RED, at=0, rot=-3)]
assert 140 + text_w("MILK?!", 230) < 1060
ims.append(render("B8_milk_receipt", els))
# ---------------------------------------------------------------- B9: the -50% poster that is really -17% (trick 4)
poster = [(150, 170), (1050, 130), (1080, 720), (170, 760)]
els = [block([(1150, -20), (1940, -20), (1940, 1100), (1030, 1100)], HL),
       d([Fl(P_poly(poster, True), RED), stk(P_poly(poster, True), 10)], 3),
       T("SALE", 610, 300, 110, WHITE, at=0, anchor="m", rot=-2), T("-50%", 615, 620, 330, WHITE, at=0, anchor="m", rot=-2),
       cross(615, 450, 330, 0, INK, 24),
       T("real:", 1250, 330, 130, INK, at=0, rot=-4), T("-17%", 1200, 640, 300, RED, at=0, rot=-4),
       arrow(P_bez((900, 880), (1050, 960), (1250, 780)), 0, INK, 12, 0.0, head=40)]
ims.append(render("B9_fake_sale", els))
# ---------------------------------------------------------------- B10: €9.99 is €10 (trick 1, the price that ends in 9)
els = [block([(-20, -20), (1180, -20), (980, 1100), (-20, 1100)], HL),
       d(tag(640, 420, 3.9, "€9.99", WHITE, 290)),
       T("= €10", 250, 900, 230, RED, at=0, rot=-4),
       d(shock(1500, 640, 200, look=-1.0), 5),
       T("your brain", 1230, 165, 130, INK, at=0, rot=3), T("lies.", 1360, 315, 160, RED, at=0, rot=3)]
assert 1230 + text_w("your brain", 130) < 1880
ims.append(render("B10_999_brain", els))
# ---------------------------------------------------------------- B11: on strings, shocked (shops pull your strings)
fx, fy, fs = 1330, 1060, 2.45
PUP = dict(la=(-130, -150), ra=(130, 150), ll=(-10, -5), rl=(10, 5), lean=0, tilt=0)
hand_dx, hand_y, head_top = 68.9 * fs, fy - 304.1 * fs, fy - 325 * fs
ps = min(230, 690 / text_w("played.", 1))
els = [block([(1000, -20), (1940, -20), (1940, 1100), (880, 1100)], ORANGE),
       d([stk(P_line(1070, 120, fx - hand_dx, hand_y, 0.0, 3), 7, INK), stk(P_line(1590, 120, fx + hand_dx, hand_y, 0.0, 4), 7, INK),
          stk(P_line(fx, 200, fx, head_top, 0.0, 5), 7, INK)], 40),
       d([stk(P_line(1030, 120, 1630, 120, 0.01, 1), 16), stk(P_line(fx, 60, fx + 2, 200, 0.01, 2), 16)], 41),
       Fig(fx, fy, fs, poses=[(PUP, 0)], moods=[("wow", 0)], seed=6, enter="none", idle=0),
       T("you're", 110, 300, 170, INK, at=0, rot=-4), T("being", 130, 490, 170, INK, at=0, rot=-4),
       T("played.", 150, 720, ps, RED, at=0, rot=-4)]
ims.append(render("B11_played", els))

sheet = Image.new("RGB", (1280 * 2 + 30, 730 * 2 + 10), (60, 60, 60))
for k, im in enumerate(ims):
    sheet.paste(im, (10 + (k % 2) * 1290, 10 + (k // 2) * 730))
sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(os.path.join(OUT, "sheet_B8_B11.jpg"), quality=88)
small = Image.new("RGB", (4 * 178 + 10, 114), (255, 255, 255))
for k, im in enumerate(ims):
    small.paste(im.resize((168, 94), Image.LANCZOS), (10 + k * 178, 10))
small.save(os.path.join(OUT, "feed_size_B8_B11.png"))
print("ok")
