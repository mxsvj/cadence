"""DON'T OPEN THE DOOR - episode 2: the hallway. Picks up on episode 1's last line ("I'm down here, sweetheart").
Maya tests the voice; it answers with her own voice: it does not talk, it listens (to the whole building) and stitches.
Mom texts from a nurse's phone: hers is gone (so who texted at 7:06?). The tap runs dry; they open the door for the first
time and cross the landing past the baker and Mister Duval. A bottle rolls, the baker's head turns all the way round and
says Noah's line in Noah's voice. At the stairs, Noah's voice cries from Duval's open flat upstairs; the real Noah
whispers "That's not me", and the voice upstairs uses it: "He's not me." The hand in Maya's goes still.
Voices as in episode 1; the voice copying Maya is af_heart through the door, the baker and the flat upstairs are Noah's."""
from story_video import *  # noqa: F401,F403
from doodle_video import stk
from doodle import POSES, clip_ell
from build_door1 import (COAT, DIM, KSKIN, LIGHT, NIGHT, WHITE, WOOD, back_fig, black, bubble_text, door, group, hallway,
                         knocks, lever_op, peep_ring, ph_screen, screen_lines)

NARR, MOM, NOAH = "af_heart", "af_bella", "af_nicole"
POSES["kneel"] = dict(la=(55, 95), ra=(70, 110), ll=(95, 0), rl=(100, 4), lean=38, tilt=24)
POSES["handin"] = dict(la=(-20, -10), ra=(35, 20), ll=(-10, -5), rl=(10, 5), lean=0, tilt=0)
POSES["handin_l"] = dict(la=(-35, -20), ra=(20, 10), ll=(-10, -5), rl=(10, 5), lean=0, tilt=0)

V = Story("door2", tapes=[("For the first time since 3:12", "The hallway was full.", "cut"),
                          ("Halfway down, Noah's foot", "We didn't move.", "cut"),
                          ("Then the voice upstairs said", "Next: episode three", "cut")],
          swells=[("Then the voice upstairs said", "And the hand in mine", 0.35)],
          dips=[("Next: episode three", None, 0.5)],
          hush=[("We walked in our socks", "Halfway down")],
          say={"3:12": "three twelve", "7:06": "seven oh six"}, beat_groups=("st4",), seed=22)
L = V.L
DOOR = dict(voice=MOM, fx="door", speed=0.86, who="MOM'S VOICE")
WHISPER = dict(gain=-3, fx="whisper", who="MAYA")
COPY_NOAH = dict(voice=NOAH, gain=-2)

