"""Demo: 'Can Europeans buy VOO?' (~1 min, beginner investing in Europe, faceless).
Same template as the other demos: animated flat illustrations, transitions, punch zooms,
chapter bar, key-points tracker, subscribe reminder, lo-fi bed, quiet SFX, karaoke captions."""
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
LINES = [
    dict(scene="hook", tts="Every American finance video says: just buy V O O. But if you live in Europe, you probably can't.",
         sub="Every American finance video says: just buy **VOO.** But if you live in Europe, you probably **can't.**"),
    dict(scene="priips", tts="It's not your broker being difficult. It's a European rule called preeps.",
         sub="It's not your broker being difficult. It's a European rule called **PRIIPs.**"),
    dict(scene="ch1", tts="Part one. The missing document.", sub="Part one. The **missing** **document.**"),
    dict(scene="kid", tts="Since twenty eighteen, funds sold to everyday European investors need a short Key Information Document. "
                          "Most U.S. funds simply don't make one.",
         sub="Since **2018,** funds sold to everyday European investors need a short **Key** **Information** **Document.** "
             "Most US funds simply **don't** **make** **one.**"),
    dict(scene="ch2", tts="Part two. There's a European twin.", sub="Part two. There's a **European** **twin.**"),
    dict(scene="twin", tts="The same S and P five hundred exists as a you-sits E T F, usually based in Ireland. "
                           "Same five hundred companies, built for European investors.",
         sub="The same S&P 500 exists as a **UCITS** **ETF,** usually based in **Ireland.** "
             "Same **500** **companies,** built for European investors."),
    dict(scene="ch3", tts="Part three. The real difference is cost.", sub="Part three. The real difference is **cost.**"),
    dict(scene="fees", tts="Fees are often a bit higher. The biggest ones charge about zero point zero seven percent a year, "
                           "versus zero point zero three. On ten thousand euros, that's around four euros a year.",
         sub="Fees are often a bit higher. The biggest ones charge about **0.07%** a year, "
             "versus **0.03%.** On **€10,000,** that's around **€4** **a** **year.**"),
    dict(scene="check", tts="So: no V O O, no problem. Search for an S and P five hundred you-sits E T F, then check the fees, "
                            "and where it's based.",
         sub="So: no VOO, no problem. Search for an **S&P** **500** **UCITS** **ETF,** then check the **fees,** "
             "and where it's **based.**"),
    dict(scene="end", tts="Next video: accumulating or distributing, which one should you pick? This is not financial advice.",
         sub="Next video: **accumulating** or **distributing,** which one should you pick? This is **not** **financial** **advice.**"),
]
# how long each displayed token takes to say (keeps the karaoke in sync when the caption shows a figure)
SAY = {"VOO": "vee oh oh", "PRIIPs": "preeps", "2018": "twenty eighteen", "US": "you ess", "S&P": "S and P",
       "500": "five hundred", "UCITS": "you sits", "ETF": "ee tee eff", "0.07%": "zero point zero seven percent",
       "0.03%": "zero point zero three", "€10,000": "ten thousand euros", "€4": "four euros"}
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


# --------------------------------------------------------------------------- flags, pills, small parts
def star_pts(cx, cy, r, rot=-90):
    return [(cx + (r if k % 2 == 0 else r * 0.42) * math.cos(math.radians(rot + 36 * k)),
             cy + (r if k % 2 == 0 else r * 0.42) * math.sin(math.radians(rot + 36 * k))) for k in range(10)]


def round_corners(cv, r):
    m = Image.new("L", cv.im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, cv.im.width - 1, cv.im.height - 1], r * S, fill=255)
    cv.im.putalpha(Image.fromarray(np.minimum(np.array(cv.im.split()[3]), np.array(m))))
    return cv.out()


def flag(kind, w, h):
    k = Cv(None, size=(w, h))
    if kind == "eu":
        k.rect([0, 0, w, h], (0, 51, 153))
        for j in range(12):
            a = math.radians(-90 + 30 * j)
            k.poly(star_pts(w / 2 + h * 0.32 * math.cos(a), h / 2 + h * 0.32 * math.sin(a), h * 0.07), YEL)
    elif kind == "us":
        k.rect([0, 0, w, h], WHITE)
        for j in range(0, 13, 2):
            k.rect([0, j * h / 13, w, (j + 1) * h / 13], (178, 34, 52))
        k.rect([0, 0, w * 0.42, h * 7 / 13], (60, 59, 110))
        for r in range(4):
            for c in range(5):
                x, y = w * 0.42 * (c + 0.5) / 5, h * 7 / 13 * (r + 0.5) / 4
                k.ellipse([x - 2, y - 2, x + 2, y + 2], WHITE)
    else:
        for j, col in enumerate(((22, 155, 98), WHITE, (255, 136, 62))):
            k.rect([j * w / 3, 0, (j + 1) * w / 3 + 1, h], col)
    k.rect([1, 1, w - 1, h - 1], None, r=8, outline=(200, 206, 218), width=2)
    return round_corners(k, 8)


