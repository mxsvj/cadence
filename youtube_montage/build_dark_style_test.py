"""Style test: the first ~20 s of 'Can Europeans buy VOO?' in a dark, minimal video-essay look
(black screen, typed monospace text, hard cuts with glitches, ambient drone with silences, quiet white captions).
Reuses the voice, timings and helpers of build_finance_demo.py."""
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw

D = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(D, "build_finance_demo.py")).read()
ns = {"__file__": os.path.join(D, "build_finance_demo.py")}
exec(src[: src.index("# --------------------------------------------------------------------------- render shots")], ns)
globals().update({k: v for k, v in ns.items() if not k.startswith("__")})

E = os.path.join(D, "ego")
os.makedirs(E, exist_ok=True)
BG, FG, DIM, ERR = (7, 7, 9), (236, 236, 236), (118, 118, 126), (232, 58, 64)
MONO = "../../truetype/dejavu/DejaVuSansMono.ttf"
K = 4                                   # lines 0-3: hook, PRIIPs, part 1, KID
NF = sum(frames[:K])
T_END = NF / FPS
rng = np.random.default_rng(7)
ticks = []                              # typewriter key times (global seconds)


def typed(txt, t, t0, cps=26, gt0=None):
    """Prefix of txt typed since t0; registers one key tick per character (once, via gt0)."""
    if gt0 is not None:
        ticks.extend(gt0 + t0 + k / cps for k in range(len(txt)) if txt[k] != " ")
    return "" if t < t0 else txt[: int((t - t0) * cps) + 1]


def caret(d, x, y, t, size):
    if t % 0.9 < 0.5:
        d.rectangle([x + 4, y - size * 0.8, x + 4 + size * 0.55, y + size * 0.15], fill=FG)


def letters(d, xy, txt, font, t, t0, step=0.04, fade=0.25, fill=FG):
    """Centered text whose letters fade in one after the other."""
    x = xy[0] - d.textlength(txt, font=font) / 2
    for k, ch in enumerate(txt):
        a = prog(t, t0 + k * step, t0 + k * step + fade)
        if a > 0:
            d.text((x, xy[1]), ch, font=font, fill=fill + (int(255 * a),), anchor="ls")
        x += d.textlength(ch, font=font)


