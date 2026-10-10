"""v5: v2 edit + price tracker, chapter bar, subscribe reminder, punch zooms, lo-fi music,
and two caption styles (karaoke / big words). Reuses assets2 (shots, voice, v2 SFX)."""
import math
import os
import re
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(D, "assets2")
O = os.path.join(D, "out5")
os.makedirs(O, exist_ok=True)
FD = "/usr/share/fonts/opentype/inter/"
W, H, S, SR, FPS = 1920, 1080, 2, 44100, 30
LEAD, GAP, TAIL = 0.4, 0.35, 2.2
SHORT_LAST = 3
NAVY, YEL, WHITE, SOFT, RED = (20, 33, 61), (255, 201, 60), (255, 255, 255), (170, 182, 210), (204, 30, 30)

_f = {}


def F(name, size):
    k = (name, int(size))
    if k not in _f:
        _f[k] = ImageFont.truetype(FD + name, int(size))
    return _f[k]


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# --------------------------------------------------------------------------- timeline + word timings
SUBS = [
    "This house in rural France costs **€100,000.**",
    "But that's not what you'll **actually** pay. Here are three costs nobody mentions.",
    "Number one. **Notary** **fees.**",
    "On an older home, they're around **7–8%** of the price. Roughly **€7,500,** on top.",
    "Number two. **Agency** **fees.**",
    "They're often already **included** in the listing price. Look for three letters. **F.** **A.** **I.**",
    "Number three. The **property** **tax.**",
    "The taxe foncière is paid by the owner, **every** **single** **year.**",
    "And location changes everything. The same money buys a **village** **house** in central France, or barely a **studio** on the Riviera.",
    "So, budget the price, plus about **10%.** Next: the five mistakes foreigners make when buying in France.",
]
SCENES = ["house", "house_q", "ch1", "counter", "ch2", "listing", "ch3", "tax", "map", "end"]
voice = []
for i in range(len(SUBS)):
    with wave.open(os.path.join(A, "voice", f"l{i:02d}.wav")) as w:
        voice.append(np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768)
starts, frames, t = [], [], 0.0
for i, v in enumerate(voice):
    n = round((len(v) / SR + GAP + (LEAD if i == 0 else 0) + (TAIL if i == len(voice) - 1 else 0)) * FPS)
    starts.append(t)
    frames.append(n)
    t += n / FPS
TOTAL = t
NS = int(round(TOTAL * SR))
line_times = [(starts[i] + (LEAD if i == 0 else 0), starts[i] + (LEAD if i == 0 else 0) + len(v) / SR) for i, v in enumerate(voice)]
SC = {name: (starts[i], starts[i] + frames[i] / FPS) for i, name in enumerate(SCENES)}


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


WEAK = {"the", "a", "an", "of", "in", "by", "when", "to", "for", "on", "and", "or", "about", "what", "that's", "you'll", "is", "are", "be"}
cl = lambda w: w.replace("*", "")


