"""DON'T OPEN THE DOOR - episode 1: the knock. A doodle horror story in four episodes (pure fiction).
3:12 a.m., every phone gets the same alert: do not open your door. Then someone knocks, with Mom's voice.
Voices: Maya (narrator) af_heart, Mom af_bella (muffled through the door), Noah af_nicole (a whisper), the news am_michael (radio)."""
from story_video import *  # noqa: F401,F403
from doodle_video import stk, endcard
from doodle import POSES, clip_ell

NARR, MOM, NOAH, NEWS = "af_heart", "af_bella", "af_nicole", "am_michael"
NIGHT = (24, 23, 28)
WHITE = (250, 248, 242)
WOOD = (156, 112, 78)
KSKIN = (198, 208, 186)          # the knockers: a shade too grey
COAT = (150, 186, 214)
POSES["knock"] = dict(la=(-20, -10), ra=(112, 158), ll=(-10, -5), rl=(10, 5), lean=3, tilt=4)
POSES["wait"] = dict(la=(-8, -4), ra=(8, 4), ll=(-8, -4), rl=(8, 4), lean=0, tilt=13)

V = Story("door1", tapes=[("And that's when someone knocked.", "Don't Open the Door."), ("Then, at 6:58", "When it got light"), ("Then someone knocked again.", "Next: episode two")],
          say={"3:12": "three twelve", "3:14": "three fourteen", "6:58": "six fifty-eight", "7:06": "seven oh six"},
          keys=dict(prog=[(50, 53, 57, 62), (46, 50, 53, 58), (43, 50, 55, 58), (45, 49, 52, 57)], roots=[38, 34, 31, 33], bpm=56),
          hush=[("Around five, the words", "I had said his name")], beat_groups=(), seed=21)
L = V.L
MOM_DOOR = '"Maya? Sweetheart, it\'s Mom. Open the door."'

L("o1", "At 3:12 in the morning, every phone in the city lit up at the same time.")
L("o1", "One message. No sender.")
L("o1", "Do not open your door. Do not answer anyone.")
L("o2", "I read it twice. Then I put my phone face down, because it had to be a joke.")
L("o3", "And that's when someone knocked.", after=1.8)
L("c1", "Don't Open the Door. Episode one: the knock.")
L("s1", "My name is Maya. I'm twenty-four, and that night my little brother Noah was asleep on my couch, because Mom was working a night shift at the hospital.")
L("s1", "Noah is eight. He sleeps through anything.")
L("s2", "Three knocks. Slow. Polite.")
L("s2", MOM_DOOR, voice=MOM, fx="door", speed=0.86)
L("s3", "Mom's shift didn't end until seven. It was 3:14.")
L("s3", "And Mom never calls me sweetheart.")
L("s3", "I didn't move. I didn't even breathe.")
L("s4", "I looked through the peephole.")
L("s4", "It was her. Her coat. Her hair. Her little gold earrings.")
L("s4", "She was smiling. And she wasn't blinking.", after=1.6)
L("s5", MOM_DOOR, voice=MOM, fx="door", speed=0.86)
L("s5", "The same words. The same voice. Like a recording.")
L("s6", '"Maya? Is that Mom?"', voice=NOAH, fx="whisper")
L("s6", "Noah was awake. And he was already running for the door.")
L("s6", "I caught him by his pajamas, one step before the handle.")
L("s7", "On my phone, a man in a suit was reading the news like he hadn't slept in days.")
L("s7", '"If someone you know is at your door, do not let them in. They may look normal. They are not."', voice=NEWS, fx="radio", speed=1.0)
L("s7", "People were already calling them the knockers.", after=0.4)
L("s8", "We hid behind the couch, under a blanket, and listened.")
L("s8", "She knocked every ten minutes, until the sky turned gray.")
L("s8b", "Around five, the words changed.")
L("s8b", '"Noah? Sweetheart, it\'s Mom. Open the door."', voice=MOM, fx="door", speed=0.86)
L("s8b", "I had said his name once, when I caught him. She had heard it.")
L("s8c", "Then, at 6:58, the knocking stopped.", after=1.0)
L("s9", "When it got light, I looked out of the window.")
L("s9", "Someone was standing outside every door on my street. Not moving. Just waiting.")
L("s9", "Some of them, I knew. The baker from the corner. The lady with the little yellow dog.")
L("s10", "And upstairs, Mr. Duval's door was wide open.", after=0.4)
L("s11", "At 7:06, my phone buzzed. A text from Mom.")
L("s11", '"I\'m outside your door. Why won\'t you open?"', voice=MOM, speed=0.9)
L("s12", '"Maya... what if it\'s really her?"', voice=NOAH, fx="whisper")
L("s12", "I didn't have an answer.", after=0.3)
L("s13", "Then someone knocked again.", after=2.0)
L("end", "Next: episode two, the hallway. Subscribe, so you don't miss it. And whatever happens... don't open the door.")


