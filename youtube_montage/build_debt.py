"""'How to Pay Off Debt So Fast It Feels Illegal' (doodle style). Sources in the kit: Gal & McShane (2012, JMR), Kettle, Trudel,
Blanchard & Häubl (2016, JCR). Payoff example: €3,000 at 20% a year, interest monthly (hypothetical)."""
import numpy as np

from doodle_video import *  # noqa: F401,F403

SAY = {"10%": "ten percent", "€600": "six hundred euros", "€300": "three hundred euros", "€3,000": "three thousand euros", "20%": "twenty percent", "€60": "sixty euros", "€3,500": "three thousand five hundred euros",
       "€150": "a hundred and fifty euros", "€680": "six hundred and eighty euros", "€500": "five hundred euros"}
V = Video("debt", say=SAY, seed=31, keys=dict(prog=[(57, 60, 64, 67), (55, 59, 62, 65), (53, 57, 60, 64), (52, 55, 59, 64)],
                                              roots=[45, 43, 41, 40], bpm=78),
          hush=[("And here's the part", "The minimum payment is")], tape="Final message", beat_groups=("o3",))
L = V.L

L("o1", "You pay every month. And somehow, the debt barely moves.")
L("o2", "That's not because you're bad with money. Some debt is built to be slow.")
L("o2b", "Interest is added every month. If your payment barely covers it, you're running on the spot.")
L("o3", "And here's the part nobody tells you.")
L("o4", "The minimum payment is the most expensive button in your banking app.")
L("o5", "Here are six steps to get out faster. Let's begin.")

L("c1", "One. Look at the whole monster.")
L("c1a", "Write down every debt: how much you owe, the interest rate, and the minimum payment.")
L("c1b", "Include everything: cards, store credit, buy now pay later, car loans, even money you owe friends.")
L("c1c", "Most people have never seen the total in one place. It's scary for ten minutes. Then it's a plan.")

L("c2", "Two. Escape the minimum payment.")
L("c2a", "Say you owe €3,000 on a card at 20% a year.")
L("c2a", "Pay €60 a month, and it takes about nine years. You pay around €3,500 in interest. More than the debt itself.")
L("c2x", "Minimums are often set as a small slice of what you owe. As the debt shrinks, the payment shrinks too, so the finish line keeps moving away.")
L("c2b", "Pay €150 a month instead, and you're free in about two years, with around €680 of interest.")
L("c2b", "Same debt. Same rate. Seven years of your life back.")

L("c3", "Three. Pick an order.")
L("c3a", "The avalanche: pay the minimum on everything, and throw every extra euro at the highest interest rate first. Mathematically, it saves the most.")
L("c3a", "The snowball: smallest balance first. You close accounts quickly, and each win keeps you going.")
L("c3b", "In one study of about six thousand people in a debt programme, those who cleared small accounts first were more likely to clear all of their debt.")
L("c3b", "So if the rates are similar, start small. If one rate is much higher, kill that one first.")

L("c4", "Four. One debt at a time.")
L("c4a", "Spreading your extra money thinly across every debt feels fair. But then nothing seems to move.")
L("c4a", "Researchers found that people who focused their repayments on one account at a time felt more progress, and paid more aggressively.")
L("c4b", "So pay the minimum on all the others, and put every extra euro on one. When it's gone, roll that payment into the next.")

L("c5", "Five. Make the interest smaller.")
L("c5a", "Call your bank and ask for a lower rate. It costs nothing to ask.")
L("c5a", "A cheaper consolidation loan can help too, but only if you stop using the old cards. Check every fee first.")
L("c5b", "Even a few points matter. On €3,000, going from 20% to 10% cuts the interest from about €600 a year to about €300.")

L("c6", "Six. Don't refill the bucket.")
L("c6a", "Keep a small emergency fund, even €500, so the next surprise doesn't go straight back on the card.")
L("c6a", "And when a debt is gone, send its old payment to the next one. Then, to your savings.")
L("c6b", "And keep it visible: a list on the fridge, crossed out one line at a time.")

L("f0", "Final message.")
L("f1", "Debt isn't a character flaw. It's a maths problem, and maths problems can be solved.")
L("f2", "List it. Pay more than the minimum. Pick an order. One at a time. Lower the rate. Don't refill it.")
L("end", "This is education, not financial advice. If debt feels unmanageable, many countries have free debt advice services. "
         "If this helped, subscribe. Next up: how to invest your first thousand euros.")