L("r0", "Previously. At 3:12 a.m., every phone in the city said the same thing: don't open your door.")
L("r0", "Something with my mom's voice knocked all night. And at dawn, from right behind the door, it spoke.")
L("r0", '"I\'m down here, sweetheart. Why won\'t you open?"', after=0.8, **DOOR)
L("c1", "Don't Open the Door. Episode two: the hallway.")
L("a1", "I knelt down, with my mouth right next to the gap under the door.")
L("a1", "And I asked the one thing only Mom would know.")
L("a1", '"Mom... what did Dad use to call me?"', after=1.4, **WHISPER)
L("a2", "For a long time, nothing.")
L("a2", '"Mom... what did Dad use to call me?"', voice=NARR, fx="self_door", who="THE VOICE")
L("a2", "My own voice. My own question. Coming back from under the door.")
L("a3", "That's how it had said something new.")
L("a3", "Through the walls, it had heard everyone. The family next door. The man upstairs. Every question, every name.")
L("a3", "It hadn't learned to talk. It had learned to listen.", after=0.4)
L("a4", "At nine, my phone buzzed. Unknown number.")
L("a4", '"Maya, it\'s Mom. I lost my phone last night. I\'m at the hospital. I\'m safe."', voice=MOM, speed=0.9, who="TEXT, UNKNOWN NUMBER")
L("a4", "She had lost her phone. The phone that texted me at 7:06.")
L("a5", "Then the kitchen tap coughed, and went dry.")
L("a5", "No water, an eight-year-old, and a hospital twenty minutes away.")
L("a5", "We had to go.", after=0.3)
L("a6", "For the first time since 3:12, I opened the door.", after=1.4)
L("h1", "The hallway was full.")
L("h1", "The baker, at number four. Mister Duval from upstairs, at number six, still in his slippers. Facing the doors. Not moving.")
L("h2", "We walked in our socks. Slowly. Noah held my hand so hard it hurt.")
L("h3", "Halfway down, Noah's foot hit an empty bottle.", after=1.3)
L("h4", "The baker's head turned. Slowly. All the way round.")
L("h4", "He didn't look at us. He listened.")
L("h5", '"Maya? Is that Mom?"', fx="child_hall", who="THE BAKER", **COPY_NOAH)
L("h5", "Noah's words. Noah's voice. Out of a grown man's mouth.")
L("h6", "We didn't move. After a very long time, his head turned back to the door.")
L("st1", "We had reached the stairs when we heard it. From upstairs. From Mister Duval's open flat.")
L("st1", '"Maya? Help me! Maya, please!"', fx="child_far", who="UPSTAIRS", **COPY_NOAH)
L("st2", "Noah's voice. Crying.")
L("st2", "But Noah was right here, holding my hand.")
L("st3", '"That\'s not me."', voice=NOAH, fx="child", gain=-4, who="NOAH")
L("st3", '"I know."', **WHISPER)
L("st4", "Then the voice upstairs said something else.")
L("st4", '"Maya, don\'t go with him. He\'s not me."', fx="child_far", who="UPSTAIRS", after=0.8, **COPY_NOAH)
L("st4", "And the hand in mine went very, very still.", after=2.8)
L("end", "Next: episode three, the street. Subscribe, so you don't miss it. And whatever happens... don't let go.")


# --------------------------------------------------------------------------- props
FLOOR = 900
DOORS = {3: 160, 4: 640, 5: 1120, 6: 1600}


def front_head(x, y, s=1.0, hair="chef", skin=KSKIN):
    """A back_fig's head, turned all the way round: the same head, now with a face that looks at nothing."""
    hx, hy, R = x + 6 * s, y - 285 * s, 40 * s
    o = [Fl(P_ell(hx, hy, R, R * 1.03, 1, closed=True), skin), stk(P_ell(hx, hy, R, R * 1.03, 2, 0.08), 7.5 * s)]
    for k, ex in enumerate((hx - 0.33 * R, hx + 0.33 * R)):
        o.append(stk(P_ell(ex, hy - 0.08 * R, 0.22 * R, 0.25 * R, 5 + k, 0.08), 3.8 * s))
    o.append(stk(P_line(hx - 0.16 * R, hy + 0.42 * R, hx + 0.18 * R, hy + 0.4 * R, 0, 3), 4.5 * s))
    if hair == "chef":
        o += [Fl(P_rect(hx - 34 * s, hy - R - 66 * s, 68 * s, 76 * s, 0, r=18 * s), WHITE), stk(P_rect(hx - 34 * s, hy - R - 66 * s, 68 * s, 76 * s, 4 * s, r=18 * s), 5 * s),
              stk(P_line(hx - 34 * s, hy - R + 2 * s, hx + 34 * s, hy - R + 2 * s, 0.02, 4), 5 * s)]
    return o


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


def knockers(S, baker_turn=None, baker_back=None):
    bx, dx, s = DOORS[4], DOORS[6], 1.35
    t_turn = baker_turn if baker_turn is not None else 1e9
    S.add(Dr(back_fig(bx, FLOOR - 10, s, hair="chef"), 0.0, 0.0, seed=4))
    S.add(Dr(back_fig(dx, FLOOR - 10, s, hair="bald", coat=(150, 130, 110), slippers=True), 0.0, 0.0, seed=5))
    if baker_turn is not None:
        S.add(Dr(front_head(bx, FLOOR - 10, s), t_turn, 0.0, seed=6, until=(baker_back - EXIT) if baker_back else None))


