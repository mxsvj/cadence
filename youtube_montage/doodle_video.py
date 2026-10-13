"""Shared machinery for the doodle videos ('simple, actually' style): voice (Kokoro, cached per line), breathing between lines,
word cues, scenes grouped by drawing, chapter cards, render (cairo, 12 fps drawings, handheld camera), soft keys and sparse
sound effects, captions as a separate .srt.

A video file looks like:
    from doodle_video import *
    V = Video("compound", say={...}, keys=dict(prog=[...], bpm=80), hush=[("And here's", "It's")], tape="Final message")
    V.L("o1", "First line.")                      # group name = one drawing; consecutive lines in a group share it
    @V.scene("o1")
    def _(S): S.text("hello", 200, 300, at=S.c("first"))
    V.chapters({1: ("Title\\none.", 0), ...}, peek={1, 3})
    if __name__ == "__main__": V.main()
Run: python3 file.py | STILLS=1 python3 file.py (contact sheet) | SAMPLE=a:b python3 file.py (lines a..b-1)."""
import math
import os
import random
import re
import subprocess
import wave

import cairocffi as cairo
import numpy as np

from doodle import *          # noqa: F401,F403
from doodle import S as stk   # stroke op (scene code names its Scene argument S)

FPS, SR = 30, 44100
KOKORO_DIR = os.environ.get("KOKORO_DIR", os.path.join(D, "kokoro"))
_KOKORO = []
CHAP = re.compile(r"^c\d+$")


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def write_wav(path, data, ch=1):
    pcm = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "w") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def kokoro_say(text, path, voice="bf_emma", lang="en-gb", speed=0.95):
    if os.path.exists(path) and os.path.exists(path + ".txt") and open(path + ".txt").read() == text:
        return
    if not _KOKORO:
        from kokoro_onnx import Kokoro
        _KOKORO.append(Kokoro(os.path.join(KOKORO_DIR, "kokoro-v1.0.onnx"), os.path.join(KOKORO_DIR, "voices-v1.0.bin")))
    a, sr = _KOKORO[0].create(text, voice=voice, speed=speed, lang=lang)
    pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    open(path + ".txt", "w").write(text)


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


cl = lambda w: w.replace("*", "")


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


class Scene:
    def __init__(self, V, gk):
        self.V = V
        self.name, self.li = V.GROUPS[gk]
        self.t0 = V.starts[self.li[0]]
        self.dur = sum(V.frames[i] for i in self.li) / FPS
        self.els, self.snd = [], []
        self.rng = random.Random(gk * 97 + 1 + V.seed)
        self.cam = Camera(gk * 13 + 5 + V.seed, self.dur, push=0.0)

    def c(self, word, k=0, nth=0):
        return self.V.when(self.li[k], word, nth) - self.t0

    def l(self, k=0):
        return self.V.line_times[self.li[k]][0] - self.t0

    def e(self, k=0):
        return self.V.line_times[self.li[k]][1] - self.t0

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