def boulder(x, y, r, col=(244, 214, 210), label="DEBT"):
    o = [Fl(P_ell(x, y, r, r * 0.9, 1, closed=True), col), stk(P_ell(x, y, r, r * 0.9, 3, 0.08), 8)]
    for k, (a, b2) in enumerate(((-0.4, -0.3), (0.3, 0.2), (-0.1, 0.45))):
        o.append(stk(P_arc(x + a * r, y + b2 * r, r * 0.16, r * 0.1, 200, 330, 12), 4, GREY))
    o.append(("g", label, x, y + r * 0.18, int(r * 0.5), INK, HAND, "m"))
    return o


def snail(x, y, s=1.0):
    th = np.linspace(0, 4.2 * np.pi, 90)
    rr = 70 * s * (1 - th / (4.6 * np.pi))
    spiral = np.stack([x + rr * np.cos(th), y - 40 * s + rr * np.sin(th)], 1)
    body = [(x - 120 * s, y + 40 * s), (x + 150 * s, y + 40 * s), (x + 170 * s, y - 10 * s), (x + 120 * s, y - 20 * s), (x + 90 * s, y + 20 * s)]
    return [Fl(P_ell(x, y - 40 * s, 75 * s, 72 * s, 1, closed=True), HL), stk(spiral, 6 * s), stk(P_poly(body), 6 * s),
            stk(P_line(x + 160 * s, y - 10 * s, x + 175 * s, y - 60 * s, 0.02, 1), 4 * s), stk(P_line(x + 145 * s, y - 15 * s, x + 150 * s, y - 64 * s, 0.02, 2), 4 * s)]


def table(S, x, y, rows, at_rows, cols=("debt", "owe", "rate", "min")):
    cw = [260, 220, 180, 180]
    S.draw([stk(P_line(x, y + 20, x + sum(cw), y + 20, 0.005, 1), 5)], at_rows[0] - 0.3, 0.3, snd=None)
    cx = x
    for k, c in enumerate(cols):
        S.text(c, cx + 10, y, 58, GREY, at=at_rows[0] - 0.3)
        cx += cw[k]
    for r_, (row, at) in enumerate(zip(rows, at_rows)):
        cx = x
        for k, v in enumerate(row):
            S.text(v, cx + 10, y + 100 + r_ * 90, 64, RED if (k == 2 and v != "7%") else INK, at=at + 0.1 * k)
            cx += cw[k]


# --------------------------------------------------------------------------- cold open
@V.scene("o1")
def _(S):
    S.draw([stk(P_line(120, 980, 1800, 520, 0.02, 1), 7)], 0.0, 0.5, snd=None)
    S.draw(boulder(1080, 600, 190), 0.2, 0.5)
    S.add(Fig(760, 880, 1.2, at=0.0, poses=[("reach", 0)], moods=[("worried", 0), ("sad", S.c("barely"))], seed=3, rot=-12))
    S.text("every month", 200, 250, 84, INK, at=S.c("every") - 0.1)
    S.text("barely moves.", 1180, 1000, 96, RED, at=S.c("barely") - 0.1, rot=-3)


@V.scene("o2")
def _(S):
    S.text("bad with money", 260, 380, 120, INK, at=S.c("bad") - 0.3)
    S.add(strike(240, 340, 260 + text_w("bad with money", 120), 332, S.c("money") + 0.3, RED, 10))
    S.draw(snail(1350, 700, 1.6), S.c("slow") - 0.6, 0.6)
    S.text("built to be slow.", 340, 760, 130, ORANGE, at=S.c("built") - 0.2, rot=-3)


@V.scene("o2b")
def _(S):
    tx, ty = 960, 840
    S.draw([stk(P_rect(tx - 330, ty, 660, 70, 7, r=30), 7), stk(P_line(tx + 260, ty, tx + 300, ty - 380, 0.02, 1), 7),
            stk(P_line(tx + 230, ty - 380, tx + 380, ty - 380, 0.02, 2), 7)], 0.0, 0.4, snd=None)
    S.add(Fig(tx - 40, ty, 1.15, at=0.0, poses=[("stand", 0)], moods=[("worried", 0)], seed=3, walk=(tx - 40, tx - 39, 0.1, S.dur)))
    S.text("+ interest, every month", 160, 260, 80, RED, at=S.c("interest") - 0.1)
    S.text("running on the spot.", 1100, 1000, 80, INK, at=S.c("running") - 0.2, rot=-2)


