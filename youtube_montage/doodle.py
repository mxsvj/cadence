"""Doodle engine for the 'simple, actually' look: hand-drawn marker strokes on cream paper (cairo, anti-aliased),
line boil (each line is redrawn 3 slightly different ways and cycled 8 times a second, like hand animation),
handwritten lettering written on letter by letter, a stick figure with poses and faces, and a small prop library.
Everything that moves is stepped at 12 fps; only the handheld camera runs at the full frame rate."""
import math
import os
import random

import cairocffi as cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080
D = os.path.dirname(os.path.abspath(__file__))
FH = os.path.join(D, "fonts_hand")
HAND = os.path.join(FH, "GochiHand-Regular.ttf")          # marker lettering (has €)
HAND2 = os.path.join(FH, "PatrickHand-Regular.ttf")       # smaller notes and labels
ONE = os.path.join(FH, "CaveatBrush-Regular.ttf")         # Gochi's "1" reads like a 7: borrow a plainer one
PAPER = (244, 240, 231)
INK = (35, 32, 30)
ORANGE = (234, 126, 34)
HL = (251, 211, 156)          # highlighter
PINK = (240, 186, 180)
GREY = (160, 154, 144)
PALE = (226, 219, 205)
RED = (192, 64, 50)
GREEN = (78, 146, 92)
BOIL_FPS, STEP_FPS = 8, 12

clamp = lambda x, a=0.0, b=1.0: max(a, min(b, x))
ease_out = lambda u: 1 - (1 - u) ** 3
ease_io = lambda u: u * u * (3 - 2 * u)


def ease_back(u, s=1.6):
    u -= 1
    return 1 + (s + 1) * u ** 3 + s * u ** 2


def rgb(c, a=1.0):
    return (c[0] / 255, c[1] / 255, c[2] / 255, a)


def boil(t):
    return int(t * BOIL_FPS + 1e-6) % 3


# --------------------------------------------------------------------------- paths: wobbly, boiling, drawable in part
def _wave(s, rng, amp, wl):
    out = np.zeros_like(s)
    for a, k in ((1.0, 1.0), (0.55, 0.43), (0.3, 0.19)):
        out += a * np.sin(2 * np.pi * s / (wl * k * rng.uniform(0.8, 1.25)) + rng.uniform(0, 6.283))
    return amp * out / 1.85


class Path:
    __slots__ = ("p", "s", "L", "n", "seed")

    def __init__(self, pts, seed=0, wob=1.5, step=4.0):
        pts = np.asarray(pts, float)
        seg = np.hypot(*np.diff(pts, axis=0).T) if len(pts) > 1 else np.zeros(0)
        cum = np.concatenate([[0.0], np.cumsum(seg)])
        L = max(cum[-1], 1e-6)
        n = max(2, int(L / step) + 1)
        s = np.linspace(0, L, n)
        p = np.stack([np.interp(s, cum, pts[:, 0]), np.interp(s, cum, pts[:, 1])], 1)
        d = np.gradient(p, axis=0)
        nr = np.stack([-d[:, 1], d[:, 0]], 1)
        nr /= np.linalg.norm(nr, axis=1, keepdims=True) + 1e-9
        rng = np.random.default_rng(seed)
        self.p = p + nr * _wave(s, rng, wob * min(1.0, L / 60), 240)[:, None]
        self.s, self.L, self.n, self.seed = s, L, nr, seed

    def at(self, b, amp=1.0):
        if amp <= 0:
            return self.p
        rng = np.random.default_rng(self.seed * 7 + b * 101 + 5)
        return self.p + self.n * _wave(self.s, rng, amp * min(1.0, self.L / 40), 70)[:, None]


def _trace(ctx, q):
    ctx.new_path()
    ctx.move_to(*q[0])
    for x, y in q[1:]:
        ctx.line_to(x, y)


def stroke(ctx, path, b, w, col, frac=1.0, amp=1.0, a=1.0):
    q = path.at(b, amp)
    if frac < 1:
        m = int(np.searchsorted(path.s, frac * path.L))
        if m < 1:
            return
        q = q[:m + 1]
    _trace(ctx, q)
    ctx.set_source_rgba(*rgb(col, a))
    ctx.set_line_width(w * (1 + 0.05 * (b - 1)))
    ctx.stroke()


def fill(ctx, path, b, col, a=1.0, off=(0, 0), amp=0.6):
    q = path.at(b, amp) + np.asarray(off, float)
    _trace(ctx, q)
    ctx.close_path()
    ctx.set_source_rgba(*rgb(col, a))
    ctx.fill()


# --------------------------------------------------------------------------- shape points
def P_line(x0, y0, x1, y1, bow=0.02, seed=0):
    r = random.Random(seed)
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) + 1e-9
    k = bow * L * r.uniform(-1, 1)
    cx, cy = (x0 + x1) / 2 - dy / L * k, (y0 + y1) / 2 + dx / L * k
    t = np.linspace(0, 1, max(8, int(L / 6)))[:, None]
    return (1 - t) ** 2 * np.array([x0, y0]) + 2 * (1 - t) * t * np.array([cx, cy]) + t ** 2 * np.array([x1, y1])


def P_ell(cx, cy, rx, ry, seed=0, over=0.1, a0=None, closed=False):
    r = random.Random(seed)
    a0 = r.uniform(0, 6.283) if a0 is None else math.radians(a0)
    t = np.linspace(0, 1, 160)
    if closed:
        ang = a0 + 2 * np.pi * t
        rm = 1 + 0.025 * np.sin(2 * ang + r.uniform(0, 6.28))
    else:
        ang = a0 + 2 * np.pi * (1 + over) * t
        rm = 1 + 0.03 * np.sin(2 * ang + r.uniform(0, 6.28)) + 0.04 * (t - 0.5)
    return np.stack([cx + rx * rm * np.cos(ang), cy + ry * rm * np.sin(ang)], 1)


def P_arc(cx, cy, rx, ry, a0, a1, n=40):
    a = np.radians(np.linspace(a0, a1, n))
    return np.stack([cx + rx * np.cos(a), cy + ry * np.sin(a)], 1)


def P_rect(x, y, w, h, over=8, r=0):
    if r <= 0:
        pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y), (x + over, y - 1)]
        return np.array(pts, float)
    pts = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        pts += list(P_arc(cx, cy, r, r, a0, a0 + 90, 8))
    pts.append(pts[0])
    pts.append((pts[0][0] + over, pts[0][1]))
    return np.array(pts, float)


