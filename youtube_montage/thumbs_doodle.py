"""Thumbnails for the three doodle videos of the night (compound interest, shop tricks, first €1,000), same engine as the videos."""
import os
import random

import cairocffi as cairo
import numpy as np
from PIL import Image

from doodle_video import *  # noqa: F401,F403
from doodle_video import stk

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
    for e in ops_list:
        e(ctx, t)
    surf.flush()
    a = np.frombuffer(surf.get_data(), np.uint8).reshape(H, W, 4)[..., [2, 1, 0]].copy()
    im = Image.fromarray(a).resize((1280, 720), Image.LANCZOS)
    im.save(os.path.join(OUT, name + ".jpg"), quality=92)
    return im


d = lambda ops, seed=1: Dr(ops, 0, 0, seed=seed)
ims = []
# ---------------------------------------------------------------- compound interest
ims.append(render("A1_time", [d([hill(120, 330, 1800, 960)]), d(snowball(250, 290, 36)), d(snowball(800, 600, 80), 2), d(snowball(1500, 800, 190), 3),
                              T("TIME.", 980, 300, 240, ORANGE, at=0, rot=-5), T("beats money.", 1060, 450, 120, INK, at=0, rot=-3)]))
sc = 560 / 525
els = [d([stk(P_line(780, 940, 1820, 940, 0.005, 1), 8)])]
for k, (x, put, end, col) in enumerate(((880, 72, 244, (150, 186, 214)), (1380, 96, 525, ORANGE))):
    els.append(d([Fl(P_rect(x, 940 - end * sc, 300, (end - put) * sc, 0), col), Fl(P_rect(x, 940 - put * sc, 300, put * sc, 0), PALE),
                  stk(P_rect(x, 940 - end * sc, 300, end * sc, 7), 7)], 5 + k))
    els.append(T(f"€{end}k", x + 150, 940 - end * sc - 30, 110, INK if k == 0 else ORANGE, at=0, anchor="m"))
els += [Fig(300, 960, 1.15, poses=[("sad", 0)], moods=[("worried", 0)], kind="plain", seed=42, enter="none", idle=0),
        Fig(560, 960, 1.15, poses=[("arms_up", 0)], moods=[("grin", 0)], kind="bob", seed=41, enter="none", idle=0),
        T("+10 years", 160, 250, 170, INK, at=0, rot=-4), T("= ×2", 220, 430, 170, ORANGE, at=0, rot=-4)]
ims.append(render("A2_anna_ben", els))
ims.append(render("A3_rule_72", [T("72", 260, 760, 620, ORANGE, at=0, rot=-6), T("÷ your return", 1040, 470, 120, INK, at=0, rot=-3),
                                 T("= years to double", 1060, 640, 100, GREY, at=0, rot=-3), d(coin(1350, 860, 1.3)), d(coin(1560, 860, 1.3), 2),
                                 T("×2", 1700, 900, 120, INK, at=0)]))
# ---------------------------------------------------------------- shop tricks
ims.append(render("B1_999", [d(tag(760, 520, 3.2, "€9.99", HL, 190)), Fig(1600, 980, 1.4, poses=[("point_l", 0)], moods=[("smug", 0)], seed=3,
                                                                                     flip=True, enter="none", idle=0),
                             T("it's €10.", 520, 1000, 150, RED, at=0, rot=-3)]))
ims.append(render("B2_fake_timer", [d(clock(620, 560, 2.6, hh=-20, mm=90)), T("FAKE", 330, 640, 300, RED, at=0, rot=-14),
                                    d(phone(1420, 560, 1.8)), T("only 2\nleft!", 1420, 470, 90, RED, at=0, anchor="m"), T("09:00", 1420, 720, 100, INK, at=0, anchor="m")]))
cards = []
for k, (x, top, price) in enumerate(((330, "online", "$59"), (960, "print", "$125"), (1590, "both", "$125"))):
    cards.append(d([Fl(P_rect(x - 230, 300, 460, 420, 0, r=24), (250, 248, 242)), stk(P_rect(x - 230, 300, 460, 420, 9, r=24), 8),
                    ("g", top, x, 420, 80, INK, HAND, "m"), ("g", price, x, 620, 150, INK, HAND, "m")], 10 + k))
ims.append(render("B3_decoy", cards + [cross(960, 510, 230, 0, RED, 16), T("the decoy.", 640, 950, 190, RED, at=0, rot=-3),
                                       circ(1590, 510, 300, 280, 0, ORANGE, 10)]))
# ---------------------------------------------------------------- first €1,000
ims.append(render("C1_now_what", [Fig(470, 1000, 1.6, poses=[("shrug", 0)], moods=[("worried", 0)], seed=3, enter="none", idle=0),
                                  d(money_bag(1000, 720, 1.4)), T("€1,000", 820, 330, 200, ORANGE, at=0, rot=-4), T("now what?", 1100, 520, 140, INK, at=0, rot=4)]))