@V.scene("o3")
def _(S):
    S.add(Fig(980, 1520, 3.2, at=0.0, poses=[("stand", 0)], moods=[("smug", 0)], enter="none", seed=3, idle=0.6, look=0.4))
    S.text("psst.", 1430, 320, 96, GREY, at=S.c("part") - 0.2, rot=8)


@V.scene("o4")
def _(S):
    px, py = 620, 560
    S.draw(phone(px, py, 1.8), 0.0, 0.5)
    S.draw([Fl(P_rect(px - 120, py + 40, 240, 110, 0, r=26), ORANGE), stk(P_rect(px - 120, py + 40, 240, 110, 6, r=26), 6)], S.c("minimum") - 0.2, 0.3)
    S.text("PAY\nMINIMUM", px, py + 88, 40, INK, at=S.c("minimum"), anchor="m", lh=1.0)
    S.text("the most expensive\nbutton in the app.", 1020, 420, 96, RED, at=S.c("expensive") - 0.3, rot=-2)
    S.add(arrow(P_bez((1010, 560), (880, 640), (760, 640)), S.c("button"), RED, 7, 0.35))


@V.scene("o5")
def _(S):
    S.text("6", 300, 600, 380, ORANGE, at=S.c("six") - 0.05, anchor="m", rot=-6, cps=8)
    S.text("steps", 470, 520, 130, INK, at=S.c("steps") - 0.1)
    S.text("to get out faster.", 500, 680, 86, GREY, at=S.c("faster") - 0.3)
    S.add(Fig(1550, 950, 1.2, at=0.0, poses=[("stand", 0), ("wave", S.c("begin"))], moods=[("smile", 0), ("happy", S.c("begin"))], seed=3, flip=True))


V.chapters({1: ("Look at the\nwhole monster.", 0), 2: ("Escape the\nminimum payment.", 1), 3: ("Pick an\norder.", 0), 4: ("One debt\nat a time.", 1),
            5: ("Make the interest\nsmaller.", 0), 6: ("Don't refill\nthe bucket.", 1)}, peek={1, 3, 6})


# --------------------------------------------------------------------------- steps
@V.scene("c1a")
def _(S):
    rows = [("card A", "€800", "21%", "€25"), ("loan", "€3,500", "7%", "€60"), ("card B", "€2,200", "19%", "€45")]
    table(S, 260, 380, rows, [S.c("owe") - 0.2, S.c("rate") - 0.1, S.c("minimum") - 0.1])
    S.text("write it all down.", 260, 220, 86, ORANGE, at=S.c("write") - 0.1, rot=-2)
    S.add(Fig(1550, 950, 1.2, at=0.0, poses=[("think", 0)], moods=[("worried", 0)], seed=3, flip=True))


@V.scene("c1b")
def _(S):
    icons = ((S.c("cards"), card(300, 420, 0.8), "cards"), (S.c("store"), cart(700, 440, 0.6), "store credit"),
             (S.c("buy"), phone(1080, 430, 0.6), "pay later"), (S.c("car"), car(1460, 440, 0.6), "car loan"))
    for k, (at, ops, lab) in enumerate(icons):
        S.draw(ops, at - 0.15, 0.35, snd="scr" if k in (0, 2) else None)
        S.text(lab, [300, 700, 1080, 1460][k], 680, 60, INK, at=at, anchor="m")
    S.add(Fig(960, 1000, 0.75, at=S.c("friends") - 0.3, poses=[("hips", 0)], moods=[("smug", 0)], kind="spiky", seed=55, enter="pop"))
    S.text("\"you owe me €50\"", 1080, 880, 56, GREY, at=S.c("friends"))
    S.text("everything.", 240, 230, 120, ORANGE, at=S.c("everything") - 0.1, rot=-3)


@V.scene("c1c")
def _(S):
    S.text("total:", 260, 380, 110, INK, at=S.c("total") - 0.2)
    S.text("€6,500", 560, 400, 170, RED, at=S.c("total") + 0.1, rot=-3, cps=12)
    S.text("scary for 10 minutes.", 260, 660, 86, GREY, at=S.c("scary") - 0.2)
    S.text("then: a plan.", 260, 820, 120, ORANGE, at=S.c("plan") - 0.3, rot=-2)
    S.add(Fig(1550, 950, 1.2, at=0.0, poses=[("think", 0), ("hips", S.c("plan"))], moods=[("worried", S.c("scary")), ("smug", S.c("plan"))],
              seed=3, flip=True))


