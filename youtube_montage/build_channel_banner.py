"""Channel banner (2560x1440, text kept inside YouTube's 1546x423 safe area) and video watermark for 'Euro Unboxed',
in the flat typographic style of the logos. Dark version goes with logo 1 'eu.', sand version with logo 3."""
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
O = os.path.join(D, "logos")
os.makedirs(O, exist_ok=True)
INTER = "/usr/share/fonts/opentype/inter/"
BLACKF, MED = INTER + "InterDisplay-Black.otf", INTER + "Inter-Medium.otf"
CHARTER_BI = subprocess.run(["fc-match", "-f", "%{file}", "Bitstream Charter:style=Bold Italic"], capture_output=True, text=True).stdout
W, H, SS = 2560, 1440, 2
SAFE = ((W - 1546) / 2, (H - 423) / 2, (W + 1546) / 2, (H + 423) / 2)        # visible on every device
BG, WHITE, GREY, ORANGE = (10, 10, 10), (245, 245, 242), (130, 130, 130), (247, 147, 26)
SAND, INK, INK2 = (236, 226, 208), (18, 18, 18), (95, 86, 72)
f = lambda path, size: ImageFont.truetype(path, int(size * SS))


def banner(bg, fg, sub, title_font, name, period=True):
    im = Image.new("RGB", (W * SS, H * SS), bg)
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = SAFE
    cx = W / 2 * SS
    # centred stack inside the safe area: wordmark, tagline, the 12 boxes with one in orange
    ft = title_font
    w = d.textlength("Euro Unboxed", font=ft)
    s = 34 * SS if period else 0
    left = cx - (w + (14 * SS + s if period else 0)) / 2
    base = (y0 + 205) * SS
    d.text((left, base), "Euro Unboxed", font=ft, fill=fg, anchor="ls")
    if period:
        d.rectangle([left + w + 14 * SS, base - s, left + w + 14 * SS + s, base], fill=ORANGE)
    d.text((cx, (y0 + 288) * SS), "money, explained for Europeans", font=f(MED, 50), fill=sub, anchor="ms")
    for k in range(12):
        bx = W / 2 - 12 * 36 / 2 + k * 36 + 6
        d.rectangle([bx * SS, (y0 + 335) * SS, (bx + 24) * SS, (y0 + 359) * SS], fill=ORANGE if k == 10 else fg)
    out = im.resize((W, H), Image.LANCZOS)
    out.save(os.path.join(O, name), quality=95)
    return out


dark = banner(BG, WHITE, GREY, f(BLACKF, 132), "banner_dark_euro_unboxed.jpg")
sand = banner(SAND, INK, INK2, f(CHARTER_BI, 140), "banner_sand_euro_unboxed.jpg", period=False)

# watermark (shown bottom-right on every video, acts as a subscribe button): 'eu.' on transparent
S = 300
wm = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
d = ImageDraw.Draw(wm)
fw = f(BLACKF, 150)
x0, y0, x1, y1 = d.textbbox((0, 0), "eu", font=fw, anchor="ls")
tw = x1 - x0 + 34 * SS
bx = (S * SS - tw) / 2 - x0
by = (S * SS + (y1 - y0)) / 2 - y1
d.rounded_rectangle([0, 0, S * SS - 1, S * SS - 1], 40 * SS, fill=BG + (255,))
d.text((bx, by), "eu", font=fw, fill=WHITE + (255,), anchor="ls")
s = 30 * SS
d.rectangle([bx + x1 + 6 * SS, by + y1 - s, bx + x1 + 6 * SS + s, by + y1], fill=ORANGE + (255,))
wm.resize((S, S), Image.LANCZOS).save(os.path.join(O, "watermark_eu.png"))

# preview: how the banner is cropped on TV / desktop / mobile, with the safe area marked
prev = Image.new("RGB", (1300, 1080), (255, 255, 255))
pd = ImageDraw.Draw(prev)
lab = ImageFont.truetype(INTER + "Inter-SemiBold.otf", 24)
for j, (img, nm) in enumerate(((dark, "dark (logo 1)"), (sand, "sand (logo 3)"))):
    y = 20 + j * 530
    tv = img.resize((640, 360), Image.LANCZOS)
    prev.paste(tv, (20, y + 40))
    sx0, sy0, sx1, sy1 = [v / 4 for v in SAFE]
    pd.rectangle([20 + sx0, y + 40 + sy0, 20 + sx1, y + 40 + sy1], outline=(232, 58, 64), width=2)
    pd.text((20, y + 8), f"{nm} · full image (TV), red = safe area", font=lab, fill=(30, 30, 30))
    desk = img.crop((0, int((H - 423) / 2), W, int((H + 423) / 2))).resize((620, 102), Image.LANCZOS)
    prev.paste(desk, (670, y + 70))
    pd.text((670, y + 36), "desktop", font=lab, fill=(30, 30, 30))
    mob = img.crop((int(SAFE[0]), int(SAFE[1]), int(SAFE[2]), int(SAFE[3]))).resize((420, 115), Image.LANCZOS)
    prev.paste(mob, (670, y + 230))
    pd.text((670, y + 196), "mobile", font=lab, fill=(30, 30, 30))
prev.save(os.path.join(O, "preview_banners.png"))
print("ok")
