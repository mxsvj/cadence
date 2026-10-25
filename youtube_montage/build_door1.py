"""DON'T OPEN THE DOOR - episode 1: the knock. A doodle horror story in four episodes (pure fiction).
3:12 a.m., every phone gets the same alert: do not open your door. Then someone knocks, with Mom's voice.
The rule the episode sets up: the knockers only repeat what they have heard (it learns 'Noah' when Maya says it).
The cliffhanger breaks it: from below the peephole, the voice says something new.
Voices: Maya (narrator) af_heart, Mom af_bella (through the door), Noah af_nicole pitched up (a whisper), the news am_michael (radio)."""
from story_video import *  # noqa: F401,F403
from doodle_video import stk
from doodle import POSES, clip_ell

NARR, MOM, NOAH, NEWS = "af_heart", "af_bella", "af_nicole", "am_michael"
NIGHT = (24, 23, 28)
WHITE = (250, 248, 242)
DIM = (170, 164, 156)
WOOD = (156, 112, 78)
KSKIN = (198, 208, 186)          # the knockers: a shade too grey
COAT = (150, 186, 214)
LIGHT = (252, 236, 190)
POSES["wait"] = dict(la=(-8, -4), ra=(8, 4), ll=(-8, -4), rl=(8, 4), lean=0, tilt=13)

V = Story("door1", tapes=[("And that's when someone knocked.", "Don't Open the Door.", "tape"),
                          ("I looked through the peephole.", "The same words.", "cut"),
                          ("Then, at 6:58", "When it got light", "tape"),
                          ("At 7:06, my phone buzzed.", "Next: episode two", "cut")],
          say={"3:12": "three twelve", "3:14": "three fourteen", "6:58": "six fifty-eight", "7:06": "seven oh six"},
          swells=[("Then, from very low", "It wasn't repeating anymore.", 0.35)], dips=[("Next: episode two", None, 0.5)],
          hush=[("Around five, the words", "I had said his name")], beat_groups=("s13",), seed=21)
L = V.L
MOM_DOOR = '"Sweetheart, it\'s Mom. Open the door."'
DOOR = dict(voice=MOM, fx="door", speed=0.86, who="MOM'S VOICE")
NIGHT_TINT = (40, 48, 84)        # 3 a.m. inside the flat: blue-grey, ink still reads

L("o1", "At 3:12 in the morning, every phone in the city lit up at the same time.")
L("o1", "One message. No sender.")
L("o1", "Do not open your door. Do not answer anyone.")
L("o1", "I read it twice. Then I turned my phone face down, because it had to be a joke.")
L("o3", "And that's when someone knocked.", after=2.5)
L("o3", MOM_DOOR, after=0.6, **DOOR)
L("c1", "Don't Open the Door. Episode one: the knock.")
L("s1", "I'm Maya. That night, my little brother Noah was asleep on my couch, because Mom was working a night shift at the hospital.")
L("s3", "Her shift didn't end until seven. It was 3:14.")
L("s3", "And Mom never calls me sweetheart.")
L("s4", "I looked through the peephole.")
L("s4", "It was her. Her coat. Her hair. Her little gold earrings.")
L("s4", "She was smiling. And she wasn't blinking.", after=2.4)
L("s5", MOM_DOOR, **DOOR)
L("s5", "The same words. The same voice. Like a recording.")
L("s6", '"Maya? Is that Mom?"', voice=NOAH, fx="child", gain=-3, who="NOAH")
L("s6", "Noah was awake. And he was already running for the door.")
L("s6", '"Noah, no!"', gain=-3, fx="whisper", who="MAYA")
L("s6", "I caught him by his pajamas, one step before the handle.")
L("s7", "On the news, they said it had started two days earlier, in the south. Nobody up here had taken it seriously.")
L("s7", '"If someone you know is at your door, do not let them in. They may look normal. They are not."', voice=NEWS, fx="radio", speed=1.0, who="NEWS")
L("s7", "Down south, people called them the knockers.", after=0.4)
L("s8", "We hid behind the couch, under a blanket, and listened.")
L("s8", "She knocked every ten minutes, all night.")
L("s8b", "Around five, the words changed.")
L("s8b", '"Noah? Sweetheart, it\'s Mom. Open the door."', **DOOR)
L("s8b", "I had said his name once, when I caught him. She had heard it.")
L("s8c", "Then, at 6:58, the knocking stopped.", after=1.0)
L("s9", "When it got light, I looked through the peephole again.")
L("s9", "Someone was standing outside every other door on my floor. Not moving. Just waiting.")
L("s9", "The baker from downstairs. Mister Duval from upstairs, still in his slippers.")
L("s11", "At 7:06, my phone buzzed. A text from Mom.")
L("s11", '"I\'m outside your door."', voice=MOM, speed=0.9, who="TEXT FROM MOM")
L("s12", "I looked again. Still nobody outside mine. Nobody I could see.")
L("s12", '"Maya... what if it\'s really her?"', voice=NOAH, fx="child", gain=-3, who="NOAH")
L("s13", "Then, from very low, right behind the door, a voice spoke.")
L("s13", '"I\'m down here, sweetheart. Why won\'t you open?"', **DOOR)
L("s13", "It wasn't repeating anymore.", after=2.8)
L("end", "Next: episode two, the hallway. Subscribe, so you don't miss it. And whatever happens... don't open the door.")


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


