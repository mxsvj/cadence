"""Demo edit v2: same story, more motion and sound design.

Adds: animated reveals (drop, pop, slide, highlight sweep), camera push-in on every shot,
transitions between shots (xfade), synthesized sound effects (whoosh, pop, impact, ticks,
ding, marker swipe), a light beat under the music, and pop-in captions.
"""
import math
import os
import random
import re
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(D, "assets2")
O = os.path.join(D, "out2")
for p in (A, O, os.path.join(A, "voice"), os.path.join(A, "seg")):
    os.makedirs(p, exist_ok=True)

W, H, S, FPS, SR = 1920, 1080, 2, 30, 44100
FD = "/usr/share/fonts/opentype/inter/"
TD = 0.3  # transition length (s)
TDF = round(TD * FPS)

NAVY = (20, 33, 61)
NAVY2 = (29, 46, 82)
CREAM = (250, 242, 229)
INK = (29, 36, 51)
MUTED = (110, 118, 135)
SOFT = (170, 182, 210)
YEL = (255, 201, 60)
RED = (222, 84, 52)
GREEN = (70, 140, 90)
WHITE = (255, 255, 255)

_fonts = {}


def F(name, size):
    key = (name, int(size))
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FD + name, int(size))
    return _fonts[key]


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# --------------------------------------------------------------------------- script
LINES = [
    dict(scene="house", sub="This house in rural France costs **€100,000.**",
         tts="This house in rural France costs one hundred thousand euros."),
    dict(scene="house_q", sub="But that's not what you'll **actually** pay. Here are three costs nobody mentions.",
         tts="But that's not what you'll actually pay. Here are three costs nobody mentions."),
    dict(scene="ch1", sub="Number one. **Notary** **fees.**", tts="Number one. Notary fees."),
    dict(scene="counter", sub="On an older home, they're around **7–8%** of the price. Roughly **€7,500,** on top.",
         tts="On an older home, they're around seven to eight percent of the price. Roughly seven thousand five hundred euros, on top."),
    dict(scene="ch2", sub="Number two. **Agency** **fees.**", tts="Number two. Agency fees."),
    dict(scene="listing", sub="They're often already **included** in the listing price. Look for three letters. **F.** **A.** **I.**",
         tts="They're often already included in the listing price. Look for three letters. F. A. I."),
    dict(scene="ch3", sub="Number three. The **property** **tax.**", tts="Number three. The property tax."),
    dict(scene="tax", sub="The taxe foncière is paid by the owner, **every** **single** **year.**",
         tts="The tax fon-see-air is paid by the owner, every single year."),
    dict(scene="map", sub="And location changes everything. The same money buys a **village** **house** in central France, or barely a **studio** on the Riviera.",
         tts="And location changes everything. The same money buys a village house in central France, or barely a studio on the Riviera."),
    dict(scene="end", sub="So, budget the price, plus about **10%.** Next: the five mistakes foreigners make when buying in France.",
         tts="So, budget the price, plus about ten percent. Next: the five mistakes foreigners make when buying in France."),
]
# transition INTO scene i+1 (after scene i)
TRANS = ["fade", "smoothleft", "slideleft", "smoothleft", "slideup", "smoothleft", "slideleft", "circleopen", "fadeblack"]
LEAD, GAP, TAIL = 0.4, 0.35, 2.2
SHORT_LAST = 3


# --------------------------------------------------------------------------- voice + timeline
def tts(i, text):
    raw = os.path.join(A, "voice", f"l{i:02d}_raw.wav")
    out = os.path.join(A, "voice", f"l{i:02d}.wav")
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
    d = len(v) / SR + GAP + (LEAD if i == 0 else 0) + (TAIL if i == len(voice) - 1 else 0)
    n = round(d * FPS)
    starts.append(t)
    frames.append(n)
    t += n / FPS
TOTAL = t
NS = int(round(TOTAL * SR))
line_times, line_dur = [], []
vt = np.zeros(NS, dtype=np.float32)
for i, v in enumerate(voice):
    s0 = int(round((starts[i] + (LEAD if i == 0 else 0)) * SR))
    vt[s0:s0 + len(v)] += v[: max(0, NS - s0)]
    line_times.append((s0 / SR, s0 / SR + len(v) / SR))
    line_dur.append(len(v) / SR)


def local_voice(i, frac):
    """Scene-local time at which `frac` of line i has been spoken."""
    return (line_times[i][0] - starts[i]) + frac * line_dur[i]


def write_wav(path, data, ch=1):
    pcm = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "w") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


write_wav(os.path.join(A, "voice.wav"), vt)

# --------------------------------------------------------------------------- easing / compositing
clamp = lambda x, a=0.0, b=1.0: max(a, min(b, x))
prog = lambda t, t0, t1: clamp((t - t0) / (t1 - t0))
ease_out = lambda u: 1 - (1 - u) ** 3


def ease_back(u, s=1.9):
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


def with_alpha(layer, a):
    if a >= 0.999:
        return layer
    r, g, b, al = layer.split()
    al = al.point(lambda v: int(v * a))
    return Image.merge("RGBA", (r, g, b, al))


