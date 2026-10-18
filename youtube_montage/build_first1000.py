"""'How to Invest Your First €1,000 So Simply It Feels Illegal' (doodle style). Sources in the kit: Investor Compensation Schemes
Directive 97/9/EC (at least €20,000), S&P 500 2020 drawdown and recovery, UCITS. All growth figures hypothetical (7% a year)."""
import math
import random

import numpy as np

from doodle_video import *  # noqa: F401,F403

SAY = {"€1,000": "a thousand euros", "€1,000.": "a thousand euros", "20%": "twenty percent", "15": "fifteen", "PEA": "P E A", "ISA": "eye-suh",
       "ISK": "I S K", "UK": "U K", "EU": "E U", "€20,000": "twenty thousand euros", "€10": "ten euros", "1%": "one percent",
       "ETF": "E T F", "0.2%": "zero point two percent", "UCITS": "you-sits", "€50": "fifty euros", "7%": "seven percent",
       "€7,600": "seven thousand six hundred euros", "€100": "a hundred euros", "€125,000": "a hundred and twenty-five thousand euros",
       "€37,000": "thirty-seven thousand euros", "2020": "twenty twenty", "S&P": "S and P", "500": "five hundred",
       "2000": "two thousand", "2008": "two thousand and eight", "US": "U S"}
V = Video("first1000", say=SAY, seed=23, keys=dict(prog=[(52, 55, 59, 62), (48, 52, 55, 60), (53, 57, 60, 64), (55, 59, 62, 67)],
                                                   roots=[40, 36, 41, 43], bpm=82),
          hush=[("But your first", "It's about building")], tape="Final message", beat_groups=())
_speak = V.speak


def _say(sub):
    """'your first €1,000' is 'your first thousand euros', not 'your first a thousand euros'."""
    return _speak(sub).replace("first a thousand euros", "first thousand euros")


V.speak = _say
_autoframe = V.autoframe


def _frame_text_safe():
    """Local guard on top of the auto-framer: never zoom a page so far that a caption-free text lands in YouTube's caption band
    (below y 925) or past the side margins; back the zoom off toward 1 until every text fits."""
    _autoframe()
    for sc in V.SC:
        fs, fx, fy = sc.cam.frame

        def bad(s_):
            for tx in sc.texts:
                sz, w = tx["size"] * s_, tx["w"] * s_ * 1.08          # handwriting overhangs its measured width a little
                X, Y = fx + s_ * (tx["x"] - fx), fy + s_ * (tx["y"] - fy)
                xl = X - (w / 2 if tx["anchor"] == "m" else (w if tx["anchor"] == "r" else 0))
                if Y + sz * (tx["n"] - 1) * tx["lh"] + 0.28 * sz > 925 or xl < 110 or xl + w > W - 110:
                    return True
            return False
        while fs > 1.0 and bad(fs):
            fs = max(1.0, fs - 0.02)
        sc.cam.frame = (fs, fx, fy)


V.autoframe = _frame_text_safe
L = V.L

L("o1", "Everyone has a plan for your first €1,000. Most of them are wrong.")
L("o1", "Your bank offers a fund. A friend talks about crypto. Someone online has a secret strategy.")
L("o2", "So you do nothing. And inflation eats a little of it every year.")
L("o4", "But your first €1,000 isn't about getting rich.")
L("o4", "It's about building the habit that will.")
L("o5", "Eight steps, in order. One warning: you can lose money.")

L("c1", "One. Kill expensive debt first.")
L("c1a", "If you have a credit card or a loan at 15 or 20% a year, pay that off first.")
L("c1a", "Every euro you pay back is 20% you stop paying. No investment can promise that.")

L("c2", "Two. Keep a small safety cushion.")
L("c2a", "Before investing, keep some cash for surprises: a broken phone, a car repair, a big bill.")
L("c2a", "Start with one month of expenses, and build towards three to six. Otherwise, the first emergency forces you to sell at the worst moment.")
L("c2b", "And if €1,000 is all you have? Then that's your cushion. Keep it, and start with a small monthly plan instead.")

L("c3", "Three. Use the right account.")
L("c3a", "Many European countries have accounts with tax advantages. The PEA in France. The ISA in the UK. The ISK in Sweden.")
L("c3a", "The same investment, inside the right account, can leave you with noticeably more after tax. Check what your country offers.")

L("c4", "Four. Pick a regulated, low-cost broker.")
L("c4a", "Look for a broker authorised by a financial regulator. In the EU, if a broker fails and can't give your investments back, "
         "a compensation scheme steps in, usually up to €20,000 or more.")
L("c4a", "Then look at the fees: per order, per year, and for currency exchange. On €1,000, a €10 fee is already 1%.")

