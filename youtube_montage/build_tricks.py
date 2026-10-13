"""'7 Tricks Shops Use to Make You Spend More (and How to Beat Them)' (doodle style). Sources in the kit: Anderson & Simester 2003,
Ariely (Economist decoy), EU CPC sweep (Jan 2023), Price Indication Directive art. 6a (Omnibus), Di Maggio, Katz & Williams (NBER w30508),
Directive (EU) 2023/2225, Food (Promotion and Placement) (England) Regulations 2021."""
import numpy as np

from doodle_video import *  # noqa: F401,F403

SAY = {"€9.99": "nine ninety-nine", "$34": "thirty-four dollars", "$39": "thirty-nine dollars", "$44": "forty-four dollars",
       "€49.95": "forty-nine ninety-five", "$59": "fifty-nine dollars", "$125": "a hundred and twenty-five dollars",
       "84%": "eighty-four percent", "68%": "sixty-eight percent", "2023": "twenty twenty-three", "399": "three hundred and ninety-nine",
       "148": "a hundred and forty-eight", "42": "forty-two", "€199": "a hundred and ninety-nine euros", "€99": "ninety-nine euros",
       "2022": "twenty twenty-two", "€4.90": "four euros ninety", "€50": "fifty euros", "€38": "thirty-eight euros", "€15": "fifteen euros",
       "€10": "ten euros", "€25": "twenty-five euros", "€100": "a hundred euros", "2026": "twenty twenty-six", "EU": "E U", "US": "U S"}
V = Video("tricks", say=SAY, seed=11, keys=dict(prog=[(50, 53, 57, 60), (55, 59, 62, 65), (48, 52, 55, 59), (53, 57, 60, 64)],
                                                roots=[38, 43, 36, 41], bpm=84),
          hush=[("And here's the part", "Once you can see")], tape="Final message")
L = V.L

L("o1", "You go online to buy one thing. You leave with four.")
L("o1", "And somehow, it felt like you saved money.")
L("o2", "That's not bad luck. It's design.")
L("o3", "Shops test prices, buttons, colours and timers on millions of people. Your brain is the thing they're testing.")
L("o4", "And here's the part nobody tells you.")
L("o5", "Once you can see the tricks, most of them stop working.")
L("o6", "Here are seven of them, and how to beat each one. Let's begin.")

L("c1", "One. The price that ends in nine.")
L("c1a", "€9.99 feels much closer to nine than to ten. Your brain reads the first digit, and mostly stops there.")
L("c1b", "In one experiment, a clothing catalogue raised the price of a dress from $34 to $39. It sold about a third more.")
L("c1b", "At $44, it sold the same as at $34.")
L("c1c", "The fix: round prices up in your head. €9.99 is ten euros. €49.95 is fifty.")

L("c2", "Two. The decoy.")
L("c2a", "A magazine once offered three options. Online only: $59. Print only: $125. Print and online: $125.")
L("c2a", "Nobody picks print only. It's there to make the bundle look like a steal.")
L("c2b", "In a famous class experiment, 84% of students chose the bundle.")
L("c2b", "When the decoy was removed, 68% chose the cheap online option instead.")
L("c2c", "The fix: when you see three prices, ask which one is only there to push you. Then compare the other two.")

L("c3", "Three. The fake countdown.")
L("c3a", "Only two left. Offer ends in nine minutes. Someone in Paris just bought this.")
L("c3a", "Urgency switches off the slow, careful part of your brain.")
L("c3b", "In a check published in 2023, EU consumer authorities looked at 399 online shops. 148 used at least one manipulative trick.")
L("c3b", "42 of them had countdown timers that were fake.")
L("c3c", "The fix: if a timer says hurry, wait. A real deal survives a night of sleep.")

L("c4", "Four. The fake discount.")
L("c4a", "Was €199. Now €99. Half price! But was it ever really €199?")
L("c4a", "A high before price is an anchor. It makes the new price feel small.")
L("c4b", "In the EU, since 2022, a shop announcing a discount has to compare it with its lowest price in the previous thirty days.")
L("c4b", "So check that small line, or a price tracker, before you believe the percentage.")

L("c5", "Five. Free shipping.")
L("c5a", "Shipping costs €4.90. It's free above €50. Your basket is at €38.")
L("c5a", "So you add a €15 thing you didn't plan to buy, to save €4.90.")
L("c5b", "You just spent €10 more to avoid paying €4.90.")
L("c5b", "The fix: pay the shipping, or wait until you really need more.")