def comp(base, layer, dx=0, dy=0, a=1.0):
    if a <= 0.001:
        return
    layer = with_alpha(layer, a)
    dx, dy = int(round(dx)), int(round(dy))
    sx, sy, tx, ty = max(0, -dx), max(0, -dy), max(0, dx), max(0, dy)
    w = min(layer.width - sx, base.width - tx)
    h = min(layer.height - sy, base.height - ty)
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
    x0 = clamp(cx - w / 2, 0, W - w)
    y0 = clamp(cy - h / 2, 0, H - h)
    return im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + w, y0 + h))


# --------------------------------------------------------------------------- 2x canvas
class Cv:
    def __init__(self, bg=None, size=(W, H)):
        self.s = S
        self.w, self.h = size
        if bg is None:
            self.im = Image.new("RGBA", (self.w * S, self.h * S), (0, 0, 0, 0))
        else:
            self.im = Image.new("RGBA", (self.w * S, self.h * S), bg + (255,))
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

    def poly(self, pts, fill, outline=None, width=0):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill)
        if outline:
            self.d.line([(x * S, y * S) for x, y in pts + [pts[0]]], fill=outline, width=width * S, joint="curve")

    def line(self, pts, fill, width):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=width * S, joint="curve")

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
        sh = sh.filter(ImageFilter.GaussianBlur(blur * S))
        self.im.alpha_composite(sh)
        self.d = ImageDraw.Draw(self.im, "RGBA")

    def out(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def gradient(cv, top, bottom):
    for y in range(cv.h * S):
        k = y / (cv.h * S - 1)
        cv.d.line([(0, y), (cv.w * S, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * k) for i in range(3)))


def diag_lines(cv, alpha=10):
    for i in range(-10, 30):
        x = i * 120
        cv.line([(x, 1080), (x + 700, 0)], (255, 255, 255, alpha), 2)


def draw_house(cv, ox, oy, k=1.0, seed=3):
    rnd = random.Random(seed)
    X = lambda v: ox + v * k
    Y = lambda v: oy - v * k
    cv.rect([X(330), Y(230), X(520), Y(0)], (214, 192, 156))
    cv.poly([(X(318), Y(230)), (X(532), Y(230)), (X(500), Y(300)), (X(330), Y(300))], (176, 78, 52))
    cv.rect([X(380), Y(170), X(450), Y(70)], (60, 76, 102), r=6 * k)
    cv.rect([X(0), Y(420), X(360), Y(0)], (226, 205, 166))
    for _ in range(140):
        x, y = rnd.uniform(8, 330), rnd.uniform(10, 400)
        w, h = rnd.uniform(18, 42), rnd.uniform(10, 20)
        shade = rnd.choice([(212, 188, 146), (219, 197, 157), (232, 214, 180)])
        cv.rect([X(x), Y(y + h), X(min(x + w, 352)), Y(y)], shade, r=4 * k)
    cv.poly([(X(-30), Y(420)), (X(390), Y(420)), (X(320), Y(560)), (X(40), Y(560))], (198, 90, 58))
    for i in range(1, 6):
        yy = 420 + i * 23
        cv.line([(X(-30 + 70 * (yy - 420) / 140), Y(yy)), (X(390 - 70 * (yy - 420) / 140), Y(yy))], (170, 70, 44), max(1, int(3 * k)))
    cv.rect([X(250), Y(610), X(290), Y(500)], (190, 160, 120))
    cv.rect([X(244), Y(620), X(296), Y(605)], (160, 132, 96))

    def window(x, y, w=64, h=84):
        for sx in (x - 30, x + w):
            cv.rect([X(sx), Y(y + h), X(sx + 30), Y(y)], (74, 120, 168), r=3 * k)
        for j in range(1, 6):
            yy = y + j * h / 6
            cv.line([(X(x - 28), Y(yy)), (X(x - 2), Y(yy))], (58, 98, 142), max(1, int(2 * k)))
            cv.line([(X(x + w + 2), Y(yy)), (X(x + w + 28), Y(yy))], (58, 98, 142), max(1, int(2 * k)))
        cv.rect([X(x), Y(y + h), X(x + w), Y(y)], (246, 238, 222))
        cv.rect([X(x + 6), Y(y + h - 6), X(x + w - 6), Y(y + 6)], (58, 74, 100))
        cv.line([(X(x + w / 2), Y(y + h - 6)), (X(x + w / 2), Y(y + 6))], (246, 238, 222), max(1, int(4 * k)))

    window(60, 260)
    window(236, 260)
    window(60, 70)
    cv.rect([X(222), Y(200), X(310), Y(0)], (104, 72, 52), r=10 * k)
    cv.rect([X(230), Y(190), X(302), Y(8)], (120, 84, 60), r=8 * k)
    cv.ellipse([X(286), Y(104), X(296), Y(94)], YEL)
    for x in (190, 330):
        cv.ellipse([X(x - 26), Y(52), X(x + 26), Y(0)], (92, 132, 76))
        cv.ellipse([X(x - 12), Y(70), X(x + 22), Y(30)], (112, 156, 90))


def landscape(cv):
    gradient(cv, (244, 214, 170), (252, 243, 228))
    cv.ellipse([170, 130, 330, 290], (250, 205, 120))
    cv.poly([(0, 700)] + [(x, 640 - 40 * math.sin(x / 260) - 25 * math.sin(x / 90)) for x in range(0, 1921, 40)] + [(1920, 1080), (0, 1080)], (196, 206, 160))
    cv.poly([(0, 800)] + [(x, 760 - 30 * math.sin(x / 330 + 1)) for x in range(0, 1921, 40)] + [(1920, 1080), (0, 1080)], (150, 178, 112))
    cv.poly([(0, 900), (1920, 880), (1920, 1080), (0, 1080)], (128, 160, 96))
    for x, h in ((1270, 330), (1330, 270)):
        cv.ellipse([x - 34, 880 - h, x + 34, 890], (70, 102, 60))
    for x in (380, 450):
        cv.ellipse([x - 70, 660, x + 70, 800], (104, 140, 80))
        cv.rect([x - 8, 780, x + 8, 880], (110, 84, 60))
    cv.poly([(860, 880), (920, 880), (1010, 1080), (790, 1080)], (232, 214, 176))


def house_bg():
    cv = Cv(CREAM)
    landscape(cv)
    draw_house(cv, 640, 880, k=1.15)
    return cv.out()


def make_tag(text, extra=None, angle=-6):
    tw = 620 if not extra else 820
    c = Cv(None, size=(tw + 80, 300))
    c.rect([40, 40, 40 + tw, 250], (255, 255, 255, 255), r=34)
    c.ellipse([70, 128, 100, 158], (226, 205, 166, 255))
    c.text((128, 147), text, "Inter-ExtraBold.otf", 104, INK, anchor="lm")
    if extra:
        c.text((128 + c.tlen(text, "Inter-ExtraBold.otf", 104) + 22, 147), extra, "Inter-ExtraBold.otf", 104, RED, anchor="lm")
    tag = c.out().rotate(angle, expand=True, resample=Image.BICUBIC)
    sh = Image.new("RGBA", tag.size, (0, 0, 0, 0))
    sh.paste((10, 15, 30, 90), (0, 0), tag.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    full = Image.new("RGBA", (tag.width, tag.height + 20), (0, 0, 0, 0))
    full.alpha_composite(sh, (0, 14))
    full.alpha_composite(tag, (0, 0))
    return full


def tag_x(spr):
    return min(1240, 1880 - spr.width)


# --------------------------------------------------------------------------- scenes (each returns frame(t) -> RGBA)
def scene_house(dur):
    bg = house_bg()
    tag = make_tag("€100,000")
    tx = tag_x(tag)

    def frame(t):
        im = bg.copy()
        u = prog(t, 0.15, 0.7)
        y = -480 + (140 + 480) * ease_back(u, 1.4) if u > 0 else -1000
        comp(im, tag, tx, y)
        return camera(im, 1 + 0.05 * t / dur, 960, 520)
    return frame, [("whoosh_down", 0.05, 0.5), ("impact", 0.62, 0.9)]


def scene_house_q(dur):
    bg = house_bg()
    tag1, tag2 = make_tag("€100,000"), make_tag("€100,000", "+ ?")
    T = 0.45

    def frame(t):
        im = bg.copy()
        if t < T:
            comp(im, tag1, tag_x(tag1), 140)
        else:
            u = prog(t, T, T + 0.35)
            sc = 1 + 0.14 * math.sin(math.pi * u) if u < 1 else 1
            shake = 10 * math.sin((t - T) * 70) * math.exp(-(t - T) * 9)
            sprite_at(im, tag2, tag_x(tag2) + tag2.width / 2 + shake, 140 + tag2.height / 2, sc)
        return camera(im, 1.03 + 0.04 * t / dur, 1000, 480)
    return frame, [("impact", T, 1.0), ("pop", T + 0.02, 0.6)]


def scene_chapter(n, title):
    def build(dur):
        bgc = Cv(NAVY)
        diag_lines(bgc)
        bg = bgc.out()
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
            for c in "COST":
                d.text((940 + 120 * (1 - u) + x, 360), c, font=fk, fill=SOFT + (a,), anchor="ls")
                x += d.textlength(c, font=fk) + 5
            d.text((936 + 160 * (1 - u), 440), title, font=ft, fill=WHITE + (a,), anchor="ls")
            w = 400 * ease_out(prog(t, 0.3, 0.65))
            if w > 2:
                d.rounded_rectangle([760, 520, 760 + w, 528], 4, fill=YEL)
            d.text((760, 590), "3 costs nobody mentions", font=fs, fill=SOFT + (int(255 * prog(t, 0.5, 0.8)),), anchor="ls")
            return camera(im, 1 + 0.03 * t / dur, 960, 450)
        return frame, [("pop", 0.08, 0.8)]
    return build


def scene_counter(dur):
    bgc = Cv(NAVY)
    diag_lines(bgc, 8)
    bgc.text((960, 250), "WHAT YOU ACTUALLY PAY", "Inter-SemiBold.otf", 34, SOFT, anchor="ms", spacing=6)
    bg = bgc.out()
    f_big, f_pill, f_lab = F("Inter-ExtraBold.otf", 190), F("Inter-Bold.otf", 44), F("Inter-SemiBold.otf", 30)
    c0, c1 = 0.6, 2.2

    def frame(t):
        u = ease_out(prog(t, c0, c1))
        im = bg.copy()
        d = ImageDraw.Draw(im, "RGBA")
        punch = 1 + 0.06 * math.sin(math.pi * prog(t, c1 - 0.05, c1 + 0.25))
        num = Image.new("RGBA", (1100, 260), (0, 0, 0, 0))
        ImageDraw.Draw(num).text((550, 210), f"€{int(round((100000 + 7500 * u) / 100) * 100):,}", font=f_big, fill=WHITE, anchor="ms")
        sprite_at(im, num, 960, 520 - 210 + 130, punch)
        x0, x1, y0, y1 = 460, 1460, 620, 664
        d.rounded_rectangle([x0, y0, x1, y1], 22, fill=(255, 255, 255, 30))
        pw = (x1 - x0) * 100000 / 112000
        if u > 0:
            d.rounded_rectangle([x0 + pw - 40, y0, x0 + pw + (x1 - x0) * 7500 / 112000 * u, y1], 22, fill=YEL)
        d.rounded_rectangle([x0, y0, x0 + pw, y1], 22, fill=(244, 233, 216))
        d.text((x0, 710), "listing price  €100,000", font=f_lab, fill=(200, 208, 225), anchor="ls")
        pa = prog(t, 1.3, 1.6)
        if pa > 0:
            pill = Image.new("RGBA", (620, 110), (0, 0, 0, 0))
            pd = ImageDraw.Draw(pill)
            tw = pd.textlength("+ 7–8% notary fees", font=f_pill)
            pd.rounded_rectangle([310 - tw / 2 - 34, 13, 310 + tw / 2 + 34, 97], 42, fill=YEL)
            pd.text((310, 71), "+ 7–8% notary fees", font=f_pill, fill=NAVY, anchor="ms")
            sprite_at(im, pill, 960, 822, ease_back(pa))
        return camera(im, 1 + 0.03 * t / dur, 960, 560)
    ticks = [("tick", c0 + k * 0.075, 0.55 * (1 - k / 24)) for k in range(22)]
    return frame, ticks + [("ding", 1.3, 0.8), ("pop", c1, 0.5)]


def scene_listing(dur, i):
    bgc = Cv(CREAM)
    gradient(bgc, (250, 242, 229), (242, 230, 210))
    bg = bgc.out()
    card = Cv(None)
    card.shadow([300, 230, 1620, 830], 36, blur=24, alpha=60, dy=16)
    card.rect([300, 230, 1620, 830], WHITE, r=36)
    hb = house_bg().crop((400, 160, 1280, 1040)).resize((520 * S, 520 * S), Image.LANCZOS)
    mask = Image.new("L", hb.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, hb.width - 1, hb.height - 1], 26 * S, fill=255)
    hb.putalpha(mask)
    card.im.alpha_composite(hb, (340 * S, 270 * S))
    card.text((920, 330), "VILLAGE HOUSE · 3 BEDROOMS · CREUSE", "Inter-SemiBold.otf", 28, MUTED, anchor="ls", spacing=3)
    card.text((920, 440), "Stone house with garden", "Inter-Bold.otf", 52, INK, anchor="ls")
    card.text((920, 590), "€100,000", "Inter-ExtraBold.otf", 92, INK, anchor="ls")
    fx = 920 + card.tlen("€100,000", "Inter-ExtraBold.otf", 92) + 30
    fw = card.tlen("FAI", "Inter-ExtraBold.otf", 92)
    card = card.out()
    note = Cv(None)
    note.line([(fx + 110, 640), (fx + 60, 700), (fx - 40, 728)], RED, 6)
    note.poly([(fx - 40, 728), (fx - 6, 708), (fx - 14, 744)], RED)
    note.text((920, 742), "= frais d'agence inclus", "Inter-SemiBold.otf", 40, RED, anchor="ls")
    note.text((920, 792), "agency fees included", "Inter-Medium.otf", 34, MUTED, anchor="ls")
    note = note.out()
    f_fai = F("Inter-ExtraBold.otf", 92)
    hl = local_voice(i, 0.66)

    def frame(t):
        im = bg.copy()
        u = ease_out(prog(t, 0.0, 0.5))
        dy = 160 * (1 - u)
        comp(im, card, 0, dy, prog(t, 0, 0.3))
        d = ImageDraw.Draw(im, "RGBA")
        w = (fw + 28) * ease_out(prog(t, hl, hl + 0.25))
        if w > 2:
            d.rounded_rectangle([fx - 14, 508 + dy, fx - 14 + w, 608 + dy], 14, fill=YEL)
        d.text((fx, 590 + dy), "FAI", font=f_fai, fill=INK + (int(255 * prog(t, 0, 0.3)),), anchor="ls")
        na = prog(t, hl + 0.3, hl + 0.6)
        comp(im, note, -30 * (1 - ease_out(na)), 0, na)
        return camera(im, 1 + 0.035 * t / dur, fx, 560)
    return frame, [("swipe", hl, 0.8), ("pop", hl + 0.3, 0.6)]


def scene_tax(dur, i):
    bgc = Cv(NAVY)
    bg = bgc.out()
    card = Cv(None)
    card.shadow([560, 120, 1360, 850], 28, blur=30, alpha=120, dy=20)
    card.rect([560, 120, 1360, 850], (248, 246, 240), r=28)
    card.rect([560, 120, 1360, 240], (234, 228, 214), r=28)
    card.rect([560, 200, 1360, 240], (234, 228, 214))
    card.text((620, 195), "AVIS D'IMPÔT", "Inter-Bold.otf", 34, INK, anchor="ls", spacing=4)
    card.text((1300, 195), "TAXE FONCIÈRE", "Inter-Bold.otf", 34, RED, anchor="rs")
    for k, w in enumerate((520, 600, 440)):
        card.rect([620, 290 + k * 44, 620 + w, 306 + k * 44], (214, 210, 200), r=8)
    card = card.out()
    boxes = []
    for yr in ("2027", "2028", "2029", "2030"):
        b = Cv(None, size=(170, 200))
        b.rect([10, 10, 160, 190], WHITE, r=18, outline=(214, 210, 200), width=3)
        b.rect([10, 10, 160, 58], RED, r=18)
        b.rect([10, 40, 160, 58], RED)
        b.text((85, 45), yr, "Inter-Bold.otf", 28, WHITE, anchor="mm")
        b.line([(54, 128), (78, 152), (118, 100)], GREEN, 9)
        boxes.append(b.out())
    f1, f2 = F("Inter-ExtraBold.otf", 44), F("Inter-Medium.otf", 32)
    y0 = local_voice(i, 0.55)
    times = [y0 + k * 0.2 for k in range(4)]
    ta = local_voice(i, 0.85)

    def frame(t):
        im = bg.copy()
        u = ease_out(prog(t, 0, 0.45))
        sprite_at(im, card, 960, 540 + 60 * (1 - u), 0.94 + 0.06 * u, prog(t, 0, 0.3))
        for k, b in enumerate(boxes):
            sprite_at(im, b, 620 + k * 182 + 75, 540, ease_back(prog(t, times[k], times[k] + 0.3)))
        a = prog(t, ta, ta + 0.35)
        d = ImageDraw.Draw(im, "RGBA")
        d.text((960, 730 + 20 * (1 - a)), "Paid by the owner — every year", font=f1, fill=INK + (int(255 * a),), anchor="mm")
        d.text((960, 790 + 20 * (1 - a)), "add it to your monthly budget", font=f2, fill=MUTED + (int(255 * a),), anchor="mm")
        return camera(im, 1 + 0.03 * t / dur, 960, 500)
    return frame, [("pop", tt, 0.55 + 0.1 * k) for k, tt in enumerate(times)] + [("tick", tt + 0.12, 0.5) for tt in times]


FRANCE = [(2.54, 51.09), (1.85, 50.95), (1.6, 50.7), (1.55, 50.2), (1.08, 49.93), (0.1, 49.5), (-0.4, 49.33),
          (-1.1, 49.4), (-1.3, 49.7), (-1.95, 49.7), (-1.6, 49.2), (-1.5, 48.65), (-2.0, 48.65), (-3.0, 48.8),
          (-4.0, 48.7), (-4.75, 48.4), (-4.4, 48.0), (-3.5, 47.75), (-2.5, 47.5), (-2.2, 47.27), (-1.9, 46.7),
          (-1.2, 46.15), (-1.15, 45.6), (-1.25, 44.65), (-1.45, 43.9), (-1.55, 43.45), (-1.0, 43.1), (0.0, 42.8),
          (1.0, 42.6), (2.0, 42.4), (3.15, 42.43), (3.05, 42.8), (3.3, 43.25), (4.0, 43.55), (4.6, 43.4),
          (5.35, 43.3), (5.95, 43.1), (6.6, 43.2), (7.25, 43.7), (7.5, 43.78), (7.0, 44.2), (6.9, 44.7),
          (7.1, 45.2), (6.8, 45.8), (6.1, 46.15), (6.4, 46.5), (6.9, 47.35), (7.6, 47.6), (7.55, 48.1),
          (7.8, 48.6), (8.2, 48.97), (7.4, 49.15), (6.7, 49.2), (6.1, 49.5), (5.5, 49.5), (4.8, 49.95),
          (4.2, 49.95), (4.0, 50.35), (3.2, 50.75)]


def scene_map(dur, i):
    lon0, lat0, kx, sc = -5.0, 51.3, math.cos(math.radians(46.5)), 740 / (51.3 - 42.2)
    P = lambda lon, lat: (1020 + (lon - lon0) * kx * sc, 90 + (lat0 - lat) * sc)
    bgc = Cv(CREAM)
    gradient(bgc, (250, 242, 229), (240, 228, 208))
    pts = [P(*p) for p in FRANCE]
    bgc.poly([(x + 10, y + 14) for x, y in pts], (220, 204, 176))
    bgc.poly(pts, (236, 222, 196), outline=(196, 170, 128), width=5)
    px, py = P(2.35, 48.85)
    bgc.ellipse([px - 10, py - 10, px + 10, py + 10], INK)
    bgc.text((px + 18, py + 10), "Paris", "Inter-SemiBold.otf", 30, INK, anchor="ls")
    bg = bgc.out()
    title = Cv(None)
    title.text((120, 230), "€100,000", "Inter-ExtraBold.otf", 110, INK, anchor="ls")
    title.text((124, 300), "buys you…", "Inter-Bold.otf", 56, MUTED, anchor="ls")
    title = title.out()

    def pin_layer(lon, lat, color, t1, t2):
        c = Cv(None)
        x, y = P(lon, lat)
        c.ellipse([x - 22, y - 22, x + 22, y + 22], color, outline=WHITE, width=6)
        bx, by = x - 520, y - 70
        c.shadow([bx, by, bx + 480, by + 140], 20, blur=12, alpha=50, dy=8)
        c.rect([bx, by, bx + 480, by + 140], WHITE, r=20)
        c.rect([bx, by, bx + 14, by + 140], color, r=7)
        c.text((bx + 40, by + 58), t1, "Inter-ExtraBold.otf", 40, INK, anchor="ls")
        c.text((bx + 40, by + 108), t2, "Inter-Medium.otf", 32, MUTED, anchor="ls")
        return c.out()

    pins = [(pin_layer(2.0, 46.1, GREEN, "a whole village house", "central France (Creuse)"), local_voice(i, 0.5)),
            (pin_layer(7.25, 43.7, RED, "barely a studio", "French Riviera (Nice)"), local_voice(i, 0.84))]

    def frame(t):
        im = bg.copy()
        u = ease_out(prog(t, 0.1, 0.5))
        comp(im, title, -80 * (1 - u), 0, u)
        for layer, t0 in pins:
            v = prog(t, t0, t0 + 0.4)
            comp(im, layer, 0, -50 * (1 - ease_back(v)) if v > 0 else 0, prog(t, t0, t0 + 0.15))
        return camera(im, 1 + 0.04 * t / dur, 1200, 560)
    return frame, [("pop", pins[0][1], 0.7), ("pop", pins[1][1], 0.75)]


def scene_end(dur):
    bgc = Cv(NAVY)
    bg = bgc.out()
    ttl = Cv(None, size=(1300, 160))
    ttl.text((650, 120), "Budget = price + ~10%", "Inter-ExtraBold.otf", 96, WHITE, anchor="ms")
    ttl = ttl.out()
    ph = Cv(None)
    ph.rect([240, 420, 1040, 870], NAVY2, r=24, outline=(80, 100, 140), width=3)
    ph.text((640, 630), "NEXT VIDEO", "Inter-Bold.otf", 40, SOFT, anchor="mm", spacing=6)
    ph.text((640, 690), "5 mistakes foreigners make", "Inter-Medium.otf", 34, (130, 145, 180), anchor="mm")
    ph.ellipse([1260, 450, 1650, 840], NAVY2, outline=(80, 100, 140), width=3)
    ph.text((1455, 645), "SUBSCRIBE", "Inter-Bold.otf", 38, SOFT, anchor="mm", spacing=6)
    ph = ph.out()

    def frame(t):
        im = bg.copy()
        sprite_at(im, ttl, 960, 210 - 120 + 80, ease_back(prog(t, 0.1, 0.45)))
        w = 520 * ease_out(prog(t, 0.35, 0.7))
        if w > 2:
            ImageDraw.Draw(im).rounded_rectangle([960 - w / 2, 250, 960 + w / 2, 258], 4, fill=YEL)
        a = prog(t, 0.9, 1.3)
        comp(im, ph, 0, 40 * (1 - ease_out(a)), a)
        return camera(im, 1 + 0.02 * t / dur)
    return frame, [("ding", 0.12, 0.6), ("whoosh_up", 0.85, 0.35)]


SCENES = {
    "house": lambda d, i: scene_house(d),
    "house_q": lambda d, i: scene_house_q(d),
    "ch1": lambda d, i: scene_chapter(1, "Notary fees")(d),
    "ch2": lambda d, i: scene_chapter(2, "Agency fees")(d),
    "ch3": lambda d, i: scene_chapter(3, "Property tax")(d),
    "counter": lambda d, i: scene_counter(d),
    "listing": scene_listing,
    "tax": scene_tax,
    "map": scene_map,
    "end": lambda d, i: scene_end(d),
}

# --------------------------------------------------------------------------- render shots
sfx_events = []
segs = []
for i, l in enumerate(LINES):
    n = frames[i] + (TDF if i < len(LINES) - 1 else 0)
    dur = n / FPS
    frame_fn, ev = SCENES[l["scene"]](dur, i)
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
    print("shot", i, l["scene"], f"{dur:.2f}s", flush=True)

# xfade chain: each shot (except last) carries TD extra seconds that overlap the next one
cmd = ["ffmpeg", "-y"]
for s in segs:
    cmd += ["-i", s]
fc, prev, off = [], "[0:v]", 0.0
for k in range(1, len(segs)):
    off += frames[k - 1] / FPS
    out = f"[x{k}]"
    fc.append(f"{prev}[{k}:v]xfade=transition={TRANS[k - 1]}:duration={TD}:offset={off:.4f}{out}")
    prev = out
    if TRANS[k - 1] != "fade":
        sfx_events.append(("whoosh", off - 0.08, 0.7))
nosub = os.path.join(A, "video_nosub.mp4")
run(cmd + ["-filter_complex", ";".join(fc), "-map", prev, "-c:v", "libx264", "-preset", "medium", "-crf", "16",
           "-pix_fmt", "yuv420p", "-r", str(FPS), nosub])

# --------------------------------------------------------------------------- sound design
rng = np.random.default_rng(7)


def onepole_sweep(x, f0, f1):
    fc = np.geomspace(f0, f1, len(x))
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for k in range(len(x)):
        acc += a[k] * (x[k] - acc)
        y[k] = acc
    return y


def sfx_whoosh(dur=0.55, up=True):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    y = onepole_sweep(x, 250, 5000) if up else onepole_sweep(x, 5000, 250)
    y -= onepole_sweep(y, 120, 120)  # remove rumble
    t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t ** (0.7 if up else 1.3)) ** 2
    return y * env


