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
       "€60,000": "sixty thousand euros", "7%": "seven percent", "10%": "ten percent", "20%": "twenty percent", "1.8%": "one point eight percent",
       "0.2%": "zero point two percent", "2%": "two percent", "5%": "five percent", "72": "seventy-two", "7": "seven", "10": "ten",
       "25": "twenty-five", "35": "thirty-five", "65": "sixty-five", "11": "eleven", "30": "thirty", "125": "a hundred and twenty-five"}
V = Video("compound", say=SAY, seed=7, keys=dict(prog=[(57, 60, 64, 67), (53, 57, 60, 64), (48, 52, 55, 59), (55, 59, 62, 65)],
                                                 roots=[45, 41, 36, 43], bpm=76),
          hush=[("And here's the part", "Compound interest is slow")], tape="Final message")
L = V.L

L("o1", "Imagine putting €10,000 away, and never touching it again.")
L("o1", "Thirty years later, at 7% a year, it's worth about €76,000.")
L("o2", "You added nothing. Not one euro. The money did the work.")
L("o3", "This is compound interest. It's often called the eighth wonder of the world.")
L("o3", "That quote is usually credited to Einstein. He almost certainly never said it. But the maths is real.")
L("o4", "And here's the part nobody tells you.")
L("o5", "Compound interest is slow, then boring, then suddenly unbelievable. Most people quit during the boring part.")
L("o6", "Today, I'll explain it so simply it feels illegal. Seven ideas. No formulas. Let's begin.")

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
L("c2b", "So €10,000 becomes €20,000, then €40,000, then €80,000.")
L("c2b", "Each doubling is bigger than all the ones before it.")

L("c3", "Three. Time beats money.")
L("c3a", "Meet Anna and Ben. Both invest €200 a month, at 7% a year.")
L("c3a", "Anna starts at 25. Ben starts at 35. Both stop at 65.")
L("c3b", "Ben puts in €72,000. He ends with about €244,000.")
L("c3b", "Anna puts in only €24,000 more. She ends with about €525,000.")
L("c3c", "Ten extra years more than doubled her money. Starting early beats starting big.")

L("c4", "Four. The boring years.")
L("c4a", "Here's why most people give up. After ten years of €200 a month, Anna has about €35,000.")
L("c4a", "Only about €11,000 of that is growth. It feels like nothing is happening.")
L("c4b", "But around year 11, the growth in a single year becomes bigger than everything she puts in that year.")
L("c4b", "After that, the curve bends upward. The boring part was the foundation.")

L("c5", "Five. It works against you too.")
L("c5a", "Compound interest doesn't care which side you're on.")
L("c5a", "Some credit cards and store credit charge around 20% a year.")
L("c5b", "At 20%, a debt doubles in less than four years. That's the rule of 72, working for the bank.")
L("c5b", "So before you invest, pay off expensive debt. It's the best return you'll ever get.")

L("c6", "Six. Fees compound too.")
L("c6a", "A fee of 1.8% a year sounds tiny. It isn't.")
L("c6a", "€200 a month for 30 years: with fees of 0.2%, about €235,000. With 1.8%, about €173,000.")
L("c6b", "Same money in. Over €60,000 less out. The fee compounds against you, every single year.")

L("c7", "Seven. Inflation is compounding in reverse.")
L("c7a", "Prices rise a little every year. The European Central Bank aims for 2%.")
L("c7a", "At 2% inflation, money sitting in cash loses almost half its buying power in 30 years.")
L("c7b", "That's why long-term money usually can't just sit still. Over the last 125 years, global stocks grew about 5% a year faster than inflation, on average.")
L("c7b", "Not every year. Some years were terrible. But over decades, time did the heavy lifting.")

L("f0", "Final message.")
L("f1", "Compound interest isn't magic. It's just patience, written in maths.")
L("f2", "Start early. Start small if you have to. Keep fees low. Kill expensive debt.")
L("f3", "And then, the hardest part: do nothing, for a very long time.")
L("end", "This is education, not financial advice. The numbers here are examples, not promises. If this helped, subscribe. "
         "Next up: how to save money so easily it feels illegal.")


