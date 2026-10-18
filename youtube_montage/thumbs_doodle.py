"""Thumbnails for the night's doodle videos (compound interest, shop tricks, first €1,000, minimum payment trap), same engine as
the videos. Each one: one big idea readable at feed size, a slightly darker paper and a hand-drawn ink frame so the cream
does not dissolve into YouTube's white light mode, nothing important in the bottom-right corner (duration badge)."""
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
    ctx.set_source_rgba(0.42, 0.36, 0.28, 0.10)          # a shade darker than the video paper: reads as paper, not as white
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
ims = []
# ---------------------------------------------------------------- compound interest: A2 leads, A4 (the hook's numbers) second, A3 third
sc = 640 / 525
els = [d([stk(P_line(860, 960, 1840, 960, 0.005, 1), 9)])]
for k, (x, end, col, name) in enumerate(((930, 244, (150, 186, 214), "Ben"), (1400, 525, ORANGE, "Anna"))):
    els.append(d([Fl(P_rect(x, 960 - end * sc, 340, end * sc, 0), col), stk(P_rect(x, 960 - end * sc, 340, end * sc, 8), 8)], 5 + k))
    els.append(T(f"€{end}k", x + 170, 960 - end * sc - 34, 130, INK if k == 0 else ORANGE, at=0, anchor="m"))
    els.append(T(name, x + 170, 960 - end * sc / 2 + 30, 96, INK, at=0, anchor="m"))
els += [T("+10 years", 110, 330, 200, INK, at=0, rot=-4), T("= ×2", 170, 580, 250, ORANGE, at=0, rot=-4)]
ims.append(render("A2_anna_ben", els))
ims.append(render("A4_10k_76k", [d(money_bag(330, 640, 1.0)), T("€10,000", 140, 400, 140, INK, at=0, rot=-3),
                                 arrow(P_bez((560, 600), (760, 520), (900, 560)), 0, INK, 10, 0.0),
                                 d(money_bag(1330, 600, 2.3), 2), T("€76,000", 980, 250, 220, ORANGE, at=0, rot=-3),
                                 T("do nothing.", 150, 930, 140, INK, at=0, rot=-2)]))
ims.append(render("A3_rule_72", [T("72", 200, 780, 640, ORANGE, at=0, rot=-6), T("÷ your return", 1000, 430, 140, INK, at=0, rot=-3),
                                 T("= years to", 1040, 620, 130, INK, at=0, rot=-3), T("double.", 1080, 800, 150, ORANGE, at=0, rot=-3)]))
# ---------------------------------------------------------------- shop tricks: B1 leads (figure now points at the tag)
ims.append(render("B1_999", [d(tag(800, 470, 3.3, "€9.99", HL, 200)),
                             Fig(1560, 900, 1.35, poses=[("point_l", 0)], moods=[("smug", 0)], seed=3, enter="none", idle=0),
                             T("it's €10.", 330, 960, 200, RED, at=0, rot=-3)]))
ims.append(render("B2_fake_timer", [d(clock(620, 560, 2.6, hh=-20, mm=90)), T("FAKE", 260, 660, 330, RED, at=0, rot=-14),
                                    d(phone(1420, 540, 2.0)), T("ends in", 1420, 400, 84, INK, at=0, anchor="m"),
                                    T("9:59", 1420, 540, 150, RED, at=0, anchor="m"), T("only 2 left!", 1420, 700, 70, INK, at=0, anchor="m")]))
cards = []
for k, (x, top, price) in enumerate(((330, "online", "$59"), (960, "print", "$125"), (1590, "both", "$125"))):
    cards.append(d([Fl(P_rect(x - 240, 260, 480, 440, 0, r=24), (250, 248, 242)), stk(P_rect(x - 240, 260, 480, 440, 9, r=24), 8),
                    ("g", top, x, 400, 96, INK, HAND, "m"), ("g", price, x, 600, 170, INK, HAND, "m")], 10 + k))
ims.append(render("B3_decoy", cards + [cross(960, 480, 240, 0, RED, 16), T("nobody picks this.", 200, 930, 160, RED, at=0, rot=-3),
                                       circ(1590, 480, 300, 290, 0, ORANGE, 10)]))
