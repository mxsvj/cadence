"""POV survival: 'Your plane goes down in the jungle. Can you survive?' Serious and tense, second person, five stops
('A or B?', three silent seconds, then what each choice does). Facts kept to what the sources support:
staying with the aircraft (easier to spot, shelter, materials; Equipped to Survive / survival manuals), rainwater over
standing water (treat it if you can, let the first runoff go), unknown plants, roughly 3 days without water / weeks
without food, follow water downhill, get into the open to be seen, three of anything = distress.
Ending: Juliane Koepcke (LANSA 508, 24 Dec 1971, fell ~3 km strapped to her seat, followed a stream that became a river,
reached a hut by the river after ~10 days, poured petrol on her maggot-infested arm, found the next day by workers) and the
four Colombian children (Cessna 206, 1 May 2023, 40 days, the eldest 13 fed the others cassava flour and fruit they knew)."""
from story_video import *  # noqa: F401,F403
from doodle_video import stk
from doodle import POSES

NARR = "af_heart"
LEAF, LEAF2, TRUNK, MUD = (110, 160, 90), (78, 128, 72), (120, 90, 62), (150, 120, 80)
WATER, SKY = (130, 176, 214), (214, 226, 232)
WHITE = (250, 248, 242)
DIM = (170, 164, 156)
NIGHT = (24, 23, 28)
POSES["hang"] = dict(la=(150, 170), ra=(-150, -170), ll=(-10, -5), rl=(10, 5), lean=0, tilt=0)        # drawn rotated 180°: arms hang, legs up
POSES["sit_hug"] = dict(la=(40, 120), ra=(-40, -120), ll=(70, 10), rl=(80, 14), lean=-4, tilt=8)

V = Story("jungle", say={"Koepcke": "Kepka"}, beat_groups=(), seed=31,
          hush=[("Stop. What do you do? Option A", "If you chose option A"), ("Stop. Option A: drink", "The puddle is full"),
                ("Stop. Option A: eat", "Some jungle berries"), ("Stop. Option A: climb", "Uphill, the jungle"), ("Stop. Option A: shout", "Under the canopy")],
          tapes=[("Out here, the jungle", "Your Plane Goes Down", "cut"), ("The helicopter turns.", "This is close to", "tape")],
          dips=[("So: how many", None, 0.5)])
L = V.L

# ------------------------------------------------------------------ the crash
L("o1", "You wake up upside down, still strapped into your seat.")
L("o1", "Around you: green. Thick, wet, silent green. The rest of the plane is gone.")
L("o2", "You have a bottle of water, half full. A phone with no signal. And a cut on your arm that won't stop bleeding.")
L("o3", "Out here, the jungle doesn't need to attack you. It just needs you to make one wrong choice.", after=0.8)
L("c1", "Your Plane Goes Down in the Jungle. Can you survive?")
# ------------------------------------------------------------------ 1. stay or go
L("c2", "Hour one.")
L("d1a", "The wreck is still smoking. Your head is pounding. Every instinct says: walk. Find people.")
L("d1", "Stop. What do you do? Option A: walk away and look for help. Or option B: stay with the wreck.", after=2.4)
L("d1x", "If you chose option A, you did what most people would do.")
L("d1x", "Under this canopy, a rescue plane can't see one person. Walk ten minutes in the wrong direction, and you may never find the wreck again.")
L("d1y", "Option B is the better choice. A plane is far bigger than you, and it's what search teams look for first.")
L("d1y", "It's metal for shelter. And if its emergency beacon survived the crash, it may already be calling for help.")
L("d1y", "So you stay. You wait. You listen for engines.")
# ------------------------------------------------------------------ 2. water
L("c3", "Day two.")
L("d2a", "The bottle is empty. The heat sits on your face like a wet towel. Without water, you have roughly three days. This is day two.")
L("d2a", "Next to the wreck there's a puddle. Brown, warm, full of leaves.")
L("d2", "Stop. Option A: drink from the puddle. Or option B: wait for the rain.", after=2.4)
L("d2x", "The puddle is full of bacteria and parasites. By tomorrow you could have diarrhea, and diarrhea drains water out of you faster than the heat.")
L("d2x", "The puddle would make you thirstier.")
L("d2y", "Option B. In a rainforest, it rains often, usually in the afternoon.")
L("d2y", "Spread a sheet of plastic from the cabin, or big leaves. Let the first rinse run off, then fill the bottle.")
L("d2y", "It isn't perfect water. If you can boil it, boil it. But it's far safer than the puddle.")
L("d2y", "At four o'clock, the sky opens.")
# ------------------------------------------------------------------ 3. food
L("c4", "Day three.")
L("d3a", "Nobody has come. Your stomach hurts. On a bush by the wreck: bright red berries. Hundreds of them.")
L("d3", "Stop. Option A: eat the berries. Or option B: eat nothing you don't know.", after=2.4)
L("d3x", "Some jungle berries are food. Some will make you vomit for a day. Out here, vomiting means losing water you can't replace.")
L("d3y", "Option B. A healthy person can last weeks without food. Hunger feels urgent. It isn't. Thirst is.")
L("d3y", "You search the wreck. A bag of crackers. You eat four. You keep the rest.")
# ------------------------------------------------------------------ 4. which way
L("c5", "Day four.")
L("d4a", "The engines never came. The trees hide the wreck, and the cut on your arm is turning red. Staying is now the danger.")
L("d4a", "You have to move. But which way?")
L("d4", "Stop. Option A: climb uphill to see where you are. Or option B: find a stream and follow it downhill.", after=2.4)
L("d4x", "Uphill, the jungle is just as thick. You see more trees, and you've spent water and strength you don't have.")
L("d4y", "Option B. Water runs downhill. Small streams join bigger streams, and bigger streams become rivers. And people live by rivers.")
L("d4y", "You find a trickle of water between the roots. You follow it.")
# ------------------------------------------------------------------ 5. the helicopter
L("c6", "Day seven.")
L("d5a", "The stream is a river now. And then you hear it: a helicopter. Close. Somewhere above the trees.")
L("d5", "Stop. Option A: shout and wave from where you are. Or option B: get out onto the open riverbank and make a signal.", after=2.4)
L("d5x", "Under the canopy, you're invisible. It flies right over you. The sound fades, and doesn't come back.")
L("d5y", "Option B. On the open bank, lay out anything bright you have, as big as you can. Three of anything means help: three piles, three fires.")
L("d5y", "A pilot looking down a river sees the bank, not the forest.")
L("d5y", "The helicopter turns.", after=1.2)
# ------------------------------------------------------------------ it happened
L("t1", "This is close to what really happened to Juliane Koepcke. She was seventeen.")
L("t1", "In 1971, her plane broke apart in a storm over the Peruvian jungle, and she fell about three kilometers, still strapped to her seat.")
L("t2", "Her parents were biologists, and she remembered what her father taught her: follow the water.")
L("t2", "She walked and waded for about ten days, with maggots in a wound on her arm, until she found a hut by the river. The next day, the men who worked there found her.")
L("t3", "In 2023, four children survived forty days in the Colombian Amazon after their small plane crashed.")
L("t3", "The oldest was thirteen. She fed the others cassava flour from the plane, and fruit they knew was safe.")
L("t4", "The jungle doesn't care how strong you are. It cares what you choose.")
L("end", "So: how many did you get right? Tell me in the comments.", after=0.6)


