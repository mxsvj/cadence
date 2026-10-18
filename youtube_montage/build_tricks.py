"""'7 Tricks Shops Use to Make You Spend More (and How to Beat Them)' (doodle style). Sources in the kit: Anderson & Simester 2003,
Ariely (Economist decoy), EU CPC sweep (Jan 2023), Price Indication Directive art. 6a (Omnibus), Di Maggio, Katz & Williams (NBER w30508),
Directive (EU) 2023/2225, Food (Promotion and Placement) (England) Regulations 2021."""
import math

import numpy as np

from doodle_video import *  # noqa: F401,F403

SAY = {"€9.99": "nine ninety-nine", "$34": "thirty-four dollars", "$39": "thirty-nine dollars", "$44": "forty-four dollars",
       "€49.95": "forty-nine ninety-five", "$59": "fifty-nine dollars", "$125": "a hundred and twenty-five dollars",
       "84%": "eighty-four percent", "68%": "sixty-eight percent", "2023": "twenty twenty-three", "399": "three hundred and ninety-nine",
       "148": "a hundred and forty-eight", "42": "forty-two", "€199": "a hundred and ninety-nine euros", "€99": "ninety-nine euros",
       "2022": "twenty twenty-two", "€4.90": "four euros ninety", "€50": "fifty euros", "€38": "thirty-eight euros", "€15": "fifteen euros",
       "€10": "ten euros", "€25": "twenty-five euros", "€100": "a hundred euros", "2026": "twenty twenty-six", "EU": "E U", "US": "U S",
       "€120": "a hundred and twenty euros", "17%": "seventeen percent", "50%": "fifty percent", "20": "the twentieth of"}
V = Video("tricks", say=SAY, seed=11, keys=dict(prog=[(50, 53, 57, 60), (55, 59, 62, 65), (48, 52, 55, 59), (53, 57, 60, 64)],
                                                roots=[38, 43, 36, 41], bpm=84),
          tape="Final message")
L = V.L

L("o1", "This price says €9.99. Your brain reads nine. But it's ten.")
L("o3", "That's not an accident. Shops test prices, buttons and timers on millions of people. Your brain is the test subject.")
L("o5", "Once you can see the tricks, most of them stop working.")
L("o6", "Here are seven of them, and how to beat each one.")

L("c1", "One. The price that ends in nine.")
L("c1a", "Your brain reads the first digit, and mostly stops there. So €9.99 feels much closer to nine than to ten.")
L("c1b", "In one US experiment, a clothing catalogue raised the price of a dress from $34 to $39. It sold about a third more.")
L("c1b", "At $44, it sold the same as at $34.")
L("c1c", "The fix: round prices up in your head. €9.99 is ten euros. €49.95 is fifty.")

L("c2", "Two. The decoy.")
L("c2a", "A magazine once offered three options. Online only: $59. Print only: $125. Print and online: $125.")
L("c2a", "Nobody picks print only. It's there to make the bundle look like a steal.")
L("c2b", "In a famous class experiment, 84% of students chose the bundle.")
L("c2b", "When the decoy was removed, 68% chose the cheap online option instead.")
L("c2c", "The fix: when you see three prices, ask which one is only there to push you. Then compare the other two.")

L("c3", "Three. The fake countdown.")
L("c3a", "Only two left. Offer ends in ten minutes. Someone in Paris just bought this.")
L("c3a", "Urgency switches off the slow, careful part of your brain.")
L("c3b", "In a check published in 2023, EU consumer authorities looked at 399 online shops. 148 used at least one manipulative trick.")
L("c3b", "42 of them had countdown timers that were fake.")
L("c3c", "The fix: if a timer says hurry, wait. A real deal survives a night of sleep.")

L("c4", "Four. The fake discount.")
L("c4a", "Was €199. Now €99. Half price! But was it ever really €199?")
L("c4a", "A high before price is an anchor. It makes the new price feel small.")
L("c4b", "In the EU, since 2022, a shop announcing a discount has to compare it with its lowest price in the previous thirty days.")
L("c4b", "Here, that's €120. So the real discount is about 17%, not 50%.")
L("c4b", "Check that small line, or a price tracker, before you believe the percentage.")

L("c5", "Five. Free shipping.")
L("c5a", "Shipping costs €4.90. It's free above €50. Your basket is at €38.")
L("c5a", "So you add a €15 thing you didn't plan to buy, to save €4.90.")
L("c5b", "You just spent about €10 more to avoid paying €4.90.")
L("c5b", "The fix: pay the shipping, or wait until you really need more.")

L("c6", "Six. Buy now, pay later.")
L("c6a", "Four payments of €25 feel lighter than one payment of €100. It's the same €100.")
L("c6a", "One large study of US bank data found that once people start using buy now, pay later, their total spending goes up, and stays up for months.")
L("c6b", "New EU consumer credit rules, applying from 20 November 2026, bring most buy now, pay later under credit law, with checks on whether you can afford it.")
L("c6b", "The fix: if you can't pay for it today, you probably can't afford it today.")

L("c7", "Seven. The store map.")
L("c7a", "Milk and bread are usually at the back. To reach them, you walk past everything else.")
L("c7a", "And the sweets wait at the checkout, right where you stand still with nothing to do.")
L("c7b", "England even banned less healthy snacks from the checkouts of larger stores in 2022.")
L("c7b", "The fix: shop with a list, and walk straight to what's on it.")

L("f0", "Final message.")
L("f1", "Some of these tricks are banned. Most are perfectly legal. They're just very good design.")
L("f2", "Round prices up. Spot the decoy. Ignore the timer. Check the real old price. Pay the shipping. Pay in full. Bring a list.")
L("f3", "Your brain isn't stupid. It's just being tested by people who do this all day.")
L("end", "This is education, not financial advice. If this helped, subscribe. Next up: how to save money so easily it feels illegal.")


