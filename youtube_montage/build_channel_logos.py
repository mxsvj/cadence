"""Sober channel logos: flat, typographic, one accent colour at most (no glow, no gradient, no rainbow).
1 = 'eu.'      (Euro Unboxed)    white Inter Black on black, orange square full stop
2 = EURO / UNBOXED stacked        white on black, thin orange rule
3 = 'eu'       (Euro Unboxed)    black serif italic (Charter) on warm sand, editorial look
4 = 'dm_'      (Dark Mode Money) white Inter Black on black, green underscore cursor
Writes 1024 px avatars and a preview sheet at YouTube sizes."""
import os

from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
O = os.path.join(D, "logos")
os.makedirs(O, exist_ok=True)
INTER = "/usr/share/fonts/opentype/inter/"
BLACKF = INTER + "InterDisplay-Black.otf"
S, SS = 1024, 3                                   # final size, supersampling
BG, WHITE, ORANGE, GREEN = (10, 10, 10), (245, 245, 242), (247, 147, 26), (60, 200, 120)
SAND, INK = (236, 226, 208), (18, 18, 18)


def find_font(family_style):
    import subprocess
    out = subprocess.run(["fc-match", "-f", "%{file}", family_style], capture_output=True, text=True).stdout
    return out


CHARTER_BI = find_font("Bitstream Charter:style=Bold Italic")
f = lambda path, size: ImageFont.truetype(path, int(size * SS))


def canvas(bg):
    im = Image.new("RGB", (S * SS, S * SS), bg)
    return im, ImageDraw.Draw(im)


def done(im, name):
    out = im.resize((S, S), Image.LANCZOS)
    out.save(os.path.join(O, name))
    return out


def centered_text(d, txt, font, fill, cy, dx=0):
    x0, y0, x1, y1 = d.textbbox((0, 0), txt, font=font, anchor="ls")
    w, h = x1 - x0, y1 - y0
    x = (S * SS - w) / 2 - x0 + dx * SS
    y = cy * SS + h / 2 - y1
    d.text((x, y), txt, font=font, fill=fill, anchor="ls")
    return x + x0, y + y0, x + x1, y + y1


# 1 · eu.
im, d = canvas(BG)
x0, y0, x1, y1 = centered_text(d, "eu", f(BLACKF, 470), WHITE, 512, dx=-40)
s = 92 * SS
d.rectangle([x1 + 22 * SS, y1 - s, x1 + 22 * SS + s, y1], fill=ORANGE)
l1 = done(im, "logo_1_eu_dot.png")

# 2 · EURO / UNBOXED
im, d = canvas(BG)
fb = f(BLACKF, 158)
centered_text(d, "EURO", fb, WHITE, 410)
centered_text(d, "UNBOXED", f(BLACKF, 128), WHITE, 590)
d.rectangle([(S / 2 - 150) * SS, 712 * SS, (S / 2 + 150) * SS, 728 * SS], fill=ORANGE)
l2 = done(im, "logo_2_euro_unboxed_stack.png")

# 3 · eu, serif italic on sand
im, d = canvas(SAND)
centered_text(d, "eu", f(CHARTER_BI, 560), INK, 500)
l3 = done(im, "logo_3_eu_serif.png")

# 4 · dm_
im, d = canvas(BG)
x0, y0, x1, y1 = centered_text(d, "dm", f(BLACKF, 430), WHITE, 512, dx=-60)
d.rectangle([x1 + 26 * SS, y1 - 34 * SS, x1 + 26 * SS + 120 * SS, y1], fill=GREEN)        # underscore cursor: reads 'dm_', not 'dml'
l4 = done(im, "logo_4_dm_cursor.png")


def circle(img, dia):
    im = img.resize((dia, dia), Image.LANCZOS)
    m = Image.new("L", (dia * 4, dia * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, dia * 4 - 1, dia * 4 - 1], fill=255)
    out = Image.new("RGB", (dia, dia), (255, 255, 255))
    out.paste(im, (0, 0), m.resize((dia, dia), Image.LANCZOS))
    return out


sheet = Image.new("RGB", (1460, 560), (255, 255, 255))
dd = ImageDraw.Draw(sheet)
lab = ImageFont.truetype(INTER + "Inter-SemiBold.otf", 26)
names = ["1 · Euro Unboxed", "2 · Euro Unboxed", "3 · Euro Unboxed", "4 · Dark Mode Money"]
for k, img in enumerate((l1, l2, l3, l4)):
    x = 20 + k * 360
    dd.text((x + 160, 40), names[k], font=lab, fill=(30, 30, 30), anchor="ms")
    sheet.paste(circle(img, 320), (x, 70))
    sheet.paste(circle(img, 98), (x + 30, 420))
    sheet.paste(circle(img, 48), (x + 150, 445))
    sheet.paste(circle(img, 24), (x + 225, 457))
sheet.save(os.path.join(O, "preview_logos_v2.png"))
print("ok", CHARTER_BI)