# --------------------------------------------------------------------------- props
def black(a=0.95, col=NIGHT, at=None):
    def fn(ctx, t):
        if at is not None and t < at:
            return
        ctx.save()
        ctx.set_source_rgba(col[0] / 255, col[1] / 255, col[2] / 255, a)
        ctx.paint()
        ctx.restore()
    return fn


def fit(text, x, size, xmax=1830):
    return min(size, (xmax - x) / max(text_w(ln, 1) for ln in text.split("\n")))


def trunk(x, y0, y1, w=60, seed=0):
    pts = [(x - w / 2, y1), (x - w / 2 + 6, y0), (x + w / 2 - 4, y0), (x + w / 2, y1)]
    return [Fl(P_poly(pts, True), TRUNK), stk(P_line(x - w / 2, y1, x - w / 2 + 6, y0, 0.01, seed), 6), stk(P_line(x + w / 2, y1, x + w / 2 - 4, y0, 0.01, seed + 1), 6)]


def leaf(x, y, s=1.0, ang=0.0, col=LEAF, seed=0):
    a = math.radians(ang)
    tip = (x + 120 * s * math.cos(a), y + 120 * s * math.sin(a))
    n = (-math.sin(a) * 45 * s, math.cos(a) * 45 * s)
    mid = ((x + tip[0]) / 2, (y + tip[1]) / 2)
    shape = np.vstack([P_bez((x, y), (mid[0] + n[0], mid[1] + n[1]), tip), P_bez(tip, (mid[0] - n[0], mid[1] - n[1]), (x, y))])
    return [Fl(shape, col), stk(shape, 5 * s), stk(P_line(x, y, tip[0], tip[1], 0.02, seed), 3.5 * s)]


def canopy(top=True, seed=0, density=14, col=LEAF2):
    """A band of big leaves along the top of the frame (or the bottom)."""
    r = random.Random(seed)
    ops = []
    for k in range(density):
        x = k * 1920 / (density - 1) + r.uniform(-40, 40)
        y = (r.uniform(-20, 60) if top else r.uniform(1010, 1080))
        ops += leaf(x, y, r.uniform(1.0, 1.6), r.uniform(40, 140) if top else r.uniform(-140, -40), col if k % 2 else LEAF, seed + k)
    return ops


def jungle_bg(S, seed=0, trunks=(160, 1760), at=0.0):
    S.draw([op for x in trunks for op in trunk(x, -20, 1100, 70, seed + int(x))], at, 0.0, snd=None)
    S.draw(canopy(True, seed), at, 0.0, snd=None)


def wreck(x, y, s=1.0, smoke=True):
    """A broken piece of fuselage lying on its side: windows, a torn edge, smoke."""
    w, h = 520 * s, 210 * s
    body = [(x - w / 2, y - h)] + [(x + w / 2 - 40 * s + (25 * s if k % 2 else 0), y - h + k * h / 6) for k in range(7)] + [(x - w / 2, y)]
    o = [Fl(P_poly(body, True), (214, 214, 210)), stk(P_poly(body, True), 7 * s)]
    for k in range(4):
        o += [Fl(P_rect(x - w / 2 + 50 * s + k * 95 * s, y - h + 50 * s, 50 * s, 60 * s, 0, r=18 * s), (130, 160, 190)),
              stk(P_rect(x - w / 2 + 50 * s + k * 95 * s, y - h + 50 * s, 50 * s, 60 * s, 3 * s, r=18 * s), 4 * s)]
    o.append(stk(P_line(x - w / 2, y - 40 * s, x + w / 2 - 40 * s, y - 40 * s, 0.02, 7), 4 * s, RED))
    if smoke:
        for k in range(3):
            sx = x + w / 2 - 60 * s + k * 30 * s
            o.append(stk(P_bez((sx, y - h), (sx - 40 * s, y - h - 90 * s), (sx + 40 * s, y - h - 170 * s), (sx, y - h - 260 * s)), 6 * s, GREY))
    return o