def sfx_pop(f0=1100, f1=380, dur=0.12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.018)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.035) + 0.3 * rng.standard_normal(n) * np.exp(-t / 0.003)


def sfx_impact(dur=0.7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 42 + 70 * np.exp(-t / 0.05)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    hit = onepole_sweep(rng.standard_normal(n), 2500, 300) * np.exp(-t / 0.04)
    return body + 0.8 * hit


def sfx_tick(dur=0.03):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2600 * t) * np.exp(-t / 0.005) + 0.4 * rng.standard_normal(n) * np.exp(-t / 0.002)


def sfx_ding(dur=1.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in ((1568, 1, 0.45), (2349, 0.6, 0.3), (3136, 0.3, 0.18)))
    return s * np.minimum(1, t / 0.004)


def sfx_swipe(dur=0.3):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    hp = x - onepole_sweep(x, 1800, 1800)
    y = onepole_sweep(hp, 6000, 6000)
    t = np.linspace(0, 1, n)
    return y * np.sin(np.pi * t) ** 1.5


BANK = {
    "whoosh": sfx_whoosh(0.55, True),
    "whoosh_up": sfx_whoosh(0.5, True),
    "whoosh_down": sfx_whoosh(0.6, False),
    "pop": sfx_pop(),
    "impact": sfx_impact(),
    "tick": sfx_tick(),
    "ding": sfx_ding(),
    "swipe": sfx_swipe(),
}
for k in BANK:
    BANK[k] = BANK[k] / (np.max(np.abs(BANK[k])) + 1e-9)
