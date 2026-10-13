"""'How to Save Money So Easily It Feels Illegal' in the 'simple, actually' style: a stick-figure doodle explainer on cream paper,
few words on screen, short spoken sentences, numbered systems, soft keys underneath. Kokoro voice (bf_emma).
Usage: python3 build_save.py            (full video)
       SAMPLE=a:b python3 build_save.py (only lines a..b-1, to review)"""
import math
import os
import random
import subprocess
import wave

import cairocffi as cairo
import numpy as np

from doodle import *          # noqa: F401,F403

A = os.path.join(D, "assets_save")
E = os.path.join(D, "sa_save")
O = os.path.join(D, "out")
for p in (A, E, O, os.path.join(A, "voice")):
    os.makedirs(p, exist_ok=True)
FPS, SR = 30, 44100


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# --------------------------------------------------------------------------- script (sub = exactly what is said, shown in the .srt)
# Facts checked October 2026; sources in scripts/save_money_script.md
SAY = {"37%": "thirty-seven percent", "86%": "eighty-six percent", "3.5%": "three point five percent", "13.6%": "thirteen point six percent",
       "72-hour": "seventy-two hour", "MIT": "M I T", "ETF": "E T F", "Thaler": "Tayler", "Benartzi": "Ben-artsy"}


def speak(sub):
    out = []
    for w in sub.split():
        core = w.rstrip(".,:;?!")
        out.append(SAY.get(core, core) + w[len(core):])
    return " ".join(out)


LINES = []


def L(g, sub):
    LINES.append(dict(g=g, sub=sub, tts=speak(sub)))


L("o1", "You get paid. For about a week, you feel rich.")
L("o2", "Then, somehow, the money is gone.")
L("o2", "And you don't even know where it went.")
L("o3", "So you promise yourself: next month, I'll save.")
L("o3", "Next month comes. Same thing.")
L("o4", "And here's the part nobody tells you.")
L("o5", "It's not about how much you earn. And it's not about discipline.")
L("o6", "Your brain is built to spend now, and forget about later.")
L("o7", "Psychologists call it present bias. A euro today feels bigger than a euro next year.")
L("o8", "But researchers found something interesting.")
L("o8", "People who save a lot don't have more willpower. They just set things up so saving happens without them.")
L("o9", "Today, I'll show you eight simple systems that make saving almost automatic.")
L("o9", "No spreadsheets. No guilt. Let's begin.")

L("c1", "One. Pay yourself first.")
L("c1a", "Most people save like this: get paid, spend, and save whatever is left.")
L("c1a", "But there is almost never anything left.")
L("c1b", "Here's what people who save do: get paid, save first, then spend what's left.")
L("c1c", "Set up an automatic transfer for the day after payday. Even fifty euros is enough to start.")
L("c1d", "Because money you never see in your current account is money you don't miss.")

L("c2", "Two. Make saving the default.")
L("c2a", "In one famous study, a company changed just one thing.")
L("c2a", "New employees were signed up for the pension plan automatically, unless they said no.")
L("c2b", "Participation jumped from about 37% to 86%.")
L("c2b", "Same company. Same plan. Only the default changed.")
L("c2c", "So make everything a default: automatic saving, automatic investing, and round-ups, if your bank offers them.")
L("c2c", "Every decision you remove is one you can't get wrong.")

L("c3", "Three. Make spending hurt a little.")
L("c3a", "Handing over cash feels painful. Tapping a card or a phone barely feels like anything.")
L("c3b", "In one experiment at MIT, people paying by card offered up to twice as much for the same basketball tickets.")
L("c3c", "When money is invisible, your brain barely feels it leave.")
L("c3d", "So delete saved cards from shopping sites. Turn off one-click buying. Delete the apps you shop on when you're bored.")
L("c3d", "A few seconds of friction is often enough.")

L("c4", "Four. The 72-hour rule.")
L("c4a", "When you want something you don't need, don't say no. Just say: not yet.")
L("c4b", "Put it in your basket, close the page, and wait three days.")
L("c4c", "Most of the time, the urge is gone. You didn't want the thing. You wanted the feeling.")
L("c4d", "If you still want it after three days, buy it. Without guilt.")

L("c5", "Five. Give every euro a job.")
L("c5a", "Money sitting in one big account feels like it's all there to spend.")
L("c5b", "So split it into pots: rent, food, fun, emergencies, and future you.")
L("c5c", "In one study in rural India, workers saved more when their savings were split into two envelopes instead of one.")
L("c5c", "And even more when the envelopes had a picture of their children on them.")
L("c5d", "Most banking apps now let you create pots for free. Give each one a name.")

L("c6", "Six. Fix big things once, not small things daily.")
L("c6a", "Skipping a coffee every day takes willpower every single day.")
L("c6b", "Your phone plan, your insurance, your bank fees, your subscriptions: fix them once, and you save every month after that.")
L("c6c", "Open your bank app, scroll through the last three months, and cancel anything you wouldn't sign up for again today.")
L("c6d", "One boring hour can save you more than a year of skipped coffees.")

L("c7", "Seven. Save your next raise, before you get used to it.")
L("c7a", "When people earn more, they usually spend more: a bigger flat, a nicer car, more dinners out.")
L("c7a", "Economists call it lifestyle creep.")
L("c7b", "Richard Thaler and Shlomo Benartzi tested a simple fix: commit today to save part of your future raises.")
L("c7b", "For the people who joined, savings rates went from 3.5% to 13.6% in forty months.")
L("c7c", "So next time you get a raise, send half of it to savings from the very first month. You won't miss money you never got used to.")

L("c8", "Eight. Meet your future self.")
L("c8a", "To your brain, your future self feels almost like a stranger.")
L("c8b", "In one experiment, people who saw an aged version of their own face chose to set aside about twice as much for retirement.")
L("c8c", "Your future self is real. They will live with every choice you make today.")
L("c8d", "So once you have a safety cushion of three to six months of expenses, put the rest to work.")
L("c8d", "A cheap, diversified index fund, every month, automatically.")
L("c8e", "That's how saving turns into building.")

L("f0", "Final message.")
L("f1", "Saving money isn't about being cheap. And it isn't about willpower.")
L("f2", "It's about building a system that does the hard part for you.")
L("f3", "Pay yourself first. Make it automatic. Add a little friction. Wait three days. Name your pots. "
        "Fix the big things once. Save your raises. And remember who you're saving for.")
L("f4", "Set it up once, and it keeps working while you sleep.")
L("end", "This is education, not financial advice. If this helped, subscribe. And next up: every ETF, explained.")

GROUPS = []
for i, l in enumerate(LINES):
    if not GROUPS or GROUPS[-1][0] != l["g"]:
        GROUPS.append((l["g"], []))
    GROUPS[-1][1].append(i)
LEAD, TAIL = 0.6, 3.2

# --------------------------------------------------------------------------- voice (Kokoro, cached per line)
KOKORO_DIR = os.environ.get("KOKORO_DIR", os.path.join(D, "kokoro"))
VOICE, VOICE_LANG, VOICE_SPEED = "bf_emma", "en-gb", 0.95
_KOKORO = []


def kokoro_say(text, path):
    if os.path.exists(path) and os.path.exists(path + ".txt") and open(path + ".txt").read() == text:
        return
    if not _KOKORO:
        from kokoro_onnx import Kokoro
        _KOKORO.append(Kokoro(os.path.join(KOKORO_DIR, "kokoro-v1.0.onnx"), os.path.join(KOKORO_DIR, "voices-v1.0.bin")))
    a, sr = _KOKORO[0].create(text, voice=VOICE, speed=VOICE_SPEED, lang=VOICE_LANG)
    pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    open(path + ".txt", "w").write(text)


def tts(i, text):
    raw, out = os.path.join(A, "voice", f"l{i:02d}_raw.wav"), os.path.join(A, "voice", f"l{i:02d}.wav")
    kokoro_say(text, raw)
    if not (os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(raw)):
        run(["ffmpeg", "-y", "-i", raw, "-af",
             "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
             "-ar", str(SR), "-ac", "1", out])
    with wave.open(out) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


GI = {}
for gk, (g, idx) in enumerate(GROUPS):
    for i in idx:
        GI[i] = gk


def gap_for(i):
    """Breath after line i: tight inside a drawing, a beat longer when the page changes, longer after a chapter title."""
    rr = random.Random(i * 7919 + 3)
    if i + 1 >= len(LINES):
        return 0.0
    same = GI[i + 1] == GI[i]
    g = 0.42 if same else 0.78
    if LINES[i]["g"] in ("c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"):
        g = 0.95
    if LINES[i + 1]["g"] in ("c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "f0"):
        g += 0.45
    if LINES[i]["g"] in ("o4", "f0"):
        g += 0.5
    if len(LINES[i]["sub"].split()) <= 5:
        g -= 0.08
    return max(0.3, g + rr.uniform(-0.12, 0.14))


voice = [tts(i, l["tts"]) for i, l in enumerate(LINES)]
frames, starts, t = [], [], 0.0
for i, v in enumerate(voice):
    n = round((len(v) / SR + gap_for(i) + (LEAD if i == 0 else 0) + (TAIL if i == len(voice) - 1 else 0)) * FPS)
    starts.append(t)
    frames.append(n)
    t += n / FPS
TOTAL = t
NS = int(round(TOTAL * SR))
vt = np.zeros(NS, dtype=np.float32)
line_times = []
for i, v in enumerate(voice):
    s0 = int(round((starts[i] + (LEAD if i == 0 else 0)) * SR))
    vt[s0:s0 + len(v)] += v[: max(0, NS - s0)]
    line_times.append((s0 / SR, s0 / SR + len(v) / SR))


def write_wav(path, data, ch=1):
    pcm = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "w") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


