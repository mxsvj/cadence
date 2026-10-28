"""'The Minimum Payment Trap (and How to Escape It)' (doodle style). Sources in the kit: Gal & McShane (2012, JMR), Kettle, Trudel,
Blanchard & Häubl (2016, JCR). Payoff example: €3,000 at 20% a year, interest monthly (hypothetical); debts table, avalanche vs snowball
and consolidation figures are worked examples (see the kit notes)."""
import numpy as np

from doodle_video import *  # noqa: F401,F403

SAY = {"10%": "ten percent", "€600": "six hundred euros", "€300": "three hundred euros", "€3,000": "three thousand euros", "20%": "twenty percent",
       "€60": "sixty euros", "€3,500": "three thousand five hundred euros", "€150": "a hundred and fifty euros", "€680": "six hundred and eighty euros",
       "€500": "five hundred euros", "2%": "two percent", "€80": "eighty euros", "€11,000": "eleven thousand euros"}
V = Video("debt", say=SAY, seed=31, keys=dict(prog=[(57, 60, 64, 67), (55, 59, 62, 65), (53, 57, 60, 64), (52, 55, 59, 64)],
                                              roots=[45, 43, 41, 40], bpm=78),
          hush=(), tape="Final message", beat_groups=(),
          keep=["small accounts", "doesn't go straight back", "the rates are similar", "your card app"])
L = V.L

L("o1", "The minimum payment is the most expensive button in your card app.")
L("o1", "Pay only that on a €3,000 card, and it takes about nine years. Here are six steps out.")

L("c1", "One. Put it all on one page.")
L("c1a", "Write down every debt: how much you owe, the interest rate, and the minimum payment.")
L("c1b", "Include everything: cards, store credit, buy now pay later, car loans, even money you owe friends.")
L("c1c", "Most people have never seen the total in one place. It's scary for ten minutes. Then it's a plan.")
L("c1d", "And if it feels like too much, free debt advice exists in most countries. Use it.")

L("c2", "Two. Escape the minimum payment.")
L("c2a", "Back to that €3,000 card, at 20% a year. At a fixed €60 a month, you pay around €3,500 in interest. More than the debt itself.")
L("c2x", "And many real minimums are just a slice of what you owe, like 2%. As the debt shrinks, the payment shrinks too. "
         "Pay only that, and the same card can take over thirty years, and about €11,000 in interest.")
L("c2x", "The rules vary by country, so check yours.")
L("c2b", "At €150 a month, it's about €680 of interest, and two years instead of nine.")
L("c2b", "Same debt. Same rate. Seven years of your life back.")

L("c3", "Three. Pick an order.")
L("c3a", "The avalanche: pay the minimum on everything, and throw every extra euro at the highest interest rate first. Mathematically, it saves the most.")
L("c3a", "The snowball: smallest balance first. You close accounts quickly, and each win keeps you going.")
L("c3b", "Say you have €300 a month for all three. The avalanche saves about €80 in interest. "
         "The snowball clears its first debt in five months, instead of twelve. Both are done in about two years.")
L("c3c", "In one study of about six thousand people in a debt programme, those who cleared small accounts first were more likely to clear all of their debt.")
L("c3c", "So if the rates are similar, start small. If one rate is much higher, like this card, kill that one first.")

L("c4", "Four. One debt at a time.")
L("c4a", "Spreading your extra money thinly across every debt feels fair. But then nothing seems to move.")
L("c4a", "Researchers found that people who focused their repayments on one account at a time felt more progress, and paid more aggressively.")
L("c4b", "When one is gone, roll its whole payment into the next. Every payoff makes the next one faster.")

L("c5", "Five. Make the interest smaller.")
L("c5a", "Ask your lender for a lower rate. It doesn't always work, but it costs nothing to ask.")
L("c5c", "A consolidation loan can help too, but only if you stop using the old cards. "
         "And check the total cost: a longer loan can cost more overall, even at a lower rate.")
L("c5b", "Even a few points matter. On €3,000, going from 20% to 10% cuts the interest from about €600 a year to about €300.")

L("c6", "Six. Don't refill the card.")
L("c6a", "Keep a small emergency fund, even €500, so the next surprise doesn't go straight back on the card.")
L("c6a", "And when your last debt is gone, keep paying the same amount, into your savings.")
L("c6b", "And keep it visible: a list on the fridge, crossed out one line at a time.")

L("f0", "Final message.")
L("f1", "Debt isn't a character flaw. It's a maths problem, and maths problems can be solved.")
L("f2", "List it. Pay more than the minimum. Pick an order. One at a time. Lower the rate. Don't refill it.")
L("f2", "That's the whole plan. Screenshot it, and stick it on the fridge.")
L("end", "This is education, not financial advice. If debt feels unmanageable, many countries have free debt advice services. "
         "So: which debt are you killing first? Tell me in the comments.")