LEVEL = {"whoosh": 0.22, "whoosh_up": 0.18, "whoosh_down": 0.22, "pop": 0.35, "impact": 0.55, "tick": 0.18, "ding": 0.22, "swipe": 0.2}
sfx = np.zeros(NS + SR, dtype=np.float32)
for name, at, g in sfx_events:
    s = BANK[name] * LEVEL[name] * g
    i0 = int(max(0, at) * SR)
    sfx[i0:i0 + len(s)] += s[: len(sfx) - i0]
sfx = sfx[:NS]
write_wav(os.path.join(A, "sfx.wav"), sfx)


def music(seconds):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    chords = [[48, 52, 55, 59], [45, 48, 52, 55], [41, 45, 48, 52], [43, 47, 50, 55]]
    clen, mtof = 4.0, (lambda m: 440 * 2 ** ((m - 69) / 12))
    pad = np.zeros(n)
    for k in range(int(seconds / clen) + 1):
        st = k * clen
        i0, i1 = int(st * SR), min(n, int((st + clen + 1.5) * SR))
        if i0 >= n:
            break
        tt = t[i0:i1] - st
        env = np.minimum(1, tt / 1.5) * np.clip(1 - (tt - clen) / 1.5, 0, 1)
        sig = np.zeros_like(tt)
        for m in chords[k % 4]:
            f = mtof(m)
            sig += np.sin(2 * np.pi * f * tt) + 0.6 * np.sin(2 * np.pi * f * 1.004 * tt + 1) + 0.15 * np.sin(4 * np.pi * f * tt)
        sig += 1.2 * np.sin(2 * np.pi * mtof(chords[k % 4][0] - 12) * tt)
        pad[i0:i1] += sig * env
    pl = np.zeros(n)
    pattern = [0, 2, 3, 1, 2, 3, 1, 2]
    for k in range(int(seconds / 0.25)):
        st = k * 0.25
        if k % 2:
            continue
        m = chords[int(st // clen) % 4][pattern[(k // 2) % 8]] + 12
        i0, i1 = int(st * SR), min(n, int((st + 1.2) * SR))
        tt = t[i0:i1] - st
        pl[i0:i1] += (np.sin(2 * np.pi * mtof(m) * tt) + 0.3 * np.sin(4 * np.pi * mtof(m) * tt)) * np.exp(-tt * 3.5)
    beat = np.zeros(n)
    kick_t = np.arange(int(0.25 * SR)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-kick_t / 0.03)) / SR) * np.exp(-kick_t / 0.12)
    hat_t = np.arange(int(0.05 * SR)) / SR
    hat_n = rng.standard_normal(len(hat_t))
    hat = (hat_n - onepole_sweep(hat_n, 6000, 6000)) * np.exp(-hat_t / 0.012)
    for k in range(int(seconds / 0.5)):
        st = k * 0.5
        if st < 2.0:  # beat comes in after the intro
            continue
        i0 = int(st * SR)
        beat[i0:i0 + len(kick)] += kick[: n - i0] * (1.0 if k % 2 == 0 else 0.7)
        h0 = int((st + 0.25) * SR)
        beat[h0:h0 + len(hat)] += hat[: max(0, n - h0)] * 0.35
    mix = pad * 0.10 + pl * 0.2 + beat * 0.35
    mix *= np.minimum(1, t / 1.5) * np.clip((seconds - t) / 2.5, 0, 1)
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.5
    right = np.concatenate([np.zeros(int(0.012 * SR)), mix])[:n]
    st = np.empty(2 * n, dtype=np.float32)
    st[0::2], st[1::2] = mix, right
    return st