def P_poly(pts, closed=False):
    pts = [tuple(p) for p in pts]
    return np.array(pts + ([pts[0]] if closed else []), float)


def P_bez(*c, n=40):
    c = [np.array(p, float) for p in c]
    t = np.linspace(0, 1, n)[:, None]
    if len(c) == 3:
        return (1 - t) ** 2 * c[0] + 2 * (1 - t) * t * c[1] + t ** 2 * c[2]
    return (1 - t) ** 3 * c[0] + 3 * (1 - t) ** 2 * t * c[1] + 3 * (1 - t) * t ** 2 * c[2] + t ** 3 * c[3]


def P_wave(x0, x1, y, amp=6, wl=60):
    x = np.linspace(x0, x1, max(10, int(abs(x1 - x0) / 5)))
    return np.stack([x, y + amp * np.sin((x - x0) / wl * 2 * np.pi)], 1)


def arrow_pts(pts, head=26):
    """Shaft plus two head strokes along the end tangent."""
    pts = np.asarray(pts, float)
    e, p = pts[-1], pts[max(0, len(pts) - 4)]
    a = math.atan2(e[1] - p[1], e[0] - p[0])
    h1 = (e[0] - head * math.cos(a - 0.5), e[1] - head * math.sin(a - 0.5))
    h2 = (e[0] - head * math.cos(a + 0.5), e[1] - head * math.sin(a + 0.5))
    return [pts, np.array([h1, e]), np.array([h2, e])]


# --------------------------------------------------------------------------- lettering
_FONTS, _GLY = {}, {}
_GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"


def ensure_fonts():
    """The three handwriting fonts are free (SIL Open Font License): fetch them from Google Fonts the first time."""
    import urllib.request
    os.makedirs(FH, exist_ok=True)
    for path, sub in ((HAND, "gochihand/"), (HAND2, "patrickhand/"), (ONE, "caveatbrush/")):
        if not os.path.exists(path):
            urllib.request.urlretrieve(_GF + sub + os.path.basename(path), path)


ensure_fonts()


def font(path, size):
    k = (path, int(size))
    if k not in _FONTS:
        _FONTS[k] = ImageFont.truetype(path, int(size))
    return _FONTS[k]


def glyph(ch, size, col, path=HAND):
    key = (ch, int(size), col, path)
    if key in _GLY:
        return _GLY[key]
    f = font(ONE, size * 1.04) if (ch == "1" and path == HAND) else font(path, size)
    x0, y0, x1, y1 = f.getbbox(ch, anchor="ls")
    pad = 4
    w, h = max(1, x1 - x0 + 2 * pad), max(1, y1 - y0 + 2 * pad)
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).text((pad - x0, pad - y0), ch, font=f, fill=255, anchor="ls")
    a = np.asarray(im, np.uint16)
    arr = np.empty((h, w, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3] = a * col[2] // 255, a * col[1] // 255, a * col[0] // 255, a
    surf = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_ARGB32, w, h, w * 4)
    _GLY[key] = (surf, pad - x0, pad - y0, arr)
    return _GLY[key]


def text_w(text, size, path=HAND):
    return max(font(path, size).getlength(ln) for ln in text.split("\n"))


def T(text, x, y, size=96, col=INK, at=0.0, cps=24, dur=None, anchor="l", rot=0.0, path=HAND, seed=None, lh=1.08,
      until=None, a=1.0, move=None):
    """Handwritten text written on letter by letter from `at` (y = baseline of the first line)."""
    seed = (sum(map(ord, text)) * 13 + int(x) + int(y)) if seed is None else seed
    f = font(path, size)
    lines = text.split("\n")
    widths = [f.getlength(ln) for ln in lines]
    lay = [(ch, f.getlength(ln[:i]), li) for li, ln in enumerate(lines) for i, ch in enumerate(ln)]
    r = random.Random(seed)
    times, tt = [], 0.0
    for ch, _, _ in lay:
        times.append(tt)
        tt += (0.3 if ch == " " else r.uniform(0.6, 1.5)) / cps
    if dur:
        times = [v * dur / max(tt, 1e-6) for v in times]
    drift = [(r.uniform(-1, 1) * size * 0.025, r.uniform(0, 6.28), r.uniform(-1.2, 1.2)) for _ in lines]

    def fn(ctx, t):
        if t < at or (until is not None and t >= until):
            return
        b = boil(t)
        ctx.save()
        ctx.translate(x, y)
        if move:
            dx, dy = move(t - at)
            ctx.translate(dx, dy)
        ctx.rotate(math.radians(rot))
        for k, (ch, lx, li) in enumerate(lay):
            te = t - at - times[k]
            if te < 0:
                break
            if ch == " ":
                continue
            ox = -widths[li] / 2 if anchor == "m" else (-widths[li] if anchor == "r" else 0)
            amp, ph, tilt = drift[li]
            px = ox + lx
            py = li * size * lh + amp * math.sin(px / max(widths[li], 1) * 3.1 + ph) + tilt * px / 100
            rr = random.Random(seed * 31 + k * 7 + b)
            jx, jy, jr = rr.uniform(-0.9, 0.9), rr.uniform(-0.9, 0.9), rr.uniform(-0.018, 0.018)
            sc = 1.0 if te >= 1 / STEP_FPS else 0.82
            surf, gx, gy, _ = glyph(ch, size, col, path)
            ctx.save()
            ctx.translate(px + jx, py + jy)
            ctx.rotate(jr)
            ctx.scale(sc, sc)
            ctx.set_source_surface(surf, -gx, -gy)
            ctx.paint_with_alpha(a)
            ctx.restore()
        ctx.restore()

    fn.end = at + (times[-1] if times else 0)
    fn.w = max(widths)
    return fn


