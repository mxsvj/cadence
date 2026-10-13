"""'How to Invest Your First €1,000 So Simply It Feels Illegal' (doodle style). Sources in the kit: Investor Compensation Schemes
Directive 97/9/EC (at least €20,000), S&P 500 2020 drawdown and recovery, UCITS. All growth figures hypothetical (7% a year)."""
import numpy as np

from doodle_video import *  # noqa: F401,F403

SAY = {"€1,000": "a thousand euros", "€1,000.": "a thousand euros", "20%": "twenty percent", "15": "fifteen", "PEA": "P E A", "ISA": "eye-suh",
       "ISK": "I S K", "UK": "U K", "EU": "E U", "€20,000": "twenty thousand euros", "€10": "ten euros", "1%": "one percent",
       "ETF": "E T F", "0.2%": "zero point two percent", "UCITS": "you-sits", "€50": "fifty euros", "7%": "seven percent",
       "€7,600": "seven thousand six hundred euros", "€100": "a hundred euros", "€130,000": "a hundred and thirty thousand euros",
       "2020": "twenty twenty", "S&P": "S and P", "500": "five hundred"}
V = Video("first1000", say=SAY, seed=23, keys=dict(prog=[(52, 55, 59, 62), (48, 52, 55, 60), (53, 57, 60, 64), (55, 59, 62, 67)],
                                                   roots=[40, 36, 41, 43], bpm=82),
          hush=[("And here's the part", "Your first €1,000 isn't")], tape="Final message", beat_groups=("o3",))
L = V.L

L("o1", "You've saved your first €1,000. Now what?")
L("o1", "Your bank offers a fund. A friend talks about crypto. Someone online has a secret strategy.")
L("o2", "So you do nothing, and the money just sits there, losing a little to inflation every year.")
L("o3", "And here's the part nobody tells you.")
L("o4", "Your first €1,000 isn't about getting rich. It's about building the habit that will.")
L("o5", "Here are the eight steps, in order. Let's begin.")

L("c1", "One. Kill expensive debt first.")
L("c1a", "If you have a credit card or a loan at 15 or 20% a year, pay that off first.")
L("c1a", "Every euro of that debt you repay earns you that rate, guaranteed. No investment promises that.")

L("c2", "Two. Keep a small safety cushion.")
L("c2a", "Before investing, keep some cash for surprises: a broken phone, a car repair, a big bill.")
L("c2a", "Start with one month of expenses, and build towards three to six. Otherwise, the first emergency forces you to sell at the worst moment.")

L("c3", "Three. Use the right account.")
L("c3a", "Many European countries have accounts with tax advantages. The PEA in France. The ISA in the UK. The ISK in Sweden.")
L("c3a", "The same investment, inside the right account, can leave you with noticeably more after tax. Check what your country offers.")

L("c4", "Four. Pick a regulated, low-cost broker.")
L("c4a", "Look for a broker regulated in the EU or the UK. In the EU, if a broker fails and can't give your investments back, compensation schemes cover at least €20,000.")
L("c4a", "Then look at the fees: per order, per year, and for currency exchange. On €1,000, a €10 fee is already 1%.")

L("c5", "Five. Buy the whole market.")
L("c5a", "Instead of guessing which company will win, buy them all, with one global index ETF.")
L("c5a", "One fund can hold well over a thousand companies across dozens of countries, for around 0.2% a year or less. In Europe, look for UCITS in the name.")

L("c6", "Six. Automate it.")
L("c6a", "Many brokers let you set up a monthly savings plan, sometimes for free. Even €50 a month.")
L("c6a", "Your first €1,000 becomes the start of a habit, not a one-off bet.")
L("c6b", "€1,000 left alone for thirty years at 7% a year grows to about €7,600. Add €100 a month, and it's about €130,000.")