# --------------------------------------------------------------------------- props
def black(a=0.95, col=NIGHT):
    def fn(ctx, t):
        ctx.save()
        ctx.set_source_rgba(col[0] / 255, col[1] / 255, col[2] / 255, a)
        ctx.paint()
        ctx.restore()
    return fn


def group(*fns):
    def fn(ctx, t):
        for f in fns:
            f(ctx, t)
    return fn


def door(x, y, s=1.0, col=WOOD):
    """A flat's front door seen from inside, bottom edge on y: frame, two panels, lever handle, peephole, light under it."""
    w, h = 360 * s, 800 * s
    x0, y0 = x - w / 2, y - h
    return [Fl(P_rect(x0 - 30 * s, y0 - 30 * s, w + 60 * s, h + 30 * s, 0), (226, 219, 205)),
            stk(P_rect(x0 - 30 * s, y0 - 30 * s, w + 60 * s, h + 30 * s, 6 * s), 6 * s),
            Fl(P_rect(x0, y0, w, h, 0), col), stk(P_rect(x0, y0, w, h, 6 * s), 7 * s),
            stk(P_rect(x0 + 50 * s, y0 + 100 * s, w - 100 * s, 240 * s, 4 * s, r=6 * s), 5 * s),
            stk(P_rect(x0 + 50 * s, y0 + 420 * s, w - 100 * s, 290 * s, 4 * s, r=6 * s), 5 * s),
            Fl(P_ell(x0 + w - 52 * s, y0 + h * 0.53, 15 * s, 15 * s, 1, closed=True), HL),
            stk(P_ell(x0 + w - 52 * s, y0 + h * 0.53, 15 * s, 15 * s, 2, 0.05), 5 * s),
            stk(P_line(x0 + w - 52 * s, y0 + h * 0.53, x0 + w - 118 * s, y0 + h * 0.53 + 5 * s, 0.02, 3), 10 * s),
            ("dot", x, y0 + 62 * s, 9 * s, INK),
            Fl(P_rect(x0 + 8 * s, y - 7 * s, w - 16 * s, 9 * s, 0), (252, 236, 190))]


def knocks(S, x, y, at, size=120, gap=0.5, col=RED, sound=True, seed=0):
    r = random.Random(seed)
    for k in range(3):
        S.text("KNOCK", x + r.randint(-40, 40) + k * 40, y + k * size * 0.95, size, col, at=at + k * gap, rot=r.uniform(-9, 7), cps=60)
    if sound:
        S.add(snd="knock3", at=at)


def couch(x, y, s=1.0, col=(176, 150, 196)):
    o = [Fl(P_rect(x - 330 * s, y - 210 * s, 660 * s, 150 * s, 0, r=30 * s), col), stk(P_rect(x - 330 * s, y - 210 * s, 660 * s, 150 * s, 6 * s, r=30 * s), 7 * s),
         Fl(P_rect(x - 360 * s, y - 90 * s, 720 * s, 110 * s, 0, r=24 * s), col), stk(P_rect(x - 360 * s, y - 90 * s, 720 * s, 110 * s, 6 * s, r=24 * s), 7 * s)]
    for k in (-1, 1):
        o += [Fl(P_rect(x + k * 350 * s - 45 * s, y - 150 * s, 90 * s, 170 * s, 0, r=30 * s), col),
              stk(P_rect(x + k * 350 * s - 45 * s, y - 150 * s, 90 * s, 170 * s, 5 * s, r=30 * s), 7 * s),
              stk(P_line(x + k * 300 * s, y + 20 * s, x + k * 300 * s, y + 60 * s, 0, 2), 7 * s)]
    return o


def screen_lines(x, y, w, text, size, col=INK, at=0.0, lh=1.12, **kw):
    """Text that fits a phone screen: the size comes down until the longest line fits w."""
    sz = min(size, w / max(text_w(ln, 1) for ln in text.split("\n")))
    return T(text, x, y, sz, col, at=at, anchor="m", lh=lh, **kw)