L("c5", "Five. Buy the whole market.")
L("c5a", "Instead of guessing which company will win, buy them all, with one global index ETF.")
L("c5a", "One fund can hold well over a thousand companies across dozens of countries, for around 0.2% a year or less. In Europe, look for UCITS in the name.")

L("c6", "Six. Automate it.")
L("c6a", "Many brokers let you set up a monthly savings plan, sometimes for free. Even €50 a month.")
L("c6a", "Your first €1,000 becomes the start of a habit, not a one-off bet.")
L("c6b", "€1,000 left alone for thirty years at 7% a year grows to about €7,600. Add €100 a month, and it's about €125,000.")
L("c6b", "About €37,000 of that is money you put in. And that's before fees, inflation and tax.")

L("c7", "Seven. Then don't touch it.")
L("c7a", "In early 2020, stock markets fell about a third in a few weeks. People who sold locked in the loss.")
L("c7a", "The S&P 500, the big US index, was back at its record about five months after the bottom.")
L("c7r", "It isn't always that fast. After 2000, US stocks needed about seven years to get back, then 2008 hit. Thirteen years in all. "
         "You can lose money.")
L("c7b", "Don't check it every day. Once a month is plenty. Once a year is better.")

L("c8", "Eight. Keep learning, slowly.")
L("c8a", "Read one good book. Watch the fees. Ignore anyone promising fast, guaranteed returns.")
L("c8a", "If it sounds too good to be true, it usually is.")

L("f0", "Final message.")
L("f1", "The best first investment isn't a stock. It's a system: no expensive debt, a cushion, the right account, one cheap global fund, and automatic deposits.")
L("f2", "Boring? Yes. That's exactly why it works.")
L("end", "This is education, not financial advice. Rules differ by country, so check yours. If this helped, subscribe. "
         "Next up: compound interest, explained simply.")


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


def building(x, y, s=1.0, sign="BANK", size=None):
    o = [Fl(P_rect(x - 160 * s, y - 220 * s, 320 * s, 260 * s, 0), (250, 248, 242)), stk(P_rect(x - 160 * s, y - 220 * s, 320 * s, 260 * s, 8 * s), 7 * s),
         stk(P_poly([(x - 190 * s, y - 220 * s), (x, y - 320 * s), (x + 190 * s, y - 220 * s)], True), 7 * s)]
    for k in range(4):
        cx = x - 120 * s + k * 80 * s
        o.append(stk(P_line(cx, y - 180 * s, cx, y + 20 * s, 0.01, k), 6 * s))
    o.append(("g", sign, x, y - 236 * s, size or int(46 * s), INK, HAND, "m"))
    return o


def shield(x, y, s=1.0, col=(214, 226, 196)):
    pts = np.vstack([P_line(x - 110 * s, y - 120 * s, x + 110 * s, y - 120 * s, 0.03, 1),
                     P_bez((x + 110 * s, y - 120 * s), (x + 110 * s, y + 40 * s), (x + 40 * s, y + 110 * s), (x, y + 140 * s)),
                     P_bez((x, y + 140 * s), (x - 40 * s, y + 110 * s), (x - 110 * s, y + 40 * s), (x - 110 * s, y - 120 * s))])
    return [Fl(pts, col), stk(pts, 7 * s)]


def bill(x, y, s=1.0):
    return [Fl(P_rect(x - 80 * s, y - 100 * s, 160 * s, 200 * s, 0), (250, 248, 242)), stk(P_rect(x - 80 * s, y - 100 * s, 160 * s, 200 * s, 6 * s), 5.5 * s),
            stk(P_line(x - 50 * s, y - 50 * s, x + 50 * s, y - 50 * s, 0.02, 1), 4 * s, GREY), stk(P_line(x - 50 * s, y - 10 * s, x + 30 * s, y - 10 * s, 0.02, 2), 4 * s, GREY),
            ("g", "€€€", x, y + 70 * s, 60, RED, HAND, "m")]


def cal(x, y, s=1.0, head="MONTHLY"):
    """doodle.calendar with a header big enough to read on a phone, and a highlighter header: orange is kept for one hero per frame."""
    ops = [(op[0], op[1], HL) if op[0] == "f" and op[2] == ORANGE else op for op in calendar(x, y, s, day=None, head=None)]
    return ops + [("g", head, x, y - 125 * s + 50 * s, 58, INK, HAND, "m")]


def hl(S, pre, word, x, y, size, at, rot=0.0, cps=24, col=ORANGE):
    """Headline in ink with ONE word in the hero colour, landing a beat after the rest (hit, hold, build)."""
    a = S.text(pre, x, y, size, INK, at=at, rot=rot, cps=cps)
    w, r = text_w(pre, size), math.radians(rot)
    return S.text(word, x + w * math.cos(r), y + w * math.sin(r), size, col, at=a.end + 0.25, rot=rot, cps=cps)


