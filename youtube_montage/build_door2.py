"""DON'T OPEN THE DOOR - episode 2: the hallway. Cold open on the test (Maya asks the door a question only Mom would
know; it answers in Maya's own voice), then a recap with the rule, Noah and the 7:06 text.
The explanation: it cuts and pastes what it has heard through the walls (Duval's "sweetheart", the neighbour's "why won't
you open?"). Mom texts from a nurse's phone; Maya calls back; Mom calls her Bean, the answer the door never knew. Knockers
don't type: who sent the 7:06 text? They open the door (the mat is empty, a wet smear), cross the landing hand in hand,
the bottle rolls, Maya lets go for one second, the baker's head turns round and says Noah's line in Noah's voice.
At the stairs Noah's voice cries from Duval's flat upstairs; Noah whispers "That's not me"; the voice upstairs says it
too. The hand in Maya's stops shaking."""
from story_video import *  # noqa: F401,F403
from doodle_video import stk
from doodle import POSES, clip_ell
from build_door1 import (COAT, DIM, KSKIN, LIGHT, NIGHT, WHITE, WOOD, back_fig, black, door, group, hallway, peep_ring,
                         ph_screen, screen_lines)

NARR, MOM, NOAH = "af_heart", "af_bella", "af_nicole"
POSES["handin"] = dict(la=(-20, -10), ra=(60, 40), ll=(-10, -5), rl=(10, 5), lean=0, tilt=0)        # Noah: right hand up to hers
POSES["handin_l"] = dict(la=(-30, -10), ra=(20, 10), ll=(-10, -5), rl=(10, 5), lean=0, tilt=0)     # Maya: left hand down to his

V = Story("door2", tapes=[("For the first time since 3:12", "They were still there.", "cut"),
                          ("Halfway down, Noah's foot", "We didn't move.", "cut"),
                          ("Then the voice upstairs said it too.", "Next: episode three", "cut")],
          swells=[("Then the voice upstairs said it too.", "And the hand in mine", 0.35)],
          dips=[("Next: episode three", None, 0.5)],
          hush=[("We walked in our socks", "Halfway down"), ("Noah's voice. Crying.", "Then the voice upstairs")],
          say={"3:12": "three twelve", "7:06": "seven oh six"}, beat_groups=("st4",), seed=22)
L = V.L
DOOR = dict(voice=MOM, fx="door", speed=0.86, who="MOM'S VOICE")
WHISPER = dict(gain=-3, fx="whisper", who="MAYA")
UPSTAIRS = dict(voice=NOAH, fx="child_far2", gain=-8, speed=0.9, who="UPSTAIRS (NOAH'S VOICE)")

L("k0", "I lay down on the floor, with my mouth right at the gap under the door. And I asked the one thing only Mom would know.")
L("k0", '"Mom... what did Dad use to call me?"', after=1.4, **WHISPER)
L("k0", "For a long time, nothing.")
L("k0", '"Mom... what did Dad use to call me?"', voice=NARR, fx="self_door", who="THE DOOR (MAYA'S VOICE)")
L("k0", "My own voice. My own question. Coming back from under the door.")
L("r0", "Let me back up.")
L("r0", "At 3:12 a.m., every phone in the city said: don't open your door.")
L("r0", "Then something with my mom's voice knocked all night. My little brother Noah and I learned the rule: it only repeats what it hears.")
L("r0", "Then, at 7:06, a text from Mom's phone. And from under the door, a sentence nobody had ever said.")
L("r0", '"I\'m down here, sweetheart. Why won\'t you open?"', after=0.6, **DOOR)
L("c1", "Don't Open the Door. Episode two: the hallway.")
L("a3", "It hadn't invented anything.")
L("a3", "Mom never calls me sweetheart. But Mister Duval says it to his wife every night, through my ceiling.")
L("a3", "And why won't you open, is what the man next door yells at his son.")
L("a3", "It wasn't talking. It was cutting and pasting. It had been listening to the whole building.", after=0.3)
L("a4", "At nine, my phone buzzed. Unknown number.")
L("a4", '"Maya, it\'s Mom. Lost my phone. At the hospital. Safe."', voice=MOM, speed=0.9, who="MOM (TEXT)")
L("a4b", "I called the number back. A nurse answered, and put her on.")
L("a4b", '"Bean? It\'s me. Bring Noah, and get out of that building. Now."', voice=MOM, fx="phone", speed=0.92, who="MOM (PHONE)")
L("a4b", "Bean. Dad's name for me. The thing at the door never knew it.")
L("a4b", "But knockers don't type. So who had sent the text at 7:06?", after=0.4)
L("a5", '"Maya, I\'m thirsty."', voice=NOAH, fx="child", gain=-2, who="NOAH")
L("a5", "The tap had gone dry an hour before. Mom said go. So we went.")
L("a6", "For the first time since 3:12, I opened the door.", after=1.0)
L("a6b", "The mat outside was empty. Just a wet smear, where something had lain all morning.", after=0.6)
L("h1", "They were still there.")
L("h1", "The baker, at number four. Mister Duval, at number six, still in his slippers. Facing the doors. Not moving.")
L("h2", "We walked in our socks. Slowly. Noah held my hand so hard it hurt.")
L("h3", "Halfway down, Noah's foot hit an empty bottle.", after=1.7)
L("h3", "I let go of his hand to stop it. One second. Then I grabbed it again.")
L("h4", "The baker's head turned. Slowly. All the way round.")
L("h4", "He didn't look at us. He listened.")
L("h5", '"Maya? Is that Mom?"', voice=NOAH, fx="child_hall", gain=-2, who="THE BAKER (NOAH'S VOICE)")
L("h5", "Noah's words. Noah's voice. Out of a grown man's mouth.")
L("h6", "We didn't move. After a very long time, his head turned back to the door.")
L("st1", "At the stairs down, we heard it. From upstairs. From Mister Duval's open flat.")
L("st1", '"Maya? Help me! Maya, please!"', **UPSTAIRS)
L("st2", "Noah's voice. Crying.")
L("st2", "But Noah was right here. His hand was shaking in mine.")
L("st3", '"That\'s not me."', voice=NOAH, fx="child", gain=-2, who="NOAH")
L("st3", '"I know."', after=0.3, **WHISPER)
L("st4", "Then the voice upstairs said it too.")
L("st4", '"Maya! That\'s not me!"', after=0.8, **UPSTAIRS)
L("st4", "And the hand in mine stopped shaking.", after=2.8)
L("end", "Next: episode three, the street. Subscribe, so you don't miss it. And whatever happens... don't let go.")