def pill(txt, bg, fg, size=30, pad=34, spacing=2, font="Inter-ExtraBold.otf"):
    w = int(Cv(None, size=(8, 8)).tlen(txt, font, size) + spacing * len(txt) + 2 * pad)
    h = int(size * 2.2)
    k = Cv(None, size=(w + 20, h + 20))
    k.rect([10, 10, w + 10, h + 10], bg, r=h // 2)
    k.text(((w + 20) / 2, (h + 20) / 2 + size * 0.36), txt, font, size, fg, anchor="ms", spacing=spacing)
    return k.out()


def badge(ok, size):
    k = Cv(None, size=(size, size))
    k.ellipse([8, 8, size - 8, size - 8], TEAL if ok else RED)
    s = size / 120
    if ok:
        k.line([(38 * s, 62 * s), (54 * s, 80 * s), (84 * s, 44 * s)], WHITE, 12 * s, caps=True)
    else:
        k.line([(42 * s, 42 * s), (78 * s, 78 * s)], WHITE, 12 * s, caps=True)
        k.line([(78 * s, 42 * s), (42 * s, 78 * s)], WHITE, 12 * s, caps=True)
    return k.out()


def shake_at(t, t0, amp=9):
    return amp * math.sin((t - t0) * 70) * math.exp(-(t - t0) * 8) if t > t0 else 0


# --------------------------------------------------------------------------- scenes
def scene_hook(dur, i):
    c = Cv(NAVY)
    diag_lines(c, 8)
    bg = c.out().convert("RGB")
    p = Cv(None, size=(420, 800))
    p.shadow([10, 10, 410, 790], 56, blur=20, alpha=90, dy=14)
    p.rect([10, 10, 410, 790], (16, 18, 26), r=56)
    p.rect([24, 24, 396, 776], (246, 247, 250), r=44)
    p.rect([165, 40, 255, 64], (16, 18, 26), r=12)
    p.text((58, 62), "9:41", "Inter-Bold.otf", 20, INK, anchor="ls")
    p.text((46, 140), "Search", "Inter-ExtraBold.otf", 42, INK, anchor="ls")
    p.rect([44, 168, 376, 236], WHITE, r=34, outline=(214, 219, 229), width=2)
    p.ellipse([66, 189, 88, 211], None, outline=MUTED, width=4)
    p.line([(85, 208), (95, 218)], MUTED, 4)
    for y, w in ((470, 330), (520, 220), (600, 330), (650, 260)):
        p.rect([44, y, 44 + w, y + 26], (228, 231, 238), r=13)
    base = p.out()

    def row(ok):
        k = Cv(None, size=(372, 150))
        k.rect([1, 1, 371, 149], WHITE, r=22, outline=(222, 226, 234), width=2)
        k.rect([22, 32, 106, 116], NAVY, r=18)
        k.line([(38, 96), (56, 78), (70, 88), (92, 56)], TEAL, 7)
        k.text((126, 78), "VOO", "Inter-Black.otf", 38, INK, anchor="ls")
        k.text((127, 108), "S&P 500 ETF · USA", "Inter-SemiBold.otf", 19, MUTED, anchor="ls")
        k.rect([268, 54, 352, 98], TEAL if ok else (196, 200, 210), r=22)
        k.text((310, 84), "BUY", "Inter-ExtraBold.otf", 22, WHITE, anchor="ms")
        return k.out()
    row_ok, row_off = row(True), row(False)
    b = Cv(None, size=(400, 170))
    b.shadow([10, 10, 390, 150], 22, blur=12, alpha=90, dy=8)
    b.rect([10, 10, 390, 150], RED, r=22)
    b.ellipse([30, 48, 94, 112], WHITE)
    b.line([(49, 67), (75, 93)], RED, 9, caps=True)
    b.line([(75, 67), (49, 93)], RED, 9, caps=True)
    b.text((112, 76), "NOT AVAILABLE", "Inter-Black.otf", 30, WHITE, anchor="ls")
    b.text((112, 112), "in your region", "Inter-SemiBold.otf", 26, WHITE, anchor="ls")
    banner = b.out()
    ch = Cv(None, size=(560, 110))
    ch.rect([10, 10, 550, 100], NAVY2, r=45, outline=(80, 100, 140), width=2)
    ch.text((140, 67), "YOU LIVE IN EUROPE", "Inter-ExtraBold.otf", 28, WHITE, anchor="ls", spacing=2)
    chip = ch.out()
    chip.alpha_composite(flag("eu", 84, 56), (36, 27))
    t_v, t_eu, t_c = lw(i, "voo"), lw(i, "europe"), lw(i, "can't")
    t_type = max(0.5, t_v - 0.45)
    t_res = t_type + 0.6
    fq, fs, ft = F("Inter-Black.otf", 120), F("Inter-SemiBold.otf", 36), F("Inter-SemiBold.otf", 30)

    def frame(t):
        im = bg.copy()
        d = ImageDraw.Draw(im, "RGBA")
        a = prog(t, 0.15, 0.45)
        dx, al = -60 * (1 - ease_out(a)), int(255 * a)
        d.text((150 + dx, 400), "“JUST BUY", font=fq, fill=WHITE + (al,), anchor="ls")
        d.text((150 + dx, 530), "VOO.”", font=fq, fill=YEL + (al,), anchor="ls")
        d.text((156 + dx, 600), "– every US finance video", font=fs, fill=SOFT + (al,), anchor="ls")
        sprite_at(im, chip, 150 + chip.width / 2, 730, ease_back(prog(t, t_eu, t_eu + 0.3)))
        ph = base.copy()
        pd = ImageDraw.Draw(ph, "RGBA")
        n = 0 if t < t_type else min(3, int((t - t_type) / 0.11) + 1)
        pd.text((108, 214), "VOO"[:n], font=ft, fill=INK, anchor="ls")
        if t < t_res and t % 0.8 < 0.45:
            x = 108 + pd.textlength("VOO"[:n], font=ft) + 3
            pd.line([(x, 186), (x, 220)], fill=(40, 110, 230), width=3)
        ra = prog(t, t_res, t_res + 0.3)
        comp(ph, row_off if t >= t_c else row_ok, 24, 268 + 30 * (1 - ease_out(ra)), ra)
        sprite_at(ph, banner, 210, 343, ease_back(prog(t, t_c, t_c + 0.3)))
        u = ease_out(prog(t, 0.1, 0.6))
        comp(im, ph, 1340 - 210 + shake_at(t, t_c, 10), 120 + 760 * (1 - u))
        return camera(im, 1 + 0.04 * t / dur, 960, 520)
    ev = [("whoosh", 0.1, 0.5)] + [("tick", t_type + k * 0.11, 0.9) for k in range(3)]
    return frame, ev + [("pop", t_res, 0.5), ("pop", t_eu, 0.6), ("impact", t_c, 0.9)]


def scene_priips(dur, i):
    c = Cv(NAVY)
    diag_lines(c)
    bg = c.out().convert("RGB")
    st = Cv(None, size=(80, 80))
    st.poly(star_pts(40, 43, 34), YEL)
    st = st.out()
    k = Cv(None, size=(720, 360))
    k.shadow([30, 30, 690, 320], 26, blur=16, alpha=110, dy=12)
    k.rect([30, 30, 690, 320], WHITE, r=26)
    k.rect([64, 84, 76, 266], YEL, r=6)
    k.text((390, 200), "PRIIPs", "Inter-Black.otf", 130, NAVY, anchor="ms")
    k.text((390, 266), "EU RULE  ·  SINCE 2018", "Inter-Bold.otf", 30, MUTED, anchor="ms", spacing=3)
    card = k.out().rotate(-4, expand=True, resample=Image.BICUBIC)
    t_p, t_eu = lw(i, "priips"), lw(i, "european")
    f1 = F("Inter-ExtraBold.otf", 54)
    hit = t_p + 0.18

    def frame(t):
        im = bg.copy()
        dim = 1 - 0.55 * prog(t, t_p, t_p + 0.3)
        for j in range(12):
            a = math.radians(-90 + 30 * j + 8 * t)
            sprite_at(im, st, 960 + 270 * math.cos(a), 560 + 270 * math.sin(a), ease_back(prog(t, 0.1 + j * 0.05, 0.35 + j * 0.05)), dim)
        d = ImageDraw.Draw(im, "RGBA")
        a1 = prog(t, 0.2, 0.5) * (1 - prog(t, t_eu - 0.25, t_eu))
        d.text((960, 200), "NOT YOUR BROKER…", font=f1, fill=SOFT + (int(255 * a1),), anchor="ms")
        a2 = prog(t, t_eu, t_eu + 0.3)
        d.text((960, 200 - 20 * (1 - a2)), "…A EUROPEAN RULE", font=f1, fill=YEL + (int(255 * a2),), anchor="ms")
        u = prog(t, t_p, hit)
        if u > 0:
            sprite_at(im, card, 960, 560, 1.7 - 0.7 * ease_out(u), prog(t, t_p, t_p + 0.1))
        return camera(im, 1 + 0.03 * t / dur, 960 + shake_at(t, hit), 560)
    ev = [("whoosh", 0.05, 0.5)] + [("tick", 0.1 + j * 0.05, 0.35) for j in range(12)]
    return frame, ev + [("pop", t_eu, 0.5), ("impact", hit - 0.03, 0.8)]


def scene_chapter(n, title):
    def build(dur, i):
        c = Cv(NAVY)
        diag_lines(c)
        bg = c.out().convert("RGB")
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
            for ch in "PART":
                d.text((940 + 120 * (1 - u) + x, 338), ch, font=fk, fill=SOFT + (a,), anchor="ls")
                x += d.textlength(ch, font=fk) + 5
            d.text((936 + 160 * (1 - u), 440), title, font=ft, fill=WHITE + (a,), anchor="ls")
            w = 400 * ease_out(prog(t, 0.3, 0.65))
            if w > 2:
                d.rounded_rectangle([760, 520, 760 + w, 528], 4, fill=YEL)
            d.text((760, 590), "can Europeans buy VOO?", font=fs, fill=SOFT + (int(255 * prog(t, 0.5, 0.8)),), anchor="ls")
            return camera(im, 1 + 0.03 * t / dur, 960, 450)
        return frame, [("pop", 0.08, 0.8)]
    return build


def doc_page(k, cx, cy, missing):
    x0, y0, x1, y1 = cx - 120, cy - 150, cx + 120, cy + 150
    if missing:
        col = (196, 202, 214)
        for x in range(x0, x1, 26):
            for y in (y0, y1):
                k.line([(x, y), (min(x + 14, x1), y)], col, 4)
        for y in range(y0, y1, 26):
            for x in (x0, x1):
                k.line([(x, y), (x, min(y + 14, y1))], col, 4)
        k.text((cx, cy - 30), "KID", "Inter-Black.otf", 60, col, anchor="ms")
        k.text((cx, cy + 90), "?", "Inter-Black.otf", 110, col, anchor="ms")
        return
    k.shadow([x0, y0, x1, y1], 10, blur=10, alpha=40, dy=6)
    k.rect([x0, y0, x1, y1], (250, 251, 253), r=10, outline=(214, 219, 229), width=2)
    k.poly([(x1 - 46, y0 - 2), (x1 + 2, y0 - 2), (x1 + 2, y0 + 46)], WHITE)
    k.poly([(x1 - 46, y0), (x1, y0 + 46), (x1 - 46, y0 + 46)], (222, 226, 234))
    k.text((x0 + 26, y0 + 76), "KID", "Inter-Black.otf", 54, NAVY, anchor="ls")
    k.text((x0 + 26, y0 + 110), "Key Information", "Inter-SemiBold.otf", 19, MUTED, anchor="ls")
    k.text((x0 + 26, y0 + 134), "Document", "Inter-SemiBold.otf", 19, MUTED, anchor="ls")
    for j, w in enumerate((188, 160, 188, 120, 170)):
        k.rect([x0 + 26, y0 + 160 + j * 24, x0 + 26 + w, y0 + 170 + j * 24], (222, 226, 234), r=5)


def scene_kid(dur, i):
    c = Cv(CREAM)
    gradient(c, (250, 242, 229), (242, 230, 210))
    bg = c.out().convert("RGB")

    def card(title, col, fg, missing, foot):
        k = Cv(None, size=(620, 580))
        k.shadow([20, 20, 600, 560], 30, blur=18, alpha=55, dy=12)
        k.rect([20, 20, 600, 560], WHITE, r=30)
        tw = k.tlen(title, "Inter-ExtraBold.otf", 32)
        k.rect([56, 52, 56 + tw + 44, 106], col, r=27)
        k.text((78, 91), title, "Inter-ExtraBold.otf", 32, fg, anchor="ls")
        doc_page(k, 310, 300, missing)
        k.text((310, 522), foot, "Inter-SemiBold.otf", 28, MUTED, anchor="ms")
        return k.out()
    c_eu = card("EU FUND", TEAL, NAVY, False, "costs · risks · scenarios")
    c_us = card("US ETF  ·  VOO", NAVY, WHITE, True, "no KID = not sold to you")
    chip = pill("SINCE 2018", NAVY, YEL, size=34)
    ok, no = badge(True, 120), badge(False, 150)
    t18, tf, tk, td, tm, tx = (lw(i, w) for w in ("2018", "funds", "key", "document", "most", "don't"))

    def frame(t):
        im = bg.copy()
        sprite_at(im, chip, 960, 200, ease_back(prog(t, t18, t18 + 0.3)))
        for spr, cx, t0, sgn in ((c_eu, 560, tf, -1), (c_us, 1360, tm, 1)):
            u = prog(t, t0, t0 + 0.45)
            sprite_at(im, spr, cx + sgn * 140 * (1 - ease_out(u)), 580, 1, prog(t, t0, t0 + 0.25))
        hw = 186 * ease_out(prog(t, tk, tk + 0.5))
        if hw > 1:
            ImageDraw.Draw(im, "RGBA").rounded_rectangle([458, 532, 458 + hw, 582], 6, fill=YEL + (120,))
        sprite_at(im, ok, 690, 440, ease_back(prog(t, td + 0.3, td + 0.6)))
        sprite_at(im, no, 1360, 652, ease_back(prog(t, tx, tx + 0.3)))
        return camera(im, 1 + 0.035 * t / dur, 960 + shake_at(t, tx, 7), 560)
    return frame, [("pop", t18, 0.6), ("whoosh", tf - 0.05, 0.3), ("ding", td + 0.3, 0.45), ("whoosh", tm - 0.05, 0.3), ("impact", tx, 0.6)]


def scene_twin(dur, i):
    c = Cv(NAVY)
    diag_lines(c, 8)
    bg = c.out().convert("RGB")
    DX0, DY0, SP = 84, 282, 18

    def card(kind, country, big, small, size_big, filled):
        k = Cv(None, size=(600, 660))
        k.rect([20, 20, 580, 640], WHITE, r=30)
        k.text((300, 196), big, "Inter-Black.otf", size_big, NAVY, anchor="ms")
        k.text((300, 238), small, "Inter-SemiBold.otf", 25, MUTED, anchor="ms")
        for r in range(20):
            for cc in range(25):
                x, y = DX0 + cc * SP, DY0 + r * SP
                k.ellipse([x - 5, y - 5, x + 5, y + 5], TEAL if filled else (226, 230, 238))
        im_ = k.out()
        im_.alpha_composite(flag(kind, 96, 64), (52, 48))
        ImageDraw.Draw(im_, "RGBA").text((166, 92), country, font=F("Inter-ExtraBold.otf", 30), fill=INK, anchor="ls")
        return im_
    us = [card("us", "USA", "VOO", "S&P 500  ·  US fund", 110, f) for f in (False, True)]
    ie = [card("ie", "IRELAND", "UCITS ETF", "S&P 500  ·  e.g. CSPX, VUAA", 80, f) for f in (False, True)]

    def reveal(pair, u):
        if u <= 0:
            return pair[0]
        if u >= 1:
            return pair[1]
        r, cc = divmod(int(500 * u), 25)
        out = pair[0].copy()
        yr = DY0 + r * SP - SP // 2
        if r:
            out.paste(pair[1].crop((0, 0, out.width, yr)), (0, 0))
        if cc:
            out.paste(pair[1].crop((0, yr, DX0 + cc * SP - SP // 2, yr + SP)), (0, yr))
        return out
    eq = Cv(None, size=(120, 100))
    eq.rect([20, 24, 100, 42], YEL, r=9)
    eq.rect([20, 58, 100, 76], YEL, r=9)
    eq = eq.out()
    tu, tie, t5 = lw(i, "ucits"), lw(i, "ireland"), lw(i, "500", 1)

    def frame(t):
        im = bg.copy()
        u = prog(t, t5, t5 + 1.1)
        for pair, cx, t0, sgn in ((us, 560, 0.15, -1), (ie, 1360, tu, 1)):
            v = prog(t, t0, t0 + 0.45)
            sprite_at(im, reveal(pair, u), cx + sgn * 160 * (1 - ease_out(v)), 560, 1, prog(t, t0, t0 + 0.25))
        sprite_at(im, eq, 960, 560, ease_back(prog(t, tie + 0.2, tie + 0.5)))
        return camera(im, 1 + 0.03 * t / dur, 960, 560)
    ticks = [("tick", t5 + k * 0.09, 0.45 * (1 - k / 14)) for k in range(12)]
    return frame, [("whoosh", 0.12, 0.35), ("whoosh", tu - 0.05, 0.35), ("pop", tie, 0.5), ("ding", tie + 0.2, 0.4)] + ticks


def scene_fees(dur, i):
    c = Cv(NAVY)
    diag_lines(c, 8)
    c.text((960, 250), "YEARLY FEE  (TER)", "Inter-SemiBold.otf", 34, SOFT, anchor="ms", spacing=6)
    bg = c.out().convert("RGB")
    t7, t3, t10, t4 = lw(i, "0.07%"), lw(i, "0.03%"), lw(i, "€10,000"), lw(i, "€4")
    chip = pill("ON €10,000 INVESTED", WHITE, NAVY, size=30)
    fl, fb, fc, fy = F("Inter-ExtraBold.otf", 38), F("Inter-Black.otf", 64), F("Inter-Black.otf", 120), F("Inter-ExtraBold.otf", 50)
    X0, L = 260, 1240
    rows = [("S&P 500 UCITS  ·  IRELAND", 0.07, YEL, 400, t7), ("VOO  ·  USA", 0.03, TEAL, 580, t3)]
    cx_chip = X0 + chip.width / 2 - 10

    def frame(t):
        im = bg.copy()
        d = ImageDraw.Draw(im, "RGBA")
        a = prog(t, 0.15, 0.45)
        for lab, fee, col, y, t0 in rows:
            d.text((X0, y - 22), lab, font=fl, fill=WHITE + (int(255 * a),), anchor="ls")
            d.rounded_rectangle([X0, y, X0 + L, y + 74], 37, fill=(255, 255, 255, int(28 * a)))
            g = ease_out(prog(t, t0, t0 + 0.7))
            if g > 0:
                x1 = X0 + max(74, L * fee / 0.07 * g)
                d.rounded_rectangle([X0, y, x1, y + 74], 37, fill=col)
                d.text((x1 + 26, y + 62), f"{fee * g:.2f}%", font=fb, fill=col, anchor="ls")
        sprite_at(im, chip, cx_chip, 790, ease_back(prog(t, t10, t10 + 0.3)))
        v = prog(t, t4, t4 + 0.6)
        if v > 0:
            al = int(255 * prog(t, t4, t4 + 0.15))
            x = X0 + chip.width + 30
            txt = f"≈ €{max(1, round(4 * ease_out(v)))}"
            d.text((x, 840), txt, font=fc, fill=YEL + (al,), anchor="ls")
            d.text((x + d.textlength(txt, font=fc) + 18, 840), "/ year", font=fy, fill=SOFT + (al,), anchor="ls")
        return camera(im, 1 + 0.03 * t / dur, 960, 560)
    ev = [("tick", t0 + k * 0.08, 0.4 * (1 - k / 10)) for _, _, _, _, t0 in rows for k in range(8)]
    return frame, ev + [("ding", t7 + 0.7, 0.35), ("ding", t3 + 0.7, 0.35), ("pop", t10, 0.6),
                        ("tick", t4, 0.5), ("tick", t4 + 0.15, 0.45), ("tick", t4 + 0.3, 0.4), ("ding", t4 + 0.6, 0.5)]


def scene_check(dur, i):
    c = Cv(CREAM)
    gradient(c, (250, 242, 229), (242, 230, 210))
    c.shadow([520, 190, 1400, 870], 34, blur=20, alpha=55, dy=14)
    c.rect([520, 190, 1400, 870], WHITE, r=34)
    bg = c.out().convert("RGB")

    def box(done):
        k = Cv(None, size=(80, 80))
        if done:
            k.rect([8, 8, 72, 72], TEAL, r=16)
            k.line([(24, 41), (35, 53), (56, 28)], WHITE, 8, caps=True)
        else:
            k.rect([10, 10, 70, 70], None, r=16, outline=(200, 206, 218), width=4)
        return k.out()
    b0, b1 = box(False), box(True)
    items = [("Search “S&P 500 UCITS ETF”", lw(i, "search")), ("Check the yearly fee (TER)", lw(i, "fees")),
             ("Check where it's based", lw(i, "based"))]
    fh, fi = F("Inter-Black.otf", 64), F("Inter-SemiBold.otf", 40)
    tp = lw(i, "problem")

    def frame(t):
        im = bg.copy()
        d = ImageDraw.Draw(im, "RGBA")
        h1, h2 = "NO VOO?", "  NO PROBLEM."
        w1, w2 = d.textlength(h1, font=fh), d.textlength(h2, font=fh)
        x = 960 - (w1 + w2) / 2
        d.text((x, 320), h1, font=fh, fill=INK + (int(255 * prog(t, 0.1, 0.35)),), anchor="ls")
        a = prog(t, tp, tp + 0.25)
        d.text((x + w1, 320 - 14 * (1 - a)), h2, font=fh, fill=TEAL + (int(255 * a),), anchor="ls")
        for k, (txt, t0) in enumerate(items):
            y = 480 + k * 130
            ia = prog(t, 0.3 + k * 0.1, 0.6 + k * 0.1)
            on = prog(t, t0, t0 + 0.25)
            sprite_at(im, b0, 640, y - 14, 1, ia * (1 - on))
            sprite_at(im, b1, 640, y - 14, ease_back(prog(t, t0, t0 + 0.3)))
            d.text((700, y), txt, font=fi, fill=INK + (int(255 * ia * (0.35 + 0.65 * on)),), anchor="ls")
        return camera(im, 1 + 0.03 * t / dur, 960, 520)
    return frame, [("pop", tp, 0.5)] + [("ding", t0 + 0.05, 0.35) for _, t0 in items]


def scene_end(dur, i):
    c = Cv(NAVY)
    bg = c.out().convert("RGB")
    ttl = Cv(None, size=(1600, 260))
    ttl.text((800, 60), "NEXT VIDEO", "Inter-SemiBold.otf", 32, SOFT, anchor="ms", spacing=6)
    ttl.text((800, 150), "ACCUMULATING vs DISTRIBUTING", "Inter-ExtraBold.otf", 76, WHITE, anchor="ms")
    ttl.text((800, 214), "which one should you pick?", "Inter-SemiBold.otf", 38, SOFT, anchor="ms")
    ttl = ttl.out()
    nfa = pill("NOT FINANCIAL ADVICE", (60, 74, 110), WHITE, size=22, spacing=3)
    ph = Cv(None)
    ph.rect([240, 440, 1040, 890], NAVY2, r=24, outline=(80, 100, 140), width=3)
    ph.text((640, 650), "NEXT VIDEO", "Inter-Bold.otf", 40, SOFT, anchor="mm", spacing=6)
    ph.text((640, 710), "accumulating vs distributing", "Inter-Medium.otf", 34, (130, 145, 180), anchor="mm")
    ph.ellipse([1260, 470, 1650, 860], NAVY2, outline=(80, 100, 140), width=3)
    ph.text((1455, 665), "SUBSCRIBE", "Inter-Bold.otf", 38, SOFT, anchor="mm", spacing=6)
    ph = ph.out()
    tn = lw(i, "not")

    def frame(t):
        im = bg.copy()
        sprite_at(im, ttl, 960, 190, ease_back(prog(t, 0.1, 0.45)))
        sprite_at(im, nfa, 960, 370, ease_back(prog(t, tn, tn + 0.3)))
        a = prog(t, 0.9, 1.3)
        comp(im, ph, 0, 40 * (1 - ease_out(a)), a)
        return camera(im, 1 + 0.02 * t / dur)
    return frame, [("ding", 0.12, 0.5), ("whoosh", 0.85, 0.35), ("pop", tn, 0.4)]


SCENES = {"hook": scene_hook, "priips": scene_priips, "ch1": scene_chapter(1, "No KID"), "kid": scene_kid,
          "ch2": scene_chapter(2, "The twin"), "twin": scene_twin, "ch3": scene_chapter(3, "The cost"),
          "fees": scene_fees, "check": scene_check, "end": scene_end}


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
PUNCH = [when(0, "can't"), when(1, "priips"), when(3, "2018"), when(3, "don't"), when(5, "ireland"), when(7, "0.07%"),
         when(7, "€4"), when(8, "problem"), when(9, "advice")]
CH = [("KID", SC["ch1"][0], SC["ch2"][0]), ("TWIN", SC["ch2"][0], SC["ch3"][0]), ("COST", SC["ch3"][0], SC["check"][0])]
RULES = [("No KID = no VOO", when(3, "don't") + 0.6), ("Buy the UCITS twin", when(5, "ireland") + 0.5),
         ("~€4/yr more on €10k", when(7, "€4") + 0.7)]
CARD_ON, CARD_OFF = RULES[0][1] - 0.3, SC["end"][0]
SUB_T0 = SC["fees"][0] + 0.8
NFA_OFF = SC["ch1"][0]


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
nfa = sprite((452, 40), lambda d: (d.rounded_rectangle([0, 0, 452 * S - 1, 40 * S - 1], 20 * S, fill=NAVY + (215,)),
                                    d.text((226 * S, 21 * S), "NOT FINANCIAL ADVICE  ·  EDUCATION ONLY", font=F("Inter-Bold.otf", 16 * S),
                                           fill=SOFT, anchor="mm")))
cursor = sprite((44, 60), lambda d: d.polygon([(4 * S, 2 * S), (4 * S, 48 * S), (16 * S, 37 * S), (25 * S, 57 * S), (33 * S, 53 * S), (24 * S, 34 * S), (40 * S, 33 * S)],
                                               fill=WHITE, outline=(0, 0, 0), width=3 * S))


def overlays(im, t):
    d = ImageDraw.Draw(im, "RGBA")
    if t <= NFA_OFF:
        paste(im, nfa, 40 + 226, 46, min(prog(t, 0.3, 0.6), 1 - prog(t, NFA_OFF - 0.4, NFA_OFF)))
    if CARD_ON <= t <= CARD_OFF + 0.3:
        a = min(prog(t, CARD_ON, CARD_ON + 0.3), 1 - prog(t, CARD_OFF, CARD_OFF + 0.3))
        shown = [(txt, t0) for txt, t0 in RULES if t >= t0]
        card, h = rules_card(len(shown))
        cd = ImageDraw.Draw(card, "RGBA")
        x = 26
        for ch in "KEY POINTS":
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
final = os.path.join(O, "finance_karaoke_16x9.mp4")
run(["ffmpeg", "-y", "-i", fx_video, "-i", mix, "-vf",
     f"ass={p169}:fontsdir={FD},fade=t=in:st=0:d=0.3,fade=t=out:st={TOTAL - 0.7:.2f}:d=0.7",
     "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", "-shortest", final])

se = SC["kid"][1]
p916 = os.path.join(A, "short.ass")
with open(p916, "w") as f:
    f.write(HEAD.format(w=1080, h=1920, styles=
                        "Style: Sub,Inter ExtraBold,76,&H003CC9FF,&H00FFFFFF,&H00141414,&H64000000,0,0,0,0,100,100,0,0,1,6,2,2,90,90,430,1\n"
                        "Style: Title,Inter ExtraBold,70,&H00FFFFFF,&H00FFFFFF,&H00141414,&H64000000,0,0,0,0,100,100,0,0,1,6,2,8,80,80,250,1")
            + "\n".join(karaoke_events(SHORT_LAST)) + "\n"
            + "Dialogue: 1,0:00:00.00," + ass_time(se) + ",Title,,0,0,0,,{\\fad(250,0)}Why Europeans\\N{\\c&H3CC9FF&}can't{\\c&HFFFFFF&} buy VOO\n")
run(["ffmpeg", "-y", "-t", f"{se:.3f}", "-i", fx_video, "-t", f"{se:.3f}", "-i", mix, "-filter_complex",
     "[0:v]split=2[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.18[bg];"
     "[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-60,"
     f"ass={p916}:fontsdir={FD},fade=t=in:st=0:d=0.3,fade=t=out:st={se - 0.5:.2f}:d=0.5[v];"
     f"[1:a]afade=t=out:st={se - 0.6:.2f}:d=0.6[au]",
     "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", os.path.join(O, "finance_karaoke_short.mp4")])
print(f"total={TOTAL:.2f}s short={se:.2f}s")
for i in range(len(LINES)):
    print(i, " | ".join(f"{a:5.2f} {p.replace('**', '')}" for p, a, b in timed_chunks(i)))
