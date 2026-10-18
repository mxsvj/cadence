"""'Compound Interest Explained So Simply It Feels Illegal' (doodle style). Numbers: 7% a year, monthly compounding for monthly
deposits; all examples hypothetical. Sources in the kit (UBS/Cambridge yearbook, ECB target, Quote Investigator)."""
import math

import numpy as np

from doodle_video import *  # noqa: F401,F403

SAY = {"€10,000": "ten thousand euros", "€76,000": "seventy-six thousand euros", "€100": "a hundred euros", "€110": "a hundred and ten euros",
       "€20,000": "twenty thousand", "€40,000": "forty thousand", "€80,000": "eighty thousand", "€200": "two hundred euros",
       "€72,000": "seventy-two thousand euros", "€244,000": "two hundred and forty-four thousand euros", "€24,000": "twenty-four thousand euros",
       "€525,000": "five hundred and twenty-five thousand euros", "€35,000": "thirty-five thousand euros", "€11,000": "eleven thousand euros",
       "€235,000": "two hundred and thirty-five thousand euros", "€173,000": "a hundred and seventy-three thousand euros",
       "€60,000": "sixty thousand euros", "€62,000": "sixty-two thousand euros", "€39,000": "thirty-nine thousand",
       "€42,000": "forty-two thousand euros", "€400": "four hundred euros",
       "€488,000": "four hundred and eighty-eight thousand euros", "45%": "forty-five percent", "7%": "seven percent", "10%": "ten percent", "20%": "twenty percent", "1.8%": "one point eight percent",
       "0.2%": "zero point two percent", "2%": "two percent", "5%": "five percent", "72": "seventy-two", "7": "seven", "10": "ten",
       "25": "twenty-five", "35": "thirty-five", "65": "sixty-five", "11": "eleven", "30": "thirty", "125": "a hundred and twenty-five"}
V = Video("compound", say=SAY, seed=7, keys=dict(prog=[(57, 60, 64, 67), (53, 57, 60, 64), (48, 52, 55, 59), (55, 59, 62, 65)],
                                                 roots=[45, 41, 36, 43], bpm=76),
          tape="Final message")
L = V.L

L("o1", "Leave €10,000 alone for 30 years, and it turns into about €76,000.")
L("o1", "At 7% a year, you don't add a single euro. The money does the work.")
L("o5", "That's compound interest. Slow, then boring, then suddenly unbelievable. Most people quit during the boring part.")
L("o6", "Seven ideas. No formulas. So simple, it feels illegal.")

L("c1", "One. Interest on interest.")
L("c1a", "Say you have €100, and it grows 10% a year.")
L("c1a", "After one year, you have €110.")
L("c1b", "Next year, you don't earn 10% on €100. You earn it on €110.")
L("c1b", "Your interest starts earning its own interest.")
L("c1c", "It's a snowball. Small at the top of the hill. Huge at the bottom.")
L("c1c", "Same snow, same slope. The only thing that changed is time.")

L("c2", "Two. The rule of 72.")
L("c2a", "Want to know how fast your money doubles? Divide 72 by the yearly return.")
L("c2a", "At 7% a year, 72 divided by 7 is about 10. Your money doubles roughly every ten years.")
L("c2b", "So €10,000 becomes about €20,000, then €39,000, then €76,000, the number from the start.")
L("c2b", "Each doubling is bigger than all the ones before it.")

L("c3", "Three. Time beats money.")
L("c3a", "Meet Anna and Ben. Both invest €200 a month, at 7% a year.")
L("c3a", "Anna starts at 25. Ben starts at 35. Both stop at 65.")
L("c3b", "Ben puts in €72,000. He ends with about €244,000.")
L("c3b", "Anna puts in only €24,000 more. She ends with about €525,000.")
L("c3b", "Even if Ben doubles it to €400 a month, he ends with about €488,000. Still less than Anna.")
L("c3c", "Anna ends with more than twice as much as Ben. Starting early beats starting big.")

L("c4", "Four. The boring years.")
L("c4a", "Here's why most people give up. After ten years of €200 a month, Anna has about €35,000.")
L("c4a", "Only about €11,000 of that is growth. It feels like nothing is happening.")
L("c4b", "But around year 11, something flips. One year of growth beats everything she puts in that year.")
L("c4b", "After that, the curve bends upward. The boring part was the foundation.")

L("c5", "Five. It works against you too.")
L("c5a", "Compound interest doesn't care which side you're on.")
L("c5a", "Store credit and credit cards can charge 20% a year.")
L("c5b", "At 20%, a debt doubles in less than four years. That's the rule of 72, working for the bank.")
L("c5b", "So before you invest, pay off expensive debt. It's the best return you'll ever get.")

L("c6", "Six. Fees compound too.")
L("c6a", "A fee of 1.8% a year sounds tiny. It isn't.")
L("c6x", "€200 a month for 30 years: with fees of 0.2%, about €235,000. With 1.8%, about €173,000.")
L("c6b", "Same money in. About €62,000 less out. The fee compounds against you, every single year.")

L("c7", "Seven. Inflation is compounding in reverse.")
L("c7a", "Prices rise a little every year. The European Central Bank aims for 2%.")
L("c7a", "At 2% inflation, cash loses about 45% of its buying power in 30 years.")
L("c7x", "The same goes for every number in this video. In today's money, that €76,000 from the start is worth about €42,000. "
         "Still four times what went in.")