def ph_screen(x, y, s, col=WHITE):
    return [Fl(P_rect(x - 85 * s, y - 155 * s, 170 * s, 310 * s, 0, r=26 * s), col), stk(P_rect(x - 85 * s, y - 155 * s, 170 * s, 310 * s, 8 * s, r=26 * s), 7 * s),
            stk(P_line(x - 22 * s, y - 133 * s, x + 22 * s, y - 133 * s, 0, 1), 5 * s)]


# --------------------------------------------------------------------------- 3:12
@V.scene("o1")
def _(S):
    S.noframe = True
    S.add(black(0.96))
    px, py, ps = 640, 530, 2.9
    t_lit = S.c("lit") - 0.15
    S.pop(ph_screen(px, py, ps), t_lit, (px, py), snd=None)
    S.add(snd="buzz", at=t_lit)
    sw = 170 * ps - 70
    S.draw([Fl(P_rect(px - 85 * ps + 18, py - 155 * ps + 60, 170 * ps - 36, 82, 0, r=12), RED)], S.c("message", 1) - 0.2, 0.2, snd=None)
    S.add(screen_lines(px, py - 155 * ps + 118, sw - 40, "ALERT", 64, WHITE, at=S.c("message", 1)))
    S.add(screen_lines(px, py - 155 * ps + 225, sw - 60, "from: ???", 72, GREY, at=S.c("sender", 1) - 0.1))
    S.add(screen_lines(px, py - 60, sw, "DO NOT\nOPEN YOUR\nDOOR.", 92, INK, at=S.c("open", 2) - 0.25, cps=30))
    S.add(screen_lines(px, py + 190, sw, "DON'T\nANSWER.", 80, RED, at=S.c("answer", 2) - 0.2, cps=30))
    S.text("3:12", 1180, 470, 280, WHITE, at=S.c("3:12") - 0.05, cps=12, rot=-3)
    S.text("a.m.", 1260, 640, 110, (170, 164, 156), at=S.c("morning") - 0.05, rot=-3)
    S.text("every phone.", 1190, 820, 96, RED, at=S.c("every"), rot=-3)


@V.scene("o2")
def _(S):
    bx, by = 760, 760
    S.draw([Fl(P_rect(bx - 520, by - 120, 1040, 150, 0, r=18), (214, 226, 196)), stk(P_rect(bx - 520, by - 120, 1040, 150, 6, r=18), 7),
            Fl(P_rect(bx - 560, by - 330, 60, 380, 0, r=10), WOOD), stk(P_rect(bx - 560, by - 330, 60, 380, 5, r=10), 7),
            Fl(P_rect(bx - 480, by - 190, 230, 80, 0, r=36), WHITE), stk(P_rect(bx - 480, by - 190, 230, 80, 5, r=36), 6),
            stk(P_line(bx - 500, by + 30, bx - 500, by + 110, 0, 1), 7), stk(P_line(bx + 500, by + 30, bx + 500, by + 110, 0, 2), 7)], 0.0, 0.5, snd=None)
    S.add(Fig(bx - 80, by - 128, 1.0, poses=[("lie", 0)], moods=[("worried", 0)], kind="bob", rot=-90, seed=11, enter="none", idle=0.4))
    S.draw([Fl(P_rect(bx - 300, by - 128, 760, 70, 0, r=20), (240, 186, 180)), stk(P_rect(bx - 300, by - 128, 760, 70, 5, r=20), 6)], 0.1, 0.4, snd=None)
    nx, ny = 1560, 760
    S.draw([Fl(P_rect(nx - 150, ny - 160, 300, 190, 0, r=10), WOOD), stk(P_rect(nx - 150, ny - 160, 300, 190, 5, r=10), 7),
            stk(P_line(nx - 120, ny + 30, nx - 120, ny + 120, 0, 1), 7), stk(P_line(nx + 120, ny + 30, nx + 120, ny + 120, 0, 2), 7)], 0.2, 0.4, snd=None)
    S.text("3:13", nx - 110, ny - 200, 84, RED, at=0.3)
    S.text("twice.", 300, 260, 110, INK, at=S.c("twice") - 0.1, rot=-3)
    S.pop([Fl(P_rect(nx - 20, ny - 190, 150, 32, 0, r=8), INK)], S.c("down") - 0.15, (nx + 55, ny - 175))
    S.text("a joke.", 1100, 330, 130, ORANGE, at=S.c("joke") - 0.25, rot=-4)


