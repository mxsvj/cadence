"""Thumbnails for 'How to Save Money So Easily It Feels Illegal', drawn with the same doodle engine as the video."""
import math
import os

import cairocffi as cairo
import numpy as np
from PIL import Image

from doodle import *  # noqa: F401,F403

OUT = os.path.join(D, "thumbs_save")
os.makedirs(OUT, exist_ok=True)
paper, _parr, PW, PH = make_paper(seed=8)


def render(name, els, t=9.0):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_surface(paper, (W - PW) / 2, (H - PH) / 2)
    ctx.paint()
    for e in els:
        e(ctx, t)
    surf.flush()
    a = np.frombuffer(surf.get_data(), np.uint8).reshape(H, W, 4)[..., [2, 1, 0]].copy()
    im = Image.fromarray(a).resize((1280, 720), Image.LANCZOS)
    im.save(os.path.join(OUT, name + ".png"))
    im.save(os.path.join(OUT, name + ".jpg"), quality=92)


def falling(x, y0, n=3, s=0.8):
    out = []
    for k in range(n):
        yy = y0 - k * 150
        out.append(Dr(coin(x + (k % 2) * 30 - 15, yy, s), 0, 0, seed=40 + k))
        out.append(Dr([S(P_line(x - 30 + (k % 2) * 30, yy - 70, x - 30 + (k % 2) * 30, yy - 120, 0, k), 5, GREY),
                       S(P_line(x + (k % 2) * 30, yy - 80, x + (k % 2) * 30, yy - 140, 0, k + 3), 5, GREY)], 0, 0, seed=50 + k))
    return out


# S1: smug figure, piggy filling by itself, FEELS ILLEGAL
els = [Fig(470, 1790, 4.5, poses=[("cross", 0)], moods=[("smug", 0)], seed=3, enter="none", idle=0)]
els += [Dr(piggy(1380, 820, 1.35), 0, 0, seed=2)] + falling(1345, 650, n=2)
els += [hilite(980, 980 + text_w("ILLEGAL", 250), 300, 150, 0, (247, 196, 140), seed=3)]
els += [T("feels", 990, 150, 130, INK, at=0, rot=-4), T("ILLEGAL", 980, 360, 250, RED, at=0, rot=-4)]
render("S1_feels_illegal", els)

# S2: asleep, the money still moves
els = [Dr([S(P_rect(150, 840, 820, 70, 6, r=24), 8), S(P_line(175, 910, 175, 1000, 0, 1), 8), S(P_line(945, 910, 945, 1000, 0, 2), 8)], 0, 0, seed=4),
       Fig(870, 820, 1.45, poses=[("lie", 0)], moods=[("sleep", 0)], seed=3, rot=-90, enter="none", idle=0)]
els += [T("Z", 560, 660, 90, GREY, at=0, rot=-8), T("Z", 650, 570, 120, GREY, at=0, rot=-6), T("Z", 760, 470, 150, GREY, at=0, rot=-4)]
els += [Dr(piggy(1450, 800, 1.2), 0, 0, seed=6)] + falling(1418, 560)
els += [T("saving", 150, 210, 170, INK, at=0, rot=-3), T("on autopilot", 180, 335, 110, ORANGE, at=0, rot=-3)]
render("S2_autopilot", els)

# S3: the brain wants NOW
els = [Dr(brain(560, 610, 1.9), 0, 0, seed=7)]
els += [T("NOW", 1060, 560, 400, ORANGE, at=0, rot=-6), T("later", 1520, 820, 70, GREY, at=0, rot=5)]
els += [T("your brain:", 160, 210, 120, INK, at=0, rot=-3)]
render("S3_brain_now", els)

sheet = Image.new("RGB", (1280 * 3 + 40, 740), (60, 60, 60))
for k, n in enumerate(("S1_feels_illegal", "S2_autopilot", "S3_brain_now")):
    sheet.paste(Image.open(os.path.join(OUT, n + ".png")), (10 + k * 1290, 10))
sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(os.path.join(OUT, "sheet.jpg"), quality=90)
print("ok")