# --------------------------------------------------------------------------- props
FLOOR = 900
DOORS = {3: 160, 4: 640, 5: 1120, 6: 1600}
KS = 1.35                          # the knockers' scale on the landing
KID_Y = 1075                       # the kids stand nearer to us than the knockers: lower in frame, bigger


def fit(text, x, size, xmax=1830):
    """The biggest size up to `size` at which the longest line, written from x, stays left of xmax."""
    return min(size, (xmax - x) / max(text_w(ln, 1) for ln in text.split("\n")))


def face_ops(x, y, s, phase, hair="chef", skin=KSKIN):
    """The head of a knocker seen from behind, turning towards us: phase 1/3 shows one eye at the edge, 2/3 two eyes
    to the side, 1 the full face. Same head, same hat."""
    hx, hy, R = x + 6 * s, y - 285 * s, 40 * s
    o = [Fl(P_ell(hx, hy, R, R * 1.03, 1, closed=True), skin), stk(P_ell(hx, hy, R, R * 1.03, 2, 0.08), 7.5 * s)]
    off = {1 / 3: (0.62, None), 2 / 3: (0.12, 0.6), 1.0: (-0.33, 0.33)}[phase]
    for k, ex in enumerate(e for e in off if e is not None):
        o.append(stk(P_ell(hx + ex * R, hy - 0.08 * R, 0.2 * R, 0.25 * R, 5 + k, 0.08), 3.8 * s))
    if phase == 1.0:
        o.append(stk(P_line(hx - 0.16 * R, hy + 0.42 * R, hx + 0.18 * R, hy + 0.4 * R, 0, 3), 4.5 * s))
    if hair == "chef":
        o += [Fl(P_rect(hx - 34 * s, hy - R - 66 * s, 68 * s, 76 * s, 0, r=18 * s), WHITE), stk(P_rect(hx - 34 * s, hy - R - 66 * s, 68 * s, 76 * s, 4 * s, r=18 * s), 5 * s),
              stk(P_line(hx - 34 * s, hy - R + 2 * s, hx + 34 * s, hy - R + 2 * s, 0.02, 4), 5 * s)]
    return o


def back_marks(x, y, s, who):
    """What tells you a stick figure has its back to you: the baker's apron strings tied in a bow, the seam down the back
    of Duval's coat."""
    if who == "baker":
        wy = y - 124 * s
        return [stk(P_ell(x - 16 * s, wy - 4 * s, 15 * s, 9 * s, 1, 0.06), 4.5 * s, WHITE), stk(P_ell(x + 16 * s, wy - 4 * s, 15 * s, 9 * s, 2, 0.06), 4.5 * s, WHITE),
                stk(P_line(x - 2 * s, wy, x - 12 * s, wy + 40 * s, 0.02, 3), 4.5 * s, WHITE), stk(P_line(x + 2 * s, wy, x + 13 * s, wy + 42 * s, 0.02, 4), 4.5 * s, WHITE)]
    return [stk(P_line(x, y - 228 * s, x + 2 * s, y - 94 * s, 0.01, 5), 4 * s, (90, 80, 70))]


