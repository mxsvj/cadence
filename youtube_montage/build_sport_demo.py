"""Demo: 'The right way to combine running and calisthenics' (~1 min, first person, faceless).
Same template as the property demo: animated flat illustrations, transitions, punch zooms,
chapter bar, rules tracker, subscribe reminder, lo-fi bed, quiet SFX, karaoke captions."""
import math
import os
import re
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(D, "assets")
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


# --------------------------------------------------------------------------- script (sub = exactly what is said)
LINES = [
    dict(scene="hook", tts="Mixing running and calisthenics the wrong way can make you worse at both.",
         sub="Mixing running and calisthenics the wrong way can make you **worse** **at** **both.**"),
    dict(scene="interf", tts="It's called the interference effect. Here's how I avoid it, without a gym.",
         sub="It's called the **interference** **effect.** Here's how I avoid it, without a gym."),
    dict(scene="ch1", tts="Rule one. Run easy.", sub="Rule one. **Run** **easy.**"),
    dict(scene="ratio", tts="About eighty percent of my runs are slow enough to hold a conversation. Only twenty percent are hard.",
         sub="About **80%** of my runs are slow enough to hold a conversation. Only **20%** are hard."),
    dict(scene="ch2", tts="Rule two. Split upper and lower body.", sub="Rule two. **Split** upper and lower body."),
    dict(scene="split", tts="Pull-ups and push-ups go on running days. Leg work goes on easy days, never before a hard run.",
         sub="Pull-ups and push-ups go on **running** **days.** Leg work goes on easy days, **never** before a hard run."),
    dict(scene="ch3", tts="Rule three. Space your sessions.", sub="Rule three. **Space** your sessions."),
    dict(scene="clock", tts="When I do both on the same day, I keep about six hours between them, and I start with what matters most.",
         sub="When I do both on the same day, I keep about **6** **hours** between them, and I start with what **matters** **most.**"),
    dict(scene="week", tts="Here's my week. Three runs, three calisthenics sessions, and two rest days.",
         sub="Here's my week. **3** **runs,** **3** **calisthenics** sessions, and **2** **rest** days."),
    dict(scene="end", tts="Next video: where swimming and boxing fit in. Subscribe so you don't miss it.",
         sub="Next video: where **swimming** and **boxing** fit in. **Subscribe** so you don't miss it."),
]
TRANS = ["slideleft", "smoothleft", "slideleft", "smoothleft", "slideup", "smoothleft", "slideleft", "circleopen", "fadeblack"]
LEAD, GAP, TAIL = 0.4, 0.35, 2.4
SHORT_LAST = 3


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


START_OK = {"can", "will", "and", "but", "or", "so", "because", "which", "that", "is", "are", "to", "when", "where", "while", "between", "before", "after"}


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
    while cut > 1 and cl(words[cut - 1]).lower().strip(",") in WEAK:
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


def timed_chunks(i):
    parts = chunks(LINES[i]["sub"])
    t0, t1 = line_times[i]
    lens = [len(cl(p)) for p in parts]
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
        lens = [len(cl(w)) + 1 for w in ws]
        t = a
        for w, n in zip(ws, lens):
            d = (b - a) * n / sum(lens)
            out.append((w, t, t + d))
            t += d
    return out


WT = [word_times(i) for i in range(len(LINES))]


def when(i, word, nth=0):
    hits = [a for w, a, b in WT[i] if cl(w).lower().rstrip(".,:") == word.lower()]
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
        base.alpha_composite(layer, dest=(tx, ty), source=(sx, sy, sx + w, sy + h))


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


# --------------------------------------------------------------------------- pictogram figures
RUN_A = dict(head=(26, -170), neck=(14, -122), hip=(0, 0), e1=(50, -78), h1=(82, -106), e2=(-32, -72), h2=(-46, -30),
             k1=(60, 36), f1=(46, 110), k2=(-18, 54), f2=(-80, 84))
RUN_B = dict(RUN_A, e1=(-32, -72), h1=(-46, -30), e2=(50, -78), h2=(82, -106), k1=(-18, 54), f1=(-80, 84), k2=(60, 36), f2=(46, 110))
PULL_DOWN = dict(head=(0, -226), neck=(0, -170), hip=(0, 0), e1=(-92, -236), h1=(-80, -300), e2=(92, -236), h2=(80, -300),
                 k1=(-20, 82), f1=(-24, 164), k2=(20, 82), f2=(24, 164))
PULL_UP = dict(head=(0, -322), neck=(0, -262), hip=(0, -86), e1=(-124, -262), h1=(-80, -300), e2=(124, -262), h2=(80, -300),
               k1=(-20, -4), f1=(-24, 78), k2=(20, -4), f2=(24, 78))
FRONT = dict(head=(0, -198), neck=(0, -142), hip=(0, 0), e1=(-60, -80), h1=(-72, -8), e2=(60, -80), h2=(72, -8),
             k1=(-28, 88), f1=(-32, 176), k2=(28, 88), f2=(32, 176))


def lerp_pose(a, b, u):
    return {k: (a[k][0] + (b[k][0] - a[k][0]) * u, a[k][1] + (b[k][1] - a[k][1]) * u) for k in a}