def fv(m, years, rate=0.07):
    i = rate / 12
    return m * ((1 + i) ** (years * 12) - 1) / i


def axes(S, x0, y0, x1, y1, at, xl=None, yl=None):
    S.draw([stk(P_line(x0, y1, x1, y1, 0.005, 1), 6), stk(P_line(x0, y1, x0 + 2, y0, 0.005, 2), 6)], at, 0.35, snd=None)
    if xl:
        S.text(xl, x1 - 10, y1 + 60, 52, GREY, at=at + 0.2, anchor="r")
    if yl:
        S.text(yl, x0 + 20, y0 + 10, 52, GREY, at=at + 0.2)


def curve_pts(x0, y0, x1, y1, fn, n=70):
    xs = np.linspace(0, 1, n)
    ys = np.array([fn(u) for u in xs])
    ys = (ys - ys.min()) / (ys.max() - ys.min() + 1e-9)
    return np.stack([x0 + xs * (x1 - x0), y1 - ys * (y1 - y0)], 1)


def stacked(S, x, base, w, parts, at, scale, cols, labels=None, step=0.5):
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
            S.text(labels[k], x + w + 30, y - h / 2 + 22, 58, INK, at=t0 + 0.3)
        y -= h


# --------------------------------------------------------------------------- cold open
@V.scene("o1")
def _(S):
    S.add(Fig(330, 930, 1.2, at=0.0, poses=[("stand", 0), ("hold_r", S.c("€10,000") - 0.1), ("shrug", S.c("thirty", 1))],
              moods=[("smile", 0), ("o", S.c("€76,000", 1))], seed=3))
    S.draw(money_bag(620, 720, 0.85), S.c("€10,000") - 0.2, 0.5)
    S.text("€10,000", 520, 500, 92, INK, at=S.c("€10,000"))
    S.text("don't touch it.", 470, 1010, 60, GREY, at=S.c("never") - 0.1, rot=-2)
    S.draw(calendar(1030, 330, 0.7, day=None, head="+30 YEARS"), S.c("thirty", 1) - 0.2, 0.4)
    S.add(arrow(P_bez((800, 720), (1030, 640), (1250, 720)), S.c("thirty", 1), INK, 6, 0.45))
    S.text("7% a year", 920, 600, 60, GREY, at=S.c("7%", 1))
    S.draw(money_bag(1560, 650, 1.6), S.c("€76,000", 1) - 0.4, 0.6)
    S.text("€76,000", 1380, 280, 130, ORANGE, at=S.c("€76,000", 1) - 0.1, rot=-4)


@V.scene("o2")
def _(S):
    S.add(Fig(500, 930, 1.3, at=0.0, poses=[("shrug", 0), ("cross", S.c("work") - 0.3)], moods=[("o", 0), ("smug", S.c("work"))], seed=3))
    S.text("you added: €0", 760, 300, 100, INK, at=S.c("nothing") - 0.2, rot=-2)
    S.draw(money_bag(1400, 680, 1.3), S.c("money") - 0.4, 0.5)
    for k, (x, y) in enumerate(((1230, 520), (1580, 500), (1620, 640))):
        S.draw([stk(P_bez((x, y), (x + 8, y - 22), (x - 4, y - 40)), 5, (120, 160, 200))], S.c("work") + 0.1 + 0.15 * k, 0.2, snd=None)
    S.text("the money did the work.", 820, 1000, 76, ORANGE, at=S.c("work") - 0.2, rot=-2)


@V.scene("o3")
def _(S):
    S.add(hilite(180, 180 + text_w("compound interest", 130), 268, 86, S.c("compound") - 0.05, seed=2))
    S.text("compound interest", 180, 300, 130, INK, at=S.c("compound") - 0.05)
    S.text("\"the 8th wonder of the world\"", 220, 450, 72, GREY, at=S.c("eighth") - 0.1)
    S.add(Fig(1450, 930, 1.25, at=S.l(1) - 0.2, poses=[("think", 0)], moods=[("flat", 0), ("worried", S.c("never", 1))], kind="spiky", seed=31,
              enter="pop"))
    S.text("Einstein?", 1310, 380, 80, INK, at=S.c("einstein", 1) - 0.2, rot=4)
    S.add(strike(1290, 350, 1640, 340, S.c("never", 1) + 0.2, RED, 8))
    S.text("probably never said it.", 1080, 1010, 62, RED, at=S.c("never", 1), rot=-2)
    S.text("the maths is real.", 260, 760, 110, ORANGE, at=S.c("real", 1) - 0.25, rot=-3)


