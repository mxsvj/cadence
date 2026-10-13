"""Thumbnails in the style of the big finance channels (Finary in France; Graham Stephan, How Money Works in the US):
one big object with a real shadow, 2-4 words max, a marker highlight on the key word, saturated flat colours,
arrows and circles. No glow, no gradient, no AI look."""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
O = os.path.join(D, "thumbs")
os.makedirs(O, exist_ok=True)
INTER = "/usr/share/fonts/opentype/inter/"
BLACKF, BOLD, SEMI = INTER + "InterDisplay-Black.otf", INTER + "Inter-Bold.otf", INTER + "Inter-SemiBold.otf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
W, H, SS = 1920, 1080, 2
INK, WHITE, PAPER = (17, 17, 17), (255, 255, 255), (244, 241, 234)
YELLOW, RED, GREEN, BLUE, ORANGE = (255, 212, 0), (228, 44, 44), (22, 168, 92), (30, 64, 190), (247, 147, 26)
f = lambda path, size: ImageFont.truetype(path, int(size * SS))
S = lambda v: [x * SS for x in v]


def canvas(bg):
    im = Image.new("RGBA", (W * SS, H * SS), bg + (255,))
    return im, ImageDraw.Draw(im, "RGBA")


def layer():
    l = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    return l, ImageDraw.Draw(l, "RGBA")


def shadowed(im, lay, dx=14, dy=22, blur=26, alpha=110):
    """Composite a drawn layer with a soft drop shadow under it (the 'sticker' look of big-channel thumbnails)."""
    a = lay.split()[3]
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: v * alpha // 255))
    sh = sh.filter(ImageFilter.GaussianBlur(blur * SS))
    im.alpha_composite(sh, (dx * SS, dy * SS))
    im.alpha_composite(lay)


def T(d, xy, txt, font, fill, anchor="ls"):
    d.text((xy[0] * SS, xy[1] * SS), txt, font=font, fill=fill, anchor=anchor)


def tw(d, txt, font):
    return d.textlength(txt, font=font) / SS


def marker(d, x, y, txt, font, fg, bg, pad=22, tilt=0):
    """Word on a highlighter block; (x, y) = baseline start."""
    l, t, r, b = [v / SS for v in d.textbbox((x * SS, y * SS), txt, font=font, anchor="ls")]
    d.polygon(S([l - pad, t - pad - tilt, r + pad, t - pad + tilt, r + pad, b + pad + tilt, l - pad, b + pad - tilt]), fill=bg)
    T(d, (x, y), txt, font, fg)
    return r - l


def arrow(d, x0, y0, x1, y1, col, width=26, head=70):
    import math
    ang = math.atan2(y1 - y0, x1 - x0)
    bx, by = x1 - head * 0.8 * math.cos(ang), y1 - head * 0.8 * math.sin(ang)
    d.line(S([x0, y0, bx, by]), fill=col, width=width * SS)
    p = [(x1, y1), (bx + head * 0.6 * math.cos(ang + math.pi / 2), by + head * 0.6 * math.sin(ang + math.pi / 2)),
         (bx - head * 0.6 * math.cos(ang + math.pi / 2), by - head * 0.6 * math.sin(ang + math.pi / 2))]
    d.polygon([(px * SS, py * SS) for px, py in p], fill=col)


def cursor(d, x, y, s=1.0):
    p = [(0, 0), (0, 74), (18, 57), (31, 88), (45, 82), (32, 52), (56, 52)]
    d.polygon([((x + px * s) * SS, (y + py * s) * SS) for px, py in p], fill=WHITE, outline=INK, width=int(5 * SS))


def done(im, name):
    out = im.convert("RGB").resize((1280, 720), Image.LANCZOS)
    out.save(os.path.join(O, name), quality=95)
    return out


# ---------------------------------------------------------------- ETF · a basket full of companies
im, d = canvas(PAPER)
lay, ld = layer()
ld.rounded_rectangle(S([200, 470, 960, 900]), radius=40 * SS, fill=INK)                       # basket
for k in range(5):
    ld.line(S([300 + k * 150, 500, 300 + k * 150, 870]), fill=(60, 60, 60), width=10 * SS)
ld.arc(S([330, 200, 830, 700]), 200, 340, fill=INK, width=34 * SS)                              # handle
cols = [ORANGE, BLUE, GREEN, RED, YELLOW, (150, 90, 230), (0, 170, 200), (240, 100, 160)]
k = 0
for row in range(3):
    for c in range(6 - (row % 2)):
        x, y = 250 + c * 118 + (row % 2) * 59, 300 + row * 62 + (row % 2) * 6     # the pile stays above the rim
        ld.rounded_rectangle(S([x, y, x + 100, y + 100]), radius=16 * SS, fill=cols[k % len(cols)])
        k += 1