def landing(S, upto=6):
    """The landing seen side-on, the same in every hallway scene: back wall, floor, numbered doors, Maya's own (3) open."""
    S.noframe = True
    S.draw([stk(P_line(0, FLOOR, 1920, FLOOR + 3, 0.003, 1), 7), stk(P_line(0, 180, 1920, 182, 0.003, 2), 5, GREY)], 0.0, 0.0, snd=None)
    for n, x in DOORS.items():
        if n > upto:
            continue
        col = NIGHT if n == 3 else ((130, 150, 120), (176, 150, 196), (110, 120, 150))[n - 4]
        S.draw([Fl(P_rect(x - 110, FLOOR - 540, 220, 540, 0), col), stk(P_rect(x - 110, FLOOR - 540, 220, 540, 5), 6),
                ("g", str(n), x, FLOOR - 566, 68, INK, DIGIT, "m")], 0.0, 0.0, snd=None)
        if n != 3:
            S.draw([("dot", x + 70, FLOOR - 270, 8, HL)], 0.0, 0.0, snd=None)


def knockers(S, turn=None, back=None):
    """The baker at 4 and Duval at 6, backs to us. turn: when the baker's head starts turning round (3 steps, 0.3 s apart);
    back: when it turns away again."""
    bx, dx = DOORS[4], DOORS[6]
    S.add(Dr(back_fig(bx, FLOOR - 10, KS, hair="chef") + back_marks(bx, FLOOR - 10, KS, "baker"), 0.0, 0.0, seed=4))
    S.add(Dr(back_fig(dx, FLOOR - 10, KS, hair="bald", coat=(150, 130, 110), slippers=True) + back_marks(dx, FLOOR - 10, KS, "duval"), 0.0, 0.0, seed=5))
    if turn is not None:
        steps = (1 / 3, 2 / 3, 1.0)
        for k, ph in enumerate(steps):
            t_on = turn + 0.3 * k
            t_off = (turn + 0.3 * (k + 1) - EXIT) if k < 2 else ((back - EXIT) if back else None)
            S.add(Dr(face_ops(bx, FLOOR - 10, KS, ph), t_on, 0.0, seed=6 + k, until=t_off))


def kids(S, x, clasp=True, let_go=None, grab=None, maya_mood="worried", noah_mood="worried"):
    """Maya and Noah, hand in hand (their hands meet: a small clasp drawn where they join)."""
    S.add(Fig(x - 150, KID_Y, 1.1, poses=[("handin", 0)], moods=[(noah_mood, 0)], kind="spiky", seed=12, enter="none", idle=0.4))
    S.add(Fig(x, KID_Y, 1.55, poses=[("handin_l", 0)], moods=[(maya_mood, 0)], kind="bob", seed=13, enter="none", idle=0.4))
    if clasp:
        ops = [Fl(P_ell(x - 58, 894, 24, 20, 1, closed=True), (236, 228, 214)), stk(P_ell(x - 58, 894, 24, 20, 2, 0.06), 6)]
        if let_go is None:
            S.add(Dr(ops, 0.0, 0.0, seed=14))
        else:
            S.add(Dr(ops, 0.0, 0.0, seed=14, until=let_go - EXIT))
            S.add(Dr(ops, grab, 0.0, seed=15))


def tremble(until=None):
    """A small hand shaking: stepped jitter, stopping dead at `until`."""
    def mv(u):
        if until is not None and u >= until:
            return (0.0, 0.0, 0.0, 1.0)
        q = math.floor(u * 15) / 15
        return (3.5 * math.sin(q * 61) + 2 * math.sin(q * 37), 3 * math.sin(q * 53 + 1), 0.0, 1.0)
    return mv


def hands(S, at=0.0, still=None, shaking=True):
    """Close-up: Noah's small hand (left) held in Maya's (right), her fingers wrapped over his; his shakes until `still`."""
    S.draw([stk(P_bez((0, 800), (300, 720), (600, 650), (820, 590)), 22), stk(P_bez((1920, 760), (1550, 690), (1300, 610), (1130, 560)), 30)], at, 0.4, snd=None)
    noah = [Fl(P_rect(800, 520, 190, 120, 0, r=50), (240, 236, 228)), stk(P_rect(800, 520, 190, 120, 6, r=50), 8)]
    noah += [op for k in range(4) for op in (Fl(P_ell(990, 535 + k * 28, 34, 13, k, closed=True), (240, 236, 228)), stk(P_ell(990, 535 + k * 28, 34, 13, k + 9, 0.06), 6))]
    maya = [Fl(P_rect(960, 440, 200, 240, 0, r=70), (236, 228, 214)), stk(P_rect(960, 440, 200, 240, 6, r=70), 10)]
    maya += [op for k in range(4) for op in (Fl(P_ell(935 + k * 6, 480 + k * 50, 50, 22, k + 20, closed=True), (236, 228, 214)),
                                             stk(P_ell(935 + k * 6, 480 + k * 50, 50, 22, k + 30, 0.06), 7))]
    mv = tremble(None if still is None else still - at) if shaking else None
    S.add(Dr(noah + maya, at + 0.15, 0.4, seed=S.rng.randint(1, 999), move=mv, anchor=(960, 560)))