# --------------------------------------------------------------------------- props for this video
def bag(x, y, s=1.0, col=(214, 226, 196)):
    o = [Fl(P_poly([(x - 70 * s, y - 60 * s), (x + 70 * s, y - 60 * s), (x + 80 * s, y + 90 * s), (x - 80 * s, y + 90 * s)], True), col),
         stk(P_poly([(x - 70 * s, y - 60 * s), (x + 70 * s, y - 60 * s), (x + 80 * s, y + 90 * s), (x - 80 * s, y + 90 * s)], True), 6 * s),
         stk(P_arc(x, y - 60 * s, 40 * s, 45 * s, 180, 360, 20), 5 * s)]
    return o


def dress(x, y, s=1.0, col=PINK):
    pts = [(x - 40 * s, y - 120 * s), (x - 30 * s, y - 40 * s), (x - 100 * s, y + 120 * s), (x + 100 * s, y + 120 * s), (x + 30 * s, y - 40 * s),
           (x + 40 * s, y - 120 * s), (x + 15 * s, y - 100 * s), (x - 15 * s, y - 100 * s)]
    return [Fl(P_poly(pts, True), col), stk(P_poly(pts, True), 6 * s), stk(P_line(x - 32 * s, y - 40 * s, x + 32 * s, y - 40 * s, 0.05, 2), 5 * s)]


def price_card(x, y, top, price, s=1.0, col=(250, 248, 242)):
    w, h = 300 * s, 260 * s
    return [Fl(P_rect(x - w / 2, y - h / 2, w, h, 0, r=18 * s), col), stk(P_rect(x - w / 2, y - h / 2, w, h, 8 * s, r=18 * s), 6.5 * s),
            ("g", top, x, y - 40 * s, int(54 * s), INK, HAND, "m"), ("g", price, x, y + 80 * s, int(96 * s), INK, HAND, "m")]


def anchor_shape(x, y, s=1.0):
    return [stk(P_ell(x, y - 150 * s, 26 * s, 26 * s, 1, 0.1), 8 * s), stk(P_line(x, y - 124 * s, x, y + 130 * s, 0.01, 2), 9 * s),
            stk(P_line(x - 80 * s, y - 70 * s, x + 80 * s, y - 70 * s, 0.02, 3), 8 * s),
            stk(P_arc(x, y + 20 * s, 120 * s, 110 * s, 20, 160, 40), 9 * s),
            stk(P_poly([(x + 128 * s, y + 20 * s), (x + 113 * s, y + 58 * s), (x + 150 * s, y + 70 * s)]), 8 * s),
            stk(P_poly([(x - 128 * s, y + 20 * s), (x - 113 * s, y + 58 * s), (x - 150 * s, y + 70 * s)]), 8 * s)]


def candy(x, y, s=1.0, col=PINK):
    return [Fl(P_ell(x, y, 34 * s, 24 * s, 1, closed=True), col), stk(P_ell(x, y, 34 * s, 24 * s, 2, 0.08), 5 * s),
            stk(P_poly([(x - 34 * s, y), (x - 62 * s, y - 20 * s), (x - 62 * s, y + 20 * s)], True), 4.5 * s),
            stk(P_poly([(x + 34 * s, y), (x + 62 * s, y - 20 * s), (x + 62 * s, y + 20 * s)], True), 4.5 * s)]


def list_paper(x, y, s=1.0, n=4):
    w, h = 300 * s, 400 * s
    o = [Fl(P_rect(x - w / 2, y - h / 2, w, h, 0), (250, 248, 242)), stk(P_rect(x - w / 2, y - h / 2, w, h, 8 * s), 6.5 * s)]
    for k in range(n):
        yy = y - h / 2 + 90 * s + k * 75 * s
        o += [stk(P_rect(x - w / 2 + 30 * s, yy - 22 * s, 36 * s, 36 * s, 3 * s), 4.5 * s), stk(P_line(x - w / 2 + 90 * s, yy, x + w / 2 - 40 * s - (k % 2) * 40 * s, yy, 0.02, k), 4.5 * s, GREY)]
    return o


def brain_switch(S, x, y, at_off):
    S.draw(brain(x, y, 1.1), 0.0, 0.5, snd=None)
    S.draw([Fl(P_rect(x + 230, y - 60, 140, 70, 0, r=35), (250, 248, 242)), stk(P_rect(x + 230, y - 60, 140, 70, 6, r=35), 6)], 0.2, 0.3, snd=None)
    S.add(Dr([Fl(P_ell(x + 335, y - 25, 26, 26, 1, closed=True), GREEN), stk(P_ell(x + 335, y - 25, 26, 26, 2, 0.05), 5)], 0.2, 0.0, until=at_off, seed=3))
    S.add(Dr([Fl(P_ell(x + 265, y - 25, 26, 26, 1, closed=True), RED), stk(P_ell(x + 265, y - 25, 26, 26, 2, 0.05), 5)], at_off, 0.0, seed=4), snd="pop", at=at_off)


def until_(fn, t1):
    """Hide an element from t1 on (for helpers that have no `until`)."""
    def g(ctx, t):
        if t < t1:
            fn(ctx, t)
    return g


def countdown(x, y, size, at, start=599, stop=None, col=INK):
    """A shop timer that ticks down once a second from 9:59 (it is a display: digits switch, they are not rewritten).
    stop: the time it freezes (ignored)."""
    n = 30
    vals = [f"{(start - k) // 60}:{(start - k) % 60:02d}" for k in range(n)]
    first = T(vals[0], x, y, size, col, at=at, anchor="m", cps=16)
    shown = [T(v, x, y, size, col, at=-10.0, anchor="m", seed=900) for v in vals]

    def fn(ctx, t):
        if t < at:
            return
        if t < at + 1.0:
            first(ctx, t)
            return
        k = int((min(t, stop) if stop is not None else t) - at)
        shown[min(k, n - 1)](ctx, t)
    return fn