L("c7b", "That's why long-term money can't just sit still. Over the last 125 years, global stocks grew about 5% a year faster than inflation, on average.")
L("c7b", "Not every year. Some years were terrible. But over decades, time did the heavy lifting.")

L("f0", "Final message.")
L("f1", "Compound interest isn't magic. It's just patience, written in maths.")
L("f2", "Start early. Start small if you have to. Keep fees low. Kill expensive debt.")
L("f3", "And then, the hardest part: do nothing, for a very long time.")
L("end", "This is education, not financial advice. The numbers here are examples, not promises. If this helped, subscribe. "
         "Next up: how to save money so easily it feels illegal.")


PUTIN = (204, 196, 181)        # "money you put in": a quiet neutral, a shade darker than the paper
BLUE = (150, 186, 214)


def fv(m, years, rate=0.07):
    i = rate / 12
    return m * ((1 + i) ** (years * 12) - 1) / i


def axes(S, x0, y0, x1, y1, at, xl=None, yl=None):
    S.draw([stk(P_line(x0, y1, x1, y1, 0.005, 1), 6), stk(P_line(x0, y1, x0 + 2, y0, 0.005, 2), 6)], at, 0.35, snd=None)
    if xl:
        S.text(xl, x1 - 10, y1 - 26, 70, GREY, at=at + 0.2, anchor="r")
    if yl:
        S.text(yl, x0 + 24, y0 + 40, 70, GREY, at=at + 0.2)


def curve_pts(x0, y0, x1, y1, fn, n=70):
    xs = np.linspace(0, 1, n)
    ys = np.array([fn(u) for u in xs])
    ys = (ys - ys.min()) / (ys.max() - ys.min() + 1e-9)
    return np.stack([x0 + xs * (x1 - x0), y1 - ys * (y1 - y0)], 1)


def stacked(S, x, base, w, parts, at, scale, cols, labels=None, step=0.5, label_size=62):
    """A bar made of stacked parts (e.g. money put in, then growth), each growing on its own cue."""
    y = base
    for k, (v, col) in enumerate(zip(parts, cols)):
        h = v * scale
        t0 = at + k * step

        def mk(y=y, h=h, t0=t0, col=col, k=k):
            fp = Path(P_rect(x, y - h, w, h, 0), 300 + k, wob=0.8)
            op = Path(P_rect(x, y - h, w, h, 6), 400 + k)

            def fn(ctx, t):
                if t < t0:
                    return
                u = ease_back(clamp((t - t0) / 0.5), 1.1)
                b = boil(t)
                ctx.save()
                ctx.translate(0, y)
                ctx.scale(1, max(0.01, u))
                ctx.translate(0, -y)
                fill(ctx, fp, b, col, 1.0, (3, -2))
                stroke(ctx, op, b, 6, INK)
                ctx.restore()
            return fn
        S.add(mk())
        if labels and labels[k]:
            S.text(labels[k], x + w + 30, y - h / 2 + 22, label_size, INK, at=t0 + 0.3)
        y -= h


def stock_path(years=125, end=565.0, seed=4):
    """Illustrative real (after-inflation) index: about +5% a year on average, with the big crashes in roughly the right places.
    Linear scale, so the early decades hug the baseline and the late crashes are visible dips that never reach zero."""
    rr = np.random.default_rng(seed)
    r = rr.normal(0.0, 0.11, years)
    for yr, hit in ((14, -0.25), (15, -0.2), (29, -0.3), (30, -0.3), (31, -0.25), (73, -0.3), (74, -0.3), (100, -0.15), (101, -0.15),
                    (102, -0.25), (108, -0.45), (122, -0.2)):
        r[yr] += hit
    r += (math.log(end) - r.sum()) / years
    return np.concatenate([[1.0], np.exp(np.cumsum(r))])


# --------------------------------------------------------------------------- cold open
@V.scene("o1")
def _(S):
    # frame 0 is the thumbnail: the whole claim is already on the page, then it builds
    S.text("€10,000", 140, 300, 120, INK, at=-1.0)
    S.draw(money_bag(370, 560, 0.9), -1.0, 0.3, snd=None)
    S.add(arrow(P_bez((570, 560), (810, 470), (1060, 560)), -1.0, INK, 7, 0.35))
    S.text("€76,000", 1130, 290, 170, ORANGE, at=-1.0, rot=-4)
    S.draw(money_bag(1420, 630, 1.5), -1.0, 0.4, snd=None)
    S.text("don't touch it.", 160, 750, 76, GREY, at=S.c("alone") - 0.1, rot=-2)
    S.text("30 years", 600, 440, 100, INK, at=S.c("30") - 0.1, rot=-2)
    S.text("before inflation", 1180, 392, 76, GREY, at=S.c("€76,000") + 0.4)
    S.text("7% a year", 700, 630, 76, INK, at=S.c("7%", 1) - 0.05)
    S.text("you add: €0", 160, 862, 88, INK, at=S.c("single", 1) - 0.3, rot=-2)
    S.text("the money does the work.", 880, 862, 84, INK, at=S.c("money", 1) - 0.35, rot=-2, cps=34)
    for k, (cx, cy) in enumerate(((1700, 560), (1180, 700), (1660, 760))):
        S.pop(coin(cx, cy, 0.8, col=HL), S.c("work", 1) + 0.1 + 0.15 * k, (cx, cy), snd="pop" if k == 0 else None)