def chapter(S, n, title, side, peek=True):
    """Number big in orange on one side, the title written next to it, never centred, never the same twice."""
    r = S.rng
    rot = r.uniform(-4, 3)
    if side == 0:
        nx, tx, anchor = 300 + r.randint(-30, 40), 640 + r.randint(-20, 30), "l"
    else:
        nx, tx, anchor = 1560 + r.randint(-40, 30), 1250 + r.randint(-30, 20), "r"
    ny = 640 + r.randint(-40, 30)
    S.add(T(str(n), nx, ny, 420, ORANGE, at=0.02, anchor="m", rot=rot, cps=6), snd="thump", at=0.02)
    S.add(circ(nx + 4, ny - 150, 175 + r.randint(-10, 10), 200 + r.randint(-10, 15), 0.3, INK, 6.5, 0.42, seed=n))
    words = title.split("\n")
    first = re.sub(r"[^\w€%'-]", "", title.split()[0]).lower()
    t_at = S.c(first) - 0.05
    ty = 520 + r.randint(-30, 20) - (len(words) - 1) * 60
    tf = S.text(title, tx, ty, 118, INK, at=t_at, anchor=anchor, rot=r.uniform(-2.5, 1.5), cps=30)
    x0 = tx if anchor == "l" else tx - tf.w
    S.add(under(x0 + 10, x0 + min(tf.w, 520), ty + (len(words) - 1) * 127 + 40, tf.end + 0.1, ORANGE, 8, 0.3, seed=n, wavy=n % 2 == 0))
    if peek:
        fx = (1650 if side == 0 else 280) + r.randint(-40, 40)
        S.add(Fig(fx, 1300, 1.3, at=0.25, poses=[("stand", 0), ("wave", 0.6)], moods=[("smile", 0), ("happy", 1.0)],
                  enter="pop", seed=n + 40, flip=side == 1))


def flow(S, items, y, at_list, x0=260, gap=520, hi=None, label_size=76):
    """A row of little drawings joined by arrows, each drawn on its word."""
    for k, ((ops_fn, label), at) in enumerate(zip(items, at_list)):
        x = x0 + k * gap
        S.draw(ops_fn(x, y), at - 0.1, 0.45)
        S.text(label, x, y + 210, label_size, ORANGE if hi == k else INK, at=at, anchor="m")
        if k:
            S.add(arrow(P_line(x - gap + 150, y, x - 160, y, 0.04, k), at - 0.25, INK, 6, 0.3))
        if hi == k:
            S.add(circ(x, y + 30, 190, 230, at + 0.35, ORANGE, 7))


def gift(x, y, s=1.0, col=(150, 186, 214)):
    return [Fl(P_rect(x - 90 * s, y - 70 * s, 180 * s, 140 * s, 0), col), stk(P_rect(x - 90 * s, y - 70 * s, 180 * s, 140 * s, 8 * s), 6.5 * s),
            stk(P_line(x, y - 70 * s, x, y + 70 * s, 0, 1), 5 * s), stk(P_bez((x, y - 70 * s), (x - 60 * s, y - 130 * s), (x - 70 * s, y - 70 * s)), 5 * s),
            stk(P_bez((x, y - 70 * s), (x + 60 * s, y - 130 * s), (x + 70 * s, y - 70 * s)), 5 * s)]


def heart(x, y, s=1.0, col=PINK):
    a = P_bez((x, y + 50 * s), (x - 90 * s, y - 10 * s), (x - 40 * s, y - 80 * s), (x, y - 30 * s))
    b = P_bez((x, y - 30 * s), (x + 40 * s, y - 80 * s), (x + 90 * s, y - 10 * s), (x, y + 50 * s))
    shape = np.vstack([a, b])
    return [Fl(shape, col), stk(shape, 6 * s)]


def tag(x, y, s=1.0, label="", col=HL, size=None):
    """Price tag with a hole and a string."""
    w, h = 230 * s, 120 * s
    pts = [(x - w / 2 + 40 * s, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2 + 40 * s, y + h / 2), (x - w / 2, y)]
    o = [Fl(P_poly(pts, True), col), stk(P_poly(pts, True), 6 * s), stk(P_ell(x - w / 2 + 34 * s, y, 9 * s, 9 * s, 2, 0.05), 4 * s),
         stk(P_bez((x - w / 2 + 26 * s, y), (x - w / 2 - 30 * s, y - 40 * s), (x - w / 2 - 50 * s, y - 80 * s)), 4 * s, GREY)]
    if label:
        o.append(("g", label, x + 18 * s, y + 22 * s, size or int(64 * s), INK, HAND, "m"))
    return o