def grow_bar(x, ybase, w, h, col, at, seed=0, grow=0.6):
    """A bar that grows up from the baseline (same motion as doodle.bars)."""
    fp = Path(P_rect(x, ybase - h, w, h, 0), seed * 9, wob=0.8)
    op = Path(P_poly([(x, ybase), (x, ybase - h), (x + w, ybase - h), (x + w, ybase)]), seed * 9 + 50)
    rr = random.Random(seed)
    off = (rr.uniform(-5, 5), rr.uniform(-4, 4))

    def fn(ctx, t):
        if t < at:
            return
        u = ease_back(clamp((t - at) / grow), 1.1)
        b = boil(t)
        ctx.save()
        ctx.translate(0, ybase)
        ctx.scale(1, max(0.01, u))
        ctx.translate(0, -ybase)
        fill(ctx, fp, b, col, 1.0, off)
        stroke(ctx, op, b, 6.5, INK)
        ctx.restore()
    return fn


def dip_line(x0, y0, x1, y1, drop, low_at, seed=0):
    """A market line: a peak, a fall to `drop`, a long climb back to the old high."""
    rr = np.random.default_rng(seed)
    n = 40
    u = np.linspace(0, 1, n)
    v = np.where(u < low_at, -drop * np.sin(u / low_at * np.pi / 2), -drop * (1 - (u - low_at) / (1 - low_at)) ** 1.4)
    v = v + rr.normal(0, 0.035, n) * (u > 0.02) * (u < 0.98)
    return np.stack([x0 + u * (x1 - x0), y0 - v * (y1 - y0)], 1)


# --------------------------------------------------------------------------- cold open
@V.scene("o1")
def _(S):
    """Frame 0 already shows the conflict: you and your €1,000, pulled three ways."""
    S.add(Fig(900, 960, 1.3, at=-1.0, poses=[("hold", 0), ("shrug", S.c("plan"))], moods=[("worried", 0)], seed=3, enter="none"))
    tug = lambda tt: (10 * math.sin(tt * 8.5), 0, 0.035 * math.sin(tt * 6.1), 1.0)
    S.add(Dr(money_bag(920, 690, 0.65, label="€"), -1.0, 0.0, pop=True, anchor=(920, 760), move=tug, seed=8))
    S.text("€1,000", 760, 420, 120, ORANGE, at=-2.0)
    S.add(Dr(building(330, 640, 0.7, size=60), -1.0, 0.3, seed=11))
    S.add(Fig(1290, 990, 0.85, at=-1.0, poses=[("point_up", 0)], moods=[("grin", 0)], kind="spiky", seed=51, enter="none"))
    S.add(Dr(phone(1590, 560, 0.75) + [("g", "$$$", 1590, 590, 64, GREEN, HAND, "m")], -1.0, 0.3, seed=12))
    for k, pts in enumerate((P_line(500, 560, 790, 650, 0.04, 1), P_line(1220, 780, 1040, 720, 0.04, 2), P_line(1500, 540, 1050, 640, 0.04, 3))):
        S.add(arrow(pts, -1.0, INK, 6, 0.3, seed=k, dashed=True))
    w0 = S.c("wrong")
    S.text("?", 640, 600, 90, INK, at=w0 - 0.1, anchor="m")
    S.add(cross(1130, 750, 34, w0 + 0.25, RED, 9, seed=1))
    S.add(cross(1300, 590, 34, w0 + 0.55, RED, 9, seed=2))
    S.draw(bubble(380, 260, 330, 120, tail=(-1, 1)), S.c("fund", 1) - 0.3, 0.3, snd=None)
    S.text("our fund!", 380, 282, 64, INK, at=S.c("fund", 1) - 0.1, anchor="m")
    S.draw(bubble(1330, 420, 300, 120, tail=(-1, 1)), S.c("crypto", 1) - 0.3, 0.3, snd=None)
    S.text("crypto!!", 1330, 442, 64, INK, at=S.c("crypto", 1) - 0.1, anchor="m")
    S.text("secret strategy", 1560, 800, 56, RED, at=S.c("secret", 1) - 0.1, anchor="m", rot=-3)


@V.scene("o2")
def _(S):
    S.add(Fig(520, 940, 1.3, at=0.0, poses=[("shrug", 0), ("sad", S.c("nothing"))], moods=[("flat", 0), ("worried", S.c("eats"))], seed=3))
    bx, by = 1200, 600

    def shrink(tt, t0=S.c("eats")):
        u = clamp((tt - t0) / 2.2)
        return (0, 0, 0, 1.0 - 0.3 * ease_io(u))
    S.add(Dr(money_bag(bx, by, 1.4), 0.0, 0.0, pop=True, anchor=(bx, by + 110), move=shrink, seed=8))
    S.text("€1,000", 1060, 300, 90, ORANGE, at=0.1)
    S.text("inflation", 1390, 420, 90, RED, at=S.c("inflation") - 0.1, rot=-3)
    S.text("a little less, every year", 960, 860, 70, INK, at=S.c("little") + 0.1)