def group(*fns):
    def fn(ctx, t):
        for f in fns:
            f(ctx, t)
    return fn


def door(x, y, s=1.0, col=WOOD, lever=True):
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
            ("dot", x, y0 + 62 * s, 9 * s, INK),
            Fl(P_rect(x0 + 8 * s, y - 7 * s, w - 16 * s, 9 * s, 0), LIGHT)] + (lever_op(x, y, s) if lever else [])


def lever_op(x, y, s=1.0, down=0.0):
    """The door's lever handle; down = how far it has been pushed (degrees)."""
    w, h = 360 * s, 800 * s
    hx, hy = x - w / 2 + w - 52 * s, y - h + h * 0.53
    a = math.radians(down)
    return [stk(P_line(hx, hy, hx - 66 * s * math.cos(a), hy + 5 * s + 66 * s * math.sin(a), 0.02, 3), 10 * s)]


def knocks(S, x, y, at, size=120, gap=Story.KNOCK_GAP, col=RED, sound=True, seed=0, dy=1.15, dx=40):
    r = random.Random(seed)
    for k in range(3):
        S.text("KNOCK", x + r.randint(-20, 20) + k * dx, y + k * size * dy, size, col, at=at + k * gap, rot=r.uniform(-7, 5), cps=60)
    if sound:
        S.add(snd="knock3", at=at)


def bubble_text(S, x, y, w, text, at, size=74, col=INK, lh=1.15, cps=26):
    """A speech bubble sized to its text (never a word through the border), tail at bottom-left."""
    lines = text.split("\n")
    sz = min(size, (w - 80) / max(text_w(ln, 1) for ln in lines))
    h = sz * lh * len(lines) + 70
    S.draw([Fl(P_rect(x, y, w, h, 0, r=36), WHITE), stk(P_rect(x, y, w, h, 6, r=36), 6),
            stk(P_poly([(x + 30, y + h - 6), (x - 50, y + h + 60), (x + 80, y + h - 4)]), 6)], at - 0.3, 0.35, snd=None)
    S.text(text, x + 40, y + 30 + sz * 0.8, sz, col, at=at + 0.1, lh=lh, cps=cps)


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


def back_fig(x, y, s=1.0, hair="bald", skin=KSKIN, coat=None, slippers=False):
    """A knocker seen from behind, facing a door: same proportions as Fig, no face, head tilted a little."""
    hip, sh, neck = (x, y - 124 * s), (x, y - 223 * s), (x, y - 242 * s)
    hx, hy, R = x + 6 * s, y - 285 * s, 40 * s
    o = []
    if coat:
        body = [(x - 44 * s, y - 230 * s), (x + 44 * s, y - 230 * s), (x + 66 * s, y - 92 * s), (x - 66 * s, y - 92 * s)]
        o += [Fl(P_poly(body, True), coat), stk(P_poly(body, True), 6 * s)]
    o += [stk(P_line(hip[0], hip[1], x - 18 * s, y, 0.01, 1), 7.5 * s), stk(P_line(hip[0], hip[1], x + 18 * s, y, 0.01, 2), 7.5 * s),
          stk(P_line(hip[0], hip[1], neck[0], neck[1], 0.01, 3), 7.5 * s),
          stk(P_poly([sh, (x - 36 * s, y - 165 * s), (x - 40 * s, y - 102 * s)]), 7.5 * s),
          stk(P_poly([sh, (x + 36 * s, y - 165 * s), (x + 40 * s, y - 102 * s)]), 7.5 * s),
          Fl(P_ell(hx, hy, R, R * 1.03, 1, closed=True), skin), stk(P_ell(hx, hy, R, R * 1.03, 2, 0.08), 7.5 * s)]
    if hair == "bald":
        o.append(stk(P_arc(hx, hy, R * 0.97, R * 0.97, 15, 165), 7 * s, GREY))
    elif hair == "chef":
        o += [Fl(P_rect(hx - 34 * s, hy - R - 66 * s, 68 * s, 76 * s, 0, r=18 * s), WHITE), stk(P_rect(hx - 34 * s, hy - R - 66 * s, 68 * s, 76 * s, 4 * s, r=18 * s), 5 * s),
              stk(P_line(hx - 34 * s, hy - R + 2 * s, hx + 34 * s, hy - R + 2 * s, 0.02, 4), 5 * s)]
    if slippers:
        for k in (-1, 1):
            o += [Fl(P_ell(x + k * 22 * s, y + 4 * s, 20 * s, 9 * s, 3 + k, closed=True), PINK), stk(P_ell(x + k * 22 * s, y + 4 * s, 20 * s, 9 * s, 5 + k, 0.05), 4 * s)]
    return o


