"""Thumbnails, second round: one visual idea per thumbnail instead of the same three layouts every time.
Still flat and sober (black / white / sand / one orange accent, no glow, no gradient), but each one shows an object:
a SELL button, a quote on orange, a checklist, bank cards, a bank statement, an ATM screen, a calendar page, a chart."""
import math
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
O = os.path.join(D, "thumbs")
os.makedirs(O, exist_ok=True)
INTER = "/usr/share/fonts/opentype/inter/"
BLACKF, MED, SEMI, BOLD = (INTER + "InterDisplay-Black.otf", INTER + "Inter-Medium.otf", INTER + "Inter-SemiBold.otf",
                           INTER + "Inter-Bold.otf")
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONOB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
CHARTER_BI = subprocess.run(["fc-match", "-f", "%{file}", "Bitstream Charter:style=Bold Italic"], capture_output=True, text=True).stdout
W, H, SS = 1920, 1080, 2
BG, WHITE, GREY, ORANGE = (10, 10, 10), (245, 245, 242), (120, 120, 120), (247, 147, 26)
SAND, INK, PAPER, DARK2 = (236, 226, 208), (18, 18, 18), (246, 244, 238), (34, 34, 36)
f = lambda path, size: ImageFont.truetype(path, int(size * SS))
S = lambda v: [x * SS for x in v]


def canvas(bg, size=(W, H)):
    im = Image.new("RGBA", (size[0] * SS, size[1] * SS), bg + (255,))
    return im, ImageDraw.Draw(im, "RGBA")


def T(d, xy, txt, font, fill, anchor="ls"):
    d.text((xy[0] * SS, xy[1] * SS), txt, font=font, fill=fill, anchor=anchor)


def tw(d, txt, font):
    return d.textlength(txt, font=font) / SS


def done(im, name):
    out = im.convert("RGB").resize((1280, 720), Image.LANCZOS)
    out.save(os.path.join(O, name), quality=95)
    return out


def cursor(d, x, y, s=1.0):
    """Flat mouse pointer, tip at (x, y)."""
    p = [(0, 0), (0, 74), (18, 57), (31, 88), (45, 82), (32, 52), (56, 52)]
    pts = [((x + px * s) * SS, (y + py * s) * SS) for px, py in p]
    d.polygon(pts, fill=WHITE, outline=INK, width=int(4 * SS))


def paste_rotated(base, layer, cx, cy, angle):
    r = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(r, (int(cx * SS - r.width / 2), int(cy * SS - r.height / 2)))


# ---------------------------------------------------------------- mistakes · the SELL button
im, d = canvas(BG)
T(d, (90, 230), "the most expensive", f(BLACKF, 112), WHITE)
T(d, (90, 360), "button.", f(BLACKF, 112), WHITE)
d.rounded_rectangle(S([150, 520, 1050, 860]), radius=60 * SS, fill=ORANGE)
d.rounded_rectangle(S([150, 520, 1050, 860]), radius=60 * SS, outline=(255, 190, 110), width=6 * SS)
T(d, (600, 760), "SELL", f(BLACKF, 230), INK, anchor="ms")
cursor(d, 930, 770, 2.4)
T(d, (1230, 700), "panic selling", f(MED, 60), GREY)
T(d, (1230, 780), "is mistake #6", f(MED, 60), GREY)
T(d, (1230, 860), "of 12.", f(MED, 60), GREY)
m_sell = done(im, "thumb_M4_mistakes_sell_button.jpg")

# ---------------------------------------------------------------- mistakes · a quote on orange
im, d = canvas(ORANGE)
fq = f(CHARTER_BI, 190)
T(d, (110, 360), "“It's only", fq, INK)
T(d, (110, 580), "1.8% a year.”", fq, INK)
d.rectangle(S([116, 660, 116 + 700, 672]), fill=INK)
T(d, (110, 860), "−€60,000", f(BLACKF, 200), INK)
T(d, (1180, 860), "mistake #4 of 12", f(MED, 56), (60, 36, 6))
m_quote = done(im, "thumb_M5_mistakes_quote.jpg")