def magazine(x, y, s=1.0, col=PINK):
    w, h = 190 * s, 250 * s
    o = [Fl(P_rect(x - w / 2, y - h / 2, w, h, 0), col), stk(P_rect(x - w / 2, y - h / 2, w, h, 7 * s), 6 * s),
         stk(P_line(x - w / 2 + 25 * s, y - h / 2 + 50 * s, x + w / 2 - 25 * s, y - h / 2 + 50 * s, 0.02, 1), 9 * s)]
    for k in range(3):
        yy = y + k * 40 * s
        o.append(stk(P_line(x - w / 2 + 25 * s, yy, x + w / 2 - (25 + 30 * (k % 2)) * s, yy, 0.02, k + 2), 4 * s))
    return o


def parcel(x, y, s=1.0, col=(214, 170, 120)):
    w, h = 220 * s, 160 * s
    return [Fl(P_rect(x - w / 2, y - h / 2, w, h, 0), col), stk(P_rect(x - w / 2, y - h / 2, w, h, 7 * s), 6.5 * s),
            stk(P_line(x - w / 2, y - h / 2 + 40 * s, x + w / 2, y - h / 2 + 40 * s, 0.01, 1), 5 * s),
            stk(P_line(x, y - h / 2, x, y - h / 2 + 40 * s, 0, 2), 5 * s)]


def rulebook(x, y, s=1.0, col=(150, 186, 214)):
    w, h = 260 * s, 340 * s
    o = [Fl(P_rect(x - w / 2, y - h / 2, w, h, 0, r=10 * s), col), stk(P_rect(x - w / 2, y - h / 2, w, h, 8 * s, r=10 * s), 7 * s),
         stk(P_line(x - w / 2 + 22 * s, y - h / 2 + 6 * s, x - w / 2 + 22 * s, y + h / 2 - 6 * s, 0, 3), 5 * s)]
    for k in range(12):                                    # a ring of twelve dots: "EU rules", no logo needed
        a = k * math.pi / 6
        cx, cy = x + 12 * s + 70 * s * math.cos(a), y - 30 * s + 70 * s * math.sin(a)
        o.append(Fl(P_ell(cx, cy, 11 * s, 11 * s, k, closed=True), HL))
    return o


def counter(x, y, s=1.0, col=(150, 186, 214)):
    w, h = 640 * s, 150 * s
    return [Fl(P_rect(x - w / 2, y, w, h, 0), col), stk(P_rect(x - w / 2, y, w, h, 7 * s), 7 * s),
            stk(P_line(x - w / 2 + 40 * s, y + h, x - w / 2 + 40 * s, y + h + 90 * s, 0, 1), 6 * s),
            stk(P_line(x + w / 2 - 40 * s, y + h, x + w / 2 - 40 * s, y + h + 90 * s, 0, 2), 6 * s)]


# --------------------------------------------------------------------------- cold open
@V.scene("o1")
def _(S):
    """Frame 0 is the thumbnail (B1): the €9.99 tag, already drawn, and a figure pointing at it."""
    S.noframe = True
    S.add(Dr(tag(760, 500, 3.0, "", HL), 0.0, 0.0, seed=5))
    S.text("€9.99", 820, 570, 180, INK, at=-3.0, anchor="m")
    S.add(Fig(1600, 980, 1.4, at=0.0, poses=[("point_l", 0)], moods=[("smug", 0), ("grin", S.c("ten"))], seed=3, flip=False, enter="none"))
    S.add(circ(752, 515, 72, 100, S.c("reads") - 0.1, ORANGE, 8))
    S.text("brain: \"9\"", 300, 830, 110, INK, at=S.c("nine") - 0.15, rot=-2)
    S.text("it's €10.", 900, 830, 150, RED, at=S.c("it's") - 0.05, rot=-3, cps=20)


@V.scene("o3")
def _(S):
    lx, ly = 560, 700
    S.draw(laptop(lx, ly, 1.3) + [Fl(P_rect(lx - 205, ly - 270, 410, 240, 0, r=6), (150, 186, 214))], S.l(0) + 0.05, 0.35)
    S.text("not an accident.", 200, 230, 110, INK, at=S.c("accident") - 0.5)
    S.pop(tag(lx - 100, ly - 190, 0.8, "€9.99", HL, 60), S.c("prices") - 0.1, (lx - 100, ly - 190), snd=None)
    for k, lab in enumerate("AB"):
        bx = lx + 40 + k * 80
        S.draw([Fl(P_rect(bx, ly - 230, 70, 60, 0, r=12), (250, 248, 242)), stk(P_rect(bx, ly - 230, 70, 60, 4, r=12), 4.5)],
               S.c("buttons") - 0.1 + 0.15 * k, 0.2, snd=None)
        S.text(lab, bx + 35, ly - 180, 60, INK, at=S.c("buttons") + 0.15 * k, anchor="m")
    S.draw(clock(lx + 120, ly - 100, 0.45, hh=-20, mm=90), S.c("timers") - 0.15, 0.3, snd=None)
    S.text("× millions of people", 240, 370, 92, INK, at=S.c("millions") - 0.3)
    S.draw(brain(1400, 580, 0.85), S.c("brain") - 0.3, 0.5)
    S.draw([stk(P_ell(1400, 580, 250, 225, 7, 0.08), 7), stk(P_line(1580, 760, 1720, 870, 0.02, 2), 14)], S.c("test", 0, 1) - 0.2, 0.4)
    S.text("the real test subject", 200, 830, 88, ORANGE, at=S.c("brain") - 0.3, cps=34)
    S.add(arrow(P_bez((950, 800), (1050, 770), (1140, 700)), S.c("brain") + 0.3, ORANGE, 6, 0.3))


