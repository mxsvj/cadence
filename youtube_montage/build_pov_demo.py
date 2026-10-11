"""'Can Europeans buy VOO?' POV story demo (~1 min) in the dark video-essay style (inspired by the EGO channel):
black screen, typed monospace text, hard cuts with glitches, grain and vignette, ambient drone with silences,
quiet grey-to-white karaoke captions."""
import math
import os
import re
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(D, "assets_pov")
O = os.path.join(D, "out")
for p in (A, O, os.path.join(A, "voice"), os.path.join(A, "seg")):
    os.makedirs(p, exist_ok=True)
W, H, S, FPS, SR = 1920, 1080, 2, 30, 44100
FD = "/usr/share/fonts/opentype/inter/"
TD = 0.3
TDF = round(TD * FPS)

NAVY, NAVY2 = (20, 33, 61), (29, 46, 82)
CREAM, INK, MUTED, SOFT = (250, 242, 229), (29, 36, 51), (110, 118, 135), (170, 182, 210)
YEL, RED, TEAL, ORANGE, GREY, WHITE = (255, 201, 60), (222, 84, 52), (38, 166, 154), (240, 146, 60), (160, 166, 178), (255, 255, 255)

_f = {}


def F(name, size):
    k = (name, int(size))
    if k not in _f:
        _f[k] = ImageFont.truetype(FD + name, int(size))
    return _f[k]


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# Pillow ignores the alpha of a text fill (only shapes blend), so fades on text did nothing:
# draw semi-transparent text through a mask instead.
_draw_text = ImageDraw.ImageDraw.text


def _text_alpha(self, xy, text, fill=None, font=None, anchor=None, **kw):
    if not (isinstance(fill, tuple) and len(fill) == 4 and fill[3] < 255):
        return _draw_text(self, xy, text, fill, font, anchor, **kw)
    if fill[3] <= 0:
        return
    x0, y0, x1, y1 = (int(v) for v in self.textbbox(xy, text, font=font, anchor=anchor))
    x0, y0, x1, y1 = x0 - 2, y0 - 2, x1 + 3, y1 + 3
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    _draw_text(ImageDraw.Draw(m), (xy[0] - x0, xy[1] - y0), text, 255, font, anchor, **kw)
    col = fill[:3] + ((255,) if self._image.mode == "RGBA" else ())
    self._image.paste(col, (x0, y0, x1, y1), m.point(lambda v: v * fill[3] // 255))


ImageDraw.ImageDraw.text = _text_alpha


# --------------------------------------------------------------------------- script (sub = exactly what is said)
def L(scene, sub, tts=None):
    return dict(scene=scene, sub=sub, tts=tts or sub)


# hypothetical: €200 a month, 7% a year compounded monthly (10 y: €34,617; 20 y: €104,185; 30 y: €243,994)
LINES = [
    L("start", "POV: you're 25, you live in Europe, and every month, you quietly put €200 into an S&P 500 ETF.",
      "P O V: you're twenty-five, you live in Europe, and every month, you quietly put two hundred euros into an S and P five hundred E T F."),
    L("friends", "Your friends upgrade their phones. You don't say anything."),
    L("age35", "At 35, you've put in €24,000. Your account shows almost €35,000.",
      "At thirty-five, you've put in twenty-four thousand euros. Your account shows almost thirty-five thousand."),
    L("drop", "Then one year, the market drops. You lose a fifth, on paper. You keep buying anyway."),
    L("age45", "At 45, something strange happens. Your money earns more in a year than you put in. About three times more.",
      "At forty-five, something strange happens. Your money earns more in a year than you put in. About three times more."),
    L("age55", "At 55, you've put in €72,000. The account says about €244,000.",
      "At fifty-five, you've put in seventy-two thousand euros. The account says about two hundred and forty-four thousand."),
    L("nobody", "Nobody noticed. Not even you, most months."),
    L("trick", "That's the whole trick: time, a cheap fund, and not stopping."),
    L("disclaimer", "This assumes 7% a year. Real returns go up and down, and nothing is guaranteed. This is not financial advice.",
      "This assumes seven percent a year. Real returns go up and down, and nothing is guaranteed. This is not financial advice."),
    L("end", "Next: which S&P 500 ETF can Europeans actually buy?",
      "Next: which S and P five hundred E T F can Europeans actually buy?"),
]
SAY = {"POV": "pee oh vee", "25": "twenty five", "€200": "two hundred euros", "S&P": "S and P", "500": "five hundred",
       "ETF": "ee tee eff", "35": "thirty five", "€24,000": "twenty four thousand euros", "€35,000": "thirty five thousand",
       "45": "forty five", "55": "fifty five", "€72,000": "seventy two thousand euros",
       "€244,000": "two hundred and forty four thousand", "7%": "seven percent"}
TRANS = []
LEAD, GAP, TAIL = 0.5, 0.8, 2.6
SHORT_LAST = 2


def tts(i, text):
    raw, out = os.path.join(A, "voice", f"l{i:02d}_raw.wav"), os.path.join(A, "voice", f"l{i:02d}.wav")
    subprocess.run(["RHVoice-test", "-p", "slt", "-r", "105", "-o", raw], input=text.encode(), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run(["ffmpeg", "-y", "-i", raw, "-af",
         "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
         "-ar", str(SR), "-ac", "1", out])
    with wave.open(out) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


voice = [tts(i, l["tts"]) for i, l in enumerate(LINES)]
frames, starts, t = [], [], 0.0
for i, v in enumerate(voice):
    n = round((len(v) / SR + GAP + (LEAD if i == 0 else 0) + (TAIL if i == len(voice) - 1 else 0)) * FPS)
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
SC = {l["scene"]: (starts[i], starts[i] + frames[i] / FPS) for i, l in enumerate(LINES)}


def write_wav(path, data, ch=1):
    pcm = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "w") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


write_wav(os.path.join(A, "voice.wav"), vt)

# --------------------------------------------------------------------------- word timings
cl = lambda w: w.replace("*", "")
WEAK = {"the", "a", "an", "of", "in", "by", "when", "to", "for", "on", "and", "or", "about", "what", "is", "are", "be", "my", "your", "i"}


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


START_OK = {"can", "will", "and", "but", "or", "so", "because", "which", "that", "is", "are", "to", "when", "where", "while", "between", "before", "after", "need", "needs"}


def _split(words, mx=8):
    """Balanced caption lines: prefer commas, then a natural start word ("can", "are"...), never end on a weak word."""
    if len(words) <= mx:
        return [words]
    target = round(len(words) / -(-len(words) // mx))
    commas = [j + 1 for j, w in enumerate(words[:-1]) if cl(w).endswith(",") and j + 1 >= 3 and len(words) - j - 1 >= 3]
    if commas:
        cut = min(commas, key=lambda c: abs(c - len(words) / 2))
    else:
        cut = next((c for c in (target, target + 1, target - 1, target + 2, target - 2)
                    if 1 < c < len(words) and cl(words[c]).lower() in START_OK), target)
    while cut > 1 and not cl(words[cut - 1]).endswith(",") and cl(words[cut - 1]).lower().strip(",") in WEAK:
        cut -= 1
    return _split(words[:cut], mx) + _split(words[cut:], mx)


def chunks(sub):
    sents, cur = [], []
    for w in sub.split():
        cur.append(w)
        if cl(w)[-1:] in ".:?!":
            sents.append(cur)
            cur = []
    if cur:
        sents.append(cur)
    merged = []
    for s in sents:
        if merged and len(merged[-1]) <= 1:
            merged[-1] = merged[-1] + s
        else:
            merged.append(s)
    return [" ".join(c) for s in merged for c in _split(s)]


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
    return hits[nth]


def lw(i, word, nth=0):
    """Scene-local time of a word."""
    return when(i, word, nth) - starts[i]


# --------------------------------------------------------------------------- drawing helpers
clamp = lambda x, a=0.0, b=1.0: max(a, min(b, x))
prog = lambda t, t0, t1: clamp((t - t0) / (t1 - t0))
ease_out = lambda u: 1 - (1 - u) ** 3


def ease_back(u, s=1.7):
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


def with_alpha(layer, a):
    if a >= 0.999:
        return layer
    r, g, b, al = layer.split()
    return Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * a))))


