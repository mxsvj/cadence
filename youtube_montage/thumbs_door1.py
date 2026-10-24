"""Thumbnails for 'Don't Open the Door' episode 1, from the episode's own drawings: the peephole (Mom, smiling, not blinking),
the 3:12 alert, the door with the knocks. Dark pages so they stand out in the feed; two to four words; the duration
badge corner left empty."""
import os

import cairocffi as cairo
from PIL import Image

from build_door1 import *  # noqa: F401,F403
from build_door1 import black, door, ph_screen, screen_lines, NIGHT, WHITE, COAT
from doodle import clip_ell

OUT = os.path.join(D, "thumbs_door1")
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


def peephole(cx, cy, r, ms, mood="stare"):
    mx, my = cx, cy + 285 * ms
    inside = group(
        d([Fl(P_rect(cx - r - 20, cy - r - 20, 2 * r + 40, 2 * r + 40, 0), (232, 226, 212))]),
        d([stk(P_line(cx - r, cy - r, cx - 0.3 * r, cy - 0.42 * r, 0.0, 1), 6, GREY), stk(P_line(cx + r, cy - r, cx + 0.3 * r, cy - 0.42 * r, 0.0, 2), 6, GREY)], 2),
        d([Fl(P_poly([(mx - 48 * ms, cy + 48 * ms), (mx + 48 * ms, cy + 48 * ms), (mx + 110 * ms, cy + 170 * ms), (mx - 110 * ms, cy + 170 * ms)], True), COAT),
           stk(P_poly([(mx - 48 * ms, cy + 48 * ms), (mx + 48 * ms, cy + 48 * ms), (mx + 110 * ms, cy + 170 * ms), (mx - 110 * ms, cy + 170 * ms)], True), 8)], 3),
        Fig(mx, my, ms, poses=[("stand", 0)], moods=[(mood, 0)], kind="long", seed=21, enter="none", idle=0.0),
        d([("dot", mx - 42 * ms, cy + 30 * ms, 7 * ms, ORANGE), ("dot", mx + 42 * ms, cy + 30 * ms, 7 * ms, ORANGE)], 4))
    return [clip_ell(inside, cx, cy, r, r), d([stk(P_ell(cx, cy, r + 8, r + 8, 1, 0.05), 18, (90, 86, 92))], 5)]


ims = []
# ---------------------------------------------------------------- E1: the peephole - "that's not Mom."
els = [black(0.97)] + peephole(1300, 520, 430, 3.6) + [
    T("that's", 110, 330, 170, WHITE, at=0, rot=-4), T("not", 130, 540, 200, WHITE, at=0, rot=-4), T("Mom.", 150, 790, 240, RED, at=0, rot=-4)]
ims.append(render("E1_peephole_not_mom", els))
# ---------------------------------------------------------------- E2: the alert at 3:12
px, py, ps = 560, 540, 3.1
sw = 170 * ps - 70
els = [black(0.97), d(ph_screen(px, py, ps)), d([Fl(P_rect(px - 85 * ps + 18, py - 155 * ps + 60, 170 * ps - 36, 90, 0, r=12), RED)], 2),
       screen_lines(px, py - 155 * ps + 125, sw - 40, "ALERT", 72, WHITE, at=0),
       screen_lines(px, py - 70, sw, "DO NOT\nOPEN YOUR\nDOOR.", 120, INK, at=0),
       screen_lines(px, py + 230, sw, "3:12 a.m.", 80, RED, at=0),
       T("then", 1120, 380, 150, WHITE, at=0, rot=-4), T("someone", 1140, 560, 170, WHITE, at=0, rot=-4), T("knocked.", 1160, 760, 190, RED, at=0, rot=-4)]
ims.append(render("E2_alert_3am", els))
# ---------------------------------------------------------------- E3: the door, three knocks, Mom's voice
els = [black(0.9), d(door(560, 1100, 1.25)),
       T("KNOCK", 980, 260, 170, RED, at=0, rot=-8), T("KNOCK", 1040, 450, 170, RED, at=0, rot=5),
       T("\"it's Mom.\"", 1000, 700, 150, WHITE, at=0, rot=-3)]
ims.append(render("E3_door_its_mom", els))

sheet = Image.new("RGB", (1280 * 3 + 40, 740), (60, 60, 60))
for k, im in enumerate(ims):
    sheet.paste(im, (10 + k * 1290, 10))
sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(os.path.join(OUT, "sheet.jpg"), quality=88)
small = Image.new("RGB", (3 * 178 + 10, 114), (255, 255, 255))
for k, im in enumerate(ims):
    small.paste(im.resize((168, 94), Image.LANCZOS), (10 + k * 178, 10))
small.save(os.path.join(OUT, "feed_size.png"))
print("ok")