@V.scene("o5")
def _(S):
    S.pop(tag(1180, 520, 1.6, "€9.99"), 0.1, (1180, 520))
    S.add(Fig(520, 950, 1.3, at=0.0, poses=[("hold_r", 0)], moods=[("o", 0), ("smug", S.c("stop") - 0.2)], seed=3))
    S.draw([stk(P_ell(860, 520, 120, 120, 3, 0.08), 9), stk(P_line(780, 610, 690, 710, 0.02, 2), 14)], 0.2, 0.4)
    S.text("seen = disarmed.", 820, 820, 100, ORANGE, at=S.c("stop") - 0.2, rot=-3)


@V.scene("o6")
def _(S):
    S.noframe = True
    S.text("7", 430, 640, 440, ORANGE, at=S.c("seven") - 0.05, anchor="m", rot=-6, cps=8)
    S.text("tricks", 640, 520, 160, INK, at=S.c("seven") + 0.2)
    S.text("+ how to beat each one", 640, 700, 84, GREY, at=S.c("beat") - 0.2)
    S.add(Fig(1680, 950, 1.2, at=0.0, poses=[("stand", 0), ("wave", S.c("beat"))], moods=[("smile", 0), ("happy", S.c("beat"))], seed=3, flip=True))


V.chapters({1: ("The price that\nends in 9.", 0), 2: ("The decoy.", 1), 3: ("The fake\ncountdown.", 0), 4: ("The fake\ndiscount.", 1),
            5: ("Free\nshipping.", 0), 6: ("Buy now,\npay later.", 1), 7: ("The store\nmap.", 0)}, peek={1, 3, 5, 6, 7})


# --------------------------------------------------------------------------- 1. the price that ends in 9
@V.scene("c1a")
def _(S):
    S.pop(tag(600, 480, 2.2, "€9.99", HL, 150), S.l(0) + 0.05, (600, 480))
    S.text("feels like 9", 260, 860, 100, INK, at=S.c("nine") - 0.2)
    S.text("is 10", 820, 860, 100, ORANGE, at=S.c("ten") - 0.1)
    S.add(circ(560, 500, 70, 90, S.c("first") - 0.1, RED, 7))
    S.text("first digit", 1200, 300, 80, RED, at=S.c("digit") - 0.2, rot=-3)
    S.add(arrow(P_bez((1190, 320), (900, 300), (660, 420)), S.c("digit"), RED, 6, 0.35))
    S.add(Fig(1550, 960, 1.15, at=0.0, poses=[("stand", 0), ("point_l", S.c("first"))], moods=[("smile", 0), ("smug", S.c("stops"))], seed=3, flip=True))


@V.scene("c1b")
def _(S):
    S.draw(dress(300, 560, 1.4), 0.0, 0.5)
    S.text("US catalogue test, in $", 140, 220, 76, GREY, at=S.c("us") - 0.1)
    base = 750
    vals = [(S.c("$34"), "$34", 100, PALE), (S.c("$39"), "$39", 133, ORANGE), (S.c("$44", 1), "$44", 100, PALE)]
    S.draw([stk(P_line(640, base, 1780, base, 0.005, 1), 7)], S.c("$34") - 0.2, 0.3, snd=None)
    for k, (at, lab, v, col) in enumerate(vals):
        x = 720 + k * 360
        h = v * 3.2
        fp = Path(P_rect(x, base - h, 220, h, 0), 70 + k, wob=0.8)
        op = Path(P_poly([(x, base), (x, base - h), (x + 220, base - h), (x + 220, base)]), 80 + k)

        def fn(ctx, t, at=at, fp=fp, op=op, k=k, col=col):
            if t < at:
                return
            u = ease_back(clamp((t - at) / 0.5), 1.1)
            ctx.save()
            ctx.translate(0, base)
            ctx.scale(1, max(0.01, u))
            ctx.translate(0, -base)
            fill(ctx, fp, boil(t), col if k != 1 else ORANGE, 1.0, (3, -2))
            stroke(ctx, op, boil(t), 6.5, INK)
            ctx.restore()
        S.add(fn)
        S.pop(tag(x + 110, base + 75, 0.75, lab, HL, 66), at, (x + 110, base + 75), snd=None)
    S.text("+1/3 sales", 1040, 290, 100, ORANGE, at=S.c("third") - 0.2, rot=-3)
    S.text("same as $34", 1400, 395, 76, GREY, at=S.c("same", 1) - 0.1)


@V.scene("c1c")
def _(S):
    S.text("the fix:", 200, 220, 84, GREY, at=S.c("fix") - 0.1)
    S.text("round up.", 520, 220, 120, INK, at=S.c("round") - 0.1, rot=-2)
    S.add(under(530, 520 + text_w("round up.", 120), 250, S.c("up") + 0.1, ORANGE, 8))
    S.pop(tag(1450, 330, 1.4, "€9.99", HL, 96), S.c("fix") - 0.05, (1450, 330))
    S.text("in your head", 1300, 560, 84, GREY, at=S.c("head") - 0.2, rot=-3)
    rows = ((S.c("€9.99"), "€9.99", "€10"), (S.c("€49.95"), "€49.95", "€50"))
    for k, (at, a, b) in enumerate(rows):
        y = 500 + k * 240
        S.text(a, 220, y, 130, INK, at=at - 0.1)
        S.add(arrow(P_line(700, y - 40, 880, y - 40, 0.03, k), at + 0.3, INK, 6, 0.3))
        S.text(b, 940, y, 150, ORANGE, at=at + 0.6)