def comp(base, layer, dx=0, dy=0, a=1.0):
    if a <= 0.001:
        return
    layer = with_alpha(layer, a)
    dx, dy = int(round(dx)), int(round(dy))
    sx, sy, tx, ty = max(0, -dx), max(0, -dy), max(0, dx), max(0, dy)
    w, h = min(layer.width - sx, base.width - tx), min(layer.height - sy, base.height - ty)
    if w > 0 and h > 0:
        if base.mode == "RGBA":
            base.alpha_composite(layer, dest=(tx, ty), source=(sx, sy, sx + w, sy + h))
        else:
            piece = layer.crop((sx, sy, sx + w, sy + h))
            base.paste(piece, (tx, ty), piece)


def sprite_at(base, spr, cx, cy, scale=1.0, a=1.0):
    if scale <= 0.01 or a <= 0.001:
        return
    if abs(scale - 1) > 0.002:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BICUBIC)
    comp(base, spr, cx - spr.width / 2, cy - spr.height / 2, a)


def camera(im, z, cx=W / 2, cy=H / 2):
    if z <= 1.0005:
        return im
    w, h = W / z, H / z
    x0, y0 = clamp(cx - w / 2, 0, W - w), clamp(cy - h / 2, 0, H - h)
    return im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h))


class Cv:
    def __init__(self, bg=None, size=(W, H)):
        self.w, self.h = size
        self.im = Image.new("RGBA", (self.w * S, self.h * S), (0, 0, 0, 0) if bg is None else bg + (255,))
        self.d = ImageDraw.Draw(self.im, "RGBA")

    def _b(self, box):
        return [v * S for v in box]

    def rect(self, box, fill, r=0, outline=None, width=0):
        if r:
            self.d.rounded_rectangle(self._b(box), r * S, fill=fill, outline=outline, width=width * S)
        else:
            self.d.rectangle(self._b(box), fill=fill, outline=outline, width=width * S)

    def ellipse(self, box, fill, outline=None, width=0):
        self.d.ellipse(self._b(box), fill=fill, outline=outline, width=width * S)

    def poly(self, pts, fill):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill)

    def line(self, pts, fill, width, caps=False):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=int(width * S), joint="curve")
        if caps:
            for x, y in (pts[0], pts[-1]):
                self.ellipse([x - width / 2, y - width / 2, x + width / 2, y + width / 2], fill)

    def arc(self, box, a0, a1, fill, width):
        self.d.arc(self._b(box), a0, a1, fill=fill, width=int(width * S))

    def text(self, xy, txt, font, size, fill, anchor="la", spacing=0):
        f = F(font, size * S)
        if spacing:
            x, y = xy[0] * S, xy[1] * S
            if anchor[0] == "m":
                x -= (sum(self.d.textlength(c, font=f) + spacing * S for c in txt) - spacing * S) / 2
            for c in txt:
                self.d.text((x, y), c, font=f, fill=fill, anchor="l" + anchor[1])
                x += self.d.textlength(c, font=f) + spacing * S
            return
        self.d.text((xy[0] * S, xy[1] * S), txt, font=f, fill=fill, anchor=anchor)

    def tlen(self, txt, font, size):
        return self.d.textlength(txt, font=F(font, size * S)) / S

    def shadow(self, box, r, blur=18, alpha=70, dy=10):
        sh = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle(self._b([box[0], box[1] + dy, box[2], box[3] + dy]), r * S, fill=(10, 15, 30, alpha))
        self.im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur * S)))
        self.d = ImageDraw.Draw(self.im, "RGBA")

    def out(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def gradient(cv, top, bottom):
    for y in range(cv.h * S):
        k = y / (cv.h * S - 1)
        cv.d.line([(0, y), (cv.w * S, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * k) for i in range(3)))


def diag_lines(cv, alpha=10):
    for i in range(-10, 30):
        cv.line([(i * 120, 1080), (i * 120 + 700, 0)], (255, 255, 255, alpha), 2)


# --------------------------------------------------------------------------- dark style: palette, typing, small helpers
BG, FG, DIM, FAINT, ERR = (7, 7, 9), (236, 236, 236), (118, 118, 126), (58, 58, 66), (232, 58, 64)
MONO, MONOB = "../../truetype/dejavu/DejaVuSansMono.ttf", "../../truetype/dejavu/DejaVuSansMono-Bold.ttf"
BLACK, LIGHT = "InterDisplay-Black.otf", "Inter-Light.otf"
ticks = []                              # typewriter key times (global seconds)
_tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))