def _split(words, mx=7):
    if len(words) <= mx:
        return [words]
    target = round(len(words) / -(-len(words) // mx))
    commas = [j + 1 for j, w in enumerate(words[:-1]) if cl(w).endswith(",") and j + 1 >= 3 and len(words) - j - 1 >= 3]
    cut = min(commas, key=lambda c: abs(c - len(words) / 2)) if commas else target
    while cut > 1 and cl(words[cut - 1]).lower().strip(",") in WEAK:
        cut -= 1
    return _split(words[:cut], mx) + _split(words[cut:], mx)


def chunks(sub):
    sents, cur = [], []
    for w in sub.split():
        cur.append(w)
        if cl(w)[-1:] in ".:?!…" and not re.fullmatch(r"[A-Z]\.", cl(w)):
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
    parts = chunks(SUBS[i])
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


WT = [word_times(i) for i in range(len(SUBS))]


def when(i, word):
    for w, a, b in WT[i]:
        if cl(w).lower().rstrip(".,") == word.lower().rstrip(".,"):
            return a
    raise KeyError(word)


PUNCH = [when(0, "€100,000"), when(1, "actually"), when(3, "7–8%"), when(3, "€7,500"), when(5, "included"),
         when(5, "F."), when(7, "every"), when(8, "village"), when(8, "studio"), when(9, "10%")]
T_FAI, T_TAX = when(5, "F."), when(7, "every")

# --------------------------------------------------------------------------- sprites
clamp = lambda x, a=0.0, b=1.0: max(a, min(b, x))
prog = lambda t, t0, t1: clamp((t - t0) / (t1 - t0))
ease_out = lambda u: 1 - (1 - u) ** 3


def ease_back(u, s=1.7):
    u -= 1
    return u * u * ((s + 1) * u + s) + 1


def sprite(size, draw):
    im = Image.new("RGBA", (size[0] * S, size[1] * S), (0, 0, 0, 0))
    draw(ImageDraw.Draw(im, "RGBA"))
    return im.resize(size, Image.LANCZOS)


def with_alpha(im, a):
    if a >= 0.999:
        return im
    r, g, b, al = im.split()
    return Image.merge("RGBA", (r, g, b, al.point(lambda v: int(v * a))))


def paste(base, spr, x, y, a=1.0, scale=1.0):
    if a <= 0.001:
        return
    if abs(scale - 1) > 0.003:
        spr = spr.resize((int(spr.width * scale), int(spr.height * scale)), Image.BICUBIC)
    spr = with_alpha(spr, a)
    base.paste(spr, (int(round(x - spr.width / 2)), int(round(y - spr.height / 2))), spr)


CARD_W, CARD_H = 400, 124
card_bg = sprite((CARD_W, CARD_H), lambda d: (
    d.rounded_rectangle([0, 0, CARD_W * S - 1, CARD_H * S - 1], 20 * S, fill=NAVY + (236,)),
    d.rounded_rectangle([0, 0, 8 * S, CARD_H * S - 1], 4 * S, fill=YEL)))
BAR_X0, BAR_W = 600, 720
bar_bg = sprite((BAR_W, 52), lambda d: d.rounded_rectangle([0, 0, BAR_W * S - 1, 52 * S - 1], 26 * S, fill=NAVY + (220,)))


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


btn_red, btn_done = _btn(RED, "SUBSCRIBE"), _btn((70, 70, 78), "SUBSCRIBED", check=True)
cursor = sprite((44, 60), lambda d: d.polygon([(4 * S, 2 * S), (4 * S, 48 * S), (16 * S, 37 * S), (25 * S, 57 * S), (33 * S, 53 * S), (24 * S, 34 * S), (40 * S, 33 * S)],
                                               fill=WHITE, outline=(0, 0, 0), width=3 * S))

CH = [("NOTARY", SC["ch1"][0], SC["ch2"][0]), ("AGENCY", SC["ch2"][0], SC["ch3"][0]), ("TAX", SC["ch3"][0], SC["map"][0])]
CARD_WINDOWS = [(1.6, SC["counter"][0]), (SC["ch2"][0] + 0.2, SC["map"][0])]
SUB_T0 = SC["listing"][0] + 0.9


def card_state(t):
    if t < SC["counter"][0]:
        return "€100,000", "listing price", None
    if t < T_FAI:
        return "€107,500", "+ notary fees", SC["ch2"][0] + 0.2
    if t < T_TAX:
        return "€107,500", "agency fees: often included", T_FAI
    return "€107,500", "+ property tax, every year", T_TAX


def overlays(im, t):
    d = ImageDraw.Draw(im, "RGBA")
    # price tracker (top-left)
    for w0, w1 in CARD_WINDOWS:
        if w0 - 0.01 <= t <= w1 + 0.3:
            a = min(prog(t, w0, w0 + 0.3), 1 - prog(t, w1, w1 + 0.3))
            num, line, tu = card_state(t)
            c = card_bg.copy()
            cd = ImageDraw.Draw(c, "RGBA")
            x = 26
            for ch in "REAL COST":
                cd.text((x, 34), ch, font=F("Inter-SemiBold.otf", 19), fill=SOFT, anchor="ls")
                x += cd.textlength(ch, font=F("Inter-SemiBold.otf", 19)) + 3
            cd.text((24, 80), num, font=F("Inter-ExtraBold.otf", 44), fill=WHITE, anchor="ls")
            la = prog(t, tu, tu + 0.25) if tu else 1
            cd.text((26, 108), line, font=F("Inter-SemiBold.otf", 20), fill=YEL + (int(255 * la),), anchor="ls")
            pop = 1 + 0.09 * math.sin(math.pi * prog(t, tu, tu + 0.3)) if tu else 1
            paste(im, c, 40 + CARD_W / 2 - 30 * (1 - ease_out(a)), 44 + CARD_H / 2, a, pop)
    # chapter bar (top-center)
    t0, t1 = CH[0][1], SC["end"][0]
    if t0 <= t <= t1 + 0.3:
        a = min(prog(t, t0, t0 + 0.4), 1 - prog(t, t1, t1 + 0.3))
        paste(im, bar_bg, BAR_X0 + BAR_W / 2, 18 + 26, a)
        for k, (lab, c0, c1) in enumerate(CH):
            x = BAR_X0 + 30 + k * 230
            p = prog(t, c0, c1)
            cur = c0 <= t < c1
            col = (WHITE if cur else SOFT) + (int(255 * a * (1 if t >= c0 else 0.55)),)
            d.text((x, 38), f"{k + 1}  {lab}", font=F("Inter-Bold.otf", 17), fill=col, anchor="ls")
            d.rounded_rectangle([x, 47, x + 200, 52], 3, fill=(255, 255, 255, int(55 * a)))
            if p > 0:
                d.rounded_rectangle([x, 47, x + max(6, 200 * p), 52], 3, fill=YEL + (int(255 * a),))
    # subscribe reminder (top-right)
    u = t - SUB_T0
    if 0 <= u <= 3.0:
        slide = ease_out(prog(u, 0, 0.3)) * (1 - ease_out(prog(u, 2.6, 2.9)))
        bx, by = 1960 + 160 - (1960 + 160 - 1720) * slide, 90
        pressed = 0.92 if 1.6 <= u < 1.72 else 1.0
        paste(im, btn_done if u >= 1.66 else btn_red, bx, by, 1.0, pressed)
        if 1.0 <= u <= 2.4:
            m = ease_out(prog(u, 1.0, 1.55))
            cx, cy = 1900 + (1760 - 1900) * m, 300 + (108 - 300) * m
            paste(im, cursor, cx + 18, cy + 26, 1 - prog(u, 2.1, 2.4))


def punch_zoom(t):
    z = 0.0
    for tp in PUNCH:
        u = t - tp
        if 0 <= u < 0.06:
            z = max(z, ease_out(u / 0.06))
        elif 0.06 <= u < 0.5:
            z = max(z, 1 - ease_out((u - 0.06) / 0.44))
    return 1 + 0.07 * z


# --------------------------------------------------------------------------- video pass
src = os.path.join(A, "video_nosub.mp4")
fx_video = os.path.join(A, "video_fx5.mp4")
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", fx_video], stdin=subprocess.PIPE)
fsize, k = W * H * 3, 0
while True:
    buf = dec.stdout.read(fsize)
    if len(buf) < fsize:
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
print("frames", k, flush=True)

# --------------------------------------------------------------------------- audio: lo-fi bed + extra SFX
rng = np.random.default_rng(11)


def onepole(x, fc):
    a = 1 - math.exp(-2 * math.pi * fc / SR)
    y, acc = np.empty_like(x), 0.0
    for j in range(len(x)):
        acc += a * (x[j] - acc)
        y[j] = acc
    return y


def lofi(seconds):
    n = int(seconds * SR)
    mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
    beat = 60 / 78
    bar = 4 * beat
    chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60, 64], [48, 52, 55, 59]]  # Fmaj7 Em7 Dm9 Cmaj7
    keys, bass, drums = np.zeros(n), np.zeros(n), np.zeros(n)

    def ep(f, dur):
        tt = np.arange(int(dur * SR)) / SR
        tone = np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(4 * np.pi * f * tt) + 0.1 * np.sin(6 * np.pi * f * tt)
        return tone * np.exp(-tt / 1.1) * np.minimum(1, tt / 0.008) * (1 + 0.12 * np.sin(2 * np.pi * 4.2 * tt))

    def add(buf, x, at):
        i0 = int(at * SR)
        if 0 <= i0 < n:
            buf[i0:i0 + len(x)] += x[: n - i0]

    kt = np.arange(int(0.3 * SR)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(48 + 70 * np.exp(-kt / 0.025)) / SR) * np.exp(-kt / 0.11)
    st = np.arange(int(0.25 * SR)) / SR
    snare = onepole(rng.standard_normal(len(st)), 3500) * np.exp(-st / 0.06) + 0.5 * np.sin(2 * np.pi * 190 * st) * np.exp(-st / 0.04)
    ht = np.arange(int(0.04 * SR)) / SR
    hn = rng.standard_normal(len(ht))
    hat = (hn - onepole(hn, 5000)) * np.exp(-ht / 0.01)
    for b in range(int(seconds / bar) + 1):
        s0 = b * bar
        ch = chords[b % 4]
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
    hiss = rng.standard_normal(n) * 0.02
    mix = keys * 0.05 + bass * 0.22 + drums * 0.33 + crackle * 0.05 + hiss
    t = np.arange(n) / SR
    mix *= np.minimum(1, t / 1.2) * np.clip((seconds - t) / 2.5, 0, 1)
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.5
    right = np.concatenate([np.zeros(int(0.011 * SR)), mix])[:n]
    out = np.empty(2 * n, dtype=np.float32)
    out[0::2], out[1::2] = mix, right
    return out