# --------------------------------------------------------------------------- drawings: strokes + fills + glyphs, drawn on or popped in
def Dr(ops, at, dur=0.5, pop=False, anchor=(W / 2, H / 2), until=None, move=None, seed=0, amp=1.0, a=1.0, fill_delay=0.55):
    """ops: ("s", pts, width, colour) strokes, ("f", pts, colour) fills (painted slightly off the outline, like a quick colour pass),
    ("dot", x, y, r, colour), ("g", text, x, y, size, colour[, path, anchor]) glyphs."""
    items = []
    for k, op in enumerate(ops):
        if op[0] == "s":
            items.append(("s", Path(op[1], seed * 53 + k), op[2], op[3]))
        elif op[0] == "f":
            rr = random.Random(seed * 17 + k)
            items.append(("f", Path(op[1], seed * 53 + k, wob=0.8), op[2], (rr.uniform(-6, 6), rr.uniform(-5, 5))))
        else:
            items.append(op)
    total = sum(it[1].L for it in items if it[0] == "s") or 1.0
    texts = [T(op[1], op[2], op[3], op[4], op[5], at=at + dur * 0.6, cps=40, path=op[6] if len(op) > 6 else HAND,
               anchor=op[7] if len(op) > 7 else "m", seed=seed * 3 + k) for k, op in enumerate(ops) if op[0] == "g"]

    def fn(ctx, t):
        if t < at or (until is not None and t >= until):
            return
        u = clamp((t - at) / dur) if dur > 0 else 1.0
        b = boil(t)
        ctx.save()
        if move:
            dx, dy, rot, sc = move(t - at)
            ctx.translate(anchor[0] + dx, anchor[1] + dy)
            ctx.rotate(rot)
            ctx.scale(sc, sc)
            ctx.translate(-anchor[0], -anchor[1])
        if pop:
            sc = ease_back(clamp((t - at) / 0.25)) if t - at < 0.25 else 1.0
            sc = max(sc, 0.05)
            ctx.translate(anchor[0], anchor[1])
            ctx.scale(sc, sc)
            ctx.translate(-anchor[0], -anchor[1])
            u = 1.0
        fa = clamp((u - fill_delay) / 0.2) if not pop else 1.0
        if fa > 0:
            for it in items:
                if it[0] == "f":
                    fill(ctx, it[1], b, it[2], a * fa, it[3])
        rem = ease_out(u) * total
        for it in items:
            if it[0] == "s":
                fr = clamp(rem / it[1].L)
                rem -= it[1].L
                if fr > 0:
                    stroke(ctx, it[1], b, it[2], it[3], fr, amp, a)
            elif it[0] == "dot" and u > 0.5:
                ctx.new_path()
                ctx.arc(it[1], it[2], it[3], 0, 2 * math.pi)
                ctx.set_source_rgba(*rgb(it[4], a))
                ctx.fill()
        for tf in texts:
            tf(ctx, t if not pop else max(t, tf.end))
        ctx.restore()

    return fn


def S(pts, w=6.5, col=INK):
    return ("s", pts, w, col)


def Fl(pts, col):
    return ("f", pts, col)


# quick marks
def under(x0, x1, y, at, col=ORANGE, w=7, dur=0.3, seed=0, wavy=False):
    pts = P_wave(x0, x1, y, 5, 70) if wavy else P_line(x0, y + 3, x1, y - 4, 0.04, seed)
    return Dr([S(pts, w, col)], at, dur, seed=seed)


def circ(cx, cy, rx, ry, at, col=ORANGE, w=7, dur=0.38, seed=0):
    return Dr([S(P_ell(cx, cy, rx, ry, seed, 0.14), w, col)], at, dur, seed=seed)


def hilite(x0, x1, y, h, at, col=HL, dur=0.3, seed=0):
    r = random.Random(seed)
    pts = P_line(x0 - 8, y + r.uniform(-3, 3), x1 + 8, y + r.uniform(-6, 4), 0.01, seed)
    return Dr([S(pts, h, col)], at, dur, seed=seed, amp=0.4)


def strike(x0, y0, x1, y1, at, col=RED, w=8, dur=0.22, seed=0):
    return Dr([S(P_line(x0, y0, x1, y1, 0.03, seed), w, col)], at, dur, seed=seed)


def cross(cx, cy, r, at, col=RED, w=9, dur=0.3, seed=0):
    return Dr([S(P_line(cx - r, cy - r, cx + r, cy + r, 0.04, seed), w, col),
               S(P_line(cx + r, cy - r * 0.9, cx - r * 1.05, cy + r, 0.04, seed + 1), w, col)], at, dur, seed=seed)


def check(cx, cy, r, at, col=GREEN, w=10, dur=0.25, seed=0):
    return Dr([S(P_poly([(cx - r, cy), (cx - r * 0.25, cy + r * 0.75), (cx + r * 1.1, cy - r * 0.9)]), w, col)], at, dur, seed=seed)


def scribble_out(x0, y0, x1, y1, at, col=INK, w=6, dur=0.45, seed=0):
    r = random.Random(seed)
    n = max(4, int((x1 - x0) / 34))
    pts = []
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n + r.uniform(-6, 6)
        pts.append((x, y1 + r.uniform(-6, 6)) if k % 2 else (x, y0 + r.uniform(-6, 6)))
    return Dr([S(P_poly(pts), w, col)], at, dur, seed=seed)


def arrow(pts, at, col=INK, w=6.5, dur=0.4, seed=0, head=26, dashed=False):
    parts = arrow_pts(pts, head)
    if dashed:
        sh = Path(parts[0], seed)
        segs, k = [], 0
        while k < len(sh.p) - 1:
            segs.append(sh.p[k:k + 5])
            k += 9
        parts = segs + parts[1:]
    return Dr([S(p, w, col) for p in parts], at, dur, seed=seed)