L("c6", "Six. Buy now, pay later.")
L("c6a", "Four payments of €25 feel lighter than one payment of €100. It's the same €100.")
L("c6a", "One large study of US bank data found that once people start using buy now, pay later, their total spending goes up, and stays up for months.")
L("c6b", "New EU consumer credit rules, due to apply from November 2026, bring most buy now, pay later under credit rules, with checks on whether you can afford it.")
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


# --------------------------------------------------------------------------- cold open
@V.scene("o1")
def _(S):
    S.draw(laptop(520, 600, 1.2), 0.0, 0.5)
    S.text("1 thing", 400, 280, 90, INK, at=S.c("one") - 0.1)
    S.add(Fig(1320, 950, 1.25, at=0.0, poses=[("stand", 0), ("hold", S.c("four") - 0.2)], moods=[("smile", 0), ("happy", S.c("four"))], seed=3))
    for k, (x, y) in enumerate(((1130, 790), (1520, 790), (1200, 900), (1450, 910))):
        S.pop(bag(x, y, 0.8, [(214, 226, 196), HL, PINK, (150, 186, 214)][k]), S.c("four") + 0.12 * k, (x, y), snd="pop" if k == 0 else None)
    S.text("4 things", 1020, 330, 110, ORANGE, at=S.c("four") + 0.1, rot=-4)
    S.text("\"I saved money!\"", 820, 470, 70, GREY, at=S.c("saved", 1) - 0.2, rot=3)


@V.scene("o2")
def _(S):
    S.text("bad luck", 300, 420, 130, INK, at=S.c("bad") - 0.2)
    S.add(strike(280, 380, 300 + text_w("bad luck", 130), 372, S.c("luck") + 0.3, RED, 10))
    S.text("design.", 600, 760, 220, ORANGE, at=S.c("design") - 0.2, rot=-4, cps=12)
    S.draw([stk(P_line(1400, 860, 1700, 380, 0.01, 3), 10), stk(P_poly([(1700, 380), (1680, 340), (1730, 330)], True), 6)], S.c("design") + 0.3, 0.4)


@V.scene("o3")
def _(S):
    lx, ly = 560, 640
    S.draw(laptop(lx, ly, 1.4), 0.0, 0.5)
    for k, (lab, pct, col) in enumerate((("A", "2.1%", HL), ("B", "3.4%", ORANGE))):
        bx = lx - 150 + k * 170
        S.draw([Fl(P_rect(bx, ly - 230, 130, 70, 0, r=14), col), stk(P_rect(bx, ly - 230, 130, 70, 5, r=14), 5)], S.c("buttons") + 0.15 * k, 0.25, snd=None)
        S.text(lab, bx + 65, ly - 178, 52, INK, at=S.c("buttons") + 0.15 * k + 0.1, anchor="m")
        S.text(pct, bx + 65, ly - 100, 48, GREY, at=S.c("timers") + 0.15 * k, anchor="m")
    S.text("tested on millions", 300, 220, 76, GREY, at=S.c("millions") - 0.2)
    S.draw(brain(1380, 560, 0.95), S.c("brain") - 0.3, 0.5)
    S.draw([stk(P_ell(1380, 560, 280, 250, 7, 0.08), 7), stk(P_line(1580, 760, 1760, 960, 0.02, 2), 14)], S.c("testing") - 0.3, 0.4)
    S.text("the real test subject", 1080, 980, 66, ORANGE, at=S.c("testing") - 0.1)


@V.scene("o4")
def _(S):
    S.add(Fig(980, 1520, 3.2, at=0.0, poses=[("stand", 0)], moods=[("smug", 0)], enter="none", seed=3, idle=0.6, look=0.4))
    S.text("psst.", 1430, 320, 96, GREY, at=S.c("part") - 0.2, rot=8)


@V.scene("o5")
def _(S):
    S.pop(tag(1180, 520, 1.6, "€9.99"), 0.1, (1180, 520))
    S.add(Fig(520, 950, 1.3, at=0.0, poses=[("hold_r", 0)], moods=[("o", 0), ("smug", S.c("stop") - 0.2)], seed=3))
    S.draw([stk(P_ell(860, 520, 120, 120, 3, 0.08), 9), stk(P_line(780, 610, 690, 710, 0.02, 2), 14)], 0.2, 0.4)
    S.text("seen = disarmed.", 820, 920, 96, ORANGE, at=S.c("stop") - 0.2, rot=-3)