def hallway(cx, cy, r, knockers_at=None):
    """What the peephole shows, the same every time: the landing, the two doors opposite (green, blue), and, once they have come,
    a knocker at each, seen from behind (the baker, Mister Duval in his slippers)."""
    fns = [Dr([Fl(P_rect(cx - r - 20, cy - r - 20, 2 * r + 40, 2 * r + 40, 0), (236, 232, 222))], 0.0, 0.0, seed=1),
           Dr([stk(P_rect(cx - 0.86 * r, cy - 0.62 * r, 1.72 * r, 1.14 * r, 4), 5, GREY),
               stk(P_line(cx - r, cy - r, cx - 0.86 * r, cy - 0.62 * r, 0.0, 1), 5, GREY), stk(P_line(cx + r, cy - r, cx + 0.86 * r, cy - 0.62 * r, 0.0, 2), 5, GREY),
               stk(P_line(cx - r, cy + r, cx - 0.86 * r, cy + 0.52 * r, 0.0, 3), 5, GREY), stk(P_line(cx + r, cy + r, cx + 0.86 * r, cy + 0.52 * r, 0.0, 4), 5, GREY)],
              0.0, 0.0, seed=2),
           Dr([Fl(P_rect(cx - 0.66 * r, cy - 0.5 * r, 0.44 * r, 1.02 * r, 0), (130, 150, 120)), stk(P_rect(cx - 0.66 * r, cy - 0.5 * r, 0.44 * r, 1.02 * r, 4), 6),
               Fl(P_rect(cx + 0.22 * r, cy - 0.5 * r, 0.44 * r, 1.02 * r, 0), (110, 120, 150)), stk(P_rect(cx + 0.22 * r, cy - 0.5 * r, 0.44 * r, 1.02 * r, 4), 6),
               ("dot", cx - 0.28 * r, cy + 0.05 * r, 8, HL), ("dot", cx + 0.28 * r, cy + 0.05 * r, 8, HL)], 0.0, 0.0, seed=3)]
    if knockers_at is not None:
        fy, fs = cy + 0.56 * r, 0.0026 * r
        fns += [Dr(back_fig(cx - 0.44 * r, fy, fs, hair="chef"), knockers_at, 0.0, pop=True, anchor=(cx - 0.44 * r, cy), seed=4),
                Dr(back_fig(cx + 0.44 * r, fy, fs, hair="bald", coat=(150, 130, 110), slippers=True), knockers_at + 0.5, 0.0, pop=True,
                   anchor=(cx + 0.44 * r, cy), seed=5)]
    return fns


PEEP = (880, 510, 390)


def peep_ring(S, cx, cy, r, at):
    S.add(Dr([stk(P_ell(cx, cy, r + 6, r + 6, 1, 0.05), 14, (90, 86, 92))], at, 0.3, seed=5))