@V.scene("c2a")
def _(S):
    S.draw(card(420, 330, 1.3), S.c("card") - 0.3, 0.4)
    S.text("€3,000 at 20%", 200, 580, 96, INK, at=S.c("€3,000") - 0.1)
    S.text("€60 a month", 200, 760, 90, INK, at=S.c("€60", 1) - 0.1)
    S.draw(calendar(1560, 380, 0.8, day=None, head="9 YEARS"), S.c("nine", 1) - 0.3, 0.4)
    S.add(*bars(940, 900, [3000, 3500], ["the debt", "interest"], S.c("€3,500", 1) - 0.4, step=0.4, maxh=380, bw=190, gap=110,
                cols=[PALE, (244, 214, 210)], txt=["€3,000", "€3,500"], seed=41, size=64))
    S.text("interest > the debt", 200, 920, 76, RED, at=S.c("more", 1) - 0.1, rot=-2)


@V.scene("c2x")
def _(S):
    S.draw([stk(P_line(140, 860, 1800, 860, 0.005, 1), 6)], 0.0, 0.3, snd=None)
    S.add(Fig(500, 860, 1.0, at=0.0, poses=[("stand", 0)], moods=[("worried", 0)], seed=3, walk=(380, 820, 0.2, S.e() + 0.4)))
    fx0, fx1 = 1100, 1650

    def drift(tt, t0=S.c("finish")):
        u = clamp((tt - t0) / 1.6)
        return ((fx1 - fx0) * ease_io(u), 0, 0, 1)
    S.add(Dr([stk(P_line(fx0, 860, fx0, 560, 0.01, 2), 7), Fl(P_poly([(fx0, 560), (fx0 + 120, 600), (fx0, 640)], True), RED),
              stk(P_poly([(fx0, 560), (fx0 + 120, 600), (fx0, 640)], True), 5)], 0.1, 0.0, anchor=(fx0, 860), move=drift, seed=9))
    S.text("minimum = a % of what you owe", 200, 260, 80, INK, at=S.c("slice") - 0.4)
    S.text("debt shrinks, payment shrinks.", 240, 400, 70, GREY, at=S.c("shrinks") - 0.2)
    S.text("the finish line moves.", 980, 1000, 76, RED, at=S.c("finish") - 0.1, rot=-2)


@V.scene("c2b")
def _(S):
    S.text("€60 / month", 200, 330, 90, GREY, at=0.1)
    S.draw([stk(P_line(200, 400, 200 + 9 * 160, 400, 0.005, 1), 22, (244, 214, 210))], 0.2, 0.6, snd=None)
    S.text("9 years · €3,500 interest", 220, 480, 64, GREY, at=0.4)
    S.text("€150 / month", 200, 650, 100, INK, at=S.c("€150") - 0.1)
    S.draw([stk(P_line(200, 720, 200 + 2 * 160, 720, 0.005, 2), 22, ORANGE)], S.c("two") - 0.2, 0.4)
    S.text("2 years · €680 interest", 220, 800, 70, INK, at=S.c("€680") - 0.2)
    S.text("7 years back.", 1060, 760, 150, ORANGE, at=S.c("seven", 1) - 0.2, rot=-4, cps=14)


@V.scene("c3a")
def _(S):
    S.text("avalanche", 260, 230, 110, INK, at=S.c("avalanche") - 0.2)
    for k, (lab, w) in enumerate((("21%", 260), ("19%", 330), ("7%", 420))):
        y = 360 + k * 110
        S.draw([Fl(P_rect(260, y, w, 80, 0, r=10), (244, 214, 210) if k == 0 else PALE), stk(P_rect(260, y, w, 80, 5, r=10), 5)],
               S.c("highest") - 0.4 + 0.1 * k, 0.25, snd="scr" if k == 0 else None)
        S.text(lab, 290, y + 58, 56, INK, at=S.c("highest") - 0.2 + 0.1 * k)
    S.add(arrow(P_line(640, 400, 560, 400, 0.02, 1), S.c("highest"), RED, 7, 0.25))
    S.text("highest rate first", 260, 760, 66, RED, at=S.c("highest") + 0.1)
    S.text("saves the most", 280, 850, 66, GREY, at=S.c("mathematically") - 0.1)
    S.draw([stk(P_line(960, 200, 965, 960, 0.01, 2), 5, GREY)], S.l(1) - 0.3, 0.3, snd=None)
    S.text("snowball", 1100, 230, 110, INK, at=S.c("snowball", 1) - 0.2)
    for k, (lab, w) in enumerate((("€800", 180), ("€2,200", 300), ("€3,500", 420))):
        y = 360 + k * 110
        S.draw([Fl(P_rect(1100, y, w, 80, 0, r=10), HL if k == 0 else PALE), stk(P_rect(1100, y, w, 80, 5, r=10), 5)],
               S.c("smallest", 1) - 0.3 + 0.1 * k, 0.25, snd=None)
        S.text(lab, 1125, y + 58, 52, INK, at=S.c("smallest", 1) - 0.1 + 0.1 * k)
    S.add(check(1330, 400, 26, S.c("close", 1), GREEN, 9))
    S.text("smallest first", 1100, 760, 66, ORANGE, at=S.c("smallest", 1) + 0.2)
    S.text("quick wins", 1120, 850, 66, GREY, at=S.c("win", 1) - 0.1)