@V.scene("o5")
def _(S):
    x0, y0, x1, y1 = 220, 180, 1700, 880
    axes(S, x0, y0, x1, y1, 0.0, "time", None)
    S.text("compound interest:", 300, 250, 90, INK, at=S.l(0) + 0.05, cps=34)
    pts = curve_pts(x0 + 20, y0 + 40, x1 - 40, y1 - 20, lambda u: math.exp(4.2 * u))
    segs = [(0, 22, "slow", S.c("slow")), (21, 46, "boring", S.c("boring")), (45, 70, "unbelievable!", S.c("unbelievable"))]
    spots = [(pts[8][0] - 40, pts[8][1] - 50, "l"), (pts[24][0] - 20, pts[24][1] - 70, "l"), (1450, 410, "r")]
    for k, (a, b, lab, at) in enumerate(segs):
        S.draw([stk(pts[a:b], 9, ORANGE if k == 2 else INK)], (S.l(0) + 0.3 if k == 0 else at - 0.15), 0.45 if k else at - S.l(0) + 0.1)
        S.text(lab, spots[k][0], spots[k][1], 74 if k < 2 else 100, ORANGE if k == 2 else INK, at=at, rot=-3, anchor=spots[k][2])
    q = S.c("quit")
    px, py = pts[40]
    S.add(cross(px, py, 34, q, RED, 9))
    S.text("most people quit here", px - 660, py - 180, 70, RED, at=q + 0.1)
    S.add(arrow(P_bez((px - 140, py - 150), (px - 70, py - 130), (px - 22, py - 44)), q + 0.3, RED, 5, 0.25, head=16))


@V.scene("o6")
def _(S):
    S.text("7", 330, 660, 420, ORANGE, at=S.c("seven") - 0.05, anchor="m", rot=-6, cps=8)
    S.text("ideas.", 500, 560, 150, INK, at=S.c("ideas") - 0.1, cps=34)
    fx, fy = 620, 790
    S.text("A = P(1 + r)", fx, fy, 88, GREY, at=S.c("no") - 0.4, cps=34)
    S.text("n", fx + line_w("A = P(1 + r)", 88) + 6, fy - 42, 56, GREY, at=S.c("no") - 0.05)
    S.add(strike(fx - 20, fy - 30, fx + line_w("A = P(1 + r)", 88) + 60, fy - 40, S.c("formulas") + 0.1, RED, 9))
    S.text("so simple,\nit feels illegal.", 1080, 300, 104, INK, at=S.c("simple") - 0.3, cps=30)


V.chapters({1: ("Interest on\ninterest.", 0), 2: ("The rule\nof 72.", 1), 3: ("Time beats\nmoney.", 0), 4: ("The boring\nyears.", 1),
            5: ("It works\nagainst you too.", 0), 6: ("Fees compound\ntoo.", 1), 7: ("Inflation:\ncompounding\nin reverse.", 0)},
           peek=set())


# --------------------------------------------------------------------------- 1. interest on interest
@V.scene("c1a")
def _(S):
    S.pop(coin(480, 520, 2.2, col=HL), S.l(0) + 0.05, (480, 520))
    S.text("€100", 400, 760, 100, INK, at=S.c("€100"))
    S.add(arrow(P_bez((660, 520), (900, 430), (1140, 520)), S.c("10%") - 0.1, INK, 6, 0.4))
    S.text("+10% a year", 760, 400, 76, GREY, at=S.c("10%"))
    S.pop(coin(1360, 520, 2.2), S.c("€110", 1) - 0.25, (1360, 520))
    S.pop(coin(1560, 380, 0.8, col=HL), S.c("€110", 1) + 0.15, (1560, 380))
    S.text("€110", 1270, 760, 110, ORANGE, at=S.c("€110", 1) - 0.1)
    S.text("+€10", 1510, 270, 70, INK, at=S.c("€110", 1) + 0.3)
    S.text("after 1 year", 1250, 850, 66, INK, at=S.c("year", 1))


@V.scene("c1b")
def _(S):
    gone = S.l(1) - 0.05
    S.text("next year:", 200, 220, 84, INK, at=S.l(0) + 0.02, cps=34)
    S.pop(coin(1180, 480, 1.9, col=HL), S.l(0) + 0.1, (1180, 480))
    S.text("€100", 1105, 700, 72, INK, at=S.l(0) + 0.3)
    S.pop(coin(1440, 400, 1.0, col=HL), S.l(0) + 0.8, (1440, 400), snd=None)
    S.text("+€10", 1390, 540, 70, INK, at=S.l(0) + 0.9)
    S.text("10% of €100", 200, 390, 92, INK, at=S.c("10%") - 0.15, until=gone)
    S.add(Dr([stk(P_line(180, 360, 220 + text_w("10% of €100", 92), 352, 0.03, 0), 8, RED)], S.c("€100") + 0.4, 0.22, until=gone))
    S.text("10% of €110", 200, 560, 110, INK, at=S.c("€110") - 0.4, until=gone)
    S.add(Dr([stk(P_line(200, 595, 200 + text_w("10% of €110", 110), 588, 0.03, 1), 6, INK)], S.c("€110") + 0.4, 0.3, until=gone))
    S.text("interest\non interest.", 200, 470, 130, ORANGE, at=S.c("interest", 1) - 0.1, rot=-3, cps=30)
    S.add(arrow(P_bez((1490, 360), (1540, 300), (1580, 330)), S.c("earning", 1), INK, 5, 0.25, head=14))
    S.pop(coin(1610, 320, 0.6, col=HL), S.c("own", 1) - 0.1, (1610, 320))
    S.text("+€1", 1575, 430, 66, INK, at=S.c("own", 1) + 0.1)


