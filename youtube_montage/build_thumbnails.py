"""Thumbnails in the edit's style (navy + yellow + red accent, flat house illustration).
Three variants for YouTube 'Test & compare'. Reuses the drawing code of build2.py."""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(D, "build_scenes.py")).read()
ns = {"__file__": os.path.join(D, "build_scenes.py")}
exec(src[: src.index("# --------------------------------------------------------------------------- script")], ns)
exec(src[src.index("# --------------------------------------------------------------------------- 2x canvas"): src.index("def tag_x")], ns)
Cv, landscape, draw_house, make_tag, F = ns["Cv"], ns["landscape"], ns["draw_house"], ns["make_tag"], ns["F"]
NAVY, YEL, RED, WHITE, SOFT, S = ns["NAVY"], ns["YEL"], ns["RED"], ns["WHITE"], ns["SOFT"], ns["S"]
O = os.path.join(D, "thumbs")
os.makedirs(O, exist_ok=True)


def fit(cv, txt, font, max_w, start):
    size = start
    while size > 40 and cv.tlen(txt, font, size) > max_w:
        size -= 4
    return size


def big(cv, xy, txt, size, fill, font="Inter-Black.otf", stroke=0, anchor="ls"):
    cv.d.text((xy[0] * S, xy[1] * S), txt, font=F(font, size * S), fill=fill, anchor=anchor,
              stroke_width=stroke * S, stroke_fill=(12, 18, 34))


def strike(cv, x0, x1, y, w=16):
    cv.line([(x0 - 10, y + 10), (x1 + 10, y - 14)], RED, w)


def arrow(cv, pts, col, w=18):
    cv.line(pts, col, w)
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    ang = math.atan2(y2 - y1, x2 - x1)
    L = 54
    cv.poly([(x2 + 10 * math.cos(ang), y2 + 10 * math.sin(ang)),
             (x2 - L * math.cos(ang - 0.5), y2 - L * math.sin(ang - 0.5)),
             (x2 - L * math.cos(ang + 0.5), y2 - L * math.sin(ang + 0.5))], col)


def scene(ox, k=1.15):
    cv = Cv((250, 242, 229))
    landscape(cv)
    draw_house(cv, ox, 880, k=k)
    return cv


def paste_tag(cv, tag, x, y, scale=1.0):
    t = tag.resize((int(tag.width * scale * S), int(tag.height * scale * S)), Image.LANCZOS)
    cv.im.alpha_composite(t, (int(x * S), int(y * S)))
    cv.d = ImageDraw.Draw(cv.im, "RGBA")


def save(cv, name):
    out = cv.out().convert("RGB").resize((1280, 720), Image.LANCZOS)
    out.save(os.path.join(O, name), quality=95)
    return out


# ---------------------------------------------------------------- A: strike-through price + "REAL PRICE?"
cv = scene(980)
paste_tag(cv, make_tag("€100,000", "+ ?"), 1130, 70, 0.82)
cv.poly([(0, 0), (900, 0), (760, 1080), (0, 1080)], NAVY + (240,))
s1 = fit(cv, "€100,000", "Inter-Black.otf", 640, 170)
big(cv, (70, 300), "€100,000", s1, WHITE)
strike(cv, 70, 70 + cv.tlen("€100,000", "Inter-Black.otf", s1), 300 - s1 * 0.36)
s2 = fit(cv, "PRICE?", "Inter-Black.otf", 640, 200)
big(cv, (66, 530), "REAL", s2, YEL)
big(cv, (66, 730), "PRICE?", s2, WHITE)
cv.rect([70, 830, 70 + cv.tlen("3 HIDDEN COSTS", "Inter-ExtraBold.otf", 52) + 60, 920], YEL, r=45)
cv.text((100, 892), "3 HIDDEN COSTS", "Inter-ExtraBold.otf", 52, NAVY, anchor="ls")
arrow(cv, [(780, 230), (930, 150), (1110, 165)], YEL)
a = save(cv, "thumb_A_real_price.jpg")