# the three debts used from step 1 on: the highest rate and the smallest balance are different debts, so the two orders really differ
DEBTS = [("store credit", 800, 9, 25), ("card", 2200, 21, 45), ("car loan", 3500, 7, 60)]


def boulder(x, y, r, col=(244, 214, 210), label="DEBT"):
    o = [Fl(P_ell(x, y, r, r * 0.9, 1, closed=True), col), stk(P_ell(x, y, r, r * 0.9, 3, 0.08), 8)]
    for k, (a, b2) in enumerate(((-0.4, -0.3), (0.3, 0.2), (-0.1, 0.45))):
        o.append(stk(P_arc(x + a * r, y + b2 * r, r * 0.16, r * 0.1, 200, 330, 12), 4, GREY))
    o.append(("g", label, x, y + r * 0.18, int(r * 0.5), INK, HAND, "m"))
    return o


def bank(x, y, s=1.0):
    """A lender: roof, four columns, steps."""
    w = 380 * s
    o = [Fl(P_poly([(x - w / 2 - 20 * s, y - 150 * s), (x, y - 290 * s), (x + w / 2 + 20 * s, y - 150 * s)], True), (236, 228, 214)),
         stk(P_poly([(x - w / 2 - 20 * s, y - 150 * s), (x, y - 290 * s), (x + w / 2 + 20 * s, y - 150 * s)], True), 7 * s),
         stk(P_rect(x - w / 2, y + 140 * s, w, 34 * s, 6 * s), 6.5 * s), stk(P_line(x - w / 2, y - 150 * s, x + w / 2, y - 150 * s, 0.01, 1), 6.5 * s)]
    for k in range(4):
        cx = x - w / 2 + 50 * s + k * (w - 100 * s) / 3
        o.append(stk(P_rect(cx - 18 * s, y - 130 * s, 36 * s, 265 * s, 5 * s), 5.5 * s))
    o.append(("g", "€", x, y - 175 * s, int(80 * s), INK, HAND, "m"))
    return o


def table(S, x, y, rows, at_cols, cols=("debt", "owe", "rate", "min"), names_at=0.3):
    """Debt names first (the voice says 'every debt'), then one column per cue word: owe, rate, minimum."""
    cw = [450, 290, 210, 190]
    S.draw([stk(P_line(x, y + 26, x + sum(cw), y + 26, 0.005, 1), 5)], names_at - 0.2, 0.3, snd=None)
    S.text(cols[0], x + 10, y, 72, GREY, at=names_at - 0.2)
    for r_, row in enumerate(rows):
        S.text(row[0], x + 10, y + 125 + r_ * 118, 74, INK, at=names_at + 0.15 * r_)
    cx = x + cw[0]
    for k in range(1, len(cols)):
        at = at_cols[k - 1]
        S.text(cols[k], cx + 10, y, 72, GREY, at=at - 0.1)
        for r_, row in enumerate(rows):
            S.text(row[k], cx + 10, y + 125 + r_ * 118, 74, RED if row[k] == "21%" else INK, at=at + 0.08 * r_)
        cx += cw[k]


def lbars(S, x0, ybase, vals, labels, at, lab_size=66, **kw):
    """The engine's bars with bigger labels under them (its own labels are 52 px)."""
    import doodle as _dd
    S.add(*bars(x0, ybase, vals, [""] * len(vals), at, **kw))
    if _dd.REG is not None:
        _dd.REG[:] = [r for r in _dd.REG if r["text"].strip()]
    bw, gap, step = kw.get("bw", 150), kw.get("gap", 90), kw.get("step", 0.35)
    for k, lab in enumerate(labels):
        S.text(lab, x0 + k * (bw + gap) + bw / 2, ybase + 72, lab_size, INK, at=at + 0.25 + k * step, anchor="m")


# --------------------------------------------------------------------------- cold open
@V.scene("o1")
def _(S):
    S.noframe = True
    px, py = 400, 540                        # frame 0 is the thumbnail (D2): phone, button, arrow and headline already there
    S.draw(phone(px, py, 2.3), -1.0, 0.0, snd=None)
    S.text("card app", px, py - 250, 72, GREY, at=-3.0, anchor="m")
    S.draw([Fl(P_rect(px - 165, py - 20, 330, 190, 0, r=34), ORANGE), stk(P_rect(px - 165, py - 20, 330, 190, 7, r=34), 7)], -1.0, 0.0, snd=None)
    S.text("PAY\nMINIMUM", px, py + 60, 78, INK, at=-3.0, anchor="m", lh=1.0)
    S.text("the most expensive", 720, 250, 100, INK, at=-3.0)
    S.text("button.", 740, 370, 120, RED, at=-3.0, rot=-2)
    S.add(arrow(P_bez((720, 330), (640, 420), (590, 520)), -1.0, RED, 8, 0.0))
    S.text("minimum only,", 720, 540, 76, INK, at=S.c("only", 1) - 0.2)            # said first: "pay only that on a €3,000 card"
    S.text("on €3,000:", 720, 650, 84, INK, at=S.c("€3,000", 1) - 0.2)
    S.draw([stk(P_line(720, 700, 720 + 9 * 110, 700, 0.005, 1), 24, (226, 150, 138))], S.c("nine", 1) - 0.6, 0.6, snd=None)
    S.text("9 years", 720 + 9 * 110, 655, 110, RED, at=S.c("nine", 1) - 0.25, anchor="r", rot=-2)
    S.text("6 steps out.", 720, 840, 100, ORANGE, at=S.c("six", 1) - 0.2, rot=-2)