@V.scene("c1c")
def _(S):
    h_ = hill(140, 260, 1780, 930)
    S.draw([Fl(np.vstack([h_[1], [(1780, 1090), (140, 1090)]]), (196, 208, 224)), h_], S.l(0), 0.5, snd=None)
    S.draw(snowball(260, 225, 30), S.l(0) + 0.2, 0.3)
    S.text("a snowball.", 1180, 220, 110, INK, at=S.c("snowball") - 0.15, cps=30)
    S.text("small", 330, 200, 72, INK, at=S.c("small"))
    S.draw(snowball(820, 520, 70), S.c("huge") - 0.6, 0.35, snd=None)
    S.draw(snowball(1500, 790, 165), S.c("huge") - 0.1, 0.45)
    S.text("huge", 1240, 520, 110, INK, at=S.c("huge"), rot=-4)
    S.text("same snow.\nsame slope.", 180, 700, 76, INK, at=S.c("same", 1) - 0.1)
    S.text("time.", 760, 390, 170, ORANGE, at=S.c("time", 1) - 0.2, rot=-5)


# --------------------------------------------------------------------------- 2. the rule of 72
@V.scene("c2a")
def _(S):
    S.pop(coin(1270, 340, 2.0, col=HL), S.l(0) + 0.05, (1270, 340))
    S.add(arrow(P_bez((1400, 330), (1465, 290), (1530, 330)), S.c("money") - 0.1, INK, 6, 0.3))
    S.pop(coin(1610, 300, 1.3, col=HL), S.c("doubles") - 0.1, (1610, 300), snd=None)
    S.pop(coin(1660, 370, 1.3, col=HL), S.c("doubles") + 0.3, (1660, 370))
    S.text("how fast?", 1290, 560, 96, INK, at=S.c("how") - 0.05, rot=3, cps=34)
    S.text("72 ÷ return", 220, 330, 150, INK, at=S.c("divide") - 0.1, cps=20)
    S.text("= years to double", 260, 470, 84, GREY, at=S.c("return") - 0.2)
    S.text("72 ÷ 7 = ~10", 240, 720, 160, ORANGE, at=S.c("72", 1) - 0.2, rot=-3, cps=16)
    S.text("every ~10 years: ×2", 300, 845, 80, INK, at=S.c("doubles", 1) - 0.2)


@V.scene("c2b")
def _(S):
    vals = [10000 * 1.07 ** y for y in (0, 10, 20, 30)]
    labs = ["€10k", "€20k", "€39k", "€76k"]
    cues = [S.c("€10,000"), S.c("€20,000"), S.c("€39,000"), S.c("€76,000")]
    base, x0, bw, gap, maxh = 780, 330, 220, 140, 540
    S.text("€10,000 at 7%", 220, 190, 90, INK, at=S.l(0) + 0.02, cps=34)
    S.draw([stk(P_line(x0 - 40, base, x0 + 4 * (bw + gap), base, 0.005, 1), 7)], S.l(0) + 0.1, 0.3, snd=None)
    for k, (v, at) in enumerate(zip(vals, cues)):
        x = x0 + k * (bw + gap)
        h = v * maxh / vals[-1]
        stacked(S, x, base, bw, [h], at - 0.1, 1.0, [ORANGE if k == 3 else PUTIN])
        S.text(["now", "10 years", "20 years", "30 years"][k], x + bw / 2, base + 72, 64, INK, at=at, anchor="m")
        S.text(labs[k], x + bw / 2, base - h - 30, 84, ORANGE if k == 3 else INK, at=at + 0.2, anchor="m")
    S.text("+€37k", 1020, 330, 96, INK, at=S.c("bigger", 1) - 0.1, rot=-4)
    S.add(arrow(P_bez((1290, 300), (1350, 290), (1395, 330)), S.c("bigger", 1) + 0.6, INK, 6, 0.3, head=18))


# --------------------------------------------------------------------------- 3. time beats money
@V.scene("c3a")
def _(S):
    S.add(Fig(460, 900, 1.05, at=0.0, poses=[("stand", 0), ("wave", S.c("anna"))], moods=[("smile", 0), ("happy", S.c("anna"))], kind="bob", seed=41))
    S.add(Fig(1460, 900, 1.05, at=0.0, poses=[("stand", 0), ("wave", S.c("ben"))], moods=[("smile", 0)], kind="plain", seed=42, flip=True))
    S.text("Anna", 560, 680, 110, INK, at=S.c("anna") - 0.05)
    S.text("Ben", 1360, 680, 110, INK, at=S.c("ben") - 0.05, anchor="r")
    S.text("€200 a month · 7% a year", 610, 530, 76, INK, at=S.c("€200") - 0.1)
    tx0, tx1, ty = 300, 1620, 230
    yx = lambda a: tx0 + (a - 25) / 40 * (tx1 - tx0)
    S.draw([stk(P_line(tx0 - 30, ty, tx1 + 30, ty, 0.005, 2), 6, GREY)], S.c("ben") + 0.35, 0.4, snd=None)
    for k, a in enumerate((25, 35, 65)):
        S.text(str(a), yx(a), ty + 78, 70, INK, at=S.c("ben") + 0.6 + 0.12 * k, anchor="m")
    S.draw([stk(P_line(yx(25), ty - 40, yx(65), ty - 40, 0.005, 3), 14, ORANGE)], S.c("25", 1) - 0.1, 0.6)
    S.text("Anna", yx(25), ty - 70, 64, ORANGE, at=S.c("25", 1))
    S.draw([stk(P_line(yx(35), ty - 10, yx(65), ty - 10, 0.005, 4), 14, INK)], S.c("35", 1) - 0.1, 0.5)
    S.text("Ben", yx(35) + 60, ty + 150, 64, INK, at=S.c("35", 1))