def stairs(S, at=0.0):
    """The stairwell: a flight down to the right (the way out), a flight up to the left, to Duval's open, dark flat."""
    S.noframe = True
    down = [(960, 560)]
    for k in range(5):
        x, y = 960 + k * 150, 560 + k * 90
        down += [(x + 150, y), (x + 150, y + 90)]
    up = [(820, 560)]
    for k in range(4):
        x, y = 820 - k * 140, 560 - k * 95
        up += [(x - 140, y), (x - 140, y - 95)]
    S.draw([stk(P_poly(down), 10), stk(P_poly(up), 10), stk(P_line(820, 560, 960, 560, 0.0, 3), 10)], at, 0.4, snd=None)
    S.draw([Fl(P_rect(130, 0, 220, 186, 0), NIGHT), stk(P_rect(130, 0, 220, 186, 6), 7)], at + 0.1, 0.3, snd=None)
    S.text("down: the way out", 1240, 470, 64, INK, at=at + 0.3, rot=2)
    S.text("Duval's flat", 380, 110, 74, INK, at=at + 0.3)


# --------------------------------------------------------------------------- cold open: the test
@V.scene("k0")
def _(S):
    S.noframe = True
    S.add(black(0.35))
    S.draw(door(520, 1040, 1.1), 0.0, 0.0, snd=None)
    S.add(Fig(1150, 1010, 1.3, poses=[("lie", 0)], moods=[("worried", 0), ("wow", S.l(3) + 0.3)], kind="bob", rot=-90, seed=13, enter="none", idle=0.3))
    S.add(Dr([Fl(P_rect(520 - 180 * 1.1 + 8, 1040 - 14, 360 * 1.1 - 16, 14, 0), LIGHT)], S.c("gap") - 0.1, 0.0, pop=True, anchor=(520, 1033), seed=9))
    S.text("only Mom\nwould know.", 1240, 230, 92, INK, at=S.c("only") - 0.1, lh=1.1, rot=-2)
    S.text("\"what did Dad\nuse to call me?\"", 1180, 480, 84, ORANGE, at=S.l(1) + 0.1, lh=1.1, rot=-2, until=S.l(2) - 0.1)
    S.text("nothing.", 1250, 500, 110, GREY, at=S.c("nothing", 2) - 0.2, rot=-3, until=S.l(3) - 0.1)
    S.text("\"what did Dad\nuse to call me?\"", 1180, 480, 84, INK, at=S.l(3) + 0.1, lh=1.1, rot=-2)
    S.add(arrow(P_bez((720, 1030), (950, 900), (1160, 560)), S.l(3), INK, 6, 0.4, dashed=True))
    S.text("my own voice.", 1200, 760, 104, RED, at=S.c("own", 4) - 0.2, rot=-3)


# --------------------------------------------------------------------------- recap
@V.scene("r0")
def _(S):
    """Three panels left to right (the alert, the peephole, the door), a caption under each, the rule and the line on top."""
    S.noframe = True
    S.add(black(0.96))
    S.pop([Fl(P_poly([(960, 120), (900, 160), (960, 200)], True), WHITE), Fl(P_poly([(1030, 120), (970, 160), (1030, 200)], True), WHITE)],
          S.l(0), (965, 160), snd=None, until=S.l(1) - 0.2)
    S.draw(ph_screen(290, 480, 1.75), S.c("3:12", 1) - 0.2, 0.0, snd=None)
    S.add(screen_lines(290, 430, 260, "DO NOT\nOPEN YOUR\nDOOR.", 80, INK, at=S.c("3:12", 1), cps=60))
    S.text("3:12", 190, 860, 96, WHITE, at=S.c("3:12", 1) - 0.1, rot=-3)
    cx, cy, r = 840, 480, 220
    ms = 1.7
    t_k = S.c("knocked", 2) - 0.3
    S.add(clip_ell(group(*hallway(cx, cy, r), Fig(cx, cy + 285 * ms, ms, at=t_k, poses=[("stand", 0)], moods=[("stare", 0)], kind="long", seed=21,
                                                     enter="pop", idle=0.0)), cx, cy, r, r))
    peep_ring(S, cx, cy, r, t_k - 0.1)
    S.text("+ Noah, 8", 690, 860, 80, WHITE, at=S.c("noah", 2) - 0.1, rot=-2)
    S.text("it only repeats what it hears.", 470, 150, fit("it only repeats what it hears.", 470, 64, 1250), ORANGE, at=S.c("rule", 2), rot=-1)
    S.draw(door(1500, 760, 0.62), S.c("door", 3) - 0.2, 0.3, snd=None)
    S.text("7:06: a text\nfrom Mom's phone", 1200, 790, fit("7:06: a text\nfrom Mom's phone", 1200, 68, 1800), WHITE, at=S.c("7:06", 3) - 0.1, lh=1.05, rot=-1)
    S.text("\"I'm down here.\"", 1330, 150, fit("\"I'm down here.\"", 1330, 80), RED, at=S.l(4) + 0.1, rot=-3)