@V.scene("o3")
def _(S):
    S.noframe = True
    S.add(black(0.6))
    S.draw(door(760, 1040, 1.12), 0.0, 0.5, snd=None)
    t = S.e(0) + 0.2
    knocks(S, 1190, 360, t, size=150, seed=3)


@V.scene("c1")
def _(S):
    S.noframe = True
    S.add(black(0.97))
    S.text("DON'T OPEN", 150, 380, 210, WHITE, at=S.c("don't") - 0.05, rot=-3, cps=30)
    S.text("THE DOOR.", 190, 600, 210, RED, at=S.c("door") - 0.1, rot=-3, cps=30)
    S.text("episode 1: the knock", 200, 800, 92, (170, 164, 156), at=S.c("episode") - 0.05, rot=-2)
    S.draw([Fl(P_rect(1460, 230, 250, 560, 0), WOOD), stk(P_rect(1460, 230, 250, 560, 6), 7, WHITE),
            ("dot", 1585, 280, 8, INK), Fl(P_ell(1675, 530, 13, 13, 1, closed=True), RED)], 0.1, 0.5, snd=None)


# --------------------------------------------------------------------------- Maya, Noah, Mom
@V.scene("s1")
def _(S):
    cx, cy = 720, 820
    S.draw(couch(cx, cy, 1.0), 0.1, 0.5)
    S.add(Fig(cx + 40, cy - 112, 0.72, at=S.c("noah") - 0.1, poses=[("lie", 0)], moods=[("sleep", 0)], kind="spiky", rot=-90, seed=12, idle=0.3))
    S.draw([Fl(P_rect(cx - 120, cy - 138, 260, 62, 0, r=24), (150, 186, 214)), stk(P_rect(cx - 120, cy - 138, 260, 62, 5, r=24), 6)], S.c("asleep"), 0.4, snd=None)
    S.text("Noah, 8", cx - 100, cy - 350, 92, INK, at=S.c("noah") + 0.1, rot=-2)
    S.text("Z", cx - 250, cy - 200, 80, INK, at=S.c("asleep") + 0.2)
    S.text("Z", cx - 300, cy - 260, 66, INK, at=S.c("asleep") + 0.5)
    S.add(Fig(1560, 900, 1.25, at=0.0, poses=[("stand", 0), ("hips", S.c("twenty-four"))], moods=[("flat", 0)], kind="bob", seed=13))
    S.text("Maya, 24", 1350, 330, 92, ORANGE, at=S.c("maya") + 0.1, rot=-2)
    hx, hy = 1680, 160
    S.draw([Fl(P_rect(hx - 110, hy - 60, 220, 120, 0, r=8), WHITE), stk(P_rect(hx - 110, hy - 60, 220, 120, 5, r=8), 6),
            Fl(P_rect(hx - 12, hy - 40, 24, 80, 0), RED), Fl(P_rect(hx - 40, hy - 12, 80, 24, 0), RED)], S.c("hospital") - 0.3, 0.4)
    S.text("Mom: night shift", 880, 185, 80, INK, at=S.c("mom") - 0.1)
    S.text("sleeps through\nanything.", 180, 330, 84, GREY, at=S.c("sleeps", 1) - 0.1, lh=1.1)


@V.scene("s2")
def _(S):
    S.draw(door(560, 1040, 1.12), 0.0, 0.4, snd=None)
    for k, w in enumerate(("three", "slow", "polite")):
        S.text("knock", 840 + k * 60, 220 + k * 110, 100, RED, at=S.c(w) - 0.05, rot=(-6, 4, -3)[k], cps=60)
    bx, by = 1090, 640
    S.draw([Fl(P_rect(bx, by - 150, 660, 330, 0, r=40), WHITE), stk(P_rect(bx, by - 150, 660, 330, 6, r=40), 6),
            stk(P_poly([(bx + 10, by + 120), (bx - 70, by + 190), (bx + 60, by + 160)]), 6)], S.l(1) - 0.3, 0.35)
    S.text("\"Maya? Sweetheart,\nit's Mom.\nOpen the door.\"", bx + 40, by - 60, 74, INK, at=S.l(1) + 0.1, lh=1.15, cps=26)