write_wav(os.path.join(A, "music.wav"), music(TOTAL + 0.5), ch=2)
run(["ffmpeg", "-y", "-i", os.path.join(A, "voice.wav"), "-i", os.path.join(A, "music.wav"), "-i", os.path.join(A, "sfx.wav"),
     "-filter_complex",
     "[0:a]aformat=channel_layouts=stereo,highpass=f=90,acompressor=threshold=-20dB:ratio=3:attack=5:release=90,asplit=2[v1][v2];"
     "[1:a]lowpass=f=5000,volume=0.24[m];"
     "[m][v1]sidechaincompress=threshold=0.015:ratio=6:attack=20:release=400[md];"
     "[2:a]aformat=channel_layouts=stereo,volume=0.5[fx];"
     "[v2][md][fx]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
     "-map", "[out]", "-ar", str(SR), os.path.join(A, "mix.wav")])


# --------------------------------------------------------------------------- captions (pop-in)
def ass_time(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def chunks(sub, max_words=7):
    out, cur = [], []
    for w in sub.split():
        cur.append(w)
        c = w.replace("*", "")
        if len(cur) >= max_words or (c[-1:] in ".:?!…" and len(cur) >= 2) or (c[-1:] == "," and len(cur) >= 4):
            out.append(cur)
            cur = []
    if cur:
        if out and len(cur) <= 2:
            out[-1] += cur
        else:
            out.append(cur)
    return [" ".join(c) for c in out]


def styled(txt):
    return re.sub(r"\*\*(.+?)\*\*", r"{\\c&H3CC9FF&}\1{\\c&HFFFFFF&}", txt)


POP = r"{\fscx86\fscy86\t(0,110,\fscx104\fscy104)\t(110,180,\fscx100\fscy100)}"


def write_ass(path, playres, style, events_until=None, extra=""):
    ev = []
    for i, l in enumerate(LINES):
        if events_until is not None and i > events_until:
            break
        t0, t1 = line_times[i]
        parts = chunks(l["sub"])
        lens = [len(p.replace("*", "")) for p in parts]
        t = t0
        for p, n in zip(parts, lens):
            d = (t1 - t0) * n / sum(lens)
            ev.append(f"Dialogue: 0,{ass_time(t)},{ass_time(t + d + 0.05)},Sub,,0,0,0,,{POP}{styled(p)}")
            t += d
    with open(path, "w") as f:
        f.write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {playres[0]}
PlayResY: {playres[1]}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n" + extra)


write_ass(os.path.join(A, "subs.ass"), (W, H),
          "Style: Sub,Inter ExtraBold,56,&H00FFFFFF,&H00FFFFFF,&H003D2114,&H00000000,0,0,0,0,100,100,0.5,0,3,12,0,2,160,160,62,1")
final = os.path.join(O, "demo2_16x9.mp4")
run(["ffmpeg", "-y", "-i", nosub, "-i", os.path.join(A, "mix.wav"), "-vf",
     f"ass={os.path.join(A, 'subs.ass')}:fontsdir={FD},fade=t=in:st=0:d=0.3,fade=t=out:st={TOTAL - 0.7:.2f}:d=0.7",
     "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", "-shortest", final])

# --------------------------------------------------------------------------- Short (9:16)
short_end = starts[SHORT_LAST] + frames[SHORT_LAST] / FPS
title = ("Dialogue: 1,0:00:00.00," + ass_time(short_end) +
         ",Title,,0,0,0,,{\\fad(250,0)}The {\\c&H3CC9FF&}REAL{\\c&HFFFFFF&} price of a\\N€100,000 house in France\n")
write_ass(os.path.join(A, "short.ass"), (1080, 1920),
          "Style: Sub,Inter ExtraBold,76,&H00FFFFFF,&H00FFFFFF,&H00141414,&H64000000,0,0,0,0,100,100,0,0,1,6,2,2,90,90,430,1\n"
          "Style: Title,Inter ExtraBold,70,&H00FFFFFF,&H00FFFFFF,&H00141414,&H64000000,0,0,0,0,100,100,0,0,1,6,2,8,80,80,250,1",
          events_until=SHORT_LAST, extra=title)
short = os.path.join(O, "demo2_short_9x16.mp4")
run(["ffmpeg", "-y", "-t", f"{short_end:.3f}", "-i", nosub, "-t", f"{short_end:.3f}", "-i", os.path.join(A, "mix.wav"),
     "-filter_complex",
     "[0:v]split=2[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.18[bg];"
     "[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-60,"
     f"ass={os.path.join(A, 'short.ass')}:fontsdir={FD},fade=t=in:st=0:d=0.3,fade=t=out:st={short_end - 0.5:.2f}:d=0.5[v];"
     f"[1:a]afade=t=out:st={short_end - 0.6:.2f}:d=0.6[au]",
     "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", short])
print(f"total={TOTAL:.2f}s short={short_end:.2f}s sfx={len(sfx_events)}")