@V.scene("c1")
def _(S):
    S.noframe = True
    S.add(black(0.97))
    S.text("DON'T OPEN", 150, 380, 210, WHITE, at=S.c("don't") - 0.05, rot=-3, cps=30)
    S.text("THE DOOR.", 190, 600, 210, RED, at=S.c("door") - 0.1, rot=-3, cps=30)
    S.text("episode 2: the hallway", 200, 800, 92, DIM, at=S.c("episode") - 0.05, rot=-2)
    S.draw([Fl(P_rect(1460, 230, 250, 560, 0), NIGHT), stk(P_rect(1460, 230, 250, 560, 6), 7, WHITE),
            Fl(P_poly([(1710, 230), (1800, 190), (1800, 830), (1710, 790)], True), WOOD), stk(P_poly([(1710, 230), (1800, 190), (1800, 830), (1710, 790)], True), 6, WHITE)],
           0.1, 0.5, snd=None)


# --------------------------------------------------------------------------- how it talks: cut and paste
def scrap(x, y, text, size, col, rot, at):
    w = text_w(text, size) + 50
    h = size * 1.25
    a = math.radians(rot)
    corners = [(x + dx * math.cos(a) - dy * math.sin(a), y + dx * math.sin(a) + dy * math.cos(a)) for dx, dy in ((-20, -h * 0.85), (w - 20, -h * 0.85), (w - 20, h * 0.4), (-20, h * 0.4))]
    return [Dr([Fl(P_poly(corners, True), col), stk(P_poly(corners, True), 4)], at, 0.0, pop=True, anchor=(x + w / 2, y), seed=int(x + y)),
            T(text, x + 5, y, size, INK, at=at + 0.05, cps=200, rot=rot)]


@V.scene("a3")
def _(S):
    x0, y0, fw, fh = 140, 160, 250, 210
    for r_ in range(3):
        for c_ in range(3):
            x, y = x0 + c_ * fw, y0 + r_ * fh
            mine = (r_, c_) == (1, 1)
            S.draw([Fl(P_rect(x, y, fw, fh, 0), (250, 236, 200) if mine else (236, 232, 222)), stk(P_rect(x, y, fw, fh, 4), 6)], 0.04 * (r_ * 3 + c_), 0.2, snd=None)
    mx, my = x0 + fw * 1.5, y0 + fh * 2
    S.draw([Fl(P_rect(mx - 30, my - 120, 60, 112, 0), WOOD), stk(P_rect(mx - 30, my - 120, 60, 112, 3), 4)], 0.3, 0.2, snd=None)
    S.text("our door", mx, my + 70, 66, ORANGE, at=0.4, anchor="m")
    # upstairs: Duval and his wife; next door: a man and his son
    S.add(Fig(x0 + fw * 1.5 - 40, y0 + fh - 8, 0.48, at=S.c("duval", 1) - 0.4, poses=[("stand", 0)], moods=[("smile", 0)], kind="old", seed=40, enter="pop"))
    S.add(Fig(x0 + fw * 1.5 + 40, y0 + fh - 8, 0.45, at=S.c("duval", 1) - 0.3, poses=[("stand", 0)], moods=[("smile", 0)], kind="long", seed=41, enter="pop"))
    S.add(Fig(x0 + fw * 2.5 - 40, y0 + 2 * fh - 8, 0.48, at=S.c("man", 2) - 0.3, poses=[("hips", 0)], moods=[("angry", 0)], kind="spiky", seed=42, enter="pop"))
    S.add(Fig(x0 + fw * 2.5 + 50, y0 + 2 * fh - 8, 0.36, at=S.c("son", 2) - 0.3, poses=[("stand", 0)], moods=[("sad", 0)], kind="bob", seed=43, enter="pop"))
    S.add(arrow(P_bez((x0 + fw * 1.5, y0 + fh * 0.6), (x0 + fw * 1.2, y0 + fh * 1.2), (mx - 20, my - 130)), S.c("ceiling", 1) - 0.2, RED, 6, 0.3, dashed=True))
    S.add(arrow(P_bez((x0 + fw * 2.2, y0 + fh * 1.6), (x0 + fw * 1.9, y0 + fh * 1.8), (mx + 36, my - 60)), S.c("yells", 2), RED, 6, 0.3, dashed=True))
    # the note it made
    S.draw([Fl(P_poly([(1000, 170), (1810, 140), (1830, 760), (1020, 790)], True), (246, 244, 236)), stk(P_poly([(1000, 170), (1810, 140), (1830, 760), (1020, 790)], True), 6)],
           S.c("invented") - 0.3, 0.3, snd=None)
    for fn in (scrap(1060, 300, "I'm", 84, HL, -4, S.c("invented") + 0.1) + scrap(1260, 300, "down here,", 84, COAT, 3, S.c("invented") + 0.4)
               + scrap(1080, 470, "sweetheart.", 96, PINK, -3, S.c("sweetheart", 1) - 0.1)
               + scrap(1060, 650, "why won't", 80, (214, 226, 196), 2, S.c("why", 2) - 0.1) + scrap(1450, 650, "you open?", 80, WHITE, -5, S.c("open", 2) - 0.1)):
        S.add(fn)
    S.text("cut & paste.", 1180, 900 - 40, 96, RED, at=S.c("cutting", 3) - 0.1, rot=-3)