# --------------------------------------------------------------------------- 3:12 (the first frame is already the alert)
@V.scene("o1")
def _(S):
    S.noframe = True
    S.add(black(0.96))
    px, py, ps = 600, 500, 2.9
    sw = 170 * ps - 70
    S.add(Dr(ph_screen(px, py, ps), 0.0, 0.0, seed=7))
    S.add(snd="buzz", at=S.c("lit") - 0.1)
    S.add(Dr([Fl(P_rect(px - 85 * ps + 18, py - 155 * ps + 60, 170 * ps - 36, 86, 0, r=12), RED)], 0.0, 0.0, seed=8))
    S.add(screen_lines(px, py - 155 * ps + 122, sw - 40, "ALERT", 66, WHITE, at=-2.0, cps=400))
    S.add(screen_lines(px, py - 90, sw, "DO NOT\nOPEN YOUR\nDOOR.", 96, INK, at=-2.0, cps=400))
    S.add(screen_lines(px, py + 215, sw - 60, "from: ???", 72, GREY, at=S.c("sender", 1) - 0.1))
    S.add(screen_lines(px, py + 330, sw, "DON'T ANSWER.", 74, RED, at=S.c("answer", 2) - 0.2, cps=30))
    S.text("3:12", 1100, 420, 280, WHITE, at=-2.0, cps=400, rot=-3)
    S.text("a.m.", 1180, 590, 110, DIM, at=S.c("morning") - 0.05, rot=-3)
    S.text("every phone.", 1110, 770, 96, RED, at=S.c("every"), rot=-3, until=S.l(3) - 0.1)
    t_down = S.c("down", 3) - 0.1
    S.add(Dr([Fl(P_rect(px - 85 * ps - 6, py - 155 * ps - 6, 170 * ps + 12, 310 * ps + 12, 0, r=26 * ps), (52, 50, 56)),
              stk(P_rect(px - 85 * ps - 6, py - 155 * ps - 6, 170 * ps + 12, 310 * ps + 12, 8 * ps, r=26 * ps), 7 * ps, (90, 86, 92))],
             t_down, 0.0, pop=True, anchor=(px, py), seed=9))
    S.text("twice.", 1110, 770, 96, WHITE, at=S.c("twice", 3) - 0.1, rot=-3)
    S.text("a joke.", 1420, 840, 104, ORANGE, at=S.c("joke", 3) - 0.25, rot=-4)


@V.scene("o3")
def _(S):
    S.noframe = True
    S.add(black(0.6))
    S.draw(door(620, 1040, 1.12), 0.0, 0.3, snd=None)
    knocks(S, 1060, 240, S.e(0) + 0.2, size=118, seed=3, dy=1.0, dx=50)
    bubble_text(S, 1050, 560, 700, "\"Sweetheart,\nit's Mom.\nOpen the door.\"", S.l(1), size=78)


@V.scene("c1")
def _(S):
    S.noframe = True
    S.add(black(0.97))
    S.text("DON'T OPEN", 150, 380, 210, WHITE, at=S.c("don't") - 0.05, rot=-3, cps=30)
    S.text("THE DOOR.", 190, 600, 210, RED, at=S.c("door") - 0.1, rot=-3, cps=30)
    S.text("episode 1: the knock", 200, 800, 92, DIM, at=S.c("episode") - 0.05, rot=-2)
    S.draw([Fl(P_rect(1460, 230, 250, 560, 0), WOOD), stk(P_rect(1460, 230, 250, 560, 6), 7, WHITE),
            ("dot", 1585, 280, 8, INK), Fl(P_ell(1675, 530, 13, 13, 1, closed=True), RED)], 0.1, 0.5, snd=None)


# --------------------------------------------------------------------------- Maya, Noah, Mom
@V.scene("s1")
def _(S):
    S.add(black(0.38, NIGHT_TINT))
    cx, cy = 720, 820
    S.draw(couch(cx, cy, 1.0), 0.05, 0.5, snd=None)
    S.add(Fig(1560, 900, 1.25, at=0.0, poses=[("stand", 0)], moods=[("flat", 0)], kind="bob", seed=13))
    S.text("Maya, 24", 1330, 330, 92, INK, at=S.c("maya") + 0.05, rot=-2)
    S.add(Fig(cx + 40, cy - 112, 0.72, at=S.c("noah") - 0.1, poses=[("lie", 0)], moods=[("sleep", 0)], kind="spiky", rot=-90, seed=12, idle=0.3))
    S.draw([Fl(P_rect(cx - 120, cy - 138, 260, 62, 0, r=24), COAT), stk(P_rect(cx - 120, cy - 138, 260, 62, 5, r=24), 6)], S.c("asleep"), 0.4, snd=None)
    S.text("Noah, 8", cx - 100, cy - 350, 92, INK, at=S.c("noah") + 0.1, rot=-2)
    S.text("Z", cx - 250, cy - 200, 80, INK, at=S.c("asleep") + 0.2)
    S.text("Z", cx - 300, cy - 260, 66, INK, at=S.c("asleep") + 0.5)
    hx, hy = 1680, 160
    S.draw([Fl(P_rect(hx - 110, hy - 60, 220, 120, 0, r=8), WHITE), stk(P_rect(hx - 110, hy - 60, 220, 120, 5, r=8), 6),
            Fl(P_rect(hx - 12, hy - 40, 24, 80, 0), RED), Fl(P_rect(hx - 40, hy - 12, 80, 24, 0), RED)], S.c("hospital") - 0.3, 0.4, snd=None)
    S.text("Mom: night shift", 880, 185, 80, INK, at=S.c("mom") - 0.1)