def figure(cv, P, ox, oy, s, upper, lower, back=None, w=24):
    X = lambda p: (ox + P[p][0] * s, oy + P[p][1] * s)
    ww = w * s
    back = back or (upper, lower)
    cv.line([X("neck"), X("e2"), X("h2")], back[0], ww, caps=True)
    cv.line([X("hip"), X("k2"), X("f2")], back[1], ww, caps=True)
    cv.line([X("neck"), X("hip")], upper, ww * 1.35, caps=True)
    hx, hy = X("head")
    cv.ellipse([hx - 30 * s, hy - 30 * s, hx + 30 * s, hy + 30 * s], upper)
    cv.line([X("hip"), X("k1"), X("f1")], lower, ww, caps=True)
    cv.line([X("neck"), X("e1"), X("h1")], upper, ww, caps=True)


def shade(c, k=0.72):
    return tuple(int(v * k) for v in c[:3])


# --------------------------------------------------------------------------- scenes
def scene_hook(dur, i):
    left = Cv(CREAM)
    gradient(left, (252, 244, 232), (238, 226, 206))
    for k in range(4):
        y = 760 + k * 70
        left.line([(0, y), (960, y - 30)], (205, 190, 165), 4)
    left.rect([960, 0, 1920, 1080], NAVY)
    diag_lines(left, 8)
    left.text((480, 170), "RUNNING", "Inter-ExtraBold.otf", 46, TEAL, anchor="ms", spacing=6)
    left.text((1440, 170), "CALISTHENICS", "Inter-ExtraBold.otf", 46, YEL, anchor="ms", spacing=6)
    bg = left.out()
    t_hit = lw(i, "worse")

    def frame(t):
        c = Cv(None)
        u = 0.5 - 0.5 * math.cos(2 * math.pi * t / 0.55)
        bob = 10 * abs(math.sin(2 * math.pi * t / 0.55))
        x = 480 + 260 * (1 - ease_out(prog(t, 0, 0.6))) * -1
        figure(c, lerp_pose(RUN_A, RUN_B, u), x, 680 - bob, 1.55, TEAL, TEAL, back=(shade(TEAL), shade(TEAL)))
        v = 0.5 - 0.5 * math.cos(2 * math.pi * t / 1.7)
        bar_y = 760 - 300 * 1.3
        c.line([(1230, bar_y), (1650, bar_y)], (200, 208, 225), 14, caps=True)
        c.line([(1240, bar_y), (1240, 960)], (120, 135, 165), 12)
        c.line([(1640, bar_y), (1640, 960)], (120, 135, 165), 12)
        figure(c, lerp_pose(PULL_DOWN, PULL_UP, v), 1440, 760, 1.3, YEL, YEL)
        b = ease_back(prog(t, t_hit, t_hit + 0.3))
        if b > 0.01:
            bolt = [(990, 250), (900, 560), (975, 560), (920, 860), (1050, 470), (970, 470), (1040, 250)]
            c.poly([(960 + (px - 960) * b, 540 + (py - 540) * b) for px, py in bolt], RED + (255,))
        im = bg.copy()
        im.alpha_composite(c.out())
        shake = 9 * math.sin((t - t_hit) * 70) * math.exp(-(t - t_hit) * 8) if t > t_hit else 0
        return camera(im, 1 + 0.04 * t / dur, 960 + shake, 520)
    return frame, [("whoosh", 0.05, 0.5), ("impact", t_hit, 0.9)]


def scene_interf(dur, i):
    c = Cv(NAVY)
    diag_lines(c)
    bg = c.out()

    def arrow(col, label, flip):
        a = Cv(None, size=(760, 170))
        pts = [(0, 45), (560, 45), (560, 0), (760, 85), (560, 170), (560, 125), (0, 125)]
        if flip:
            pts = [(760 - x, y) for x, y in pts]
        a.poly(pts, col + (255,))
        a.text((380 if not flip else 380, 98), label, "Inter-Black.otf", 46, NAVY, anchor="mm", spacing=4)
        return a.out()
    ar_l, ar_r = arrow(TEAL, "ENDURANCE", False), arrow(YEL, "STRENGTH", True)
    t_col = 0.75
    f_t, f_s = F("Inter-ExtraBold.otf", 64), F("Inter-SemiBold.otf", 40)
    t_title = lw(i, "interference")

    def frame(t):
        im = bg.copy()
        u = ease_out(prog(t, 0.1, t_col))
        sprite_at(im, ar_l, -400 + (560 - -400) * u, 560)
        sprite_at(im, ar_r, 2320 - (2320 - 1360) * u, 560)
        b = prog(t, t_col, t_col + 0.35)
        d = ImageDraw.Draw(im, "RGBA")
        if t >= t_col:
            r = 60 + 140 * ease_out(b)
            star = []
            for k in range(16):
                ang = k * math.pi / 8
                rr = r if k % 2 == 0 else r * 0.45
                star.append((960 + rr * math.cos(ang), 560 + rr * math.sin(ang)))
            d.polygon(star, fill=RED + (int(255 * (1 - 0.4 * b)),))
        a = prog(t, t_title, t_title + 0.3)
        d.text((960, 300 - 20 * (1 - a)), "THE INTERFERENCE EFFECT", font=f_t, fill=WHITE + (int(255 * a),), anchor="ms")
        a2 = prog(t, t_col + 0.6, t_col + 0.9)
        d.text((960, 800), "they compete for your recovery", font=f_s, fill=SOFT + (int(255 * a2),), anchor="ms")
        return camera(im, 1 + 0.03 * t / dur, 960, 560)
    return frame, [("whoosh", 0.05, 0.6), ("impact", t_col, 0.8), ("pop", t_title, 0.5)]