def kids(S, x0, x1=None, t0=0.0, t1=0.0, maya_mood="worried", noah_mood="worried"):
    """Maya and Noah, hand in hand, closer to us than the knockers (bigger, lower)."""
    walk_m = (x0, x1, t0, t1) if x1 is not None else None
    walk_n = (x0 - 150, x1 - 150, t0, t1) if x1 is not None else None
    S.add(Fig(x0 - 150, 1030, 1.05, poses=[("handin", 0)], moods=[(noah_mood, 0)], kind="spiky", seed=12, enter="none", walk=walk_n))
    S.add(Fig(x0, 1030, 1.45, poses=[("handin_l", 0)], moods=[(maya_mood, 0)], kind="bob", seed=13, enter="none", walk=walk_m))


def hands(S, at=0.0, still_at=None):
    """Close-up: Noah's small hand (left) held in Maya's (right), her fingers wrapped over his."""
    S.draw([stk(P_bez((0, 800), (300, 720), (600, 650), (820, 590)), 22), stk(P_bez((1920, 760), (1550, 690), (1300, 610), (1130, 560)), 30)], at, 0.4, snd=None)
    noah = [Fl(P_rect(800, 520, 190, 120, 0, r=50), (240, 236, 228)), stk(P_rect(800, 520, 190, 120, 6, r=50), 8)]
    noah += [op for k in range(4) for op in (Fl(P_ell(990, 535 + k * 28, 34, 13, k, closed=True), (240, 236, 228)), stk(P_ell(990, 535 + k * 28, 34, 13, k + 9, 0.06), 6))]
    maya = [Fl(P_rect(960, 440, 200, 240, 0, r=70), (236, 228, 214)), stk(P_rect(960, 440, 200, 240, 6, r=70), 10)]
    maya += [op for k in range(4) for op in (Fl(P_ell(935 + k * 6, 480 + k * 50, 50, 22, k + 20, closed=True), (236, 228, 214)),
                                             stk(P_ell(935 + k * 6, 480 + k * 50, 50, 22, k + 30, 0.06), 7))]
    S.draw(noah, at + 0.15, 0.4, snd=None)
    S.draw(maya, at + 0.3, 0.4, snd=None)


# --------------------------------------------------------------------------- previously
@V.scene("r0")
def _(S):
    S.noframe = True
    S.add(black(0.96))
    S.draw(ph_screen(340, 450, 1.9), 0.1, 0.0, snd=None)
    S.add(screen_lines(340, 400, 260, "DO NOT\nOPEN YOUR\nDOOR.", 80, INK, at=0.15, cps=400))
    S.text("3:12", 170, 860, 96, WHITE, at=S.c("3:12") - 0.1, rot=-3)
    cx, cy, r = 960, 450, 250
    ms = 1.9
    S.add(clip_ell(group(*hallway(cx, cy, r), Fig(cx, cy + 285 * ms, ms, at=S.c("knocked", 1) - 0.3, poses=[("stand", 0)], moods=[("stare", 0)],
                                                     kind="long", seed=21, enter="pop", idle=0.0)), cx, cy, r, r))
    peep_ring(S, cx, cy, r, S.c("knocked", 1) - 0.4)
    S.draw(door(1560, 760, 0.7), S.c("dawn", 1) - 0.2, 0.3, snd=None)
    S.text("\"I'm down here.\"", 1180, 860, 84, RED, at=S.l(2) + 0.1, rot=-3)


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


# --------------------------------------------------------------------------- the test
@V.scene("a1")
def _(S):
    S.draw(door(520, 1040, 1.1), 0.0, 0.3, snd=None)
    S.add(Fig(1010, 1070, 1.35, poses=[("kneel", 0)], moods=[("worried", 0)], kind="bob", seed=13, flip=True, enter="none"))
    S.add(Dr([Fl(P_rect(520 - 180 * 1.1 + 8, 1040 - 14, 360 * 1.1 - 16, 14, 0), LIGHT)], S.c("gap") - 0.1, 0.0, pop=True, anchor=(520, 1033), seed=9))
    S.text("only Mom\nwould know.", 1300, 260, 92, INK, at=S.c("only", 1) - 0.1, lh=1.1, rot=-2)
    S.text("\"what did Dad\nuse to call me?\"", 1150, 520, 88, ORANGE, at=S.l(2) + 0.1, lh=1.1, rot=-2)