# ---------------------------------------------------------------- mistakes · how many have you made?
im, d = canvas(BG)
T(d, (90, 260), "How many", f(BLACKF, 150), WHITE)
T(d, (90, 420), "have you made?", f(BLACKF, 150), WHITE)
checked = {0, 4, 5}
for k in range(12):
    x, y = 100 + (k % 6) * 200, 560 + (k // 6) * 200
    if k in checked:
        d.rounded_rectangle(S([x, y, x + 140, y + 140]), radius=18 * SS, fill=ORANGE)
        d.line(S([x + 32, y + 74, x + 60, y + 104, x + 110, y + 40]), fill=INK, width=16 * SS, joint="curve")
    else:
        d.rounded_rectangle(S([x, y, x + 140, y + 140]), radius=18 * SS, outline=(90, 90, 90), width=6 * SS)
T(d, (1340, 700), "12 investing", f(MED, 58), GREY)
T(d, (1340, 780), "mistakes,", f(MED, 58), GREY)
T(d, (1340, 860), "explained.", f(MED, 58), GREY)
m_check = done(im, "thumb_M6_mistakes_checklist.jpg")

# ---------------------------------------------------------------- accounts · a fan of bank cards
im, d = canvas(BG)
CW, CH = 600, 378


def card(face, fg, label, outline=None):
    c = Image.new("RGBA", (CW * SS, CH * SS), (0, 0, 0, 0))
    cd = ImageDraw.Draw(c, "RGBA")
    cd.rounded_rectangle([0, 0, CW * SS - 1, CH * SS - 1], radius=34 * SS, fill=face + (255,),
                         outline=(outline + (255,)) if outline else None, width=5 * SS)
    cd.text((40 * SS, 120 * SS), label, font=f(BLACKF, 96), fill=fg + (255,), anchor="ls")
    cd.rounded_rectangle(S([50, 190, 140, 260]), radius=12 * SS, fill=(205, 170, 90, 255))       # chip
    for k in range(3):
        cd.line(S([50, 210 + k * 17, 140, 210 + k * 17]), fill=(150, 120, 60, 255), width=2 * SS)
    cd.text((CW * SS - 50 * SS, CH * SS - 50 * SS), "eu.", font=f(BLACKF, 40), fill=fg + (170,), anchor="rs")
    return c


# a neat stack: each card shows its top strip, where the account name is
for k, (face, fg, lab, ol) in enumerate((((70, 70, 74), WHITE, "ISK", None), (BG, WHITE, "PEA", (110, 110, 110)),
                                        (WHITE, INK, "ISA", None), (ORANGE, INK, "Depot", None))):
    paste_rotated(im, card(face, fg, lab, outline=ol), 440 + k * 55, 330 + k * 135, -6)
T(d, (1180, 400), "Which one", f(BLACKF, 128), WHITE)
T(d, (1180, 540), "is yours?", f(BLACKF, 128), WHITE)
T(d, (1186, 650), "every investment account", f(MED, 50), GREY)
T(d, (1186, 715), "in Europe, explained", f(MED, 50), GREY)
a_cards = done(im, "thumb_A4_accounts_cards.jpg")

# ---------------------------------------------------------------- fees · the bank statement, fees highlighted
im, d = canvas(BG)
st = Image.new("RGBA", (980 * SS, 900 * SS), (0, 0, 0, 0))
sd = ImageDraw.Draw(st, "RGBA")
sd.rectangle([0, 0, 980 * SS, 900 * SS], fill=PAPER + (255,))
sd.text((60 * SS, 110 * SS), "STATEMENT · OCTOBER", font=f(MONOB, 40), fill=INK + (255,), anchor="ls")
sd.line(S([60, 140, 920, 140]), fill=INK + (255,), width=3 * SS)
rows = [("03/10", "GROCERIES", "−42.18", False), ("04/10", "ACCOUNT FEE", "−8.00", True), ("05/10", "RENT", "−720.00", False),
        ("07/10", "CARD FEE", "−4.50", True), ("09/10", "FX MARKUP", "−3.12", True), ("11/10", "SALARY", "+2,140.00", False),
        ("12/10", "INCIDENT FEE", "−8.00", True), ("14/10", "PHONE", "−19.99", False)]
fr = f(MONO, 38)
for k, (dt, lab, amt, fee) in enumerate(rows):
    y = 230 + k * 82
    if fee:
        sd.rectangle(S([44, y - 50, 936, y + 16]), fill=ORANGE + (150,))
    sd.text((60 * SS, y * SS), dt, font=fr, fill=(90, 90, 90, 255), anchor="ls")
    sd.text((230 * SS, y * SS), lab, font=f(MONOB, 38) if fee else fr, fill=INK + (255,), anchor="ls")
    sd.text((920 * SS, y * SS), amt, font=f(MONOB, 38) if fee else fr, fill=INK + (255,), anchor="rs")
paste_rotated(im, st, 560, 560, 4)
T(d, (1150, 430), "You pay", f(BLACKF, 130), WHITE)
T(d, (1150, 570), "these.", f(BLACKF, 130), ORANGE)
T(d, (1156, 690), "every bank fee, explained", f(MED, 52), GREY)
f_statement = done(im, "thumb_F4_fees_statement.jpg")

# ---------------------------------------------------------------- fees · the ATM question
im, d = canvas(BG)
d.rounded_rectangle(S([140, 90, 1240, 990]), radius=40 * SS, fill=DARK2)
d.rounded_rectangle(S([200, 150, 1180, 760]), radius=20 * SS, fill=(18, 40, 60))
T(d, (690, 290), "Pay in EUR", f(BOLD, 74), WHITE, anchor="ms")
T(d, (690, 380), "or in local currency?", f(BOLD, 74), WHITE, anchor="ms")
d.rounded_rectangle(S([250, 480, 670, 680]), radius=18 * SS, outline=(150, 160, 170), width=5 * SS)
T(d, (460, 600), "EUR", f(BLACKF, 90), (150, 160, 170), anchor="ms")
d.rounded_rectangle(S([710, 480, 1130, 680]), radius=18 * SS, fill=ORANGE)
T(d, (920, 600), "LOCAL", f(BLACKF, 90), INK, anchor="ms")
d.rounded_rectangle(S([420, 830, 960, 870]), radius=10 * SS, fill=(12, 12, 12))         # card slot
cursor(d, 1000, 640, 2.4)
T(d, (1310, 470), "the question", f(BLACKF, 84), WHITE)
T(d, (1310, 570), "that costs", f(BLACKF, 84), WHITE)
T(d, (1310, 670), "you money.", f(BLACKF, 84), ORANGE)
f_atm = done(im, "thumb_F5_fees_atm.jpg")

# ---------------------------------------------------------------- worst moment · the calendar page
im, d = canvas(SAND)
d.rounded_rectangle(S([150, 150, 830, 930]), radius=28 * SS, fill=PAPER, outline=(200, 190, 170), width=3 * SS)
d.rounded_rectangle(S([150, 150, 830, 330]), radius=28 * SS, fill=INK)
d.rectangle(S([150, 290, 830, 330]), fill=INK)
for x in (300, 680):                                                  # rings
    d.ellipse(S([x - 22, 118, x + 22, 162]), fill=(120, 110, 95))
T(d, (490, 265), "OCTOBER 2007", f(BLACKF, 64), PAPER, anchor="ms")
T(d, (490, 760), "9", f(BLACKF, 400), INK, anchor="ms")
T(d, (490, 860), "TUESDAY", f(SEMI, 48), (110, 100, 85), anchor="ms")
d.ellipse(S([300, 400, 680, 800]), outline=ORANGE, width=18 * SS)
T(d, (950, 420), "The worst day", f(BLACKF, 112), INK)
T(d, (950, 550), "to invest?", f(BLACKF, 112), INK)
T(d, (956, 680), "€10,000 · what happened next", f(SEMI, 54), (90, 82, 70))
w_cal = done(im, "thumb_W4_worst_calendar.jpg")

# ---------------------------------------------------------------- worst moment · "you bought here"
im, d = canvas(BG)
pts = [(120, 820), (260, 760), (380, 700), (500, 610), (600, 520), (690, 470), (760, 440), (820, 520), (900, 640), (980, 760),
       (1060, 880), (1110, 930), (1170, 900)]
d.line([(x * SS, y * SS) for x, y in pts], fill=WHITE, width=12 * SS, joint="curve")
d.ellipse(S([760 - 26, 440 - 26, 760 + 26, 440 + 26]), fill=ORANGE)
d.line(S([760, 300, 760, 400]), fill=ORANGE, width=8 * SS)
d.polygon(S([740, 390, 780, 390, 760, 415]), fill=ORANGE)
T(d, (760, 270), "you bought here.", f(BLACKF, 80), ORANGE, anchor="ms")
T(d, (1230, 900), "−57%", f(BLACKF, 220), WHITE)
T(d, (96, 150), "POV: €10,000 in October 2007", f(MONO, 50), GREY)
w_here = done(im, "thumb_W5_worst_bought_here.jpg")

sheet = Image.new("RGB", (1280 * 2 + 20, 720 * 4 + 60), (255, 255, 255))
for k, t in enumerate((m_sell, m_quote, m_check, a_cards, f_statement, f_atm, w_cal, w_here)):
    sheet.paste(t, ((k % 2) * 1300, (k // 2) * 740))
sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save(os.path.join(O, "preview_v2.jpg"), quality=88)
print("ok")