def scene_chapter(n, title):
    def build(dur, i):
        c = Cv(NAVY)
        diag_lines(c)
        bg = c.out()
        circ = Cv(None, size=(160, 160))
        circ.ellipse([10, 10, 150, 150], YEL)
        circ.text((80, 82), str(n), "Inter-ExtraBold.otf", 92, NAVY, anchor="mm")
        circ = circ.out()
        fk, ft, fs = F("Inter-SemiBold.otf", 30), F("Inter-ExtraBold.otf", 104), F("Inter-Medium.otf", 36)

        def frame(t):
            im = bg.copy()
            d = ImageDraw.Draw(im, "RGBA")
            sprite_at(im, circ, 830, 400, ease_back(prog(t, 0.05, 0.38)))
            u = ease_out(prog(t, 0.12, 0.45))
            a = int(255 * prog(t, 0.12, 0.35))
            x = 0
            for ch in "RULE":
                d.text((940 + 120 * (1 - u) + x, 360), ch, font=fk, fill=SOFT + (a,), anchor="ls")
                x += d.textlength(ch, font=fk) + 5
            d.text((936 + 160 * (1 - u), 440), title, font=ft, fill=WHITE + (a,), anchor="ls")
            w = 400 * ease_out(prog(t, 0.3, 0.65))
            if w > 2:
                d.rounded_rectangle([760, 520, 760 + w, 528], 4, fill=YEL)
            d.text((760, 590), "running + calisthenics, no gym", font=fs, fill=SOFT + (int(255 * prog(t, 0.5, 0.8)),), anchor="ls")
            return camera(im, 1 + 0.03 * t / dur, 960, 450)
        return frame, [("pop", 0.08, 0.8)]
    return build


def scene_ratio(dur, i):
    c = Cv(NAVY)
    diag_lines(c, 8)
    c.text((960, 250), "MY RUNS", "Inter-SemiBold.otf", 34, SOFT, anchor="ms", spacing=6)
    bg = c.out()
    t80, t20 = lw(i, "80%"), lw(i, "20%")
    fb, fl, fs = F("Inter-Black.otf", 120), F("Inter-ExtraBold.otf", 40), F("Inter-SemiBold.otf", 30)
    x0, x1, y0, y1 = 260, 1660, 470, 590

    def frame(t):
        im = bg.copy()
        d = ImageDraw.Draw(im, "RGBA")
        d.rounded_rectangle([x0, y0, x1, y1], 30, fill=(255, 255, 255, 28))
        g = ease_out(prog(t, t80, t80 + 0.8))
        r = ease_out(prog(t, t20, t20 + 0.5))
        if g > 0:
            d.rounded_rectangle([x0, y0, x0 + (x1 - x0) * 0.8 * g, y1], 30, fill=TEAL)
            d.text((x0 + 40, y0 - 30), f"{int(round(80 * g))}%", font=fb, fill=TEAL, anchor="ls")
            d.text((x0 + 40, y1 + 60), "EASY", font=fl, fill=WHITE + (int(255 * g),), anchor="ls")
            d.text((x0 + 40, y1 + 104), "you can still hold a conversation", font=fs, fill=SOFT + (int(255 * g),), anchor="ls")
        if r > 0:
            xs = x0 + (x1 - x0) * 0.8
            d.rounded_rectangle([xs - 30, y0, xs + (x1 - x0) * 0.2 * r, y1], 30, fill=RED)
            d.rounded_rectangle([x0, y0, xs, y1], 30, fill=TEAL)
            d.text((x1, y0 - 30), f"{int(round(20 * r))}%", font=fb, fill=RED, anchor="rs")
            d.text((x1, y1 + 60), "HARD", font=fl, fill=WHITE + (int(255 * r),), anchor="rs")
        return camera(im, 1 + 0.03 * t / dur, 960, 540)
    ticks = [("tick", t80 + k * 0.07, 0.5 * (1 - k / 13)) for k in range(11)]
    return frame, ticks + [("ding", t80 + 0.8, 0.5), ("pop", t20, 0.7)]


def scene_split(dur, i):
    c = Cv(CREAM)
    gradient(c, (250, 242, 229), (242, 230, 210))
    bg = c.out()

    def card(title, col, items, upper, lower):
        k = Cv(None, size=(700, 660))
        k.shadow([20, 20, 680, 640], 30, blur=18, alpha=55, dy=12)
        k.rect([20, 20, 680, 640], WHITE, r=30)
        tw = k.tlen(title, "Inter-ExtraBold.otf", 34)
        k.rect([60, 56, 60 + tw + 44, 112], col, r=28)
        k.text((82, 96), title, "Inter-ExtraBold.otf", 34, NAVY if col != RED else WHITE, anchor="ls")
        figure(k, FRONT, 350, 360, 1.0, upper, lower, w=26)
        k.text((350, 600), items, "Inter-SemiBold.otf", 32, MUTED, anchor="ms")
        return k.out()
    c1 = card("RUNNING DAYS", TEAL, "pull-ups · push-ups · dips", YEL, (215, 210, 200))
    c2 = card("EASY DAYS", YEL, "squats · lunges · step-ups", (215, 210, 200), TEAL)
    chip = Cv(None, size=(640, 90))
    chip.rect([10, 10, 630, 80], RED, r=35)
    chip.text((320, 58), "NEVER BEFORE A HARD RUN", "Inter-ExtraBold.otf", 32, WHITE, anchor="ms", spacing=2)
    chip = chip.out()
    t1, t2, t3 = lw(i, "pull-ups"), lw(i, "leg"), lw(i, "never")

    def frame(t):
        im = bg.copy()
        for spr, cx, t0 in ((c1, 570, t1), (c2, 1350, t2)):
            u = prog(t, t0, t0 + 0.45)
            sprite_at(im, spr, cx, 560 + 120 * (1 - ease_out(u)), 1, prog(t, t0, t0 + 0.25))
        sprite_at(im, chip, 1350, 890, ease_back(prog(t, t3, t3 + 0.3)))
        return camera(im, 1 + 0.035 * t / dur, 960, 560)
    return frame, [("pop", t1, 0.6), ("pop", t2, 0.6), ("impact", t3, 0.5)]