def seat(x, y, s=1.0):
    """An airliner seat (upside down when hung), with its belt."""
    o = [Fl(P_rect(x - 70 * s, y - 160 * s, 140 * s, 180 * s, 0, r=20 * s), (90, 110, 150)), stk(P_rect(x - 70 * s, y - 160 * s, 140 * s, 180 * s, 6 * s, r=20 * s), 7 * s),
         Fl(P_rect(x - 80 * s, y + 10 * s, 160 * s, 50 * s, 0, r=12 * s), (90, 110, 150)), stk(P_rect(x - 80 * s, y + 10 * s, 160 * s, 50 * s, 5 * s, r=12 * s), 6 * s)]
    return o


def bottle(x, y, s=1.0, level=0.5):
    h, w = 200 * s, 70 * s
    o = [Fl(P_rect(x - w / 2, y - h * level, w, h * level, 0, r=10 * s), WATER),
         stk(P_rect(x - w / 2, y - h, w, h, 5 * s, r=16 * s), 6 * s), stk(P_rect(x - 18 * s, y - h - 30 * s, 36 * s, 30 * s, 3 * s, r=6 * s), 5 * s)]
    return o


def puddle(x, y, s=1.0):
    return [Fl(P_ell(x, y, 220 * s, 50 * s, 1, closed=True), MUD), stk(P_ell(x, y, 220 * s, 50 * s, 2, 0.06), 6 * s)] + \
           [stk(P_ell(x - 80 * s + k * 70 * s, y - 5 * s + (k % 2) * 10 * s, 22 * s, 8 * s, 3 + k, 0.05), 4 * s, (90, 74, 50)) for k in range(3)]


def berries(x, y, s=1.0):
    o = []
    for k in range(5):
        o += leaf(x - 120 * s + k * 60 * s, y + (k % 2) * 30 * s, 0.9 * s, -60 - k * 20, LEAF, 50 + k)
    r = random.Random(9)
    for k in range(14):
        o.append(("dot", x - 100 * s + r.uniform(0, 230) * s, y - 40 * s + r.uniform(0, 110) * s, 13 * s, RED))
    return o


def stream(x0, y0, x1, y1, w0=14, w1=60):
    """A stream getting wider as it goes downhill (left to right, top to bottom)."""
    up = P_bez((x0, y0), ((x0 + x1) / 2, y0 + 60), ((x0 + x1) / 2, y1 - 80), (x1, y1), n=60)
    widths = np.linspace(w0, w1, len(up))
    left = up + np.stack([np.zeros(len(up)), -widths / 2], 1)
    right = up + np.stack([np.zeros(len(up)), widths / 2], 1)
    shape = np.vstack([left, right[::-1]])
    return [Fl(shape, WATER), stk(left, 5), stk(right, 5)]


def heli(x, y, s=1.0):
    return [Fl(P_ell(x, y, 120 * s, 60 * s, 1, closed=True), (200, 90, 60)), stk(P_ell(x, y, 120 * s, 60 * s, 2, 0.06), 6 * s),
            Fl(P_ell(x - 40 * s, y - 10 * s, 50 * s, 35 * s, 3, closed=True), (180, 210, 230)),
            stk(P_line(x + 110 * s, y, x + 280 * s, y - 20 * s, 0.02, 4), 10 * s), stk(P_line(x + 270 * s, y - 50 * s, x + 290 * s, y + 10 * s, 0.02, 5), 6 * s),
            stk(P_line(x, y - 60 * s, x, y - 90 * s, 0, 6), 7 * s), stk(P_line(x - 220 * s, y - 92 * s, x + 220 * s, y - 88 * s, 0.01, 7), 7 * s),
            stk(P_line(x - 70 * s, y + 60 * s, x - 70 * s, y + 85 * s, 0, 8), 5 * s), stk(P_line(x + 50 * s, y + 60 * s, x + 50 * s, y + 85 * s, 0, 9), 5 * s),
            stk(P_line(x - 110 * s, y + 85 * s, x + 90 * s, y + 85 * s, 0.01, 10), 6 * s)]


def you(x, y, s=1.0, pose="stand", mood="worried", at=0.0, **kw):
    return Fig(x, y, s, at=at, poses=[(pose, 0)] if isinstance(pose, str) else pose, moods=[(mood, 0)] if isinstance(mood, str) else mood,
               kind="you", seed=7, **kw)


def day_card(S, label, sub=None):
    """A chapter page: the time, big, on the dark green of the forest floor, a few leaves in the corner."""
    S.noframe = True
    S.add(black(0.93, (30, 46, 32)))
    r = S.rng
    S.text(label, 160 + r.randint(0, 120), 600, 230, WHITE, at=0.05, rot=r.uniform(-4, 2), cps=14)
    S.draw([op for k in range(4) for op in leaf(1700 + k * 40, 900 - k * 70, 1.4, -120 - k * 15, LEAF2, 60 + k)], 0.1, 0.4, snd=None)
    if sub:
        S.text(sub, 180, 780, 84, DIM, at=0.6)


def decision(S, a_label, a_ops, b_label, b_ops, a_at=None, b_at=None):
    """The stop: 'A or B?', two panels (each drawn on its own words), then a silent 3-2-1 in the pause after the line."""
    S.noframe = True
    S.add(black(0.9, (30, 46, 32)))
    S.text("STOP.", 150, 200, 150, RED, at=S.c("stop") - 0.05, rot=-3, cps=30)
    S.text("what do you do?", 640, 190, 84, WHITE, at=S.c("stop") + 0.4, rot=-2)
    for k, (lab, ops, at, x) in enumerate((("A", a_ops, a_at, 150), ("B", b_ops, b_at, 990))):
        S.draw([Fl(P_rect(x, 280, 780, 470, 0, r=26), (236, 232, 222)), stk(P_rect(x, 280, 780, 470, 7, r=26), 8)], at - 0.3, 0.3, snd=None)
        S.text(lab, x + 40, 400, 120, RED if k == 0 else (60, 120, 70), at=at - 0.1)
        S.draw(ops, at, 0.4, snd=None)
        S.text((a_label, b_label)[k], x + 390, 720, fit((a_label, b_label)[k], x + 30, 66, x + 750) , INK, at=at + 0.1, anchor="m")
    t = S.e(0) + 0.1
    for k, n in enumerate("321"):
        S.text(n, 960, 860, 100, WHITE, at=t + 0.75 * k, anchor="m", until=t + 0.75 * (k + 1) - 0.25, cps=60)