# --------------------------------------------------------------------------- stick figure
POSES = {
    "stand": dict(la=(-24, -13), ra=(24, 13), ll=(-10, -5), rl=(10, 5), lean=0, tilt=0),
    "relax": dict(la=(-10, -4), ra=(12, 4), ll=(-8, -4), rl=(9, 4), lean=-2, tilt=-4),
    "wave": dict(la=(-16, -8), ra=(120, 165), ll=(-10, -5), rl=(10, 5), lean=0, tilt=-5),
    "point_r": dict(la=(-14, -6), ra=(78, 84), ll=(-10, -5), rl=(10, 5), lean=2, tilt=4),
    "point_l": dict(la=(-78, -84), ra=(14, 6), ll=(-10, -5), rl=(10, 5), lean=-2, tilt=-4),
    "point_up": dict(la=(-14, -6), ra=(150, 172), ll=(-10, -5), rl=(10, 5), lean=0, tilt=-6),
    "shrug": dict(la=(-55, -140), ra=(55, 140), ll=(-10, -5), rl=(10, 5), lean=0, tilt=8),
    "think": dict(la=(-12, 70), ra=(28, -168), ll=(-9, -4), rl=(9, 4), lean=1, tilt=6),
    "arms_up": dict(la=(-150, -168), ra=(150, 168), ll=(-14, -8), rl=(14, 8), lean=0, tilt=0),
    "hold": dict(la=(-22, 72), ra=(22, -72), ll=(-10, -5), rl=(10, 5), lean=0, tilt=4),
    "hold_r": dict(la=(-14, -6), ra=(40, 110), ll=(-10, -5), rl=(10, 5), lean=1, tilt=6),
    "sad": dict(la=(-6, -3), ra=(6, 3), ll=(-8, -4), rl=(8, 4), lean=4, tilt=14),
    "facepalm": dict(la=(-14, -6), ra=(26, -172), ll=(-10, -5), rl=(10, 5), lean=3, tilt=10),
    "cross": dict(la=(-18, 80), ra=(18, -80), ll=(-12, -6), rl=(12, 6), lean=0, tilt=-4),
    "hips": dict(la=(-40, 30), ra=(40, -30), ll=(-12, -6), rl=(12, 6), lean=0, tilt=-3),
    "reach": dict(la=(-14, -6), ra=(95, 110), ll=(-6, -14), rl=(24, 10), lean=10, tilt=6),
    "sit": dict(la=(-10, 60), ra=(10, -60), ll=(-80, 0), rl=(80, 0), lean=0, tilt=0),
    "lie": dict(la=(-30, -20), ra=(30, 20), ll=(-6, -3), rl=(6, 3), lean=0, tilt=0),
    "old": dict(la=(-12, -6), ra=(26, 6), ll=(-8, -3), rl=(10, 4), lean=9, tilt=10),
}


def _blend(p0, p1, u):
    o = {}
    for k in p0:
        if isinstance(p0[k], tuple):
            o[k] = tuple(a + (b - a) * u for a, b in zip(p0[k], p1[k]))
        else:
            o[k] = p0[k] + (p1[k] - p0[k]) * u
    return o


def Fig(x, y, s=1.0, at=0.0, poses=(("stand", 0.0),), moods=(("smile", 0.0),), kind="you", enter="draw", seed=1, until=None,
        look=0.0, walk=None, held=None, idle=1.0, rot=0.0, flip=False, yfn=None):
    """Stick figure standing on (x, y). poses/moods: [(name, time)]; walk: (x0, x1, t0, t1); held(ctx, t, hand_xy, b)."""
    poses = [(POSES[p] if isinstance(p, str) else p, tt) for p, tt in poses]
    rr = random.Random(seed)
    ph = [rr.uniform(0, 6.28) for _ in range(6)]
    blinks = []
    tb = at + rr.uniform(1.0, 3.0)
    while tb < at + 120:
        blinks.append(tb)
        tb += rr.uniform(2.2, 5.0)

    def pose_at(t):
        cur = poses[0][0]
        for p1, t1 in poses[1:]:
            if t < t1:
                break
            u = clamp((t - t1) / 0.3)
            cur = _blend(cur, p1, ease_back(u, 1.2)) if u < 1 else p1
        return cur

    def mood_at(t):
        m = moods[0][0]
        for mm, tt in moods:
            if t >= tt:
                m = mm
        return m

    def fn(ctx, t):
        if t < at or (until is not None and t >= until):
            return
        b = boil(t)
        P = dict(pose_at(t))
        sw = math.sin(2 * math.pi * 0.45 * t + ph[0]) * 3 * idle
        P["la"] = (P["la"][0] - sw, P["la"][1] - sw * 1.3)
        P["ra"] = (P["ra"][0] + sw * 0.8, P["ra"][1] + sw)
        X, Y = x, y
        walking = False
        if walk:
            x0, x1, t0, t1 = walk
            u = clamp((t - t0) / (t1 - t0))
            X = x0 + (x1 - x0) * ease_io(u)
            if yfn:
                Y = yfn(X)
            if 0 < u < 1:
                walking = True
                g = math.sin((t - t0) * 2 * math.pi * 1.8)
                P["ll"] = (-22 * g, -22 * g + 8)
                P["rl"] = (22 * g, 22 * g + 8)
                P["la"] = (18 * g, 18 * g + 10)
                P["ra"] = (-18 * g, -18 * g - 10)
        sx = -1 if flip else 1
        ctx.save()
        ctx.translate(X, Y)
        if rot:
            ctx.rotate(math.radians(rot))
        sc = 1.0
        if enter == "pop" and t - at < 0.25:
            sc = max(0.05, ease_back((t - at) / 0.25))
        ctx.scale(s * sc * sx, s * sc)
        br = 1 + 0.012 * math.sin(2 * math.pi * 0.3 * t + ph[1]) * idle
        bob = (abs(math.sin((t - walk[2]) * 2 * math.pi * 1.8)) * -6) if walking else 0
        hip = np.array([0.0, -124 + bob])
        lean = math.radians(P["lean"])
        tor = 118 * br
        neck = hip + tor * np.array([math.sin(lean), -math.cos(lean)])
        sh = hip + 0.84 * tor * np.array([math.sin(lean), -math.cos(lean)])
        R = 40
        tilt = math.radians(P["tilt"] + P["lean"])
        hc = neck + (R + 3) * np.array([math.sin(tilt), -math.cos(tilt)])

        def limb(p0, a, l1, l2):
            a1, a2 = math.radians(a[0]), math.radians(a[1])
            e = p0 + l1 * np.array([math.sin(a1), math.cos(a1)])
            h = e + l2 * np.array([math.sin(a2), math.cos(a2)])
            return np.array([p0, e, h])

        parts = [limb(hip, P["ll"], 64, 62), limb(hip, P["rl"], 64, 62), np.array([hip, neck]),
                 limb(sh, P["la"], 56, 52), limb(sh, P["ra"], 56, 52)]
        u = 1.0 if enter != "draw" else clamp((t - at) / 0.6)
        order = [2, 3, 4, 0, 1]
        fr = ease_out(u) * 6
        w = 7.5
        # head first
        head = Path(P_ell(hc[0], hc[1], R, R * 1.02, seed, 0.08, a0=-100), seed * 11)
        if held and u >= 1:
            held(ctx, t, parts[4][2], b)
        ctx.new_path()
        ctx.arc(hc[0], hc[1], R - 1, 0, 2 * math.pi)
        ctx.set_source_rgba(*rgb(PAPER))
        ctx.fill()
        stroke(ctx, head, b, w, INK, clamp(fr))
        for j, k in enumerate(order):
            f = clamp(fr - 1 - j)
            if f > 0:
                stroke(ctx, Path(parts[k], seed * 11 + k + 1, wob=1.0), b, w, INK, f)
        if u >= 0.25:
            _face(ctx, hc, R, tilt, mood_at(t), t, b, look, blinks, seed)
            _hair(ctx, hc, R, tilt, kind, b, seed)
        if kind == "old" and u >= 1:
            hp = parts[4][2]
            stroke(ctx, Path(P_line(hp[0], hp[1] - 6, hp[0] + 10, 2, 0.02, seed), seed * 5), b, 6, INK)
            stroke(ctx, Path(P_arc(hp[0] - 10, hp[1] - 6, 12, 12, 180, 360), seed * 6), b, 6, INK)
        ctx.restore()

    return fn