def scene_clock(dur, i):
    c = Cv(NAVY)
    diag_lines(c, 8)
    cx, cy, R = 600, 560, 300
    c.ellipse([cx - R, cy - R, cx + R, cy + R], (248, 246, 240))
    for h in range(12):
        ang = math.radians(-90 + 30 * h)
        r0 = R - (40 if h % 3 == 0 else 26)
        c.line([(cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)), (cx + (R - 12) * math.cos(ang), cy + (R - 12) * math.sin(ang))],
               INK, 8 if h % 3 == 0 else 4)
    bg = c.out()
    ts, tm = lw(i, "6"), lw(i, "matters")
    fb, fc = F("Inter-Black.otf", 150), F("Inter-ExtraBold.otf", 40)

    def chip(txt, col, fg):
        k = Cv(None, size=(560, 90))
        k.rect([10, 10, 550, 80], col, r=35)
        k.text((280, 58), txt, "Inter-ExtraBold.otf", 32, fg, anchor="ms", spacing=2)
        return k.out()
    c_run, c_cal, c_pri = chip("07:00  RUN", TEAL, NAVY), chip("13:00  CALISTHENICS", YEL, NAVY), chip("PRIORITY SESSION FIRST", RED, WHITE)

    def frame(t):
        im = bg.copy()
        u = ease_out(prog(t, ts, ts + 1.0))
        lay = Cv(None)
        if u > 0:
            lay.arc([cx - R + 34, cy - R + 34, cx + R - 34, cy + R - 34], 120, 120 + 180 * u, YEL + (235,), 40)
        hour = 7 + 6 * u
        ang = math.radians(-90 + 30 * hour)
        lay.line([(cx, cy), (cx + 170 * math.cos(ang), cy + 170 * math.sin(ang))], INK, 16, caps=True)
        lay.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], RED)
        im.alpha_composite(lay.out())
        d = ImageDraw.Draw(im, "RGBA")
        sprite_at(im, c_run, 1360, 330, ease_back(prog(t, 0.3, 0.6)))
        sprite_at(im, c_cal, 1360, 450, ease_back(prog(t, ts + 1.0, ts + 1.3)))
        a = prog(t, ts + 0.2, ts + 0.5)
        d.text((1360, 680), f"{int(round(6 * u))} H", font=fb, fill=YEL + (int(255 * a),), anchor="ms")
        d.text((1360, 740), "between sessions", font=fc, fill=SOFT + (int(255 * a),), anchor="ms")
        sprite_at(im, c_pri, 1360, 860, ease_back(prog(t, tm, tm + 0.3)))
        return camera(im, 1 + 0.03 * t / dur, 960, 560)
    ticks = [("tick", ts + k * 0.09, 0.5 * (1 - k / 14)) for k in range(12)]
    return frame, ticks + [("pop", 0.3, 0.5), ("ding", ts + 1.0, 0.5), ("pop", tm, 0.6)]


WEEK = [("MON", [("EASY RUN", TEAL), ("UPPER BODY", YEL)]), ("TUE", [("HARD RUN", RED)]), ("WED", [("LEGS + CORE", ORANGE)]),
        ("THU", [("UPPER BODY", YEL)]), ("FRI", [("EASY RUN", TEAL)]), ("SAT", [("REST", GREY)]), ("SUN", [("REST", GREY)])]


def scene_week(dur, i):
    c = Cv(CREAM)
    gradient(c, (250, 242, 229), (242, 230, 210))
    c.text((960, 200), "MY WEEK", "Inter-Black.otf", 64, INK, anchor="ms", spacing=4)
    bg = c.out()
    cards = []
    for day, blocks in WEEK:
        k = Cv(None, size=(230, 420))
        k.shadow([10, 10, 220, 410], 22, blur=12, alpha=45, dy=8)
        k.rect([10, 10, 220, 410], WHITE, r=22)
        k.text((115, 66), day, "Inter-ExtraBold.otf", 34, INK, anchor="ms", spacing=3)
        y = 96
        hgt = 280 if len(blocks) == 1 else 134
        for lab, col in blocks:
            k.rect([26, y, 204, y + hgt], col + (255,), r=16)
            for j, part in enumerate(lab.split(" ")):
                k.text((115, y + hgt / 2 + (j - (len(lab.split(' ')) - 1) / 2) * 30 + 10), part, "Inter-ExtraBold.otf", 24,
                       NAVY if col not in (RED,) else WHITE, anchor="ms")
            y += hgt + 12
        cards.append(k.out())

    def chip(txt, col, fg):
        k = Cv(None, size=(420, 80))
        k.rect([10, 10, 410, 70], col, r=30)
        k.text((210, 52), txt, "Inter-ExtraBold.otf", 30, fg, anchor="ms", spacing=2)
        return k.out()
    chips = [(chip("3 RUNS", TEAL, NAVY), lw(i, "3", 0)), (chip("3 CALISTHENICS", YEL, NAVY), lw(i, "3", 1)), (chip("2 REST DAYS", GREY, NAVY), lw(i, "2"))]
    t0 = 0.15

    def frame(t):
        im = bg.copy()
        for k, spr in enumerate(cards):
            sprite_at(im, spr, 222 + k * 246, 500, ease_back(prog(t, t0 + k * 0.16, t0 + k * 0.16 + 0.3)))
        for k, (spr, tt) in enumerate(chips):
            sprite_at(im, spr, 520 + k * 440, 800, ease_back(prog(t, tt, tt + 0.3)))
        return camera(im, 1 + 0.03 * t / dur, 960, 520)
    return frame, [("pop", t0 + k * 0.16, 0.45) for k in range(7)] + [("ding", tt, 0.35) for _, tt in chips]