V.chapters({1: ("Put it all\non one page.", 0), 2: ("Escape the\nminimum payment.", 1), 3: ("Pick an\norder.", 0), 4: ("One debt\nat a time.", 1),
            5: ("Make the interest\nsmaller.", 0), 6: ("Don't refill\nthe card.", 1)}, peek=())


# --------------------------------------------------------------------------- steps
@V.scene("c1a")
def _(S):
    rows = [(n, f"€{b:,}", f"{r}%", f"€{m}") for n, b, r, m in DEBTS]
    table(S, 180, 400, rows, [S.c("owe") - 0.2, S.c("rate") - 0.1, S.c("minimum") - 0.1], names_at=0.35)
    S.text("write it all down.", 200, 220, 96, ORANGE, at=0.05, rot=-2)
    S.add(Fig(1680, 880, 1.05, at=0.0, poses=[("think", 0)], moods=[("worried", 0)], seed=3, flip=True))


@V.scene("c1b")
def _(S):
    icons = ((0.3, card(290, 400, 0.85), "cards"), (S.c("store"), cart(690, 420, 0.65), "store credit"),
             (S.c("buy"), phone(1090, 400, 0.75), "pay later"), (S.c("car"), car(1490, 420, 0.62), "car loan"))
    for k, (at, ops, lab) in enumerate(icons):
        if k == 2:
            ops = ops + [("g", "4×", 1090, 420, 64, INK, HAND, "m")]
        S.draw(ops, at - 0.15, 0.35, snd="scr" if k in (0, 2) else None)
        S.text(lab, [290, 690, 1090, 1490][k], 660, 68, INK, at=max(at, S.c("cards")) if k == 0 else at, anchor="m")
    S.add(Fig(760, 1000, 0.75, at=S.c("owe") - 0.4, poses=[("hips", 0)], moods=[("smug", 0)], kind="spiky", seed=55, enter="pop"))
    S.draw(bubble(1160, 830, 560, 130, tail=(-1, 1)), S.c("owe") - 0.2, 0.25, snd=None)
    S.text("\"you owe me €50\"", 1160, 852, 64, INK, at=S.c("owe"), anchor="m")
    S.text("everything.", 220, 210, 120, ORANGE, at=0.05, rot=-3)


@V.scene("c1c")
def _(S):
    S.noframe = True
    px, py = 180, 170                         # the one page: one line per debt
    S.draw([Fl(P_rect(px, py, 460, 600, 0, r=8), (250, 248, 242)), stk(P_rect(px, py, 460, 600, 7, r=8), 6)], 0.0, 0.35)
    for k, (n, b, r, m) in enumerate(DEBTS):
        S.text(f"€{b:,}", px + 50, py + 150 + k * 135, 92, INK, at=0.3 + 0.2 * k)
    S.draw([stk(P_line(px + 40, py + 500, px + 420, py + 500, 0.01, 4), 6)], 0.9, 0.2, snd=None)
    S.text("total:", 760, 290, 110, INK, at=S.c("total") - 0.4)
    S.text("€6,500", 760, 500, 200, RED, at=S.c("total") + 0.1, rot=-3, cps=12)
    S.text("scary for 10 minutes.", 760, 680, 92, INK, at=S.c("scary") - 0.2)
    S.text("then: a plan.", 760, 830, 130, ORANGE, at=S.c("plan") - 0.3, rot=-2)


@V.scene("c1d")
def _(S):
    S.add(Fig(1480, 940, 1.2, at=0.0, poses=[("sad", 0), ("stand", S.c("free")), ("wave", S.c("use"))], moods=[("worried", 0), ("smile", S.c("free"))],
              seed=8))
    S.text("too much?", 200, 300, 110, INK, at=0.05)
    S.draw(phone(1180, 520, 0.9), 0.4, 0.3, snd=None)
    S.draw(bubble(1180, 300, 300, 120, tail=(-1, 1)), S.c("advice") - 0.3, 0.25, snd=None)
    S.text("help", 1180, 322, 76, INK, at=S.c("advice") - 0.1, anchor="m")
    S.text("free debt advice", 200, 540, 110, GREEN, at=S.c("free") - 0.1)
    S.text("exists. use it.", 220, 720, 110, GREEN, at=S.c("exists") - 0.1, rot=-2)