@V.scene("a2")
def _(S):
    S.draw(door(520, 1040, 1.1), 0.0, 0.3, snd=None)
    S.add(Fig(1010, 1070, 1.35, poses=[("kneel", 0)], moods=[("worried", 0), ("wow", S.l(1) + 0.3)], kind="bob", seed=13, flip=True, enter="none"))
    S.text("nothing.", 1250, 250, 110, GREY, at=S.c("nothing") - 0.2, rot=-3)
    S.text("\"what did Dad\nuse to call me?\"", 1150, 470, 88, INK, at=S.l(1) + 0.1, lh=1.1, rot=-2)
    S.add(arrow(P_bez((640, 1030), (900, 900), (1120, 560)), S.l(1), INK, 6, 0.4, dashed=True))
    S.text("my own voice.", 1180, 740, 110, RED, at=S.c("own", 2) - 0.2, rot=-3)


@V.scene("a3")
def _(S):
    x0, y0, fw, fh = 560, 150, 260, 220
    for r_ in range(3):
        for c_ in range(3):
            x, y = x0 + c_ * fw, y0 + r_ * fh
            mine = (r_, c_) == (1, 1)
            S.draw([Fl(P_rect(x, y, fw, fh, 0), (250, 236, 200) if mine else (236, 232, 222)), stk(P_rect(x, y, fw, fh, 4), 6)], 0.05 * (r_ * 3 + c_), 0.2, snd=None)
            if not mine:
                S.add(Dr(back_fig(x + fw / 2, y + fh - 8, 0.5, hair=("bald", "chef", None, "bald", None, "chef", None, "bald")[r_ * 3 + c_ - (1 if r_ * 3 + c_ > 4 else 0)]),
                         S.c("everyone", 1) + 0.08 * (r_ * 3 + c_), 0.0, pop=True, anchor=(x + fw / 2, y + fh / 2), seed=30 + r_ * 3 + c_))
    S.text("me", x0 + fw + fw / 2, y0 + fh + 140, 64, ORANGE, at=S.c("everyone", 1), anchor="m")
    for k, (ax, ay) in enumerate(((x0 + 120, y0 + 110), (x0 + 2 * fw + 140, y0 + 110), (x0 + 130, y0 + 2 * fh + 110), (x0 + 2 * fw + 130, y0 + 2 * fh + 110))):
        S.add(arrow(P_bez((ax, ay), ((ax + x0 + 1.5 * fw) / 2, (ay + y0 + 1.5 * fh) / 2 - 30), (x0 + 1.5 * fw, y0 + 1.5 * fh)), S.c("question", 1) + 0.1 * k, RED, 5, 0.3, dashed=True))
    S.text("it learned\nto listen.", 1380, 300, 100, RED, at=S.c("listen", 2) - 0.3, lh=1.1, rot=-3)
    S.text("new?", 200, 300, 120, INK, at=S.c("new") - 0.2, rot=-4)


@V.scene("a4")
def _(S):
    px, py, ps = 680, 540, 2.75
    S.draw(ph_screen(px, py, ps), 0.0, 0.3, snd=None)
    S.add(snd="buzz", at=S.c("buzzed") - 0.1)
    sw = 170 * ps - 70
    S.add(screen_lines(px, py - 155 * ps + 110, sw - 80, "9:00", 72, INK, at=S.c("nine") - 0.1))
    S.add(screen_lines(px, py - 190, sw - 60, "unknown", 70, INK, at=S.c("unknown") - 0.1))
    S.draw([Fl(P_rect(px - 195, py - 120, 390, 420, 0, r=30), (226, 219, 205)), stk(P_rect(px - 195, py - 120, 390, 420, 5, r=30), 6)], S.l(1) - 0.3, 0.3, snd=None)
    S.add(screen_lines(px, py - 40, 370, "It's Mom.\nLost my phone.\nAt the hospital.\nI'm safe.", 70, INK, at=S.l(1) + 0.05, cps=30))
    S.text("lost?", 1240, 330, 120, RED, at=S.c("lost", 2) - 0.2, rot=-3)
    S.text("then who\ntexted at 7:06?", 1200, 560, 90, INK, at=S.c("7:06", 2) - 0.4, lh=1.1, rot=-2)