def ego_hook(dur, i):
    t_v, t_eu, t_c = lw(i, "voo"), lw(i, "europe"), lw(i, "can't")
    cols, rows, bw, bh, gap = 11, 7, 140, 80, 22
    gx0 = (W - (cols * bw + (cols - 1) * gap)) / 2
    gy0 = (H - (rows * bh + (rows - 1) * gap)) / 2 - 30
    tile = Cv(None, size=(bw, bh))
    tile.rect([2, 2, bw - 2, bh - 2], None, r=8, outline=DIM, width=2)
    tile.text((bw / 2, bh / 2 + 6), "buy VOO.", MONO, 17, FG, anchor="ms")
    tile = tile.out()
    order = rng.permutation(cols * rows)
    appear = {int(c): 0.3 + (t_v - 0.6) * (r / (cols * rows)) ** 1.8 for r, c in enumerate(order)}
    voo = Cv(None, size=(900, 360))
    voo.text((450, 290), "VOO", "InterDisplay-Black.otf", 300, FG, anchor="ms")
    voo = voo.out()
    fm, fe = F(MONO, 36), F(MONO, 30)
    loc, err = "location = EUROPE", "ERROR: NOT AVAILABLE IN YOUR REGION"
    typed(loc, 0, t_eu, 22, starts[i])
    typed(err, 0, t_c + 0.12, 60, starts[i])

    def frame(t):
        im = Image.new("RGB", (W, H), BG)
        wall = 1 - 0.88 * prog(t, t_v, t_v + 0.25)
        for c, ap in appear.items():
            if t >= ap:
                x, y = gx0 + (c % cols) * (bw + gap), gy0 + (c // cols) * (bh + gap)
                comp(im, tile, x, y, prog(t, ap, ap + 0.12) * wall)
        if t >= t_v:
            sprite_at(im, voo, W / 2, 470, 1.06 - 0.06 * ease_out(prog(t, t_v, t_v + 0.4)), prog(t, t_v, t_v + 0.08))
        d = ImageDraw.Draw(im, "RGBA")
        s = typed(loc, t, t_eu, 22)
        if s:
            w = d.textlength(loc, font=fm)
            d.text((W / 2 - w / 2, 720), s, font=fm, fill=DIM, anchor="ls")
            if t < t_c:
                caret(d, W / 2 - w / 2 + d.textlength(s, font=fm), 720, t, 36)
        if t >= t_c:
            u = ease_out(prog(t, t_c, t_c + 0.15))
            d.line([(W / 2 - 340, 476), (W / 2 - 340 + 680 * u, 476)], fill=ERR, width=10)
            s = typed(err, t, t_c + 0.12, 60)
            w = d.textlength(err, font=fe)
            d.text((W / 2 - w / 2, 800), s, font=fe, fill=ERR, anchor="ls")
        z = 1.15 - 0.15 * ease_out(prog(t, 0, t_v)) + 0.04 * prog(t, t_v, dur)
        return camera(im, z, W / 2, 470 if t >= t_v else H / 2)
    return frame, [("boom", t_v, 0.9), ("glitch", t_c, 1.0)]


def ego_priips(dur, i):
    t_d, t_e, t_p = lw(i, "difficult"), lw(i, "european"), lw(i, "priips")
    l1, l2 = "> blocked_by = broker", "> blocked_by = EU_RULE"
    typed(l1, 0, 0.2, 24, starts[i])
    typed(l2, 0, t_e - 0.1, 24, starts[i])
    fm, fb, fs = F(MONO, 44), F("InterDisplay-Black.otf", 230), F(MONO, 30)
    x0 = 520

    def frame(t):
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im, "RGBA")
        if t < t_p:
            s1 = typed(l1, t, 0.2, 24)
            d.text((x0, 480), s1, font=fm, fill=FG, anchor="ls")
            if t >= t_d:
                bx = x0 + d.textlength("> blocked_by = ", font=fm)
                u = ease_out(prog(t, t_d, t_d + 0.2))
                d.line([(bx - 6, 466), (bx - 6 + (d.textlength("broker", font=fm) + 12) * u, 466)], fill=ERR, width=5)
            s2 = typed(l2, t, t_e - 0.1, 24)
            d.text((x0, 560), s2, font=fm, fill=FG, anchor="ls")
            cur = (s2, 560) if s2 else (s1, 480)
            caret(d, x0 + d.textlength(cur[0], font=fm), cur[1], t, 44)
            return camera(im, 1 + 0.04 * t / dur)
        d.text((W / 2, 560), "PRIIPs", font=fb, fill=FG, anchor="ms")
        letters(d, (W / 2, 660), "EU regulation  ·  since 2018", fs, t, t_p + 0.3, step=0.02, fill=DIM)
        return camera(im, 1.0 + 0.05 * prog(t, t_p, dur), W / 2, 520)
    return frame, [("boom", t_p, 1.0), ("glitch", t_p, 0.5)]


def ego_chapter(n, title):
    def build(dur, i):
        fk, ft = F(MONO, 30), F("Inter-Light.otf", 104)
        lab = f"PART {n:02d}"
        typed(lab, 0, 0.1, 20, starts[i])

        def frame(t):
            im = Image.new("RGB", (W, H), BG)
            d = ImageDraw.Draw(im, "RGBA")
            s = typed(lab, t, 0.1, 20)
            d.text((W / 2 - d.textlength(lab, font=fk) / 2, 430), s, font=fk, fill=DIM, anchor="ls")
            letters(d, (W / 2, 580), title, ft, t, 0.35, step=0.035)
            w = 520 * ease_out(prog(t, 0.3, 1.0))
            d.line([(W / 2 - w / 2, 640), (W / 2 + w / 2, 640)], fill=FG + (110,), width=2)
            return camera(im, 1 + 0.03 * t / dur)
        return frame, [("boom", 0.0, 0.45)]
    return build


