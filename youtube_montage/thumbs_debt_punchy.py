"""Louder thumbnails for 'The Minimum Payment Trap (and How to Escape It)' (D4-D7), in the style that worked for the
shop-tricks video (B10): a flat block of colour on half the frame, a shocked face or one big object, two to four words.
Every number is one the video uses: €3,000 card, a fixed €60 a month = about 9 years and ~€3,500 of interest (so about
€6,500 paid in all); a 2% minimum = 30+ years."""
from thumbs_tricks_punchy import *  # noqa: F401,F403
from thumbs_tricks_punchy import block, d, render, shock
from doodle import calendar, coin, phone
from build_debt import bank

ims = []
# ---------------------------------------------------------------- D4: the payoff bar that barely moves - 9 YEARS.
px, py, ps = 1460, 560, 3.0
els = [block([(980, -20), (1940, -20), (1940, 1100), (1100, 1100)], ORANGE),
       d(phone(px, py, ps), 3),
       T("debt paid:", px, py - 250, 64, INK, at=0, anchor="m"),
       d([Fl(P_rect(px - 200, py - 200, 400, 70, 0, r=30), (236, 232, 222)), stk(P_rect(px - 200, py - 200, 400, 70, 6, r=30), 7),
          Fl(P_rect(px - 194, py - 194, 34, 58, 0, r=26), GREEN)], 4),
       T("4%", px - 120, py - 40, 90, GREEN, at=0, anchor="m"),
       T("9 years\nleft", px, py + 130, 110, RED, at=0, anchor="m", lh=1.0),
       d(shock(470, 760, 170, look=1.0), 5),
       T("€3,000 card:", 90, 200, 110, INK, at=0, rot=-3), T("9 YEARS.", 100, 430, 210, RED, at=0, rot=-3)]
assert 100 + text_w("9 YEARS.", 210) < 1080, text_w("9 YEARS.", 210)
ims.append(render("D4_9_years", els))
# ---------------------------------------------------------------- D5: borrowed €3,000, paid €6,500 - you pay DOUBLE.
c1 = [(1130, 150), (1800, 120), (1820, 400), (1150, 430)]
c2 = [(1080, 540), (1850, 500), (1880, 930), (1110, 970)]
els = [block([(960, -20), (1940, -20), (1940, 1100), (1060, 1100)], HL),
       d([Fl(P_poly(c1, True), WHITE), stk(P_poly(c1, True), 8)], 3),
       T("borrowed", 1200, 240, 66, GREY, at=0, rot=-2), T("€3,000", 1220, 370, 130, INK, at=0, rot=-2),
       d([Fl(P_poly(c2, True), WHITE), stk(P_poly(c2, True), 9)], 4),
       T("paid", 1170, 660, 80, GREY, at=0, rot=-3), T("€6,500", 1170, 860, 200, RED, at=0, rot=-3),
       d(shock(480, 760, 170, look=1.0), 5),
       T("you pay", 90, 210, 160, INK, at=0, rot=-3), T("DOUBLE.", 110, 430, 200, RED, at=0, rot=-3)]
assert 110 + text_w("DOUBLE.", 200) < 1000 and 1170 + text_w("€6,500", 200) < 1860
ims.append(render("D5_you_pay_double", els))
# ---------------------------------------------------------------- D6: a 2% minimum - 30+ YEARS?! (mirrored: block on the left)
els = [block([(-20, -20), (900, -20), (780, 1100), (-20, 1100)], PINK)]
for k, (yr, x, y, col) in enumerate((("2026", 250, 300, INK), ("2041", 420, 560, INK), ("2056", 330, 840, RED))):
    els.append(d(calendar(x, y, 1.55, head=None), 10 + k))
    els.append(T(yr, x, y + 45, 130, col, at=0, anchor="m"))          # above where the next page starts
els += [
        d(shock(1500, 800, 165, look=-1.0), 5),
        T("a 2% minimum:", 1000, 200, 96, INK, at=0, rot=-3), T("30+ YEARS.", 960, 420, 190, RED, at=0, rot=-3)]
assert 960 + text_w("30+ YEARS.", 190) < 1890, text_w("30+ YEARS.", 190)
ims.append(render("D6_30_years", els))
# ---------------------------------------------------------------- D7: banks LOVE this button
els = [block([(1000, -20), (1940, -20), (1940, 1100), (1120, 1100)], ORANGE),
       d(bank(1480, 420, 1.35), 3),
       d([Fl(P_rect(240, 560, 640, 330, 0, r=50), ORANGE), stk(P_rect(240, 560, 640, 330, 10, r=50), 11)], 6),
       T("PAY\nMINIMUM", 560, 700, 120, INK, at=0, anchor="m", lh=1.0),
       d([stk(P_bez((900, 700), (990, 760), (1080, 760), (1160, 690)), 9, RED), stk(P_poly([(1125, 680), (1165, 688), (1150, 728)]), 9, RED)], 7),
       d(coin(1000, 860, 1.3) + coin(1110, 900, 1.1) + coin(1210, 850, 1.2), 8),
       T("banks", 90, 200, 150, INK, at=0, rot=-3), T("LOVE it.", 120, 400, 190, RED, at=0, rot=-3)]
assert 120 + text_w("LOVE it.", 190) < 1000
ims.append(render("D7_banks_love_it", els))

small = Image.new("RGB", (4 * 178 + 10, 114), (255, 255, 255))
for k, im in enumerate(ims):
    small.paste(im.resize((168, 94), Image.LANCZOS), (10 + k * 178, 10))
small.save(os.path.join(OUT, "feed_size_D4_D7.png"))
sheet = Image.new("RGB", (1280, 720))
for k, im in enumerate(ims):
    sheet.paste(im.resize((640, 360), Image.LANCZOS), ((k % 2) * 640, (k // 2) * 360))
sheet.save(os.path.join(OUT, "sheet_D4_D7.jpg"), quality=90)
print("ok")