@V.scene("c3b")
def _(S):
    base, sc, bw = 760, 540 / 525, 200
    bx = (220, 720, 1220)
    S.text("€200 a month", 220, 340, 80, INK, at=S.l(0) + 0.02, cps=34)
    S.draw([stk(P_line(180, base, 1700, base, 0.005, 1), 7)], S.l(0) + 0.1, 0.3, snd=None)
    stacked(S, bx[0], base, bw, [72, 244 - 72], S.c("puts") - 0.1, sc, [PUTIN, BLUE], ["in: €72k", None],
            step=S.c("€244,000") - S.c("puts"), label_size=70)
    S.text("Ben", bx[0] + bw / 2, base + 80, 84, INK, at=S.l(0) + 0.1, anchor="m")
    S.text("€244k", bx[0] + bw / 2, base - 244 * sc - 30, 90, INK, at=S.c("€244,000") + 0.3, anchor="m")
    stacked(S, bx[1], base, bw, [96, 525 - 96], S.c("€24,000", 1) - 0.1, sc, [PUTIN, ORANGE], ["in: €96k", None],
            step=S.c("€525,000", 1) - S.c("€24,000", 1), label_size=70)
    S.text("Anna", bx[1] + bw / 2, base + 80, 84, INK, at=S.l(1), anchor="m")
    S.text("€525k", bx[1] + bw / 2, base - 525 * sc - 30, 100, ORANGE, at=S.c("€525,000", 1) + 0.3, anchor="m")
    # Ben doubles his money and starts ten years late: still short of Anna
    stacked(S, bx[2], base, bw, [144, 488 - 144], S.c("doubles", 2) - 0.1, sc, [PUTIN, BLUE], ["in: €144k", None],
            step=S.c("€488,000", 2) - S.c("doubles", 2), label_size=70)
    S.text("Ben at €400", bx[2] + bw / 2, base + 80, 70, INK, at=S.c("doubles", 2), anchor="m")
    S.text("€488k", bx[2] + bw + 24, base - 488 * sc + 60, 90, INK, at=S.c("€488,000", 2) + 0.3)
    ay = base - 525 * sc
    for k in range(9):
        xa = bx[1] + bw + 14 + k * 58
        S.add(Dr([stk(P_line(xa, ay, xa + 32, ay, 0.0, k), 5, GREY)], S.c("still", 2) - 0.1 + 0.03 * k, 0.08, seed=500 + k))
    S.text("still less.", bx[2] + bw + 24, ay - 10, 76, INK, at=S.c("less", 2) - 0.1)


@V.scene("c3c")
def _(S):
    S.text("+10 years", 240, 330, 140, INK, at=S.l(0), rot=-3, cps=32)
    S.text("= more than ×2", 300, 480, 110, ORANGE, at=S.c("twice") - 0.2, rot=-3)
    S.draw(plant(1400, 760, 1.5, leaves=5), S.l(0) + 0.3, 0.6)
    S.text("start early", 240, 780, 110, INK, at=S.c("early") - 0.1)
    S.text(">", 820, 780, 130, INK, at=S.c("beats") - 0.05)
    S.text("start big", 920, 780, 90, GREY, at=S.c("big") - 0.1)


# --------------------------------------------------------------------------- 4. the boring years
@V.scene("c4a")
def _(S):
    base, sc = 840, 520 / 35
    S.text("why people give up:", 200, 210, 96, INK, at=S.l(0) + 0.02, cps=34)
    S.text("10 years × €200 a month", 200, 330, 76, INK, at=S.c("ten") - 0.1)
    S.draw([stk(P_line(900, base, 1500, base, 0.005, 1), 7), stk(P_rect(1000, base - 35 * sc, 240, 35 * sc, 6), 5, GREY)], S.l(0) + 0.05, 0.4)
    stacked(S, 1000, base, 240, [24, 11], S.c("€200") - 0.1, sc, [PUTIN, ORANGE], ["put in €24k", "growth €11k"],
            step=S.c("€11,000", 1) - S.c("€200") + 0.1)
    S.text("€35k", 1120, base - 35 * sc - 30, 110, INK, at=S.c("€35,000") - 0.1, anchor="m")
    S.add(Fig(420, 920, 1.1, at=0.0, poses=[("stand", 0), ("sad", S.c("nothing", 1) - 0.2)], moods=[("flat", 0), ("worried", S.c("nothing", 1))],
              seed=3))
    S.text("...nothing?", 540, 560, 84, GREY, at=S.c("nothing", 1), rot=5)