@V.scene("s3")
def _(S):
    S.add(Fig(360, 920, 1.3, poses=[("think", 0), ("cross", S.c("never", 1))], moods=[("worried", 0)], kind="bob", seed=13))
    S.draw([Fl(P_rect(640, 170, 520, 230, 0, r=24), (40, 38, 42)), stk(P_rect(640, 170, 520, 230, 6, r=24), 7)], S.c("shift") - 0.3, 0.4)
    S.text("7:00", 900, 330, 130, (170, 164, 156), at=S.c("seven") - 0.1, anchor="m")
    S.text("shift ends", 660, 470, 70, GREY, at=S.c("shift") + 0.2)
    S.text("3:14", 1330, 360, 200, RED, at=S.c("3:14") - 0.1, rot=-3)
    S.text("\"sweetheart\"", 760, 700, 120, INK, at=S.c("sweetheart", 1) - 0.4, rot=-2)
    S.add(strike(740, 680, 1360, 650, S.c("sweetheart", 1) + 0.35, RED, 10))
    S.text("never.", 1420, 790, 110, RED, at=S.c("never", 1), rot=-4)


@V.scene("s4")
def _(S):
    S.noframe = True
    S.add(black(0.96))
    cx, cy, r = 900, 500, 380
    mx, my, ms = cx, cy + 880, 3.1
    inside = group(
        Dr([Fl(P_rect(cx - r - 20, cy - r - 20, 2 * r + 40, 2 * r + 40, 0), (232, 226, 212))], 0.0, 0.0, seed=1),
        Dr([stk(P_line(cx - r, cy - r, cx - 120, cy - 160, 0.0, 1), 5, GREY), stk(P_line(cx + r, cy - r, cx + 120, cy - 160, 0.0, 2), 5, GREY),
            stk(P_line(cx - r, cy + r, cx - 120, cy + 60, 0.0, 3), 5, GREY), stk(P_line(cx + r, cy + r, cx + 120, cy + 60, 0.0, 4), 5, GREY),
            stk(P_rect(cx - 120, cy - 160, 240, 220, 4), 5, GREY)], 0.0, 0.0, seed=2),
        Dr([Fl(P_poly([(mx - 150, cy + 150), (mx + 150, cy + 150), (mx + 330, cy + 520), (mx - 330, cy + 520)], True), COAT),
            stk(P_poly([(mx - 150, cy + 150), (mx + 150, cy + 150), (mx + 330, cy + 520), (mx - 330, cy + 520)], True), 8)], S.c("coat", 1) - 0.2, 0.4, seed=3),
        Fig(mx, my, ms, at=S.c("her", 1) - 0.25, poses=[("stand", 0)], moods=[("smile", 0), ("stare", S.c("blinking", 2) - 0.3)], kind="long",
            seed=21, enter="pop", idle=0.0),
        Dr([("dot", mx - 42 * ms, my - 285 * ms + 30 * ms, 7 * ms, ORANGE), ("dot", mx + 42 * ms, my - 285 * ms + 30 * ms, 7 * ms, ORANGE)],
           S.c("earrings", 1) - 0.1, 0.0, pop=True, anchor=(mx, my - 285 * ms), seed=4))
    S.add(clip_ell(inside, cx, cy, r, r))
    S.add(Dr([stk(P_ell(cx, cy, r + 6, r + 6, 1, 0.05), 14, (90, 86, 92))], S.l(0) + 0.1, 0.4, seed=5))
    S.text("her.", 1420, 270, 120, WHITE, at=S.c("her", 1), rot=-3)
    S.text("not blinking.", 1350, 480, 90, RED, at=S.c("blinking", 2) - 0.2, rot=-3)
    knocks(S, 1420, 680, S.e(2) + 0.25, size=88, gap=0.5, seed=5)


@V.scene("s5")
def _(S):
    S.draw(door(380, 1040, 1.05), 0.0, 0.4, snd=None)
    for k, (bx, by) in enumerate(((740, 300), (1220, 600))):
        at = S.l(0) - 0.2 if k == 0 else S.c("same", 1) - 0.1
        S.draw([Fl(P_rect(bx, by - 120, 600, 260, 0, r=36), WHITE), stk(P_rect(bx, by - 120, 600, 260, 6, r=36), 6)], at, 0.3)
        S.text("\"Maya? Sweetheart,\nit's Mom.\nOpen the door.\"", bx + 36, by - 50, 62, INK, at=at + 0.2, lh=1.12, cps=40 if k else 26)
    S.text("=", 1080, 540, 160, RED, at=S.c("same", 1) + 0.2)
    S.text("like a recording.", 670, 850, 100, RED, at=S.c("recording", 1) - 0.3, rot=-2)