_SD = {"dur": None}                    # duration of the scene being built or drawn (set by the render loop)


def typed(txt, t, t0, cps=28, gt0=None):
    """Prefix of txt typed since t0; with gt0 (scene start), registers one key tick per character instead.
    Types faster when needed so the line is complete before the scene cuts."""
    if _SD["dur"] is not None:
        cps = max(cps, len(txt) / max(0.3, _SD["dur"] - 0.4 - t0))
    if gt0 is not None:
        ticks.extend(gt0 + t0 + k / cps for k in range(len(txt)) if txt[k] != " ")
    return "" if t < t0 else txt[: int((t - t0) * cps) + 1]


def caret(d, x, y, t, size):
    if t % 0.9 < 0.5:
        d.rectangle([x + 4, y - size * 0.8, x + 4 + size * 0.55, y + size * 0.15], fill=FG)


def mid_text(d, y, full, shown, font, fill, x=W / 2):
    """Typed text that stays centered (on x) on its full length."""
    d.text((x - d.textlength(full, font=font) / 2, y), shown, font=font, fill=fill, anchor="ls")


def letters(d, xy, txt, font, t, t0, step=0.04, fade=0.25, fill=FG):
    """Centered text whose letters fade in one after the other."""
    x = xy[0] - d.textlength(txt, font=font) / 2
    for k, ch in enumerate(txt):
        a = prog(t, t0 + k * step, t0 + k * step + fade)
        if a > 0:
            d.text((x, xy[1]), ch, font=font, fill=fill + (int(255 * a),), anchor="ls")
        x += d.textlength(ch, font=font)


def star_pts(cx, cy, r, rot=-90):
    return [(cx + (r if k % 2 == 0 else r * 0.42) * math.cos(math.radians(rot + 36 * k)),
             cy + (r if k % 2 == 0 else r * 0.42) * math.sin(math.radians(rot + 36 * k))) for k in range(10)]


def black():
    return Image.new("RGB", (W, H), BG)


def trig(i, spec):
    """Scene-local time of a cue: seconds, a word, or (word, nth[, offset])."""
    if isinstance(spec, (int, float)):
        return float(spec)
    if isinstance(spec, tuple):
        return lw(i, spec[0], spec[1]) + (spec[2] if len(spec) > 2 else 0)
    return lw(i, spec)