def write_wav(path, data, ch=1):
    pcm = (np.clip(data, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "w") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


write_wav(os.path.join(A, "music_lofi.wav"), lofi(TOTAL + 0.5), ch=2)

with wave.open(os.path.join(A, "sfx.wav")) as w:
    sfx = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
sfx = np.pad(sfx, (0, max(0, NS - len(sfx))))[:NS].copy()


def place(x, at, g):
    i0 = int(at * SR)
    if 0 <= i0 < NS:
        sfx[i0:i0 + len(x)] += (x * g)[: NS - i0]


tt = np.arange(int(0.2 * SR)) / SR
thump = np.sin(2 * np.pi * np.cumsum(55 + 60 * np.exp(-tt / 0.02)) / SR) * np.exp(-tt / 0.07)
pt = np.arange(int(0.1 * SR)) / SR
pop = np.sin(2 * np.pi * np.cumsum(380 + 700 * np.exp(-pt / 0.015)) / SR) * np.exp(-pt / 0.03)
ct = np.arange(int(0.03 * SR)) / SR
click = np.sin(2 * np.pi * 3200 * ct) * np.exp(-ct / 0.004) + 0.5 * rng.standard_normal(len(ct)) * np.exp(-ct / 0.0015)
wt = np.linspace(0, 1, int(0.35 * SR))
swish = onepole(rng.standard_normal(len(wt)), 2500) * np.sin(np.pi * wt) ** 2
swish /= np.max(np.abs(swish))
for tp in PUNCH:
    place(thump, tp, 0.22)
for at in (1.6, SC["ch2"][0] + 0.2, T_FAI, T_TAX):
    place(pop, at, 0.14)
place(swish, SUB_T0, 0.10)
place(click, SUB_T0 + 1.6, 0.35)
place(pop, SUB_T0 + 1.66, 0.12)
place(swish, SUB_T0 + 2.6, 0.08)
write_wav(os.path.join(A, "sfx5.wav"), sfx)

mix = os.path.join(A, "mix5.wav")
run(["ffmpeg", "-y", "-i", os.path.join(A, "voice.wav"), "-i", os.path.join(A, "music_lofi.wav"), "-i", os.path.join(A, "sfx5.wav"),
     "-filter_complex",
     "[0:a]aformat=channel_layouts=stereo,highpass=f=90,acompressor=threshold=-20dB:ratio=3:attack=5:release=90,asplit=2[v1][v2];"
     "[1:a]lowpass=f=3400,highpass=f=40,volume=0.30[m];"
     "[m][v1]sidechaincompress=threshold=0.015:ratio=5:attack=20:release=450[md];"
     "[2:a]aformat=channel_layouts=stereo,volume=0.5[fx];"
     "[v2][md][fx]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
     "-map", "[out]", "-ar", str(SR), mix])


# --------------------------------------------------------------------------- captions
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
BIGPOP = r"{\fscx60\fscy60\t(0,90,\fscx112\fscy112)\t(90,170,\fscx100\fscy100)}"
YELC, WHC = r"{\c&H3CC9FF&}", r"{\c&HFFFFFF&}"


def karaoke_events(until=None):
    ev = []
    for i in range(len(SUBS)):
        if until is not None and i > until:
            break
        for part, a, b in timed_chunks(i):
            ws = [x for x in WT[i] if a - 1e-6 <= x[1] < b - 1e-6]
            txt = "".join(f"{{\\k{max(1, round((wb - wa) * 100))}}}{cl(w)} " for w, wa, wb in ws).rstrip()
            ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b + 0.05)},Sub,,0,0,0,,{POP}{txt}")
    return ev