def snowball(x, y, r, col=(236, 240, 246)):
    o = [Fl(P_ell(x, y, r, r * 0.96, 1, closed=True), col), stk(P_ell(x, y, r, r * 0.96, 3, 0.08), max(4.5, min(8, r / 14)))]
    rr = random.Random(int(r))
    for k in range(int(3 + r / 30)):
        a, d = rr.uniform(0, 6.28), rr.uniform(0.2, 0.75) * r
        cx, cy = x + d * math.cos(a), y + d * math.sin(a)
        o.append(stk(P_arc(cx, cy, r * 0.12, r * 0.08, rr.uniform(0, 180), rr.uniform(200, 320), 12), 3.5, GREY))
    return o


def hill(x0, y0, x1, y1):
    return stk(P_bez((x0, y0), ((x0 + x1) / 2, y0 + (y1 - y0) * 0.1), ((x0 + x1) / 2, y1 - (y1 - y0) * 0.05), (x1, y1), n=60), 7)


def money_bag(x, y, s=1.0, col=(214, 226, 196), label="€"):
    body = np.vstack([P_bez((x - 30 * s, y - 80 * s), (x - 150 * s, y - 20 * s), (x - 150 * s, y + 110 * s), (x, y + 110 * s)),
                      P_bez((x, y + 110 * s), (x + 150 * s, y + 110 * s), (x + 150 * s, y - 20 * s), (x + 30 * s, y - 80 * s))])
    return [Fl(body, col), stk(body, 7 * s), stk(P_poly([(x - 40 * s, y - 80 * s), (x - 60 * s, y - 120 * s), (x, y - 100 * s), (x + 60 * s, y - 120 * s), (x + 40 * s, y - 80 * s)]), 6 * s),
            stk(P_line(x - 40 * s, y - 80 * s, x + 40 * s, y - 80 * s, 0.05, 2), 6 * s), ("g", label, x, y + 60 * s, int(110 * s), INK, HAND, "m")]


def plant(x, y, s=1.0, leaves=3):
    o = [Fl(P_poly([(x - 60 * s, y - 70 * s), (x + 60 * s, y - 70 * s), (x + 45 * s, y + 40 * s), (x - 45 * s, y + 40 * s)], True), (214, 160, 120)),
         stk(P_poly([(x - 60 * s, y - 70 * s), (x + 60 * s, y - 70 * s), (x + 45 * s, y + 40 * s), (x - 45 * s, y + 40 * s)], True), 6 * s)]
    top = y - 70 * s - 40 * s * leaves
    o.append(stk(P_bez((x, y - 70 * s), (x - 10 * s, (y - 70 * s + top) / 2), (x + 8 * s, top)), 6 * s, GREEN))
    for k in range(leaves):
        ly = y - 100 * s - k * 40 * s
        sd = 1 if k % 2 else -1
        leaf = np.vstack([P_bez((x, ly), (x + sd * 30 * s, ly - 40 * s), (x + sd * 80 * s, ly - 30 * s)),
                          P_bez((x + sd * 80 * s, ly - 30 * s), (x + sd * 50 * s, ly + 10 * s), (x, ly))])
        o += [Fl(leaf, (170, 210, 160)), stk(leaf, 4.5 * s, GREEN)]
    return o


def laptop(x, y, s=1.0):
    return [Fl(P_rect(x - 170 * s, y - 220 * s, 340 * s, 210 * s, 0, r=10 * s), (250, 248, 242)),
            stk(P_rect(x - 170 * s, y - 220 * s, 340 * s, 210 * s, 8 * s, r=10 * s), 6.5 * s),
            stk(P_poly([(x - 210 * s, y), (x + 210 * s, y), (x + 180 * s, y - 10 * s), (x - 180 * s, y - 10 * s)], True), 6.5 * s)]