@V.scene("c2a")
def _(S):
    S.draw(card(360, 250, 1.1), 0.0, 0.35)
    S.text("€3,000 at 20%", 200, 480, 100, INK, at=S.c("€3,000") - 0.2)
    S.text("fixed €60 a month", 200, 620, 86, INK, at=S.c("€60") - 0.2)
    S.text("= 9 years", 200, 740, 86, RED, at=S.c("€60") + 0.5)
    lbars(S, 980, 760, [3000, 3500], ["the debt", "interest"], S.c("€3,500") - 0.45, step=0.4, maxh=360, bw=200, gap=110,
          cols=[PALE, (226, 150, 138)], txt=["€3,000", "€3,500"], seed=41, size=72)
    S.text("interest > debt", 960, 240, 88, RED, at=S.c("more") - 0.15, rot=-2)


@V.scene("c2x")
def _(S):
    S.draw([stk(P_line(140, 820, 1800, 820, 0.005, 1), 6)], 0.0, 0.3, snd=None)
    S.add(Fig(500, 820, 0.75, at=0.0, poses=[("stand", 0)], moods=[("worried", 0), ("sad", S.c("thirty"))], seed=3,
              walk=(380, 820, 0.2, S.c("thirty"))))
    fx0, fx1 = 1100, 1650

    def drift(tt, t0=S.c("shrinks", 0, 1)):
        u = clamp((tt - t0) / 1.6)
        return ((fx1 - fx0) * ease_io(u), 0, 0, 1)
    S.add(Dr([stk(P_line(fx0, 820, fx0, 560, 0.01, 2), 7), Fl(P_poly([(fx0, 560), (fx0 + 120, 600), (fx0, 640)], True), RED),
              stk(P_poly([(fx0, 560), (fx0 + 120, 600), (fx0, 640)], True), 5)], 0.1, 0.0, anchor=(fx0, 820), move=drift, seed=9))
    S.text("minimum = 2% of what you owe", 200, 190, 80, INK, at=0.3)
    S.text("debt shrinks, payment shrinks.", 220, 300, 72, INK, at=S.c("shrinks") - 0.2)
    S.text("30+ years", 1250, 430, 130, RED, at=S.c("thirty") - 0.2, rot=-3, cps=14)
    S.text("~€11,000 interest", 1260, 520, 72, RED, at=S.c("€11,000") - 0.2)
    S.text("rules vary by country:", 200, 440, 76, INK, at=S.c("rules", 1) - 0.1)
    S.text("check yours.", 220, 530, 76, INK, at=S.c("check", 1) - 0.1)


@V.scene("c2b")
def _(S):
    S.text("€60 a month", 200, 280, 86, INK, at=0.05)
    S.draw([stk(P_line(200, 340, 200 + 9 * 150, 340, 0.005, 1), 24, (226, 150, 138))], 0.15, 0.5, snd=None)
    S.text("9 years · €3,500 interest", 220, 430, 72, INK, at=0.35)
    S.text("€150 a month", 200, 590, 100, INK, at=S.c("€150") - 0.2)
    S.draw([stk(P_line(200, 650, 200 + 2 * 150, 650, 0.005, 2), 24, GREEN)], S.c("two") - 0.3, 0.4)
    S.text("2 years · €680 interest", 220, 750, 76, INK, at=S.c("€680") - 0.2)
    S.text("7 years\nback.", 1120, 600, 150, ORANGE, at=S.c("seven", 1) - 0.2, rot=-4, cps=14, lh=1.0)