def verdict(S, ok, x=1800, y=110):
    """The result stamp on an outcome page: a red cross for the wrong choice, a green tick for the right one."""
    if ok:
        S.add(check(x, y, 50, S.l(0) + 0.1, (60, 140, 70), 13))
    else:
        S.add(cross(x, y, 48, S.l(0) + 0.1, RED, 13))


# --------------------------------------------------------------------------- the crash
@V.scene("o1")
def _(S):
    S.noframe = True
    jungle_bg(S, 1)
    S.draw([stk(P_bez((620, -10), (640, 120), (600, 230), (640, 300)), 8, LEAF2)], 0.0, 0.0, snd=None)
    S.add(Dr(seat(640, 470, 1.6), 0.0, 0.0, seed=3))
    S.add(you(640, 200, 1.5, pose="hang", mood=[("sleep", 0), ("wow", S.c("wake") + 0.2)], rot=180, enter="none"))
    S.draw([stk(P_line(560, 420, 720, 420, 0.02, 4), 10, (200, 170, 60))], 0.0, 0.0, snd=None)
    S.text("upside down.", 1000, 400, 110, INK, at=S.c("upside") - 0.1, rot=-3)
    S.text("silent.", 1060, 600, 100, (60, 120, 70), at=S.c("silent", 1) - 0.1, rot=-3)
    S.text("the plane is gone.", 980, 780, 92, RED, at=S.c("gone", 1) - 0.3, rot=-2)


@V.scene("o2")
def _(S):
    S.text("you have:", 200, 220, 96, INK, at=0.05, rot=-2)
    S.draw(bottle(420, 760, 1.3, 0.5), S.c("bottle") - 0.2, 0.4)
    S.text("half full.", 300, 400, 92, INK, at=S.c("half") - 0.1, rot=-3)
    S.draw([Fl(P_rect(860, 400, 200, 360, 0, r=28), WHITE), stk(P_rect(860, 400, 200, 360, 7, r=28), 8)], S.c("phone") - 0.2, 0.3)
    S.text("no\nsignal", 960, 640, 62, RED, at=S.c("signal") - 0.1, anchor="m", lh=1.0)
    S.add(cross(960, 500, 50, S.c("signal") + 0.1, RED, 9))
    arm = np.vstack([P_bez((1230, 760), (1400, 690), (1560, 660), (1780, 600)), P_bez((1790, 660), (1580, 720), (1420, 750), (1240, 830))])
    S.draw([Fl(arm, (236, 214, 190)), stk(arm, 7), stk(P_line(1430, 720, 1580, 690, 0.06, 2), 10, RED)], S.c("cut") - 0.3, 0.4)
    for k in range(3):
        S.add(Dr([Fl(P_ell(1480 + k * 40, 780 + k * 30, 9, 13, k, closed=True), RED)], S.c("bleeding") + 0.2 * k, 0.0, pop=True, anchor=(1480 + k * 40, 780), seed=5 + k))
    S.text("won't stop.", 1300, 450, 100, RED, at=S.c("stop") - 0.2, rot=-3)


@V.scene("o3")
def _(S):
    S.noframe = True
    S.add(black(0.6, (30, 46, 32)))
    jungle_bg(S, 2)
    S.add(you(1350, 980, 1.2, mood="worried"))
    S.text("it doesn't need\nto attack you.", 340, 330, 90, INK, at=S.c("attack") - 0.4, lh=1.1, rot=-2)
    S.text("one wrong choice.", 340, 620, 110, RED, at=S.c("one") - 0.2, rot=-3)


@V.scene("c1")
def _(S):
    S.noframe = True
    S.add(black(0.95, (30, 46, 32)))
    S.text("Your plane goes down", 140, 360, 140, WHITE, at=S.c("plane") - 0.1, rot=-3, cps=36)
    S.text("in the jungle.", 180, 540, 160, (150, 210, 130), at=S.c("jungle") - 0.1, rot=-3, cps=30)
    S.text("can you survive?", 200, 760, 110, RED, at=S.c("survive") - 0.3, rot=-2)


# --------------------------------------------------------------------------- 1. stay or go
@V.scene("c2")
def _(S):
    day_card(S, "hour 1")


@V.scene("d1a")
def _(S):
    jungle_bg(S, 3)
    S.draw(wreck(820, 860, 1.25), 0.0, 0.4, snd=None)
    S.add(you(1400, 960, 1.2, pose=[("stand", 0), ("point_r", S.c("walk") - 0.1)], mood="worried"))
    S.text("pounding.", 240, 300, 100, INK, at=S.c("pounding") - 0.2, rot=-3)
    S.text("walk.", 1420, 300, 130, RED, at=S.c("walk") - 0.1, rot=-3)
    S.text("find people.", 1300, 470, 96, RED, at=S.c("people") - 0.3, rot=-3)


@V.scene("d1")
def _(S):
    a_ops = [stk(P_line(420, 640, 760, 640, 0.02, 1), 6), stk(P_poly([(720, 610), (770, 640), (720, 670)]), 6)] + leaf(560, 470, 0.8, -60, LEAF, 3)
    decision(S, "walk for help", a_ops, "stay with the wreck", wreck(1390, 690, 0.6, smoke=False), a_at=S.c("walk"), b_at=S.c("stay"))
    S.add(you(330, 690, 0.8, at=S.c("walk"), pose="point_r", enter="pop"))
    S.add(you(1690, 690, 0.8, at=S.c("stay"), pose="stand", enter="pop"))