@V.scene("s3")
def _(S):
    S.add(black(0.38, NIGHT_TINT))
    S.add(Fig(360, 920, 1.3, poses=[("think", 0), ("cross", S.c("never", 1))], moods=[("worried", 0)], kind="bob", seed=13))
    S.draw([Fl(P_rect(640, 170, 520, 230, 0, r=24), (40, 38, 42)), stk(P_rect(640, 170, 520, 230, 6, r=24), 7)], 0.05, 0.4, snd=None)
    S.text("7:00", 900, 330, 130, DIM, at=S.c("seven") - 0.1, anchor="m")
    S.text("shift ends", 660, 470, 72, INK, at=S.c("shift") + 0.2)
    S.text("3:14", 1330, 360, 200, RED, at=S.c("3:14") - 0.1, rot=-3)
    S.text("\"sweetheart\"", 760, 700, 120, INK, at=S.c("sweetheart", 1) - 0.4, rot=-2)
    S.add(strike(740, 680, 1360, 650, S.c("sweetheart", 1) + 0.35, RED, 10))
    S.text("never.", 1420, 790, 110, RED, at=S.c("never", 1), rot=-4)


@V.scene("s4")
def _(S):
    S.noframe = True
    S.add(black(0.96))
    cx, cy, r = PEEP
    mx, ms = cx, 3.0
    my = cy + 285 * ms
    t_her = S.c("her", 1) - 0.25
    inside = group(*hallway(cx, cy, r),
        Dr([Fl(P_poly([(mx - 150, cy + 150), (mx + 150, cy + 150), (mx + 330, cy + 520), (mx - 330, cy + 520)], True), COAT),
            stk(P_poly([(mx - 150, cy + 150), (mx + 150, cy + 150), (mx + 330, cy + 520), (mx - 330, cy + 520)], True), 8)], S.c("coat", 1) - 0.2, 0.4, seed=3),
        Fig(mx, my, ms, at=t_her, poses=[("stand", 0)], moods=[("stare", 0)], kind="long", seed=21, enter="pop", idle=0.0),
        Dr([("dot", mx - 45 * ms, cy + 14 * ms, 3.6 * ms, ORANGE), ("dot", mx + 45 * ms, cy + 14 * ms, 3.6 * ms, ORANGE)],
           S.c("earrings", 1) - 0.1, 0.0, pop=True, anchor=(mx, cy), seed=4))
    S.add(clip_ell(inside, cx, cy, r, r))
    peep_ring(S, cx, cy, r, S.l(0) + 0.1)
    S.text("her.", 1420, 260, 120, WHITE, at=S.c("her", 1), rot=-3)
    S.text("not blinking.", 1350, 460, 90, RED, at=S.c("blinking", 2) - 0.2, rot=-3)
    knocks(S, 1400, 640, S.e(2) + 0.25, size=80, seed=5, dy=1.2, dx=36)


@V.scene("s5")
def _(S):
    S.add(black(0.38, NIGHT_TINT))
    S.draw(door(380, 1040, 1.05), 0.0, 0.4, snd=None)
    bubble_text(S, 740, 210, 560, "\"Sweetheart,\nit's Mom.\nOpen the door.\"", S.l(0), size=62)
    bubble_text(S, 1250, 400, 560, "\"Sweetheart,\nit's Mom.\nOpen the door.\"", S.c("same", 1) - 0.1, size=62, cps=40)
    S.text("=", 1120, 610, 150, RED, at=S.c("same", 1) + 0.2)
    S.text("like a recording.", 690, 860, 100, RED, at=S.c("recording", 1) - 0.3, rot=-2)


@V.scene("s6")
def _(S):
    S.add(black(0.38, NIGHT_TINT))
    S.draw(door(300, 1040, 1.0), 0.0, 0.4, snd=None)
    t_run, t_c = S.c("running", 1) - 0.1, S.c("caught", 3)
    S.add(Fig(1150, 900, 0.8, at=0.0, poses=[("stand", 0)], moods=[("wow", 0)], kind="spiky", seed=12, walk=(1150, 640, t_run, t_c), flip=True))
    S.add(Fig(1700, 900, 1.2, at=0.0, poses=[("stand", 0), ("reach", t_c - 0.15)], moods=[("worried", 0)], kind="bob", seed=13,
              walk=(1700, 860, S.l(2) - 0.2, t_c), flip=True))
    S.text("\"is that Mom?\"", 1080, 250, 84, INK, at=S.l(0), rot=-2)
    S.text("\"Noah, no!\"", 1330, 400, 92, ORANGE, at=S.l(2), rot=-3)
    S.text("one step.", 590, 300, 100, RED, at=S.c("step", 3) - 0.1, rot=-3)
    S.add(arrow(P_bez((640, 340), (600, 480), (460, 640)), S.c("handle", 3) - 0.2, RED, 7, 0.3))