def _face(ctx, hc, R, tilt, mood, t, b, look, blinks, seed):
    ctx.save()
    ctx.translate(hc[0] + look * R * 0.2, hc[1])
    ctx.rotate(tilt * 0.6)
    blink = any(bt <= t < bt + 0.12 for bt in blinks)
    ey = -R * 0.08
    for ex in (-R * 0.33, R * 0.33):
        if mood in ("sleep",):
            stroke(ctx, Path(P_arc(ex, ey, 7, 5, 20, 160), seed + 3), b, 4, INK, amp=0.3)
        elif blink or mood == "happy":
            stroke(ctx, Path(P_arc(ex, ey + (4 if mood == "happy" else 0), 7, 6, 200, 340) if mood == "happy" else P_line(ex - 7, ey, ex + 7, ey, 0, 1),
                             seed + 4), b, 4, INK, amp=0.3)
        else:
            ctx.new_path()
            ctx.arc(ex + (b - 1) * 0.4, ey, 5.2, 0, 2 * math.pi)
            ctx.set_source_rgba(*rgb(INK))
            ctx.fill()
    my = R * 0.42
    m = {
        "smile": P_bez((-R * 0.3, my - 3), (0, my + 12), (R * 0.3, my - 3)),
        "happy": P_bez((-R * 0.34, my - 5), (0, my + 16), (R * 0.34, my - 5)),
        "sad": P_bez((-R * 0.28, my + 7), (0, my - 8), (R * 0.28, my + 7)),
        "flat": P_line(-R * 0.22, my + 2, R * 0.22, my, 0, 2),
        "worried": P_wave(-R * 0.26, R * 0.26, my + 2, 3, 18),
        "smug": P_bez((-R * 0.22, my + 2), (R * 0.1, my + 4), (R * 0.32, my - 8)),
        "sleep": P_ell(0, my + 2, 5, 4, 1, 0.0, closed=True),
    }.get(mood)
    if mood in ("o", "wow"):
        rr = 7 if mood == "o" else 10
        stroke(ctx, Path(P_ell(0, my + 3, rr * 0.8, rr, seed, 0.1), seed + 5), b, 4.5, INK, amp=0.3)
    elif mood == "grin":
        q = np.vstack([P_bez((-R * 0.32, my - 4), (0, my + 22), (R * 0.32, my - 4)), [(-R * 0.32, my - 4)]])
        ctx.new_path()
        ctx.move_to(*q[0])
        for p in q[1:]:
            ctx.line_to(*p)
        ctx.set_source_rgba(*rgb(INK))
        ctx.fill()
    elif m is not None:
        stroke(ctx, Path(m, seed + 6), b, 4.5, INK, amp=0.3)
    brows = {"worried": ((-R * 0.48, ey - 15, -R * 0.18, ey - 21), (R * 0.18, ey - 21, R * 0.48, ey - 15)),
             "angry": ((-R * 0.48, ey - 20, -R * 0.16, ey - 13), (R * 0.16, ey - 13, R * 0.48, ey - 20)),
             "wow": ((-R * 0.46, ey - 21, -R * 0.2, ey - 23), (R * 0.2, ey - 23, R * 0.46, ey - 21)),
             "smug": ((R * 0.16, ey - 18, R * 0.46, ey - 22),)}.get(mood, ())
    for k, (a0, b0, a1, b1) in enumerate(brows):
        stroke(ctx, Path(P_line(a0, b0, a1, b1, 0, k), seed + 7 + k), b, 4, INK, amp=0.3)
    ctx.restore()


def _hair(ctx, hc, R, tilt, kind, b, seed):
    ctx.save()
    ctx.translate(*hc)
    ctx.rotate(tilt)
    if kind == "you":                      # one curl on top: the character's signature
        stroke(ctx, Path(P_bez((-4, -R + 2), (-14, -R - 26), (14, -R - 30), (8, -R - 12)), seed + 9), b, 6, INK)
    elif kind == "old":
        for k, dx in enumerate((-14, -2, 10)):
            stroke(ctx, Path(P_bez((dx, -R + 1), (dx - 6, -R - 12), (dx + 8, -R - 16)), seed + 20 + k), b, 4, GREY)
        for ex in (-R * 0.33, R * 0.33):
            stroke(ctx, Path(P_ell(ex, -R * 0.08, 12, 10, seed, 0.05), seed + 30), b, 3.5, INK, amp=0.3)
        stroke(ctx, Path(P_line(-R * 0.13, -R * 0.1, R * 0.13, -R * 0.1, 0.1, 3), seed + 31), b, 3.5, INK, amp=0.3)
    elif kind == "bob":
        stroke(ctx, Path(P_arc(0, 0, R + 9, R + 11, 160, 380, 50), seed + 40), b, 7, INK)
    elif kind == "spiky":
        pts = [(-R * 0.7, -R * 0.6), (-R * 0.45, -R * 1.25), (-R * 0.15, -R * 0.85), (R * 0.15, -R * 1.35), (R * 0.4, -R * 0.85), (R * 0.75, -R * 1.2), (R * 0.75, -R * 0.55)]
        stroke(ctx, Path(P_poly(pts), seed + 41), b, 6, INK)
    ctx.restore()


# --------------------------------------------------------------------------- props: each returns a list of ops around (x, y) at scale s
def coin(x, y, s=1.0, col=ORANGE):
    r = 46 * s
    return [Fl(P_ell(x, y, r, r, 1, closed=True), col), S(P_ell(x, y, r, r, 2, 0.1), 6 * s), ("g", "€", x, y + 22 * s, int(62 * s), INK)]