@V.scene("o4")
def _(S):
    S.add(Fig(980, 1520, 3.2, at=0.0, poses=[("stand", 0)], moods=[("smug", 0)], enter="none", seed=3, idle=0.6, look=0.4))
    S.text("psst.", 1430, 320, 96, GREY, at=S.c("part") - 0.2, rot=8)


@V.scene("o5")
def _(S):
    x0, y0, x1, y1 = 220, 180, 1700, 900
    axes(S, x0, y0, x1, y1, 0.0, "time", "money")
    pts = curve_pts(x0 + 20, y0 + 40, x1 - 40, y1 - 20, lambda u: math.exp(4.2 * u))
    segs = [(0, 22, "slow", S.c("slow")), (21, 46, "boring", S.c("boring")), (45, 70, "unbelievable!", S.c("unbelievable"))]
    spots = [(pts[8][0] - 40, pts[8][1] - 50), (pts[24][0] - 20, pts[24][1] - 70), (1080, 330)]
    for k, (a, b, lab, at) in enumerate(segs):
        S.draw([stk(pts[a:b], 9, ORANGE if k == 2 else INK)], at - 0.15, 0.45)
        S.text(lab, spots[k][0], spots[k][1], 70 if k < 2 else 96, ORANGE if k == 2 else INK, at=at, rot=-3)
    q = S.c("quit")
    px, py = pts[40]
    S.add(cross(px, py, 34, q, RED, 9))
    S.text("most people quit here", px - 180, py + 150, 62, RED, at=q + 0.1)
    S.add(arrow(P_bez((px - 40, py + 100), (px - 30, py + 70), (px - 8, py + 40)), q + 0.3, RED, 5, 0.25, head=16))


@V.scene("o6")
def _(S):
    S.text("7", 300, 600, 380, ORANGE, at=S.c("seven") - 0.05, anchor="m", rot=-6, cps=8)
    S.text("ideas", 470, 520, 130, INK, at=S.c("ideas"))
    S.text("A = P(1+r)^n", 520, 800, 96, GREY, at=S.c("formulas") - 0.6, cps=30, path=HAND2)
    S.add(strike(500, 770, 1060, 760, S.c("formulas") + 0.15, RED, 9))
    S.text("so simple it feels illegal.", 470, 300, 72, GREY, at=S.c("simply") - 0.2, rot=-2)
    S.add(Fig(1550, 950, 1.2, at=0.0, poses=[("stand", 0), ("wave", S.c("begin"))], moods=[("smile", 0), ("happy", S.c("begin"))], seed=3, flip=True))


V.chapters({1: ("Interest on\ninterest.", 0), 2: ("The rule\nof 72.", 1), 3: ("Time beats\nmoney.", 0), 4: ("The boring\nyears.", 1),
            5: ("It works\nagainst you too.", 0), 6: ("Fees compound\ntoo.", 1), 7: ("Inflation:\ncompounding\nin reverse.", 0)},
           peek={1, 4, 6})


# --------------------------------------------------------------------------- 1. interest on interest
@V.scene("c1a")
def _(S):
    S.pop(coin(480, 560, 2.2), S.c("€100") - 0.1, (480, 560))
    S.text("€100", 400, 800, 96, INK, at=S.c("€100"))
    S.add(arrow(P_bez((660, 560), (900, 470), (1140, 560)), S.c("10%") - 0.1, INK, 6, 0.4))
    S.text("+10% a year", 780, 440, 72, GREY, at=S.c("10%"))
    S.pop(coin(1360, 560, 2.2), S.c("€110", 1) - 0.25, (1360, 560))
    S.pop(coin(1560, 420, 0.8, col=HL), S.c("€110", 1) + 0.15, (1560, 420))
    S.text("€110", 1270, 800, 110, ORANGE, at=S.c("€110", 1) - 0.1)
    S.text("+€10", 1520, 300, 60, INK, at=S.c("€110", 1) + 0.3)
    S.text("year 1", 1300, 900, 56, GREY, at=S.c("year", 1))


