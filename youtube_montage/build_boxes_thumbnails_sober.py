"""Sober thumbnails for the night's four videos, same system as the ETF and crypto ones (black / white / one orange accent):
per video a 'list' version (title + numbered boxes, the trap in orange), a serif-on-sand version, and one bold idea."""
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


def tw(d, txt, font):
    return d.textlength(txt, font=font) / SS


def list_thumb(name, top, bottom, sub, items, hot):
    im, d = canvas(BG)
    fb = f(BLACKF, 250)
    for size in (250, 220, 190, 170):                 # shrink the big words until they leave room for the list
        fb = f(BLACKF, size)
        if max(tw(d, top, fb), tw(d, bottom, fb)) < 1150:
            break
    T(d, (90, 420), top, fb, WHITE)
    T(d, (90, 650), bottom, fb, WHITE)
    T(d, (98, 790), sub, f(MED, 62), GREY)
    R(d, (98, 850, 98 + 120, 864), ORANGE)
    n = len(items)
    step = min(70, 840 / n)
    fl, fn = f(MONO, 40 if n <= 10 else 38), f(MONOB, 40 if n <= 10 else 38)
    for k, c in enumerate(items):
        y = 150 + k * step + (12 - n) * step / 2
        is_hot = c == hot
        col = ORANGE if is_hot else (WHITE if k < 3 else GREY)
        T(d, (1330, y), f"{k + 1:02d}", fn if is_hot else fl, col)
        T(d, (1420, y), c + ("  ←" if is_hot else ""), fn if is_hot else fl, col)
    return done(im, name)


def serif_thumb(name, l1, l2, n, hot, sub):
    im, d = canvas(SAND)
    fs = f(CHARTER_BI, 200)
    while max(tw(d, l1, fs), tw(d, l2, fs)) > 1700:
        fs = f(CHARTER_BI, fs.size / SS - 10)
    T(d, (110, 420), l1, fs, INK)
    T(d, (110, 640), l2, fs, INK)
    sq = min(66, 1100 / n - 26)
    for k in range(n):
        x = 116 + k * (sq + 26)
        R(d, (x, 760, x + sq, 760 + sq), ORANGE if k == hot else INK)
    T(d, (116, 920), sub, f(SEMI, 54), (90, 82, 70))
    return done(im, name)


def sheet(name, ims):
    sh = Image.new("RGB", (1280 * len(ims) + 20 * (len(ims) - 1), 720 + 20 + 180), (255, 255, 255))
    for j, t in enumerate(ims):
        sh.paste(t, (j * 1300, 0))
        sh.paste(t.resize((320, 180), Image.LANCZOS), (j * 1300, 740))
        sh.paste(t.resize((168, 94), Image.LANCZOS), (j * 1300 + 340, 740))
    sh.save(os.path.join(O, name))


# ---------------------------------------------------------------- every investment account
ACC = ["Savings account", "Brokerage account", "Tax-free account", "Life insurance", "Personal pension", "Workplace plan",
       "Kids' accounts", "Robo-advisor", "Trading account", "Foreign broker"]
a1 = list_thumb("thumb_A1_accounts_list.jpg", "EVERY", "ACCOUNT", "investing in Europe, explained", ACC, "Trading account")
a2 = serif_thumb("thumb_A2_accounts_serif.jpg", "Every account,", "explained.", 10, 8, "ISA · PEA · ISK · Depot · and the rest")
im, d = canvas(BG)
fa = f(BLACKF, 200)
for k, (w_, col) in enumerate((("ISA.", WHITE), ("PEA.", WHITE), ("ISK.", WHITE), ("Depot?", ORANGE))):
    T(d, (90 + (k % 2) * 860, 400 + (k // 2) * 260), w_, fa, col)
T(d, (96, 930), "every investment account in Europe, explained", f(MED, 60), GREY)
a3 = done(im, "thumb_A3_accounts_acronyms.jpg")
sheet("preview_accounts.png", (a1, a2, a3))

# ---------------------------------------------------------------- every investing mistake
MIS = ["Waiting to start", "No safety cushion", "Money needed soon", "High fees", "Timing the market", "Panic selling",
       "Chasing winners", "One big bet", "Trading too much", "Following hype", "Not understanding", "Wrong account"]
m1 = list_thumb("thumb_M1_mistakes_list.jpg", "EVERY", "MISTAKE", "investing, explained", MIS, "Panic selling")
m2 = serif_thumb("thumb_M2_mistakes_serif.jpg", "Every mistake,", "explained.", 12, 5, "12 investing mistakes · and how to avoid them")
im, d = canvas(BG)
f12 = f(BLACKF, 760)
T(d, (60, 860), "12", f12, WHITE)
x1 = 60 + tw(d, "12", f12)
R(d, (x1 + 30, 860 - 150, x1 + 30 + 150, 860), ORANGE)
T(d, (1180, 470), "investing", f(BLACKF, 120), WHITE)
T(d, (1180, 610), "mistakes,", f(BLACKF, 120), WHITE)
T(d, (1180, 750), "explained.", f(BLACKF, 120), GREY)
m3 = done(im, "thumb_M3_mistakes_12.jpg")
sheet("preview_mistakes.png", (m1, m2, m3))

# ---------------------------------------------------------------- every bank fee
FEE = ["Account fees", "Card fees", "Overdraft fees", "Currency fees", "\"Pay in euros?\"", "Transfer fees", "Fund fees",
       "Entry fees", "Broker fees", "\"Free\" trading"]
fe1 = list_thumb("thumb_F1_fees_list.jpg", "EVERY", "FEE", "your bank charges you, explained", FEE, "\"Pay in euros?\"")
fe2 = serif_thumb("thumb_F2_fees_serif.jpg", "Every bank fee,", "explained.", 10, 4, "the small ones add up")
im, d = canvas(BG)
T(d, (90, 420), "“Pay in", f(BLACKF, 220), WHITE)
T(d, (90, 650), "euros?”", f(BLACKF, 220), WHITE)
T(d, (1180, 650), "No.", f(BLACKF, 300), ORANGE)
T(d, (96, 880), "every bank fee, explained", f(MED, 66), GREY)
fe3 = done(im, "thumb_F3_fees_question.jpg")
sheet("preview_fees.png", (fe1, fe2, fe3))

# ---------------------------------------------------------------- POV: the worst possible moment
im, d = canvas(BG)
T(d, (96, 190), "POV: October 2007", f(MONO, 64), GREY)
T(d, (80, 500), "€10,000", f(BLACKF, 300), WHITE)
R(d, (98, 580, 98 + 120, 594), ORANGE)
T(d, (96, 740), "invested at the very top.", f(MED, 80), GREY)
T(d, (90, 940), "then what?", f(BLACKF, 150), ORANGE)
w1 = done(im, "thumb_W1_worst_10000.jpg")
w2 = serif_thumb("thumb_W2_worst_serif.jpg", "10,000 euros at the", "worst moment.", 6, 2, "what happened next · real market data")
im, d = canvas(BG)
fm = f(BLACKF, 520)
T(d, (60, 700), "−57%", fm, WHITE)
x1 = 60 + tw(d, "−57%", fm)
R(d, (x1 + 30, 700 - 110, x1 + 30 + 110, 700), ORANGE)
T(d, (80, 900), "you bought the top. now what?", f(MED, 76), GREY)
w3 = done(im, "thumb_W3_worst_57.jpg")
sheet("preview_worst.png", (w1, w2, w3))
print("ok")