def note(x, y, s=1.0, col=(214, 226, 196)):
    w, h = 190 * s, 96 * s
    return [Fl(P_rect(x - w / 2, y - h / 2, w, h, 0), col), S(P_rect(x - w / 2, y - h / 2, w, h, 10 * s), 6 * s),
            S(P_ell(x, y, 26 * s, 26 * s, 3, 0.08), 4.5 * s), ("g", "€", x, y + 14 * s, int(40 * s), INK)]


def piggy(x, y, s=1.0, col=PINK):
    o = [Fl(P_ell(x, y, 130 * s, 92 * s, 1, closed=True), col), S(P_ell(x, y, 130 * s, 92 * s, 4, 0.08), 7 * s)]
    o += [Fl(P_ell(x + 128 * s, y + 4 * s, 24 * s, 30 * s, 2, closed=True), col), S(P_ell(x + 128 * s, y + 4 * s, 24 * s, 30 * s, 5, 0.1), 6 * s)]
    o += [("dot", x + 124 * s, y - 4 * s, 4 * s, INK), ("dot", x + 134 * s, y + 10 * s, 4 * s, INK), ("dot", x + 70 * s, y - 34 * s, 6 * s, INK)]
    o += [S(P_poly([(x + 30 * s, y - 80 * s), (x + 52 * s, y - 128 * s), (x + 74 * s, y - 72 * s)]), 6 * s)]
    for lx in (-70, -30, 40, 80):
        o.append(S(P_line(x + lx * s, y + 80 * s, x + lx * s + 4 * s, y + 124 * s, 0.05, lx), 8 * s))
    o += [S(P_bez((x - 128 * s, y - 6 * s), (x - 170 * s, y - 30 * s), (x - 150 * s, y + 20 * s), (x - 176 * s, y + 6 * s)), 5 * s)]
    o += [S(P_line(x - 30 * s, y - 88 * s, x + 26 * s, y - 90 * s, 0.05, 9), 9 * s)]
    return o


def jar(x, y, s=1.0, label="", fill_u=0.0, col=HL):
    w, h = 140 * s, 180 * s
    o = []
    if fill_u > 0:
        fh = h * 0.85 * fill_u
        o.append(Fl(P_rect(x - w / 2 + 8 * s, y + h / 2 - fh - 6 * s, w - 16 * s, fh, 0, r=10 * s), col))
    o += [S(P_rect(x - w / 2, y - h / 2, w, h, 9 * s, r=22 * s), 6.5 * s),
          S(P_rect(x - w / 2 - 10 * s, y - h / 2 - 30 * s, w + 20 * s, 30 * s, 6 * s, r=8 * s), 6 * s)]
    if label:
        o.append(("g", label, x, y + 8 * s, int(40 * s), INK, HAND, "m"))
    return o


def envelope(x, y, s=1.0, col=(238, 228, 206), kid=False):
    w, h = 220 * s, 140 * s
    o = [Fl(P_rect(x - w / 2, y - h / 2, w, h, 0), col), S(P_rect(x - w / 2, y - h / 2, w, h, 8 * s), 6 * s),
         S(P_poly([(x - w / 2, y - h / 2), (x, y + 6 * s), (x + w / 2, y - h / 2)]), 5.5 * s)]
    if kid:   # a tiny drawing of a child stuck on the envelope
        cx, cy = x + 52 * s, y + 30 * s
        o += [S(P_rect(cx - 34 * s, cy - 40 * s, 68 * s, 76 * s, 4 * s), 4 * s), S(P_ell(cx, cy - 16 * s, 11 * s, 11 * s, 3, 0.1), 3.5 * s),
              S(P_line(cx, cy - 5 * s, cx, cy + 16 * s, 0, 1), 3.5 * s), S(P_poly([(cx - 12 * s, cy + 30 * s), (cx, cy + 16 * s), (cx + 12 * s, cy + 30 * s)]), 3.5 * s),
              S(P_line(cx - 14 * s, cy + 2 * s, cx + 14 * s, cy + 2 * s, 0, 2), 3.5 * s)]
    return o


def phone(x, y, s=1.0, col=(250, 248, 242)):
    w, h = 170 * s, 310 * s
    return [Fl(P_rect(x - w / 2, y - h / 2, w, h, 0, r=26 * s), col), S(P_rect(x - w / 2, y - h / 2, w, h, 8 * s, r=26 * s), 7 * s),
            S(P_line(x - 22 * s, y - h / 2 + 22 * s, x + 22 * s, y - h / 2 + 22 * s, 0, 1), 5 * s)]


def card(x, y, s=1.0, col=(150, 186, 214)):
    w, h = 250 * s, 158 * s
    return [Fl(P_rect(x - w / 2, y - h / 2, w, h, 0, r=18 * s), col), S(P_rect(x - w / 2, y - h / 2, w, h, 8 * s, r=18 * s), 6.5 * s),
            S(P_rect(x - w / 2 + 28 * s, y - 28 * s, 46 * s, 36 * s, 4 * s, r=6 * s), 4.5 * s),
            S(P_line(x - w / 2 + 28 * s, y + 42 * s, x + 40 * s, y + 42 * s, 0.02, 2), 5 * s)]


def calendar(x, y, s=1.0, day=None, head="PAYDAY"):
    w, h = 270 * s, 250 * s
    o = [Fl(P_rect(x - w / 2, y - h / 2, w, h, 0), (250, 248, 242)), Fl(P_rect(x - w / 2, y - h / 2, w, 62 * s, 0), ORANGE),
         S(P_rect(x - w / 2, y - h / 2, w, h, 8 * s), 6.5 * s), S(P_line(x - w / 2, y - h / 2 + 62 * s, x + w / 2, y - h / 2 + 62 * s, 0.01, 3), 5 * s)]
    for k in (-1, 1):
        o.append(S(P_line(x + k * 70 * s, y - h / 2 - 22 * s, x + k * 70 * s, y - h / 2 + 18 * s, 0, k), 7 * s))
    if head:
        o.append(("g", head, x, y - h / 2 + 48 * s, int(40 * s), INK, HAND, "m"))
    if day is not None:
        o.append(("g", str(day), x, y + 82 * s, int(130 * s), INK, HAND, "m"))
    return o