@V.scene("o4")
def _(S):
    S.text("your first €1,000", 240, 300, 110, INK, at=S.l(0) + 0.02, cps=28)
    S.pop(money_bag(1480, 330, 0.85, label="€"), S.l(0) + 0.05, (1480, 400))
    S.text("getting rich", 300, 520, 130, INK, at=S.c("getting") - 0.1)
    S.add(strike(280, 480, 300 + text_w("getting rich", 130) + 20, 472, S.c("rich") + 0.3, RED, 10))
    hl(S, "the ", "habit.", 380, 800, 200, S.c("the", 1) - 0.1, rot=-4, cps=16)
    S.draw(cal(1500, 720, 0.9), S.c("building", 1) - 0.2, 0.4)
    for k in range(6):
        S.add(check(1410 + (k % 3) * 90, 750 + (k // 3) * 80, 20, S.c("will", 1) + 0.1 * k, GREEN, 7, seed=k))


@V.scene("o5")
def _(S):
    S.text("8", 320, 560, 380, ORANGE, at=S.l(0) + 0.02, anchor="m", rot=-6, cps=10)
    S.text("steps", 470, 470, 130, INK, at=S.c("steps") - 0.2)
    S.text("in order.", 500, 620, 90, INK, at=S.c("order") - 0.2)
    S.draw([stk(P_poly([(960, 400), (1040, 260), (1120, 400)], True), 8, RED)], S.c("warning") - 0.3, 0.3)
    S.text("!", 1040, 385, 100, RED, at=S.c("warning") - 0.1, anchor="m")
    S.text("you can lose money.", 840, 540, 84, RED, at=S.c("lose") - 0.4)
    S.text("education, not advice.", 840, 660, 72, INK, at=S.c("lose") + 0.3, cps=40)
    S.add(Fig(1560, 960, 1.1, at=0.0, poses=[("stand", 0), ("point_l", S.c("warning"))], moods=[("smile", 0), ("worried", S.c("warning"))],
              seed=3, flip=True))


V.chapters({1: ("Kill expensive\ndebt first.", 0), 2: ("Keep a small\nsafety cushion.", 1), 3: ("Use the right\naccount.", 0),
            4: ("Pick a regulated,\nlow-cost broker.", 1), 5: ("Buy the whole\nmarket.", 0), 6: ("Automate it.", 1),
            7: ("Then don't\ntouch it.", 0), 8: ("Keep learning,\nslowly.", 1)}, peek=set())


# --------------------------------------------------------------------------- steps
@V.scene("c1a")
def _(S):
    S.draw(card(500, 440, 1.5), S.l(0) + 0.05, 0.45)
    S.pop(tag(820, 650, 1.1, "20%/yr", (244, 214, 210), 64), S.c("20%") - 0.1, (820, 650))
    S.add(cross(500, 440, 180, S.c("off") + 0.05, RED, 12))
    hl(S, "pay it off ", "first.", 220, 840, 100, S.c("pay") - 0.1, rot=-2)
    S.text("= 20% you", 1050, 360, 96, INK, at=S.c("stop", 1) - 0.6, rot=-3)
    S.text("stop paying", 1070, 480, 96, INK, at=S.c("stop", 1) - 0.1, rot=-3)
    S.text("no investment\ncan promise that.", 1000, 660, 70, INK, at=S.c("promise", 1) - 0.4)


@V.scene("c2a")
def _(S):
    cx, cy = 960, 470
    pil = np.vstack([P_bez((cx - 220, cy - 80), (cx, cy - 150), (cx + 220, cy - 80)), P_bez((cx + 220, cy - 80), (cx + 270, cy), (cx + 220, cy + 80)),
                     P_bez((cx + 220, cy + 80), (cx, cy + 150), (cx - 220, cy + 80)), P_bez((cx - 220, cy + 80), (cx - 270, cy), (cx - 220, cy - 80))])
    S.draw([Fl(pil, (150, 186, 214)), stk(pil, 7), stk(P_bez((cx - 230, cy - 90), (cx - 270, cy - 120), (cx - 250, cy - 70)), 5),
            stk(P_bez((cx + 230, cy + 90), (cx + 270, cy + 120), (cx + 250, cy + 70)), 5), ("g", "cash", cx, cy + 25, 80, INK, HAND, "m")],
           S.l(0) + 0.05, 0.5)
    S.text("cash for surprises", 640, 230, 84, INK, at=S.c("surprises") - 0.4)
    S.draw(phone(320, 470, 0.75) + [stk(P_poly([(290, 380), (330, 440), (300, 500), (350, 560)]), 4, RED)], S.c("phone") - 0.3, 0.35)
    S.draw(car(1560, 420, 0.6), S.c("car") - 0.2, 0.35)
    S.draw(bill(1640, 620, 0.8), S.c("bill") - 0.2, 0.3)
    S.text("1 month", 300, 760, 110, INK, at=S.c("one", 1) - 0.1)
    S.add(arrow(P_line(720, 730, 920, 730, 0.03, 1), S.c("build", 1), INK, 6, 0.3))
    S.text("3–6 months", 980, 760, 110, ORANGE, at=S.c("three", 1) - 0.1)
    S.text("or you sell at the worst moment", 380, 890, 68, RED, at=S.c("forces", 1) - 0.2)


@V.scene("c2b")
def _(S):
    cx, cy = 560, 660
    pil = np.vstack([P_bez((cx - 260, cy - 70), (cx, cy - 130), (cx + 260, cy - 70)), P_bez((cx + 260, cy - 70), (cx + 310, cy), (cx + 260, cy + 70)),
                     P_bez((cx + 260, cy + 70), (cx, cy + 130), (cx - 260, cy + 70)), P_bez((cx - 260, cy + 70), (cx - 310, cy), (cx - 260, cy - 70))])
    S.draw([Fl(pil, (150, 186, 214)), stk(pil, 7)], S.l(0) + 0.02, 0.3)
    S.pop(money_bag(560, 470, 0.9, label="€"), S.l(0) + 0.1, (560, 560))
    S.text("all you have?", 180, 230, 96, INK, at=S.l(0) + 0.2, cps=48)
    hl(S, "= your ", "cushion.", 300, 880, 90, S.c("your") - 0.1, rot=-2)
    S.text("keep it.", 1060, 380, 96, INK, at=S.c("keep") - 0.1)
    S.draw(cal(1480, 560, 0.9), S.c("monthly") - 0.4, 0.4)
    S.add(arrow(P_bez((900, 560), (1080, 640), (1300, 600)), S.c("start") - 0.1, INK, 6, 0.4))
    S.text("small monthly plan", 1140, 820, 76, INK, at=S.c("plan") - 0.3)


@V.scene("c3a")
def _(S):
    for k, (lab, ctry, w_) in enumerate((("PEA", "France", "pea"), ("ISA", "UK", "isa"), ("ISK", "Sweden", "isk"))):
        x, sj = 330 + k * 300, 1.1
        at = S.c(w_) - 0.2
        S.draw(jar(x, 430, sj), S.l(0) + 0.05 + 0.15 * k, 0.35, snd="scr" if k == 0 else None)
        fh = 180 * sj * 0.85 * 0.6
        S.pop([Fl(P_rect(x - 70 * sj + 8 * sj, 430 + 90 * sj - fh - 6 * sj, 140 * sj - 16 * sj, fh, 0, r=10 * sj), [HL, (150, 186, 214), (214, 226, 196)][k])],
              at, (x, 470), snd=None)
        S.text(lab, x, 450, 76, INK, at=at + 0.15, anchor="m")
        S.text(ctry, x, 650, 66, INK, at=at + 0.25, anchor="m")
    S.text("tax advantages", 1140, 290, 84, INK, at=S.l(0) + 0.1, rot=-3)
    S.draw(plant(1090, 780, 0.9, leaves=2), S.c("same", 1) - 0.2, 0.4)
    S.draw(plant(1540, 780, 1.25, leaves=5), S.c("right", 1) - 0.2, 0.5)
    S.text("normal account", 1090, 880, 62, INK, at=S.c("same", 1), anchor="m")
    S.text("the right one", 1540, 880, 62, ORANGE, at=S.c("right", 1), anchor="m")
    S.text("check your country.", 230, 840, 84, INK, at=S.c("check", 1) - 0.1)


@V.scene("c4a")
def _(S):
    S.draw(building(380, 620, 1.1, sign="BROKER", size=60), S.l(0) + 0.05, 0.5)
    S.text("authorised by a financial regulator", 140, 190, 70, INK, at=S.l(0) + 0.3)
    S.draw(shield(980, 440, 0.9), S.c("compensation") - 0.4, 0.4)
    S.text("€20,000+", 980, 670, 88, INK, at=S.c("€20,000") - 0.4, anchor="m")
    S.text("if the broker fails", 980, 760, 62, INK, at=S.c("fails") - 0.1, anchor="m")
    items = (("order", "· per order"), ("year", "· per year"), ("currency", "· currency"))
    for k, (w_, lab) in enumerate(items):
        S.text(lab, 1340, 330 + k * 105, 68, INK, at=S.c(w_, 1) - 0.2)
    S.text("€10 on €1,000 = 1%", 1060, 860, 76, RED, at=S.c("€10", 1) - 0.3, rot=-3)


@V.scene("c5a")
def _(S):
    gone = S.l(1) - 0.2
    for k, x in enumerate((240, 420, 600)):
        S.draw([Fl(P_rect(x - 70, 300, 140, 140, 0, r=10), [HL, PINK, (150, 186, 214)][k]), stk(P_rect(x - 70, 300, 140, 140, 5, r=10), 5)],
               S.l(0) + 0.05 + 0.12 * k, 0.25, snd="scr" if k == 0 else None, until=gone)
        S.add(T("?", x, 410, 90, INK, at=S.c("which") + 0.1 * k, anchor="m", until=gone))
    S.draw([stk(p_, 6) for p_ in arrow_pts(P_bez((700, 370), (840, 330), (980, 370)))], S.c("all") - 0.3, 0.3, snd=None, until=gone)
    S.draw([stk(P_poly([(1040, 260), (1100, 700), (1700, 700), (1760, 260)], True), 9)], S.c("all") - 0.1, 0.4)
    import random as _r
    rr = _r.Random(4)
    for k in range(40):
        x = 1120 + (k % 8) * 80 + rr.uniform(-6, 6)
        y = 320 + (k // 8) * 80 + rr.uniform(-6, 6)
        S.pop([Fl(P_rect(x - 30, y - 28, 60, 56, 0, r=8), [HL, PINK, (150, 186, 214), (214, 226, 196), ORANGE][k % 5]), stk(P_rect(x - 30, y - 28, 60, 56, 4, r=8), 4.5)],
              S.c("all") + 0.3 + 0.025 * k, (x, y), snd=None)
    hl(S, "buy ", "everything.", 160, 700, 130, S.c("buy") - 0.1, rot=-4)
    S.text("1 global index ETF", 1090, 800, 76, INK, at=S.c("etf") - 0.4)
    S.draw(globe(250, 420, 115), S.c("countries", 1) - 0.4, 0.5)
    S.text("1,000+ companies", 400, 390, 64, INK, at=S.c("thousand", 1) - 0.1)
    S.text("~0.2% a year", 400, 480, 64, INK, at=S.c("0.2%", 1) - 0.1)
    S.text("look for: UCITS", 1090, 890, 76, INK, at=S.c("ucits", 1) - 0.3)


@V.scene("c6a")
def _(S):
    S.draw(cal(400, 450, 1.2), S.l(0) + 0.05, 0.45)
    S.add(arrow(P_arc(400, 450, 270, 250, -160, 150, 50), S.c("plan") - 0.1, INK, 7, 0.6))
    hl(S, "", "€50", 160, 820, 110, S.c("€50") - 0.1, cps=14)
    S.text("a month", 160 + text_w("€50 ", 110), 820, 110, INK, at=S.c("month") - 0.1)
    S.text("sometimes free", 200, 900, 62, INK, at=S.c("free") - 0.2)
    S.text("monthly savings plan", 900, 190, 84, INK, at=S.l(0) + 0.25)
    S.text("a habit", 1060, 420, 120, INK, at=S.c("habit", 1) - 0.1)
    S.add(check(1480, 380, 40, S.c("habit", 1) + 0.4, GREEN, 11))
    S.text("a one-off bet", 1060, 650, 100, INK, at=S.c("one-off", 1) - 0.2)
    S.add(cross(1650, 620, 40, S.c("bet", 1), RED, 9))


@V.scene("c6b")
def _(S):
    yb, mh, bw = 800, 560, 260
    hs = [mh * 7.6 / 124.6, mh]
    t1, t2 = S.c("€1,000") + 0.1, S.c("add") - 0.1
    S.draw([stk(P_line(360, yb, 1360, yb, 0.01, 2), 7)], S.l(0) + 0.02, 0.3, snd=None)
    S.text("example: 7% a year, 30 years", 130, 160, 66, INK, at=S.l(0) + 0.05)
    S.text("not guaranteed.", 130, 250, 66, INK, at=S.c("7%") + 0.2)
    S.pop(money_bag(270, 700, 0.7, label="€"), S.l(0) + 0.1, (270, 770))
    S.add(grow_bar(520, yb, bw, hs[0], HL, t1, seed=31))
    S.text("€7.6k", 650, yb - hs[0] - 30, 92, INK, at=S.c("€7,600") - 0.3, anchor="m")
    S.text("€1,000 alone", 650, yb + 80, 62, INK, at=t1, anchor="m")
    S.add(grow_bar(1000, yb, bw, hs[1], ORANGE, t2, seed=32))
    S.text("€125k", 1130, yb - hs[1] - 30, 92, INK, at=S.c("€125,000") - 0.3, anchor="m")
    S.text("+ €100 a month", 1130, yb + 80, 62, INK, at=t2, anchor="m")
    dep = mh * 37 / 124.6
    S.add(grow_bar(1000, yb, bw, dep, PALE, S.c("€37,000", 1) - 0.2, seed=33, grow=0.4))
    S.add(arrow(P_line(1420, yb - dep / 2 - 40, 1280, yb - dep / 2, 0.03, 4), S.c("€37,000", 1), INK, 6, 0.3))
    S.text("you put in\n€37k", 1440, yb - dep / 2 - 50, 70, INK, at=S.c("€37,000", 1) + 0.1)
    S.text("before fees,\ninflation, tax", 130, 370, 66, RED, at=S.c("before", 1) - 0.2)


@V.scene("c7a")
def _(S):
    x0, y0, x1, y1 = 220, 260, 1700, 880
    S.draw([stk(P_line(x0, y1, x1, y1, 0.005, 1), 6)], S.l(0) + 0.02, 0.3, snd=None)
    S.text("US stocks · S&P 500 · 2020", 200, 180, 72, INK, at=S.l(0) + 0.05)
    rr = np.random.default_rng(9)
    n = 60
    v = np.concatenate([np.linspace(0, 0.5, 18) + rr.normal(0, 0.02, 18), np.linspace(0.5, -2.8, 8) + rr.normal(0, 0.05, 8),
                        np.linspace(-2.8, 0.55, 28) + rr.normal(0, 0.06, 28), np.linspace(0.55, 1.1, n - 54) + rr.normal(0, 0.04, n - 54)])
    pts = np.stack([x0 + 30 + np.arange(n) / (n - 1) * (x1 - x0 - 80), y1 - 120 - (v + 2.8) / 3.9 * (y1 - y0 - 160)], 1)
    S.draw([stk(pts[:27], 9, INK)], S.l(0) + 0.15, 1.1)
    S.text("-34%", pts[25][0] + 30, pts[25][1] + 95, 92, RED, at=S.c("third") - 0.1)
    S.add(cross(pts[25][0], pts[25][1], 26, S.c("sold") + 0.1, RED, 8))
    S.text("sold here =\nloss locked in", pts[25][0] - 70, pts[25][1] - 60, 64, RED, at=S.c("locked") - 0.3, anchor="r")
    S.draw([stk(pts[26:], 9, ORANGE)], S.c("back", 1) - 0.3, 1.0)
    S.draw([stk(P_line(pts[17][0], pts[17][1], x1 - 40, pts[17][1], 0.005, 5), 4, GREY)], S.c("record", 1) - 0.2, 0.4, snd=None)
    S.text("record again ~5 months later", 560, pts[17][1] - 40, 66, INK, at=S.c("five", 1) - 0.4)


@V.scene("c7r")
def _(S):
    """S&P 500 price index: Mar 2000 peak, -49% by Oct 2002, back in May 2007, -57% by Mar 2009, above the 2000 peak for good in Mar 2013."""
    yx = lambda yr: 200 + (yr - 2000.2) / 13.4 * 1480
    yv = lambda v: 400 - v * 470
    key = [(2000.2, 0.0), (2001.0, -0.2), (2001.7, -0.3), (2002.8, -0.49), (2003.6, -0.32), (2005.0, -0.2), (2006.3, -0.1), (2007.4, 0.0),
           (2007.8, 0.03), (2008.4, -0.15), (2008.9, -0.45), (2009.2, -0.56), (2010.0, -0.3), (2011.3, -0.15), (2012.4, -0.1), (2013.2, 0.0), (2013.6, 0.06)]
    rr = np.random.default_rng(5)
    yrs = np.linspace(2000.2, 2013.6, 90)
    vals = np.interp(yrs, [k[0] for k in key], [k[1] for k in key]) + rr.normal(0, 0.012, 90) * (yrs > 2000.3) * (yrs < 2013.5)
    pts = np.stack([[yx(y) for y in yrs], [yv(v) for v in vals]], 1)
    cut = int(np.searchsorted(yrs, 2007.6))
    head = S.text("not always this fast.", 150, 190, 96, INK, at=S.l(0) + 0.02, until=S.c("lose") - 0.3)
    S.text("you can lose money.", 150, 190, 96, RED, at=S.c("lose") - 0.2)
    S.draw([stk(P_line(yx(2000.2), yv(0), yx(2013.6) + 20, yv(0), 0.005, 1), 4, GREY)], S.l(0) + 0.0, 0.3, snd=None)
    area = np.vstack([pts[:cut + 1], [[pts[cut][0], yv(0)], [pts[0][0], yv(0)]]])
    S.draw([Fl(area, PINK), stk(pts[:cut + 1], 8, INK)], S.l(0) + 0.05, 1.0, fill_delay=0.2)
    S.text("-49%", yx(2002.8) - 60, yv(-0.49) + 80, 66, RED, at=S.c("needed") - 0.1)
    S.add(arrow(P_line(yx(2000.3), yv(0) - 45, yx(2007.3), yv(0) - 45, 0.01, 3), S.c("seven") - 0.2, INK, 6, 0.4))
    S.text("~7 years", yx(2003.2), yv(0) - 70, 70, INK, at=S.c("seven") + 0.1)
    area2 = np.vstack([pts[cut:], [[pts[-1][0], yv(0)], [pts[cut][0], yv(0)]]])
    S.draw([Fl(area2, PINK), stk(pts[cut:], 8, RED)], S.c("2008") - 0.4, 1.1)
    S.text("then 2008: -57%", yx(2009.2) - 150, yv(-0.56) + 80, 66, RED, at=S.c("2008") + 0.4)
    S.add(arrow(P_line(yx(2000.3), 820, yx(2013.1), 820, 0.01, 4), S.c("thirteen") - 0.3, INK, 6, 0.5))
    S.text("13 years", yx(2005.6), 900, 80, ORANGE, at=S.c("thirteen") - 0.1)


@V.scene("c7b")
def _(S):
    S.draw(phone(480, 540, 1.5, col=(190, 214, 230)) + [stk(P_poly([(400, 640), (440, 560), (470, 610), (510, 480), (540, 560), (570, 450)]), 6, RED)], 0.0, 0.4)
    S.text("every day", 360, 280, 80, INK, at=S.l(0) + 0.15)
    S.add(cross(480, 540, 150, S.c("day") + 0.1, RED, 11))
    S.text("once a month: plenty", 900, 470, 88, INK, at=S.c("month") - 0.3)
    hl(S, "once a year: ", "better", 900, 670, 100, S.c("year") - 0.4, rot=-2)


@V.scene("c8a")
def _(S):
    S.draw(book(400, 520, 1.3), S.l(0) + 0.05, 0.45)
    S.text("1 good book", 250, 860, 80, INK, at=S.c("book") - 0.1)
    S.text("watch the fees", 820, 250, 80, INK, at=S.c("fees") - 0.2)
    S.draw(bubble(1260, 500, 760, 190, tail=(1, 1)), S.c("promising") - 0.4, 0.3)
    S.text("guaranteed 30% a month!", 1260, 522, 66, INK, at=S.c("promising") - 0.2, anchor="m")
    S.add(cross(1600, 400, 55, S.c("returns") + 0.1, RED, 11))
    S.text("too good to be true?", 880, 760, 84, INK, at=S.c("good", 1) - 0.4, rot=-2)
    S.text("it usually is.", 880, 860, 84, ORANGE, at=S.c("usually", 1) - 0.3, rot=-2)


@V.scene("f0")
def _(S):
    S.text("final message.", 260, 600, 150, INK, at=0.02, rot=-3, cps=28)
    S.add(under(270, 1140, 650, 0.6, ORANGE, 8, 0.4, wavy=True))


@V.scene("f1")
def _(S):
    S.text("not a stock.", 200, 200, 110, INK, at=S.l(0) + 0.02)
    S.draw([Fl(P_rect(880, 70, 300, 170, 0, r=14), PINK), stk(P_rect(880, 70, 300, 170, 6, r=14), 6),
            stk(P_poly([(910, 210), (970, 140), (1020, 180), (1090, 100), (1150, 120)]), 7, INK)], S.l(0) + 0.2, 0.4)
    S.add(cross(1030, 155, 80, S.c("stock") + 0.1, RED, 9))
    S.text("a system:", 200, 330, 110, ORANGE, at=S.c("system") - 0.1)
    items = (("debt", "no expensive debt"), ("cushion", "a cushion"), ("account", "the right account"), ("fund", "one cheap global fund"),
             ("automatic", "automatic deposits"))
    for k, (w_, lab) in enumerate(items):
        y = 460 + k * 100
        at = S.c(w_) - 0.25
        S.text(lab, 310, y, 76, INK, at=at)
        S.add(check(250, y - 28, 24, at + 0.4, GREEN, 8, seed=k))
    S.add(Fig(1560, 950, 1.2, at=0.0, poses=[("stand", 0), ("point_l", S.c("system"))], moods=[("smile", 0)], seed=3, flip=True))


@V.scene("f2")
def _(S):
    S.text("boring?", 360, 400, 150, INK, at=S.l(0) + 0.0, rot=-3)
    S.text("yes.", 560, 620, 180, ORANGE, at=S.c("yes") - 0.1, rot=-4)
    S.text("that's why it works.", 420, 840, 90, INK, at=S.c("works") - 0.5)
    S.add(Fig(1500, 950, 1.3, at=0.0, poses=[("cross", 0)], moods=[("smug", 0)], seed=3, flip=True))


@V.scene("end")
def _(S):
    endcard(S, "compound interest,\nexplained simply.", note="education, not financial advice.\nrules differ by country.")


if __name__ == "__main__":
    V.main()