@V.scene("c3b")
def _(S):
    S.text("~6,000 people", 220, 260, 96, INK, at=S.c("six") - 0.1)
    S.text("small accounts cleared first", 240, 400, 70, GREY, at=S.c("small") - 0.2)
    S.text("= more likely to clear it all", 260, 510, 76, ORANGE, at=S.c("likely") - 0.2)
    S.text("rates similar?", 220, 760, 76, INK, at=S.c("similar", 1) - 0.2)
    S.text("start small.", 760, 760, 86, ORANGE, at=S.c("start", 1) - 0.1)
    S.text("one much higher?", 220, 920, 76, INK, at=S.c("higher", 1) - 0.4)
    S.text("kill that one.", 840, 920, 86, RED, at=S.c("kill", 1) - 0.1)
    S.draw(snowball(1560, 520, 160), S.c("six") + 0.2, 0.5, snd=None)


@V.scene("c4a")
def _(S):
    for k in range(4):
        x = 230 + k * 190
        S.draw(jar(x, 520, 0.85, fill_u=0.18, col=(214, 226, 196)), 0.1 + 0.08 * k, 0.3, snd="scr" if k == 0 else None)
    S.text("spread thin", 230, 820, 90, GREY, at=S.c("spreading") - 0.1)
    S.text("nothing moves.", 260, 940, 76, RED, at=S.c("nothing") - 0.2)
    S.draw([stk(P_line(1000, 220, 1005, 960, 0.01, 2), 5, GREY)], S.l(1) - 0.3, 0.3, snd=None)
    S.draw(jar(1180, 520, 0.85, fill_u=0.95, col=ORANGE), S.c("focused", 1) - 0.2, 0.35)
    for k in range(3):
        S.draw(jar(1370 + k * 170, 520, 0.85, fill_u=0.05, col=(214, 226, 196)), S.c("focused", 1) + 0.1 * k, 0.25, snd=None)
    S.add(check(1180, 300, 34, S.c("progress", 1) - 0.1, GREEN, 11))
    S.text("one at a time", 1130, 820, 90, ORANGE, at=S.c("one", 1) - 0.1)
    S.text("more progress, paid faster", 1110, 940, 62, INK, at=S.c("aggressively", 1) - 0.5)


@V.scene("c4b")
def _(S):
    for k in range(3):
        S.draw(jar(300 + k * 200, 560, 0.85, fill_u=0.1, col=(214, 226, 196)), 0.0, 0.3, snd=None)
        S.text("min", 300 + k * 200, 790, 52, GREY, at=S.c("minimum") + 0.1 * k, anchor="m")
    S.draw(jar(1180, 560, 1.2, fill_u=0.85, col=ORANGE), S.c("extra") - 0.2, 0.4)
    S.text("every extra €", 1060, 860, 66, ORANGE, at=S.c("extra"))
    S.add(arrow(P_bez((1300, 360), (1440, 260), (1560, 380)), S.c("roll") - 0.1, INK, 6, 0.4))
    S.text("roll it into the next", 1340, 230, 60, INK, at=S.c("roll"))
    S.draw(jar(1600, 560, 0.85, fill_u=0.4, col=HL), S.c("next") - 0.1, 0.3, snd=None)