pts = [(160, 1000)]
for k in range(8):
    x, y = 160 + k * 200, 1000 - k * 95
    pts += [(x + 200, y)] + ([(x + 200, y - 95)] if k < 7 else [])
els = [d([stk(P_poly(pts), 8)])]
for k in range(8):
    els.append(T(str(k + 1), 230 + k * 200, 980 - k * 95, 70, ORANGE, at=0, anchor="m"))
els += [Fig(1670, 335, 0.9, poses=[("arms_up", 0)], moods=[("grin", 0)], seed=3, enter="none", idle=0),
        T("8 steps.", 140, 300, 220, INK, at=0, rot=-4), T("first €1,000", 180, 460, 110, ORANGE, at=0, rot=-4)]
ims.append(render("C2_8_steps", els))
rr = random.Random(4)
els = [d([stk(P_poly([(1100, 380), (1170, 840), (1800, 840), (1860, 380)], True), 10)])]
for k in range(40):
    x = 1180 + (k % 8) * 80 + rr.uniform(-6, 6)
    y = 430 + (k // 8) * 80 + rr.uniform(-6, 6)
    els.append(d([Fl(P_rect(x - 30, y - 28, 60, 56, 0, r=8), [HL, PINK, (150, 186, 214), (214, 226, 196), ORANGE][k % 5]), stk(P_rect(x - 30, y - 28, 60, 56, 4, r=8), 4.5)], 100 + k))
els += [T("buy", 140, 420, 230, INK, at=0, rot=-4), T("everything.", 160, 640, 190, ORANGE, at=0, rot=-4),
        T("(1 global index fund)", 200, 800, 80, GREY, at=0, rot=-2)]
ims.append(render("C3_buy_everything", els))

# ---------------------------------------------------------------- pay off debt
from build_debt import boulder  # noqa: E402
ims.append(render("D1_boulder", [d([stk(P_line(100, 1000, 1820, 470, 0.02, 1), 8)]), d(boulder(1150, 560, 250), 3),
                                 Fig(760, 900, 1.4, poses=[("reach", 0)], moods=[("worried", 0)], seed=3, rot=-12, enter="none", idle=0),
                                 T("why it never", 140, 230, 140, INK, at=0, rot=-3), T("ends.", 220, 420, 190, RED, at=0, rot=-3)]))
ims.append(render("D2_minimum_button", [d(phone(560, 560, 2.4)), d([Fl(P_rect(400, 600, 320, 150, 0, r=34), ORANGE), stk(P_rect(400, 600, 320, 150, 8, r=34), 8)], 4),
                                        T("PAY\nMINIMUM", 560, 662, 62, INK, at=0, anchor="m", lh=1.0),
                                        T("the most", 1000, 380, 130, INK, at=0, rot=-3), T("expensive", 1020, 560, 150, RED, at=0, rot=-3),
                                        T("button.", 1060, 720, 130, INK, at=0, rot=-3), arrow(P_bez((1000, 640), (860, 700), (760, 690)), 0, RED, 9, 0.0)]))
els = [d([stk(P_line(960, 280, 965, 980, 0.01, 2), 6, GREY)])]
for k, (lab, w, col) in enumerate((("21%", 340, (244, 214, 210)), ("19%", 430, PALE), ("7%", 540, PALE))):
    els.append(d([Fl(P_rect(200, 420 + k * 150, w, 110, 0, r=12), col), stk(P_rect(200, 420 + k * 150, w, 110, 6, r=12), 7), ("g", lab, 260, 500 + k * 150, 80, INK, HAND, "l")], 60 + k))
for k, (lab, w, col) in enumerate((("€800", 240, HL), ("€2,200", 400, PALE), ("€3,500", 560, PALE))):
    els.append(d([Fl(P_rect(1110, 420 + k * 150, w, 110, 0, r=12), col), stk(P_rect(1110, 420 + k * 150, w, 110, 6, r=12), 7), ("g", lab, 1150, 500 + k * 150, 72, INK, HAND, "l")], 70 + k))
els += [T("avalanche", 200, 330, 120, INK, at=0, rot=-2), T("snowball", 1110, 330, 120, INK, at=0, rot=-2), T("which one?", 560, 200, 130, ORANGE, at=0, rot=-3)]
ims.append(render("D3_which_order", els))

sheet = Image.new("RGB", (1280 * 3 + 40, 740 * 4), (60, 60, 60))
for k, im in enumerate(ims):
    sheet.paste(im, (10 + (k % 3) * 1290, 10 + (k // 3) * 740))
sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(os.path.join(OUT, "sheet.jpg"), quality=88)
print("ok")