def bigword_events(until=None):
    ev = []
    for i in range(len(SUBS)):
        if until is not None and i > until:
            break
        groups, cur = [], []
        for w in WT[i]:
            cur.append(w)
            if len(cur) >= 3 or cl(w[0])[-1:] in ".,:?!":
                groups.append(cur)
                cur = []
        if cur:
            groups.append(cur)
        for g in groups:
            txt = " \\h".join(re.sub(r"\*\*(.+?)\*\*", lambda m: YELC + m.group(1) + WHC, w) for w, _, _ in g)
            ev.append(f"Dialogue: 0,{ass_time(g[0][1])},{ass_time(g[-1][2] + 0.04)},Big,,0,0,0,,{BIGPOP}{txt}")
    return ev


VARIANTS = {
    "karaoke": ("Style: Sub,Inter ExtraBold,56,&H003CC9FF,&H00FFFFFF,&H003D2114,&H00000000,0,0,0,0,100,100,0.5,0,3,12,0,2,160,160,62,1",
                "Style: Sub,Inter ExtraBold,76,&H003CC9FF,&H00FFFFFF,&H00141414,&H64000000,0,0,0,0,100,100,0,0,1,6,2,2,90,90,430,1",
                karaoke_events),
    "bigwords": ("Style: Big,Inter Black,96,&H00FFFFFF,&H00FFFFFF,&H00101010,&H78000000,0,0,0,0,100,100,0,0,1,7,4,2,120,120,90,1",
                 "Style: Big,Inter Black,118,&H00FFFFFF,&H00FFFFFF,&H00101010,&H78000000,0,0,0,0,100,100,0,0,1,8,4,2,80,80,470,1",
                 bigword_events),
}
se = SC["counter"][1]
TITLE = ("Style: Title,Inter ExtraBold,70,&H00FFFFFF,&H00FFFFFF,&H00141414,&H64000000,0,0,0,0,100,100,0,0,1,6,2,8,80,80,250,1",
         "Dialogue: 1,0:00:00.00," + ass_time(se) + ",Title,,0,0,0,,{\\fad(250,0)}The {\\c&H3CC9FF&}REAL{\\c&HFFFFFF&} price of a\\N€100,000 house in France")