# ---------------------------------------------------------------- B: the counter (€100,000 -> €107,500)
cv = Cv(NAVY)
for i in range(-10, 30):
    cv.line([(i * 120, 1080), (i * 120 + 700, 0)], (255, 255, 255, 12), 2)
hs = scene(640)
house = hs.out().crop((380, 120, 1340, 1020)).resize((560, 525), Image.LANCZOS)
frame = Image.new("RGBA", (600, 565), (255, 255, 255, 255))
frame.paste(house, (20, 20))
mask = Image.new("L", frame.size, 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, 599, 564], 36, fill=255)
frame.putalpha(mask)
frame = frame.rotate(4, expand=True, resample=Image.BICUBIC)
sh = Image.new("RGBA", frame.size, (0, 0, 0, 0))
sh.paste((0, 0, 0, 140), (0, 0), frame.split()[3])
sh = sh.filter(ImageFilter.GaussianBlur(18))
base = cv.out()
base.alpha_composite(sh, (1270, 340))
base.alpha_composite(frame, (1250, 320))
cv.im = base.resize((1920 * S, 1080 * S), Image.LANCZOS)
cv.d = ImageDraw.Draw(cv.im, "RGBA")
s_old = 130
big(cv, (80, 330), "€100,000", s_old, SOFT, font="Inter-ExtraBold.otf")
strike(cv, 80, 80 + cv.tlen("€100,000", "Inter-ExtraBold.otf", s_old), 330 - s_old * 0.36, 14)
s_new = fit(cv, "€107,500", "Inter-Black.otf", 1080, 250)
big(cv, (70, 620), "€107,500", s_new, YEL)
cv.rect([80, 680, 1140, 728], (255, 255, 255, 40), r=24)
cv.rect([80, 680, 80 + 1060 * 100 / 112, 728], (244, 233, 216), r=24)
cv.rect([80 + 1060 * 100 / 112 - 30, 680, 80 + 1060 * 107.5 / 112, 728], YEL, r=24)
cv.rect([80, 680, 80 + 1060 * 100 / 112, 728], (244, 233, 216), r=24)
big(cv, (80, 900), "THE REAL PRICE", fit(cv, "THE REAL PRICE", "Inter-Black.otf", 1060, 120), WHITE)
b = save(cv, "thumb_B_counter.jpg")

# ---------------------------------------------------------------- C: full scene + headline
cv = Cv((250, 242, 229))
landscape(cv)
draw_house(cv, 640, 1030, k=0.95)
paste_tag(cv, make_tag("€100,000", "+ ?"), 1060, 560, 0.85)
grad = Image.new("RGBA", (1920 * S, 620 * S), (0, 0, 0, 0))
gd = ImageDraw.Draw(grad)
for y in range(620 * S):
    gd.line([(0, y), (1920 * S, y)], fill=NAVY + (int(245 * (1 - y / (620 * S)) ** 1.1),))
cv.im.alpha_composite(grad, (0, 0))
cv.d = ImageDraw.Draw(cv.im, "RGBA")
s = fit(cv, "WHAT €100K", "Inter-Black.otf", 1500, 190)
big(cv, (80, 200), "WHAT €100K", s, WHITE, stroke=0)
big(cv, (80, 380), "REALLY COSTS", s, YEL, stroke=0)
c = save(cv, "thumb_C_headline.jpg")

# ---------------------------------------------------------------- preview sheet: full size + phone-size
sheet = Image.new("RGB", (1280 + 20 + 320, 3 * 720 + 40), (255, 255, 255))
for i, im in enumerate((a, b, c)):
    sheet.paste(im, (0, i * 740))
    sheet.paste(im.resize((320, 180), Image.LANCZOS), (1300, i * 740))
sheet.save(os.path.join(O, "preview.png"))
print("ok")