# --------------------------------------------------------------------------- Mom
@V.scene("a4")
def _(S):
    px, py, ps = 680, 540, 2.75
    S.draw(ph_screen(px, py, ps), 0.0, 0.3, snd=None)
    S.add(snd="buzz", at=S.c("buzzed") - 0.1)
    S.add(screen_lines(px, py - 155 * ps + 160, 260, "9:00", 72, INK, at=S.c("nine") - 0.1))
    S.add(screen_lines(px, py - 190, 300, "unknown", 70, INK, at=S.c("unknown") - 0.1))
    S.draw([Fl(P_rect(px - 195, py - 120, 390, 420, 0, r=30), (226, 219, 205)), stk(P_rect(px - 195, py - 120, 390, 420, 5, r=30), 6)], S.l(1) - 0.3, 0.3, snd=None)
    S.add(screen_lines(px, py - 40, 370, "It's Mom.\nLost my phone.\nAt the hospital.\nSafe.", 70, INK, at=S.l(1) + 0.05, cps=30))
    S.text("unknown number.", 1120, 330, fit("unknown number.", 1120, 92), INK, at=S.c("unknown") + 0.2, rot=-2)
    S.text("is it her?", 1220, 560, 110, RED, at=S.l(1) + 1.5, rot=-3)


@V.scene("a4b")
def _(S):
    px, py, ps = 600, 540, 2.75
    S.draw(ph_screen(px, py, ps), 0.0, 0.0, snd=None)
    S.add(screen_lines(px, py - 250, 300, "calling...", 70, INK, at=S.c("called") - 0.1, until=S.l(1) - 0.1))
    S.add(screen_lines(px, py - 250, 380, "nurse's phone", 66, INK, at=S.l(1) - 0.05))
    for k in range(7):
        hgt = (60, 130, 90, 170, 110, 70, 140)[k]
        S.draw([Fl(P_rect(px - 160 + k * 46, py + 60 - hgt / 2, 26, hgt, 0, r=10), COAT)], S.l(1) + 0.08 * k, 0.1, snd=None)
    S.text("Bean.", 1150, 360, 200, ORANGE, at=S.c("bean", 2) - 0.1, rot=-4)
    S.text("the door never knew.", 1060, 520, fit("the door never knew.", 1060, 80), INK, at=S.c("never", 2) - 0.2, rot=-2)
    S.text("knockers don't type.", 1040, 720, fit("knockers don't type.", 1040, 92), RED, at=S.c("type", 3) - 0.3, rot=-3)
    S.text("so who sent 7:06?", 1060, 850, fit("so who sent 7:06?", 1060, 76), INK, at=S.c("7:06", 3) - 0.3, rot=-2)


@V.scene("a5")
def _(S):
    S.draw([Fl(P_rect(200, 620, 680, 200, 0, r=20), (196, 196, 194)), stk(P_rect(200, 620, 680, 200, 8, r=20), 9),
            stk(P_poly([(540, 620), (540, 410), (720, 410), (720, 470)]), 26)], 0.0, 0.3, snd=None)
    S.add(Fig(1060, 920, 0.95, poses=[("stand", 0)], moods=[("sad", 0)], kind="spiky", seed=12, enter="none"))
    S.text("\"Maya, I'm thirsty.\"", 900, 330, 90, INK, at=S.l(0) + 0.05, rot=-2)
    S.text("dry.", 820, 470, 110, RED, at=S.c("dry", 1) - 0.1, rot=-3)
    hx, hy = 1640, 520
    S.draw([Fl(P_rect(hx - 130, hy - 70, 260, 140, 0, r=8), WHITE), stk(P_rect(hx - 130, hy - 70, 260, 140, 5, r=8), 6),
            Fl(P_rect(hx - 14, hy - 46, 28, 92, 0), RED), Fl(P_rect(hx - 46, hy - 14, 92, 28, 0), RED)], S.c("mom", 1) - 0.3, 0.4, snd=None)
    S.text("so we went.", 1300, 760, 100, RED, at=S.c("went", 1) - 0.3, rot=-2)