def cam(im, t, dur, cy=500, z=0.035):
    return camera(im, 1 + z * t / dur, W / 2, cy)


def is_mono(font):
    return font in (MONO, MONOB)


def dot_grid(cols, rows, sp, r, col):
    g = Cv(None, size=(cols * sp, rows * sp))
    for rr in range(rows):
        for c in range(cols):
            x, y = c * sp + sp / 2, rr * sp + sp / 2
            g.ellipse([x - r, y - r, x + r, y + r], col)
    return g.out()


def reveal_rows(im, grid, cx, cy, u):
    hh = int(grid.height * ease_out(u))
    if hh > 0:
        comp(im, grid.crop((0, 0, grid.width, hh)), cx - grid.width / 2, cy - grid.height / 2)


# --------------------------------------------------------------------------- generic scenes
def term(rows, size=44, cps=28, cy=480):
    """Terminal block: each (text, cue, colour) row is typed when its cue is said."""
    def build(dur, i):
        fm = F(MONO, size)
        R = [(txt, trig(i, cue), col) for txt, cue, col in rows]
        for txt, t0, _ in R:
            typed(txt, 0, t0, cps, starts[i])
        x0 = (W - max(_tmp.textlength(txt, font=fm) for txt, _, _ in R)) / 2
        lh = size * 1.9
        y0 = cy - (len(R) - 1) * lh / 2

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            last = None
            for k, (txt, t0, col) in enumerate(R):
                s = typed(txt, t, t0, cps)
                if s:
                    d.text((x0, y0 + k * lh), s, font=fm, fill=col, anchor="ls")
                    last = (s, y0 + k * lh)
            if last:
                caret(d, x0 + d.textlength(last[0], font=fm), last[1], t, size)
            return cam(im, t, dur, cy)
        return frame, []
    return build


def bigs(items, events=()):
    """Free layout: (text, cue, font, size, colour, x, y) items; mono text is typed, the rest fades in."""
    def build(dur, i):
        R = []
        for txt, cue, font, size, col, x, y in items:
            t0 = trig(i, cue)
            if is_mono(font):
                typed(txt, 0, t0, 30, starts[i])
            R.append((txt, t0, F(font, size), font, col, x, y))

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            for txt, t0, f, font, col, x, y in R:
                if t < t0:
                    continue
                if is_mono(font):
                    mid_text(d, y, txt, typed(txt, t, t0, 30), f, col, x)
                else:
                    a = prog(t, t0, t0 + 0.15)
                    d.text((x, y + 12 * (1 - a)), txt, font=f, fill=col + (int(255 * a),), anchor="ms")
            return cam(im, t, dur)
        return frame, [(n, trig(i, cue), g) for n, cue, g in events]
    return build


def chapter(n, title):
    def build(dur, i):
        fk, ft = F(MONO, 30), F(LIGHT, 104)
        lab = f"PART {n:02d}"
        typed(lab, 0, 0.1, 20, starts[i])

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            mid_text(d, 430, lab, typed(lab, t, 0.1, 20), fk, DIM)
            letters(d, (W / 2, 580), title, ft, t, 0.35, step=0.035)
            w = 520 * ease_out(prog(t, 0.3, 1.0))
            d.line([(W / 2 - w / 2, 640), (W / 2 + w / 2, 640)], fill=FG + (110,), width=2)
            return cam(im, t, dur, 450, 0.03)
        return frame, [("boom", 0.0, 0.45)]
    return build


def checklist(head_cue, items, head="> checklist"):
    def build(dur, i):
        fm = F(MONO, 42)
        th = trig(i, head_cue)
        typed(head, 0, th, 30, starts[i])
        R = [(txt, trig(i, cue)) for txt, cue in items]
        for k, (txt, _) in enumerate(R):
            typed("[ ] " + txt, 0, th + 0.4 + k * 0.4, 60, starts[i])
        x0 = (W - max(_tmp.textlength("[ ] " + txt, font=fm) for txt, _ in R)) / 2

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            d.text((x0, 330), typed(head, t, th, 30), font=fm, fill=FG, anchor="ls")
            for k, (txt, t0) in enumerate(R):
                s = typed("[ ] " + txt, t, th + 0.4 + k * 0.4, 60)
                if not s:
                    continue
                done = t >= t0
                col = FG if done else DIM
                d.text((x0, 460 + k * 84), ("[x] " if done else "[ ] ")[:len(s)], font=fm, fill=col, anchor="ls")
                d.text((x0 + d.textlength("[ ] ", font=fm), 460 + k * 84), s[4:], font=fm, fill=col, anchor="ls")
            return cam(im, t, dur, 520, 0.03)
        return frame, [("boom", t0, 0.3) for _, t0 in R]
    return build