@V.scene("c3a")
def _(S):
    rate = sorted(DEBTS, key=lambda d: -d[2])
    bal = sorted(DEBTS, key=lambda d: d[1])
    short = {"store credit": "store", "card": "card", "car loan": "loan"}
    t_av = S.c("avalanche") + 0.3
    S.text("avalanche", 200, 210, 110, INK, at=S.c("avalanche") - 0.2)
    for k, (n, b, r, m) in enumerate(rate):
        y = 290 + k * 110
        w = 330 * r / 21
        S.text(short[n], 200, y + 66, 66, INK, at=t_av + 0.1 * k)
        S.draw([Fl(P_rect(380, y, w, 84, 0, r=10), PALE), stk(P_rect(380, y, w, 84, 5, r=10), 5)], t_av + 0.1 * k, 0.25, snd="scr" if k == 0 else None)
        S.text(f"{r}%", 380 + w + 22, y + 66, 70, RED if k == 0 else INK, at=t_av + 0.15 + 0.1 * k)
    S.text("min on all", 200, 680, 70, INK, at=S.c("minimum") - 0.1, until=S.c("mathematically") - 0.3)
    S.text("+ every extra €", 200, 760, 70, INK, at=S.c("extra") - 0.1)
    S.draw([Fl(P_rect(380, 290, 330, 84, 0, r=10), (226, 150, 138)), stk(P_rect(380, 290, 330, 84, 6, r=10), 6)], S.c("highest") - 0.1, 0.25)
    S.add(arrow(P_line(880, 240, 810, 300, 0.02, 1), S.c("highest") + 0.3, RED, 7, 0.25))
    S.text("= the card first", 200, 840, 76, RED, at=S.c("first") - 0.1)
    S.text("saves the most", 200, 680, 70, GREEN, at=S.c("mathematically") - 0.05)
    S.draw([stk(P_line(980, 180, 985, 900, 0.01, 2), 5, GREY)], S.l(1) - 0.3, 0.3, snd=None)
    t_sb = S.c("snowball", 1) + 0.3
    S.text("snowball", 1060, 210, 110, INK, at=S.c("snowball", 1) - 0.2)
    for k, (n, b, r, m) in enumerate(bal):
        y = 290 + k * 110
        w = 300 * b / 3500
        S.text(short[n], 1060, y + 66, 66, INK, at=t_sb + 0.1 * k)
        S.draw([Fl(P_rect(1240, y, w, 84, 0, r=10), PALE), stk(P_rect(1240, y, w, 84, 5, r=10), 5)], t_sb + 0.1 * k, 0.25, snd=None)
        S.text(f"€{b:,}", 1240 + w + 22, y + 66, 70, INK, at=t_sb + 0.15 + 0.1 * k)
    S.draw([Fl(P_rect(1240, 290, 300 * 800 / 3500, 84, 0, r=10), HL), stk(P_rect(1240, 290, 300 * 800 / 3500, 84, 6, r=10), 6)],
           S.c("smallest", 1) - 0.1, 0.25, snd=None)
    S.add(check(1525, 325, 30, S.c("close", 1), GREEN, 10))
    S.text("= the store credit first", 1060, 680, 70, ORANGE, at=S.c("smallest", 1) + 0.4)
    S.text("quick wins", 1060, 780, 76, INK, at=S.c("win", 1) - 0.1)


@V.scene("c3b")
def _(S):
    S.text("€300 a month", 200, 220, 100, INK, at=0.05)
    for k in range(3):
        S.draw(coin(880 + k * 95, 186, 0.6, col=HL), 0.25 + 0.12 * k, 0.15, snd="pop" if k == 0 else None)
    S.draw([stk(P_line(960, 300, 965, 790, 0.01, 2), 5, GREY)], 0.4, 0.3, snd=None)
    S.text("avalanche", 200, 370, 96, INK, at=0.6)
    S.text("snowball", 1060, 370, 96, INK, at=0.8)
    S.text("interest: ~€670", 200, 480, 80, INK, at=S.c("saves") - 0.2)
    S.text("interest: ~€750", 1060, 480, 80, INK, at=S.c("saves") + 0.4)
    S.text("saves ~€80", 220, 620, 110, GREEN, at=S.c("€80") - 0.1, rot=-2)
    S.text("first payoff: month 12", 200, 740, 72, INK, at=S.c("first") - 0.2)
    S.text("first payoff: month 5", 1060, 740, 72, INK, at=S.c("five") - 0.2)
    S.text("faster win", 1080, 620, 110, ORANGE, at=S.c("five") + 0.6, rot=-2)
    S.text("both done in ~2 years", 960, 860, 80, INK, at=S.c("both") - 0.1, anchor="m")