@V.scene("c4b")
def _(S):
    x0, y0, x1, y1 = 220, 200, 1700, 880
    axes(S, x0, y0, x1, y1, 0.0, "year", None)
    yrs = np.arange(1, 31)
    growth = np.array([fv(200, y) - fv(200, y - 1) - 2400 for y in yrs])
    top = growth.max()
    X = lambda y: x0 + 30 + (y - 1) / 29 * (x1 - x0 - 80)
    Y = lambda v: y1 - 20 - v / top * (y1 - y0 - 60)
    S.draw([stk(P_line(X(1), Y(2400), X(30), Y(2400), 0.005, 3), 6, GREY)], 0.2, 0.5, snd=None)
    S.text("put in each year: €2,400", 1100, Y(2400) - 30, 64, INK, at=0.5)
    pts = np.array([(X(y), Y(g)) for y, g in zip(yrs, growth)])
    S.draw([stk(pts[:11], 9, INK)], 0.3, 0.6)
    S.text("growth each year", 1560, 240, 70, INK, at=S.c("bends", 1) - 0.1, anchor="r")
    mx, my = X(11), Y(2400)
    S.add(circ(mx, my, 40, 40, S.c("11") - 0.05, ORANGE, 7))
    S.text("year 11", mx + 100, my + 70, 70, ORANGE, at=S.c("11") + 0.1)
    S.text("growth > what\nshe puts in", 260, 400, 80, INK, at=S.c("beats") - 0.2)
    S.add(arrow(P_bez((600, 520), (660, 600), (mx - 30, my - 110)), S.c("beats") + 0.5, INK, 5, 0.3, head=16))
    S.draw([stk(pts[10:], 10, INK)], S.c("bends", 1) - 0.4, 0.9)
    for k in range(6):
        bx = x0 + 40 + k * 90
        S.draw([stk(P_rect(bx, y1 - 64, 84, 40, 3), 4.5, (170, 120, 90))], S.c("foundation", 1) - 0.3 + 0.06 * k, 0.15, snd=None)
    S.text("the foundation", 250, Y(2400) - 40, 66, (150, 100, 70), at=S.c("foundation", 1) - 0.3)


# --------------------------------------------------------------------------- 5. it works against you too
@V.scene("c5a")
def _(S):
    S.draw(snowball(430, 560, 110), S.l(0), 0.35, snd=None)
    S.text("for you", 340, 770, 80, GREEN, at=S.l(0) + 0.15)
    S.draw([stk(P_line(800, 300, 805, 820, 0.01, 2), 5, GREY)], S.l(0) + 0.1, 0.3, snd=None)
    S.draw(snowball(1150, 560, 110, col=(244, 214, 210)), S.l(0) + 0.35, 0.35, snd=None)
    S.text("against you", 1010, 770, 80, RED, at=S.l(0) + 0.5)
    S.text("doesn't care.", 480, 230, 100, INK, at=S.c("care") - 0.25, rot=-3)
    S.draw(card(1600, 400, 0.9), S.c("credit", 1) - 0.2, 0.4)
    S.text("20% a year", 1420, 640, 84, RED, at=S.c("20%", 1) - 0.1)


@V.scene("c5b")
def _(S):
    S.text("72 ÷ 20 = 3.6 years", 200, 260, 120, INK, at=S.c("20%") - 0.15, cps=26)
    S.text("to double a debt", 240, 380, 84, RED, at=S.c("doubles") - 0.1)
    for k, (x, r) in enumerate(((300, 40), (520, 70), (820, 110))):
        S.draw(snowball(x, 720 - r, r, col=(244, 214, 210)), S.c("doubles") + 0.2 * k, 0.3, snd="scr" if k == 2 else None)
    S.text("for the bank.", 1000, 560, 80, INK, at=S.c("bank") - 0.2)
    S.draw(card(1560, 330, 0.8), S.l(0) + 0.05, 0.4)
    S.add(cross(1560, 330, 100, S.c("expensive", 1) + 0.2, RED, 11))
    S.text("pay it off first.", 1060, 760, 90, ORANGE, at=S.c("pay", 1) - 0.1, rot=-3)
    S.text("best return you'll ever get.", 960, 850, 72, INK, at=S.c("best", 1) - 0.1)


# --------------------------------------------------------------------------- 6. fees compound too
@V.scene("c6a")
def _(S):
    S.text("a fee of", 220, 300, 84, INK, at=S.l(0) + 0.02, cps=34)
    S.text("1.8%", 200, 640, 260, ORANGE, at=S.c("1.8%") - 0.3, rot=-5, cps=16)
    S.text("a year", 830, 620, 90, INK, at=S.c("year") - 0.1)
    S.text("tiny?", 1180, 380, 110, GREY, at=S.c("tiny") - 0.15, rot=4)
    S.add(strike(1160, 350, 1440, 340, S.c("isn't") + 0.1, RED, 9))
    S.text("it isn't.", 1100, 790, 130, RED, at=S.c("isn't") - 0.1, rot=-3)