@V.scene("a6")
def _(S):
    S.noframe = True
    S.add(black(0.5))
    x, y, s = 760, 1040, 1.12
    t_open = S.c("opened") - 0.1
    S.add(Dr(door(x, y, s), 0.0, 0.0, seed=7, until=t_open - EXIT))
    w, h = 360 * s, 800 * s
    x0, y0 = x - w / 2, y - h
    S.add(Dr([Fl(P_rect(x0 - 30 * s, y0 - 30 * s, w + 60 * s, h + 30 * s, 0), (226, 219, 205)), stk(P_rect(x0 - 30 * s, y0 - 30 * s, w + 60 * s, h + 30 * s, 6 * s), 6 * s),
              Fl(P_rect(x0, y0, w, h, 0), LIGHT), stk(P_rect(x0, y0, w, h, 6 * s), 7 * s),
              Fl(P_poly([(x0, y0), (x0 - 150, y0 - 60), (x0 - 150, y + 60), (x0, y)], True), WOOD), stk(P_poly([(x0, y0), (x0 - 150, y0 - 60), (x0 - 150, y + 60), (x0, y)], True), 7)],
             t_open, 0.0, seed=8))
    S.text("3:12", 1230, 330, 150, DIM, at=S.c("3:12") - 0.2, rot=-3)
    S.add(strike(1210, 300, 1500, 280, S.c("3:12") + 0.4, RED, 9))
    S.text("open.", 1240, 620, 160, RED, at=t_open + 0.1, rot=-3)


@V.scene("a6b")
def _(S):
    S.noframe = True
    S.add(black(0.55))
    S.draw([stk(P_line(0, 820, 1920, 822, 0.003, 1), 7, (150, 146, 140))], 0.0, 0.0, snd=None)
    mat = [(560, 800), (1360, 800), (1440, 900), (480, 900)]
    S.draw([Fl(P_poly(mat, True), (150, 120, 86)), stk(P_poly(mat, True), 7)], 0.0, 0.3, snd=None)
    S.text("empty.", 760, 500, 150, WHITE, at=S.c("empty") - 0.2, rot=-3)
    smear = P_bez((700, 860), (820, 820), (1060, 880), (1240, 840))
    S.draw([stk(smear, 34, (70, 74, 70)), stk(P_bez((760, 870), (900, 850), (1000, 880), (1120, 862)), 18, (90, 96, 88))], S.c("smear") - 0.2, 0.6, snd=None)
    S.text("a wet smear.", 1080, 690, 92, DIM, at=S.c("smear") + 0.1, rot=-2)
    S.text("all morning.", 300, 690, 80, RED, at=S.c("morning") - 0.3, rot=-2)


# --------------------------------------------------------------------------- the landing
@V.scene("h1")
def _(S):
    landing(S)
    knockers(S)
    kids(S, 520)
    S.text("still there.", 200, 140, 90, RED, at=S.c("still") - 0.2, rot=-2)
    S.text("the baker", 760, 140, 84, INK, at=S.c("baker", 1) - 0.1, rot=-2)
    S.text("Mr. Duval", DOORS[6] - 140, 140, 84, INK, at=S.c("duval", 1) - 0.1, rot=-2)
    S.text("slippers.", DOORS[6] - 120, 250, 76, INK, at=S.c("slippers", 1) - 0.1, rot=-2)


@V.scene("h2")
def _(S):
    landing(S)
    knockers(S)
    kids(S, 980)
    S.text("socks.", 280, 140, 100, INK, at=S.c("socks") - 0.2, rot=-2)
    S.text("slowly.", 760, 140, 100, INK, at=S.c("slowly") - 0.2, rot=-2)
    S.text("so hard it hurt.", 1230, 140, 84, RED, at=S.c("hurt") - 0.4, rot=-2)


@V.scene("h3")
def _(S):
    landing(S)
    knockers(S)
    t_hit = S.e(0) + 0.15
    kids(S, 980, let_go=S.c("let", 1), grab=S.c("grabbed", 1))
    roll = lambda u: (230 * ease_out(min(1.0, u / 1.2)), 0.0, 0.07 * math.sin(u * 22) * max(0.0, 1 - u / 1.2), 1.0)
    bottle = [Fl(P_rect(870, 1046, 90, 32, 0, r=14), (150, 186, 214)), stk(P_rect(870, 1046, 90, 32, 4, r=14), 5),
              Fl(P_rect(960, 1053, 34, 18, 0, r=6), (150, 186, 214)), stk(P_rect(960, 1053, 34, 18, 3, r=6), 4)]
    S.add(Dr(bottle, 0.0, 0.0, seed=9, move=lambda u: roll(max(0.0, u - t_hit)), anchor=(915, 1062)))
    S.add(snd="clink", at=t_hit)
    S.text("clink.", 1240, 640, 110, RED, at=t_hit + 0.05, rot=8)
    S.text("one second.", 1180, 140, 100, RED, at=S.c("second", 1) - 0.3, rot=-2)