# --------------------------------------------------------------------------- POV story scenes
def person(d, cx, cy, s, col):
    """Minimal 'you' glyph: head + shoulders."""
    d.ellipse([cx - 20 * s, cy - 78 * s, cx + 20 * s, cy - 38 * s], fill=col)
    d.pieslice([cx - 44 * s, cy - 30 * s, cx + 44 * s, cy + 58 * s], 180, 360, fill=col)


def bars(rows, extra=None):
    """Horizontal bars: (label, value text, fraction, colour, cue); extra = (text, cue) shown big on the right."""
    def build(dur, i):
        fm = F(MONO, 32)
        R = [(lab, val, fr, col, trig(i, cue)) for lab, val, fr, col, cue in rows]
        for lab, _, _, _, t0 in R:
            typed(lab, 0, t0, 30, starts[i])
        ex = (extra[0], trig(i, extra[1])) if extra else None
        X0, L = 340, 1000

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            for k, (lab, val, fr, col, t0) in enumerate(R):
                y = 400 + k * 190
                d.text((X0, y - 24), typed(lab, t, t0, 30), font=fm, fill=FG, anchor="ls")
                g = ease_out(prog(t, t0, t0 + 0.6))
                if g > 0:
                    d.rectangle([X0, y, X0 + max(8, L * fr * g), y + 60], fill=col)
                    d.text((X0 + max(8, L * fr * g) + 24, y + 46), val, font=F(MONOB, 40), fill=col, anchor="ls")
            if ex and t >= ex[1]:
                d.text((1620, 560), ex[0], font=F(BLACK, 170), fill=FG + (int(255 * prog(t, ex[1], ex[1] + 0.15)),), anchor="ms")
            return cam(im, t, dur, 500)
        ev = [("boom", t0, 0.35) for *_, t0 in R] + ([("boom", ex[1], 0.7)] if ex else [])
        return frame, ev
    return build


def sc_start(dur, i):
    tp, t25, teu, t200 = lw(i, "pov"), lw(i, "25"), lw(i, "europe"), lw(i, "€200")
    loc = "location = EU"
    typed(loc, 0, teu, 30, starts[i])
    fb, fm, fl = F(BLACK, 150), F(MONO, 34), F(MONOB, 26)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        if t >= tp:
            d.text((W / 2, 260), "POV", font=fb, fill=FG + (int(255 * prog(t, tp, tp + 0.15)),), anchor="ms")
        if t >= t25:
            a = prog(t, t25, t25 + 0.3)
            person(d, 640, 640, 1.6, FG + (int(255 * a),))
        mid_text(d, 800, loc, typed(loc, t, teu, 30), fm, DIM, 640)
        if t >= t200:
            a = int(255 * prog(t, t200, t200 + 0.3))
            d.rounded_rectangle([1180, 520, 1500, 680], 14, outline=FG + (a,), width=3)
            d.text((1340, 610), "S&P 500 ETF", font=F(MONO, 30), fill=FG + (a,), anchor="ms")
            k = 0
            while t200 + 0.2 + k * 0.55 <= t:
                u = prog(t, t200 + 0.2 + k * 0.55, t200 + 0.2 + k * 0.55 + 0.5)
                if u < 1:
                    x = 760 + (1170 - 760) * ease_out(u)
                    d.rounded_rectangle([x - 50, 580, x + 50, 620], 20, fill=FG + (int(255 * (1 - u * 0.6)),))
                    d.text((x, 608), "€200", font=fl, fill=BG, anchor="ms")
                k += 1
        return cam(im, t, dur, 520)
    return frame, [("tick", t200 + 0.7 + k * 0.55, 0.4) for k in range(int(max(0, dur - lw(i, "€200") - 0.7) / 0.55))]


def sc_friends(dur, i):
    tu, td = lw(i, "upgrade"), lw(i, "don't")
    lab = "€200 → ETF"
    typed(lab, 0, td, 26, starts[i])
    xs = [480, 720, 960, 1200, 1440]

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        for k, x in enumerate(xs):
            you = k == 2
            person(d, x, 600, 1.3, FG if you else (96, 96, 104))
            if not you and t >= tu + k * 0.12:
                u = ease_back(prog(t, tu + k * 0.12, tu + k * 0.12 + 0.3))
                w, h = 34 * u, 60 * u
                d.rounded_rectangle([x - w / 2, 430 - h / 2, x + w / 2, 430 + h / 2], 6, outline=FG, width=3)
                d.text((x + 34, 410), "new", font=F(MONO, 20), fill=DIM, anchor="ls")
        mid_text(d, 760, lab, typed(lab, t, td, 26), F(MONO, 38), FG, 960)
        return cam(im, t, dur, 540)
    return frame, [("tick", tu + k * 0.12, 0.5) for k in range(4)]