@V.scene("o6")
def _(S):
    S.text("7", 300, 600, 380, ORANGE, at=S.c("seven") - 0.05, anchor="m", rot=-6, cps=8)
    S.text("tricks", 470, 520, 130, INK, at=S.c("seven") + 0.2)
    S.text("+ how to beat each one", 490, 680, 76, GREY, at=S.c("beat") - 0.2)
    S.add(Fig(1550, 950, 1.2, at=0.0, poses=[("stand", 0), ("wave", S.c("begin"))], moods=[("smile", 0), ("happy", S.c("begin"))], seed=3, flip=True))


V.chapters({1: ("The price that\nends in 9.", 0), 2: ("The decoy.", 1), 3: ("The fake\ncountdown.", 0), 4: ("The fake\ndiscount.", 1),
            5: ("Free\nshipping.", 0), 6: ("Buy now,\npay later.", 1), 7: ("The store\nmap.", 0)}, peek={1, 3, 6})


# --------------------------------------------------------------------------- 1. the price that ends in 9
@V.scene("c1a")
def _(S):
    S.pop(tag(600, 480, 2.2, "€9.99", HL, 150), S.c("€9.99") - 0.1, (600, 480))
    S.text("feels like 9", 260, 860, 100, INK, at=S.c("nine") - 0.2)
    S.text("is 10", 820, 860, 100, ORANGE, at=S.c("ten") - 0.1)
    S.add(circ(560, 500, 70, 90, S.c("first") - 0.1, RED, 7))
    S.text("first digit", 1200, 300, 80, RED, at=S.c("digit") - 0.2, rot=-3)
    S.add(arrow(P_bez((1190, 320), (900, 300), (660, 420)), S.c("digit"), RED, 6, 0.35))
    S.add(Fig(1550, 960, 1.15, at=0.0, poses=[("stand", 0), ("point_l", S.c("first"))], moods=[("smile", 0), ("smug", S.c("stops"))], seed=3, flip=True))


@V.scene("c1b")
def _(S):
    S.draw(dress(300, 560, 1.4), 0.0, 0.5)
    S.text("clothing catalogue", 140, 220, 66, GREY, at=S.c("catalogue") - 0.2)
    base = 900
    vals = [(S.c("$34"), "$34", 100, PALE), (S.c("$39"), "$39", 133, ORANGE), (S.c("$44", 1), "$44", 100, PALE)]
    S.draw([stk(P_line(640, base, 1780, base, 0.005, 1), 7)], S.c("$34") - 0.2, 0.3, snd=None)
    for k, (at, lab, v, col) in enumerate(vals):
        x = 720 + k * 360
        h = v * 4.2
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
        S.pop(tag(x + 110, base + 90, 0.55, lab, HL, 46), at, (x + 110, base + 90), snd=None)
    S.text("+1/3 sales", 1040, 260, 96, ORANGE, at=S.c("third") - 0.2, rot=-3)
    S.text("same as $34", 1400, 420, 64, GREY, at=S.c("same", 1) - 0.1)


@V.scene("c1c")
def _(S):
    S.text("the fix:", 200, 220, 80, GREY, at=S.c("fix") - 0.1)
    S.text("round up.", 500, 220, 110, ORANGE, at=S.c("round") - 0.1, rot=-2)
    rows = ((S.c("€9.99"), "€9.99", "€10"), (S.c("€49.95"), "€49.95", "€50"))
    for k, (at, a, b) in enumerate(rows):
        y = 520 + k * 260
        S.text(a, 300, y, 130, INK, at=at - 0.1)
        S.add(arrow(P_line(780, y - 40, 1000, y - 40, 0.03, k), at + 0.3, INK, 6, 0.3))
        S.text(b, 1060, y, 150, ORANGE, at=at + 0.5)