@V.scene("s7")
def _(S):
    S.add(black(0.38, NIGHT_TINT))
    x0, y0, w, h = 160, 170, 1020, 600
    S.draw([Fl(P_rect(x0, y0, w, h, 0, r=40), (44, 42, 48)), stk(P_rect(x0, y0, w, h, 8, r=40), 8),
            Fl(P_rect(x0 + 40, y0 + 40, w - 80, h - 80, 0, r=14), (214, 226, 196))], 0.0, 0.4, snd=None)
    S.draw([Fl(P_rect(x0 + 40, y0 + 380, w - 80, 70, 0), (226, 219, 205)), stk(P_line(x0 + 40, y0 + 380, x0 + w - 40, y0 + 380, 0, 1), 6)], 0.1, 0.3, snd=None)
    S.add(Fig(x0 + 520, y0 + 470, 0.95, at=S.c("news") - 0.2, poses=[("stand", 0)], moods=[("flat", 0)], kind="old", seed=31, enter="pop", idle=0.3))
    S.draw([Fl(P_poly([(x0 + 520, y0 + 250), (x0 + 535, y0 + 330), (x0 + 520, y0 + 360), (x0 + 505, y0 + 330)], True), RED)], S.c("news") + 0.1, 0.2, snd=None)
    S.draw([Fl(P_rect(x0 + 40, y0 + h - 150, w - 80, 74, 0), RED)], S.c("started") - 0.2, 0.25, snd=None)
    t_let = S.c("let", 1) - 0.2
    S.add(screen_lines(x0 + w / 2, y0 + h - 95, w - 140, "STARTED 2 DAYS AGO, IN THE SOUTH", 60, WHITE, at=S.c("started") - 0.05, cps=40, until=t_let - 0.25))
    S.add(screen_lines(x0 + w / 2, y0 + h - 95, w - 140, "DO NOT LET THEM IN", 60, WHITE, at=t_let, cps=40))
    fit = lambda txt, sz: min(sz, (1830 - 1250) / text_w(txt, 1))
    S.text("nobody believed it.", 1250, 230, fit("nobody believed it.", 76), INK, at=S.c("nobody") - 0.1, rot=-2)
    S.text("may look normal.", 1250, 380, fit("may look normal.", 80), INK, at=S.c("normal", 1) - 0.2, rot=-2)
    S.text("they are not.", 1250, 520, 92, RED, at=S.c("not", 1, 1) - 0.15, rot=-2)
    S.text("the knockers.", 1250, 740, fit("the knockers.", 130), RED, at=S.c("knockers", 2) - 0.25, rot=-4)


@V.scene("s8")
def _(S):
    S.add(black(0.38, NIGHT_TINT))
    cx, cy = 880, 960
    tent = P_bez((cx - 260, cy - 360), (cx - 170, cy - 560), (cx + 200, cy - 560), (cx + 290, cy - 360))
    S.draw([Fl(tent.tolist() + [(cx - 260, cy - 360)], COAT), stk(tent, 6)], S.c("blanket") - 0.2, 0.4, snd=None)
    S.add(Fig(cx - 120, cy - 120, 1.0, at=0.45, poses=[("stand", 0)], moods=[("worried", 0)], kind="bob", seed=13, enter="none", idle=0.5))
    S.add(Fig(cx + 110, cy - 190, 0.72, at=0.45, poses=[("stand", 0)], moods=[("wow", 0)], kind="spiky", seed=12, enter="none", idle=0.5))
    S.draw([Fl(P_rect(cx - 520, cy - 360, 1040, 360, 0, r=40), (176, 150, 196)), stk(P_rect(cx - 520, cy - 360, 1040, 360, 7, r=40), 8)], 0.0, 0.4, snd=None)
    S.text("behind the couch.", 180, 230, 84, INK, at=S.c("couch") - 0.1, rot=-2)
    S.add(snd="knock1m", at=S.l(1) + 0.25)
    for k, (tm, x, y) in enumerate((("3:40", 1120, 200), ("3:50", 1460, 260), ("4:00", 1180, 400), ("4:10", 1520, 470))):
        at = S.l(1) + 0.1 + k * 0.42
        S.text(tm, x, y, 72, INK, at=at)
        S.text("knock", x + 150, y + 4, 70, RED, at=at + 0.15, rot=(-5, 4, -3, 6)[k])