write_wav(os.path.join(A, "voice.wav"), vt)

# --------------------------------------------------------------------------- word timings (for cues and the .srt)
cl = lambda w: w.replace("*", "")


def pauses(v, win=0.01, thr=0.012, min_len=0.09):
    n = int(win * SR)
    rms = np.sqrt(np.convolve(v ** 2, np.ones(n) / n, mode="same"))[::n]
    q, out, k = rms < thr, [], 0
    while k < len(q):
        if q[k]:
            j = k
            while j < len(q) and q[j]:
                j += 1
            if (j - k) * win >= min_len and k > 0 and j < len(q):
                out.append((k + j) / 2 * win)
            k = j
        else:
            k += 1
    return out


def chunks(sub, mx=9):
    sents, cur = [], []
    for w in sub.split():
        cur.append(w)
        if cl(w)[-1:] in ".:?!":
            sents.append(cur)
            cur = []
    if cur:
        sents.append(cur)
    out = []
    for s in sents:
        while len(s) > mx:
            cut = next((j + 1 for j in range(len(s) // 2, len(s) - 2) if cl(s[j]).endswith(",")), None) or \
                next((j + 1 for j in range(len(s) // 2, 1, -1) if cl(s[j]).endswith(",")), None) or len(s) // 2
            out.append(s[:cut])
            s = s[cut:]
        out.append(s)
    return [" ".join(c) for c in out]


def slen(w):
    k = cl(w).rstrip(".,:?!")
    return len(SAY.get(k, k)) + 1


def timed_chunks(i):
    parts = chunks(LINES[i]["sub"])
    t0, t1 = line_times[i]
    lens = [sum(slen(w) for w in p.split()) for p in parts]
    ps = [t0 + p for p in pauses(voice[i])]
    bounds, acc = [t0], t0
    for k, n in enumerate(lens[:-1]):
        acc += (t1 - t0) * n / sum(lens)
        b = acc
        if cl(parts[k])[-1:] in ".,:?!" and ps:
            near = min(ps, key=lambda p: abs(p - acc))
            if abs(near - acc) < 0.7:
                b = near
        bounds.append(max(b, bounds[-1] + 0.25))
    bounds.append(t1)
    return list(zip(parts, bounds[:-1], bounds[1:]))


def word_times(i):
    out = []
    for part, a, b in timed_chunks(i):
        ws = part.split()
        lens = [slen(w) for w in ws]
        t = a
        for w, n in zip(ws, lens):
            d = (b - a) * n / sum(lens)
            out.append((w, t, t + d))
            t += d
    return out


WT = [word_times(i) for i in range(len(LINES))]


def when(i, word, nth=0):
    hits = [a for w, a, b in WT[i] if cl(w).lower().strip("\"“”").rstrip(".,:?!;") == word.lower()]
    if len(hits) <= nth:
        raise KeyError(f"cue {word!r} not in line {i}: {LINES[i]['sub']}")
    return hits[nth]


# --------------------------------------------------------------------------- scene helper
class Scene:
    def __init__(self, gk):
        self.name, self.li = GROUPS[gk]
        self.t0 = starts[self.li[0]]
        self.dur = sum(frames[i] for i in self.li) / FPS
        self.els, self.snd = [], []
        self.rng = random.Random(gk * 97 + 1)
        self.cam = Camera(gk * 13 + 5, self.dur, push=0.0)

    def c(self, word, k=0, nth=0):
        return when(self.li[k], word, nth) - self.t0

    def l(self, k=0):
        return line_times[self.li[k]][0] - self.t0

    def e(self, k=0):
        return line_times[self.li[k]][1] - self.t0

    def add(self, *fns, snd=None, at=None):
        self.els += list(fns)
        if snd and at is not None:
            self.snd.append((snd, self.t0 + at))
        return fns[0] if fns else None

    def draw(self, ops, at, dur=0.5, snd="scr", **kw):
        return self.add(Dr(ops, at, dur, seed=self.rng.randint(1, 9999), **kw), snd=snd, at=at)

    def pop(self, ops, at, anchor, snd="pop", **kw):
        return self.add(Dr(ops, at, 0.0, pop=True, anchor=anchor, seed=self.rng.randint(1, 9999), **kw), snd=snd, at=at)

    def text(self, txt, x, y, size=96, col=INK, at=0.0, **kw):
        return self.add(T(txt, x, y, size, col, at=at, **kw))

    def push(self, amount, cx=W / 2, cy=H / 2):
        self.cam = Camera(self.rng.randint(1, 999), self.dur, push=amount, cx=cx, cy=cy)


SCENES = {}


def scene(name):
    def deco(f):
        SCENES[name] = f
        return f
    return deco


def chapter(S, n, title, side, peek=True):
    """Number big in orange on one side, the title written next to it, never centred, never the same twice."""
    r = S.rng
    num = str(n)
    rot = r.uniform(-4, 3)
    if side == 0:
        nx, tx, anchor = 300 + r.randint(-30, 40), 640 + r.randint(-20, 30), "l"
    else:
        nx, tx, anchor = 1560 + r.randint(-40, 30), 1250 + r.randint(-30, 20), "r"
    ny = 640 + r.randint(-40, 30)
    S.add(T(num, nx, ny, 420, ORANGE, at=0.02, anchor="m", rot=rot, cps=6), snd="thump", at=0.02)
    S.add(circ(nx + 4, ny - 150, 175 + r.randint(-10, 10), 200 + r.randint(-10, 15), 0.3, INK, 6.5, 0.42, seed=n))
    words = title.split("\n")
    t_at = S.c(title.split()[0].strip(".,").lower()) - 0.05
    ty = 520 + r.randint(-30, 20) - (len(words) - 1) * 60
    tf = S.text(title, tx, ty, 118, INK, at=t_at, anchor=anchor, rot=r.uniform(-2.5, 1.5), cps=30)
    w = tf.w
    x0 = tx if anchor == "l" else tx - w
    S.add(under(x0 + 10, x0 + min(w, 520), ty + (len(words) - 1) * 127 + 40, tf.end + 0.1, ORANGE, 8, 0.3, seed=n, wavy=n % 2 == 0))
    if peek:
        fx = (1650 if side == 0 else 280) + r.randint(-40, 40)
        S.add(Fig(fx, 1300, 1.3, at=0.25, poses=[("stand", 0), ("wave", 0.6)], moods=[("smile", 0), ("happy", 1.0)],
                  enter="pop", seed=n + 40, flip=side == 1))


# --------------------------------------------------------------------------- scenes: cold open
@scene("o1")
def _(S):
    S.add(Fig(720, 900, 1.35, at=0.0, poses=[("stand", 0), ("arms_up", S.c("rich"))], moods=[("smile", 0), ("grin", S.c("rich"))], seed=3))
    S.draw(calendar(1330, 470, 1.0, day=28), S.c("paid") - 0.1, 0.5)
    for k, (x, y, s) in enumerate(((470, 330, 0.8), (980, 260, 1.0), (1040, 520, 0.7), (420, 600, 0.65))):
        S.pop(coin(x, y, s), S.c("rich") + 0.08 * k, (x, y), snd="pop" if k == 0 else None)
    S.text("rich.", 1180, 820, 130, ORANGE, at=S.c("rich") + 0.15, rot=-6)


@scene("o2")
def _(S):
    gone = S.c("gone")
    S.add(Fig(820, 900, 1.35, at=0.0, poses=[("arms_up", 0), ("stand", 0.4), ("shrug", S.c("know", 1))],
              moods=[("grin", 0), ("o", gone), ("worried", S.c("know", 1))], seed=3))
    for k, (x, y) in enumerate(((560, 330), (1080, 280), (1130, 520), (510, 600))):
        fly = (lambda u, k=k: (u * (900 + 120 * k) * 1.6, -u * (520 - 90 * k) * 1.4 + 300 * u * u, u * (2 + k), 1.0))
        S.add(Dr(coin(x, y, 0.8), 0.0, 0.0, anchor=(x, y), move=lambda tt, f=fly, s0=gone - 0.35: f(max(0.0, tt - s0) ** 1.6 * 0.7),
                 seed=k + 70, until=gone + 1.2))
    S.text("gone.", 1290, 720, 120, INK, at=gone + 0.1, rot=-4)
    q = S.c("where", 1)
    S.text("?", 905, 420, 170, ORANGE, at=q, rot=10)
    S.text("?", 700, 470, 110, INK, at=q + 0.25, rot=-12)


@scene("o3")
def _(S):
    S.add(Fig(520, 920, 1.3, at=0.0, poses=[("stand", 0), ("point_up", S.c("promise") - 0.1), ("shrug", S.c("same", 1))],
              moods=[("smile", 0), ("happy", S.c("save")), ("flat", S.c("same", 1))], seed=3))
    S.draw(bubble(980, 330, 560, 210, tail=(-1, 1)), S.c("next") - 0.15, 0.35)
    S.text("next month,\nI'll save!", 760, 300, 82, INK, at=S.c("next"), cps=30)
    c = S.c("comes", 1)
    S.draw(calendar(1400, 760, 0.85, day=28, head="NEXT MONTH"), c - 0.3, 0.45)
    S.add(arrow(P_arc(1400, 760, 250, 230, -150, 160, 50), c + 0.2, ORANGE, 7, 0.6))
    S.text("same thing.", 640, 1020, 92, GREY, at=S.c("same", 1), rot=-3)


@scene("o4")
def _(S):
    S.add(Fig(980, 1520, 3.2, at=0.0, poses=[("stand", 0)], moods=[("smug", 0)], enter="none", seed=3, idle=0.6, look=0.4))
    S.text("psst.", 1430, 320, 96, GREY, at=S.c("part") - 0.2, rot=8)


@scene("o5")
def _(S):
    S.text("how much you earn", 250, 420, 112, INK, at=S.c("earn") - 0.45, cps=34)
    S.add(strike(230, 395, 1150, 380, S.c("and") + 0.05, RED, 9))
    S.text("discipline", 330, 690, 140, INK, at=S.c("discipline") - 0.2, rot=-3)
    S.add(strike(310, 650, 960, 640, S.c("discipline") + 0.75, RED, 10))
    S.add(Fig(1530, 930, 1.3, at=0.0, poses=[("stand", 0), ("shrug", S.c("not") + 0.1)], moods=[("flat", 0), ("smug", S.c("discipline"))], seed=3, flip=True))


@scene("o6")
def _(S):
    S.draw(brain(620, 560, 1.25), S.c("brain") - 0.25, 0.7)
    S.text("NOW", 1060, 560, 260, ORANGE, at=S.c("now") - 0.1, rot=-5, cps=10)
    S.text("later", 1560, 760, 52, GREY, at=S.c("later") - 0.05, rot=4)
    S.add(arrow(P_bez((1530, 700), (1480, 640), (1440, 610)), S.c("later") + 0.4, GREY, 4, 0.3, head=14))


@scene("o7")
def _(S):
    S.add(hilite(150, 150 + text_w("present bias", 96), 212, 66, S.c("present") - 0.05, seed=4))
    S.text("present bias", 150, 230, 96, INK, at=S.c("present") - 0.05)
    S.pop(coin(720, 620, 2.6), S.c("today"), (720, 620))
    S.text("today", 640, 830, 84, INK, at=S.c("today") + 0.15)
    S.pop(coin(1360, 700, 1.0), S.c("next") - 0.05, (1360, 700))
    S.text("next year", 1250, 820, 64, GREY, at=S.c("year") - 0.1)
    S.text(">", 1010, 720, 200, ORANGE, at=S.c("bigger"), rot=4)


@scene("o8")
def _(S):
    S.add(Fig(900, 990, 1.3, at=0.0,
              poses=[("think", 0), ("stand", S.l(1)), ("cross", S.c("set", 1))],
              moods=[("smile", 0), ("o", S.c("interesting")), ("flat", S.l(1)), ("smug", S.c("set", 1))], seed=3))
    S.text("hmm.", 990, 690, 72, GREY, at=S.c("found") - 0.1, rot=-6)
    S.text("more willpower", 220, 260, 86, INK, at=S.c("willpower", 1) - 0.35, cps=34)
    S.add(strike(200, 232, 240 + text_w("more willpower", 86), 224, S.c("willpower", 1) + 0.5, RED, 9))
    s = S.c("set", 1)
    S.draw(calendar(300, 720, 0.75, day=28), s - 0.15, 0.45)
    S.draw(piggy(1520, 700, 0.9), s + 0.1, 0.6)
    S.add(arrow(P_bez((440, 640), (900, 300), (1370, 600)), s + 0.4, ORANGE, 6, 0.5, dashed=True))
    for k in range(5):            # coins sliding along the arrow, on their own
        t0 = s + 0.9 + k * 0.62
        pts = P_bez((440, 620), (900, 280), (1440, 590), n=30)

        def mv(tt, pts=pts):
            u = clamp(tt / 1.1)
            j = min(len(pts) - 1, int(u * (len(pts) - 1)))
            return pts[j][0] - 440, pts[j][1] - 620, 0.0, 1.0 - 0.3 * u
        S.add(Dr(coin(440, 620, 0.45), t0, 0.0, pop=True, anchor=(440, 620), move=mv, until=t0 + 1.1, seed=80 + k))
    S.text("on its own.", 1240, 1000, 76, ORANGE, at=S.c("without", 1), rot=-3)


@scene("o9")
def _(S):
    S.text("8", 330, 560, 380, ORANGE, at=S.c("eight") - 0.05, anchor="m", rot=-6, cps=8)
    S.text("simple systems", 520, 400, 110, INK, at=S.c("simple"), cps=30)
    S.add(under(530, 520 + text_w("simple systems", 110), 428, S.c("systems") + 0.2, ORANGE, 7, 0.35, wavy=True))
    S.text("almost automatic.", 600, 540, 76, GREY, at=S.c("automatic") - 0.25)
    sp = S.c("spreadsheets", 1)
    gx, gy = 640, 700
    ops = [S_(P_rect(gx, gy, 300, 200, 8), 6)]
    for k in (1, 2, 3):
        ops.append(S_(P_line(gx, gy + k * 50, gx + 300, gy + k * 50, 0.01, k), 4))
    for k in (1, 2):
        ops.append(S_(P_line(gx + k * 100, gy, gx + k * 100, gy + 200, 0.01, k + 5), 4))
    S.draw(ops, sp - 0.3, 0.4)
    S.add(cross(790, 800, 90, sp + 0.35, RED, 10))
    S.text("guilt", 1110, 840, 100, INK, at=S.c("guilt", 1) - 0.1)
    S.add(cross(1210, 805, 80, S.c("guilt", 1) + 0.35, RED, 10))
    S.add(Fig(1640, 950, 1.2, at=0.0, poses=[("stand", 0), ("point_l", S.l(0) + 0.3), ("wave", S.c("begin", 1))],
              moods=[("smile", 0), ("happy", S.c("begin", 1))], seed=3, flip=True))


S_ = S       # the stroke-op helper from doodle (the class below shadows the letter in scene code)

# --------------------------------------------------------------------------- 1. pay yourself first
CH = {1: ("Pay yourself\nfirst.", 0), 2: ("Make saving\nthe default.", 1), 3: ("Make spending\nhurt a little.", 0),
      4: ("The 72-hour\nrule.", 1), 5: ("Give every euro\na job.", 0), 6: ("Fix big things\nonce.", 1),
      7: ("Save your\nnext raise.", 0), 8: ("Meet your\nfuture self.", 1)}
for _n in CH:
    def _mk(n):
        def f(S):
            title, side = CH[n]
            chapter(S, n, title, side, peek=n in (1, 3, 6, 8))
        SCENES[f"c{n}"] = f
    _mk(_n)


def flow(S, items, y, at_list, x0=260, gap=520, hi=None):
    """A row of little drawings joined by arrows, each drawn on its word."""
    for k, ((ops_fn, label), at) in enumerate(zip(items, at_list)):
        x = x0 + k * gap
        S.draw(ops_fn(x, y), at - 0.1, 0.45)
        S.text(label, x, y + 210, 76, ORANGE if hi == k else INK, at=at, anchor="m")
        if k:
            S.add(arrow(P_line(x - gap + 150, y, x - 160, y, 0.04, k), at - 0.25, INK, 6, 0.3))
        if hi == k:
            S.add(circ(x, y + 30, 190, 230, at + 0.35, ORANGE, 7))


paid = lambda x, y: calendar(x, y, 0.62, day=28)
spend = lambda x, y: cart(x, y + 10, 0.85)
save = lambda x, y: piggy(x, y + 10, 0.62)


@scene("c1a")
def _(S):
    S.text("most people:", 160, 160, 70, GREY, at=S.c("most") - 0.1)
    flow(S, [(paid, "paid"), (spend, "spend"), (save, "save?")], 520, [S.c("paid"), S.c("spend"), S.c("save", 0, 1)], x0=330, gap=620)
    S.text("€0", 1450, 340, 150, RED, at=S.c("never", 1), rot=-8)


@scene("c1b")
def _(S):
    S.text("people who save:", 160, 160, 70, GREY, at=S.c("people") - 0.1)
    flow(S, [(paid, "paid"), (save, "save"), (spend, "spend")], 520, [S.c("paid"), S.c("save", 0, 1), S.c("spend")], x0=330, gap=620, hi=1)


@scene("c1c")
def _(S):
    px, py = 700, 560
    S.draw(phone(px, py, 1.45), S.c("automatic") - 0.4, 0.5)
    S.text("auto\ntransfer", px - 95, py - 110, 54, INK, at=S.c("transfer") - 0.1, cps=30)
    tx, ty = px - 60, py + 70
    S.draw([S_(P_rect(tx, ty, 120, 60, 6, r=30), 6)], S.c("transfer"), 0.3)
    tog = S.c("transfer") + 0.6
    S.add(Dr([Fl(P_rect(tx + 4, ty + 4, 112, 52, 0, r=26), ORANGE)], tog, 0.0, pop=True, anchor=(tx + 60, ty + 30)))
    S.add(Dr([Fl(P_ell(tx + 30, ty + 30, 21, 21, 3, closed=True), (250, 248, 242)), S_(P_ell(tx + 30, ty + 30, 21, 21, 4, 0.05), 5)], 0, 0.0,
             until=tog, seed=5))
    S.add(Dr([Fl(P_ell(tx + 90, ty + 30, 21, 21, 3, closed=True), (250, 248, 242)), S_(P_ell(tx + 90, ty + 30, 21, 21, 4, 0.05), 5)], tog, 0.0,
             seed=6), snd="pop", at=tog)
    S.text("day after payday", 1080, 380, 76, INK, at=S.c("day") - 0.1, rot=-2)
    S.add(under(1080, 1600, 410, S.c("payday") + 0.3, ORANGE, 6, 0.3))
    S.text("€50", 1180, 700, 230, ORANGE, at=S.c("fifty") - 0.1, rot=-6, cps=9)
    S.text("is enough to start.", 1150, 820, 66, GREY, at=S.c("enough"))


@scene("c1d")
def _(S):
    S.add(Fig(620, 920, 1.3, at=0.0, poses=[("cross", 0)], moods=[("smug", 0)], seed=3, look=-0.6))
    S.draw(music_note(450, 470, 1.0), 0.3, 0.3, snd=None)
    S.draw(music_note(400, 380, 0.7), 0.9, 0.3, snd=None)
    S.draw(piggy(1320, 720, 1.0), 0.2, 0.55)
    for k in range(4):
        t0 = 0.9 + k * 0.85
        S.add(Dr(coin(1318, 380, 0.42), t0, 0.0, pop=True, anchor=(1318, 380),
                 move=lambda tt: (0, min(1.0, tt / 0.45) ** 2 * 230, 0, 1), until=t0 + 0.45, seed=90 + k))
    S.text("never see it,", 980, 230, 86, INK, at=S.c("never") - 0.05, rot=-3)
    S.text("never miss it.", 1080, 330, 86, ORANGE, at=S.c("miss") - 0.05, rot=-3)


# --------------------------------------------------------------------------- 2. make saving the default
@scene("c2a")
def _(S):
    bx, by = 380, 880
    ops = [S_(P_rect(bx - 150, by - 520, 300, 520, 8), 7)]
    for r_ in range(5):
        for c_ in range(3):
            x, y = bx - 110 + c_ * 80, by - 470 + r_ * 85
            ops.append(S_(P_rect(x, y, 50, 50, 4), 4.5))
    S.draw(ops, S.c("company") - 0.3, 0.7)
    fx, fy = 1080, 560
    S.draw([Fl(P_rect(fx - 230, fy - 300, 460, 600, 0), (250, 248, 242)), S_(P_rect(fx - 230, fy - 300, 460, 600, 8), 6.5)] +
           [S_(P_line(fx - 180, fy - 140 + k * 60, fx + 180 - (k % 2) * 60, fy - 140 + k * 60, 0.01, k), 4, GREY) for k in range(4)],
           S.c("new", 1) - 0.1, 0.5)
    S.text("PENSION PLAN", fx, fy - 200, 64, INK, at=S.c("pension", 1), anchor="m")
    S.draw([S_(P_rect(fx - 180, fy + 150, 70, 70, 5), 6)], S.c("automatically", 1) - 0.3, 0.25)
    S.add(check(fx - 150, fy + 180, 40, S.c("automatically", 1) + 0.1, GREEN, 10))
    S.text("yes (by default)", fx - 88, fy + 205, 46, INK, at=S.c("automatically", 1) + 0.2)
    S.text("unless they say no", 1380, 960, 60, GREY, at=S.c("unless", 1), rot=-3)
    S.text("1 change.", 1450, 230, 90, ORANGE, at=S.c("one", 0, 1) - 0.05, rot=5)


@scene("c2b")
def _(S):
    S.add(*bars(260, 860, [37, 86], ["before", "by default"], S.c("participation") - 0.1, step=S.c("86%") - S.c("37%"),
                maxh=520, bw=190, gap=200, cols=[PALE, ORANGE], txt=["37%", "86%"], seed=5, size=80))
    S.add(circ(745, 290, 140, 78, S.c("86%") + 0.7, INK, 6))
    for k, (w_, txt) in enumerate((("same", "same company"), ("same", "same plan"), ("default", "new default"))):
        at = S.c(w_, 1, 0 if k == 0 else (1 if k == 1 else 0)) - 0.05
        S.text(txt, 1240, 420 + k * 150, 84, ORANGE if k == 2 else INK, at=at, rot=-2)
        if k == 2:
            S.add(check(1190, 395 + k * 150, 26, at + 0.4, GREEN, 8))


@scene("c2c")
def _(S):
    items = (("automatic", 0, "auto-save"), ("automatic", 1, "auto-invest"), ("round-ups", 0, "round-ups"))
    for k, (w_, nth, lab) in enumerate(items):
        y = 300 + k * 190
        at = S.c(w_, 0, nth) - 0.1
        S.draw([S_(P_rect(260, y - 60, 80, 80, 6), 6.5)], at - 0.1, 0.25)
        S.add(check(285, y - 25, 44, at + 0.35, GREEN, 11))
        S.text(lab, 400, y + 8, 100, INK, at=at)
    S.text("(if your bank has them)", 400, 800, 52, GREY, at=S.c("bank") - 0.1)
    S.add(Fig(1480, 930, 1.3, at=0.0, poses=[("stand", 0), ("hips", S.l(1))], moods=[("smile", 0), ("smug", S.l(1))], seed=3, flip=True))
    S.text("fewer decisions,\nfewer mistakes.", 1160, 250, 70, ORANGE, at=S.c("remove", 1) - 0.1, rot=3)


# --------------------------------------------------------------------------- 3. make spending hurt a little
@scene("c3a")
def _(S):
    S.draw([S_(P_line(960, 120, 965, 980, 0.01, 2), 5, GREY)], 0.0, 0.3, snd=None)
    S.add(Fig(430, 900, 1.25, at=0.0, poses=[("hold_r", 0)], moods=[("worried", S.c("painful") - 0.2)], seed=3))
    S.pop(note(600, 610, 0.85), S.c("cash") - 0.1, (600, 610))
    S.text("ouch.", 520, 300, 90, RED, at=S.c("painful"), rot=-6)
    S.add(Fig(1380, 900, 1.25, at=0.0, poses=[("hold_r", 0)], moods=[("smile", 0), ("happy", S.c("barely"))], seed=4))
    S.draw(phone(1530, 610, 0.5), S.c("tapping") - 0.2, 0.3)
    S.text("beep.", 1640, 330, 80, GREY, at=S.c("barely") - 0.2, rot=8)
    S.text("cash", 330, 1020, 70, INK, at=S.c("cash") - 0.1)
    S.text("card / phone", 1220, 1020, 70, INK, at=S.c("card") - 0.1)


@scene("c3b")
def _(S):
    tx, ty = 420, 470
    S.draw([Fl(P_rect(tx - 210, ty - 120, 420, 240, 0, r=16), HL), S_(P_rect(tx - 210, ty - 120, 420, 240, 8, r=16), 6.5),
            S_(P_line(tx + 110, ty - 115, tx + 112, ty + 115, 0.01, 3), 4, GREY)], S.c("basketball") - 0.4, 0.5)
    S.text("GAME", tx - 60, ty + 30, 92, INK, at=S.c("tickets") - 0.2, anchor="m")
    S.text("MIT", 180, 210, 80, GREY, at=S.c("mit") - 0.1)
    S.add(*bars(940, 880, [1, 2], ["cash", "card"], S.c("card") - 0.1, step=0.5, maxh=560, bw=200, gap=180,
                cols=[PALE, ORANGE], txt=["×1", "up to ×2"], seed=7, size=78))


@scene("c3c")
def _(S):
    S.draw(brain(560, 600, 1.15), 0.0, 0.6)
    S.add(Dr([S_(p, 5, GREY) for p in [P_ell(1250, 460, 80, 80, 3, 0.08)]] + [("g", "€", 1250, 495, 90, GREY)], S.c("invisible") - 0.1, 0.4,
             a=0.55, move=lambda tt: (tt * 60, -tt * 30, 0, 1)), snd="scr", at=S.c("invisible"))
    S.text("invisible", 1040, 760, 110, GREY, at=S.c("invisible"), rot=-3)
    S.text("= no pain", 1180, 880, 90, INK, at=S.c("barely"), rot=-3)


@scene("c3d")
def _(S):
    px, py = 470, 540
    S.draw(phone(px, py, 1.5), 0.0, 0.5)
    icons = [(px - 60 + (k % 2) * 120, py - 120 + (k // 2) * 120) for k in range(6)]
    for k, (x, y) in enumerate(icons):
        S.draw([Fl(P_rect(x - 40, y - 40, 80, 80, 0, r=18), [HL, PINK, (150, 186, 214)][k % 3]), S_(P_rect(x - 40, y - 40, 80, 80, 4, r=18), 4.5)],
               0.25 + 0.06 * k, 0.25, snd=None)
    for k, (w_, nth, lab) in enumerate((("cards", 0, "saved cards"), ("one-click", 0, "one-click buying"), ("apps", 0, "shopping apps"))):
        y = 330 + k * 170
        at = S.c(w_, 0, nth) - 0.2
        S.text(lab, 880, y, 88, INK, at=at)
        S.add(strike(860, y - 30, 880 + text_w(lab, 88) + 20, y - 36, at + 0.55, RED, 8, seed=k))
    S.add(cross(px + 60, py + 120, 48, S.c("apps") + 0.3, RED, 9))
    S.add(cross(px - 60, py, 48, S.c("apps") + 0.5, RED, 9))
    S.text("a few seconds of friction.", 880, 930, 76, ORANGE, at=S.c("few", 1) - 0.1, rot=-2)


# --------------------------------------------------------------------------- 4. the 72-hour rule
def gift(x, y, s=1.0, col=(150, 186, 214)):
    return [Fl(P_rect(x - 90 * s, y - 70 * s, 180 * s, 140 * s, 0), col), S_(P_rect(x - 90 * s, y - 70 * s, 180 * s, 140 * s, 8 * s), 6.5 * s),
            S_(P_line(x, y - 70 * s, x, y + 70 * s, 0, 1), 5 * s), S_(P_bez((x, y - 70 * s), (x - 60 * s, y - 130 * s), (x - 70 * s, y - 70 * s)), 5 * s),
            S_(P_bez((x, y - 70 * s), (x + 60 * s, y - 130 * s), (x + 70 * s, y - 70 * s)), 5 * s)]


@scene("c4a")
def _(S):
    S.add(Fig(520, 920, 1.3, at=0.0, poses=[("stand", 0), ("reach", S.c("want") - 0.1), ("hips", S.c("yet"))],
              moods=[("happy", 0), ("o", S.c("no") - 0.1), ("smug", S.c("yet"))], seed=3))
    S.draw(gift(1000, 640, 1.0), S.c("something") - 0.2, 0.45)
    S.draw(bubble(1360, 330, 480, 200, tail=(-1, 1)), S.c("yet") - 0.5, 0.3)
    S.text("not yet.", 1360, 360, 120, ORANGE, at=S.c("yet") - 0.25, anchor="m")
    S.text("no", 1220, 700, 100, GREY, at=S.c("no") - 0.1)
    S.add(strike(1200, 668, 1330, 660, S.c("no") + 0.4, RED, 8))


@scene("c4b")
def _(S):
    S.draw(cart(380, 560, 1.0), S.c("basket") - 0.3, 0.5)
    S.pop(gift(370, 420, 0.55), S.c("basket"), (370, 420))
    wx, wy = 820, 300
    S.draw([S_(P_rect(wx, wy, 380, 260, 8, r=10), 6.5), S_(P_line(wx, wy + 50, wx + 380, wy + 50, 0.01, 2), 5)], S.c("close") - 0.3, 0.4)
    S.add(cross(wx + 345, wy + 26, 14, S.c("close") + 0.15, RED, 6))
    S.add(arrow(P_line(wx + 190, wy + 290, wx + 190, wy + 330, 0, 1), S.c("wait") - 0.5, GREY, 4, 0.2, head=14))
    S.draw(clock(1480, 520, 1.25), S.c("wait") - 0.2, 0.5)
    S.text("72h", 1480, 840, 190, ORANGE, at=S.c("three") - 0.05, anchor="m", rot=-4, cps=10)


@scene("c4c")
def _(S):
    g = S.c("gone")
    S.add(Dr(gift(560, 560, 1.4), 0.0, 0.0, pop=True, anchor=(560, 560), until=g + 0.6,
             move=lambda tt: (0, 0, 0, 1.0 - 0.6 * clamp((tt - g) / 0.6)) if tt > g else (0, 0, 0, 1)))
    S.add(Dr([S_(P_ell(560, 560, 130, 110, 4, 0.1), 5, GREY)], g + 0.6, 0.0, pop=True, anchor=(560, 560), a=0.6))
    S.text("urge: gone.", 360, 870, 86, GREY, at=g - 0.3, rot=-2)
    S.text("the thing", 1080, 420, 100, INK, at=S.c("thing") - 0.2)
    S.add(strike(1060, 390, 1100 + text_w("the thing", 100), 384, S.c("thing") + 0.35, RED, 8))
    S.text("the feeling", 1100, 640, 120, ORANGE, at=S.c("feeling") - 0.3, rot=-3)
    hx, hy = 1700, 560
    S.draw([Fl(P_bez((hx, hy + 50), (hx - 90, hy - 10), (hx - 40, hy - 80), (hx, hy - 30)).tolist() + P_bez((hx, hy - 30), (hx + 40, hy - 80), (hx + 90, hy - 10), (hx, hy + 50)).tolist(), PINK),
            S_(np.vstack([P_bez((hx, hy + 50), (hx - 90, hy - 10), (hx - 40, hy - 80), (hx, hy - 30)), P_bez((hx, hy - 30), (hx + 40, hy - 80), (hx + 90, hy - 10), (hx, hy + 50))]), 6)],
           S.c("feeling") + 0.2, 0.4)


@scene("c4d")
def _(S):
    S.add(Fig(720, 920, 1.35, at=0.0, poses=[("hold", 0), ("arms_up", S.c("guilt") - 0.1)], moods=[("smile", 0), ("grin", S.c("buy"))], seed=3))
    S.pop(gift(724, 690, 0.7), S.c("buy") - 0.1, (724, 690))
    S.add(check(1250, 520, 110, S.c("buy") + 0.2, GREEN, 18))
    S.text("without guilt.", 1110, 830, 100, INK, at=S.c("without") - 0.1, rot=-3)


# --------------------------------------------------------------------------- 5. give every euro a job
@scene("c5a")
def _(S):
    S.draw(jar(1150, 600, 2.0, fill_u=0.85, col=(214, 226, 196)), 0.0, 0.6)
    S.text("ALL", 1150, 640, 120, INK, at=S.c("one") - 0.05, anchor="m")
    S.add(Fig(560, 920, 1.3, at=0.0, poses=[("stand", 0), ("reach", S.c("spend") - 0.4)], moods=[("smile", 0), ("smug", S.c("spend") - 0.3)], seed=3))
    S.text("spend me!", 1340, 270, 76, ORANGE, at=S.c("spend") - 0.1, rot=7)


@scene("c5b")
def _(S):
    labs = (("rent", "rent", 0), ("food", "food", 0), ("fun", "fun", 0), ("emergencies", "SOS", 0), ("future", "future you", 0))
    cols = [(150, 186, 214), (214, 226, 196), PINK, HL, ORANGE]
    for k, (w_, lab, nth) in enumerate(labs):
        x = 260 + k * 350
        at = S.c(w_) - 0.2
        S.draw(jar(x, 600, 1.35, fill_u=0.55 + 0.08 * (k % 3), col=cols[k]), at - 0.1, 0.4, snd="scr" if k in (0, 3) else None)
        S.text(lab, x, 900, 76, ORANGE if k == 4 else INK, at=at + 0.1, anchor="m")
    S.text("pots.", 160, 220, 110, INK, at=S.c("pots") - 0.1, rot=-4)


@scene("c5c")
def _(S):
    S.text("rural India", 160, 200, 76, GREY, at=S.c("india") - 0.2)
    S.draw(envelope(330, 520, 0.95), S.c("india") + 0.2, 0.35)
    S.add(strike(200, 450, 460, 600, S.c("one", 0, 1) + 0.1, RED, 8))
    for k in range(2):
        x = 650 + k * 280
        S.draw(envelope(x, 520, 0.95), S.c("two") - 0.2 + 0.12 * k, 0.35, snd="scr" if k == 0 else None)
    S.text("saved more", 300, 790, 96, INK, at=S.c("saved") - 0.1, rot=-2)
    k1 = S.c("picture", 1)
    S.pop(envelope(1500, 520, 1.6, kid=True), k1 - 0.1, (1500, 520))
    S.text("even more.", 1310, 850, 110, ORANGE, at=S.c("even", 1) + 0.1, rot=-4)


@scene("c5d")
def _(S):
    px, py = 700, 560
    S.draw(phone(px, py, 1.6), 0.0, 0.5)
    for k, lab in enumerate(("Japan trip", "Emergency", "New laptop")):
        y = py - 140 + k * 120
        at = S.c("name") - 0.3 + 0.35 * k
        S.draw([Fl(P_rect(px - 110, y - 40, 220, 88, 0, r=14), [HL, (214, 226, 196), PINK][k]), S_(P_rect(px - 110, y - 40, 220, 88, 4, r=14), 4.5)],
               S.c("pots") - 0.2 + 0.1 * k, 0.3, snd=None)
        S.text(lab, px, y + 18, 46, INK, at=at, anchor="m", path=HAND2)
    S.text("free.", 1150, 420, 120, ORANGE, at=S.c("free") - 0.1, rot=-6)
    S.text("give it a name.", 1000, 700, 84, INK, at=S.c("name") - 0.15, rot=-2)
    S.add(Fig(1730, 950, 1.15, at=0.0, poses=[("point_l", 0.3)], moods=[("smile", 0)], seed=3, flip=True))


# --------------------------------------------------------------------------- 6. fix big things once
@scene("c6a")
def _(S):
    S.draw(coffee(420, 600, 1.4), 0.0, 0.5)
    S.add(Fig(760, 930, 1.2, at=0.0, poses=[("stand", 0), ("sad", S.c("single") - 0.3)], moods=[("flat", 0), ("worried", S.c("willpower"))], seed=3))
    t0 = S.c("every", 0, 1) - 0.1
    for gk in range(10):                     # tally marks piling up: one per day
        x0, y0 = 1060 + (gk % 5) * 150, 300 + (gk // 5) * 230
        ops = [S_(P_line(x0 + m * 26, y0, x0 + m * 26 + 4, y0 + 150, 0.03, gk * 5 + m), 6) for m in range(4)]
        ops.append(S_(P_line(x0 - 14, y0 + 110, x0 + 110, y0 + 40, 0.03, gk), 6, RED))
        S.draw(ops, t0 + gk * 0.16, 0.18, snd="scr" if gk in (0, 6) else None)
    S.text("every. single. day.", 1050, 900, 80, GREY, at=S.c("single") - 0.3, rot=-2)


@scene("c6b")
def _(S):
    items = (("phone", "phone plan"), ("insurance", "insurance"), ("fees", "bank fees"), ("subscriptions", "subscriptions"))
    for k, (w_, lab) in enumerate(items):
        y = 260 + k * 150
        at = S.c(w_) - 0.15
        S.text(lab, 260, y, 92, INK, at=at)
        S.add(check(190, y - 30, 28, S.c("once") + 0.1 * k, GREEN, 9))
    S.text("1×", 1220, 560, 300, ORANGE, at=S.c("once") - 0.15, anchor="m", rot=-6, cps=8)
    S.add(circ(1230, 450, 190, 170, S.c("once") + 0.35, INK, 6.5))
    for k in range(6):
        S.pop(coin(1020 + k * 120, 880 + (k % 2) * 20, 0.45), S.c("month") + 0.12 * k, (1020 + k * 120, 880), snd="pop" if k == 0 else None)
    S.text("every month after", 1020, 1010, 62, GREY, at=S.c("month") + 0.1)


@scene("c6c")
def _(S):
    px, py = 560, 560
    S.draw(phone(px, py, 1.7), 0.0, 0.5)
    rows = 6
    for k in range(rows):
        y = py - 170 + k * 62
        S.draw([S_(P_line(px - 100, y, px + 30 + (k * 23) % 50, y, 0.02, k), 5, GREY), S_(P_line(px + 70, y, px + 110, y, 0.02, k + 9), 5)],
               S.c("scroll") - 0.2 + 0.08 * k, 0.2, snd=None)
    for k in (1, 3, 4):
        y = py - 170 + k * 62
        S.add(scribble_out(px - 110, y - 18, px + 120, y + 16, S.c("cancel") + 0.2 + 0.25 * (k > 1) + 0.25 * (k > 3), RED, 5, 0.3, seed=k))
    S.text("last 3 months", 980, 330, 90, INK, at=S.c("three") - 0.2)
    S.text("would I sign up\nagain today?", 980, 560, 96, ORANGE, at=S.c("sign") - 0.3, rot=-2)
    S.text("no? cancel.", 1080, 900, 86, RED, at=S.c("cancel") + 0.4, rot=-4)


@scene("c6d")
def _(S):
    S.draw(clock(470, 520, 1.5), 0.0, 0.5)
    S.text("1 boring hour", 280, 860, 86, INK, at=S.c("boring") - 0.2)
    S.text(">", 900, 640, 220, ORANGE, at=S.c("more") - 0.1, rot=4)
    for k in range(9):
        x, y = 1180 + (k % 3) * 190, 330 + (k // 3) * 220
        S.draw(coffee(x, y, 0.55), S.c("year") - 0.3 + 0.06 * k, 0.22, snd="scr" if k == 0 else None)
    S.text("a year of coffees", 1130, 1010, 70, GREY, at=S.c("coffees") - 0.4)


# --------------------------------------------------------------------------- 7. save your raise first
@scene("c7a")
def _(S):
    pts = [(220, 960)]
    for k in range(5):
        x, y = 220 + k * 300, 960 - k * 150
        pts += [(x + 300, y)] + ([(x + 300, y - 150)] if k < 4 else [])
    S.draw([S_(P_poly(pts), 7)], 0.0, 0.7)
    step_y = lambda X: 960 - 150 * clamp(math.floor((X - 220) / 300), 0, 4)
    S.add(Fig(370, 960, 0.85, at=0.0, poses=[("stand", 0)], moods=[("happy", 0)], seed=3,
              walk=(370, 1570, S.c("earn") - 0.2, S.c("out") + 0.6), yfn=step_y))
    S.text("earn more", 120, 260, 80, INK, at=S.c("earn") - 0.2)
    S.text("spend more", 160, 370, 80, RED, at=S.c("spend") - 0.2, rot=-2)
    S.draw(house(1180, 880, 0.6), S.c("flat") - 0.3, 0.4)
    S.draw(car(1560, 930, 0.6), S.c("car") - 0.3, 0.4)
    S.draw([S_(P_ell(1800, 700, 80, 26, 3, 0.1), 6), S_(P_line(1730, 700, 1870, 700, 0.01, 2), 4)], S.c("dinners") - 0.2, 0.3)
    S.add(hilite(150, 150 + text_w("lifestyle creep", 92), 575, 62, S.c("lifestyle", 1) - 0.1, seed=7))
    S.text("lifestyle creep", 150, 600, 92, INK, at=S.c("lifestyle", 1) - 0.1)


@scene("c7b")
def _(S):
    S.add(Fig(300, 920, 1.05, at=0.0, poses=[("stand", 0), ("point_up", S.c("fix") - 0.2)], moods=[("smile", 0)], kind="spiky", seed=11))
    S.add(Fig(560, 920, 1.05, at=0.0, poses=[("cross", 0)], moods=[("smile", 0)], kind="plain", seed=12, flip=True))
    S.text("Thaler & Benartzi", 150, 260, 66, GREY, at=S.c("thaler") - 0.1)
    S.add(hilite(830, 830 + text_w("Save More Tomorrow", 96), 200, 66, S.c("fix") - 0.1, seed=3))
    S.text("Save More Tomorrow", 830, 225, 96, INK, at=S.c("fix") - 0.1)
    S.text("future raises", 900, 360, 66, GREY, at=S.c("raises") - 0.3)
    k = 1
    S.add(*bars(950, 920, [3.5, 13.6], ["before", "40 months later"], S.c("rates", k) - 0.1, step=S.c("13.6%", k) - S.c("3.5%", k),
                maxh=400, bw=180, gap=240, cols=[PALE, ORANGE], txt=["3.5%", "13.6%"], seed=9, size=80))


@scene("c7c")
def _(S):
    S.pop(coin(960, 330, 1.5), S.c("raise") - 0.2, (960, 330))
    S.text("+ raise", 1060, 220, 70, GREEN, at=S.c("raise") - 0.1, rot=6)
    S.add(arrow(P_bez((900, 420), (760, 520), (620, 600)), S.c("half") - 0.1, INK, 6, 0.35))
    S.add(arrow(P_bez((1020, 420), (1160, 520), (1300, 600)), S.c("half") + 0.1, INK, 6, 0.35))
    S.draw(piggy(520, 760, 0.9), S.c("savings") - 0.3, 0.5)
    S.text("½", 610, 520, 120, ORANGE, at=S.c("half") + 0.1)
    S.text("½", 1240, 520, 120, INK, at=S.c("half") + 0.3)
    S.add(Fig(1420, 960, 1.05, at=0.0, poses=[("stand", 0), ("arms_up", S.c("half") + 0.4)], moods=[("smile", 0), ("happy", S.c("half") + 0.4)], seed=3))
    S.text("from month 1.", 980, 1010, 70, GREY, at=S.c("first") - 0.2)


# --------------------------------------------------------------------------- 8. meet your future self
@scene("c8a")
def _(S):
    S.add(Fig(420, 920, 1.3, at=0.0, poses=[("stand", 0)], moods=[("smile", 0), ("flat", S.c("stranger") - 0.2)], seed=3, look=0.5))
    S.add(Fig(1530, 760, 0.75, at=S.c("future") - 0.2, poses=[("old", 0)], moods=[("flat", 0)], kind="old", seed=21, enter="pop"))
    S.add(arrow(P_bez((620, 600), (1000, 520), (1400, 560)), S.c("future") + 0.2, GREY, 5, 0.6, dashed=True, head=20))
    S.text("you", 360, 1030, 70, INK, at=0.2)
    S.text("future you", 1420, 900, 62, GREY, at=S.c("future") + 0.1)
    S.text("stranger?", 860, 360, 110, ORANGE, at=S.c("stranger") - 0.2, rot=-4)


@scene("c8b")
def _(S):
    mx, my = 640, 520
    S.draw([Fl(P_ell(mx, my, 230, 300, 2, closed=True), (220, 230, 236)), S_(P_ell(mx, my, 230, 300, 5, 0.08), 9),
            S_(P_line(mx, my + 300, mx, my + 400, 0.01, 1), 8), S_(P_line(mx - 120, my + 400, mx + 120, my + 400, 0.02, 2), 8)], S.c("aged") - 0.6, 0.6)
    S.add(clip_ell(Fig(mx, my + 640, 2.4, at=S.c("aged") - 0.1, poses=[("old", 0)], moods=[("smile", 0)], kind="old", seed=22, enter="pop", idle=0.4),
                   mx, my, 222, 292))
    S.add(Dr([S_(P_ell(mx, my, 232, 302, 5, 0.08), 9)], S.c("aged"), 0.0, seed=33))
    S.text("×2", 1320, 560, 300, ORANGE, at=S.c("twice") - 0.1, anchor="m", rot=-6, cps=8)
    S.text("more saved", 1160, 760, 92, INK, at=S.c("twice") + 0.3)
    S.text("(in a lab test)", 1160, 860, 56, GREY, at=S.c("retirement") - 0.1)


@scene("c8c")
def _(S):
    S.add(Fig(700, 920, 1.3, at=0.0, poses=[("stand", 0)], moods=[("smile", 0), ("happy", S.c("today"))], seed=3, look=0.5))
    S.add(Fig(1200, 920, 1.3, at=0.0, poses=[("old", 0), ("wave", S.c("real") + 0.1)], moods=[("smile", 0), ("happy", S.c("real"))],
              kind="old", seed=22, look=-0.5))
    S.draw(bubble(1430, 320, 380, 170, tail=(-1, 1)), S.c("live") - 0.3, 0.3)
    S.text("thanks :)", 1430, 345, 92, INK, at=S.c("live") - 0.1, anchor="m")
    S.text("real.", 330, 300, 140, ORANGE, at=S.c("real") - 0.1, rot=-6)


@scene("c8d")
def _(S):
    cx, cy = 420, 560
    pil = np.vstack([P_bez((cx - 200, cy - 80), (cx, cy - 140), (cx + 200, cy - 80)), P_bez((cx + 200, cy - 80), (cx + 250, cy), (cx + 200, cy + 80)),
                     P_bez((cx + 200, cy + 80), (cx, cy + 140), (cx - 200, cy + 80)), P_bez((cx - 200, cy + 80), (cx - 250, cy), (cx - 200, cy - 80))])
    S.draw([Fl(pil, (150, 186, 214)), S_(pil, 7), S_(P_bez((cx - 60, cy - 20), (cx, cy + 10), (cx + 60, cy - 20)), 4)], S.c("cushion") - 0.3, 0.5)
    S.text("safety cushion", 220, 830, 82, INK, at=S.c("cushion") - 0.2)
    S.text("3–6 months", 260, 940, 72, ORANGE, at=S.c("three") - 0.1)
    S.add(arrow(P_bez((720, 560), (850, 480), (980, 560)), S.c("rest") - 0.2, INK, 6, 0.35))
    bx, by = 1340, 600
    bk = [S_(P_poly([(bx - 260, by - 120), (bx - 200, by + 160), (bx + 200, by + 160), (bx + 260, by - 120)], True), 7)]
    S.draw(bk, S.c("index", 1) - 0.5, 0.45)
    r = random.Random(4)
    for k in range(28):
        x = bx - 220 + (k % 7) * 70 + r.uniform(-8, 8)
        y = by - 90 + (k // 7) * 62 + r.uniform(-6, 6)
        col = [HL, PINK, (150, 186, 214), (214, 226, 196), ORANGE][k % 5]
        S.pop([Fl(P_rect(x - 24, y - 24, 48, 48, 0, r=6), col), S_(P_rect(x - 24, y - 24, 48, 48, 3, r=6), 3.5)], S.c("diversified", 1) + 0.04 * k,
              (x, y), snd=None)
    S.text("1 cheap index fund", 1040, 360, 84, INK, at=S.c("cheap", 1) - 0.1, rot=-2)
    S.text("every month, auto.", 1080, 900, 80, ORANGE, at=S.c("month", 1) - 0.1, rot=-2)


@scene("c8e")
def _(S):
    S.draw([S_(P_line(220, 900, 1700, 900, 0.005, 1), 6), S_(P_line(220, 900, 222, 180, 0.005, 2), 6)], 0.0, 0.4)
    xs = np.linspace(0, 1, 60)
    pts = np.stack([240 + xs * 1420, 880 - (np.exp(xs * 3.2) - 1) / (math.exp(3.2) - 1) * 640], 1)
    S.add(arrow(pts, 0.25, ORANGE, 9, 1.0, head=34))
    S.text("saving", 420, 830, 80, GREY, at=S.c("saving") - 0.1)
    S.text("building.", 700, 330, 130, INK, at=S.c("building") - 0.15, rot=-5)
    S.add(Fig(1480, 470, 0.6, at=S.c("building") + 0.1, poses=[("arms_up", 0)], moods=[("grin", 0)], seed=3, enter="pop"))


# --------------------------------------------------------------------------- final message
@scene("f0")
def _(S):
    S.text("final message.", 260, 600, 120, INK, at=0.05, rot=-3, cps=20)
    S.add(under(270, 980, 640, 1.0, ORANGE, 7, 0.4, wavy=True))


@scene("f1")
def _(S):
    S.text("being cheap", 300, 420, 130, INK, at=S.c("cheap") - 0.4)
    S.add(strike(280, 380, 1000, 372, S.c("cheap") + 0.35, RED, 10))
    S.text("willpower", 420, 720, 130, INK, at=S.c("willpower") - 0.3, rot=-2)
    S.add(strike(400, 680, 960, 674, S.c("willpower") + 0.45, RED, 10))
    S.add(Fig(1500, 940, 1.3, at=0.0, poses=[("stand", 0), ("shrug", S.c("willpower") - 0.2)], moods=[("smile", 0), ("smug", S.c("willpower"))],
              seed=3, flip=True))


@scene("f2")
def _(S):
    S.draw(calendar(260, 520, 0.7, day=28), 0.0, 0.4, snd=None)
    S.add(arrow(P_line(420, 520, 620, 520, 0.03, 1), S.c("system") - 0.4, INK, 6, 0.3))
    S.draw([Fl(P_rect(660, 330, 560, 380, 0, r=30), HL), S_(P_rect(660, 330, 560, 380, 8, r=30), 7.5)], S.c("system") - 0.25, 0.4)
    S.text("system", 940, 550, 120, INK, at=S.c("system"), anchor="m")
    for k, (cx, cy) in enumerate(((760, 650), (1120, 420))):
        S.draw([S_(P_ell(cx, cy, 36, 36, k, 0.1), 5)] + [S_(P_line(cx + 36 * math.cos(a), cy + 36 * math.sin(a), cx + 52 * math.cos(a), cy + 52 * math.sin(a), 0, j), 5)
                                                     for j, a in enumerate(np.linspace(0, 2 * math.pi, 8, endpoint=False))], S.c("hard") - 0.3 + 0.2 * k, 0.3, snd=None)
    S.add(arrow(P_line(1260, 520, 1440, 520, 0.03, 2), S.c("hard"), INK, 6, 0.3))
    S.draw(piggy(1650, 520, 0.75), S.c("part") - 0.1, 0.45)
    S.text("for you.", 1500, 820, 100, ORANGE, at=S.c("you") - 0.2, rot=-4)


@scene("f3")
def _(S):
    items = (("pay", "pay yourself first"), ("automatic", "make it automatic"), ("friction", "add friction"), ("wait", "wait 3 days"),
             ("name", "name your pots"), ("fix", "fix big things once"), ("raises", "save your raises"), ("remember", "meet future you"))
    for k, (w_, lab) in enumerate(items):
        col, row = k // 4, k % 4
        x, y = 200 + col * 860, 250 + row * 190
        at = S.c(w_) - 0.15
        S.text(f"{k + 1}.", x, y, 80, ORANGE, at=at - 0.05)
        S.text(lab, x + 90, y, 82, INK, at=at, cps=34)
        S.add(check(x + 110 + text_w(lab, 82) + 30, y - 30, 26, at + 0.55, GREEN, 9, seed=k))


@scene("f4")
def _(S):
    S.add(Fig(930, 835, 1.15, at=0.0, poses=[("lie", 0)], moods=[("sleep", 0)], seed=3, rot=-90, idle=0.3))
    S.draw([S_(P_rect(300, 860, 700, 60, 6, r=20), 7), S_(P_line(320, 920, 320, 1000, 0, 1), 7), S_(P_line(980, 920, 980, 1000, 0, 2), 7)], 0.0, 0.5)
    S.text("Z", 560, 700, 80, GREY, at=0.6, rot=-8)
    S.text("Z", 630, 610, 100, GREY, at=1.0, rot=-6)
    S.text("Z", 710, 500, 130, GREY, at=1.4, rot=-4)
    S.draw(piggy(1520, 700, 0.9), S.c("working") - 0.4, 0.5)
    for k in range(4):
        t0 = S.c("working") + 0.3 + k * 0.7
        S.add(Dr(coin(1490, 360, 0.42), t0, 0.0, pop=True, anchor=(1490, 360),
                 move=lambda tt: (0, min(1.0, tt / 0.45) ** 2 * 240, 0, 1), until=t0 + 0.45, seed=60 + k))


@scene("end")
def _(S):
    S.text("not financial advice. just education.", 200, 200, 58, GREY, at=S.c("education") - 0.2)
    sx, sy = 520, 600
    S.draw([Fl(P_rect(sx - 220, sy - 70, 440, 140, 0, r=26), ORANGE), S_(P_rect(sx - 220, sy - 70, 440, 140, 8, r=26), 7)], S.c("subscribe") - 0.3, 0.4)
    S.text("subscribe", sx, sy + 26, 92, INK, at=S.c("subscribe") - 0.1, anchor="m")
    vx, vy = 1350, 560
    S.draw([S_(P_rect(vx - 330, vy - 190, 660, 380, 8, r=12), 7)], S.c("next") - 0.2, 0.45)
    S.text("next:", vx - 320, vy - 220, 70, GREY, at=S.c("next") - 0.1)
    S.text("every ETF,\nexplained.", vx, vy - 10, 96, INK, at=S.c("etf") - 0.1, anchor="m")
    S.add(Fig(820, 980, 0.95, at=0.0, poses=[("stand", 0), ("point_r", S.c("next") + 0.1)], moods=[("smile", 0), ("happy", S.c("subscribe"))], seed=3))


# --------------------------------------------------------------------------- build all scenes
SC = []
for gk in range(len(GROUPS)):
    sc = Scene(gk)
    SCENES[sc.name](sc)
    SC.append(sc)
for gk, sc in enumerate(SC):                          # a slow push-in on some drawings, never the same twice
    r = random.Random(gk * 5 + 2)
    if sc.name[:2] in ("o4",):
        continue
    if r.random() < 0.38 and sc.dur > 3.5:
        sc.push(r.uniform(0.03, 0.075), W / 2 + r.uniform(-300, 300), H / 2 + r.uniform(-150, 150))
GSTART = [sc.t0 for sc in SC]
NF = sum(frames)
SFX_EVENTS = [ev for sc in SC for ev in sc.snd]


def overlay(ctx, t, fns=[]):
    """'not financial advice' scribbled small in a corner for the first seconds."""
    if not fns:
        fns.append(T("not financial advice · just education", 70, 70, 34, GREY, at=0.4, path=HAND2, cps=60))
    if t < starts[3]:
        fns[0](ctx, t)


def write_srt(path):
    """Captions as a separate .srt (YouTube CC), nothing burnt in; a caption never overlaps the next one."""
    def srt_time(t):
        ms = int(round(t * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    cues = [(part, a, b) for i in range(len(LINES)) for part, a, b in timed_chunks(i)]
    out = []
    for c, (part, a, b) in enumerate(cues):
        end = min(b + 0.05, cues[c + 1][1] - 0.02) if c + 1 < len(cues) else b + 0.05
        out.append(f"{c + 1}\n{srt_time(a)} --> {srt_time(end)}\n{part}\n")
    open(path, "w").write("\n".join(out))


def still(t, surf, paper, PW, PH):
    g = max(j for j in range(len(SC)) if GSTART[j] <= t + 1e-6)
    sc = SC[g]
    tl = t - sc.t0
    tq = math.floor(tl * STEP_FPS + 1e-6) / STEP_FPS
    ctx = cairo.Context(surf)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.save()
    sc.cam.apply(ctx, tl)
    ctx.set_source_surface(paper, (W - PW) / 2, (H - PH) / 2)
    ctx.paint()
    for fn in sc.els:
        fn(ctx, tq)
    ctx.restore()
    overlay(ctx, math.floor(t * STEP_FPS) / STEP_FPS)
    surf.flush()


if __name__ == "__main__" and os.environ.get("STILLS"):
    from PIL import Image
    paper, _parr, PW, PH = make_paper()
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ims = []
    for sc in SC:
        still(sc.t0 + sc.dur - 0.35, surf, paper, PW, PH)
        a_ = np.frombuffer(surf.get_data(), np.uint8).reshape(H, W, 4)[..., [2, 1, 0]].copy()
        ims.append(Image.fromarray(a_).resize((640, 360), Image.LANCZOS))
    cols = 4
    sheet = Image.new("RGB", (cols * 650, ((len(ims) + cols - 1) // cols) * 370), (90, 90, 90))
    for k, im in enumerate(ims):
        sheet.paste(im, ((k % cols) * 650 + 5, (k // cols) * 370 + 5))
    os.makedirs(os.path.join(D, "qa_save"), exist_ok=True)
    for p in range(0, len(ims), 16):
        sheet.crop((0, (p // cols) * 370, cols * 650, min(sheet.height, (p // cols + 4) * 370))).save(os.path.join(D, "qa_save", f"sheet_{p // 16}.png"))
    print("stills ok", len(SC), f"total={TOTAL:.1f}s")

if __name__ == "__main__" and not os.environ.get("STILLS"):
    SAMPLE = os.environ.get("SAMPLE")
    la, lb = (int(v) for v in SAMPLE.split(":")) if SAMPLE else (0, len(LINES))
    K0, K1 = round(starts[la] * FPS), (round(starts[lb] * FPS) if lb < len(LINES) else NF)
    paper, _parr, PW, PH = make_paper()
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    vid = os.path.join(E, "video.mp4" if not SAMPLE else "video_sample.mp4")
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    for k in range(K0, K1):
        t = k / FPS
        g = max(j for j in range(len(SC)) if GSTART[j] <= t + 1e-6)
        sc = SC[g]
        tl = t - sc.t0
        tq = math.floor(tl * STEP_FPS + 1e-6) / STEP_FPS
        ctx = cairo.Context(surf)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.save()
        sc.cam.apply(ctx, tl)
        ctx.set_source_surface(paper, (W - PW) / 2, (H - PH) / 2)
        ctx.paint()
        for fn in sc.els:
            fn(ctx, tq)
        ctx.restore()
        overlay(ctx, math.floor(t * STEP_FPS) / STEP_FPS)
        surf.flush()
        enc.stdin.write(bytes(surf.get_data()))
        if k % 600 == 0:
            print("frame", k, "/", NF, flush=True)
    enc.stdin.close()
    enc.wait()
    print("video ok", flush=True)

    # ----------------------------------------------------------------------- music: soft keys and a round bass, humanised; drops out on cue
    n = int(TOTAL * SR) + SR
    mus = np.zeros(n, np.float32)
    mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
    mr = np.random.default_rng(5)

    def keys(f, dur, vel):
        m = int(dur * SR)
        tt = np.arange(m) / SR
        x = (np.sin(2 * np.pi * f * tt) + 0.3 * np.exp(-tt / 0.35) * np.sin(4 * np.pi * f * tt)
             + 0.1 * np.exp(-tt / 0.12) * np.sin(6 * np.pi * f * tt) + 0.04 * np.exp(-tt / 0.04) * np.sin(2 * np.pi * 7.1 * f * tt))
        return (x * np.exp(-tt / 1.15) * (1 - np.exp(-tt / 0.006)) * (1 + 0.12 * np.sin(2 * np.pi * 4.3 * tt)) * vel).astype(np.float32)

    def bass(f, dur, vel):
        m = int(dur * SR)
        tt = np.arange(m) / SR
        return ((np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt / 0.55) * (1 - np.exp(-tt / 0.01)) * vel).astype(np.float32)

    def place(x, at):
        i0 = int(at * SR)
        if 0 <= i0 < n:
            mus[i0:i0 + len(x)] += x[: n - i0]

    PROG = [(53, 57, 60, 64), (52, 55, 59, 62), (50, 53, 57, 60), (48, 52, 55, 59)]
    ROOT = [41, 40, 38, 36]
    beat = 60 / 80
    bar = 4 * beat
    q_at = lambda txt: next(starts[j] for j, l in enumerate(LINES) if l["sub"].startswith(txt))
    hush = [(q_at("And here's the part"), q_at("It's not about") - 0.2), (q_at("Final message") - 0.05, q_at("Saving money isn't"))]
    tb, bi = 0.4, 0
    while tb < TOTAL:
        quiet = any(a - 0.2 <= tb < b for a, b in hush)
        if not quiet:
            ch, rt = PROG[bi % 4], ROOT[bi % 4]
            hj = lambda: mr.uniform(-0.014, 0.014)
            for j, m_ in enumerate(ch):
                place(keys(mtof(m_), 2.6, 0.16 * mr.uniform(0.8, 1.05)), tb + 0.012 * j + hj())
            if mr.random() < 0.85:
                for m_ in ch[2:]:
                    place(keys(mtof(m_), 1.6, 0.09 * mr.uniform(0.7, 1.0)), tb + 1.5 * beat + hj())
            if mr.random() < 0.55:
                place(keys(mtof(ch[mr.integers(1, 4)] + 12), 1.2, 0.07 * mr.uniform(0.7, 1.0)), tb + 3 * beat + hj())
            if bi >= 2:
                place(bass(mtof(rt), 1.4, 0.34), tb + hj())
                place(bass(mtof(rt), 1.0, 0.22), tb + 2 * beat + hj())
        tb += bar
        bi += 1
    tm = np.arange(n) / SR
    env = np.minimum(1, tm / 2.0) * np.clip((TOTAL - tm) / 2.5, 0, 1)
    for a, b in hush:                               # hard cut to silence, then the keys come back softly
        env[int(a * SR):int(b * SR)] = 0
        r0 = int(b * SR)
        env[r0:r0 + int(1.2 * SR)] *= np.linspace(0, 1, len(env[r0:r0 + int(1.2 * SR)]))
    mus *= env.astype(np.float32)
    a_, b_ = int((hush[1][0] - 0.7) * SR), int(hush[1][0] * SR)      # tape-stop into "Final message."
    seg = mus[a_:b_].copy()
    sp = np.linspace(1, 0, len(seg)) ** 1.3
    pos = np.cumsum(sp)
    pos -= pos[0]
    mus[a_:b_] = np.interp(pos, np.arange(len(seg)), seg) * np.linspace(1, 0.4, len(seg))
    mus /= max(1e-6, np.max(np.abs(mus)))
    write_wav(os.path.join(E, "music.wav"), mus[: int(TOTAL * SR)] * 0.6)

    # ----------------------------------------------------------------------- sfx: marker scribbles, soft pops, chapter thumps; most draws stay silent
    sfx = np.zeros(n, np.float32)
    sr_ = np.random.default_rng(13)

    def scribble(d):
        m = int(d * SR)
        tt = np.arange(m) / SR
        x = sr_.standard_normal(m)
        x = np.diff(x, prepend=0) * 0.6 + np.convolve(x, np.ones(3) / 3, "same") * 0.4
        strokes = np.abs(np.sin(2 * np.pi * sr_.uniform(5, 9) * tt + sr_.uniform(0, 3))) ** 0.7
        return (x * strokes * np.minimum(1, tt / 0.03) * np.clip((d - tt) / 0.08, 0, 1)).astype(np.float32)

    def pop_s():
        m = int(0.12 * SR)
        tt = np.arange(m) / SR
        f = 380 + 900 * tt / 0.12
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.03)).astype(np.float32)

    def thump():
        m = int(0.4 * SR)
        tt = np.arange(m) / SR
        return (np.sin(2 * np.pi * np.cumsum(70 + 60 * np.exp(-tt / 0.03)) / SR) * np.exp(-tt / 0.16)).astype(np.float32)

    def put(x, at, g):
        i0 = int(max(0, at) * SR)
        sfx[i0:i0 + len(x)] += (x * g)[: n - i0]

    for kind, at in SFX_EVENTS:
        r = sr_.random()
        if kind == "scr" and r < 0.42:
            put(scribble(sr_.uniform(0.25, 0.5)), at + sr_.uniform(0, 0.05), 0.05 * sr_.uniform(0.5, 1.0))
        elif kind == "pop" and r < 0.5:
            put(pop_s(), at, 0.06 * sr_.uniform(0.5, 1.0))
        elif kind == "thump" and r < 0.75:
            put(thump(), at, 0.35 * sr_.uniform(0.7, 1.0))
    write_wav(os.path.join(E, "sfx.wav"), sfx[: int(TOTAL * SR)])
    mix = os.path.join(E, "mix.wav")
    run(["ffmpeg", "-y", "-i", os.path.join(A, "voice.wav"), "-i", os.path.join(E, "music.wav"), "-i", os.path.join(E, "sfx.wav"), "-filter_complex",
         "[0:a]aformat=channel_layouts=stereo,highpass=f=90,acompressor=threshold=-20dB:ratio=3:attack=5:release=90,asplit=2[v1][v2];"
         "[1:a]aformat=channel_layouts=stereo,volume=0.3[m];[m][v1]sidechaincompress=threshold=0.02:ratio=3:attack=40:release=500[md];"
         "[2:a]aformat=channel_layouts=stereo,volume=0.6[fx];"
         "[v2][md][fx]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
         "-map", "[out]", "-ar", str(SR), mix])

    write_srt(os.path.join(E, "subtitles_en.srt"))

    final = os.path.join(O, "save_money_sample.mp4" if SAMPLE else "save_money_16x9.mp4")
    T0, T1 = K0 / FPS, K1 / FPS
    run(["ffmpeg", "-y", "-i", vid, "-ss", f"{T0:.3f}", "-t", f"{T1 - T0:.3f}", "-i", mix, "-vf", f"fade=t=out:st={T1 - T0 - 0.6:.2f}:d=0.6",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest", final])
    print(f"done total={TOTAL:.2f}s -> {final}")