@V.scene("d1x")
def _(S):
    S.noframe = True
    S.add(black(0.15))
    S.draw(canopy(True, 4, 18), 0.0, 0.0, snd=None)
    S.draw(canopy(True, 5, 16, LEAF), 0.0, 0.0, snd=None)
    verdict(S, False)
    S.draw([stk(P_line(120, 300, 1800, 300, 0.01, 1), 4, GREY)], 0.1, 0.3, snd=None)
    S.add(Dr(heli(1500, 120, 0.6), S.c("rescue", 1) - 0.3, 0.3, seed=11, move=lambda u: (-500 * min(1, u / 4), 0, 0, 1), anchor=(1500, 120)))
    S.add(you(900, 900, 0.7, pose="stand", mood="worried"))
    S.text("can't see\none person.", 200, 500, 96, INK, at=S.c("person", 1) - 0.3, lh=1.1, rot=-2)
    S.add(arrow(P_bez((900, 740), (1100, 640), (1400, 760)), S.c("wrong", 1) - 0.2, RED, 7, 0.5, dashed=True))
    S.text("never find it again.", 1050, 600, 80, RED, at=S.c("never", 1) - 0.2, rot=-2)


@V.scene("d1y")
def _(S):
    jungle_bg(S, 6, trunks=(120, 1820))
    verdict(S, True)
    S.draw(wreck(800, 860, 1.4, smoke=False), 0.0, 0.3, snd=None)
    S.add(you(1350, 960, 1.1, mood="flat"))
    S.text("bigger than you.", 260, 330, 96, INK, at=S.c("bigger") - 0.2, rot=-2)
    S.text("shelter.", 300, 480, 90, (60, 120, 70), at=S.c("shelter", 1) - 0.1, rot=-2)
    for k in range(3):
        S.add(Dr([stk(P_arc(1000, 520, 60 + 50 * k, 60 + 50 * k, 300, 360, 12), 6, RED)], S.c("beacon", 1) + 0.2 * k, 0.2, seed=20 + k))
    S.text("beacon", 1060, 420, 72, RED, at=S.c("beacon", 1) + 0.1)
    S.text("listen.", 1460, 300, 100, INK, at=S.c("listen", 2) - 0.2, rot=-3)


# --------------------------------------------------------------------------- 2. water
@V.scene("c3")
def _(S):
    day_card(S, "day 2")


@V.scene("d2a")
def _(S):
    jungle_bg(S, 7)
    S.draw(bottle(400, 760, 1.2, 0.0), 0.0, 0.3, snd=None)
    S.text("empty.", 300, 380, 100, RED, at=S.c("empty") - 0.1, rot=-3)
    S.draw([Fl(P_rect(700, 220, 900, 70, 0, r=30), (236, 232, 222)), stk(P_rect(700, 220, 900, 70, 5, r=30), 6)], S.c("three") - 0.4, 0.3, snd=None)
    S.draw([Fl(P_rect(705, 225, 600, 60, 0, r=28), RED)], S.c("two") - 0.2, 0.4, snd=None)
    S.text("3 days", 1620, 280, 70, INK, at=S.c("three") - 0.1)
    S.text("day 2", 900, 380, 84, RED, at=S.c("two") - 0.1)
    S.draw(puddle(1150, 860, 1.3), S.c("puddle", 1) - 0.3, 0.4)
    S.text("brown. warm.", 1000, 690, 84, (110, 80, 50), at=S.c("brown", 1) - 0.1, rot=-2)


@V.scene("d2")
def _(S):
    rain = [stk(P_line(1200 + k * 60, 330, 1170 + k * 60, 420, 0, k), 5, WATER) for k in range(9)]
    decision(S, "drink the puddle", puddle(540, 600, 0.9), "wait for the rain", rain + bottle(1380, 700, 0.8, 0.2), a_at=S.c("drink"), b_at=S.c("wait"))


@V.scene("d2x")
def _(S):
    verdict(S, False)
    S.draw(puddle(560, 820, 1.4), 0.0, 0.3, snd=None)
    r = random.Random(4)
    for k in range(9):
        cx, cy = 360 + r.uniform(0, 400), 790 + r.uniform(-20, 40)
        S.add(Dr([stk(P_wave(cx, cx + 40, cy, 5, 14), 4, (60, 90, 50))], S.c("bacteria") + 0.08 * k, 0.1, seed=30 + k))
    S.text("bacteria. parasites.", 220, 330, 96, INK, at=S.c("bacteria") - 0.2, rot=-2)
    S.draw([Fl(P_rect(1150, 500, 600, 70, 0, r=30), (236, 232, 222)), stk(P_rect(1150, 500, 600, 70, 5, r=30), 6)], S.c("drains") - 0.3, 0.3, snd=None)
    S.add(Dr([Fl(P_rect(1155, 505, 420, 60, 0, r=28), WATER)], S.c("drains") - 0.1, 0.0, seed=40, until=S.c("faster") - 0.1 - EXIT))
    S.add(Dr([Fl(P_rect(1155, 505, 120, 60, 0, r=28), WATER)], S.c("faster") - 0.1, 0.0, seed=41))
    S.text("water out.", 1250, 430, 84, RED, at=S.c("drains") - 0.1, rot=-2)
    S.text("thirstier.", 1250, 760, 120, RED, at=S.c("thirstier", 1) - 0.3, rot=-3)