def sc_drop(dur, i):
    td, tf, tk = lw(i, "drops"), lw(i, "fifth"), lw(i, "keep")
    path = [100, 104, 109, 113, 118, 112, 101, 94, 97, 103, 110, 116]
    keep = "> keep buying"
    typed(keep, 0, tk, 26, starts[i])
    X0, X1, Y0, Y1 = 400, 1400, 300, 740

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        d.line([(X0, Y0), (X0, Y1), (X1, Y1)], fill=FAINT, width=2)
        d.text((X1, Y1 + 40), "(illustration)", font=F(MONO, 22), fill=FAINT, anchor="rs")
        u = min(prog(t, 0.2, td + 0.6) * 0.62 + 0.38 * prog(t, tk, tk + 1.5), 1)
        n = len(path) - 1
        pts = [(X0 + 30 + k * (X1 - X0 - 60) / n, Y1 - 40 - (v - 90) / 30 * (Y1 - Y0 - 80)) for k, v in enumerate(path)]
        m = u * n
        k = int(m)
        show = pts[: k + 1] + ([(pts[k][0] + (pts[k + 1][0] - pts[k][0]) * (m - k), pts[k][1] + (pts[k + 1][1] - pts[k][1]) * (m - k))] if k < n else [])
        if len(show) > 1:
            d.line(show, fill=FG, width=5, joint="curve")
        if t >= tf:
            d.text((1640, 520), "−20%", font=F(BLACK, 110), fill=ERR + (int(255 * prog(t, tf, tf + 0.15)),), anchor="ms")
            d.text((1640, 580), "on paper", font=F(MONO, 30), fill=DIM, anchor="ms")
        mid_text(d, 850, keep, typed(keep, t, tk, 26), F(MONO, 40), FG)
        return cam(im, t, dur, 520)
    return frame, [("glitch", td, 0.5), ("boom", tf, 0.7)]


def sc_age55(dur, i):
    t72, t244 = lw(i, "€72,000"), lw(i, "€244,000")
    put = "put in: €72,000"
    typed(put, 0, t72, 26, starts[i])

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        mid_text(d, 340, put, typed(put, t, t72, 26), F(MONO, 44), DIM)
        if t >= t244:
            v = 243994 * ease_out(prog(t, t244, t244 + 1.2))
            d.text((W / 2, 600), f"€{int(round(v, -3)):,}", font=F(BLACK, 210), fill=FG, anchor="ms")
            d.text((W / 2, 690), "account value (hypothetical)", font=F(MONO, 30), fill=DIM + (int(255 * prog(t, t244 + 0.8, t244 + 1.1)),), anchor="ms")
        return cam(im, t, dur, 520, 0.05)
    return frame, [("tick", t244 + k * 0.1, 0.45 * (1 - k / 13)) for k in range(12)] + [("boom", t244 + 1.2, 1.0)]


def sc_pov_end(dur, i):
    fk, ft = F(MONO, 26), F(LIGHT, 76)
    typed("next >", 0, 0.05, 30, starts[i])
    ph = Cv(None)
    ph.rect([240, 430, 1040, 880], None, r=6, outline=FAINT, width=2)
    ph.text((640, 665), "next video", MONO, 30, DIM, anchor="mm")
    ph.ellipse([1260, 460, 1650, 850], None, outline=FAINT, width=2)
    ph.text((1455, 655), "subscribe", MONO, 30, DIM, anchor="mm")
    ph = ph.out()

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        mid_text(d, 130, "next >", typed("next >", t, 0.05, 30), fk, DIM)
        letters(d, (W / 2, 250), "Which S&P 500 ETF can Europeans buy?", ft, t, 0.2, step=0.025)
        comp(im, ph, 0, 0, prog(t, 1.0, 1.6))
        return cam(im, t, dur, 540, 0.02)
    return frame, [("boom", 0.0, 0.5)]


SCENES = {
    "start": sc_start, "friends": sc_friends,
    "age35": bars([("put in", "€24,000", 0.69, (110, 110, 118), "put"), ("your account", "≈ €35,000", 0.99, FG, "account")]),
    "drop": sc_drop,
    "age45": bars([("you add / year", "€2,400", 0.33, (110, 110, 118), "put"), ("your money earns / year", "≈ €7,300", 1.0, FG, "earns")],
                  extra=("×3", "three")),
    "age55": sc_age55,
    "nobody": bigs([("Nobody noticed.", 0.2, LIGHT, 110, FG, W / 2, 540), ("not even you", "even", MONO, 38, DIM, W / 2, 660)]),
    "trick": term([("time", "time", FG), ("+ a cheap fund", "cheap", FG), ("+ not stopping", "stopping", FG)], size=60),
    "disclaimer": term([("hypothesis: 7% / year", "7%", FG), ("real returns: up and down", "real", DIM),
                        ("guaranteed: nothing", "guaranteed", DIM), ("not financial advice", "advice", ERR)]),
    "end": sc_pov_end,
}
AGE = {"start": 25, "friends": 25, "age35": 35, "drop": 38, "age45": 45, "age55": 55, "nobody": 55, "trick": 55}

# --------------------------------------------------------------------------- overlays: disclaimer, terminal-style subscribe reminder
E = os.path.join(D, "pov")
os.makedirs(E, exist_ok=True)
K = len(LINES)
NF = sum(frames)
SCN = [l["scene"] for l in LINES]
NFA_OFF = starts[2]
SUB_T0 = 1e9                        # no mid-video subscribe reminder in the short story format
f_nfa, f_sub = F(MONO, 18), F(MONO, 26)