@V.scene("c1b")
def _(S):
    S.text("10% of €100", 200, 300, 92, INK, at=S.c("€100") - 0.5)
    S.add(strike(180, 270, 220 + text_w("10% of €100", 92), 262, S.c("€100") + 0.4, RED, 8))
    S.text("10% of €110", 200, 470, 110, ORANGE, at=S.c("€110") - 0.4)
    S.add(under(200, 200 + text_w("10% of €110", 110), 500, S.c("€110") + 0.4, INK, 6))
    S.pop(coin(1180, 500, 1.9), S.c("interest", 1) - 0.4, (1180, 500))
    S.pop(coin(1440, 420, 1.0, col=HL), S.c("earning", 1), (1440, 420))
    S.pop(coin(1590, 350, 0.55, col=HL), S.c("own", 1), (1590, 350))
    S.text("€100", 1110, 720, 64, INK, at=S.c("interest", 1))
    S.text("+€10", 1390, 580, 56, INK, at=S.c("earning", 1) + 0.1)
    S.text("+€1", 1560, 470, 48, INK, at=S.c("own", 1) + 0.1)
    S.text("interest on interest.", 960, 930, 96, ORANGE, at=S.c("interest", 1, 1) - 0.2, rot=-3)


@V.scene("c1c")
def _(S):
    S.draw([hill(140, 260, 1780, 930)], 0.0, 0.6, snd=None)
    S.draw([stk(P_line(1450, 960, 1800, 960, 0.01, 4), 6)], 0.2, 0.3, snd=None)
    S.draw(snowball(260, 225, 30), S.c("small") - 0.1, 0.3)
    S.text("small", 330, 200, 64, GREY, at=S.c("small"))
    S.draw(snowball(820, 520, 70), S.c("huge") - 0.6, 0.35, snd=None)
    S.draw(snowball(1500, 790, 165), S.c("huge") - 0.1, 0.45)
    S.text("huge", 1240, 520, 110, INK, at=S.c("huge"), rot=-4)
    S.text("same snow. same slope.", 140, 1010, 64, GREY, at=S.c("same", 1) - 0.1)
    S.text("time.", 760, 330, 170, ORANGE, at=S.c("time", 1) - 0.2, rot=-5)


# --------------------------------------------------------------------------- 2. the rule of 72
@V.scene("c2a")
def _(S):
    S.text("72 ÷ return", 220, 330, 150, INK, at=S.c("divide") - 0.1, cps=14)
    S.text("= years to double", 260, 470, 84, GREY, at=S.c("return") - 0.2)
    S.text("72 ÷ 7 = ~10", 240, 760, 160, ORANGE, at=S.c("72", 1) - 0.2, rot=-3, cps=12)
    S.text("every ~10 years: ×2", 300, 930, 76, INK, at=S.c("doubles", 1) - 0.2)
    S.add(Fig(1550, 950, 1.2, at=0.0, poses=[("think", 0), ("point_l", S.c("72", 1))], moods=[("flat", 0), ("happy", S.c("doubles", 1))],
              seed=3, flip=True))


