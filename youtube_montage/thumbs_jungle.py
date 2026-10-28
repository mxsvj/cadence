"""Thumbnails for 'Your Plane Goes Down in the Jungle': J1 the wreck under the canopy, 'would you survive?';
J2 the first choice as two cards, 'only one keeps you alive.' Same drawings as the video, dark green, two to five words."""
import os

import cairocffi as cairo
from PIL import Image

from build_jungle import *  # noqa: F401,F403
from build_jungle import black, canopy, leaf, trunk, wreck, you, WHITE

OUT = os.path.join(D, "thumbs_jungle")
os.makedirs(OUT, exist_ok=True)
paper, _parr, PW, PH = make_paper(seed=8)
GREEN_DARK = (30, 46, 32)


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
    im.save(os.path.join(OUT, name + ".jpg"), quality=92)
    return im


d = lambda ops, seed=1: Dr(ops, 0, 0, seed=seed)
ims = []
# ---------------------------------------------------------------- J1: the wreck, would you survive?
els = [black(0.95, GREEN_DARK),
       d([Fl(P_poly([(900, -20), (1940, -20), (1940, 1100), (1000, 1100)], True), (190, 210, 176))], 1),
       d([op for x in (1000, 1850) for op in trunk(x, -20, 1100, 80, int(x))], 2),
       d(wreck(1380, 880, 1.45), 3), d(canopy(True, 3, 10), 4),
       you(1700, 1040, 1.15, mood="wow", enter="none", idle=0.0),
       T("would you", 100, 330, 170, WHITE, at=0, rot=-4), T("survive?", 130, 560, 210, RED, at=0, rot=-4),
       T("hour 1.", 140, 800, 110, (150, 210, 130), at=0, rot=-3)]
ims.append(render("J1_would_you_survive", els))
# ---------------------------------------------------------------- J2: the first choice
els = [black(0.95, GREEN_DARK)]
for k, (lab, x, col) in enumerate((("A", 120, ORANGE), ("B", 980, ORANGE))):
    els += [d([Fl(P_rect(x, 330, 820, 560, 0, r=28), (236, 232, 222)), stk(P_rect(x, 330, 820, 560, 8, r=28), 9)], 10 + k),
            T(lab, x + 40, 470, 150, col, at=0)]
els += [d([stk(P_line(330, 720, 720, 720, 0.02, 1), 8), stk(P_poly([(680, 690), (730, 720), (680, 750)]), 8)] + leaf(500, 520, 1.0, -60, LEAF, 3), 20),
        you(300, 800, 0.95, pose="point_r", enter="none", idle=0.0),
        d(wreck(1420, 760, 0.75, smoke=True), 21), you(1700, 800, 0.95, enter="none", idle=0.0),
        T("only one keeps", 120, 210, 120, WHITE, at=0, rot=-2), T("you alive.", 1180, 210, 120, RED, at=0, rot=-2)]
ims.append(render("J2_only_one_keeps_you_alive", els))

small = Image.new("RGB", (2 * 178 + 10, 114), (255, 255, 255))
for k, im in enumerate(ims):
    small.paste(im.resize((168, 94), Image.LANCZOS), (10 + k * 178, 10))
small.save(os.path.join(OUT, "feed_size.png"))
print("ok")