def overlays(im, t):
    d = ImageDraw.Draw(im, "RGBA")
    if t < NFA_OFF:
        a = min(prog(t, 0.3, 0.7), 1 - prog(t, NFA_OFF - 0.5, NFA_OFF))
        d.text((44, 56), "not financial advice · education only", font=f_nfa, fill=DIM + (int(255 * a),), anchor="ls")
    i_ = max(j for j in range(K) if starts[j] <= t + 1e-6)
    age = AGE.get(SCN[i_])
    if age is not None:
        a = min(1.0, prog(t, starts[0] + 0.6, starts[0] + 1.0))
        d.text((W - 60, 72), f"AGE {age}", font=F(MONOB, 30), fill=FG + (int(255 * a),), anchor="rs")
    u = t - SUB_T0
    if 0 <= u <= 3.4:
        txt = "[ subscribed ✓ ]" if u >= 1.8 else "[ subscribe ]"
        shown = txt if u >= 1.8 else typed(txt, u, 0, 30)
        a = 1 - prog(u, 3.0, 3.4)
        d.text((W - 60 - d.textlength(txt, font=f_sub), 72), shown, font=f_sub, fill=(FG if u >= 1.8 else DIM) + (int(255 * a),), anchor="ls")


typed("[ subscribe ]", 0, 0, 30, SUB_T0)