@V.scene("d2y")
def _(S):
    verdict(S, True)
    S.draw([Fl(P_ell(cx_, 150, 170, 70, k, closed=True), (200, 206, 214)) for k, cx_ in enumerate((500, 760, 1020, 1280))]
           + [stk(P_arc(cx_, 150, 170, 70, 180 + (25 if k else 0), 360 - (25 if k < 3 else 0), 30), 6) for k, cx_ in enumerate((500, 760, 1020, 1280))]
           + [stk(P_line(340, 205, 1440, 205, 0.01, 7), 6)], S.l(0) + 0.05, 0.4)
    t_rain = S.c("rains")
    for k in range(18):
        S.add(Dr([stk(P_line(260 + k * 70, 250 + (k % 3) * 30, 235 + k * 70, 350 + (k % 3) * 30, 0, k), 6, WATER)], t_rain + 0.05 * k, 0.1, seed=50 + k))
    sheet = [(600, 560), (1300, 520), (1000, 760)]
    S.draw([Fl(P_poly(sheet, True), (226, 230, 236)), stk(P_poly(sheet, True), 6)], S.c("plastic", 1) - 0.2, 0.3)
    S.draw(bottle(1000, 1000, 0.9, 0.0), S.c("fill", 1) - 0.3, 0.3)
    S.add(Dr([Fl(P_rect(1000 - 31, 1000 - 180 * 0.6, 62, 180 * 0.6, 0, r=8), WATER)], S.c("fill", 1) + 0.3, 0.0, seed=55))
    S.text("first rinse: let it go.", 200, 480, 76, INK, at=S.c("rinse", 1) - 0.2, rot=-2)
    S.text("boil it if you can.", 1150, 480, 84, RED, at=S.c("boil", 2) - 0.2, rot=-2)
    S.text("4 p.m.", 200, 800, 110, INK, at=S.c("four", 3) - 0.2, rot=-3)


# --------------------------------------------------------------------------- 3. food
@V.scene("c4")
def _(S):
    day_card(S, "day 3")


@V.scene("d3a")
def _(S):
    jungle_bg(S, 8)
    S.add(you(500, 980, 1.2, pose="sit_hug", mood="sad"))
    S.text("nobody came.", 240, 320, 96, INK, at=S.c("nobody") - 0.1, rot=-2)
    S.draw(berries(1250, 720, 1.6), S.c("bush") - 0.3, 0.5)
    S.text("hundreds.", 1150, 400, 110, RED, at=S.c("hundreds") - 0.2, rot=-3)


@V.scene("d3")
def _(S):
    decision(S, "eat the berries", berries(540, 560, 1.0), "eat nothing you don't know", [stk(P_ell(1380, 560, 120, 120, 1, 0.06), 9, (60, 120, 70)),
                                                                                           stk(P_line(1300, 640, 1460, 480, 0.02, 2), 9, (60, 120, 70))],
             a_at=S.c("eat"), b_at=S.c("eat", 0, 1))


@V.scene("d3x")
def _(S):
    verdict(S, False)
    S.draw(berries(500, 640, 1.4), 0.0, 0.3, snd=None)
    S.text("food?", 300, 330, 110, INK, at=S.c("food") - 0.1, rot=-2)
    S.text("or poison.", 1100, 330, 110, RED, at=S.c("vomit") - 0.4, rot=-2)
    S.add(you(1350, 980, 1.1, pose="sad", mood="sad", at=S.c("vomit") - 0.1, enter="pop"))
    S.text("= losing water.", 1100, 520, 92, RED, at=S.c("losing") - 0.2, rot=-2)


@V.scene("d3y")
def _(S):
    verdict(S, True)
    S.text("weeks without food.", 200, 300, 100, INK, at=S.l(0) + 0.2, rot=-2)
    S.text("days without water.", 200, 460, 100, RED, at=S.c("thirst") - 0.3, rot=-2)
    bag = [(1150, 600), (1450, 580), (1470, 860), (1140, 880)]
    S.draw([Fl(P_poly(bag, True), (230, 200, 140)), stk(P_poly(bag, True), 7), ("g", "crackers", 1305, 740, 60, INK, HAND, "m")], S.c("crackers", 1) - 0.3, 0.4)
    for k in range(4):
        S.add(Dr([Fl(P_rect(1560 + k * 50, 900, 40, 40, 0, r=6), (230, 200, 140)), stk(P_rect(1560 + k * 50, 900, 40, 40, 3, r=6), 4)],
                 S.c("four", 1) + 0.1 * k, 0.0, pop=True, anchor=(1580 + k * 50, 920), seed=60 + k))
    S.text("keep the rest.", 1150, 460, 84, (60, 120, 70), at=S.c("keep", 1) - 0.2, rot=-2)


# --------------------------------------------------------------------------- 4. which way
@V.scene("c5")
def _(S):
    day_card(S, "day 4")


@V.scene("d4a")
def _(S):
    jungle_bg(S, 9)
    S.draw([stk(P_bez((300, 760), (420, 720), (520, 700), (660, 650)), 40), stk(P_line(460, 710, 560, 690, 0.05, 2), 9, RED)], 0.0, 0.3, snd=None)
    S.add(Dr([Fl(P_ell(520, 700, 90, 50, 1, closed=True), (230, 120, 100))], S.c("red") - 0.2, 0.4, seed=70, a=0.55))
    S.text("turning red.", 260, 400, 100, RED, at=S.c("red") - 0.2, rot=-3)
    S.text("staying is now\nthe danger.", 1050, 330, 96, INK, at=S.c("danger") - 0.4, lh=1.1, rot=-2)
    S.text("which way?", 1100, 700, 130, RED, at=S.c("way", 1) - 0.3, rot=-3)