L("c7", "Seven. Then don't touch it.")
L("c7a", "In early 2020, stock markets fell about a third in a few weeks. People who sold locked in the loss.")
L("c7a", "The S&P 500 was back at its record about five months after the bottom.")
L("c7b", "Don't check it every day. Once a month is plenty. Once a year is better.")

L("c8", "Eight. Keep learning, slowly.")
L("c8a", "Read one good book. Watch the fees. Ignore anyone promising fast, guaranteed returns.")
L("c8a", "If it sounds too good to be true, it usually is.")

L("f0", "Final message.")
L("f1", "The best first investment isn't a stock. It's a system: no expensive debt, a cushion, the right account, one cheap global fund, and automatic deposits.")
L("f2", "Boring? Yes. That's exactly why it works.")
L("end", "This is education, not financial advice. Rules differ by country, so check yours. If this helped, subscribe. "
         "Next up: compound interest, explained so simply it feels illegal.")


def book(x, y, s=1.0, col=(150, 186, 214)):
    return [Fl(P_rect(x - 110 * s, y - 150 * s, 220 * s, 300 * s, 0, r=8 * s), col), stk(P_rect(x - 110 * s, y - 150 * s, 220 * s, 300 * s, 8 * s, r=8 * s), 6.5 * s),
            stk(P_line(x - 80 * s, y - 150 * s, x - 80 * s, y + 150 * s, 0.01, 2), 5 * s),
            stk(P_line(x - 40 * s, y - 80 * s, x + 70 * s, y - 80 * s, 0.02, 3), 5 * s), stk(P_line(x - 40 * s, y - 40 * s, x + 50 * s, y - 40 * s, 0.02, 4), 5 * s)]


def globe(x, y, r=150, col=(190, 214, 230)):
    o = [Fl(P_ell(x, y, r, r, 1, closed=True), col), stk(P_ell(x, y, r, r, 2, 0.08), 7)]
    for k, rx in enumerate((0.35, 0.75)):
        o.append(stk(P_arc(x, y, r * rx, r, -90, 90, 30), 4.5))
        o.append(stk(P_arc(x, y, r * rx, r, 90, 270, 30), 4.5))
    for k, dy in enumerate((-0.5, 0, 0.5)):
        w = r * (1 - dy * dy) ** 0.5
        o.append(stk(P_line(x - w, y + dy * r, x + w, y + dy * r, 0.01, k), 4.5))
    return o


def building(x, y, s=1.0, sign="BANK"):
    o = [Fl(P_rect(x - 160 * s, y - 220 * s, 320 * s, 260 * s, 0), (250, 248, 242)), stk(P_rect(x - 160 * s, y - 220 * s, 320 * s, 260 * s, 8 * s), 7 * s),
         stk(P_poly([(x - 190 * s, y - 220 * s), (x, y - 320 * s), (x + 190 * s, y - 220 * s)], True), 7 * s)]
    for k in range(4):
        cx = x - 120 * s + k * 80 * s
        o.append(stk(P_line(cx, y - 180 * s, cx, y + 20 * s, 0.01, k), 6 * s))
    o.append(("g", sign, x, y - 240 * s, int(46 * s), INK, HAND, "m"))
    return o


def shield(x, y, s=1.0, col=(214, 226, 196)):
    pts = np.vstack([P_line(x - 110 * s, y - 120 * s, x + 110 * s, y - 120 * s, 0.03, 1),
                     P_bez((x + 110 * s, y - 120 * s), (x + 110 * s, y + 40 * s), (x + 40 * s, y + 110 * s), (x, y + 140 * s)),
                     P_bez((x, y + 140 * s), (x - 40 * s, y + 110 * s), (x - 110 * s, y + 40 * s), (x - 110 * s, y - 120 * s))])
    return [Fl(pts, col), stk(pts, 7 * s)]