@V.scene("c2b")
def _(S):
    vals = [10, 20, 40, 80]
    cues = [S.c("€10,000"), S.c("€20,000"), S.c("€40,000"), S.c("€80,000")]
    base, x0, bw, gap, maxh = 880, 260, 220, 140, 640
    S.draw([stk(P_line(x0 - 40, base, x0 + 4 * (bw + gap), base, 0.005, 1), 7)], 0.0, 0.3, snd=None)
    for k, (v, at) in enumerate(zip(vals, cues)):
        x = x0 + k * (bw + gap)
        stacked(S, x, base, bw, [v * maxh / 80], at - 0.1, 1.0, [ORANGE if k == 3 else PALE])
        S.text(["now", "10 y", "20 y", "30 y"][k], x + bw / 2, base + 70, 56, INK, at=at, anchor="m")
        S.text(f"€{v}k", x + bw / 2, base - v * maxh / 80 - 30, 76, INK, at=at + 0.2, anchor="m")
    S.text("(roughly)", x0 + 3 * (bw + gap) + bw / 2, base + 140, 48, GREY, at=S.c("€80,000") + 0.3, anchor="m")
    S.add(circ(x0 + 3 * (bw + gap) + bw / 2, base - 400, 170, 360, S.c("bigger", 1), INK, 6))
    S.text("+€40k", 1040, 260, 90, ORANGE, at=S.c("bigger", 1) + 0.2, rot=-4)


# --------------------------------------------------------------------------- 3. time beats money
@V.scene("c3a")
def _(S):
    S.add(Fig(460, 950, 1.15, at=0.0, poses=[("stand", 0), ("wave", S.c("anna"))], moods=[("smile", 0), ("happy", S.c("anna"))], kind="bob", seed=41))
    S.add(Fig(1460, 950, 1.15, at=0.0, poses=[("stand", 0), ("wave", S.c("ben"))], moods=[("smile", 0)], kind="plain", seed=42, flip=True))
    S.text("Anna", 390, 1040, 64, INK, at=S.c("anna"))
    S.text("Ben", 1410, 1040, 64, INK, at=S.c("ben"))
    S.text("€200 / month · 7%", 740, 620, 66, GREY, at=S.c("€200") - 0.1)
    tx0, tx1, ty = 300, 1620, 260
    yx = lambda a: tx0 + (a - 25) / 40 * (tx1 - tx0)
    S.draw([stk(P_line(tx0 - 30, ty, tx1 + 30, ty, 0.005, 2), 5, GREY)], S.l(1) - 0.2, 0.3, snd=None)
    for a in (25, 35, 65):
        S.text(str(a), yx(a), ty + 70, 56, GREY, at=S.l(1), anchor="m")
    S.draw([stk(P_line(yx(25), ty - 40, yx(65), ty - 40, 0.005, 3), 14, ORANGE)], S.c("25", 1) - 0.1, 0.6)
    S.text("Anna", yx(25), ty - 70, 52, ORANGE, at=S.c("25", 1))
    S.draw([stk(P_line(yx(35), ty - 10, yx(65), ty - 10, 0.005, 4), 14, INK)], S.c("35", 1) - 0.1, 0.5)
    S.text("Ben", yx(35) + 10, ty + 140, 52, INK, at=S.c("35", 1))


@V.scene("c3b")
def _(S):
    base, sc = 900, 640 / 525
    S.draw([stk(P_line(200, base, 1500, base, 0.005, 1), 7)], 0.0, 0.3, snd=None)
    stacked(S, 300, base, 220, [72, 244 - 72], S.c("€72,000") - 0.1, sc, [PALE, (150, 186, 214)], ["put in: €72k", None],
            step=S.c("€244,000") - S.c("€72,000"))
    S.text("Ben", 410, base + 70, 64, INK, at=0.1, anchor="m")
    S.text("€244k", 410, base - 244 * sc - 30, 84, INK, at=S.c("€244,000") + 0.3, anchor="m")
    stacked(S, 900, base, 220, [96, 525 - 96], S.c("€24,000", 1) - 0.1, sc, [PALE, ORANGE], ["put in: €96k", None],
            step=S.c("€525,000", 1) - S.c("€24,000", 1))
    S.text("Anna", 1010, base + 70, 64, INK, at=S.l(1), anchor="m")
    S.text("€525k", 1010, base - 525 * sc - 30, 96, ORANGE, at=S.c("€525,000", 1) + 0.3, anchor="m")


@V.scene("c3c")
def _(S):
    S.text("+10 years", 240, 330, 140, INK, at=S.c("ten") - 0.1, rot=-3)
    S.text("= more than ×2", 300, 480, 110, ORANGE, at=S.c("doubled") - 0.2, rot=-3)
    S.draw(plant(1400, 760, 1.5, leaves=5), S.c("early") - 0.3, 0.6)
    S.text("start early", 240, 800, 110, INK, at=S.c("early") - 0.1)
    S.text(">", 820, 800, 130, ORANGE, at=S.c("beats") - 0.05)
    S.text("start big", 920, 800, 80, GREY, at=S.c("big") - 0.1)