def clock(x, y, s=1.0, hh=-60, mm=30):
    r = 92 * s
    o = [Fl(P_ell(x, y, r, r, 1, closed=True), (250, 248, 242)), S(P_ell(x, y, r, r, 3, 0.1), 7 * s)]
    for a, l in ((hh, 0.5), (mm, 0.78)):
        o.append(S(P_line(x, y, x + r * l * math.sin(math.radians(a)), y - r * l * math.cos(math.radians(a)), 0, 3), 6.5 * s))
    for k in range(12):
        a = math.radians(k * 30)
        o.append(("dot", x + r * 0.8 * math.sin(a), y - r * 0.8 * math.cos(a), 3.2 * s, INK))
    return o


def cart(x, y, s=1.0):
    o = [S(P_poly([(x - 150 * s, y - 120 * s), (x - 110 * s, y - 120 * s), (x - 80 * s, y + 20 * s), (x + 110 * s, y + 20 * s),
                   (x + 140 * s, y - 80 * s), (x - 98 * s, y - 80 * s)]), 7 * s),
         S(P_line(x - 76 * s, y + 20 * s, x - 70 * s, y + 50 * s, 0, 1), 6 * s), S(P_line(x - 70 * s, y + 50 * s, x + 100 * s, y + 50 * s, 0, 2), 6 * s),
         S(P_ell(x - 50 * s, y + 76 * s, 18 * s, 18 * s, 1, 0.1), 6 * s), S(P_ell(x + 80 * s, y + 76 * s, 18 * s, 18 * s, 2, 0.1), 6 * s)]
    for k in range(1, 4):
        xx = x - 98 * s + k * 58 * s
        o.append(S(P_line(xx, y - 78 * s, xx + 8 * s, y + 18 * s, 0.03, k), 3.5 * s))
    return o


def coffee(x, y, s=1.0):
    o = [Fl(P_poly([(x - 56 * s, y - 70 * s), (x + 56 * s, y - 70 * s), (x + 42 * s, y + 70 * s), (x - 42 * s, y + 70 * s)], True), (250, 248, 242)),
         S(P_poly([(x - 56 * s, y - 70 * s), (x + 56 * s, y - 70 * s), (x + 42 * s, y + 70 * s), (x - 42 * s, y + 70 * s)], True), 6.5 * s),
         Fl(P_rect(x - 52 * s, y - 20 * s, 102 * s, 46 * s, 0), (196, 150, 108)),
         S(P_rect(x - 64 * s, y - 92 * s, 128 * s, 22 * s, 4 * s, r=6 * s), 6 * s)]
    for k, dx in enumerate((-18, 14)):
        o.append(S(P_bez((x + dx * s, y - 110 * s), (x + (dx - 14) * s, y - 135 * s), (x + (dx + 14) * s, y - 155 * s), (x + dx * s, y - 180 * s)), 4.5 * s, GREY))
    return o


def house(x, y, s=1.0):
    return [Fl(P_rect(x - 110 * s, y - 80 * s, 220 * s, 170 * s, 0), (250, 248, 242)),
            S(P_rect(x - 110 * s, y - 80 * s, 220 * s, 170 * s, 8 * s), 7 * s),
            Fl(P_poly([(x - 140 * s, y - 76 * s), (x, y - 190 * s), (x + 140 * s, y - 76 * s)], True), ORANGE),
            S(P_poly([(x - 140 * s, y - 76 * s), (x, y - 190 * s), (x + 140 * s, y - 76 * s)]), 7 * s),
            S(P_rect(x - 26 * s, y + 10 * s, 52 * s, 80 * s, 4 * s), 6 * s), S(P_rect(x + 44 * s, y - 50 * s, 44 * s, 44 * s, 4 * s), 5 * s)]


def car(x, y, s=1.0, col=(150, 186, 214)):
    body = [(x - 170 * s, y + 20 * s), (x - 170 * s, y - 30 * s), (x - 100 * s, y - 40 * s), (x - 60 * s, y - 95 * s), (x + 70 * s, y - 95 * s),
            (x + 110 * s, y - 40 * s), (x + 170 * s, y - 30 * s), (x + 170 * s, y + 20 * s)]
    return [Fl(P_poly(body, True), col), S(P_poly(body, True), 7 * s),
            Fl(P_ell(x - 100 * s, y + 24 * s, 34 * s, 34 * s, 1, closed=True), (250, 248, 242)), S(P_ell(x - 100 * s, y + 24 * s, 34 * s, 34 * s, 2, 0.1), 7 * s),
            Fl(P_ell(x + 100 * s, y + 24 * s, 34 * s, 34 * s, 3, closed=True), (250, 248, 242)), S(P_ell(x + 100 * s, y + 24 * s, 34 * s, 34 * s, 4, 0.1), 7 * s),
            S(P_line(x, y - 92 * s, x + 2 * s, y - 40 * s, 0, 1), 5 * s)]


def brain(x, y, s=1.0, col=PINK):
    out = P_bez((x - 150 * s, y + 30 * s), (x - 210 * s, y - 150 * s), (x + 210 * s, y - 170 * s), (x + 150 * s, y + 40 * s), n=60)
    bot = P_bez((x + 150 * s, y + 40 * s), (x + 120 * s, y + 110 * s), (x - 140 * s, y + 110 * s), (x - 150 * s, y + 30 * s), n=40)
    shape = np.vstack([out, bot])
    o = [Fl(shape, col), S(shape, 7 * s), S(P_bez((x, y - 112 * s), (x - 20 * s, y - 30 * s), (x + 20 * s, y + 20 * s), (x, y + 84 * s)), 5 * s)]
    for k, (x0, y0, x1, y1, bend) in enumerate(((-120, -60, -40, -80, 26), (-130, 10, -50, 30, -22), (-90, 70, -20, 60, 18),
                                                 (40, -95, 120, -50, -24), (30, -20, 125, 10, 22), (40, 60, 110, 70, -18))):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        o.append(S(P_bez((x + x0 * s, y + y0 * s), (x + (mx - 12) * s, y + (my - bend) * s), (x + (mx + 12) * s, y + (my + bend) * s),
                         (x + x1 * s, y + y1 * s)), 4.5 * s))
    return o