@V.scene("s8b")
def _(S):
    S.add(black(0.38, NIGHT_TINT))
    S.draw(door(380, 1040, 1.05), 0.0, 0.4, snd=None)
    S.text("\"Sweetheart, it's Mom.\"", 840, 380, 92, INK, at=S.c("words") - 0.3, rot=-2)
    S.text("\"Noah?\"", 700, 230, 140, RED, at=S.l(1) + 0.05, rot=-4)
    S.add(arrow(P_bez((760, 250), (790, 300), (835, 335)), S.l(1) + 0.3, RED, 7, 0.3))
    S.add(Fig(1560, 920, 1.15, at=0.0, poses=[("stand", 0), ("facepalm", S.c("heard", 2) - 0.2)], moods=[("worried", 0), ("sad", S.c("heard", 2))],
              kind="bob", seed=13))
    S.text("she heard me.", 700, 640, 120, RED, at=S.c("heard", 2) - 0.2, rot=-3)


@V.scene("s8c")
def _(S):
    S.noframe = True
    S.add(black(0.9))
    S.text("6:58", 520, 560, 300, RED, at=S.c("6:58") - 0.1, rot=-3, cps=12)
    S.text("silence.", 1100, 700, 130, WHITE, at=S.c("stopped") + 0.2, rot=-3)


@V.scene("s9")
def _(S):
    S.noframe = True
    S.add(black(0.96))
    cx, cy, r = PEEP
    S.add(clip_ell(group(*hallway(cx, cy, r, knockers_at=S.c("standing", 1) - 0.2)), cx, cy, r, r))
    peep_ring(S, cx, cy, r, 0.05)
    S.text("every other door.", 1320, 240, min(92, 500 / text_w("every other door.", 1)), WHITE, at=S.c("every", 1) - 0.1, rot=-3)
    S.text("not moving.", 1340, 390, 90, RED, at=S.c("moving", 1) - 0.2, rot=-3)
    S.text("the baker", 1340, 590, 80, WHITE, at=S.c("baker", 2) - 0.1, rot=-2)
    S.text("Mr. Duval", 1340, 720, 80, WHITE, at=S.c("duval", 2) - 0.1, rot=-2)
    S.text("(slippers)", 1360, 820, 64, DIM, at=S.c("slippers", 2) - 0.1, rot=-2)


@V.scene("s11")
def _(S):
    px, py, ps = 760, 540, 2.4
    S.draw(ph_screen(px, py, ps), 0.0, 0.3, snd=None)
    S.add(snd="buzz", at=S.c("buzzed") - 0.1)
    sw = 170 * ps - 70
    S.add(screen_lines(px, py - 155 * ps + 110, sw - 80, "7:06", 60, GREY, at=S.c("7:06") - 0.1))
    S.draw(heart(px - 70, py - 200, 0.45, RED), S.c("text") - 0.2, 0.3, snd=None)
    S.add(screen_lines(px + 40, py - 185, sw - 150, "Mom", 70, INK, at=S.c("mom") - 0.1))
    S.draw([Fl(P_rect(px - 160, py - 110, 330, 300, 0, r=30), (226, 219, 205)), stk(P_rect(px - 160, py - 110, 330, 300, 5, r=30), 6)], S.l(1) - 0.3, 0.3, snd=None)
    S.add(screen_lines(px + 5, py + 20, 280, "I'm outside\nyour door.", 64, INK, at=S.l(1) + 0.05, cps=30))
    S.text("from Mom.", 1240, 400, 110, ORANGE, at=S.c("mom") + 0.1, rot=-3)
    S.text("outside?", 1260, 640, 120, RED, at=S.c("outside", 1) - 0.1, rot=-3)


@V.scene("s12")
def _(S):
    S.noframe = True
    S.add(black(0.96))
    cx, cy, r = PEEP
    S.add(clip_ell(group(*hallway(cx, cy, r, knockers_at=-1.0)), cx, cy, r, r))
    peep_ring(S, cx, cy, r, 0.05)
    S.text("still nobody", 1320, 330, min(110, 500 / text_w("still nobody", 1)), WHITE, at=S.c("nobody") - 0.1, rot=-3)
    S.text("at mine.", 1360, 460, 110, WHITE, at=S.c("mine") - 0.1, rot=-3)
    S.text("(that I could see)", 1340, 580, 70, DIM, at=S.c("see") - 0.3, rot=-3)
    S.text("\"what if it's\nreally her?\"", 1310, 740, 80, ORANGE, at=S.l(1) + 0.2, lh=1.1)