# --------------------------------------------------------------------------- 2. the decoy
@V.scene("c2a")
def _(S):
    cards = ((S.c("online"), "online", "$59", 330), (S.c("print"), "print only", "$125", 960), (S.c("print", 0, 1), "print + online", "$125", 1590))
    for k, (at, top, price, x) in enumerate(cards):
        S.draw(price_card(x, 520, top, price, 1.35), at - 0.15, 0.4)
    S.add(cross(960, 520, 160, S.c("nobody", 1) + 0.1, RED, 10))
    S.text("decoy", 870, 820, 90, RED, at=S.c("nobody", 1) + 0.3, rot=-4)
    S.add(circ(1590, 520, 250, 230, S.c("bundle", 1) - 0.1, ORANGE, 8))
    S.text("\"what a deal!\"", 1440, 860, 66, ORANGE, at=S.c("steal", 1) - 0.1, rot=3)


@V.scene("c2b")
def _(S):
    S.text("with the decoy", 250, 200, 76, INK, at=S.c("84%") - 0.6)
    S.add(*bars(260, 820, [84, 16], ["bundle", "online"], S.c("84%") - 0.1, step=0.4, maxh=480, bw=170, gap=90, cols=[ORANGE, PALE],
                txt=["84%", "16%"], seed=21, size=70))
    S.draw([stk(P_line(960, 200, 965, 900, 0.01, 2), 5, GREY)], S.l(1) - 0.2, 0.3, snd=None)
    S.text("without it", 1110, 200, 76, INK, at=S.c("removed", 1) - 0.4)
    S.add(*bars(1130, 820, [32, 68], ["bundle", "online"], S.c("68%", 1) - 0.1, step=0.4, maxh=480 * 68 / 84, bw=170, gap=90, cols=[PALE, ORANGE],
                txt=["32%", "68%"], seed=22, size=70))


@V.scene("c2c")
def _(S):
    S.text("the fix:", 200, 220, 80, GREY, at=S.c("fix") - 0.1)
    for k, x in enumerate((420, 960, 1500)):
        S.draw(price_card(x, 600, ["A", "B", "C"][k], "?", 1.1), S.c("three") - 0.2 + 0.12 * k, 0.3, snd="scr" if k == 0 else None)
    S.add(cross(960, 600, 130, S.c("push") - 0.1, RED, 10))
    S.text("which one is only there to push you?", 280, 960, 70, INK, at=S.c("which") - 0.1)
    S.add(arrow(P_bez((520, 380), (960, 240), (1400, 380)), S.c("compare"), ORANGE, 7, 0.45))
    S.text("compare these two", 760, 300, 64, ORANGE, at=S.c("compare") + 0.2)


# --------------------------------------------------------------------------- 3. the fake countdown
@V.scene("c3a")
def _(S):
    px, py = 560, 560
    S.draw(phone(px, py, 1.7), 0.0, 0.5)
    S.text("only 2 left!", px, py - 140, 56, RED, at=S.c("two") - 0.1, anchor="m")
    S.text("09:00", px, py - 10, 96, INK, at=S.c("minutes") - 0.3, anchor="m", cps=14)
    S.draw([Fl(P_rect(px - 120, py + 70, 240, 90, 0, r=16), HL), stk(P_rect(px - 120, py + 70, 240, 90, 5, r=16), 5)], S.c("someone") - 0.1, 0.25)
    S.text("someone in Paris\njust bought this", px, py + 108, 30, INK, at=S.c("paris") - 0.1, anchor="m", path=HAND2)
    brain_switch(S, 1200, 560, S.c("switches", 1) + 0.2)
    S.text("slow, careful thinking", 1120, 300, 64, GREY, at=S.c("slow", 1) - 0.1)
    S.text("OFF", 1480, 720, 110, RED, at=S.c("switches", 1) + 0.25, rot=-6)