class Video:
    def __init__(self, slug, say=None, voice_speed=0.95, keys=None, hush=(), tape=None, seed=0, beat_groups=("o4",)):
        self.slug, self.SAY, self.speed, self.seed = slug, dict(say or {}), voice_speed, seed
        self.keys = dict(prog=[(53, 57, 60, 64), (52, 55, 59, 62), (50, 53, 57, 60), (48, 52, 55, 59)], roots=[41, 40, 38, 36], bpm=80)
        self.keys.update(keys or {})
        self.hush, self.tape, self.beat_groups = list(hush), tape, set(beat_groups)
        self.LINES, self.SCENES = [], {}
        self.A = os.path.join(D, f"assets_{slug}")
        self.E = os.path.join(D, f"sa_{slug}")
        self.O = os.path.join(D, "out")
        for p in (self.A, self.E, self.O, os.path.join(self.A, "voice")):
            os.makedirs(p, exist_ok=True)
        self.ready = False

    # ------------------------------------------------------------------ script
    def speak(self, sub):
        out = []
        for w in sub.split():
            core = w.rstrip(".,:;?!")
            out.append(self.SAY.get(core, core) + w[len(core):])
        return " ".join(out)

    def L(self, g, sub):
        self.LINES.append(dict(g=g, sub=sub))

    def scene(self, name):
        def deco(f):
            self.SCENES[name] = f
            return f
        return deco

    def chapters(self, CH, peek=()):
        for n, (title, side) in CH.items():
            def f(S, n=n, title=title, side=side):
                chapter(S, n, title, side, peek=n in peek)
            self.SCENES[f"c{n}"] = f

    # ------------------------------------------------------------------ voice, timing, cues
    def tts(self, i, text):
        raw, out = os.path.join(self.A, "voice", f"l{i:02d}_raw.wav"), os.path.join(self.A, "voice", f"l{i:02d}.wav")
        kokoro_say(text, raw, speed=self.speed)
        if not (os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(raw)):
            run(["ffmpeg", "-y", "-i", raw, "-af",
                 "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
                 "-ar", str(SR), "-ac", "1", out])
        with wave.open(out) as w:
            return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768

    def gap_for(self, i):
        rr = random.Random(i * 7919 + 3 + self.seed)
        L_ = self.LINES
        if i + 1 >= len(L_):
            return 0.0
        same = self.GI[i + 1] == self.GI[i]
        g = 0.42 if same else 0.78
        if CHAP.match(L_[i]["g"]):
            g = 0.95
        if CHAP.match(L_[i + 1]["g"]) or L_[i + 1]["g"] == "f0":
            g += 0.45
        if L_[i]["g"] in self.beat_groups or L_[i]["g"] == "f0":
            g += 0.5
        if len(L_[i]["sub"].split()) <= 5:
            g -= 0.08
        return max(0.3, g + rr.uniform(-0.12, 0.14))

    def prepare(self, lead=0.6, tail=3.2):
        if self.ready:
            return
        L_ = self.LINES
        for l in L_:
            l["tts"] = self.speak(l["sub"])
        self.GROUPS = []
        for i, l in enumerate(L_):
            if not self.GROUPS or self.GROUPS[-1][0] != l["g"]:
                self.GROUPS.append((l["g"], []))
            self.GROUPS[-1][1].append(i)
        self.GI = {i: gk for gk, (g, idx) in enumerate(self.GROUPS) for i in idx}
        self.voice = [self.tts(i, l["tts"]) for i, l in enumerate(L_)]
        self.frames, self.starts, t = [], [], 0.0
        for i, v in enumerate(self.voice):
            n = round((len(v) / SR + self.gap_for(i) + (lead if i == 0 else 0) + (tail if i == len(L_) - 1 else 0)) * FPS)
            self.starts.append(t)
            self.frames.append(n)
            t += n / FPS
        self.TOTAL = t
        NS = int(round(t * SR))
        vt = np.zeros(NS, dtype=np.float32)
        self.line_times = []
        for i, v in enumerate(self.voice):
            s0 = int(round((self.starts[i] + (lead if i == 0 else 0)) * SR))
            vt[s0:s0 + len(v)] += v[: max(0, NS - s0)]
            self.line_times.append((s0 / SR, s0 / SR + len(v) / SR))
        write_wav(os.path.join(self.A, "voice.wav"), vt)
        self.WT = [self.word_times(i) for i in range(len(L_))]
        self.SC = []
        for gk in range(len(self.GROUPS)):
            sc = Scene(self, gk)
            if sc.name not in self.SCENES:
                raise KeyError(f"no scene for group {sc.name}")
            self.SCENES[sc.name](sc)
            self.SC.append(sc)
        for gk, sc in enumerate(self.SC):                 # a slow push-in on some drawings, never the same twice
            r = random.Random(gk * 5 + 2 + self.seed)
            if sc.name in self.beat_groups:
                continue
            if r.random() < 0.38 and sc.dur > 3.5:
                sc.push(r.uniform(0.03, 0.075), W / 2 + r.uniform(-300, 300), H / 2 + r.uniform(-150, 150))
        self.GSTART = [sc.t0 for sc in self.SC]
        self.NF = sum(self.frames)
        self.ready = True

    def slen(self, w):
        k = cl(w).rstrip(".,:?!")
        return len(self.SAY.get(k, k)) + 1

    def timed_chunks(self, i):
        parts = chunks(self.LINES[i]["sub"])
        t0, t1 = self.line_times[i]
        lens = [sum(self.slen(w) for w in p.split()) for p in parts]
        ps = [t0 + p for p in pauses(self.voice[i])]
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

    def word_times(self, i):
        out = []
        for part, a, b in self.timed_chunks(i):
            ws = part.split()
            lens = [self.slen(w) for w in ws]
            t = a
            for w, n in zip(ws, lens):
                d = (b - a) * n / sum(lens)
                out.append((w, t, t + d))
                t += d
        return out

    def when(self, i, word, nth=0):
        hits = [a for w, a, b in self.WT[i] if cl(w).lower().strip("\"“”()").rstrip(".,:?!;)") == word.lower()]
        if len(hits) <= nth:
            raise KeyError(f"cue {word!r} not in line {i}: {self.LINES[i]['sub']}")
        return hits[nth]

    def q_at(self, txt):
        return next(self.starts[j] for j, l in enumerate(self.LINES) if l["sub"].startswith(txt))

    # ------------------------------------------------------------------ outputs
    def write_srt(self, path):
        def stamp(t):
            ms = int(round(t * 1000))
            return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
        cues = [(part, a, b) for i in range(len(self.LINES)) for part, a, b in self.timed_chunks(i)]
        out = []
        for c, (part, a, b) in enumerate(cues):
            end = min(b + 0.05, cues[c + 1][1] - 0.02) if c + 1 < len(cues) else b + 0.05
            out.append(f"{c + 1}\n{stamp(a)} --> {stamp(end)}\n{part}\n")
        open(path, "w").write("\n".join(out))

    def _overlay(self, ctx, t):
        if not hasattr(self, "_nfa"):
            self._nfa = T("not financial advice · just education", 70, 70, 34, GREY, at=0.4, path=HAND2, cps=60)
        if t < self.starts[min(3, len(self.starts) - 1)]:
            self._nfa(ctx, t)

    def frame(self, surf, paper, PW, PH, t):
        g = max(j for j in range(len(self.SC)) if self.GSTART[j] <= t + 1e-6)
        sc = self.SC[g]
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
        self._overlay(ctx, math.floor(t * STEP_FPS) / STEP_FPS)
        surf.flush()

    def stills(self):
        from PIL import Image
        paper, _parr, PW, PH = make_paper(seed=3 + self.seed)
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
        ims = []
        for sc in self.SC:
            self.frame(surf, paper, PW, PH, sc.t0 + sc.dur - 0.35)
            a_ = np.frombuffer(surf.get_data(), np.uint8).reshape(H, W, 4)[..., [2, 1, 0]].copy()
            ims.append(Image.fromarray(a_).resize((640, 360), Image.LANCZOS))
        cols = 4
        sheet = Image.new("RGB", (cols * 650, ((len(ims) + cols - 1) // cols) * 370), (90, 90, 90))
        for k, im in enumerate(ims):
            sheet.paste(im, ((k % cols) * 650 + 5, (k // cols) * 370 + 5))
        qd = os.path.join(D, f"qa_{self.slug}")
        os.makedirs(qd, exist_ok=True)
        for p in range(0, len(ims), 16):
            sheet.crop((0, (p // cols) * 370, cols * 650, min(sheet.height, (p // cols + 4) * 370))).save(os.path.join(qd, f"sheet_{p // 16}.png"))
        print("stills ok", len(self.SC), f"total={self.TOTAL:.1f}s", flush=True)

    def music(self):
        n = int(self.TOTAL * SR) + SR
        mus = np.zeros(n, np.float32)
        mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
        mr = np.random.default_rng(5 + self.seed)

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

        PROG, ROOT, bpm = self.keys["prog"], self.keys["roots"], self.keys["bpm"]
        beat = 60 / bpm
        bar = 4 * beat
        hush = [(self.q_at(a) - 0.05, self.q_at(b) - 0.2) for a, b in self.hush]
        if self.tape:
            hush.append((self.q_at(self.tape) - 0.05, self.starts[self.LINES.index(next(l for l in self.LINES if l["sub"].startswith(self.tape))) + 1]))
        tb, bi = 0.4, 0
        while tb < self.TOTAL:
            if not any(a - 0.2 <= tb < b for a, b in hush):
                ch, rt = PROG[bi % len(PROG)], ROOT[bi % len(ROOT)]
                hj = lambda: mr.uniform(-0.014, 0.014)
                for j, m_ in enumerate(ch):
                    place(keys(mtof(m_), 2.6, 0.16 * mr.uniform(0.8, 1.05)), tb + 0.012 * j + hj())
                if mr.random() < 0.85:
                    for m_ in ch[2:]:
                        place(keys(mtof(m_), 1.6, 0.09 * mr.uniform(0.7, 1.0)), tb + 1.5 * beat + hj())
                if mr.random() < 0.55:
                    place(keys(mtof(ch[mr.integers(1, len(ch))] + 12), 1.2, 0.07 * mr.uniform(0.7, 1.0)), tb + 3 * beat + hj())
                if bi >= 2:
                    place(bass(mtof(rt), 1.4, 0.34), tb + hj())
                    place(bass(mtof(rt), 1.0, 0.22), tb + 2 * beat + hj())
            tb += bar
            bi += 1
        tm = np.arange(n) / SR
        env = np.minimum(1, tm / 2.0) * np.clip((self.TOTAL - tm) / 2.5, 0, 1)
        for a, b in hush:
            env[int(a * SR):int(b * SR)] = 0
            r0 = int(b * SR)
            env[r0:r0 + int(1.2 * SR)] *= np.linspace(0, 1, len(env[r0:r0 + int(1.2 * SR)]))
        mus *= env.astype(np.float32)
        if self.tape:
            a_, b_ = int((hush[-1][0] - 0.7) * SR), int(hush[-1][0] * SR)
            seg = mus[a_:b_].copy()
            pos = np.cumsum(np.linspace(1, 0, len(seg)) ** 1.3)
            pos -= pos[0]
            mus[a_:b_] = np.interp(pos, np.arange(len(seg)), seg) * np.linspace(1, 0.4, len(seg))
        mus /= max(1e-6, np.max(np.abs(mus)))
        write_wav(os.path.join(self.E, "music.wav"), mus[: int(self.TOTAL * SR)] * 0.6)

    def sfx(self):
        n = int(self.TOTAL * SR) + SR
        sfx = np.zeros(n, np.float32)
        sr_ = np.random.default_rng(13 + self.seed)

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
            return (np.sin(2 * np.pi * np.cumsum(380 + 900 * tt / 0.12) / SR) * np.exp(-tt / 0.03)).astype(np.float32)

        def thump():
            m = int(0.4 * SR)
            tt = np.arange(m) / SR
            return (np.sin(2 * np.pi * np.cumsum(70 + 60 * np.exp(-tt / 0.03)) / SR) * np.exp(-tt / 0.16)).astype(np.float32)

        def put(x, at, g):
            i0 = int(max(0, at) * SR)
            sfx[i0:i0 + len(x)] += (x * g)[: n - i0]

        for kind, at in [ev for sc in self.SC for ev in sc.snd]:
            r = sr_.random()
            if kind == "scr" and r < 0.42:
                put(scribble(sr_.uniform(0.25, 0.5)), at + sr_.uniform(0, 0.05), 0.05 * sr_.uniform(0.5, 1.0))
            elif kind == "pop" and r < 0.5:
                put(pop_s(), at, 0.06 * sr_.uniform(0.5, 1.0))
            elif kind == "thump" and r < 0.75:
                put(thump(), at, 0.35 * sr_.uniform(0.7, 1.0))
        write_wav(os.path.join(self.E, "sfx.wav"), sfx[: int(self.TOTAL * SR)])

    def render(self, sample=None):
        la, lb = sample or (0, len(self.LINES))
        K0, K1 = round(self.starts[la] * FPS), (round(self.starts[lb] * FPS) if lb < len(self.LINES) else self.NF)
        paper, _parr, PW, PH = make_paper(seed=3 + self.seed)
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
        vid = os.path.join(self.E, "video_sample.mp4" if sample else "video.mp4")
        enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
        for k in range(K0, K1):
            self.frame(surf, paper, PW, PH, k / FPS)
            enc.stdin.write(bytes(surf.get_data()))
            if k % 600 == 0:
                print("frame", k, "/", self.NF, flush=True)
        enc.stdin.close()
        enc.wait()
        print("video ok", flush=True)
        self.music()
        self.sfx()
        mix = os.path.join(self.E, "mix.wav")
        run(["ffmpeg", "-y", "-i", os.path.join(self.A, "voice.wav"), "-i", os.path.join(self.E, "music.wav"), "-i", os.path.join(self.E, "sfx.wav"),
             "-filter_complex",
             "[0:a]aformat=channel_layouts=stereo,highpass=f=90,acompressor=threshold=-20dB:ratio=3:attack=5:release=90,asplit=2[v1][v2];"
             "[1:a]aformat=channel_layouts=stereo,volume=0.3[m];[m][v1]sidechaincompress=threshold=0.02:ratio=3:attack=40:release=500[md];"
             "[2:a]aformat=channel_layouts=stereo,volume=0.6[fx];"
             "[v2][md][fx]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
             "-map", "[out]", "-ar", str(SR), mix])
        self.write_srt(os.path.join(self.E, "subtitles_en.srt"))
        final = os.path.join(self.O, f"{self.slug}_sample.mp4" if sample else f"{self.slug}_16x9.mp4")
        T0, T1 = K0 / FPS, K1 / FPS
        run(["ffmpeg", "-y", "-i", vid, "-ss", f"{T0:.3f}", "-t", f"{T1 - T0:.3f}", "-i", mix, "-vf", f"fade=t=out:st={T1 - T0 - 0.6:.2f}:d=0.6",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
             "-movflags", "+faststart", "-shortest", final])
        print(f"done total={self.TOTAL:.2f}s -> {final}", flush=True)

    def main(self):
        self.prepare()
        if os.environ.get("STILLS"):
            self.stills()
            return
        s = os.environ.get("SAMPLE")
        self.render(tuple(int(v) for v in s.split(":")) if s else None)