def scene_end(dur, i):
    c = Cv(NAVY)
    bg = c.out()
    ttl = Cv(None, size=(1500, 200))
    ttl.text((750, 90), "NEXT: SWIMMING + BOXING", "Inter-ExtraBold.otf", 88, WHITE, anchor="ms")
    ttl.text((750, 160), "where they fit in a hybrid week", "Inter-SemiBold.otf", 40, SOFT, anchor="ms")
    ttl = ttl.out()
    ph = Cv(None)
    ph.rect([240, 420, 1040, 870], NAVY2, r=24, outline=(80, 100, 140), width=3)
    ph.text((640, 630), "NEXT VIDEO", "Inter-Bold.otf", 40, SOFT, anchor="mm", spacing=6)
    ph.text((640, 690), "swimming + boxing", "Inter-Medium.otf", 34, (130, 145, 180), anchor="mm")
    ph.ellipse([1260, 450, 1650, 840], NAVY2, outline=(80, 100, 140), width=3)
    ph.text((1455, 645), "SUBSCRIBE", "Inter-Bold.otf", 38, SOFT, anchor="mm", spacing=6)
    ph = ph.out()

    def frame(t):
        im = bg.copy()
        sprite_at(im, ttl, 960, 210, ease_back(prog(t, 0.1, 0.45)))
        a = prog(t, 0.9, 1.3)
        comp(im, ph, 0, 40 * (1 - ease_out(a)), a)
        return camera(im, 1 + 0.02 * t / dur)
    return frame, [("ding", 0.12, 0.5), ("whoosh", 0.85, 0.35)]


SCENES = {"hook": scene_hook, "interf": scene_interf, "ch1": scene_chapter(1, "Run easy"), "ratio": scene_ratio,
          "ch2": scene_chapter(2, "Split the body"), "split": scene_split, "ch3": scene_chapter(3, "Space sessions"),
          "clock": scene_clock, "week": scene_week, "end": scene_end}