# --------------------------------------------------------------------------- render: hard cuts, glitches, grain, vignette
if __name__ == "__main__" and os.environ.get("LONG_PREVIEW") is None:
    yy, xx = np.mgrid[0:H, 0:W]
    vig = (1 - 0.38 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.4).clip(0.45, 1)[..., None].astype(np.float32)
    grng = np.random.default_rng(7)
    grain = [grng.normal(0, 3.2, (H, W, 1)).astype(np.float32) for _ in range(6)]

    def glitch(a, amt, seed):
        g = np.random.default_rng(seed)
        out = a.copy()
        for _ in range(int(5 + 14 * amt)):
            y, hh = int(g.integers(0, H - 40)), int(g.integers(3, 42))
            out[y:y + hh] = np.roll(a[y:y + hh], int(g.integers(-90, 90) * amt), axis=1)
        k = int(14 * amt)
        if k:
            out[..., 0] = np.roll(out[..., 0], k, axis=1)
            out[..., 2] = np.roll(out[..., 2], -k, axis=1)
        return out

    fns, events = [], []
    for i, l in enumerate(LINES):
        _SD["dur"] = frames[i] / FPS
        fn, ev = SCENES[l["scene"]](frames[i] / FPS, i)
        fns.append(fn)
        events += [(n, starts[i] + tt, g) for n, tt, g in ev]
    # glitch cuts into each chapter card and out of it; plain hard cuts elsewhere
    cut_g = [starts[SCN.index(s_)] for s_ in ("age35", "age45", "age55", "disclaimer")]
    G = [(at, 0.32, g) for n, at, g in events if n == "glitch"] + [(c - 0.05, 0.12, 0.6) for c in cut_g]

    vid = os.path.join(E, "video.mp4")
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    for k in range(NF):
        t = k / FPS
        i = max(j for j in range(K) if starts[j] <= t + 1e-6)
        _SD["dur"] = frames[i] / FPS
        im = fns[i](t - starts[i]).convert("RGB")
        overlays(im, t)
        a = np.asarray(im, dtype=np.uint8)
        amt = max([g * (1 - (t - at) / du) for at, du, g in G if at <= t < at + du] + [0])
        if amt > 0.02 and k % 3 != 2:
            a = glitch(a, amt, k)
        f = a.astype(np.float32) * vig + grain[k % 6]
        enc.stdin.write(f.clip(0, 255).astype(np.uint8).tobytes())
        if k % 600 == 0:
            print("frame", k, "/", NF, flush=True)
    enc.stdin.close()
    enc.wait()
    print("video ok", NF, flush=True)

    # ----------------------------------------------------------------------- sound: drone that changes chord per part, silences, booms, glitches, keys
    n = int(TOTAL * SR)
    tt = np.arange(n) / SR
    mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
    CHORDS = [(45, 52, 57, 60, 64), (41, 48, 53, 57, 64), (38, 50, 53, 57, 62), (40, 52, 55, 59, 64),
              (45, 52, 57, 60, 64), (41, 48, 53, 57, 64), (45, 52, 57, 60, 64)]
    CHORDS[3] = (48, 52, 55, 60, 64)                # C major for the "it worked" part
    PART = [0, 0, 1, 2, 2, 3, 3, 3, 4, 4]
    music = np.zeros(n)
    for c, notes in enumerate(CHORDS):
        lines_c = [j for j in range(K) if PART[j] == c]
        if not lines_c:
            continue
        a0, a1 = starts[lines_c[0]], starts[lines_c[-1]] + frames[lines_c[-1]] / FPS
        w = np.clip(np.minimum((tt - a0 + 0.6) / 1.2, (a1 + 0.6 - tt) / 1.2), 0, 1)
        pad = np.zeros(n)
        for j, m in enumerate(notes):
            for det in (-0.15, 0.15):
                f = mtof(m) + det
                pad += (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.07 * tt + j))
        pad += 1.4 * np.sin(2 * np.pi * mtof(notes[0] - 12) * tt)
        music += pad * w
    music += 0.6 * np.sin(2 * np.pi * mtof(88) * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * tt))
    music /= np.max(np.abs(music))
    env = np.minimum(1, tt / 2.5) * np.clip((TOTAL - tt) / 2.5, 0, 1)
    j1, j2 = SCN.index("drop"), SCN.index("age55")
    DIPS = [(when(j1, "drops") + 0.45, 0.4), (when(j2, "€244,000") - 0.3, 0.3)]
    for c0, hw in DIPS:
        env *= 1 - np.clip(1 - np.abs(tt - c0) / hw, 0, 1) ** 0.3
    write_wav(os.path.join(E, "music.wav"), (music * env * 0.5).astype(np.float32))

    sfx = np.zeros(n + SR, dtype=np.float32)

    def put(x, at, g):
        i0 = int(max(0, at) * SR)
        sfx[i0:i0 + len(x)] += (x * g)[: len(sfx) - i0]

    srng = np.random.default_rng(9)
    bt = np.arange(int(1.6 * SR)) / SR
    boom = np.sin(2 * np.pi * np.cumsum(32 + 40 * np.exp(-bt / 0.08)) / SR) * np.exp(-bt / 0.5)
    gt = int(0.32 * SR)
    gl = srng.standard_normal(gt) * np.repeat(srng.integers(0, 2, gt // 441 + 1), 441)[:gt]
    gl = gl + 0.6 * np.sign(np.sin(2 * np.pi * 180 * np.arange(gt) / SR)) * np.repeat(srng.integers(0, 2, gt // 882 + 1), 882)[:gt]
    gl /= np.max(np.abs(gl))
    kt = np.arange(int(0.03 * SR)) / SR
    tick = np.sin(2 * np.pi * 2600 * kt) * np.exp(-kt / 0.005) + 0.4 * srng.standard_normal(len(kt)) * np.exp(-kt / 0.002)
    for name, at, g in events:
        if name == "boom":
            put(boom, at, 0.6 * g)
        elif name == "glitch":
            put(gl, at, 0.22 * g)
        else:
            put(tick, at, 0.12 * g)
    for at, du, g in G:
        if du < 0.2:
            put(gl[: int(0.12 * SR)], at, 0.12)
    for at in ticks:
        put(tick, at, 0.06 * srng.uniform(0.7, 1.0))
    write_wav(os.path.join(E, "sfx.wav"), sfx[:n])
    mix = os.path.join(E, "mix.wav")
    run(["ffmpeg", "-y", "-i", os.path.join(A, "voice.wav"), "-i", os.path.join(E, "music.wav"), "-i", os.path.join(E, "sfx.wav"), "-filter_complex",
         "[0:a]aformat=channel_layouts=stereo,highpass=f=90,acompressor=threshold=-20dB:ratio=3:attack=5:release=90,asplit=2[v1][v2];"
         "[1:a]aformat=channel_layouts=stereo,volume=0.35[m];[m][v1]sidechaincompress=threshold=0.02:ratio=3:attack=30:release=600[md];"
         "[2:a]aformat=channel_layouts=stereo,volume=0.5[fx];"
         "[v2][md][fx]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
         "-map", "[out]", "-ar", str(SR), mix])

    # ----------------------------------------------------------------------- quiet karaoke captions (grey -> white, no box) + final render
    def ass_time(t):
        t = max(0, t)
        return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

    HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{styles}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for i in range(K):
        for part, a, b in timed_chunks(i):
            ws = [x for x in WT[i] if a - 1e-6 <= x[1] < b - 1e-6]
            txt = "".join(f"{{\\k{max(1, round((wb - wa) * 100))}}}{cl(w)} " for w, wa, wb in ws).rstrip()
            ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b + 0.05)},Sub,,0,0,0,,{{\\fad(120,80)}}{txt}")
    subs = os.path.join(E, "subs.ass")
    with open(subs, "w") as f:
        f.write(HEAD.format(w=W, h=H, styles="Style: Sub,Inter Medium,44,&H00F0F0F0,&H00707070,&H00000000,&H96000000,0,0,0,0,100,100,0.5,0,1,0,2,2,220,220,70,1")
                + "\n".join(ev) + "\n")
    final = os.path.join(O, "pov_dark_16x9.mp4")
    run(["ffmpeg", "-y", "-i", vid, "-i", mix, "-vf", f"ass={subs}:fontsdir={FD},fade=t=out:st={TOTAL - 0.8:.2f}:d=0.8",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest", final])
    print(f"done total={TOTAL:.2f}s")