@V.scene("c3c")
def _(S):
    S.text("one study:", 200, 230, 90, INK, at=0.05)
    for k in range(18):                      # a crowd of tiny people
        x, y = 1160 + (k % 6) * 105, 250 + (k // 6) * 120
        S.draw([stk(P_ell(x, y, 20, 20, 3, 0.1), 4.5), stk(P_line(x, y + 20, x, y + 62, 0.02, k), 4.5),
                stk(P_poly([(x - 20, y + 86), (x, y + 62), (x + 20, y + 86)]), 4.5)], 0.15 + 0.04 * k, 0.15, snd="scr" if k == 0 else None)
    S.text("~6,000 people", 600, 230, 96, INK, at=S.c("six") - 0.1)
    S.text("small ones cleared first", 200, 380, 76, INK, at=S.c("small") - 0.2)
    S.text("= more likely to clear it all", 200, 500, 82, INK, at=S.c("likely") - 0.2)
    S.text("rates similar?", 200, 680, 82, INK, at=S.c("similar", 1) - 0.2)
    S.text("start small.", 780, 680, 92, ORANGE, at=S.c("start", 1) - 0.1)
    S.text("one much higher?", 200, 820, 82, INK, at=S.c("higher", 1) - 0.4)
    S.text("kill it first.", 880, 820, 92, RED, at=S.c("kill", 1) - 0.1)
    S.draw(card(1560, 720, 0.95, col=(244, 214, 210)) + [("g", "21%", 1590, 745, 72, RED, HAND, "m")], S.c("card", 1) - 0.3, 0.35)


@V.scene("c4a")
def _(S):
    for k in range(4):
        x = 250 + k * 190
        S.draw(jar(x, 440, 0.85, fill_u=0.3, col=HL), 0.1 + 0.08 * k, 0.3, snd="scr" if k == 0 else None)
        S.text("€", x, 470, 64, INK, at=0.4 + 0.08 * k, anchor="m")
    S.text("spread thin", 220, 690, 92, INK, at=S.c("spreading") - 0.1)
    S.text("nothing moves.", 240, 820, 84, RED, at=S.c("nothing") - 0.2)
    S.draw([stk(P_line(1000, 200, 1005, 870, 0.01, 2), 5, GREY)], S.l(1) - 0.3, 0.3, snd=None)
    S.text("researchers:", 1110, 190, 72, INK, at=S.c("researchers", 1) - 0.1)
    S.draw(jar(1180, 440, 0.85, fill_u=0.95, col=ORANGE), S.c("focused", 1) - 0.2, 0.35)
    for k in range(3):
        S.draw(jar(1370 + k * 170, 440, 0.85, fill_u=0.08, col=HL), S.c("focused", 1) + 0.1 * k, 0.25, snd=None)
    S.add(check(1180, 265, 34, S.c("progress", 1) - 0.1, GREEN, 11))
    S.text("one at a time", 1110, 670, 92, INK, at=S.c("one", 1) - 0.1)
    S.text("felt more progress,", 1110, 760, 68, INK, at=S.c("progress", 1) - 0.3)
    S.text("paid more aggressively.", 1110, 845, 68, INK, at=S.c("aggressively", 1) - 0.5)


@V.scene("c4b")
def _(S):
    xs = (420, 900, 1380)
    for k, x in enumerate(xs):
        S.draw(jar(x, 520, 1.0, fill_u=0.0), 0.05 + 0.1 * k, 0.3, snd="scr" if k == 0 else None)
    S.add(check(xs[0], 520, 40, S.c("gone") - 0.1, GREEN, 12))
    S.add(arrow(P_bez((520, 380), (650, 300), (790, 380)), S.c("roll") - 0.1, INK, 7, 0.35))
    S.text("roll the whole payment", 200, 210, 92, INK, at=0.05)
    S.draw(jar(xs[1], 520, 1.0, fill_u=0.6, col=HL), S.c("payment") - 0.2, 0.3, snd=None)
    S.add(arrow(P_bez((1000, 380), (1130, 300), (1270, 380)), S.c("payoff") - 0.2, INK, 7, 0.35))
    S.draw(jar(xs[2], 520, 1.0, fill_u=0.9, col=HL), S.c("faster") - 0.4, 0.3, snd=None)
    S.text("each payoff: faster", 200, 820, 96, ORANGE, at=S.c("faster") - 0.3, rot=-2)


@V.scene("c5a")
def _(S):
    S.draw(phone(420, 540, 1.4), 0.0, 0.4)
    S.text("lender", 420, 470, 64, INK, at=0.2, anchor="m")
    S.draw(bubble(960, 300, 520, 160, tail=(-1, 1)), S.c("lower") - 0.6, 0.3, snd=None)
    S.text("lower rate?", 960, 330, 84, INK, at=S.c("lower") - 0.1, anchor="m")
    S.text("not always yes.", 760, 560, 80, INK, at=S.c("always") - 0.2)
    S.text("free to ask.", 760, 700, 96, GREEN, at=S.c("nothing") - 0.2, rot=-2)
    S.add(Fig(1560, 940, 1.1, at=0.0, poses=[("hold_r", 0)], moods=[("smile", 0), ("worried", S.c("always")), ("smile", S.c("nothing"))], seed=3, flip=True))


@V.scene("c5c")
def _(S):
    for k, x in enumerate((240, 400, 560)):
        S.draw(card(x, 280 + k * 34, 0.6), 0.05 + 0.12 * k, 0.25, snd="scr" if k == 0 else None)
    S.add(arrow(P_bez((680, 330), (760, 330), (820, 330)), S.c("loan") - 0.1, INK, 6, 0.3))
    lab = "one cheaper loan"
    bw_ = text_w(lab, 66) + 90
    S.draw([Fl(P_rect(850, 255, bw_, 150, 0, r=16), (214, 226, 196)), stk(P_rect(850, 255, bw_, 150, 6, r=16), 6)], S.c("loan") + 0.1, 0.3)
    S.text(lab, 850 + bw_ / 2, 352, 66, INK, at=S.c("loan") + 0.25, anchor="m")
    S.text("only if the old cards stop.", 200, 560, 80, RED, at=S.c("stop") - 0.3)
    S.text("check the total cost:", 200, 700, 80, INK, at=S.c("total") - 0.3)
    S.text("interest on €6,500:", 1120, 500, 66, INK, at=S.c("longer") - 0.4)
    lbars(S, 1120, 760, [1272, 1936], ["3 yrs · 12%", "6 yrs · 9%"], S.c("longer") - 0.2, step=0.5, maxh=150, bw=210, gap=170,
          cols=[(214, 226, 196), (244, 214, 210)], txt=["€1,272", "€1,936"], seed=77, size=70, lab_size=70)
    S.text("longer can cost more.", 200, 840, 84, RED, at=S.c("overall") - 0.3, rot=-2)


@V.scene("c5b")
def _(S):
    S.draw(card(1450, 250, 0.9, col=(226, 150, 138)), 0.0, 0.3, snd=None)
    S.text("20%", 200, 360, 200, RED, at=0.05, cps=12)
    S.add(arrow(P_line(560, 290, 740, 290, 0.02, 3), 0.55, INK, 10, 0.3, head=36))
    S.text("10%", 790, 360, 200, GREEN, at=0.75, cps=12)
    S.text("on €3,000:", 200, 560, 92, INK, at=S.c("€3,000") - 0.1)
    lbars(S, 1250, 760, [600, 300], ["at 20%", "at 10%"], S.c("€600") - 0.2, step=S.c("€300") - S.c("€600"), maxh=320, bw=200, gap=140,
          cols=[(226, 150, 138), (214, 226, 196)], txt=["€600/yr", "€300/yr"], seed=51, size=76, lab_size=70)
    S.text("half the interest.", 200, 760, 104, ORANGE, at=S.c("€300") + 0.3, rot=-3)


@V.scene("c6a")
def _(S):
    S.text("emergency fund", 200, 220, 92, INK, at=0.05)
    S.draw(jar(430, 520, 1.7, fill_u=0.6, col=(150, 186, 214)), 0.15, 0.45)
    S.text("€500", 430, 560, 96, INK, at=S.c("€500") - 0.1, anchor="m")
    S.draw(card(800, 700, 0.7), S.c("card") - 0.4, 0.3, snd=None)
    S.text("stays at €0", 560, 840, 76, INK, at=S.c("card") - 0.2)
    S.draw([stk(P_line(1040, 180, 1045, 900, 0.01, 2), 5, GREY)], S.l(1) - 0.3, 0.3, snd=None)
    for k, (n, b, r, m) in enumerate(DEBTS):
        y = 280 + k * 100
        S.text(n, 1120, y, 70, INK, at=S.c("last", 1) - 0.3 + 0.1 * k)
        S.add(strike(1110, y - 22, 1130 + text_w(n, 70), y - 30, S.c("gone", 1) + 0.15 * k, RED, 7, seed=k))
    S.add(arrow(P_bez((1300, 540), (1310, 610), (1330, 660)), S.c("paying", 1), INK, 7, 0.3))
    S.text("same amount,", 1120, 740, 80, ORANGE, at=S.c("same", 1) - 0.1)
    S.text("into savings.", 1140, 850, 80, ORANGE, at=S.c("savings", 1) - 0.3)
    S.draw(piggy(1690, 600, 0.65), S.c("savings", 1) - 0.1, 0.4)


@V.scene("c6b")
def _(S):
    fx, fy = 640, 560
    S.draw([Fl(P_rect(fx - 260, fy - 420, 520, 880, 0, r=30), (236, 240, 246)), stk(P_rect(fx - 260, fy - 420, 520, 880, 8, r=30), 8),
            stk(P_line(fx - 260, fy - 120, fx + 260, fy - 120, 0.01, 1), 6), stk(P_line(fx + 200, fy - 360, fx + 200, fy - 220, 0.01, 2), 8),
            stk(P_line(fx + 200, fy - 60, fx + 200, fy + 120, 0.01, 3), 8)], 0.0, 0.5)
    S.draw([Fl(P_rect(fx - 160, fy - 40, 260, 340, 0), (250, 248, 242)), stk(P_rect(fx - 160, fy - 40, 260, 340, 6), 5)], S.c("list") - 0.3, 0.4)
    for k in range(4):
        y = fy + 30 + k * 70
        S.draw([stk(P_line(fx - 130, y, fx + 60, y, 0.02, k), 4.5, GREY)], S.c("list") + 0.1 * k, 0.15, snd=None)
        if k < 3:
            S.add(strike(fx - 140, y + 4, fx + 75, y - 4, S.c("crossed") + 0.3 * k, RED, 6, seed=k))
    S.text("keep it visible.", 1060, 420, 110, ORANGE, at=S.c("visible") - 0.2, rot=-3)
    S.text("one line at a time.", 1080, 620, 86, INK, at=S.c("line") - 0.2)


@V.scene("f0")
def _(S):
    S.text("final message.", 260, 600, 130, INK, at=0.05, rot=-3, cps=20)
    S.add(under(270, 1040, 640, 1.0, ORANGE, 7, 0.4, wavy=True))


@V.scene("f1")
def _(S):
    S.text("a character flaw", 220, 330, 124, INK, at=0.05)
    S.add(strike(200, 290, 220 + text_w("a character flaw", 124), 282, S.c("flaw") + 0.3, RED, 10))
    S.text("a maths problem.", 260, 560, 144, ORANGE, at=S.c("maths") - 0.3, rot=-3)
    S.text("= solvable", 320, 750, 104, GREEN, at=S.c("solved") - 0.3)
    S.add(check(860, 720, 34, S.c("solved") + 0.2, GREEN, 11))


@V.scene("f2")
def _(S):
    S.noframe = True
    S.draw([Fl(P_rect(120, 50, 1680, 840, 0, r=10), (250, 248, 242)), stk(P_rect(120, 50, 1680, 840, 7, r=10), 6),
            Fl(P_rect(880, 30, 160, 60, 0), (236, 228, 200))], 0.0, 0.35, snd=None)        # one sheet, taped up: screenshot it
    S.text("6 steps:", 200, 170, 110, INK, at=0.05)
    items = (("list", "list it"), ("minimum", "beat the minimum"), ("order", "pick an order"), ("one", "one at a time"),
             ("lower", "lower the rate"), ("refill", "don't refill it"))
    for k in range(6):                       # empty boxes first, ticked one by one
        col, row = k // 3, k % 3
        x, y = 200 + col * 860, 340 + row * 180
        S.draw([stk(P_rect(x, y - 62, 64, 64, 5, r=8), 5.5)], 0.05 + 0.08 * k, 0.15, snd="scr" if k == 0 else None)
    for k, (w_, lab) in enumerate(items):
        col, row = k // 3, k % 3
        x, y = 200 + col * 860, 340 + row * 180
        at = S.c(w_) - 0.2
        S.text(lab, x + 100, y, 82, INK, at=at, cps=34)
        S.add(check(x + 32, y - 34, 26, at + 0.45, GREEN, 9, seed=k))
    S.text("the whole plan.", 1060, 820, 90, ORANGE, at=S.c("whole", 1) - 0.2, rot=-2)


@V.scene("end")
def _(S):
    """The outro: no next-video box, no subscribe target. The fridge list from step 6, its last line crossed out on
    "killing", you pointing at it, and the question."""
    S.noframe = True
    t0 = S.l(0)
    S.text("education, not financial advice.\nfree debt help exists in most countries.", 130, 150, 64, GREY, at=t0 + 0.1, lh=1.1)
    fx, fy = 1520, 560
    S.draw([Fl(P_rect(fx - 260, fy - 420, 520, 880, 0, r=30), (236, 240, 246)), stk(P_rect(fx - 260, fy - 420, 520, 880, 8, r=30), 8),
            stk(P_line(fx - 260, fy - 120, fx + 260, fy - 120, 0.01, 1), 6), stk(P_line(fx - 200, fy - 360, fx - 200, fy - 220, 0.01, 2), 8),
            stk(P_line(fx - 200, fy - 60, fx - 200, fy + 120, 0.01, 3), 8)], t0 + 0.3, 0.5)
    S.draw([Fl(P_rect(fx - 100, fy - 40, 260, 340, 0), (250, 248, 242)), stk(P_rect(fx - 100, fy - 40, 260, 340, 6), 5)], t0 + 0.8, 0.3, snd=None)
    for k in range(4):
        y = fy + 30 + k * 70
        S.draw([stk(P_line(fx - 70, y, fx + 120, y, 0.02, k), 4.5, GREY)], t0 + 1.0 + 0.1 * k, 0.15, snd=None)
        S.add(strike(fx - 80, y + 4, fx + 135, y - 4, (t0 + 1.6 + 0.3 * k) if k < 3 else S.c("killing") + 0.3, RED, 6, seed=k))
    S.add(Fig(1130, 990, 0.95, poses=[("stand", 0), ("point_r", S.c("which") + 0.1)], moods=[("smile", 0), ("happy", S.c("comments"))], seed=3))
    S.text("which debt are you", 130, 520, 110, INK, at=S.c("which") - 0.2, rot=-2)
    S.text("killing first?", 160, 690, 150, ORANGE, at=S.c("killing") - 0.2, rot=-2)
    S.text("tell me in the comments.", 170, 850, 72, INK, at=S.c("comments") - 0.4, rot=-1)


if __name__ == "__main__":
    V.prepare(tail=4.5)              # a short outro, not a 12 s end screen
    V.main()