def bubble(x, y, w, h, tail=(-1, 1), s=1.0, col=(252, 250, 245)):
    tx, ty = x + tail[0] * w * 0.25, y + h / 2
    pts = np.vstack([P_rect(x - w / 2, y - h / 2, w, h, 0, r=min(w, h) * 0.32)])
    o = [Fl(pts, col), S(pts, 6 * s),
         Fl(P_poly([(tx - 20, ty - 4), (tx + 26 * tail[0] * -1 + 40 * tail[0], ty + 52 * tail[1]), (tx + 24, ty - 4)], True), col),
         S(P_poly([(tx - 20, ty), (tx + 40 * tail[0] - 26 * tail[0], ty + 52 * tail[1]), (tx + 24, ty)]), 6 * s)]
    return o


def bars(x0, ybase, vals, labels, at, step=0.35, maxh=420, bw=150, gap=90, cols=None, grow=0.6, txt=None, seed=0, size=64):
    """Hand-drawn bars that grow from the baseline one after another; returns element functions."""
    els = [Dr([S(P_line(x0 - 40, ybase, x0 + len(vals) * (bw + gap) - gap + 40, ybase, 0.01, seed), 7)], at, 0.3, seed=seed)]
    mx = max(vals)
    for k, v in enumerate(vals):
        x = x0 + k * (bw + gap)
        h = maxh * v / mx
        t0 = at + 0.25 + k * step
        col = (cols or [PALE] * len(vals))[k]

        def mk(x=x, h=h, t0=t0, col=col, k=k):
            fp = Path(P_rect(x, ybase - h, bw, h, 0), seed * 9 + k, wob=0.8)
            op = Path(P_poly([(x, ybase), (x, ybase - h), (x + bw, ybase - h), (x + bw, ybase)]), seed * 9 + k + 50)
            rr = random.Random(seed + k)
            off = (rr.uniform(-5, 5), rr.uniform(-4, 4))

            def fn(ctx, t):
                if t < t0:
                    return
                u = ease_back(clamp((t - t0) / grow), 1.1)
                b = boil(t)
                ctx.save()
                ctx.translate(0, ybase)
                ctx.scale(1, max(0.01, u))
                ctx.translate(0, -ybase)
                fill(ctx, fp, b, col, 1.0, off)
                stroke(ctx, op, b, 6.5, INK)
                ctx.restore()
            return fn
        els.append(mk())
        els.append(T(labels[k], x + bw / 2, ybase + 70, 52, INK, at=t0, anchor="m", seed=seed + k))
        if txt:
            els.append(T(txt[k], x + bw / 2, ybase - h - 26, size, INK, at=t0 + grow * 0.8, anchor="m", seed=seed + 20 + k))
    return els


# --------------------------------------------------------------------------- paper and camera
def make_paper(seed=3):
    PW, PH = int(W * 1.12), int(H * 1.12)
    rng = np.random.default_rng(seed)
    lo = Image.fromarray(((rng.normal(0, 1, (PH // 90 + 2, PW // 90 + 2)) * 40) + 128).clip(0, 255).astype(np.uint8)).resize((PW, PH), Image.BICUBIC)
    lo = (np.asarray(lo, np.float32) - 128) / 40 * 2.6
    mid = Image.fromarray(((rng.normal(0, 1, (PH // 6, PW // 6)) * 40) + 128).clip(0, 255).astype(np.uint8)).resize((PW, PH), Image.BILINEAR)
    mid = (np.asarray(mid, np.float32) - 128) / 40 * 1.3
    fine = rng.normal(0, 1.6, (PH, PW)).astype(np.float32)
    yy, xx = np.mgrid[0:PH, 0:PW]
    vig = 1 - 0.07 * (((xx - PW / 2) / (PW / 2)) ** 2 + ((yy - PH / 2) / (PH / 2)) ** 2) ** 1.5
    arr = np.empty((PH, PW, 4), np.uint8)
    for c, ch in ((0, 2), (1, 1), (2, 0)):
        arr[..., c] = ((PAPER[ch] + lo + mid + fine) * vig).clip(0, 255)
    arr[..., 3] = 255
    surf = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_RGB24, PW, PH, PW * 4)
    return surf, arr, PW, PH


class Camera:
    """Handheld drift at full frame rate (smooth noise, never a straight line), optional slow push-in."""

    def __init__(self, seed, dur, push=0.0, cx=W / 2, cy=H / 2, amp=1.0):
        r = random.Random(seed)
        self.ph = [r.uniform(0, 6.28) for _ in range(6)]
        self.fr = [r.uniform(0.07, 0.16), r.uniform(0.05, 0.12), r.uniform(0.3, 0.6), r.uniform(0.35, 0.7), r.uniform(0.04, 0.09)]
        self.dur, self.push, self.cx, self.cy, self.amp = dur, push, cx, cy, amp
        self.pw = r.uniform(1.6, 2.6)

    def apply(self, ctx, t):
        p = self.ph
        a = self.amp
        dx = a * (5 * math.sin(2 * math.pi * self.fr[0] * t + p[0]) + 1.1 * math.sin(2 * math.pi * self.fr[2] * t + p[2]))
        dy = a * (4 * math.sin(2 * math.pi * self.fr[1] * t + p[1]) + 0.9 * math.sin(2 * math.pi * self.fr[3] * t + p[3]))
        rot = a * 0.0012 * math.sin(2 * math.pi * self.fr[4] * t + p[4])
        u = clamp(t / max(self.dur, 0.1))
        z = 1.0 + self.push * (1 - (1 - u) ** self.pw)
        ctx.translate(W / 2, H / 2)
        ctx.rotate(rot)
        ctx.scale(z, z)
        ctx.translate(-W / 2 + dx + (W / 2 - self.cx) * (z - 1) / z, -H / 2 + dy + (H / 2 - self.cy) * (z - 1) / z)


def clip_ell(fn, cx, cy, rx, ry):
    """Draw fn only inside an ellipse (a face in a mirror, a picture in a frame)."""
    def g(ctx, t):
        ctx.save()
        ctx.new_path()
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(rx, ry)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.clip()
        fn(ctx, t)
        ctx.restore()
    return g


def music_note(x, y, s=1.0, col=GREY):
    return [Fl(P_ell(x, y, 16 * s, 12 * s, 1, closed=True), col), S(P_line(x + 14 * s, y - 2 * s, x + 16 * s, y - 70 * s, 0, 2), 5 * s, col),
            S(P_bez((x + 16 * s, y - 70 * s), (x + 40 * s, y - 56 * s), (x + 38 * s, y - 36 * s)), 5 * s, col)]