@V.scene("s6")
def _(S):
    S.draw(door(300, 1040, 1.0), 0.0, 0.4, snd=None)
    t_run, t_c = S.c("running", 1) - 0.1, S.c("caught", 2)
    S.add(Fig(1150, 900, 0.8, at=0.0, poses=[("stand", 0)], moods=[("wow", 0)], kind="spiky", seed=12, walk=(1150, 640, t_run, t_c), flip=True))
    S.add(Fig(1700, 900, 1.2, at=0.0, poses=[("stand", 0), ("reach", t_c - 0.15)], moods=[("worried", 0)], kind="bob", seed=13,
              walk=(1700, 860, t_c - 0.7, t_c), flip=True))
    S.text("\"is that Mom?\"", 1000, 380, 80, GREY, at=S.l(0), rot=-2)
    S.text("one step.", 590, 300, 100, RED, at=S.c("step", 2) - 0.1, rot=-3)
    S.add(arrow(P_bez((640, 340), (600, 480), (460, 640)), S.c("handle", 2) - 0.2, RED, 7, 0.3))


@V.scene("s7")
def _(S):
    x0, y0, w, h = 160, 170, 1020, 600
    S.draw([Fl(P_rect(x0, y0, w, h, 0, r=40), (44, 42, 48)), stk(P_rect(x0, y0, w, h, 8, r=40), 8),
            Fl(P_rect(x0 + 40, y0 + 40, w - 80, h - 80, 0, r=14), (214, 226, 196))], 0.0, 0.5, snd=None)
    S.draw([Fl(P_rect(x0 + 40, y0 + 380, w - 80, 70, 0), (226, 219, 205)), stk(P_line(x0 + 40, y0 + 380, x0 + w - 40, y0 + 380, 0, 1), 6)], 0.1, 0.3, snd=None)
    S.add(Fig(x0 + 520, y0 + 470, 0.95, at=S.c("suit") - 0.2, poses=[("stand", 0)], moods=[("flat", 0)], kind="old", seed=31, enter="pop", idle=0.3))
    S.draw([Fl(P_poly([(x0 + 520, y0 + 250), (x0 + 535, y0 + 330), (x0 + 520, y0 + 360), (x0 + 505, y0 + 330)], True), RED)], S.c("suit") + 0.1, 0.2, snd=None)
    S.draw([Fl(P_rect(x0 + 40, y0 + h - 150, w - 80, 74, 0), RED)], S.l(1) - 0.2, 0.25, snd=None)
    S.add(screen_lines(x0 + w / 2, y0 + h - 95, w - 140, "DO NOT LET THEM IN", 60, WHITE, at=S.c("let", 1) - 0.2, cps=40))
    fit = lambda txt, sz: min(sz, (1830 - 1250) / text_w(txt, 1))
    S.text("someone you know", 1250, 230, fit("someone you know", 76), INK, at=S.c("someone", 1) - 0.1, rot=-2)
    S.text("may look normal.", 1250, 360, fit("may look normal.", 76), INK, at=S.c("normal", 1) - 0.2, rot=-2)
    S.text("they are not.", 1250, 490, 92, RED, at=S.c("not", 1, 1) - 0.15, rot=-2)
    ks = min(130, (1830 - 1250) / text_w("the knockers.", 1))
    S.text("the knockers.", 1250, 720, ks, RED, at=S.c("knockers", 2) - 0.25, rot=-4)


@V.scene("s8")
def _(S):
    S.add(black(0.35))
    cx, cy = 900, 900
    S.draw([Fl(P_rect(cx - 520, cy - 330, 1040, 330, 0, r=36), (176, 150, 196)), stk(P_rect(cx - 520, cy - 330, 1040, 330, 7, r=36), 8)], 0.0, 0.5, snd=None)
    blanket = P_bez((cx - 240, cy - 330), (cx - 200, cy - 520), (cx + 160, cy - 540), (cx + 230, cy - 330))
    S.draw([Fl(np.vstack([blanket, [(cx - 240, cy - 330)]]), (150, 186, 214)), stk(blanket, 7)], S.c("blanket") - 0.3, 0.4)
    for k, ex in enumerate((cx - 120, cx - 60, cx + 40, cx + 110)):
        S.pop([("dot", ex, cy - 400 + (8 if k > 1 else 0), 9, INK)], S.c("listened") + 0.06 * k, (ex, cy - 400), snd=None)
    for k, (tm, x, y) in enumerate((("3:40", 240, 220), ("4:30", 660, 160), ("5:20", 1100, 230), ("6:10", 1520, 170))):
        at = S.l(1) + k * 0.75
        S.text(tm, x, y, 76, GREY, at=at)
        S.text("knock", x - 10, y + 100, 72, RED, at=at + 0.2, rot=(-5, 4, -3, 6)[k])


