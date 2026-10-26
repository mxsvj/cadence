"""Avatar and banner for the horror-story channel (working name '3AM Doodles'), drawn with the episode's own pieces:
the peephole, Mom's stare, the door with light under it, the knockers seen from behind. Dark pages, one red.
Avatar 800x800 (shown as a circle down to ~48 px: one shape, thick lines). Banner 2560x1440, everything that carries
meaning inside the 1546x423 area every device shows."""
import os

import cairocffi as cairo
from PIL import Image, ImageDraw

from build_door1 import *  # noqa: F401,F403
from build_door1 import NIGHT, WHITE, DIM, KSKIN, back_fig, black, door, group, hallway
from doodle import clip_ell

NAME, TAG = "3AM Doodles", "horror stories, drawn by hand."
OUT = os.path.join(D, "branding_door")
os.makedirs(OUT, exist_ok=True)
paper, _parr, PW, PH = make_paper(seed=11)


def render(name, els, size, virtual, t=9.0):
    w, h = size
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    ctx = cairo.Context(surf)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.scale(w / virtual[0], w / virtual[0])
    ctx.set_source_surface(paper, (virtual[0] - PW) / 2, (virtual[1] - PH) / 2)
    ctx.paint()
    for e in els:
        e(ctx, t)
    surf.flush()
    a = np.frombuffer(surf.get_data(), np.uint8).reshape(h, w, 4)[..., [2, 1, 0]].copy()
    im = Image.fromarray(a)
    im.save(os.path.join(OUT, name + ".png"))
    return im


# ---------------------------------------------------------------- avatar: the peephole, and the stare inside it
cx, cy, r = 540, 540, 420
ms = 7.6
face = group(Dr([Fl(P_rect(0, 0, 1080, 1080, 0), (236, 232, 222))], 0, 0, seed=1),
             Fig(cx, cy + 285 * ms + 30, ms, poses=[("stand", 0)], moods=[("stare", 0)], kind="long", seed=21, enter="none", idle=0.0,
                 skin=KSKIN))
av = render("avatar_peephole", [black(1.0), clip_ell(face, cx, cy, r, r), Dr([stk(P_ell(cx, cy, r + 10, r + 10, 1, 0.05), 34, (90, 86, 92))], 0, 0, seed=2)],
            (800, 800), (1080, 1080))

# ---------------------------------------------------------------- banner (virtual 1920x1080 -> 2560x1440); safe area x 380-1540, y 381-699
X0 = 640
ns = min(190, (1500 - X0) / text_w(NAME, 1))
ts = min(76, (1500 - X0) / text_w(TAG, 1))
els = [black(0.97),
       Dr(door(480, 700, 0.38), 0, 0, seed=3),
       T(NAME, X0, 560, ns, WHITE, at=-2, cps=400, rot=-2),
       T(TAG, X0 + 10, 665, ts, RED, at=-2, cps=400, rot=-2)]
assert X0 + text_w(NAME, ns) < 1540 and X0 + 10 + text_w(TAG, ts) < 1540, "banner text leaves the safe area"
# outside the safe area (wide screens and TVs only): the landing with the two knockers waiting, and a peephole
els += [Dr(back_fig(170, 1000, 0.95, hair="chef"), 0, 0, seed=4), Dr(back_fig(1750, 1000, 0.95, hair="bald", coat=(150, 130, 110), slippers=True), 0, 0, seed=5),
        Dr([stk(P_line(40, 1002, 1880, 1004, 0.003, 6), 6, (90, 86, 92))], 0, 0, seed=6)]
banner = render("banner_2560x1440", els, (2560, 1440), (1920, 1080))

# ---------------------------------------------------------------- previews: the avatar as YouTube crops it, the banner's safe areas
pv = Image.new("RGB", (560, 280), (255, 255, 255))
for j, sz in enumerate((240, 88, 48)):
    c = av.resize((sz, sz), Image.LANCZOS)
    m = Image.new("L", (sz, sz), 0)
    ImageDraw.Draw(m).ellipse((0, 0, sz - 1, sz - 1), fill=255)
    pv.paste(c, (20 + j * 260 if j < 2 else 480, 20 + (240 - sz) // 2), m)
pv.save(os.path.join(OUT, "preview_avatar.png"))
b = banner.copy()
dr = ImageDraw.Draw(b)
dr.rectangle(((2560 - 1546) // 2, (1440 - 423) // 2, (2560 + 1546) // 2, (1440 + 423) // 2), outline=(220, 40, 40), width=6)
dr.rectangle((0, (1440 - 423) // 2, 2559, (1440 + 423) // 2), outline=(40, 90, 220), width=4)
b.resize((1280, 720), Image.LANCZOS).save(os.path.join(OUT, "preview_banner_zones.png"))
print("ok")
