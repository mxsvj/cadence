"""Sober thumbnails for 'Every ETF Explained in 11 Minutes', same system as the crypto ones and the 'eu.' logo:
black / white / one orange accent, no glow, no gradient, no glitch.
S1 = 'EVERY ETF' + the 12 boxes as a numbered list, 'Leveraged' (the trap) marked in orange
S2 = editorial: black serif italic on warm sand, 12 squares with one orange
S3 = a giant '12.' with the orange square full stop of the logo, 'types of ETFs, explained.'"""
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
O = os.path.join(D, "thumbs")
os.makedirs(O, exist_ok=True)
INTER = "/usr/share/fonts/opentype/inter/"
BLACKF, MED, SEMI = INTER + "InterDisplay-Black.otf", INTER + "Inter-Medium.otf", INTER + "Inter-SemiBold.otf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
CHARTER_BI = subprocess.run(["fc-match", "-f", "%{file}", "Bitstream Charter:style=Bold Italic"], capture_output=True, text=True).stdout
W, H, SS = 1920, 1080, 2
BG, WHITE, GREY, ORANGE = (10, 10, 10), (245, 245, 242), (120, 120, 120), (247, 147, 26)
SAND, INK = (236, 226, 208), (18, 18, 18)
f = lambda path, size: ImageFont.truetype(path, int(size * SS))
CATS = ["Index", "Country & region", "Sector", "Thematic", "Factor", "Dividend", "Bonds", "Money market", "Commodities",
        "Leveraged", "Active", "Crypto ETPs"]
HOT = "Leveraged"


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


# S1 · EVERY ETF + numbered list
im, d = canvas(BG)
T(d, (90, 420), "EVERY", f(BLACKF, 250), WHITE)
T(d, (90, 650), "ETF", f(BLACKF, 250), WHITE)
T(d, (98, 790), "explained in 11 minutes", f(MED, 62), GREY)
R(d, (98, 850, 98 + 120, 850 + 14), ORANGE)
fl, fn = f(MONO, 40), f(MONOB, 40)
for k, c in enumerate(CATS):
    y = 150 + k * 70
    scam = c == HOT
    col = ORANGE if scam else (WHITE if k < 3 else GREY)
    T(d, (1330, y), f"{k + 1:02d}", fn if scam else fl, col)
    T(d, (1420, y), c + ("  ←" if scam else ""), fn if scam else fl, col)
s1 = done(im, "thumb_S1_etf_list.jpg")

# S2 · editorial serif on sand
im, d = canvas(SAND)
fs = f(CHARTER_BI, 210)
T(d, (110, 420), "Every ETF,", fs, INK)
T(d, (110, 640), "explained.", fs, INK)
for k in range(12):
    x = 116 + k * 92
    R(d, (x, 760, x + 66, 826), ORANGE if k == 9 else INK)
T(d, (116, 920), "12 boxes · 11 minutes", f(SEMI, 54), (90, 82, 70))
s2 = done(im, "thumb_S2_etf_serif.jpg")

# S3 · giant '12.'
im, d = canvas(BG)
f12 = f(BLACKF, 760)
T(d, (60, 860), "12", f12, WHITE)
x1 = 60 + d.textlength("12", font=f12) / SS
R(d, (x1 + 30, 860 - 150, x1 + 30 + 150, 860), ORANGE)
T(d, (1180, 470), "types of", f(BLACKF, 120), WHITE)
T(d, (1180, 610), "ETFs,", f(BLACKF, 120), WHITE)
T(d, (1180, 750), "explained.", f(BLACKF, 120), GREY)
s3 = done(im, "thumb_S3_etf_12.jpg")

# comparison sheet: full size + YouTube sizes
sheet = Image.new("RGB", (1280 * 3 + 40, 720 + 20 + 180), (255, 255, 255))
for j, t in enumerate((s1, s2, s3)):
    sheet.paste(t, (j * 1300, 0))
    sheet.paste(t.resize((320, 180), Image.LANCZOS), (j * 1300, 740))
    sheet.paste(t.resize((168, 94), Image.LANCZOS), (j * 1300 + 340, 740))
sheet.save(os.path.join(O, "preview_etf_sober.png"))
print("ok")