# --------------------------------------------------------------------------- 4. the boring years
@V.scene("c4a")
def _(S):
    base, sc = 900, 560 / 35
    S.draw([stk(P_line(300, base, 900, base, 0.005, 1), 7)], 0.0, 0.3, snd=None)
    stacked(S, 480, base, 240, [24, 11], S.c("€35,000") - 0.2, sc, [PALE, ORANGE], ["put in €24k", "growth €11k"],
            step=S.c("€11,000", 1) - S.c("€35,000") + 0.1)
    S.text("10 years: €35k", 300, 230, 96, INK, at=S.c("€35,000") - 0.2)
    S.add(Fig(1550, 950, 1.2, at=0.0, poses=[("stand", 0), ("sad", S.c("nothing", 1) - 0.2)], moods=[("flat", 0), ("worried", S.c("nothing", 1))],
              seed=3, flip=True))
    S.text("...nothing?", 1330, 470, 84, GREY, at=S.c("nothing", 1), rot=5)


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
    S.text("put in each year: €2,400", X(19), Y(2400) + 60, 54, GREY, at=0.5)
    pts = np.array([(X(y), Y(g)) for y, g in zip(yrs, growth)])
    S.draw([stk(pts[:11], 9, INK)], 0.3, 0.6)
    S.text("growth each year", X(2), Y(2400) - 120, 56, INK, at=0.6)
    mx, my = X(11), Y(2400)
    S.add(circ(mx, my, 40, 40, S.c("11") - 0.05, ORANGE, 7))
    S.text("year 11", mx - 70, my - 70, 64, ORANGE, at=S.c("11"))
    S.text("growth > what she puts in", mx + 60, my - 160, 60, ORANGE, at=S.c("bigger") - 0.2)
    S.draw([stk(pts[10:], 10, ORANGE)], S.c("bends", 1) - 0.4, 0.9)
    for k in range(6):
        bx = x0 + 40 + k * 90
        S.draw([stk(P_rect(bx, y1 - 64, 84, 40, 3), 4.5, (170, 120, 90))], S.c("foundation", 1) - 0.3 + 0.06 * k, 0.15, snd=None)
    S.text("the foundation", x0 + 30, y1 + 70, 64, (150, 100, 70), at=S.c("foundation", 1))


# --------------------------------------------------------------------------- 5. it works against you too
@V.scene("c5a")
def _(S):
    S.draw(snowball(560, 650, 120), 0.1, 0.4, snd=None)
    S.text("for you", 470, 900, 76, GREEN, at=S.c("side") - 0.4)
    S.draw([stk(P_line(960, 300, 965, 900, 0.01, 2), 5, GREY)], 0.0, 0.3, snd=None)
    S.draw(snowball(1360, 650, 120, col=(244, 214, 210)), S.c("side") - 0.3, 0.4, snd=None)
    S.text("against you", 1220, 900, 76, RED, at=S.c("side") - 0.1)
    S.text("doesn't care.", 700, 220, 90, INK, at=S.c("care") - 0.2, rot=-3)
    S.draw(card(1500, 360, 0.9), S.c("credit", 1) - 0.2, 0.4)
    S.pop(tag(1680, 520, 0.9, "20%/yr", (244, 214, 210), 50), S.c("20%", 1) - 0.1, (1680, 520))