@V.scene("c3b")
def _(S):
    gx, gy, n = 220, 260, 40
    for k in range(n):
        x, y = gx + (k % 10) * 82, gy + (k // 10) * 120
        bad = k in (1, 4, 6, 9, 12, 15, 17, 21, 24, 27, 30, 33, 35, 38, 39)
        S.draw([Fl(P_rect(x, y, 62, 80, 0, r=6), (244, 214, 210) if bad else (250, 248, 242)), stk(P_rect(x, y, 62, 80, 3, r=6), 4)],
               (S.c("shops") - 0.4 + 0.02 * k) if not bad else (S.c("148") - 0.1 + 0.03 * k), 0.18, snd=None)
    S.text("399 shops checked", 220, 830, 80, INK, at=S.c("399") - 0.1)
    S.text("148 with tricks", 220, 940, 80, RED, at=S.c("148") - 0.1)
    S.draw(clock(1450, 480, 1.4, hh=-20, mm=90), S.c("42", 1) - 0.3, 0.4)
    S.text("FAKE", 1300, 500, 150, RED, at=S.c("fake", 1) - 0.1, rot=-14)
    S.text("42 fake timers", 1250, 800, 84, INK, at=S.c("42", 1) + 0.2)
    S.text("(EU check, 2023)", 1280, 900, 54, GREY, at=S.c("2023") + 0.3)


@V.scene("c3c")
def _(S):
    S.text("the fix:", 200, 220, 80, GREY, at=S.c("fix") - 0.1)
    S.text("hurry?", 360, 450, 130, RED, at=S.c("hurry") - 0.2, rot=-3)
    S.text("wait.", 420, 640, 170, ORANGE, at=S.c("wait") - 0.1, rot=-3)
    S.draw([Fl(P_bez((1460, 300), (1290, 380), (1300, 640), (1520, 700)).tolist() + P_bez((1520, 700), (1380, 600), (1360, 420), (1460, 300)).tolist(),
               HL), stk(np.vstack([P_bez((1460, 300), (1290, 380), (1300, 640), (1520, 700)), P_bez((1520, 700), (1380, 600), (1360, 420), (1460, 300))]), 6)],
           S.c("night") - 0.4, 0.5)
    S.text("Z", 1560, 380, 90, GREY, at=S.c("sleep") - 0.1)
    S.text("a real deal survives\na night of sleep.", 1060, 860, 70, INK, at=S.c("real") - 0.1)


# --------------------------------------------------------------------------- 4. the fake discount
@V.scene("c4a")
def _(S):
    S.pop(tag(560, 420, 1.9, "€199", HL, 110), S.c("€199") - 0.1, (560, 420))
    S.add(strike(400, 400, 760, 380, S.c("now") - 0.1, RED, 9))
    S.text("€99", 380, 760, 220, ORANGE, at=S.c("€99") - 0.1, rot=-4, cps=10)
    S.text("-50%!", 760, 700, 110, RED, at=S.c("half") - 0.1, rot=8)
    S.text("ever?", 1000, 300, 90, GREY, at=S.c("ever") - 0.1, rot=4)
    S.draw(anchor_shape(1480, 560, 1.4), S.c("anchor", 1) - 0.3, 0.6)
    S.text("€199", 1530, 380, 60, INK, at=S.c("anchor", 1) + 0.2)
    S.text("the anchor", 1330, 900, 80, INK, at=S.c("anchor", 1) + 0.1)


@V.scene("c4b")
def _(S):
    x0, y0, x1, y1 = 240, 360, 1100, 860
    S.draw([stk(P_line(x0, y1, x1, y1, 0.005, 1), 6), stk(P_line(x0, y1, x0 + 2, y0, 0.005, 2), 6)], 0.0, 0.3, snd=None)
    pr = [150, 150, 150, 120, 120, 199, 199, 99]
    pts = []
    for k, p in enumerate(pr):
        x = x0 + 30 + k * (x1 - x0 - 60) / (len(pr) - 1)
        pts.append((x, y1 - 20 - p * 2.1))
    S.draw([stk(P_poly(pts), 7, INK)], S.c("lowest") - 1.2, 0.8)
    S.add(circ(pts[3][0] + 50, pts[3][1], 110, 50, S.c("lowest") - 0.1, ORANGE, 6))
    S.text("lowest in 30 days: €120", 280, 300, 70, ORANGE, at=S.c("thirty") - 0.2)
    S.text("EU rule since 2022", 1260, 330, 76, INK, at=S.c("since") - 0.2)
    S.draw([Fl(P_rect(1240, 520, 520, 220, 0, r=14), (250, 248, 242)), stk(P_rect(1240, 520, 520, 220, 6, r=14), 6)], S.c("small", 1) - 0.4, 0.3)
    S.text("€99", 1300, 620, 90, INK, at=S.c("small", 1) - 0.2)
    S.text("lowest 30-day price: €120", 1270, 700, 40, GREY, at=S.c("line", 1) - 0.1, path=HAND2)
    S.add(under(1270, 1700, 715, S.c("line", 1) + 0.3, RED, 5))


# --------------------------------------------------------------------------- 5. free shipping
@V.scene("c5a")
def _(S):
    S.draw(cart(420, 640, 1.2), 0.0, 0.5)
    S.text("€38", 360, 400, 110, INK, at=S.c("€38") - 0.1)
    S.draw([Fl(P_rect(820, 230, 900, 130, 0, r=20), HL), stk(P_rect(820, 230, 900, 130, 8, r=20), 7)], S.c("free") - 0.3, 0.35)
    S.text("FREE shipping above €50", 1270, 320, 70, INK, at=S.c("free") - 0.1, anchor="m")
    S.text("shipping: €4.90", 900, 520, 70, GREY, at=S.c("€4.90") - 0.2)
    S.pop(gift(1180, 760, 1.0), S.c("€15", 1) - 0.1, (1180, 760))
    S.text("+€15 (unplanned)", 1080, 960, 70, RED, at=S.c("plan", 1) - 0.1)
    S.add(arrow(P_bez((1060, 760), (860, 700), (640, 620)), S.c("add", 1), INK, 6, 0.35))


@V.scene("c5b")
def _(S):
    S.text("+€15 to save €4.90", 260, 380, 110, INK, at=S.c("spent") - 0.3)
    S.text("= €10 more spent.", 300, 600, 150, RED, at=S.c("€10") - 0.2, rot=-3, cps=14)
    S.text("the fix: pay the shipping,\nor wait.", 300, 880, 76, ORANGE, at=S.c("fix", 1) - 0.1)
    S.add(Fig(1550, 950, 1.2, at=0.0, poses=[("shrug", 0), ("hips", S.l(1))], moods=[("worried", 0), ("smug", S.l(1))], seed=3, flip=True))


# --------------------------------------------------------------------------- 6. buy now, pay later
@V.scene("c6a")
def _(S):
    for k in range(4):
        S.pop(coin(250 + k * 140, 380, 0.9, col=HL), S.c("four") + 0.1 * k, (250 + k * 140, 380), snd="pop" if k == 0 else None)
    S.text("4 × €25", 250, 560, 90, INK, at=S.c("€25") - 0.1)
    S.pop(coin(1000, 380, 1.9), S.c("€100") - 0.1, (1000, 380))
    S.text("1 × €100", 900, 560, 90, INK, at=S.c("€100") + 0.1)
    S.text("= the same €100", 1260, 400, 70, ORANGE, at=S.c("same") - 0.1)
    x0, y0, x1, y1 = 300, 680, 1500, 1000
    S.draw([stk(P_line(x0, y1, x1, y1, 0.005, 1), 6)], S.c("study", 1) - 0.3, 0.3, snd=None)
    pts = [(x0 + 20, y1 - 80), (x0 + 500, y1 - 90), (x0 + 520, y1 - 230), (x1 - 40, y1 - 220)]
    S.draw([stk(P_poly(pts), 8, RED)], S.c("start", 1) - 0.2, 0.6)
    S.text("first use", x0 + 420, y1 - 260, 52, GREY, at=S.c("start", 1))
    S.text("total spending: up, and stays up", 1000, y1 - 280, 54, RED, at=S.c("stays", 1) - 0.2)


@V.scene("c6b")
def _(S):
    S.text("new EU credit rules", 220, 300, 96, INK, at=S.c("rules") - 0.3)
    S.text("from November 2026", 260, 420, 76, GREY, at=S.c("november") - 0.1)
    S.text("\"can you afford it?\" checks", 260, 560, 76, ORANGE, at=S.c("afford") - 0.4, path=HAND2)
    S.text("can't pay today?", 300, 820, 110, INK, at=S.c("pay", 1) - 0.1)
    S.text("can't afford today.", 520, 960, 110, RED, at=S.c("afford", 1) - 0.2, rot=-2)
    S.add(Fig(1600, 950, 1.15, at=0.0, poses=[("stand", 0), ("cross", S.l(1))], moods=[("flat", 0), ("smug", S.l(1))], seed=3, flip=True))


# --------------------------------------------------------------------------- 7. the store map
@V.scene("c7a")
def _(S):
    sx, sy, sw, sh = 260, 180, 1100, 760
    S.draw([stk(P_rect(sx, sy, sw, sh, 8), 7)], 0.0, 0.5, snd=None)
    for k in range(4):
        ax = sx + 180 + k * 220
        S.draw([Fl(P_rect(ax, sy + 200, 70, 380, 0), PALE), stk(P_rect(ax, sy + 200, 70, 380, 4), 5)], 0.2 + 0.08 * k, 0.25, snd=None)
    S.draw([Fl(P_rect(sx + 700, sy + 30, 360, 100, 0, r=10), (214, 226, 196)), stk(P_rect(sx + 700, sy + 30, 360, 100, 4, r=10), 5)], S.c("milk") - 0.2, 0.3)
    S.text("milk & bread", sx + 880, sy + 95, 52, INK, at=S.c("milk"), anchor="m")
    S.text("entrance", sx + 30, sy + sh + 70, 56, GREY, at=S.c("back") - 0.2)
    path = [(sx + 80, sy + sh - 20), (sx + 120, sy + 150), (sx + 330, sy + 140), (sx + 340, sy + sh - 120), (sx + 560, sy + sh - 120),
            (sx + 570, sy + 160), (sx + 860, sy + 150)]
    S.add(arrow(P_poly(path), S.c("walk") - 0.2, ORANGE, 6, 1.0, dashed=True))
    cx, cy = sx + sw - 220, sy + sh - 110
    S.draw([stk(P_rect(cx, cy, 180, 70, 4), 5)], S.c("checkout", 1) - 0.3, 0.3)
    for k in range(3):
        S.pop(candy(cx + 40 + k * 55, cy - 30, 0.55, [PINK, HL, (150, 186, 214)][k]), S.c("sweets", 1) + 0.1 * k, (cx + 40 + k * 55, cy - 30),
              snd="pop" if k == 0 else None)
    S.text("sweets: right here", 1400, 840, 60, RED, at=S.c("checkout", 1))
    S.text("you wait here, bored", 1400, 930, 50, GREY, at=S.c("still", 1) - 0.1)


@V.scene("c7b")
def _(S):
    S.text("England, 2022:", 220, 260, 86, INK, at=S.c("england") - 0.1)
    S.text("no junk snacks at\nbig-store checkouts", 260, 400, 76, GREY, at=S.c("banned") - 0.2)
    S.draw(list_paper(1380, 520, 1.3), S.c("list", 1) - 0.3, 0.5)
    for k in range(4):
        y = 520 - 260 + 117 + k * 97.5
        S.add(check(1380 - 195 + 63, y - 6, 18, S.c("straight", 1) + 0.15 * k, GREEN, 7, seed=k))
    S.text("the fix: a list,\nstraight to it.", 260, 800, 96, ORANGE, at=S.c("fix", 1) - 0.1)


# --------------------------------------------------------------------------- final message
@V.scene("f0")
def _(S):
    S.text("final message.", 260, 600, 120, INK, at=0.05, rot=-3, cps=20)
    S.add(under(270, 980, 640, 1.0, ORANGE, 7, 0.4, wavy=True))


@V.scene("f1")
def _(S):
    S.text("some: banned", 300, 360, 110, RED, at=S.c("banned") - 0.3)
    S.text("most: legal", 340, 560, 110, INK, at=S.c("legal") - 0.3)
    S.text("just very good design.", 380, 800, 110, ORANGE, at=S.c("design") - 0.6, rot=-2)


@V.scene("f2")
def _(S):
    items = (("round", "round prices up"), ("decoy", "spot the decoy"), ("timer", "ignore the timer"), ("old", "check the real old price"),
             ("shipping", "pay the shipping"), ("full", "pay in full"), ("list", "bring a list"))
    for k, (w_, lab) in enumerate(items):
        col, row = k // 4, k % 4
        x, y = 200 + col * 880, 260 + row * 190
        at = S.c(w_) - 0.2
        S.text(f"{k + 1}.", x, y, 80, ORANGE, at=at - 0.05)
        S.text(lab, x + 90, y, 82, INK, at=at, cps=34)
        S.add(check(x + 110 + text_w(lab, 82) + 30, y - 30, 26, at + 0.55, GREEN, 9, seed=k))


@V.scene("f3")
def _(S):
    S.draw(brain(620, 560, 1.4), 0.0, 0.5)
    S.text("not stupid.", 1060, 460, 130, INK, at=S.c("stupid") - 0.2, rot=-3)
    S.text("just tested.\nall day.", 1100, 680, 96, ORANGE, at=S.c("tested") - 0.1, rot=-3)


@V.scene("end")
def _(S):
    S.text("not financial advice. just education.", 200, 200, 58, GREY, at=S.c("education") - 0.2)
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