def ego_kid(dur, i):
    t18, tf, tk, tm, tx = (lw(i, w) for w in ("2018", "funds", "key", "most", "don't"))
    fm, fl = F(MONO, 30), F(MONO, 26)
    ts, lab_l, lab_k = "since 2018-01-01", "EU_FUND/KID.pdf", "Key Information Document"
    lab_r, lab_x = "US_FUND/KID.pdf", "404: FILE NOT FOUND"
    for txt, t0, cps in ((ts, t18, 30), (lab_l, tf + 0.3, 30), (lab_k, tk, 30), (lab_r, tm + 0.3, 30), (lab_x, tx, 50)):
        typed(txt, 0, t0, cps, starts[i])

    def doc(d, cx, cy, a, dashed, fill_u):
        x0, y0, x1, y1 = cx - 150, cy - 190, cx + 150, cy + 190
        col = FG + (int(255 * a),)
        if dashed:
            for x in range(x0, x1, 28):
                for y in (y0, y1):
                    d.line([(x, y), (min(x + 14, x1), y)], fill=DIM + (int(255 * a),), width=3)
            for y in range(y0, y1, 28):
                for x in (x0, x1):
                    d.line([(x, y), (x, min(y + 14, y1))], fill=DIM + (int(255 * a),), width=3)
            return
        d.line([(x0, y0), (x1 - 50, y0), (x1, y0 + 50), (x1, y1), (x0, y1), (x0, y0)], fill=col, width=3)
        d.line([(x1 - 50, y0), (x1 - 50, y0 + 50), (x1, y0 + 50)], fill=col, width=3)
        for k, w in enumerate((170, 220, 200, 230, 140, 210, 180)):
            u = prog(fill_u, k / 7, (k + 1) / 7)
            if u > 0:
                d.line([(x0 + 36, y0 + 90 + k * 36), (x0 + 36 + w * u, y0 + 90 + k * 36)], fill=col, width=6)

    def frame(t):
        im = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(im, "RGBA")
        s = typed(ts, t, t18, 30)
        d.text((W / 2 - d.textlength(ts, font=fm) / 2, 150), s, font=fm, fill=DIM, anchor="ls")
        if t >= tf:
            doc(d, 640, 470, prog(t, tf, tf + 0.3), False, prog(t, tf + 0.2, tf + 1.6))
            s = typed(lab_l, t, tf + 0.3, 30)
            d.text((640 - d.textlength(lab_l, font=fl) / 2, 730), s, font=fl, fill=FG, anchor="ls")
            s = typed(lab_k, t, tk, 30)
            d.text((640 - d.textlength(lab_k, font=fl) / 2, 776), s, font=fl, fill=DIM, anchor="ls")
        if t >= tm:
            doc(d, 1280, 470, prog(t, tm, tm + 0.3), True, 0)
            txt, col, t0, cps = (lab_x, ERR, tx, 50) if t >= tx else (lab_r, FG, tm + 0.3, 30)
            s = typed(txt, t, t0, cps)
            d.text((1280 - d.textlength(txt, font=fl) / 2, 730), s, font=fl, fill=col, anchor="ls")
        return camera(im, 1 + 0.04 * t / dur, W / 2, 480)
    return frame, [("boom", tx, 0.7), ("glitch", tx, 0.6)]


SC_EGO = [ego_hook, ego_priips, ego_chapter(1, "The missing document."), ego_kid]

# --------------------------------------------------------------------------- render: hard cuts, glitches, grain, vignette
yy, xx = np.mgrid[0:H, 0:W]
vig = (1 - 0.38 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.4).clip(0.45, 1)[..., None].astype(np.float32)
grain = [rng.normal(0, 5.5, (H, W, 1)).astype(np.float32) for _ in range(6)]


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


fns, events, offs = [], [], []
for i in range(K):
    fn, ev = SC_EGO[i](frames[i] / FPS, i)
    fns.append(fn)
    events += [(n, starts[i] + tt, g) for n, tt, g in ev]
    offs.append(starts[i])
G = [(at, 0.32 if n == "glitch" else 0.0, g) for n, at, g in events if n == "glitch"]
G += [(starts[i] - 0.05, 0.12, 0.6) for i in range(1, K)]