@V.scene("c5b")
def _(S):
    S.text("72 ÷ 20 = 3.6 years", 220, 300, 120, INK, at=S.c("20%") - 0.1, cps=16)
    S.text("to double a debt", 260, 420, 80, RED, at=S.c("doubles") - 0.1)
    for k, (x, r) in enumerate(((300, 40), (520, 70), (820, 110))):
        S.draw(snowball(x, 760 - r, r, col=(244, 214, 210)), S.c("doubles") + 0.2 * k, 0.3, snd="scr" if k == 2 else None)
    S.text("for the bank.", 980, 640, 80, GREY, at=S.c("bank") - 0.2)
    S.draw(card(1460, 520, 1.0), S.c("expensive", 1) - 0.6, 0.4)
    S.add(cross(1460, 520, 120, S.c("expensive", 1) + 0.2, RED, 11))
    S.text("pay it off first.", 1180, 860, 86, ORANGE, at=S.c("pay", 1) - 0.1, rot=-3)
    S.text("best return you'll ever get.", 940, 1000, 64, INK, at=S.c("best", 1) - 0.1)


# --------------------------------------------------------------------------- 6. fees compound too
@V.scene("c6a")
def _(S):
    S.text("1.8%", 300, 300, 60, INK, at=S.c("1.8%") - 0.1)
    S.text("tiny?", 480, 300, 60, GREY, at=S.c("tiny") - 0.1)
    S.text("1.8%", 200, 620, 260, RED, at=S.c("isn't") - 0.2, rot=-5, cps=10)
    S.add(*bars(960, 880, [235, 173], ["0.2% fees", "1.8% fees"], S.c("0.2%", 1) - 0.1, step=S.c("1.8%", 1) - S.c("0.2%", 1),
                maxh=560, bw=220, gap=200, cols=[ORANGE, (244, 214, 210)], txt=["€235k", "€173k"], seed=6, size=80))
    S.text("€200 / month · 30 years", 980, 160, 60, GREY, at=S.c("€200", 1))


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
    S.text("-€60,000+", 980, 560, 190, RED, at=S.c("€60,000") - 0.25, rot=-4, cps=12)
    S.text("every single year.", 1060, 760, 76, GREY, at=S.c("every") - 0.1)


# --------------------------------------------------------------------------- 7. inflation
@V.scene("c7a")
def _(S):
    S.draw(cart(420, 640, 1.1), 0.0, 0.5)
    S.pop(tag(440, 440, 0.9, "€1.00"), S.c("prices") - 0.05, (440, 440))
    S.pop(tag(700, 330, 0.9, "€1.02", HL), S.c("rise") + 0.1, (700, 330))
    S.text("ECB target: 2%", 220, 960, 76, INK, at=S.c("aims") - 0.2)
    nx, ny = 1350, 560

    def shrink(tt, t0=S.c("loses", 1) - S.c("2%", 1) + 0.0):
        u = clamp((tt - t0) / 1.6)
        return (0, 0, 0, 1.0 - 0.45 * ease_io(u))
    S.add(Dr(note(nx, ny, 2.2), S.c("2%", 1) - 0.1, 0.0, pop=True, anchor=(nx, ny), move=shrink, seed=77), snd="pop", at=S.c("2%", 1))
    S.text("€100 in cash", 1180, 300, 70, INK, at=S.c("cash", 1) - 0.1)
    S.text("30 years later: buys ~€55", 1060, 900, 70, RED, at=S.c("30", 1) - 0.1)


@V.scene("c7b")
def _(S):
    x0, y0, x1, y1 = 200, 200, 1720, 860
    axes(S, x0, y0, x1, y1, 0.0, "decades", None)
    rr = np.random.default_rng(3)
    steps = 90
    v = np.cumsum(rr.normal(0.05, 0.6, steps))
    v = np.cumsum(rr.normal(0.06, 0.55, steps))
    v[30:] -= 3.5
    v[33:] += 2.0
    v[60:] -= 3.0
    v[63:] += 1.6
    pts = np.stack([x0 + 30 + np.arange(steps) / (steps - 1) * (x1 - x0 - 80), y1 - 30 - (v - v.min()) / (v.max() - v.min()) * (y1 - y0 - 120)], 1)
    S.draw([stk(pts, 7, INK)], S.c("global") - 0.4, 1.2)
    S.text("global stocks: ~5% a year above inflation", 260, 170, 64, INK, at=S.c("5%") - 0.4)
    S.text("(average, 125 years)", 300, 250, 52, GREY, at=S.c("average") - 0.1)
    for k, j in enumerate((31, 61)):
        px, py = pts[j]
        S.add(circ(px, py + 20, 60, 70, S.c("terrible", 1) + 0.2 * k, RED, 6))
    S.text("terrible years", pts[31][0] - 120, 960, 56, RED, at=S.c("terrible", 1) + 0.1)
    S.text("time did the heavy lifting.", 1100, 1020, 70, ORANGE, at=S.c("heavy", 1) - 0.3, rot=-2)