def bill(x, y, s=1.0):
    return [Fl(P_rect(x - 80 * s, y - 100 * s, 160 * s, 200 * s, 0), (250, 248, 242)), stk(P_rect(x - 80 * s, y - 100 * s, 160 * s, 200 * s, 6 * s), 5.5 * s),
            stk(P_line(x - 50 * s, y - 50 * s, x + 50 * s, y - 50 * s, 0.02, 1), 4 * s, GREY), stk(P_line(x - 50 * s, y - 10 * s, x + 30 * s, y - 10 * s, 0.02, 2), 4 * s, GREY),
            ("g", "€€€", x, y + 70 * s, int(44 * s), RED, HAND, "m")]


# --------------------------------------------------------------------------- cold open
@V.scene("o1")
def _(S):
    S.add(Fig(480, 940, 1.3, at=0.0, poses=[("hold", 0), ("shrug", S.c("now"))], moods=[("happy", 0), ("worried", S.c("now"))], seed=3))
    S.pop(money_bag(500, 690, 0.65, label="€"), 0.1, (500, 690))
    S.text("€1,000", 380, 400, 100, ORANGE, at=S.c("€1,000") - 0.1)
    S.text("now what?", 640, 300, 80, GREY, at=S.c("now") - 0.1, rot=4)
    S.draw(building(1100, 560, 0.55), S.c("bank", 1) - 0.2, 0.4)
    S.draw(bubble(1180, 230, 300, 110, tail=(-1, 1)), S.c("fund", 1) - 0.2, 0.3, snd=None)
    S.text("our fund!", 1180, 250, 54, INK, at=S.c("fund", 1), anchor="m")
    S.add(Fig(1500, 1000, 0.8, at=S.c("friend", 1) - 0.2, poses=[("point_up", 0)], moods=[("grin", 0)], kind="spiky", seed=51, enter="pop"))
    S.draw(bubble(1560, 480, 280, 110, tail=(-1, 1)), S.c("crypto", 1) - 0.2, 0.3, snd=None)
    S.text("crypto!!", 1560, 500, 54, INK, at=S.c("crypto", 1), anchor="m")
    S.draw(phone(1760, 800, 0.5), S.c("online", 1) - 0.2, 0.3, snd=None)
    S.text("secret strategy", 1500, 1030, 54, RED, at=S.c("secret", 1), rot=-3)


@V.scene("o2")
def _(S):
    S.add(Fig(520, 940, 1.3, at=0.0, poses=[("shrug", 0), ("sad", S.c("sits"))], moods=[("flat", 0), ("worried", S.c("losing"))], seed=3))
    bx, by = 1200, 640

    def shrink(tt, t0=S.c("losing")):
        u = clamp((tt - t0) / 2.2)
        return (0, 0, 0, 1.0 - 0.3 * ease_io(u))
    S.add(Dr(money_bag(bx, by, 1.4), 0.0, 0.0, pop=True, anchor=(bx, by + 110), move=shrink, seed=8))
    S.text("inflation", 1040, 300, 90, RED, at=S.c("inflation") - 0.1, rot=-3)
    S.text("-a little, every year", 1000, 980, 64, GREY, at=S.c("every") - 0.1)


@V.scene("o3")
def _(S):
    S.add(Fig(980, 1520, 3.2, at=0.0, poses=[("stand", 0)], moods=[("smug", 0)], enter="none", seed=3, idle=0.6, look=0.4))
    S.text("psst.", 1430, 320, 96, GREY, at=S.c("part") - 0.2, rot=8)