@V.scene("s8b")
def _(S):
    S.draw(door(420, 1040, 1.05), 0.0, 0.4, snd=None)
    S.text("\"Maya?\"", 820, 270, 110, INK, at=S.c("words") - 0.3, rot=-3)
    S.add(strike(800, 240, 1140, 220, S.c("changed") - 0.1, RED, 10))
    S.text("\"Noah?\"", 1180, 290, 140, RED, at=S.l(1) + 0.05, rot=-4)
    S.add(Fig(1500, 900, 0.8, at=S.l(1) + 0.4, poses=[("stand", 0), ("facepalm", S.l(1) + 0.9)], moods=[("wow", 0), ("worried", S.l(1) + 1.2)],
              kind="spiky", seed=12, enter="pop"))
    S.text("she heard me.", 760, 640, 120, RED, at=S.c("heard", 2) - 0.2, rot=-3)


@V.scene("s8c")
def _(S):
    S.noframe = True
    S.add(black(0.9))
    S.text("6:58", 520, 560, 300, RED, at=S.c("6:58") - 0.1, rot=-3, cps=12)
    S.text("silence.", 1100, 700, 130, WHITE, at=S.c("stopped") + 0.2, rot=-3)


@V.scene("s9")
def _(S):
    wx, wy, ww, wh = 140, 120, 1640, 760
    S.draw([Fl(P_rect(wx, wy, ww, wh, 0), (214, 214, 210)), stk(P_rect(wx, wy, ww, wh, 8), 10)], 0.0, 0.5, snd=None)
    S.draw([stk(P_line(wx, wy + 560, wx + ww, wy + 560, 0.005, 1), 7)], 0.1, 0.3, snd=None)
    doors = [(330, 1), (700, 2), (1080, 3), (1450, 4)]
    for k, (dx, sd) in enumerate(doors):
        S.draw([Fl(P_rect(dx - 160, wy + 130, 320, 430, 0), (236, 230, 218)), stk(P_rect(dx - 160, wy + 130, 320, 430, 5), 6),
                Fl(P_rect(dx - 60, wy + 300, 120, 260, 0), (WOOD, (130, 150, 120), (170, 90, 80), (110, 120, 150))[k]),
                stk(P_rect(dx - 60, wy + 300, 120, 260, 4), 5)], 0.2 + 0.1 * k, 0.4, snd=None)
    t1 = S.c("standing", 1) - 0.2
    for k, (dx, sd) in enumerate(doors):
        S.add(Fig(dx + 10, wy + 562, 0.62, at=t1 + 0.35 * k, poses=[("wait", 0)], moods=[("blank", 0)], kind=("bob", "old", "spiky", "long")[k],
                  skin=KSKIN, seed=40 + k, enter="pop", idle=0.0))
    S.draw([stk(P_line(wx + ww / 2, wy, wx + ww / 2 + 2, wy + wh, 0.0, 5), 9), stk(P_line(wx, wy + wh / 2 - 120, wx + ww, wy + wh / 2 - 122, 0.0, 6), 9)],
           0.05, 0.3, snd=None)
    S.text("the baker", 600, 375, 70, INK, at=S.c("baker", 2) - 0.1, rot=-3)
    S.add(arrow(P_bez((680, 390), (700, 430), (712, 470)), S.c("baker", 2), INK, 5, 0.25))
    S.text("the dog lady", 1270, 375, 70, INK, at=S.c("lady", 2) - 0.1, rot=-3)
    S.add(arrow(P_bez((1400, 390), (1440, 430), (1462, 470)), S.c("lady", 2), INK, 5, 0.25))
    S.pop([Fl(P_ell(1530, wy + 540, 38, 22, 1, closed=True), HL), stk(P_ell(1530, wy + 540, 38, 22, 2, 0.06), 5),
           Fl(P_ell(1570, wy + 515, 18, 16, 3, closed=True), HL), stk(P_ell(1570, wy + 515, 18, 16, 4, 0.06), 5)],
          S.c("dog", 2) - 0.1, (1540, wy + 530))
    S.text("not moving.", 260, 230, 92, RED, at=S.c("moving", 1) - 0.2, rot=-2)
    S.text("just waiting.", 1180, 230, 92, RED, at=S.c("waiting", 1) - 0.2, rot=-2)