# --------------------------------------------------------------------------- final message
@V.scene("f0")
def _(S):
    S.text("final message.", 260, 600, 120, INK, at=0.05, rot=-3, cps=20)
    S.add(under(270, 980, 640, 1.0, ORANGE, 7, 0.4, wavy=True))


@V.scene("f1")
def _(S):
    S.text("magic", 300, 420, 140, INK, at=S.c("magic") - 0.3)
    S.add(strike(280, 380, 740, 372, S.c("magic") + 0.4, RED, 10))
    S.text("patience", 360, 720, 170, ORANGE, at=S.c("patience") - 0.2, rot=-3)
    S.text("(written in maths)", 420, 840, 66, GREY, at=S.c("maths") - 0.3)
    S.draw(clock(1450, 560, 1.6), S.c("patience") - 0.4, 0.5)


@V.scene("f2")
def _(S):
    items = (("early", "start early"), ("small", "start small if needed"), ("fees", "keep fees low"), ("kill", "kill expensive debt"))
    for k, (w_, lab) in enumerate(items):
        y = 300 + k * 170
        at = S.c(w_) - 0.25
        S.text(lab, 300, y, 96, INK, at=at)
        S.add(check(220, y - 32, 30, at + 0.5, GREEN, 10, seed=k))
    S.draw(snowball(1500, 640, 150), 0.2, 0.5, snd=None)


@V.scene("f3")
def _(S):
    S.add(Fig(620, 950, 1.3, at=0.0, poses=[("sit", 0)], moods=[("smile", 0), ("sleep", S.c("nothing") + 0.2)], seed=3, idle=0.4))
    S.draw([stk(P_rect(470, 790, 270, 26, 5, r=8), 7), stk(P_line(490, 816, 490, 950, 0, 1), 7), stk(P_line(720, 816, 720, 950, 0, 2), 7),
            stk(P_line(476, 792, 450, 520, 0.02, 3), 7)], 0.0, 0.4, snd=None)
    S.draw(plant(1600, 900, 1.0, leaves=2), 0.2, 0.4, snd=None, until=S.c("long") - 0.2)
    S.draw(plant(1600, 900, 1.9, leaves=6), S.c("long") - 0.2, 0.7)
    S.text("do nothing.", 760, 250, 130, ORANGE, at=S.c("nothing") - 0.2, rot=-4)
    S.text("for a very long time.", 800, 370, 70, GREY, at=S.c("long") - 0.3)


@V.scene("end")
def _(S):
    S.text("not financial advice. examples, not promises.", 200, 200, 56, GREY, at=S.c("education") - 0.2)
    sx, sy = 520, 600
    S.draw([Fl(P_rect(sx - 220, sy - 70, 440, 140, 0, r=26), ORANGE), stk(P_rect(sx - 220, sy - 70, 440, 140, 8, r=26), 7)], S.c("subscribe") - 0.3, 0.4)
    S.text("subscribe", sx, sy + 26, 92, INK, at=S.c("subscribe") - 0.1, anchor="m")
    vx, vy = 1350, 560
    S.draw([stk(P_rect(vx - 330, vy - 190, 660, 380, 8, r=12), 7)], S.c("next") - 0.2, 0.45)
    S.text("next:", vx - 320, vy - 220, 70, GREY, at=S.c("next") - 0.1)
    S.text("save money so easily\nit feels illegal.", vx, vy - 20, 70, INK, at=S.c("save") - 0.1, anchor="m")
    S.add(Fig(820, 980, 0.95, at=0.0, poses=[("stand", 0), ("point_r", S.c("next") + 0.1)], moods=[("smile", 0), ("happy", S.c("subscribe"))], seed=3))


if __name__ == "__main__":
    V.main()
