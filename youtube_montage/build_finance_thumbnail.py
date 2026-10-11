"""Style A thumbnail for 'Can Europeans buy VOO?': navy diagonal panel on the left with the struck-through hook,
a 2-word question (first word yellow), a yellow pill and a yellow arrow to the key element of the illustration."""
import math
import os

from PIL import Image, ImageDraw

D = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(D, "build_finance_demo.py")).read()
ns = {"__file__": os.path.join(D, "build_finance_demo.py")}
exec(src[: src.index("# --------------------------------------------------------------------------- script")], ns)
exec(src[src.index("# --------------------------------------------------------------------------- drawing helpers"):
         src.index("# --------------------------------------------------------------------------- scenes")], ns)
Cv, F, S, flag, star_pts, gradient = ns["Cv"], ns["F"], ns["S"], ns["flag"], ns["star_pts"], ns["gradient"]
NAVY, YEL, RED, TEAL, WHITE, INK, MUTED = (ns[k] for k in ("NAVY", "YEL", "RED", "TEAL", "WHITE", "INK", "MUTED"))
O = os.path.join(D, "thumbs")
os.makedirs(O, exist_ok=True)


def fit(cv, txt, font, max_w, start):
    size = start
    while size > 40 and cv.tlen(txt, font, size) > max_w:
        size -= 4
    return size


def big(cv, xy, txt, size, fill, font="Inter-Black.otf"):
    cv.d.text((xy[0] * S, xy[1] * S), txt, font=F(font, size * S), fill=fill, anchor="ls")


def arrow(cv, pts, col, w=18):
    cv.line(pts, col, w)
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    ang = math.atan2(y2 - y1, x2 - x1)
    L = 54
    cv.poly([(x2 + 10 * math.cos(ang), y2 + 10 * math.sin(ang)),
             (x2 - L * math.cos(ang - 0.5), y2 - L * math.sin(ang - 0.5)),
             (x2 - L * math.cos(ang + 0.5), y2 - L * math.sin(ang + 0.5))], col)


def phone(k):
    p = Cv(None, size=(int(420 * k), int(800 * k)))
    q = lambda *v: [x * k for x in v]
    p.shadow(q(10, 10, 410, 790), 56 * k, blur=26, alpha=110, dy=18)
    p.rect(q(10, 10, 410, 790), (16, 18, 26), r=56 * k)
    p.rect(q(24, 24, 396, 776), (246, 247, 250), r=44 * k)
    p.rect(q(165, 40, 255, 64), (16, 18, 26), r=12 * k)
    p.text(q(46, 140), "Search", "Inter-ExtraBold.otf", 42 * k, INK, anchor="ls")
    p.rect(q(44, 168, 376, 236), WHITE, r=34 * k, outline=(214, 219, 229), width=2)
    p.ellipse(q(66, 189, 88, 211), None, outline=MUTED, width=4)
    p.line([q(85, 208), q(95, 218)], MUTED, 4 * k)
    p.text(q(108, 214), "VOO", "Inter-SemiBold.otf", 30 * k, INK, anchor="ls")
    p.rect(q(44, 268, 376, 418), WHITE, r=22 * k, outline=(222, 226, 234), width=2)
    p.rect(q(66, 300, 150, 384), NAVY, r=18 * k)
    p.line([q(82, 364), q(100, 346), q(114, 356), q(136, 324)], TEAL, 7 * k)
    p.text(q(170, 346), "VOO", "Inter-Black.otf", 38 * k, INK, anchor="ls")
    p.rect(q(288, 322, 364, 366), (196, 200, 210), r=22 * k)
    p.text(q(326, 352), "BUY", "Inter-ExtraBold.otf", 22 * k, WHITE, anchor="ms")
    for y, w in ((470, 330), (520, 220), (600, 330), (650, 260)):
        p.rect(q(44, y, 44 + w, y + 26), (228, 231, 238), r=13 * k)
    return p.out()


def banner():
    b = Cv(None, size=(640, 230))
    b.shadow([14, 14, 626, 210], 30, blur=16, alpha=110, dy=12)
    b.rect([14, 14, 626, 210], RED, r=30)
    b.ellipse([44, 62, 144, 162], WHITE)
    b.line([(74, 92), (114, 132)], RED, 14, caps=True)
    b.line([(114, 92), (74, 132)], RED, 14, caps=True)
    b.text((170, 108), "NOT AVAILABLE", "Inter-Black.otf", 50, WHITE, anchor="ls")
    b.text((172, 162), "in your region", "Inter-SemiBold.otf", 40, WHITE, anchor="ls")
    return b.out()


cv = Cv((250, 242, 229))
gradient(cv, (252, 245, 233), (238, 225, 203))
for i in range(-10, 30):
    cv.line([(i * 120, 1080), (i * 120 + 700, 0)], (205, 190, 165, 60), 2)
ph = phone(1.42).rotate(-6, expand=True, resample=Image.BICUBIC)
bn = banner().rotate(4, expand=True, resample=Image.BICUBIC)
base = cv.out()
base.alpha_composite(ph, (1060, 18))
base.alpha_composite(bn, (930, 330))
eu = flag("eu", 150, 100)
base.alpha_composite(eu, (1700, 900))
cv.im = base.resize((1920 * S, 1080 * S), Image.LANCZOS)
cv.d = ImageDraw.Draw(cv.im, "RGBA")

cv.poly([(0, 0), (900, 0), (760, 1080), (0, 1080)], NAVY + (245,))
s1 = fit(cv, "VOO", "Inter-Black.otf", 560, 260)
big(cv, (70, 300), "VOO", s1, WHITE)
w1 = cv.tlen("VOO", "Inter-Black.otf", s1)
cv.line([(60, 300 - s1 * 0.36 + 12), (80 + w1, 300 - s1 * 0.36 - 18)], RED, 22)
s2 = fit(cv, "BLOCKED?", "Inter-Black.otf", 650, 200)
big(cv, (66, 520), "WHY", s2, YEL)
big(cv, (66, 700), "BLOCKED?", s2, WHITE)
cv.rect([70, 790, 70 + cv.tlen("IN EUROPE", "Inter-ExtraBold.otf", 60) + 70, 890], YEL, r=50)
cv.text((105, 861), "IN EUROPE", "Inter-ExtraBold.otf", 60, NAVY, anchor="ls")
arrow(cv, [(500, 430), (720, 350), (912, 440)], YEL)
out = cv.out().convert("RGB").resize((1280, 720), Image.LANCZOS)
out.save(os.path.join(O, "thumb_A_voo.jpg"), quality=95)
sheet = Image.new("RGB", (1280 + 20 + 320, 720), (255, 255, 255))
sheet.paste(out, (0, 0))
sheet.paste(out.resize((320, 180), Image.LANCZOS), (1300, 0))
sheet.paste(out.resize((168, 94), Image.LANCZOS), (1300, 200))
sheet.save(os.path.join(O, "preview.png"))
print("ok")