# --------------------------------------------------------------------------- render shots + transitions
sfx_events, segs = [], []
for i, l in enumerate(LINES):
    n = frames[i] + (TDF if i < len(LINES) - 1 else 0)
    frame_fn, ev = SCENES[l["scene"]](n / FPS, i)
    sfx_events += [(name, starts[i] + tt, g) for name, tt, g in ev]
    seg = os.path.join(A, "seg", f"s{i:02d}.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", seg],
                         stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for k in range(n):
        p.stdin.write(frame_fn(k / FPS).convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    segs.append(seg)
    print("shot", i, l["scene"], f"{n / FPS:.2f}s", flush=True)

cmd = ["ffmpeg", "-y"]
for s in segs:
    cmd += ["-i", s]
fc, prev, off = [], "[0:v]", 0.0
for k in range(1, len(segs)):
    off += frames[k - 1] / FPS
    fc.append(f"{prev}[{k}:v]xfade=transition={TRANS[k - 1]}:duration={TD}:offset={off:.4f}[x{k}]")
    prev = f"[x{k}]"
    sfx_events.append(("whoosh", off - 0.08, 0.7))
nosub = os.path.join(A, "video_nosub.mp4")
run(cmd + ["-filter_complex", ";".join(fc), "-map", prev, "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), nosub])

# --------------------------------------------------------------------------- overlay pass: punch zooms, chapter bar, rules tracker, subscribe
PUNCH = [when(0, "worse"), when(1, "interference"), when(3, "80%"), when(3, "20%"), when(5, "never"), when(7, "6"),
         when(7, "most"), when(8, "3"), when(9, "subscribe")]
CH = [("EASY", SC["ch1"][0], SC["ch2"][0]), ("SPLIT", SC["ch2"][0], SC["ch3"][0]), ("SPACE", SC["ch3"][0], SC["week"][0])]
RULES = [("Run easy (80/20)", SC["ch1"][0] + 0.3), ("Split upper / lower", SC["ch2"][0] + 0.3), ("6 h between sessions", SC["ch3"][0] + 0.3)]
CARD_ON, CARD_OFF = SC["ch1"][0], SC["end"][0]
SUB_T0 = SC["clock"][0] + 1.2


def sprite(size, draw):
    im = Image.new("RGBA", (size[0] * S, size[1] * S), (0, 0, 0, 0))
    draw(ImageDraw.Draw(im, "RGBA"))
    return im.resize(size, Image.LANCZOS)


def paste(base, spr, x, y, a=1.0, scale=1.0):
    if a <= 0.001:
        return
    if abs(scale - 1) > 0.003:
        spr = spr.resize((int(spr.width * scale), int(spr.height * scale)), Image.BICUBIC)
    spr = with_alpha(spr, a)
    base.paste(spr, (int(round(x - spr.width / 2)), int(round(y - spr.height / 2))), spr)


BAR_X0, BAR_W = 600, 720
bar_bg = sprite((BAR_W, 52), lambda d: d.rounded_rectangle([0, 0, BAR_W * S - 1, 52 * S - 1], 26 * S, fill=NAVY + (220,)))


def rules_card(n_items):
    h = 64 + 40 * max(1, n_items)

    def draw(d):
        d.rounded_rectangle([0, 0, 420 * S - 1, h * S - 1], 20 * S, fill=NAVY + (236,))
        d.rounded_rectangle([0, 0, 8 * S, h * S - 1], 4 * S, fill=YEL)
    return sprite((420, h), draw), h


def _bell(d, x, y, s, col):
    d.ellipse([(x - 11) * s, (y - 13) * s, (x + 11) * s, (y + 9) * s], fill=col)
    d.rectangle([(x - 11) * s, (y - 2) * s, (x + 11) * s, (y + 7) * s], fill=col)
    d.rounded_rectangle([(x - 15) * s, (y + 5) * s, (x + 15) * s, (y + 10) * s], 2 * s, fill=col)
    d.ellipse([(x - 4) * s, (y + 10) * s, (x + 4) * s, (y + 17) * s], fill=col)


def _btn(fill, label, check=False):
    def draw(d):
        d.rounded_rectangle([0, 0, 320 * S - 1, 80 * S - 1], 40 * S, fill=fill)
        if check:
            d.line([(30 * S, 41 * S), (42 * S, 53 * S), (62 * S, 29 * S)], fill=WHITE, width=6 * S, joint="curve")
        else:
            _bell(d, 46, 38, S, WHITE)
        d.text((188 * S, 41 * S), label, font=F("Inter-Bold.otf", 28 * S), fill=WHITE, anchor="mm")
    return sprite((320, 80), draw)


btn_red, btn_done = _btn((204, 30, 30), "SUBSCRIBE"), _btn((70, 70, 78), "SUBSCRIBED", check=True)
cursor = sprite((44, 60), lambda d: d.polygon([(4 * S, 2 * S), (4 * S, 48 * S), (16 * S, 37 * S), (25 * S, 57 * S), (33 * S, 53 * S), (24 * S, 34 * S), (40 * S, 33 * S)],
                                               fill=WHITE, outline=(0, 0, 0), width=3 * S))


def overlays(im, t):
    d = ImageDraw.Draw(im, "RGBA")
    if CARD_ON <= t <= CARD_OFF + 0.3:
        a = min(prog(t, CARD_ON, CARD_ON + 0.3), 1 - prog(t, CARD_OFF, CARD_OFF + 0.3))
        shown = [(txt, t0) for txt, t0 in RULES if t >= t0]
        card, h = rules_card(len(shown))
        cd = ImageDraw.Draw(card, "RGBA")
        x = 26
        for ch in "THE RULES":
            cd.text((x, 38), ch, font=F("Inter-SemiBold.otf", 19), fill=SOFT, anchor="ls")
            x += cd.textlength(ch, font=F("Inter-SemiBold.otf", 19)) + 3
        for k, (txt, t0) in enumerate(shown):
            la = int(255 * prog(t, t0, t0 + 0.25))
            y = 74 + k * 40
            cd.line([(28, y - 8), (36, y), (50, y - 16)], fill=YEL + (la,), width=4, joint="curve")
            cd.text((62, y), txt, font=F("Inter-SemiBold.otf", 24), fill=WHITE + (la,), anchor="ls")
        paste(im, card, 40 + 210 - 30 * (1 - ease_out(a)), 44 + h / 2, a)
    t0, t1 = CH[0][1], SC["end"][0]
    if t0 <= t <= t1 + 0.3:
        a = min(prog(t, t0, t0 + 0.4), 1 - prog(t, t1, t1 + 0.3))
        paste(im, bar_bg, BAR_X0 + BAR_W / 2, 44, a)
        for k, (lab, c0, c1) in enumerate(CH):
            x = BAR_X0 + 30 + k * 230
            p = prog(t, c0, c1)
            col = (WHITE if c0 <= t < c1 else SOFT) + (int(255 * a * (1 if t >= c0 else 0.55)),)
            d.text((x, 38), f"{k + 1}  {lab}", font=F("Inter-Bold.otf", 17), fill=col, anchor="ls")
            d.rounded_rectangle([x, 47, x + 200, 52], 3, fill=(255, 255, 255, int(55 * a)))
            if p > 0:
                d.rounded_rectangle([x, 47, x + max(6, 200 * p), 52], 3, fill=YEL + (int(255 * a),))
    u = t - SUB_T0
    if 0 <= u <= 3.0:
        slide = ease_out(prog(u, 0, 0.3)) * (1 - ease_out(prog(u, 2.6, 2.9)))
        bx = 2120 - (2120 - 1720) * slide
        paste(im, btn_done if u >= 1.66 else btn_red, bx, 90, 1.0, 0.92 if 1.6 <= u < 1.72 else 1.0)
        if 1.0 <= u <= 2.4:
            m = ease_out(prog(u, 1.0, 1.55))
            paste(im, cursor, 1900 + (1760 - 1900) * m + 18, 300 + (108 - 300) * m + 26, 1 - prog(u, 2.1, 2.4))


def punch_zoom(t):
    z = 0.0
    for tp in PUNCH:
        u = t - tp
        if 0 <= u < 0.06:
            z = max(z, ease_out(u / 0.06))
        elif 0.06 <= u < 0.5:
            z = max(z, 1 - ease_out((u - 0.06) / 0.44))
    return 1 + 0.07 * z


fx_video = os.path.join(A, "video_fx.mp4")
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", nosub, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", fx_video], stdin=subprocess.PIPE)
k = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    t = k / FPS
    im = Image.frombytes("RGB", (W, H), buf)
    z = punch_zoom(t)
    if z > 1.001:
        w, h = W / z, H / z
        y0 = clamp((H - h) / 2 - 20 * (z - 1) / 0.07, 0, H - h)
        im = im.resize((W, H), Image.BICUBIC, box=((W - w) / 2, y0, (W + w) / 2, y0 + h))
    overlays(im, t)
    enc.stdin.write(im.tobytes())
    k += 1
enc.stdin.close()
enc.wait()
dec.wait()
print("fx frames", k, flush=True)

# --------------------------------------------------------------------------- sound
rng = np.random.default_rng(5)


def onepole_sweep(x, f0, f1):
    fc = np.geomspace(f0, f1, len(x))
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y, acc = np.empty_like(x), 0.0
    for j in range(len(x)):
        acc += a[j] * (x[j] - acc)
        y[j] = acc
    return y


def sfx_whoosh(dur=0.55):
    n = int(dur * SR)
    y = onepole_sweep(rng.standard_normal(n), 250, 5000)
    y -= onepole_sweep(y, 120, 120)
    return y * np.sin(np.pi * np.linspace(0, 1, n) ** 0.7) ** 2


def sfx_pop():
    t = np.arange(int(0.12 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(380 + 720 * np.exp(-t / 0.018)) / SR) * np.exp(-t / 0.035)


def sfx_impact():
    t = np.arange(int(0.7 * SR)) / SR
    body = np.sin(2 * np.pi * np.cumsum(42 + 70 * np.exp(-t / 0.05)) / SR) * np.exp(-t / 0.22)
    return body + 0.8 * onepole_sweep(rng.standard_normal(len(t)), 2500, 300) * np.exp(-t / 0.04)


def sfx_tick():
    t = np.arange(int(0.03 * SR)) / SR
    return np.sin(2 * np.pi * 2600 * t) * np.exp(-t / 0.005) + 0.4 * rng.standard_normal(len(t)) * np.exp(-t / 0.002)


def sfx_ding():
    t = np.arange(int(1.2 * SR)) / SR
    return sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in ((1568, 1, 0.45), (2349, 0.6, 0.3), (3136, 0.3, 0.18))) * np.minimum(1, t / 0.004)


BANK = {"whoosh": sfx_whoosh(), "pop": sfx_pop(), "impact": sfx_impact(), "tick": sfx_tick(), "ding": sfx_ding()}
BANK = {k: v / (np.max(np.abs(v)) + 1e-9) for k, v in BANK.items()}
LEVEL = {"whoosh": 0.22, "pop": 0.35, "impact": 0.55, "tick": 0.18, "ding": 0.22}
tt = np.arange(int(0.2 * SR)) / SR
thump = np.sin(2 * np.pi * np.cumsum(55 + 60 * np.exp(-tt / 0.02)) / SR) * np.exp(-tt / 0.07)
ct = np.arange(int(0.03 * SR)) / SR
click = np.sin(2 * np.pi * 3200 * ct) * np.exp(-ct / 0.004) + 0.5 * rng.standard_normal(len(ct)) * np.exp(-ct / 0.0015)
sfx = np.zeros(NS + SR, dtype=np.float32)


def place(x, at, g):
    i0 = int(max(0, at) * SR)
    sfx[i0:i0 + len(x)] += (x * g)[: len(sfx) - i0]


for name, at, g in sfx_events:
    place(BANK[name], at, LEVEL[name] * g)
for tp in PUNCH:
    place(thump, tp, 0.22)
for _, t0 in RULES:
    place(BANK["pop"], t0, 0.14)
place(click, SUB_T0 + 1.6, 0.35)
place(BANK["pop"], SUB_T0 + 1.66, 0.12)
write_wav(os.path.join(A, "sfx.wav"), sfx[:NS])


def lofi(seconds):
    n = int(seconds * SR)
    mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
    beat = 60 / 80
    bar = 4 * beat
    chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60, 64], [48, 52, 55, 59]]
    keys, bass, drums = np.zeros(n), np.zeros(n), np.zeros(n)

    def ep(f, dur):
        t = np.arange(int(dur * SR)) / SR
        tone = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.1 * np.sin(6 * np.pi * f * t)
        return tone * np.exp(-t / 1.1) * np.minimum(1, t / 0.008) * (1 + 0.12 * np.sin(2 * np.pi * 4.2 * t))

    def add(buf, x, at):
        i0 = int(at * SR)
        if 0 <= i0 < n:
            buf[i0:i0 + len(x)] += x[: n - i0]

    kt = np.arange(int(0.3 * SR)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(48 + 70 * np.exp(-kt / 0.025)) / SR) * np.exp(-kt / 0.11)
    st = np.arange(int(0.25 * SR)) / SR
    snare = onepole_sweep(rng.standard_normal(len(st)), 3500, 3500) * np.exp(-st / 0.06) + 0.5 * np.sin(2 * np.pi * 190 * st) * np.exp(-st / 0.04)
    ht = np.arange(int(0.04 * SR)) / SR
    hn = rng.standard_normal(len(ht))
    hat = (hn - onepole_sweep(hn, 5000, 5000)) * np.exp(-ht / 0.01)
    for b in range(int(seconds / bar) + 1):
        s0, ch = b * bar, chords[b % 4]
        for hit, vel in ((0, 1.0), (1.5 * beat, 0.55), (2.75 * beat, 0.45)):
            for m in ch:
                add(keys, ep(mtof(m), 2.4) * vel * rng.uniform(0.85, 1.0), s0 + hit + rng.uniform(0, 0.02))
        for hit in (0, 2 * beat, 3.5 * beat):
            bt = np.arange(int(0.6 * SR)) / SR
            add(bass, np.sin(2 * np.pi * mtof(ch[0] - 24) * bt) * np.exp(-bt / 0.35) * np.minimum(1, bt / 0.01), s0 + hit)
        if s0 < 1.5:
            continue
        for hit in (0, 2.5 * beat):
            add(drums, kick, s0 + hit)
        for hit in (beat, 3 * beat):
            add(drums, snare * 0.55, s0 + hit)
        for e in range(8):
            add(drums, hat * (0.3 if e % 2 else 0.22), s0 + e * beat / 2 + (0.07 if e % 2 else 0))
    crackle = np.zeros(n)
    idx = rng.integers(0, n, int(seconds * 9))
    crackle[idx] = rng.uniform(-1, 1, len(idx)) * rng.uniform(0.2, 1, len(idx))
    mix = keys * 0.05 + bass * 0.22 + drums * 0.33 + crackle * 0.05 + rng.standard_normal(n) * 0.02
    t = np.arange(n) / SR
    mix *= np.minimum(1, t / 1.2) * np.clip((seconds - t) / 2.5, 0, 1)
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.5
    right = np.concatenate([np.zeros(int(0.011 * SR)), mix])[:n]
    out = np.empty(2 * n, dtype=np.float32)
    out[0::2], out[1::2] = mix, right
    return out


