"""Channel logos (avatars) for the two name proposals, in the look of the videos (black, colour per box, monospace):
A = 'Euro Unboxed': a € rising out of an open box (flaps open), each side in one of the box colours.
B = 'Dark Mode Money': a terminal prompt '> €' with a coloured block cursor.
Writes 1024 px avatars and a preview sheet (circle crops at YouTube sizes + a channel header mock-up)."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw

D = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(D, "build_finance_demo.py")).read()
ns = {"__file__": os.path.join(D, "build_finance_demo.py")}
exec(src[: src.index("# --------------------------------------------------------------------------- script")], ns)
exec(src[src.index("# --------------------------------------------------------------------------- drawing helpers"):
         src.index("# --------------------------------------------------------------------------- scenes")], ns)
Cv, F = ns["Cv"], ns["F"]
BG, FG, DIM = (7, 7, 9), (240, 240, 240), (118, 118, 126)
ORANGE, INDIGO, GREEN, PINK, VIOLET = (247, 147, 26), (130, 140, 255), (60, 200, 120), (255, 80, 170), (150, 120, 255)
MONO, MONOB = "../../truetype/dejavu/DejaVuSansMono.ttf", "../../truetype/dejavu/DejaVuSansMono-Bold.ttf"
BLACK = "InterDisplay-Black.otf"
O = os.path.join(D, "logos")
os.makedirs(O, exist_ok=True)
S = 1024


def glow(im, col, k=0.22, cy=0.55):
    a = np.asarray(im.convert("RGB"), dtype=np.float32)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    f = np.exp(-(((xx - S / 2) / 420) ** 2 + ((yy - S * cy) / 420) ** 2))
    return Image.fromarray(np.clip(a + f[..., None] * np.array(col, np.float32) * k, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- A: Euro Unboxed
cv = Cv(BG, size=(S, S))
x0, y0, x1, y1, w = 292, 480, 732, 850, 40
YELLOW = (243, 190, 50)
cv.text((S / 2, 790), "€", BLACK, 500, FG, anchor="ms")                       # the € sits in the box and rises out of it
cv.line([(x0, y0), (x0, y1)], ORANGE, w, caps=True)                          # left side
cv.line([(x0, y1), (x1, y1)], INDIGO, w, caps=True)                          # bottom
cv.line([(x1, y1), (x1, y0)], GREEN, w, caps=True)                           # right side
fl, ang = 200, math.radians(40)                                             # two flaps, opened outwards
cv.line([(x0, y0), (x0 - fl * math.sin(ang), y0 - fl * math.cos(ang))], PINK, w, caps=True)
cv.line([(x1, y0), (x1 + fl * math.sin(ang), y0 - fl * math.cos(ang))], YELLOW, w, caps=True)
a_img = glow(cv.out(), VIOLET)
a_img.save(os.path.join(O, "logo_A_euro_unboxed.png"))

# ---------------------------------------------------------------- B: Dark Mode Money
cv = Cv(BG, size=(S, S))
cv.text((150, 640), ">", MONOB, 300, DIM, anchor="ls")
cv.text((385, 660), "€", BLACK, 420, FG, anchor="ls")
cv.rect([735, 380, 865, 660], GREEN)                                        # block cursor
for k, col in enumerate((ORANGE, INDIGO, GREEN, PINK)):                     # the four box colours, like the chapter progress bar
    cv.rect([272 + k * 130, 760, 372 + k * 130, 800], col)
b_img = glow(cv.out(), GREEN, 0.16, 0.5)
b_img.save(os.path.join(O, "logo_B_dark_mode_money.png"))


# ---------------------------------------------------------------- preview: circle crops and a channel header mock-up
def circle(img, d):
    im = img.resize((d, d), Image.LANCZOS)
    m = Image.new("L", (d * 4, d * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, d * 4 - 1, d * 4 - 1], fill=255)
    out = Image.new("RGB", (d, d), (255, 255, 255))
    out.paste(im, (0, 0), m.resize((d, d), Image.LANCZOS))
    return out


sheet = Image.new("RGB", (1500, 1060), (255, 255, 255))
d = ImageDraw.Draw(sheet)
for j, (img, name, handle) in enumerate(((a_img, "Euro Unboxed", "@EuroUnboxed"), (b_img, "Dark Mode Money", "@DarkModeMoney"))):
    y = 30 + j * 520
    sheet.paste(circle(img, 420), (30, y))
    sheet.paste(circle(img, 98), (480, y + 20))
    sheet.paste(circle(img, 48), (600, y + 45))
    sheet.paste(circle(img, 24), (670, y + 57))
    # channel header mock-up (dark YouTube)
    d.rectangle([480, y + 160, 1470, y + 400], fill=(15, 15, 15))
    sheet.paste(circle(img, 160).convert("RGB"), (510, y + 200))
    d.text((700, y + 250), name, font=F("Inter-Bold.otf", 52) if os.path.exists(os.path.join(ns["FD"], "Inter-Bold.otf")) else F(BLACK, 52),
           fill=(241, 241, 241), anchor="ls")
    d.text((700, y + 300), f"{handle} · money, explained for Europeans", font=F(MONO, 24), fill=(170, 170, 170), anchor="ls")
    d.rounded_rectangle([700, y + 325, 860, y + 375], 25, fill=(241, 241, 241))
    d.text((780, y + 358), "Subscribe", font=F(BLACK, 22), fill=(15, 15, 15), anchor="ms")
sheet.save(os.path.join(O, "preview_logos.png"))
print("ok")