@V.scene("a5")
def _(S):
    S.draw([Fl(P_rect(200, 620, 680, 200, 0, r=20), (196, 196, 194)), stk(P_rect(200, 620, 680, 200, 8, r=20), 9),
            stk(P_poly([(540, 620), (540, 410), (720, 410), (720, 470)]), 26)], 0.0, 0.3, snd=None)
    S.text("the tap.", 200, 300, 100, INK, at=0.1, rot=-2)
    S.pop([Fl(P_ell(700, 520, 12, 18, 1, closed=True), COAT), stk(P_ell(700, 520, 12, 18, 2, 0.05), 4)], S.c("coughed") - 0.1, (700, 520), snd=None,
          until=S.c("dry") + 0.3)
    S.text("dry.", 820, 430, 120, RED, at=S.c("dry") - 0.1, rot=-3)
    hx, hy = 1600, 300
    S.draw([Fl(P_rect(hx - 130, hy - 70, 260, 140, 0, r=8), WHITE), stk(P_rect(hx - 130, hy - 70, 260, 140, 5, r=8), 6),
            Fl(P_rect(hx - 14, hy - 46, 28, 92, 0), RED), Fl(P_rect(hx - 46, hy - 14, 92, 28, 0), RED)], S.c("hospital", 1) - 0.3, 0.4, snd=None)
    S.text("20 min", 1520, 470, 92, INK, at=S.c("twenty", 1) - 0.1)
    S.add(Fig(1000, 900, 0.85, at=S.c("eight-year-old", 1) - 0.3, poses=[("stand", 0)], moods=[("worried", 0)], kind="spiky", seed=12, enter="pop"))
    S.text("we had to go.", 1180, 760, 104, RED, at=S.c("go", 2) - 0.3, rot=-2)


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


# --------------------------------------------------------------------------- the landing
@V.scene("h1")
def _(S):
    landing(S)
    knockers(S)
    kids(S, 480)
    S.text("full.", 300, 140, 110, RED, at=S.c("full") - 0.2, rot=-2)
    S.text("the baker", DOORS[4] - 120, 130, 84, INK, at=S.c("baker", 1) - 0.1, rot=-2)
    S.text("Mr. Duval", DOORS[6] - 140, 130, 84, INK, at=S.c("duval", 1) - 0.1, rot=-2)
    S.text("slippers.", DOORS[6] - 120, 250, 76, INK, at=S.c("slippers", 1) - 0.1, rot=-2)


@V.scene("h2")
def _(S):
    landing(S)
    knockers(S)
    kids(S, 480, 960, S.c("walked") - 0.1, S.e(0) - 0.2)
    S.text("socks.", 280, 130, 100, INK, at=S.c("socks") - 0.2, rot=-2)
    S.text("slowly.", 760, 130, 100, INK, at=S.c("slowly") - 0.2, rot=-2)
    S.text("so hard it hurt.", 1230, 130, 84, RED, at=S.c("hurt") - 0.4, rot=-2)


@V.scene("h3")
def _(S):
    landing(S)
    knockers(S)
    kids(S, 960)
    t_hit = S.c("bottle") - 0.05
    roll = lambda u: (180 * ease_out(min(1.0, u / 1.2)), 0.0, 3.0 * ease_out(min(1.0, u / 1.2)), 1.0)
    bottle = [Fl(P_rect(790, 1010, 90, 34, 0, r=14), (150, 186, 214)), stk(P_rect(790, 1010, 90, 34, 4, r=14), 5),
              Fl(P_rect(880, 1018, 34, 18, 0, r=6), (150, 186, 214)), stk(P_rect(880, 1018, 34, 18, 3, r=6), 4)]
    S.add(Dr(bottle, 0.0, 0.0, seed=9, move=lambda u: roll(max(0.0, u - t_hit)), anchor=(840, 1027)))
    S.add(snd="clink", at=t_hit + 0.05)
    S.text("clink.", 1120, 760, 110, RED, at=t_hit + 0.1, rot=8)