# --------------------------------------------------------------------------- 2. the decoy
@V.scene("c2a")
def _(S):
    S.draw(magazine(230, 250, 0.85), S.l(0) + 0.05, 0.4)
    S.text("a magazine's offer", 360, 230, 84, INK, at=S.c("magazine") - 0.1)
    S.text("(US, in $)", 380, 320, 70, GREY, at=S.c("three") - 0.1)
    for k, x in enumerate((330, 960, 1590)):
        S.draw([Fl(P_rect(x - 200, 430, 400, 340, 0, r=22), (250, 248, 242)), stk(P_rect(x - 200, 430, 400, 340, 9, r=22), 8)],
               S.c("three") - 0.1 + 0.15 * k, 0.3, snd="scr" if k == 0 else None)
    cards = ((S.c("online"), "online", "$59", 330), (S.c("print"), "print only", "$125", 960), (S.c("print", 0, 1), "print + online", "$125", 1590))
    for at, top, price, x in cards:
        S.text(top, x, 540, 70, INK, at=at - 0.1, anchor="m")
        S.text(price, x, 690, 130, INK, at=at + 0.15, anchor="m")
    S.add(cross(960, 600, 160, S.c("nobody", 1) + 0.1, RED, 10))
    S.text("decoy", 870, 850, 96, RED, at=S.c("nobody", 1) + 0.3, rot=-4)
    S.add(circ(1590, 600, 245, 192, S.c("bundle", 1) - 0.1, ORANGE, 8))
    S.text("\"what a deal!\"", 1540, 860, 80, ORANGE, at=S.c("bundle", 1) - 0.3, rot=3, anchor="m", cps=34)


@V.scene("c2b")
def _(S):
    S.draw([Fl(P_rect(1120, 230, 620, 300, 0, r=10), (70, 92, 80)), stk(P_rect(1120, 230, 620, 300, 10, r=10), 9)], S.l(0) + 0.05, 0.4,
           until=S.l(1) - 0.3)
    S.text("class\nexperiment", 1430, 350, 96, (250, 248, 242), at=S.c("class") - 0.1, anchor="m", until=S.l(1) - 0.3)
    S.text("with the decoy", 250, 200, 80, INK, at=S.c("famous") - 0.1)
    S.add(*bars(260, 760, [84, 16], ["", ""], S.c("84%") - 0.1, step=0.4, maxh=440, bw=170, gap=90, cols=[ORANGE, PALE],
                txt=["84%", "16%"], seed=21, size=78))
    for k, lab in enumerate(("bundle", "online")):          # bars() writes its labels at 52 px: ours are phone-sized
        S.text(lab, 260 + k * 260 + 85, 835, 66, INK, at=S.c("84%") + 0.15 + 0.4 * k, anchor="m")
    S.draw([stk(P_line(960, 200, 965, 860, 0.01, 2), 5, GREY)], S.l(1) - 0.2, 0.3, snd=None)
    S.text("without it", 1110, 200, 80, INK, at=S.c("removed", 1) - 0.4)
    S.add(*bars(1130, 760, [32, 68], ["", ""], S.c("68%", 1) - 0.1, step=0.4, maxh=440 * 68 / 84, bw=170, gap=90, cols=[PALE, ORANGE],
                txt=["32%", "68%"], seed=22, size=78))
    for k, lab in enumerate(("bundle", "online")):
        S.text(lab, 1130 + k * 260 + 85, 835, 66, INK, at=S.c("68%", 1) + 0.15 + 0.4 * k, anchor="m")


@V.scene("c2c")
def _(S):
    S.text("the fix:", 160, 190, 84, GREY, at=S.c("fix") - 0.1)
    for k, x in enumerate((420, 960, 1500)):
        S.draw(price_card(x, 650, ["A", "B", "C"][k], "?", 1.1), S.c("fix") + 0.1 + 0.15 * k, 0.3, snd="scr" if k == 0 else None)
    S.text("which one is only there to push you?", 470, 190, 76, INK, at=S.c("which") - 0.1)
    S.add(cross(960, 650, 130, S.c("push") - 0.1, RED, 10))
    S.add(arrow(P_bez((520, 470), (960, 340), (1400, 470)), S.c("compare"), ORANGE, 7, 0.45))
    S.text("compare these two", 720, 380, 76, ORANGE, at=S.c("compare") + 0.2)


# --------------------------------------------------------------------------- 3. the fake countdown
@V.scene("c3a")
def _(S):
    px, py = 480, 560
    S.draw(phone(px, py, 1.7), 0.0, 0.5)
    S.text("only 2 left!", px, py - 140, 62, RED, at=S.c("two") - 0.1, anchor="m")
    S.add(countdown(px, py - 10, 100, S.c("minutes") - 0.3))
    S.draw([Fl(P_rect(px - 140, py + 120, 520, 150, 0, r=18), HL), stk(P_rect(px - 140, py + 120, 520, 150, 6, r=18), 6)], S.c("someone") - 0.1, 0.25)
    S.text("someone in Paris\njust bought this", px + 120, py + 185, 60, INK, at=S.c("paris") - 0.1, anchor="m")
    brain_switch(S, 1250, 560, S.c("switches", 1) + 0.2)
    S.text("slow, careful thinking", 1080, 300, 76, GREY, at=S.c("slow", 1) - 0.1)
    S.text("OFF", 1520, 740, 120, RED, at=S.c("switches", 1) + 0.25, rot=-6)