for name, (st169, st916, evf) in VARIANTS.items():
    p169 = os.path.join(A, f"subs5_{name}.ass")
    with open(p169, "w") as f:
        f.write(HEAD.format(w=W, h=H, styles=st169) + "\n".join(evf()) + "\n")
    run(["ffmpeg", "-y", "-i", fx_video, "-i", mix, "-vf",
         f"ass={p169}:fontsdir={FD},fade=t=in:st=0:d=0.3,fade=t=out:st={TOTAL - 0.7:.2f}:d=0.7",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest", os.path.join(O, f"demo5_{name}_16x9.mp4")])
    p916 = os.path.join(A, f"short5_{name}.ass")
    with open(p916, "w") as f:
        f.write(HEAD.format(w=1080, h=1920, styles=st916 + "\n" + TITLE[0]) + "\n".join(evf(SHORT_LAST)) + "\n" + TITLE[1] + "\n")
    run(["ffmpeg", "-y", "-t", f"{se:.3f}", "-i", fx_video, "-t", f"{se:.3f}", "-i", mix, "-filter_complex",
         "[0:v]split=2[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.18[bg];"
         "[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-60,"
         f"ass={p916}:fontsdir={FD},fade=t=in:st=0:d=0.3,fade=t=out:st={se - 0.5:.2f}:d=0.5[v];"
         f"[1:a]afade=t=out:st={se - 0.6:.2f}:d=0.6[au]",
         "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", os.path.join(O, f"demo5_{name}_short.mp4")])
    print("rendered", name, flush=True)
print("punch at", [round(p, 2) for p in PUNCH], "sub reminder", round(SUB_T0, 2))