@V.scene("h4")
def _(S):
    landing(S)
    t_turn = S.c("turned") - 0.1
    knockers(S, baker_turn=t_turn)
    kids(S, 960, maya_mood="wow", noah_mood="wow")
    S.text("all the way round.", 220, 130, 92, RED, at=S.c("round") - 0.4, rot=-2)
    S.text("listening.", 1250, 130, 100, INK, at=S.c("listened", 1) - 0.3, rot=-2)


@V.scene("h5")
def _(S):
    landing(S)
    knockers(S, baker_turn=-1.0)
    kids(S, 960, maya_mood="wow", noah_mood="wow")
    S.text("\"Maya? Is that Mom?\"", 220, 130, 92, INK, at=S.l(0) + 0.1, rot=-2)
    S.add(arrow(P_bez((520, 160), (600, 220), (640, 300)), S.l(0) + 0.3, INK, 5, 0.3))
    S.text("Noah's voice.", 1150, 130, 100, RED, at=S.c("voice", 1) - 0.3, rot=-2)


@V.scene("h6")
def _(S):
    landing(S)
    t_back = S.c("back") - 0.2
    knockers(S, baker_turn=-1.0, baker_back=t_back)
    kids(S, 960)
    S.text("don't move.", 260, 130, 100, INK, at=S.c("move") - 0.2, rot=-2)
    S.text("a very long time.", 1100, 130, 92, GREY, at=S.c("long") - 0.3, rot=-2)


# --------------------------------------------------------------------------- the stairs
def stairs(S, at=0.0):
    pts = [(1450, 900)]
    for k in range(6):
        x, y = 1450 - k * 140, 900 - k * 100
        pts += [(x - 140, y), (x - 140, y - 100)]
    S.draw([stk(P_poly(pts), 10)], at, 0.4, snd=None)
    S.draw([Fl(P_rect(230, 60, 220, 330, 0), NIGHT), stk(P_rect(230, 60, 220, 330, 6), 7)], at + 0.1, 0.3, snd=None)
    S.text("Duval's flat", 180, 460, 74, INK, at=at + 0.3)


@V.scene("st1")
def _(S):
    stairs(S)
    S.add(Fig(1640, 1000, 1.3, poses=[("handin_l", 0)], moods=[("wow", S.l(1))], kind="bob", seed=13, enter="none"))
    S.add(Fig(1500, 1000, 0.95, poses=[("handin", 0)], moods=[("wow", S.l(1))], kind="spiky", seed=12, enter="none"))
    S.text("upstairs.", 820, 160, 100, INK, at=S.c("upstairs") - 0.2, rot=-3)
    S.text("\"Maya? Help me!\"", 820, 300, 110, RED, at=S.l(1) + 0.05, rot=-3)
    S.add(arrow(P_bez((460, 230), (640, 300), (800, 270)), S.l(1) + 0.2, RED, 6, 0.3, dashed=True))


@V.scene("st2")
def _(S):
    hands(S)
    S.text("Noah's voice.", 200, 230, 100, RED, at=S.c("voice") - 0.3, rot=-3)
    S.text("but Noah\nwas right here.", 1180, 230, 90, INK, at=S.c("here", 1) - 0.5, lh=1.1, rot=-2)


@V.scene("st3")
def _(S):
    hands(S, at=-1.0)
    S.text("\"that's not me.\"", 160, 300, 96, INK, at=S.l(0) + 0.05, rot=-3)
    S.text("\"I know.\"", 1340, 300, 110, ORANGE, at=S.l(1) + 0.05, rot=-3)


@V.scene("st4")
def _(S):
    S.noframe = True
    S.add(black(0.9))
    S.draw([Fl(P_rect(230, 60, 220, 330, 0), (12, 12, 14)), stk(P_rect(230, 60, 220, 330, 6), 7, (120, 116, 112))], 0.0, 0.0, snd=None)
    S.text("\"Maya, don't go\nwith him.\nHe's not me.\"", 600, 230, 104, RED, at=S.l(1) + 0.05, lh=1.1, rot=-3)
    t_h = S.l(2) - 0.2
    S.add(black(0.97, at=t_h))
    hands(S, at=t_h)
    S.text("very, very still.", 1180, 860 - 30, 96, WHITE, at=S.c("still", 2) - 0.4, rot=-2)
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
