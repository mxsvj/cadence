"""Sober thumbnails for 'POV: You're 25 and Invest €200 a Month' (remake), same system as the ETF and crypto ones:
black / white / one orange accent, no glow, no gradient, no glitch.
P1 = '€200 / month' and, below, '30 years later: €244,000' with the figure in orange
P2 = editorial: black serif italic on warm sand, a row of 30 squares (one per year), the last one orange
P3 = '25 → 55' huge, with the orange square full stop of the logo"""
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
O = os.path.join(D, "thumbs")
os.makedirs(O, exist_ok=True)
INTER = "/usr/share/fonts/opentype/inter/"
BLACKF, MED, SEMI = INTER + "InterDisplay-Black.otf", INTER + "Inter-Medium.otf", INTER + "Inter-SemiBold.otf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
CHARTER_BI = subprocess.run(["fc-match", "-f", "%{file}", "Bitstream Charter:style=Bold Italic"], capture_output=True, text=True).stdout
W, H, SS = 1920, 1080, 2
BG, WHITE, GREY, ORANGE = (10, 10, 10), (245, 245, 242), (120, 120, 120), (247, 147, 26)
SAND, INK = (236, 226, 208), (18, 18, 18)
f = lambda path, size: ImageFont.truetype(path, int(size * SS))


def canvas(bg):
    im = Image.new("RGB", (W * SS, H * SS), bg)
    return im, ImageDraw.Draw(im)


def T(d, xy, txt, font, fill, anchor="ls"):
    d.text((xy[0] * SS, xy[1] * SS), txt, font=font, fill=fill, anchor=anchor)


def R(d, box, fill):
    d.rectangle([v * SS for v in box], fill=fill)


def done(im, name):
    out = im.resize((1280, 720), Image.LANCZOS)
    out.save(os.path.join(O, name), quality=95)
    return out


# P1 · €200 / month → €244,000
im, d = canvas(BG)
T(d, (96, 190), "POV: you're 25", f(MONO, 64), GREY)
f200 = f(BLACKF, 330)
T(d, (80, 520), "€200", f200, WHITE)
x = 80 + d.textlength("€200", font=f200) / SS
T(d, (x + 30, 520), "/ month", f(MED, 90), GREY)
R(d, (98, 600, 98 + 120, 614), ORANGE)
T(d, (96, 760), "30 years later:", f(MED, 80), GREY)
T(d, (90, 950), "€244,000", f(BLACKF, 190), ORANGE)
p1 = done(im, "thumb_P1_pov_200.jpg")

# P2 · editorial serif on sand
im, d = canvas(SAND)
fs = f(CHARTER_BI, 160)                                  # Charter has no € glyph, so the amount is written out
T(d, (110, 360), "200 euros a month,", fs, INK)
T(d, (110, 560), "for 30 years.", fs, INK)
for k in range(30):
    x = 116 + k * 56
    R(d, (x, 700, x + 40, 740), ORANGE if k == 29 else INK)
T(d, (116, 860), "what really happens in between", f(SEMI, 54), (90, 82, 70))
p2 = done(im, "thumb_P2_pov_serif.jpg")

# P3 · 25 → 55.
im, d = canvas(BG)
fb = f(BLACKF, 420)
T(d, (70, 640), "25", fb, GREY)
x = 70 + d.textlength("25", font=fb) / SS
T(d, (x + 40, 600), "→", f(MED, 200), GREY)
x2 = x + 40 + d.textlength("→", font=f(MED, 200)) / SS + 40
T(d, (x2, 640), "55", fb, WHITE)
x3 = x2 + d.textlength("55", font=fb) / SS
R(d, (x3 + 24, 640 - 90, x3 + 24 + 90, 640), ORANGE)
T(d, (80, 860), "€200 a month. Nothing else.", f(MED, 74), WHITE)
p3 = done(im, "thumb_P3_pov_25_55.jpg")

sheet = Image.new("RGB", (1280 * 3 + 40, 720 + 20 + 180), (255, 255, 255))
for j, t in enumerate((p1, p2, p3)):
    sheet.paste(t, (j * 1300, 0))
    sheet.paste(t.resize((320, 180), Image.LANCZOS), (j * 1300, 740))
    sheet.paste(t.resize((168, 94), Image.LANCZOS), (j * 1300 + 340, 740))
sheet.save(os.path.join(O, "preview_pov_sober.png"))
print("ok")