vid = os.path.join(E, "video.mp4")
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
for k in range(NF):
    t = k / FPS
    i = max(j for j in range(K) if starts[j] <= t + 1e-6)
    a = np.asarray(fns[i](t - starts[i]).convert("RGB"), dtype=np.uint8)
    amt = max([g * (1 - (t - at) / du) for at, du, g in G if du and at <= t < at + du] + [0])
    if amt > 0.02 and k % 3 != 2:
        a = glitch(a, amt, k)
    f = a.astype(np.float32) * vig + grain[k % 6]
    enc.stdin.write(f.clip(0, 255).astype(np.uint8).tobytes())
enc.stdin.close()
enc.wait()
print("video ok", NF, flush=True)

# --------------------------------------------------------------------------- sound: drone, silences, booms, glitches, keys
n = int(T_END * SR)
tt = np.arange(n) / SR
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
pad = np.zeros(n)
for j, m in enumerate((45, 52, 57, 60, 64)):
    for det in (-0.15, 0.15):
        f = mtof(m) + det
        pad += (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.07 * tt + j))
pad += 1.4 * np.sin(2 * np.pi * mtof(33) * tt) + 0.08 * np.sin(2 * np.pi * mtof(88) * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * tt))
pad /= np.max(np.abs(pad))
env = np.minimum(1, tt / 2.5) * np.clip((T_END - tt) / 1.5, 0, 1)
t_cut = starts[0] + lw(0, "can't")
env *= 1 - np.clip(1 - np.abs(tt - (t_cut + 0.45)) / 0.45, 0, 1) ** 0.3 * (tt > t_cut - 0.02)
music = (pad * env * 0.5).astype(np.float32)
write_wav(os.path.join(E, "music.wav"), music)

sfx = np.zeros(n + SR, dtype=np.float32)


def put(x, at, g):
    i0 = int(max(0, at) * SR)
    sfx[i0:i0 + len(x)] += (x * g)[: len(sfx) - i0]


bt = np.arange(int(1.6 * SR)) / SR
boom = np.sin(2 * np.pi * np.cumsum(32 + 40 * np.exp(-bt / 0.08)) / SR) * np.exp(-bt / 0.5)
gt = int(0.32 * SR)
gl = rng.standard_normal(gt) * np.repeat(rng.integers(0, 2, gt // 441 + 1), 441)[:gt]
gl = gl + 0.6 * np.sign(np.sin(2 * np.pi * 180 * np.arange(gt) / SR)) * np.repeat(rng.integers(0, 2, gt // 882 + 1), 882)[:gt]
kt = np.arange(int(0.03 * SR)) / SR
tick = np.sin(2 * np.pi * 2600 * kt) * np.exp(-kt / 0.005) + 0.4 * rng.standard_normal(len(kt)) * np.exp(-kt / 0.002)
for name, at, g in events:
    put(boom if name == "boom" else gl / np.max(np.abs(gl)), at, (0.6 if name == "boom" else 0.22) * g)
for at in ticks:
    put(tick, at, 0.06 * rng.uniform(0.7, 1.0))
write_wav(os.path.join(E, "sfx.wav"), sfx[:n])
voice_cut = os.path.join(E, "voice.wav")
write_wav(voice_cut, vt[:n])
mix = os.path.join(E, "mix.wav")
run(["ffmpeg", "-y", "-i", voice_cut, "-i", os.path.join(E, "music.wav"), "-i", os.path.join(E, "sfx.wav"), "-filter_complex",
     "[0:a]aformat=channel_layouts=stereo,highpass=f=90,acompressor=threshold=-20dB:ratio=3:attack=5:release=90,asplit=2[v1][v2];"
     "[1:a]aformat=channel_layouts=stereo,volume=0.35[m];[m][v1]sidechaincompress=threshold=0.02:ratio=3:attack=30:release=600[md];"
     "[2:a]aformat=channel_layouts=stereo,volume=0.5[fx];"
     "[v2][md][fx]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
     "-map", "[out]", "-ar", str(SR), mix])

# --------------------------------------------------------------------------- quiet karaoke captions (grey -> white, no box)
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
out = os.path.join(O, "ego_style_test_16x9.mp4")
run(["ffmpeg", "-y", "-i", vid, "-i", mix, "-vf", f"ass={subs}:fontsdir={FD},fade=t=out:st={T_END - 0.6:.2f}:d=0.6",
     "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", "-shortest", out])
print("done", out, f"{T_END:.2f}s")