ld.rounded_rectangle(S([200, 470, 960, 560]), radius=20 * SS, fill=INK)                       # rim in front of the tiles
shadowed(im, lay)
T(d, (1040, 330), "1 ETF =", f(BLACKF, 120), INK)
marker(d, 1040, 500, "1,300", f(BLACKF, 160), INK, YELLOW, tilt=4)
T(d, (1040, 640), "companies", f(BLACKF, 110), INK)
T(d, (1046, 790), "every ETF, explained", f(SEMI, 56), (110, 104, 92))
t_etf = done(im, "thumb_X1_etf_basket.jpg")

# ---------------------------------------------------------------- POV €200 a month · the before/after
im, d = canvas((232, 246, 236))
lay, ld = layer()
ld.rounded_rectangle(S([120, 300, 760, 820]), radius=36 * SS, fill=WHITE)
ld.text((440 * SS, 470 * SS), "every month", font=f(SEMI, 54), fill=(110, 110, 110), anchor="ms")
ld.text((440 * SS, 680 * SS), "€200", font=f(BLACKF, 220), fill=INK, anchor="ms")
ld.rounded_rectangle(S([1100, 210, 1800, 870]), radius=36 * SS, fill=INK)
ld.text((1450 * SS, 380 * SS), "30 years later", font=f(SEMI, 54), fill=(170, 170, 170), anchor="ms")
ld.text((1450 * SS, 610 * SS), "€244k", font=f(BLACKF, 185), fill=(80, 220, 140), anchor="ms")
ld.text((1450 * SS, 760 * SS), "(hypothetical, 7% / year)", font=f(SEMI, 40), fill=(150, 150, 150), anchor="ms")
shadowed(im, lay)
arrow(d, 790, 560, 1070, 560, GREEN, width=34, head=90)
marker(d, 120, 200, "POV: you're 25", f(BLACKF, 96), WHITE, INK, tilt=-3)
t_pov = done(im, "thumb_X2_pov200_before_after.jpg")

# ---------------------------------------------------------------- accounts · the cards on EU blue
im, d = canvas(BLUE)
import math
for k in range(12):                                                        # the ring of stars, flat and large
    a = math.radians(-90 + 30 * k)
    cx, cy, r = 1460 + 360 * math.cos(a), 540 + 360 * math.sin(a), 34
    pts = []
    for j in range(10):
        rr = r if j % 2 == 0 else r * 0.42
        aa = math.radians(-90 + 36 * j)
        pts.append(((cx + rr * math.cos(aa)) * SS, (cy + rr * math.sin(aa)) * SS))
    d.polygon(pts, fill=YELLOW)
CW, CH = 640, 404


def card(face, fg, label):
    c = Image.new("RGBA", (CW * SS, CH * SS), (0, 0, 0, 0))
    cd = ImageDraw.Draw(c, "RGBA")
    cd.rounded_rectangle([0, 0, CW * SS - 1, CH * SS - 1], radius=34 * SS, fill=face + (255,))
    cd.text((44 * SS, 130 * SS), label, font=f(BLACKF, 110), fill=fg + (255,), anchor="ls")
    cd.rounded_rectangle(S([50, 200, 150, 275]), radius=14 * SS, fill=(214, 178, 96, 255))
    return c


lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
for k, (face, fg, lab) in enumerate((((60, 60, 64), WHITE, "ISK"), (INK, WHITE, "PEA"), (WHITE, INK, "ISA"), (ORANGE, INK, "Depot"))):
    r = card(face, fg, lab).rotate(-7, resample=Image.BICUBIC, expand=True)
    lay.alpha_composite(r, (int((150 + k * 60) * SS), int((120 + k * 150) * SS)))
shadowed(im, lay, alpha=140)
d = ImageDraw.Draw(im, "RGBA")
marker(d, 1240, 520, "WHICH", f(BLACKF, 120), INK, YELLOW, tilt=3)
marker(d, 1240, 680, "ONE?", f(BLACKF, 120), INK, YELLOW, tilt=-3)
t_acc = done(im, "thumb_X3_accounts_which_one.jpg")