# ---------------------------------------------------------------- first €1,000: C3 leads
rr = random.Random(4)
bx0, bx1, by0, by1 = 1000, 1860, 250, 900
els = [d([stk(P_poly([(bx0, by0), (bx0 + 80, by1), (bx1 - 70, by1), (bx1, by0)], True), 12)])]
for k in range(48):
    x = bx0 + 110 + (k % 8) * 86 + rr.uniform(-6, 6)
    y = by0 + 70 + (k // 8) * 96 + rr.uniform(-6, 6)
    els.append(d([Fl(P_rect(x - 34, y - 32, 68, 64, 0, r=9), [HL, PINK, (150, 186, 214), (214, 226, 196), ORANGE][k % 5]),
                  stk(P_rect(x - 34, y - 32, 68, 64, 4, r=9), 5)], 100 + k))
els += [T("buy", 130, 460, 260, INK, at=0, rot=-4), T("every-", 140, 690, 200, ORANGE, at=0, rot=-4), T("thing.", 180, 890, 200, ORANGE, at=0, rot=-4)]
ims.append(render("C3_buy_everything", els))
pts = [(160, 1000)]
for k in range(8):
    x, y = 160 + k * 200, 1000 - k * 95
    pts += [(x + 200, y)] + ([(x + 200, y - 95)] if k < 7 else [])
els = [d([stk(P_poly(pts), 9)])]
for k in range(8):
    els.append(T(str(k + 1), 230 + k * 200, 980 - k * 95, 80, ORANGE, at=0, anchor="m"))
els += [Fig(1670, 335, 0.9, poses=[("arms_up", 0)], moods=[("grin", 0)], seed=3, enter="none", idle=0),
        T("8 steps.", 130, 300, 230, INK, at=0, rot=-4), T("first €1,000", 170, 470, 130, ORANGE, at=0, rot=-4)]
ims.append(render("C2_8_steps", els))
ims.append(render("C1_now_what", [Fig(470, 1000, 1.6, poses=[("shrug", 0)], moods=[("worried", 0)], seed=3, enter="none", idle=0),
                                  d(money_bag(1230, 790, 1.5)), T("€1,000", 780, 300, 220, ORANGE, at=0, rot=-4),
                                  T("now what?", 860, 500, 160, INK, at=0, rot=3)]))
# ---------------------------------------------------------------- minimum payment trap: D2 leads (zoomed on the button), D1 second
els = [d(phone(470, 600, 3.6)), d([Fl(P_rect(205, 430, 530, 330, 0, r=50), ORANGE), stk(P_rect(205, 430, 530, 330, 10, r=50), 10)], 4),
       T("PAY\nMINIMUM", 470, 575, 128, INK, at=0, anchor="m", lh=0.95),
       T("the most", 960, 330, 160, INK, at=0, rot=-3), T("expensive", 980, 550, 200, RED, at=0, rot=-3),
       T("button.", 1020, 760, 160, INK, at=0, rot=-3), arrow(P_bez((960, 650), (860, 640), (775, 600)), 0, RED, 11, 0.0)]
ims.append(render("D2_minimum_button", els))
try:
    from build_debt import boulder  # noqa: E402
except Exception:                   # build_debt mid-edit: a plain round boulder will do
    def boulder(x, y, r):
        return [Fl(P_ell(x, y, r, r * 0.9, 1, closed=True), (190, 180, 166)), stk(P_ell(x, y, r, r * 0.9, 3, 0.08), 8)]
ims.append(render("D1_boulder", [d([stk(P_line(100, 1000, 1820, 470, 0.02, 1), 9)]), d(boulder(1150, 560, 250), 3),
                                 Fig(760, 900, 1.4, poses=[("reach", 0)], moods=[("worried", 0)], seed=3, rot=-12, enter="none", idle=0),
                                 T("why it never", 120, 230, 150, INK, at=0, rot=-3), T("ends.", 200, 440, 210, RED, at=0, rot=-3)]))

sheet = Image.new("RGB", (1280 * 3 + 40, 740 * 4), (60, 60, 60))
order = ["A2", "A4", "A3", "B1", "B2", "B3", "C3", "C2", "C1", "D2", "D1"]
for k, im in enumerate(ims):
    sheet.paste(im, (10 + (k % 3) * 1290, 10 + (k // 3) * 740))
sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(os.path.join(OUT, "sheet.jpg"), quality=88)
small = Image.new("RGB", (4 * 178 + 10, 3 * 104 + 10), (255, 255, 255))     # what the feed shows: 168 px wide on white
for k, im in enumerate(ims):
    small.paste(im.resize((168, 94), Image.LANCZOS), (10 + (k % 4) * 178, 10 + (k // 4) * 104))
small.save(os.path.join(OUT, "feed_size.png"))
print("ok", order)