@V.scene("h4")
def _(S):
    landing(S)
    knockers(S, turn=S.c("turned") - 0.1)
    kids(S, 980, maya_mood="wow", noah_mood="wow")
    S.text("all the way round.", 220, 140, 92, RED, at=S.c("round") - 0.4, rot=-2)
    S.text("listening.", 1250, 140, 100, INK, at=S.c("listened", 1) - 0.3, rot=-2)


@V.scene("h5")
def _(S):
    """Close on the baker: the back of his body, his face turned all the way round, the apron bow still behind."""
    S.noframe = True
    S.add(black(0.4))
    bx, by, bs = 700, 1500, 3.6
    S.draw([Fl(P_rect(bx - 380, 0, 760, 1080, 0), (130, 150, 120)), stk(P_rect(bx - 380, 0, 760, 1080, 6), 7)], 0.0, 0.0, snd=None)
    S.add(Dr(back_fig(bx, by, bs, hair=None) + face_ops(bx, by, bs, 1.0), 0.0, 0.0, seed=4))
    S.text("\"Maya?\nIs that Mom?\"", 1180, 300, 104, INK, at=S.l(0) + 0.05, lh=1.1, rot=-2)
    S.text("Noah's voice.", 1180, 640, 110, RED, at=S.c("voice", 1) - 0.3, rot=-3)
    S.text("a grown man's mouth.", 1150, 800, fit("a grown man's mouth.", 1150, 76), INK, at=S.c("mouth", 1) - 0.4, rot=-2)


@V.scene("h6")
def _(S):
    landing(S)
    t0 = S.c("back") - 0.2
    knockers(S, turn=-1.0, back=t0)
    kids(S, 980)
    S.text("don't move.", 260, 140, 100, INK, at=S.c("move") - 0.2, rot=-2)
    S.text("a very long time.", 1100, 140, 92, GREY, at=S.c("long") - 0.3, rot=-2)


# --------------------------------------------------------------------------- the stairs
@V.scene("st1")
def _(S):
    stairs(S)
    S.add(Fig(1060, 560, 1.15, poses=[("handin_l", 0)], moods=[("worried", 0), ("wow", S.l(1))], kind="bob", seed=13, enter="none"))
    S.add(Fig(940, 560, 0.82, poses=[("handin", 0)], moods=[("worried", 0), ("wow", S.l(1))], kind="spiky", seed=12, enter="none"))
    S.text("upstairs.", 90, 340, 90, INK, at=S.c("upstairs") - 0.2, rot=-3)
    S.text("\"Maya? Help me!\"", 1180, 250, fit("\"Maya? Help me!\"", 1180, 104), RED, at=S.l(1) + 0.05, rot=-3)
    S.add(arrow(P_bez((360, 175), (800, 210), (1170, 230)), S.l(1) + 0.2, RED, 6, 0.4, dashed=True))


@V.scene("st2")
def _(S):
    hands(S)
    S.text("Noah's voice.", 200, 230, 100, RED, at=S.c("voice") - 0.3, rot=-3)
    S.text("crying.", 260, 360, 90, INK, at=S.c("crying") - 0.2, rot=-3)
    S.text("shaking.", 1300, 260, 110, INK, at=S.c("shaking", 1) - 0.3, rot=-2)


@V.scene("st3")
def _(S):
    hands(S, at=-1.0)
    S.text("\"that's not me.\"", 160, 300, 96, INK, at=S.l(0) + 0.05, rot=-3)
    S.text("\"I know.\"", 1340, 300, 110, ORANGE, at=S.l(1) + 0.05, rot=-3)


@V.scene("st4")
def _(S):
    S.noframe = True
    S.add(black(0.9))
    S.draw([Fl(P_rect(130, 0, 220, 186, 0), (12, 12, 14)), stk(P_rect(130, 0, 220, 186, 6), 7, (120, 116, 112))], 0.0, 0.0, snd=None)
    S.text("\"Maya!\nThat's not me!\"", 480, 260, 110, RED, at=S.l(1) + 0.05, lh=1.1, rot=-3, until=S.l(2) - 0.3)
    t_h = S.l(1) + 0.9
    S.add(black(0.97, at=t_h))
    hands(S, at=t_h, still=S.c("stopped", 2) - 0.1)
    S.text("stopped shaking.", 1100, 830, fit("stopped shaking.", 1100, 96), WHITE, at=S.c("stopped", 2) - 0.1, rot=-2)
    S.add(black(1.0, at=S.e(2) + 0.35))                 # hard cut to black, and silence


@V.scene("end")
def _(S):
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
    S.text("episode 3:\nthe street.", vx, vy - 10, 84, WHITE, at=t0 + 0.5, anchor="m")
    S.text("don't let go.", 640, 860, 90, RED, at=S.c("go") - 0.3, rot=-2)
    S.add(snd="knock1", at=S.dur - 2.4)


if __name__ == "__main__":
    V.main()