@V.scene("c6x")
def _(S):
    S.text("€200 a month · 30 years", 200, 190, 80, INK, at=S.l(0) + 0.02, cps=34)
    for k in range(12):
        S.pop(coin(250 + (k % 6) * 105, 420 + (k // 6) * 110, 0.85, col=HL), S.l(0) + 0.15 + 0.07 * k, (250 + (k % 6) * 105, 420 + (k // 6) * 110),
              snd="pop" if k == 0 else None)
    S.text("every month", 230, 650, 76, GREY, at=S.l(0) + 1.0)
    S.text("you put in: €72,000", 220, 800, 76, INK, at=S.c("years") + 0.2)
    base = 770
    S.add(*bars(1000, base, [234581, 172745], ["", ""], S.c("0.2%") - 0.1, step=S.c("1.8%") - S.c("0.2%"), maxh=520, bw=240, gap=220,
                cols=[ORANGE, (244, 214, 210)], txt=["€235k", "€173k"], seed=6, size=90))
    S.text("fees 0.2%", 1120, base + 76, 70, INK, at=S.c("0.2%"), anchor="m")
    S.text("fees 1.8%", 1580, base + 76, 70, RED, at=S.c("1.8%"), anchor="m")


@V.scene("c6b")
def _(S):
    jx, jy = 560, 560
    S.draw(jar(jx, jy, 1.9, fill_u=0.75, col=(214, 226, 196)), 0.0, 0.5)
    S.draw([stk(P_ell(jx + 110, jy + 120, 9, 7, 2, 0.05), 5)], S.c("compounds") - 0.4, 0.2, snd=None)
    for k in range(5):
        t0 = S.c("compounds") - 0.2 + k * 0.42
        S.add(Dr(coin(jx + 125, jy + 150, 0.32), t0, 0.0, pop=True, anchor=(jx + 125, jy + 150),
                 move=lambda tt: (min(1.0, tt / 0.5) * 30, min(1.0, tt / 0.5) ** 2 * 300, 0, 1), until=t0 + 0.5, seed=200 + k))
    S.text("same money in.", 1000, 320, 90, INK, at=S.c("same") - 0.1)
    S.text("€62k less.", 960, 560, 160, RED, at=S.c("€62,000") - 0.25, rot=-4, cps=14)
    S.text("every single year.", 1040, 760, 80, GREY, at=S.c("every") - 0.1)


# --------------------------------------------------------------------------- 7. inflation
@V.scene("c7a")
def _(S):
    S.draw(cart(420, 600, 1.1), 0.0, 0.5)
    S.pop(tag(440, 400, 0.9, "€1.00"), S.c("prices") - 0.05, (440, 400))
    S.pop(tag(700, 290, 0.9, "€1.02", HL), S.c("rise") + 0.1, (700, 290))
    S.text("ECB target: 2%", 200, 830, 80, INK, at=S.c("aims") - 0.2)
    nx, ny = 1350, 540

    def shrink(tt, t0=S.c("loses", 1) - S.c("2%", 1) + 0.0):
        u = clamp((tt - t0) / 1.6)
        return (0, 0, 0, 1.0 - 0.45 * ease_io(u))
    S.add(Dr(note(nx, ny, 2.2), S.c("2%", 1) - 0.1, 0.0, pop=True, anchor=(nx, ny), move=shrink, seed=77), snd="pop", at=S.c("2%", 1))
    S.text("€100 in cash", 1180, 290, 76, INK, at=S.c("cash", 1) - 0.1)
    S.text("30 years later: buys ~€55", 1000, 820, 74, RED, at=S.c("45%", 1) - 0.1)


@V.scene("c7x")
def _(S):
    S.text("every number in this video:", 200, 210, 80, INK, at=S.l(0) + 0.02, cps=34)
    for k, lab in enumerate(("€76k", "€525k", "€235k")):
        S.pop(tag(1200 + 240 * k, 320, 0.9, lab, HL), S.l(0) + 0.5 + 0.35 * k, (1200 + 240 * k, 320), snd="pop" if k == 0 else None,
              until=S.c("€76,000") - 0.35)
    S.text("€76,000", 220, 470, 140, INK, at=S.c("€76,000") - 0.2)
    S.text("before inflation", 240, 570, 70, GREY, at=S.c("€76,000") + 0.25)
    S.add(arrow(P_bez((780, 430), (920, 390), (1060, 440)), S.c("worth") - 0.2, INK, 6, 0.35))
    S.text("~€42,000", 1100, 470, 140, ORANGE, at=S.c("€42,000") - 0.25)
    S.text("in today's money", 1120, 570, 70, ORANGE, at=S.c("€42,000") + 0.15)
    S.text("still ×4", 520, 830, 150, INK, at=S.c("four") - 0.25, rot=-3)
    S.text("what went in: €10,000", 1060, 810, 70, GREY, at=S.c("still") - 0.1)


@V.scene("c7b")
def _(S):
    S.noframe = True
    x0, y0, x1, y1 = 200, 420, 1720, 860
    S.text("money can't sit still.", 200, 190, 110, INK, at=S.l(0) + 0.02, cps=44)
    axes(S, x0, y0, x1, y1, S.l(0) + 0.05, None, None)
    v = stock_path()
    n = len(v)
    xs = x0 + 30 + np.arange(n) / (n - 1) * (x1 - x0 - 80)
    ys = y1 - 20 - v / v.max() * (y1 - y0 - 40)
    pts = np.stack([xs, ys], 1)
    t_draw = S.l(0) + 0.3
    S.draw([stk(pts, 7, INK)], t_draw, max(1.5, S.c("average") - t_draw))
    S.text("125 years of global stocks, after inflation", 230, 310, 64, INK, at=S.c("125") - 0.1)
    S.text("illustration, not real data", 250, 490, 70, GREY, at=S.c("grew") - 0.1)
    S.text("~5% a year, on average", 250, 590, 76, INK, at=S.c("5%") - 0.2)
    for k, j in enumerate((102, 109)):
        px, py = pts[j]
        S.add(circ(px, py + 8, 40, 52, S.c("terrible", 1) + 0.25 * k, RED, 6))
    S.text("terrible years", 1210, 600, 70, RED, at=S.c("terrible", 1) + 0.1)
    S.add(arrow(P_bez((1330, 625), (1375, 670), (pts[102][0] - 6, pts[102][1] - 50)), S.c("terrible", 1) + 0.5, RED, 5, 0.25, head=14))
    S.text("time did the heavy lifting.", 250, 720, 86, ORANGE, at=S.c("heavy", 1) - 0.6, rot=-2, cps=30)


# --------------------------------------------------------------------------- final message
@V.scene("f0")
def _(S):
    S.noframe = True
    S.text("final message.", 260, 600, 160, INK, at=0.02, rot=-3, cps=34)
    S.add(under(270, 1100, 650, 0.6, ORANGE, 8, 0.4, wavy=True))


@V.scene("f1")
def _(S):
    S.draw(clock(1450, 520, 1.6), S.l(0) + 0.05, 0.5)
    S.text("compound interest", 260, 230, 90, INK, at=S.l(0) + 0.1, cps=34)
    S.text("magic", 300, 440, 140, INK, at=S.c("magic") - 0.35)
    S.add(strike(280, 400, 740, 392, S.c("magic") + 0.35, RED, 10))
    S.text("patience", 360, 720, 170, ORANGE, at=S.c("patience") - 0.2, rot=-3)
    S.text("(written in maths)", 420, 800, 76, GREY, at=S.c("written") - 0.25)


@V.scene("f2")
def _(S):
    S.noframe = True
    S.draw([stk(P_rect(170, 180, 1060, 720, 6, r=18), 6), stk(P_line(470, 152, 930, 152, 0.01, 7), 9)], S.l(0), 0.4, snd=None)
    items = (("early", "start early"), ("small", "start small if needed"), ("fees", "keep fees low"), ("kill", "kill expensive debt"))
    for k, (w_, lab) in enumerate(items):
        y = 320 + k * 165
        at = S.c(w_) - 0.25
        S.text(lab, 320, y, 100, INK, at=at, cps=32)
        S.add(check(250, y - 32, 30, at + 0.4, GREEN, 10, seed=k))
    S.draw(snowball(1550, 600, 150), S.l(0) + 0.1, 0.5, snd=None)


@V.scene("f3")
def _(S):
    S.add(Fig(620, 950, 1.3, at=0.0, poses=[("sit", 0)], moods=[("smile", 0), ("sleep", S.c("nothing") + 0.2)], seed=3, idle=0.4))
    S.draw([stk(P_rect(470, 790, 270, 26, 5, r=8), 7), stk(P_line(490, 816, 490, 950, 0, 1), 7), stk(P_line(720, 816, 720, 950, 0, 2), 7),
            stk(P_line(476, 792, 450, 520, 0.02, 3), 7)], 0.0, 0.4, snd=None)
    S.draw(plant(1600, 900, 1.0, leaves=2), 0.2, 0.4, snd=None, until=S.c("long") - 0.2)
    S.draw(plant(1600, 900, 1.9, leaves=6), S.c("long") - 0.2, 0.7)
    S.text("do nothing.", 760, 250, 130, ORANGE, at=S.c("nothing") - 0.2, rot=-4)
    S.text("for a very long time.", 800, 370, 76, GREY, at=S.c("long") - 0.3)


@V.scene("end")
def _(S):
    endcard(S, "save money so easily\nit feels illegal.", note="education, not financial advice.\nexamples, not promises.")


# --------------------------------------------------------------------------- framing: keep text out of the caption band (local helper)
def _text_box(tx, fs, fx, fy):
    sz = tx["size"] * fs
    X, Y, w = fx + fs * (tx["x"] - fx), fy + fs * (tx["y"] - fy), tx["w"] * fs
    xl = X - (w / 2 if tx["anchor"] == "m" else (w if tx["anchor"] == "r" else 0))
    return xl, Y - 0.75 * sz, xl + w, Y + sz * (tx["n"] - 1) * tx["lh"] + 0.28 * sz


_autoframe = V.autoframe


def autoframe_text_safe():
    """Belt and braces on top of the framework framer: text stays above a two-line caption (y <= 888) and inside x 90..1830.
    Zoom back (never below 1.0) until every text box fits."""
    _autoframe()
    for sc in V.SC:
        fs, fx, fy = sc.cam.frame
        while fs > 1.0 and any(b[0] < 90 or b[2] > W - 90 or b[1] < 52 or b[3] > 888 for b in (_text_box(t, fs, fx, fy) for t in sc.texts)):
            fs = max(1.0, round(fs - 0.02, 3))
        sc.cam.frame = (fs, fx, fy)


V.autoframe = autoframe_text_safe


if __name__ == "__main__":
    V.main()