@V.scene("c3b")
def _(S):
    S.text("EU check, 2023", 1150, 200, 90, INK, at=S.c("check") - 0.2)
    gx, gy, n = 220, 150, 40
    t_in = S.l(0) + 0.1
    for k in range(n):
        x, y = gx + (k % 10) * 82, gy + (k // 10) * 110
        bad = k in (1, 4, 6, 9, 12, 15, 17, 21, 24, 27, 30, 33, 35, 38, 39)
        S.draw([Fl(P_rect(x, y, 62, 76, 0, r=6), (250, 248, 242)), stk(P_rect(x, y, 62, 76, 4, r=6), 4.5)], t_in + 0.05 * k, 0.18,
               snd="scr" if k == 0 else None)
        if bad:
            S.draw([Fl(P_rect(x, y, 62, 76, 0, r=6), (236, 160, 150)), stk(P_rect(x, y, 62, 76, 4, r=6), 4.5)], S.c("148") - 0.1 + 0.03 * k, 0.18,
                   snd=None)
    S.text("399 shops checked", 220, 690, 84, INK, at=S.c("399") - 0.1)
    S.text("148 with tricks", 220, 800, 84, RED, at=S.c("148") - 0.1)
    S.draw(clock(1450, 470, 1.4, hh=-20, mm=90), S.c("42", 1) - 0.3, 0.4)
    S.text("FAKE", 1300, 490, 150, RED, at=S.c("fake", 1) - 0.1, rot=-14)
    S.text("42 fake timers", 1210, 780, 90, INK, at=S.c("42", 1) + 0.2)


@V.scene("c3c")
def _(S):
    S.text("the fix:", 200, 200, 84, GREY, at=S.c("fix") - 0.1)
    S.draw([Fl(P_rect(820, 110, 400, 160, 0, r=20), HL), stk(P_rect(820, 110, 400, 160, 7, r=20), 7)], S.l(0) + 0.05, 0.3)
    S.add(countdown(1020, 230, 110, S.l(0) + 0.2, stop=S.c("wait") + 0.1))
    S.text("hurry?", 360, 450, 130, RED, at=S.c("hurry") - 0.35, rot=-3, cps=34)
    S.add(cross(1020, 190, 90, S.c("wait") + 0.15, RED, 10))
    S.text("wait.", 420, 650, 170, ORANGE, at=S.c("wait") - 0.3, rot=-3, cps=30)
    S.draw([Fl(P_bez((1580, 210), (1410, 290), (1420, 550), (1640, 610)).tolist() + P_bez((1640, 610), (1500, 510), (1480, 330), (1580, 210)).tolist(),
               HL), stk(np.vstack([P_bez((1580, 210), (1410, 290), (1420, 550), (1640, 610)), P_bez((1640, 610), (1500, 510), (1480, 330), (1580, 210))]), 6)],
           S.c("night") - 0.4, 0.5)
    S.text("Z", 1700, 300, 96, GREY, at=S.c("sleep") - 0.1)
    S.text("a real deal survives\na night of sleep.", 860, 700, 76, INK, at=S.c("real") - 0.1)


# --------------------------------------------------------------------------- 4. the fake discount
@V.scene("c4a")
def _(S):
    S.pop(tag(560, 420, 1.9, "€199", HL, 110), S.c("€199") - 0.1, (560, 420))
    S.add(strike(400, 400, 760, 380, S.c("now") - 0.1, RED, 9))
    S.text("€99", 380, 760, 220, ORANGE, at=S.c("€99") - 0.1, rot=-4, cps=10)
    S.text("-50%!", 760, 700, 110, RED, at=S.c("half") - 0.1, rot=8)
    S.text("ever?", 1000, 300, 96, GREY, at=S.c("ever") - 0.1, rot=4)
    S.draw(anchor_shape(1480, 560, 1.4), S.c("anchor", 1) - 0.3, 0.6)
    S.text("€199", 1540, 370, 84, INK, at=S.c("anchor", 1) + 0.2)
    S.text("the anchor", 1330, 860, 84, INK, at=S.c("anchor", 1) + 0.1)


@V.scene("c4b")
def _(S):
    t1 = S.l(1) - 0.1
    S.draw([Fl(P_rect(1220, 240, 560, 120, 0, r=14), HL), stk(P_rect(1220, 240, 560, 120, 6, r=14), 6)], S.l(0) + 0.05, 0.3, until=t1)
    S.text("EU rule since 2022", 1500, 325, 76, INK, at=S.c("since") - 0.2, anchor="m", until=t1)
    x0, y0, x1, y1 = 240, 380, 1100, 840
    S.draw([stk(P_line(x0, y1, x1, y1, 0.005, 1), 6), stk(P_line(x0, y1, x0 + 2, y0, 0.005, 2), 6)], S.l(0) + 0.1, 0.3, snd=None)
    pr = [150, 150, 150, 120, 120, 199, 199, 99]
    pts = []
    for k, p in enumerate(pr):
        x = x0 + 30 + k * (x1 - x0 - 60) / (len(pr) - 1)
        pts.append((x, y1 - 20 - p * 2.0))
    S.draw([stk(P_poly(pts), 8, INK)], S.l(0) + 0.4, 1.8)
    S.text("€199", pts[5][0] - 30, pts[5][1] - 30, 76, INK, at=S.l(0) + 1.7)
    S.text("€99", pts[7][0] - 150, pts[7][1] + 40, 76, INK, at=S.l(0) + 2.1)
    S.add(circ(pts[3][0] + 50, pts[3][1], 110, 50, S.c("lowest") - 0.1, ORANGE, 6))
    S.text("lowest in 30 days: €120", 280, 300, 72, INK, at=S.c("thirty") - 0.2)
    S.text("real discount:", 1200, 300, 84, INK, at=S.c("real", 1) - 0.3)
    S.text("-17%", 1230, 490, 170, ORANGE, at=S.c("17%", 1) - 0.15, cps=12)
    S.text("(not -50%)", 1240, 565, 66, RED, at=S.c("50%", 1) - 0.1)
    S.draw([Fl(P_rect(1150, 600, 690, 230, 0, r=14), (250, 248, 242)), stk(P_rect(1150, 600, 690, 230, 6, r=14), 6)], S.l(2) + 0.05, 0.3)
    S.text("€99", 1200, 700, 96, INK, at=S.c("small", 2) - 0.2)
    S.text("lowest 30-day price: €120", 1190, 790, 60, INK, at=S.c("line", 2) - 0.1)
    S.add(under(1190, 1815, 806, S.c("line", 2) + 0.3, RED, 5))


# --------------------------------------------------------------------------- 5. free shipping
@V.scene("c5a")
def _(S):
    S.draw(parcel(1080, 660, 1.0), S.l(0) + 0.05, 0.35)
    S.text("shipping: €4.90", 900, 540, 76, INK, at=S.c("€4.90") - 0.3)
    S.draw(cart(380, 660, 1.2), 0.1, 0.4, snd=None)
    S.draw([Fl(P_rect(820, 180, 900, 120, 0, r=20), HL), stk(P_rect(820, 180, 900, 120, 8, r=20), 7)], S.c("free") - 0.3, 0.35)
    S.text("FREE shipping above €50", 1270, 262, 72, INK, at=S.c("free") - 0.1, anchor="m")
    mx0, my, sc_ = 820, 360, 15                          # basket meter: €0..€60
    S.draw([stk(P_rect(mx0, my, 900, 70, 6, r=12), 6), stk(P_line(mx0 + 50 * sc_, my - 25, mx0 + 50 * sc_, my + 95, 0.01, 4), 7, RED)],
           S.c("free") + 0.3, 0.3, snd=None)
    S.draw([Fl(P_rect(mx0 + 6, my + 8, 38 * sc_ - 6, 54, 0, r=8), (214, 226, 196))], S.c("€38") - 0.2, 0.3, snd=None)
    S.text("€38", 300, 440, 110, INK, at=S.c("€38") - 0.1)
    S.pop(gift(1420, 700, 0.9), S.c("€15", 1) - 0.1, (1420, 700))
    S.add(arrow(P_bez((1320, 720), (900, 820), (540, 660)), S.c("add", 1), INK, 6, 0.4))
    S.draw([Fl(P_rect(mx0 + 38 * sc_, my + 8, 15 * sc_, 54, 0, r=8), ORANGE)], S.c("€15", 1) + 0.3, 0.3, snd=None)
    S.add(strike(290, 410, 480, 400, S.c("€15", 1) + 0.4, RED, 8))
    S.text("€53", 500, 440, 110, ORANGE, at=S.c("€15", 1) + 0.5)
    S.text("+€15 unplanned", 1250, 830, 76, RED, at=S.c("plan", 1) - 0.1)


@V.scene("c5b")
def _(S):
    S.draw(gift(1500, 320, 1.0), 0.0, 0.3, snd=None)
    S.text("+€15 to save €4.90", 260, 340, 110, INK, at=S.c("spent") - 0.3)
    S.text("= €10.10 more spent.", 280, 560, 140, RED, at=S.c("€10") - 0.2, rot=-3, cps=14)
    S.text("the fix: pay the shipping,\nor wait.", 300, 760, 84, ORANGE, at=S.c("fix", 1) - 0.1)
    S.add(Fig(1550, 950, 1.2, at=0.0, poses=[("shrug", 0), ("hips", S.l(1))], moods=[("worried", 0), ("smug", S.l(1))], seed=3, flip=True))


# --------------------------------------------------------------------------- 6. buy now, pay later
@V.scene("c6a")
def _(S):
    for k in range(4):
        S.pop(coin(240 + k * 150, 360, 1.3, col=HL), S.c("four") + 0.1 * k, (240 + k * 150, 360), snd="pop" if k == 0 else None)
    S.text("4 × €25", 230, 560, 96, INK, at=S.c("€25") - 0.1)
    S.pop(coin(1060, 360, 2.2), S.c("€100") - 0.1, (1060, 360))
    S.text("1 × €100", 940, 560, 96, INK, at=S.c("€100") + 0.1)
    S.text("= the same €100", 1300, 380, 76, ORANGE, at=S.c("same") - 0.1)
    x0, x1, y1 = 300, 1340, 860
    S.draw([stk(P_line(x0, y1, x1, y1, 0.005, 1), 6)], S.c("study", 1) - 0.3, 0.3, snd=None)
    pts = [(x0 + 20, y1 - 120), (x0 + 440, y1 - 125), (x0 + 460, y1 - 160), (x1 - 30, y1 - 155)]
    S.draw([stk(P_poly(pts), 8, RED)], S.c("start", 1) - 0.2, 0.6)
    S.text("first use", x0 + 470, y1 - 50, 70, INK, at=S.c("start", 1))
    S.text("spending: up, and stays up", 560, y1 - 215, 70, RED, at=S.c("stays", 1) - 0.2)
    S.text("(sketch,\nnot to scale)", x1 + 50, y1 - 120, 70, GREY, at=S.c("start", 1) + 0.6)


@V.scene("c6b")
def _(S):
    S.draw(rulebook(1500, 470, 1.15), S.l(0) + 0.05, 0.45)
    S.text("new EU credit rules", 200, 250, 100, INK, at=S.c("rules") - 0.3)
    S.text("from 20 Nov 2026", 240, 360, 84, GREY, at=S.c("november") - 0.3)
    S.text("\"can you afford it?\" checks", 240, 480, 80, ORANGE, at=S.c("afford") - 0.4)
    S.text("can't pay today?", 260, 650, 110, INK, at=S.c("pay", 1) - 0.1)
    S.text("can't afford today.", 480, 790, 110, RED, at=S.c("afford", 1) - 0.2, rot=-2)


# --------------------------------------------------------------------------- 7. the store map
@V.scene("c7a")
def _(S):
    S.noframe = True
    sx, sy, sw, sh = 220, 110, 1000, 600
    S.draw([stk(P_rect(sx, sy, sw, sh, 8), 7)], 0.0, 0.5, snd=None)
    for k in range(4):
        ax = sx + 160 + k * 200
        S.draw([Fl(P_rect(ax, sy + 180, 70, 280, 0), (196, 186, 166)), stk(P_rect(ax, sy + 180, 70, 280, 4), 5)], 0.2 + 0.08 * k, 0.25, snd=None)
    S.draw([Fl(P_rect(sx + 560, sy + 25, 400, 110, 0, r=10), (214, 226, 196)), stk(P_rect(sx + 560, sy + 25, 400, 110, 4, r=10), 5)], S.c("milk") - 0.2, 0.3)
    S.text("milk & bread", sx + 760, sy + 100, 66, INK, at=S.c("milk"), anchor="m")
    S.text("entrance", sx + 10, sy + sh + 85, 70, INK, at=S.c("back") - 0.2)
    path = [(sx + 80, sy + sh - 20), (sx + 110, sy + 150), (sx + 300, sy + 140), (sx + 310, sy + sh - 100), (sx + 500, sy + sh - 100),
            (sx + 510, sy + 160), (sx + 760, sy + 150)]
    S.add(arrow(P_poly(path), S.c("walk") - 0.2, ORANGE, 6, 1.0, dashed=True))
    cx, cy = sx + sw - 230, sy + sh - 110
    S.draw([stk(P_rect(cx, cy, 190, 70, 4), 5)], S.c("checkout", 1) - 0.3, 0.3)
    for k in range(3):
        S.pop(candy(cx + 45 + k * 55, cy - 30, 0.55, [PINK, HL, (150, 186, 214)][k]), S.c("sweets", 1) + 0.1 * k, (cx + 45 + k * 55, cy - 30),
              snd="pop" if k == 0 else None)
    S.add(arrow(P_bez((1290, 560), (1200, 600), (1150, 650)), S.c("checkout", 1) + 0.1, RED, 6, 0.3))
    S.text("sweets:\nright here", 1290, 520, 80, RED, at=S.c("checkout", 1))
    S.text("you wait\nhere, bored", 1290, 760, 72, INK, at=S.c("still", 1) - 0.1)


@V.scene("c7b")
def _(S):
    S.noframe = True
    t1 = S.l(1) + 0.1
    S.draw(counter(1250, 560, 1.0), S.l(0) + 0.05, 0.4, until=t1)
    for k in range(4):
        S.pop(candy(1030 + k * 140, 520, 0.9, [PINK, HL, (150, 186, 214), PINK][k]), S.l(0) + 0.3 + 0.08 * k, (1030 + k * 140, 520),
              snd=None, until=t1)
    S.add(until_(cross(1250, 520, 260, S.c("banned") - 0.05, RED, 12), t1))
    S.text("England, 2022:", 200, 260, 96, INK, at=S.c("england") - 0.1, until=t1)
    S.text("no junk snacks at\nbig-store checkouts", 220, 400, 84, GREY, at=S.c("banned") - 0.2, until=t1)
    S.draw(list_paper(560, 560, 1.3) + [Fl(P_rect(365, 300, 390, 60, 0), HL)], S.l(1) - 0.4, 0.45)
    for k in range(4):
        y = 560 - 260 + 117 + k * 97.5
        S.add(check(560 - 195 + 63, y - 6, 18, S.c("straight", 1) + 0.15 * k, GREEN, 7, seed=k))
    S.text("the fix:", 960, 330, 90, GREY, at=S.c("fix", 1) - 0.1)
    S.text("a list,", 980, 520, 140, ORANGE, at=S.c("list", 1) - 0.1, rot=-2)
    S.text("straight to it.", 960, 700, 110, INK, at=S.c("straight", 1) - 0.1, rot=-2)


# --------------------------------------------------------------------------- final message
@V.scene("f0")
def _(S):
    S.draw(envelope(1350, 560, 1.6), 0.0, 0.35, snd=None)
    S.text("final message.", 220, 600, 140, INK, at=0.05, rot=-3, cps=26)
    S.add(under(230, 1040, 640, 0.7, ORANGE, 7, 0.4, wavy=True))


@V.scene("f1")
def _(S):
    for k in range(7):
        x = 230 + k * 230
        S.pop(tag(x, 250, 0.7, str(k + 1), HL, 64), S.l(0) + 0.05 + 0.08 * k, (x, 250), snd="pop" if k == 0 else None)
    for k in (2, 3):
        S.add(cross(230 + k * 230, 250, 70, S.c("banned") + 0.1 + 0.15 * (k - 2), RED, 10))
    for j, k in enumerate((0, 1, 4, 5, 6)):
        S.add(check(230 + k * 230, 330, 28, S.c("legal") + 0.1 + 0.1 * j, GREEN, 9, seed=k))
    S.text("some: banned", 300, 500, 110, RED, at=S.c("banned") - 0.3)
    S.text("most: legal", 340, 660, 110, INK, at=S.c("legal") - 0.3)
    S.text("just very good design.", 380, 820, 110, ORANGE, at=S.c("design") - 0.6, rot=-2)


@V.scene("f2")
def _(S):
    S.draw([Fl(P_rect(180, 110, 560, 120, 0, r=16), HL), stk(P_rect(180, 110, 560, 120, 7, r=16), 7)], 0.0, 0.3)
    S.text("7 fixes", 460, 195, 90, INK, at=0.05, anchor="m")
    items = (("round", "round prices up"), ("decoy", "spot the decoy"), ("timer", "ignore the timer"), ("old", "check the real old price"),
             ("shipping", "pay the shipping"), ("full", "pay in full"), ("list", "bring a list"))
    for k, (w_, lab) in enumerate(items):
        col, row = k // 4, k % 4
        x, y = 200 + col * 860, 360 + row * 160
        at = 0.25 + 0.3 * k                                  # the whole card is up early; each fix gets its tick when she says it
        S.text(f"{k + 1}.", x, y, 80, GREY, at=at - 0.05, cps=40)
        S.text(lab, x + 90, y, 80, INK, at=at, cps=45)
        S.add(check(x + 110 + text_w(lab, 80) + 30, y - 30, 26, S.c(w_) + 0.2, GREEN, 9, seed=k))


@V.scene("f3")
def _(S):
    S.draw(brain(520, 560, 1.4), 0.0, 0.5)
    S.text("not stupid.", 920, 460, 130, INK, at=S.c("stupid") - 0.2, rot=-3)
    S.text("just tested.\nall day.", 960, 680, 100, ORANGE, at=S.c("tested") - 0.1, rot=-3)


@V.scene("end")
def _(S):
    endcard(S, "save money so easily\nit feels illegal.", note="education, not financial advice.")


if __name__ == "__main__":
    V.main()