@V.scene("o4")
def _(S):
    S.text("getting rich", 260, 380, 130, INK, at=S.c("rich") - 0.4)
    S.add(strike(240, 340, 260 + text_w("getting rich", 130), 332, S.c("rich") + 0.3, RED, 10))
    S.text("the habit.", 380, 700, 200, ORANGE, at=S.c("habit") - 0.2, rot=-4, cps=12)
    S.draw(calendar(1480, 560, 1.0, day=None, head="EVERY MONTH"), S.c("habit") - 0.4, 0.4)
    for k in range(6):
        S.add(check(1380 + (k % 3) * 100, 600 + (k // 3) * 90, 22, S.c("will") + 0.1 * k, GREEN, 7, seed=k))


@V.scene("o5")
def _(S):
    S.text("8", 300, 600, 380, ORANGE, at=S.c("eight") - 0.05, anchor="m", rot=-6, cps=8)
    S.text("steps", 470, 520, 130, INK, at=S.c("steps") - 0.1)
    S.text("in order.", 500, 680, 90, GREY, at=S.c("order") - 0.2)
    S.add(Fig(1550, 950, 1.2, at=0.0, poses=[("stand", 0), ("wave", S.c("begin"))], moods=[("smile", 0), ("happy", S.c("begin"))], seed=3, flip=True))


V.chapters({1: ("Kill expensive\ndebt first.", 0), 2: ("Keep a small\nsafety cushion.", 1), 3: ("Use the right\naccount.", 0),
            4: ("Pick a regulated,\nlow-cost broker.", 1), 5: ("Buy the whole\nmarket.", 0), 6: ("Automate it.", 1),
            7: ("Then don't\ntouch it.", 0), 8: ("Keep learning,\nslowly.", 1)}, peek={1, 4, 7})


# --------------------------------------------------------------------------- steps
@V.scene("c1a")
def _(S):
    S.draw(card(520, 480, 1.5), S.c("credit") - 0.2, 0.45)
    S.pop(tag(820, 680, 1.1, "20%/yr", (244, 214, 210), 58), S.c("20%") - 0.1, (820, 680))
    S.add(cross(520, 480, 180, S.c("off") + 0.05, RED, 12))
    S.text("pay it off first.", 260, 900, 96, ORANGE, at=S.c("pay") - 0.1, rot=-2)
    S.text("= a guaranteed 20%", 1000, 420, 86, INK, at=S.c("guaranteed", 1) - 0.3, rot=-3)
    S.text("no investment promises that.", 1000, 600, 60, GREY, at=S.c("promises", 1) - 0.3)


@V.scene("c2a")
def _(S):
    cx, cy = 960, 520
    pil = np.vstack([P_bez((cx - 220, cy - 80), (cx, cy - 150), (cx + 220, cy - 80)), P_bez((cx + 220, cy - 80), (cx + 270, cy), (cx + 220, cy + 80)),
                     P_bez((cx + 220, cy + 80), (cx, cy + 150), (cx - 220, cy + 80)), P_bez((cx - 220, cy + 80), (cx - 270, cy), (cx - 220, cy - 80))])
    S.draw([Fl(pil, (150, 186, 214)), stk(pil, 7), stk(P_bez((cx - 60, cy - 20), (cx, cy + 10), (cx + 60, cy - 20)), 4)], S.c("cash") - 0.3, 0.5)
    S.text("cash for surprises", 700, 260, 84, INK, at=S.c("surprises") - 0.3)
    S.draw(phone(330, 520, 0.8) + [stk(P_poly([(300, 420), (340, 480), (310, 540), (360, 600)]), 4, RED)], S.c("phone") - 0.3, 0.35)
    S.draw(car(1600, 470, 0.6), S.c("car") - 0.2, 0.35)
    S.draw(bill(1720, 720, 0.9), S.c("bill") - 0.2, 0.3)
    S.text("1 month", 380, 900, 110, INK, at=S.c("one", 1) - 0.1)
    S.add(arrow(P_line(800, 860, 1000, 860, 0.03, 1), S.c("build", 1), INK, 6, 0.3))
    S.text("3–6 months", 1060, 900, 110, ORANGE, at=S.c("three", 1) - 0.1)
    S.text("(or you sell at the worst moment)", 540, 1030, 56, GREY, at=S.c("worst", 1) - 0.4)


@V.scene("c3a")
def _(S):
    for k, (lab, ctry, w_) in enumerate((("PEA", "France", "pea"), ("ISA", "UK", "isa"), ("ISK", "Sweden", "isk"))):
        x = 360 + k * 300
        at = S.c(w_) - 0.2
        S.draw(jar(x, 430, 1.05, label=lab, fill_u=0.6, col=[HL, (150, 186, 214), (214, 226, 196)][k]), at, 0.35, snd="scr" if k == 0 else None)
        S.text(ctry, x, 650, 60, GREY, at=at + 0.2, anchor="m")
    S.text("tax advantages", 1240, 330, 80, ORANGE, at=S.c("tax") - 0.2, rot=-3)
    S.draw(plant(1160, 900, 0.9, leaves=2), S.c("same", 1) - 0.2, 0.4)
    S.draw(plant(1560, 900, 1.25, leaves=5), S.c("right", 1) - 0.2, 0.5)
    S.text("normal account", 1000, 1030, 50, GREY, at=S.c("same", 1))
    S.text("the right one", 1440, 1030, 50, ORANGE, at=S.c("right", 1))
    S.text("check your country.", 260, 920, 76, INK, at=S.c("check", 1) - 0.1)


@V.scene("c4a")
def _(S):
    S.draw(building(420, 560, 1.1, sign="BROKER"), S.c("broker") - 0.3, 0.5)
    S.text("regulated (EU / UK)", 180, 760, 70, INK, at=S.c("regulated") - 0.2)
    S.draw(shield(1000, 480, 1.0), S.c("compensation") - 0.4, 0.4)
    S.text("€20,000+", 1000, 500, 54, INK, at=S.c("€20,000") - 0.2, anchor="m")
    S.text("if it fails", 900, 700, 60, GREY, at=S.c("fails") - 0.1)
    items = (("order", "per order"), ("year", "per year"), ("currency", "currency exchange"))
    for k, (w_, lab) in enumerate(items):
        y = 320 + k * 110
        S.text("· " + lab, 1250, y, 64, INK, at=S.c(w_, 1) - 0.2)
    S.text("€10 on €1,000 = 1%", 1150, 820, 80, RED, at=S.c("€10", 1) - 0.2, rot=-3)


@V.scene("c5a")
def _(S):
    for k, x in enumerate((240, 420, 600)):
        S.draw([Fl(P_rect(x - 70, 300, 140, 140, 0, r=10), [HL, PINK, (150, 186, 214)][k]), stk(P_rect(x - 70, 300, 140, 140, 5, r=10), 5)],
               S.c("guessing") - 0.2 + 0.1 * k, 0.25, snd="scr" if k == 0 else None)
        S.text("?", x, 410, 90, INK, at=S.c("which") + 0.1 * k, anchor="m")
    S.add(arrow(P_bez((700, 370), (820, 330), (940, 370)), S.c("all") - 0.2, INK, 6, 0.3))
    bx, by = 1300, 380
    S.draw([stk(P_poly([(bx - 260, by - 120), (bx - 200, by + 140), (bx + 200, by + 140), (bx + 260, by - 120)], True), 7)], S.c("all") - 0.1, 0.4)
    import random as _r
    rr = _r.Random(4)
    for k in range(24):
        x = bx - 210 + (k % 6) * 84 + rr.uniform(-6, 6)
        y = by - 80 + (k // 6) * 54 + rr.uniform(-5, 5)
        S.pop([Fl(P_rect(x - 22, y - 20, 44, 40, 0, r=6), [HL, PINK, (150, 186, 214), (214, 226, 196), ORANGE][k % 5]), stk(P_rect(x - 22, y - 20, 44, 40, 3, r=6), 3.5)],
              S.c("etf") - 0.2 + 0.03 * k, (x, y), snd=None)
    S.text("1 global index ETF", 1060, 640, 76, ORANGE, at=S.c("etf") - 0.3)
    S.draw(globe(400, 820, 150), S.c("countries", 1) - 0.4, 0.5)
    S.text("1,000+ companies", 640, 790, 70, INK, at=S.c("thousand", 1) - 0.1)
    S.text("~0.2% a year", 660, 900, 70, INK, at=S.c("0.2%", 1) - 0.1)
    S.text("look for: UCITS", 1220, 900, 80, ORANGE, at=S.c("ucits", 1) - 0.2, rot=-2)


@V.scene("c6a")
def _(S):
    S.draw(calendar(440, 520, 1.1, day=None, head="EVERY MONTH"), S.c("monthly") - 0.3, 0.45)
    S.add(arrow(P_arc(440, 520, 260, 240, -160, 150, 50), S.c("plan") - 0.1, ORANGE, 7, 0.6))
    S.text("€50", 380, 640, 150, ORANGE, at=S.c("€50") - 0.1, cps=10)
    S.text("(sometimes free)", 280, 900, 60, GREY, at=S.c("free") - 0.2)
    S.text("a habit", 1080, 420, 120, INK, at=S.c("habit", 1) - 0.1)
    S.add(check(1500, 380, 40, S.c("habit", 1) + 0.4, GREEN, 11))
    S.text("a one-off bet", 1080, 640, 100, GREY, at=S.c("bet", 1) - 0.4)
    S.add(cross(1660, 610, 40, S.c("bet", 1) + 0.2, RED, 9))


@V.scene("c6b")
def _(S):
    S.add(*bars(420, 880, [7.6, 130], ["€1,000 alone", "+ €100 a month"], S.c("€1,000") + 0.2, step=S.c("add") - S.c("€1,000"),
                maxh=620, bw=260, gap=360, cols=[HL, ORANGE], txt=["€7.6k", "€130k"], seed=31, size=86))
    S.text("30 years · 7% a year (example)", 200, 200, 60, GREY, at=S.c("thirty") - 0.1)


@V.scene("c7a")
def _(S):
    x0, y0, x1, y1 = 220, 220, 1700, 880
    S.draw([stk(P_line(x0, y1, x1, y1, 0.005, 1), 6)], 0.0, 0.3, snd=None)
    rr = np.random.default_rng(9)
    n = 60
    v = np.concatenate([np.linspace(0, 0.5, 18) + rr.normal(0, 0.02, 18), np.linspace(0.5, -2.8, 8) + rr.normal(0, 0.05, 8),
                        np.linspace(-2.8, 0.55, 28) + rr.normal(0, 0.06, 28), np.linspace(0.55, 1.1, n - 54) + rr.normal(0, 0.04, n - 54)])
    pts = np.stack([x0 + 30 + np.arange(n) / (n - 1) * (x1 - x0 - 80), y1 - 120 - (v + 2.8) / 3.9 * (y1 - y0 - 160)], 1)
    S.draw([stk(pts[:27], 8, INK)], S.c("2020") - 0.2, 0.8)
    S.text("-34%", pts[25][0] - 40, pts[25][1] + 90, 90, RED, at=S.c("third") - 0.1)
    S.add(cross(pts[25][0], pts[25][1], 26, S.c("sold") + 0.1, RED, 8))
    S.text("sold here = loss locked in", pts[25][0] - 600, pts[25][1] + 30, 56, RED, at=S.c("locked") - 0.2)
    S.draw([stk(pts[26:], 9, ORANGE)], S.c("back", 1) - 0.3, 1.0)
    S.draw([stk(P_line(pts[17][0], pts[17][1], x1 - 40, pts[17][1], 0.005, 5), 4, GREY)], S.c("record", 1) - 0.2, 0.4, snd=None)
    S.text("record again ~5 months later", 1000, pts[17][1] - 50, 54, ORANGE, at=S.c("five", 1) - 0.1)
    S.text("S&P 500, 2020", 240, 990, 56, GREY, at=S.c("s&p", 1))


@V.scene("c7b")
def _(S):
    S.draw(phone(480, 560, 1.5), 0.0, 0.4)
    S.text("every day", 360, 300, 76, INK, at=S.c("check") - 0.1)
    S.add(cross(480, 560, 150, S.c("day") + 0.1, RED, 11))
    S.text("once a month: plenty", 1000, 480, 84, INK, at=S.c("month") - 0.3)
    S.text("once a year: better", 1000, 680, 100, ORANGE, at=S.c("year") - 0.3, rot=-2)


@V.scene("c8a")
def _(S):
    S.draw(book(420, 560, 1.4), S.c("book") - 0.3, 0.45)
    S.text("1 good book", 260, 900, 80, INK, at=S.c("book") - 0.1)
    S.text("watch the fees", 820, 300, 76, INK, at=S.c("fees") - 0.2)
    S.draw(bubble(1300, 560, 600, 200, tail=(1, 1)), S.c("promising") - 0.3, 0.3)
    S.text("guaranteed 30% a month!", 1300, 580, 50, INK, at=S.c("promising") - 0.1, anchor="m")
    S.add(cross(1300, 560, 120, S.c("returns") + 0.1, RED, 11))
    S.text("too good to be true?\nit usually is.", 980, 880, 84, ORANGE, at=S.c("true", 1) - 0.4, rot=-2)


@V.scene("f0")
def _(S):
    S.text("final message.", 260, 600, 120, INK, at=0.05, rot=-3, cps=20)
    S.add(under(270, 980, 640, 1.0, ORANGE, 7, 0.4, wavy=True))


@V.scene("f1")
def _(S):
    S.text("not a stock.", 220, 220, 90, GREY, at=S.c("stock") - 0.2)
    S.text("a system:", 220, 360, 110, ORANGE, at=S.c("system") - 0.1)
    items = (("debt", "no expensive debt"), ("cushion", "a cushion"), ("account", "the right account"), ("fund", "one cheap global fund"),
             ("automatic", "automatic deposits"))
    for k, (w_, lab) in enumerate(items):
        y = 500 + k * 110
        at = S.c(w_) - 0.25
        S.text(lab, 330, y, 76, INK, at=at)
        S.add(check(270, y - 28, 24, at + 0.4, GREEN, 8, seed=k))
    S.add(Fig(1560, 950, 1.2, at=0.0, poses=[("stand", 0), ("point_l", S.c("system"))], moods=[("smile", 0)], seed=3, flip=True))


@V.scene("f2")
def _(S):
    S.text("boring?", 360, 420, 150, GREY, at=S.c("boring") - 0.2, rot=-3)
    S.text("yes.", 560, 640, 180, ORANGE, at=S.c("yes") - 0.1, rot=-4)
    S.text("that's why it works.", 420, 860, 90, INK, at=S.c("works") - 0.5)
    S.add(Fig(1500, 950, 1.3, at=0.0, poses=[("cross", 0)], moods=[("smug", 0)], seed=3, flip=True))


@V.scene("end")
def _(S):
    S.text("not financial advice. rules differ by country.", 200, 200, 56, GREY, at=S.c("education") - 0.2)
    sx, sy = 520, 600
    S.draw([Fl(P_rect(sx - 220, sy - 70, 440, 140, 0, r=26), ORANGE), stk(P_rect(sx - 220, sy - 70, 440, 140, 8, r=26), 7)], S.c("subscribe") - 0.3, 0.4)
    S.text("subscribe", sx, sy + 26, 92, INK, at=S.c("subscribe") - 0.1, anchor="m")
    vx, vy = 1350, 560
    S.draw([stk(P_rect(vx - 330, vy - 190, 660, 380, 8, r=12), 7)], S.c("next") - 0.2, 0.45)
    S.text("next:", vx - 320, vy - 220, 70, GREY, at=S.c("next") - 0.1)
    S.text("compound interest,\nexplained simply.", vx, vy - 20, 76, INK, at=S.c("compound") - 0.1, anchor="m")
    S.add(Fig(820, 980, 0.95, at=0.0, poses=[("stand", 0), ("point_r", S.c("next") + 0.1)], moods=[("smile", 0), ("happy", S.c("subscribe"))], seed=3))


if __name__ == "__main__":
    V.main()