@V.scene("d4")
def _(S):
    hill = [stk(P_bez((200, 720), (380, 380), (560, 380), (740, 720)), 8)]
    decision(S, "climb uphill", hill + [stk(P_poly([(470, 420), (470, 340), (500, 360)]), 6)], "follow a stream downhill",
             stream(1040, 380, 1700, 680, 10, 50), a_at=S.c("climb"), b_at=S.c("stream"))


@V.scene("d4x")
def _(S):
    verdict(S, False)
    S.draw([stk(P_bez((100, 1000), (600, 300), (1300, 300), (1820, 1000)), 9)], 0.0, 0.4, snd=None)
    S.add(you(960, 410, 0.9, pose="hips", mood="sad"))
    for k in range(10):
        S.add(Dr(leaf(150 + k * 180, 700 + (k % 2) * 60, 1.3, -90 + (k % 3) * 30, LEAF2, 80 + k), S.c("thick") + 0.06 * k, 0.2, seed=90 + k))
    S.text("just more trees.", 220, 250, 96, INK, at=S.c("trees") - 0.3, rot=-2)
    S.text("water spent.", 1250, 250, 96, RED, at=S.c("spent") - 0.2, rot=-2)


@V.scene("d4y")
def _(S):
    verdict(S, True)
    S.draw(stream(140, 260, 900, 520, 10, 30), S.l(0) + 0.1, 0.5)
    S.draw(stream(900, 520, 1500, 760, 30, 70), S.c("bigger") - 0.2, 0.5)
    S.draw(stream(1500, 760, 1900, 900, 70, 150), S.c("rivers") - 0.2, 0.4)
    S.draw([Fl(P_rect(1560, 520, 180, 120, 0), (226, 210, 170)), stk(P_rect(1560, 520, 180, 120, 5), 6),
            Fl(P_poly([(1540, 520), (1650, 440), (1760, 520)], True), MUD), stk(P_poly([(1540, 520), (1650, 440), (1760, 520)], True), 6)], S.c("people") - 0.3, 0.4)
    S.text("water runs downhill.", 200, 160, 92, INK, at=S.l(0) + 0.3, rot=-2)
    S.text("people live by rivers.", 950, 330, 92, (60, 120, 70), at=S.c("people") - 0.4, rot=-2)
    S.add(you(330, 520, 0.8, pose="point_r", mood="flat", at=S.c("follow", 1) - 0.4, enter="pop"))


# --------------------------------------------------------------------------- 5. the helicopter
@V.scene("c6")
def _(S):
    day_card(S, "day 7")


@V.scene("d5a")
def _(S):
    S.noframe = True
    S.draw(canopy(True, 10, 18), 0.0, 0.0, snd=None)
    S.draw(stream(0, 700, 1920, 860, 160, 240), 0.0, 0.4, snd=None)
    S.add(you(700, 760, 0.9, mood=[("flat", 0), ("wow", S.c("hear"))]))
    for k in range(3):
        S.add(Dr([stk(P_arc(1400, 120, 80 + 60 * k, 50 + 40 * k, 20, 160, 14), 6, INK)], S.c("helicopter") + 0.25 * k, 0.2, seed=100 + k))
    S.text("a helicopter.", 1150, 380, 104, RED, at=S.c("helicopter") - 0.2, rot=-3)
    S.text("above the trees.", 1150, 520, 84, INK, at=S.c("trees") - 0.3, rot=-2)


@V.scene("d5")
def _(S):
    decision(S, "shout from the trees", leaf(300, 560, 1.0, -40, LEAF2, 1) + leaf(560, 520, 1.1, -140, LEAF, 2),
             "open bank + a signal", [stk(P_line(1260, 470, 1460, 670, 0.02, 1), 16, ORANGE), stk(P_line(1460, 470, 1260, 670, 0.02, 2), 16, ORANGE)],
             a_at=S.c("shout"), b_at=S.c("riverbank"))


@V.scene("d5x")
def _(S):
    S.noframe = True
    verdict(S, False)
    S.draw(canopy(True, 11, 20), 0.0, 0.0, snd=None)
    S.draw(canopy(True, 12, 16, LEAF), 0.0, 0.0, snd=None)
    S.add(you(900, 980, 0.9, pose="wave", mood="wow"))
    S.add(Dr(heli(400, 100, 0.55), 0.0, 0.0, seed=12, move=lambda u: (1600 * min(1, u / 6), 0, 0, 1), anchor=(400, 100)))
    S.text("invisible.", 200, 500, 120, RED, at=S.c("invisible") - 0.2, rot=-3)
    S.text("it doesn't come back.", 1000, 520, 84, INK, at=S.c("back") - 0.4, rot=-2)


@V.scene("d5y")
def _(S):
    S.noframe = True
    verdict(S, True)
    S.draw(stream(0, 760, 1920, 920, 180, 260), 0.0, 0.0, snd=None)
    S.draw([Fl(P_rect(0, 560, 1920, 160, 0), (226, 210, 170))], 0.0, 0.0, snd=None)
    S.draw(canopy(True, 13, 14), 0.0, 0.0, snd=None)
    S.draw([stk(P_line(700, 580, 1000, 700, 0.02, 1), 20, ORANGE), stk(P_line(1000, 580, 700, 700, 0.02, 2), 20, ORANGE)], S.c("bright") - 0.2, 0.4)
    for k, x in enumerate((1250, 1420, 1590)):
        S.add(Dr([Fl(P_poly([(x - 50, 690), (x, 600), (x + 50, 690)], True), (200, 160, 110)), stk(P_poly([(x - 50, 690), (x, 600), (x + 50, 690)], True), 5)],
                 S.c("three", 0, 1) + 0.2 * k, 0.0, pop=True, anchor=(x, 650), seed=110 + k))
    S.text("three = help.", 1200, 480, 92, RED, at=S.c("help") - 0.3, rot=-2)
    S.text("the bank, not the forest.", 200, 480, 84, INK, at=S.c("bank", 1) - 0.3, rot=-2)
    S.add(Dr(heli(1500, 180, 0.6), S.c("turns", 2) - 0.6, 0.0, seed=13, move=lambda u: (-300 * min(1, u / 2), 60 * min(1, u / 2), -0.15 * min(1, u / 2), 1), anchor=(1500, 180)))