@V.scene("c5a")
def _(S):
    S.draw(phone(420, 560, 1.4), 0.0, 0.4)
    S.draw(bubble(860, 300, 460, 150, tail=(-1, 1)), S.c("ask") - 0.6, 0.3, snd=None)
    S.text("lower rate?", 860, 325, 76, INK, at=S.c("lower") - 0.1, anchor="m")
    S.text("free to ask.", 700, 520, 76, GREEN, at=S.c("nothing") - 0.2)
    for k, x in enumerate((1180, 1340, 1500)):
        S.draw(card(x, 330 + k * 30, 0.5), S.c("consolidation", 1) - 0.3 + 0.1 * k, 0.25, snd=None)
    S.add(arrow(P_bez((1340, 470), (1350, 560), (1360, 640)), S.c("loan", 1), INK, 6, 0.3))
    S.draw([Fl(P_rect(1200, 650, 320, 130, 0, r=14), (214, 226, 196)), stk(P_rect(1200, 650, 320, 130, 6, r=14), 6)], S.c("loan", 1) + 0.2, 0.3)
    S.text("1 cheaper loan", 1360, 735, 52, INK, at=S.c("loan", 1) + 0.3, anchor="m")
    S.text("only if the old cards stop.", 1000, 900, 64, RED, at=S.c("stop", 1) - 0.3)
    S.text("check every fee.", 1100, 1000, 60, GREY, at=S.c("fee", 1) - 0.2)
    S.text("calling\nthe bank", 420, 520, 40, INK, at=0.4, anchor="m", path=HAND2)


@V.scene("c5b")
def _(S):
    S.text("on €3,000:", 200, 240, 84, GREY, at=S.c("€3,000") - 0.1)
    S.add(*bars(400, 880, [600, 300], ["at 20%", "at 10%"], S.c("€600") - 0.2, step=S.c("€300") - S.c("€600"), maxh=480, bw=240, gap=200,
                cols=[(244, 214, 210), (214, 226, 196)], txt=["€600/yr", "€300/yr"], seed=51, size=74))
    S.text("half the interest.", 1060, 520, 96, ORANGE, at=S.c("€300") + 0.3, rot=-3)


@V.scene("c6a")
def _(S):
    cx, cy = 460, 560
    pil = np.vstack([P_bez((cx - 200, cy - 80), (cx, cy - 140), (cx + 200, cy - 80)), P_bez((cx + 200, cy - 80), (cx + 250, cy), (cx + 200, cy + 80)),
                     P_bez((cx + 200, cy + 80), (cx, cy + 140), (cx - 200, cy + 80)), P_bez((cx - 200, cy + 80), (cx - 250, cy), (cx - 200, cy - 80))])
    S.draw([Fl(pil, (150, 186, 214)), stk(pil, 7)], S.c("emergency") - 0.3, 0.45)
    S.text("€500", cx, cy + 25, 90, INK, at=S.c("€500") - 0.1, anchor="m")
    S.text("so the card stays at zero", 240, 820, 64, GREY, at=S.c("card") - 0.4)
    S.draw([Fl(P_rect(1050, 300, 300, 110, 0, r=14), PALE), stk(P_rect(1050, 300, 300, 110, 6, r=14), 6)], S.c("gone", 1) - 0.3, 0.3)
    S.text("debt 1", 1200, 375, 60, INK, at=S.c("gone", 1) - 0.2, anchor="m")
    S.add(check(1380, 340, 30, S.c("gone", 1) + 0.1, GREEN, 9))
    S.add(arrow(P_bez((1200, 420), (1210, 480), (1220, 530)), S.c("payment", 1), ORANGE, 6, 0.3))
    S.draw([Fl(P_rect(1070, 540, 300, 110, 0, r=14), (244, 214, 210)), stk(P_rect(1070, 540, 300, 110, 6, r=14), 6)], S.c("next", 1) - 0.2, 0.3)
    S.text("debt 2", 1220, 615, 60, INK, at=S.c("next", 1), anchor="m")
    S.add(arrow(P_bez((1220, 660), (1230, 720), (1240, 770)), S.c("savings", 1) - 0.3, ORANGE, 6, 0.3))
    S.draw(piggy(1260, 880, 0.55), S.c("savings", 1) - 0.1, 0.4)
    S.text("same payment,\nnext target", 1460, 600, 56, GREY, at=S.c("next", 1) + 0.3)