@V.scene("s13")
def _(S):
    S.noframe = True
    S.add(black(0.78))
    dx_, dy_, ds = 760, 900, 1.0
    w = 360 * ds
    x0 = dx_ - w / 2
    S.push(0.08, cx=dx_, cy=dy_ - 60)                                   # a slow push-in towards the gap under the door
    S.draw([stk(P_line(140, dy_, 1780, dy_ + 4, 0.004, 1), 6, (120, 116, 112))], 0.0, 0.3, snd=None)
    S.draw(door(dx_, dy_, ds, lever=False), 0.0, 0.3, snd=None)
    S.add(Dr([Fl(P_rect(x0 + 8, dy_ - 30, w - 16, 30, 0), LIGHT)], 0.0, 0.0, seed=11))          # the light under the door
    t_open = S.c("open", 1) - 0.1
    S.add(Dr(lever_op(dx_, dy_, ds), 0.0, 0.0, seed=12, until=t_open - EXIT))
    S.add(Dr(lever_op(dx_, dy_, ds, down=28), t_open, 0.0, seed=13))
    S.pop([Fl(P_rect(x0 + 60 + k * 150, dy_ - 30, 70, 30, 0, r=8), NIGHT) for k in range(2)], S.c("low") - 0.1, (dx_, dy_ - 15), snd=None)
    t_f = S.c("here", 1) - 0.35
    slide = lambda u: (0.0, 70 * ease_out(min(1.0, u / 1.1)), 0.0, 1.0)
    fingers = []
    for k, (fx, ln) in enumerate(((0, 40), (40, 50), (80, 48), (120, 38))):      # four long grey fingers, nails toward us
        cx_f = x0 + 100 + fx
        fingers += [Fl(P_ell(cx_f, dy_ - 10 + ln / 2, 17, ln, k, closed=True), KSKIN), stk(P_ell(cx_f, dy_ - 10 + ln / 2, 17, ln, k + 4, 0.06), 5),
                    stk(P_arc(cx_f, dy_ + ln * 1.2, 10, 8, 200, 340, 12), 4)]
    S.add(Dr(fingers, t_f, 0.0, move=slide, anchor=(x0 + 160, dy_), seed=14))
    S.text("down here.", 1120, 560, 130, RED, at=S.c("here", 1) - 0.3, rot=-3)
    S.text("it wasn't repeating\nanymore.", 1120, 280, 84, WHITE, at=S.c("repeating", 2) - 0.3, lh=1.1, rot=-2)
    S.add(black(1.0, at=S.e(2) + 0.35))                 # hard cut to black, and silence


@V.scene("end")
def _(S):
    """The end screen on a dark page (YouTube's elements go on the round target and the 16:9 box), no mascot."""
    S.noframe = True
    S.add(black(0.95))
    t0 = S.l(0)
    S.text("a story in 4 episodes.", 130, 150, 76, DIM, at=t0 + 0.1)
    sx, sy, r = 470, 540, 125
    S.draw([Fl(P_ell(sx, sy, r, r, 1, closed=True), RED), stk(P_ell(sx, sy, r, r, 3, 0.06), 8, WHITE)], t0 + 0.3, 0.4, snd=None)
    S.draw([stk(P_line(sx - 45, sy, sx + 45, sy, 0.02, 1), 11, WHITE), stk(P_line(sx, sy - 45, sx, sy + 45, 0.02, 2), 11, WHITE)], t0 + 0.6, 0.25, snd=None)
    S.text("subscribe", sx, sy + r + 95, 80, WHITE, at=S.c("subscribe") - 0.2, anchor="m")
    vx, vy, vw, vh = 1290, 540, 720, 405
    S.draw([Fl(P_rect(vx - vw / 2, vy - vh / 2, vw, vh, 0, r=14), (44, 42, 48)), stk(P_rect(vx - vw / 2, vy - vh / 2, vw, vh, 8, r=14), 7, WHITE)],
           t0 + 0.2, 0.4, snd=None)
    S.text("next:", vx - vw / 2 + 10, vy - vh / 2 - 30, 70, DIM, at=t0 + 0.3)
    S.text("episode 2:\nthe hallway.", vx, vy - 10, 84, WHITE, at=t0 + 0.5, anchor="m")
    S.text("don't open the door.", 640, 890 - 30, 90, RED, at=S.c("open") - 0.3, rot=-2)
    S.add(snd="knock1", at=S.dur - 2.4)


if __name__ == "__main__":
    V.main()