write_wav(os.path.join(A, "music.wav"), lofi(TOTAL + 0.5), ch=2)
mix = os.path.join(A, "mix.wav")
run(["ffmpeg", "-y", "-i", os.path.join(A, "voice.wav"), "-i", os.path.join(A, "music.wav"), "-i", os.path.join(A, "sfx.wav"),
     "-filter_complex",
     "[0:a]aformat=channel_layouts=stereo,highpass=f=90,acompressor=threshold=-20dB:ratio=3:attack=5:release=90,asplit=2[v1][v2];"
     "[1:a]lowpass=f=3400,highpass=f=40,volume=0.30[m];"
     "[m][v1]sidechaincompress=threshold=0.015:ratio=5:attack=20:release=450[md];"
     "[2:a]aformat=channel_layouts=stereo,volume=0.5[fx];"
     "[v2][md][fx]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
     "-map", "[out]", "-ar", str(SR), mix])


# --------------------------------------------------------------------------- karaoke captions + final renders
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
POP = r"{\fscx86\fscy86\t(0,110,\fscx104\fscy104)\t(110,180,\fscx100\fscy100)}"


def karaoke_events(until=None):
    ev = []
    for i in range(len(LINES)):
        if until is not None and i > until:
            break
        for part, a, b in timed_chunks(i):
            ws = [x for x in WT[i] if a - 1e-6 <= x[1] < b - 1e-6]
            txt = "".join(f"{{\\k{max(1, round((wb - wa) * 100))}}}{cl(w)} " for w, wa, wb in ws).rstrip()
            ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b + 0.05)},Sub,,0,0,0,,{POP}{txt}")
    return ev