# --------------------------------------------------------------------------- it happened
@V.scene("t1")
def _(S):
    S.noframe = True
    S.add(black(0.9))
    S.text("1971", 160, 330, 200, WHITE, at=S.c("1971", 1) - 0.1, rot=-3)
    S.text("Juliane Koepcke, 17", 160, 470, 92, DIM, at=S.c("juliane") + 0.1, rot=-2)
    for k in range(3):
        S.add(Dr([stk(P_poly([(1250 + k * 160, 120), (1210 + k * 160, 230), (1260 + k * 160, 230), (1220 + k * 160, 340)]), 8, (240, 220, 120))],
                 S.c("storm", 1) + 0.1 * k, 0.15, seed=120 + k))
    S.draw(seat(1400, 700, 0.8), S.c("seat", 1) - 0.3, 0.3, snd=None)
    S.add(arrow(P_line(1400, 420, 1400, 560, 0.0, 3), S.c("fell", 1), WHITE, 7, 0.3))
    S.text("3 km", 1500, 500, 110, RED, at=S.c("three", 1) - 0.1, rot=-3)
    S.draw(canopy(False, 21, 16), S.c("jungle", 1) - 0.2, 0.5, snd=None)


@V.scene("t2")
def _(S):
    S.draw(stream(120, 200, 1300, 820, 10, 140), S.l(0) + 0.1, 0.6)
    S.text("follow the water.", 150, 160, 100, (60, 120, 70), at=S.c("water") - 0.3, rot=-2)
    S.text("biologists", 1250, 160, 84, INK, at=S.c("biologists") - 0.2, rot=-2)
    S.text("maggots in the wound", 1150, 480, fit("maggots in the wound", 1150, 76), RED, at=S.c("maggots", 1) - 0.2, rot=-2)
    S.text("about 10 days", 1300, 330, fit("about 10 days", 1300, 100), INK, at=S.c("ten", 1) - 0.2, rot=-3)
    S.draw([Fl(P_rect(1450, 620, 220, 140, 0), (226, 210, 170)), stk(P_rect(1450, 620, 220, 140, 5), 6),
            Fl(P_poly([(1430, 620), (1560, 530), (1690, 620)], True), MUD), stk(P_poly([(1430, 620), (1560, 530), (1690, 620)], True), 6)], S.c("hut", 1) - 0.3, 0.4)
    S.text("the next day: found.", 1100, 850, fit("the next day: found.", 1100, 84), RED, at=S.c("found", 1) - 0.3, rot=-2)


@V.scene("t3")
def _(S):
    S.noframe = True
    S.add(black(0.35, (30, 46, 32)))
    S.text("2023", 160, 300, 200, INK, at=S.c("2023") - 0.1, rot=-3)
    S.text("40 days", 160, 470, 130, RED, at=S.c("forty") - 0.1, rot=-3)
    for k, (s, kd) in enumerate(((1.1, "long"), (0.9, "bob"), (0.7, "spiky"), (0.5, "spiky"))):
        S.add(Fig(1000 + k * 200, 980, s, at=S.c("four") + 0.12 * k, poses=[("stand", 0)], moods=[("flat", 0)], kind=kd, seed=130 + k, enter="pop"))
    S.draw([stk(P_line(560, 760, 860, 700, 0.02, 1), 9), stk(P_line(640, 690, 760, 790, 0.02, 2), 8), stk(P_line(840, 690, 870, 760, 0.02, 3), 7)],
           S.c("plane") - 0.2, 0.3)
    S.text("the oldest: 13", 1050, 300, 84, INK, at=S.c("oldest", 1) - 0.1, rot=-2)
    S.text("cassava flour + fruit they knew", 900, 420, fit("cassava flour + fruit they knew", 900, 70), (60, 100, 60), at=S.c("cassava", 1) - 0.2, rot=-2)


@V.scene("t4")
def _(S):
    S.noframe = True
    S.add(black(0.93, (30, 46, 32)))
    S.text("it cares", 200, 450, 170, WHITE, at=S.c("cares") - 0.2, rot=-3)
    S.text("what you choose.", 240, 680, 170, (150, 210, 130), at=S.c("choose") - 0.4, rot=-3)


@V.scene("end")
def _(S):
    """The outro: no next-video box, no buttons. Evening on the river; you, small, walking along the bank; the question."""
    S.noframe = True
    S.add(black(0.55, (30, 46, 32)))
    S.draw(stream(0, 700, 1920, 860, 160, 240), 0.0, 0.0, snd=None)
    S.draw([Fl(P_rect(0, 560, 1920, 140, 0), (200, 186, 150))], 0.0, 0.0, snd=None)
    S.draw(canopy(True, 14, 16), 0.0, 0.0, snd=None)
    S.add(Fig(300, 690, 0.7, poses=[("stand", 0)], moods=[("flat", 0)], kind="you", seed=7, enter="none", walk=(300, 1500, 0.3, S.dur)))
    S.text("how many did you", 180, 260, 110, WHITE, at=S.c("many") - 0.2, rot=-2)
    S.text("get right?", 220, 420, 130, (150, 210, 130), at=S.c("right") - 0.2, rot=-2)
    S.text("tell me in the comments.", 1000, 980 - 80, 72, WHITE, at=S.c("comments") - 0.4, rot=-1)


if __name__ == "__main__":
    V.prepare(tail=4.5)              # a short outro, not a 12 s end screen
    V.main()