@V.scene("c6b")
def _(S):
    fx, fy = 760, 560
    S.draw([Fl(P_rect(fx - 260, fy - 420, 520, 880, 0, r=30), (236, 240, 246)), stk(P_rect(fx - 260, fy - 420, 520, 880, 8, r=30), 8),
            stk(P_line(fx - 260, fy - 120, fx + 260, fy - 120, 0.01, 1), 6), stk(P_line(fx + 200, fy - 360, fx + 200, fy - 220, 0.01, 2), 8),
            stk(P_line(fx + 200, fy - 60, fx + 200, fy + 120, 0.01, 3), 8)], 0.0, 0.5)
    S.draw(list_paper(fx - 40, fy + 120, 0.8), S.c("list") - 0.3, 0.4) if False else S.draw(
        [Fl(P_rect(fx - 160, fy - 40, 260, 340, 0), (250, 248, 242)), stk(P_rect(fx - 160, fy - 40, 260, 340, 6), 5)], S.c("list") - 0.3, 0.4)
    for k in range(4):
        y = fy + 30 + k * 70
        S.draw([stk(P_line(fx - 130, y, fx + 60, y, 0.02, k), 4.5, GREY)], S.c("list") + 0.1 * k, 0.15, snd=None)
        if k < 3:
            S.add(strike(fx - 140, y + 4, fx + 75, y - 4, S.c("crossed") + 0.3 * k, RED, 6, seed=k))
    S.text("keep it visible.", 1160, 460, 100, ORANGE, at=S.c("visible") - 0.2, rot=-3)
    S.text("one line at a time.", 1180, 640, 76, INK, at=S.c("line") - 0.2)


@V.scene("f0")
def _(S):
    S.text("final message.", 260, 600, 120, INK, at=0.05, rot=-3, cps=20)
    S.add(under(270, 980, 640, 1.0, ORANGE, 7, 0.4, wavy=True))


@V.scene("f1")
def _(S):
    S.text("a character flaw", 260, 380, 120, INK, at=S.c("character") - 0.3)
    S.add(strike(240, 340, 260 + text_w("a character flaw", 120), 332, S.c("flaw") + 0.3, RED, 10))
    S.text("a maths problem.", 300, 640, 140, ORANGE, at=S.c("maths") - 0.3, rot=-3)
    S.text("= solvable", 360, 820, 100, GREEN, at=S.c("solved") - 0.3)
    S.add(check(860, 790, 34, S.c("solved") + 0.2, GREEN, 11))


@V.scene("f2")
def _(S):
    items = (("list", "list it"), ("minimum", "beat the minimum"), ("order", "pick an order"), ("one", "one at a time"),
             ("lower", "lower the rate"), ("refill", "don't refill it"))
    for k, (w_, lab) in enumerate(items):
        col, row = k // 3, k % 3
        x, y = 200 + col * 900, 340 + row * 210
        at = S.c(w_) - 0.2
        S.text(f"{k + 1}.", x, y, 80, ORANGE, at=at - 0.05)
        S.text(lab, x + 90, y, 78 if k != 1 else 70, INK, at=at, cps=34)
        S.add(check(x + 110 + text_w(lab, 78 if k != 1 else 70) + 30, y - 30, 26, at + 0.55, GREEN, 9, seed=k))


@V.scene("end")
def _(S):
    S.text("not financial advice. free debt advice exists in many countries.", 200, 200, 52, GREY, at=S.c("education") - 0.2)
    sx, sy = 520, 600
    S.draw([Fl(P_rect(sx - 220, sy - 70, 440, 140, 0, r=26), ORANGE), stk(P_rect(sx - 220, sy - 70, 440, 140, 8, r=26), 7)], S.c("subscribe") - 0.3, 0.4)
    S.text("subscribe", sx, sy + 26, 92, INK, at=S.c("subscribe") - 0.1, anchor="m")
    vx, vy = 1350, 560
    S.draw([stk(P_rect(vx - 330, vy - 190, 660, 380, 8, r=12), 7)], S.c("next") - 0.2, 0.45)
    S.text("next:", vx - 320, vy - 220, 70, GREY, at=S.c("next") - 0.1)
    S.text("invest your\nfirst €1,000.", vx, vy - 20, 80, INK, at=S.c("invest") - 0.1, anchor="m")
    S.add(Fig(820, 980, 0.95, at=0.0, poses=[("stand", 0), ("point_r", S.c("next") + 0.1)], moods=[("smile", 0), ("happy", S.c("subscribe"))], seed=3))


if __name__ == "__main__":
    V.main()