p169 = os.path.join(A, "subs.ass")
with open(p169, "w") as f:
    f.write(HEAD.format(w=W, h=H, styles="Style: Sub,Inter ExtraBold,56,&H003CC9FF,&H00FFFFFF,&H003D2114,&H00000000,0,0,0,0,100,100,0.5,0,3,12,0,2,160,160,62,1")
            + "\n".join(karaoke_events()) + "\n")
final = os.path.join(O, "sport_karaoke_16x9.mp4")
run(["ffmpeg", "-y", "-i", fx_video, "-i", mix, "-vf",
     f"ass={p169}:fontsdir={FD},fade=t=in:st=0:d=0.3,fade=t=out:st={TOTAL - 0.7:.2f}:d=0.7",
     "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", "-shortest", final])

se = SC["ratio"][1]
p916 = os.path.join(A, "short.ass")
with open(p916, "w") as f:
    f.write(HEAD.format(w=1080, h=1920, styles=
                        "Style: Sub,Inter ExtraBold,76,&H003CC9FF,&H00FFFFFF,&H00141414,&H64000000,0,0,0,0,100,100,0,0,1,6,2,2,90,90,430,1\n"
                        "Style: Title,Inter ExtraBold,70,&H00FFFFFF,&H00FFFFFF,&H00141414,&H64000000,0,0,0,0,100,100,0,0,1,6,2,8,80,80,250,1")
            + "\n".join(karaoke_events(SHORT_LAST)) + "\n"
            + "Dialogue: 1,0:00:00.00," + ass_time(se) + ",Title,,0,0,0,,{\\fad(250,0)}Running {\\c&H3CC9FF&}+{\\c&HFFFFFF&} calisthenics:\\Nthe right way\n")
run(["ffmpeg", "-y", "-t", f"{se:.3f}", "-i", fx_video, "-t", f"{se:.3f}", "-i", mix, "-filter_complex",
     "[0:v]split=2[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.18[bg];"
     "[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-60,"
     f"ass={p916}:fontsdir={FD},fade=t=in:st=0:d=0.3,fade=t=out:st={se - 0.5:.2f}:d=0.5[v];"
     f"[1:a]afade=t=out:st={se - 0.6:.2f}:d=0.6[au]",
     "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", os.path.join(O, "sport_karaoke_short.mp4")])
print(f"total={TOTAL:.2f}s short={se:.2f}s")
for i in range(len(LINES)):
    print(i, " | ".join(f"{a:5.2f} {p.replace('**', '')}" for p, a, b in timed_chunks(i)))