@V.scene("s10")
def _(S):
    pts = [(260, 900)]
    for k in range(7):
        x, y = 260 + k * 150, 900 - k * 95
        pts += [(x + 150, y), (x + 150, y - 95)]
    S.draw([stk(P_poly(pts), 12)], 0.0, 0.4, snd=None)
    S.draw([stk(P_line(260, 760, 1310, 95, 0.01, 2), 6, GREY)], 0.2, 0.4, snd=None)
    ox, oy = 1540, 640
    S.draw([Fl(P_rect(ox - 150, oy - 440, 300, 440, 0), (226, 219, 205)), stk(P_rect(ox - 150, oy - 440, 300, 440, 6), 7),
            Fl(P_rect(ox - 130, oy - 420, 260, 420, 0), NIGHT)], S.c("door") - 0.3, 0.4)
    S.draw([Fl(P_poly([(ox + 130, oy - 420), (ox + 230, oy - 470), (ox + 230, oy + 40), (ox + 130, oy)], True), WOOD),
            stk(P_poly([(ox + 130, oy - 420), (ox + 230, oy - 470), (ox + 230, oy + 40), (ox + 130, oy)], True), 6)], S.c("wide") - 0.2, 0.3)
    S.text("upstairs", 300, 300, 110, INK, at=S.c("upstairs") - 0.1, rot=-4)
    S.text("Mr. Duval", 1180, 120, 84, INK, at=S.c("duval's") - 0.1)
    S.text("open.", 1350, 820, 120, RED, at=S.c("open") - 0.1, rot=-3)


@V.scene("s11")
def _(S):
    px, py, ps = 760, 540, 2.4
    S.draw(ph_screen(px, py, ps), 0.0, 0.4, snd=None)
    S.add(snd="buzz", at=S.c("buzzed") - 0.1)
    sw = 170 * ps - 70
    S.add(screen_lines(px, py - 155 * ps + 110, sw - 80, "7:06", 60, GREY, at=S.c("7:06") - 0.1))
    S.draw(heart(px - 70, py - 200, 0.45, RED), S.c("text") - 0.2, 0.3, snd=None)
    S.add(screen_lines(px + 40, py - 185, sw - 150, "Mom", 70, INK, at=S.c("mom") - 0.1))
    S.draw([Fl(P_rect(px - 160, py - 110, 330, 300, 0, r=30), (226, 219, 205)), stk(P_rect(px - 160, py - 110, 330, 300, 5, r=30), 6)], S.l(1) - 0.3, 0.3)
    S.add(screen_lines(px + 5, py - 30, 280, "I'm outside\nyour door.\nWhy won't\nyou open?", 56, INK, at=S.l(1) + 0.05, cps=30))
    S.text("from Mom.", 1240, 400, 110, ORANGE, at=S.c("mom") + 0.1, rot=-3)
    S.text("outside?", 1260, 640, 120, RED, at=S.c("outside", 1) - 0.1, rot=-3)


@V.scene("s12")
def _(S):
    S.draw(door(320, 1040, 0.95), 0.0, 0.4, snd=None)
    S.add(Fig(900, 900, 0.8, poses=[("stand", 0)], moods=[("worried", 0)], kind="spiky", seed=12))
    S.add(Fig(1320, 900, 1.25, poses=[("stand", 0), ("think", S.l(1))], moods=[("worried", 0), ("flat", S.l(1))], kind="bob", seed=13, flip=True))
    S.text("\"what if it's\nreally her?\"", 760, 330, 84, GREY, at=S.l(0) + 0.2, lh=1.1)
    S.text("...", 1500, 420, 140, INK, at=S.c("answer", 1))


@V.scene("s13")
def _(S):
    S.noframe = True
    S.add(black(0.7))
    S.draw(door(700, 1040, 1.12), 0.0, 0.3, snd=None)
    knocks(S, 1130, 330, S.e(0) + 0.25, size=170, seed=9)


@V.scene("end")
def _(S):
    endcard(S, "episode 2:\nthe hallway.", note="a story in 4 episodes.")


if __name__ == "__main__":
    V.main()