# ---------------------------------------------------------------- mistakes · don't press it
im, d = canvas(PAPER)
lay, ld = layer()
ld.rounded_rectangle(S([230, 520, 1150, 900]), radius=70 * SS, fill=(160, 20, 20))                # button base (3D)
ld.rounded_rectangle(S([230, 470, 1150, 850]), radius=70 * SS, fill=RED)
ld.text((690 * SS, 740 * SS), "SELL", font=f(BLACKF, 250), fill=WHITE, anchor="ms")
shadowed(im, lay)
cursor(d, 1040, 760, 2.8)
marker(d, 140, 250, "DON'T", f(BLACKF, 170), WHITE, INK, tilt=-4)
T(d, (720, 250), "press it.", f(BLACKF, 130), INK)
T(d, (1290, 620), "12 investing", f(BLACKF, 76), INK)
T(d, (1290, 710), "mistakes", f(BLACKF, 76), INK)
T(d, (1296, 790), "and what they cost", f(SEMI, 48), (110, 104, 92))
t_mis = done(im, "thumb_X4_mistakes_dont_press.jpg")

# ---------------------------------------------------------------- fees · never press this (the ATM)
im, d = canvas((222, 226, 230))
lay, ld = layer()
ld.rounded_rectangle(S([120, 90, 1180, 1000]), radius=44 * SS, fill=(52, 56, 62))
ld.rounded_rectangle(S([180, 150, 1120, 760]), radius=24 * SS, fill=(14, 52, 92))
ld.text((650 * SS, 300 * SS), "Pay in EUR or", font=f(BOLD, 78), fill=WHITE, anchor="ms")
ld.text((650 * SS, 390 * SS), "local currency?", font=f(BOLD, 78), fill=WHITE, anchor="ms")
ld.rounded_rectangle(S([230, 480, 630, 680]), radius=18 * SS, fill=(235, 235, 235))
ld.text((430 * SS, 610 * SS), "LOCAL", font=f(BLACKF, 92), fill=INK, anchor="ms")
ld.rounded_rectangle(S([670, 480, 1070, 680]), radius=18 * SS, fill=(235, 235, 235))
ld.text((870 * SS, 610 * SS), "EUR", font=f(BLACKF, 100), fill=INK, anchor="ms")
ld.rounded_rectangle(S([400, 840, 900, 880]), radius=10 * SS, fill=(20, 20, 20))
shadowed(im, lay)
d.ellipse(S([620, 430, 1120, 730]), outline=RED, width=20 * SS)
arrow(d, 1440, 700, 1150, 610, RED, width=30, head=90)
marker(d, 1300, 330, "NEVER", f(BLACKF, 150), WHITE, RED, tilt=-3)
T(d, (1300, 500), "press", f(BLACKF, 120), INK)
T(d, (1300, 630), "this.", f(BLACKF, 120), INK)
t_fee = done(im, "thumb_X5_fees_never_press.jpg")

# ---------------------------------------------------------------- POV worst moment · you bought here
im, d = canvas(WHITE)
for g in range(5):                                                         # light chart grid
    d.line(S([100, 300 + g * 150, 1820, 300 + g * 150]), fill=(232, 232, 232), width=3 * SS)
pts = [(120, 840), (300, 760), (460, 690), (600, 580), (720, 470), (820, 400), (900, 360), (980, 520), (1080, 700), (1180, 860),
       (1260, 960), (1330, 990), (1420, 930)]
d.line([(x * SS, y * SS) for x, y in pts], fill=RED, width=18 * SS, joint="curve")
d.ellipse(S([900 - 34, 360 - 34, 900 + 34, 360 + 34]), fill=INK)
marker(d, 560, 200, "YOU BOUGHT HERE", f(BLACKF, 92), WHITE, INK, tilt=-2)
arrow(d, 900, 220, 900, 320, INK, width=20, head=60)
T(d, (1310, 540), "−57%", f(BLACKF, 190), RED)
marker(d, 1340, 700, "€10,000", f(BLACKF, 96), INK, YELLOW, tilt=3)
T(d, (1344, 800), "October 2007", f(SEMI, 52), (110, 110, 110))
t_wor = done(im, "thumb_X6_worst_bought_here.jpg")

sheet = Image.new("RGB", (1280 * 2 + 20, 720 * 3 + 40), (255, 255, 255))
for k, t in enumerate((t_etf, t_pov, t_acc, t_mis, t_fee, t_wor)):
    sheet.paste(t, ((k % 2) * 1300, (k // 2) * 740))
sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(os.path.join(O, "preview_v3.jpg"), quality=88)
small = Image.new("RGB", (6 * 330, 190), (255, 255, 255))
for k, t in enumerate((t_etf, t_pov, t_acc, t_mis, t_fee, t_wor)):
    small.paste(t.resize((320, 180), Image.LANCZOS), (k * 330, 5))
small.save(os.path.join(O, "preview_v3_small.jpg"), quality=90)
print("ok")
