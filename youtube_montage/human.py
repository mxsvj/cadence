# --------------------------------------------------------------------------- human pass: remove the "auto-generated" tells
# Loaded after every scene file. What it changes, and why:
# - type: Inter is gone. One family, FreeSans (a free Helvetica), bold for display, regular for secondary text,
#   always set a little tight (negative tracking) like an editorial title, never the default spacing.
# - layout: big text is no longer centred on the frame. Each scene gets its own left column, items sit on it with
#   a few pixels of drift, and some key phrases are pasted on as a paper sticker, slightly crooked.
# - colour: no glow behind the scenes, no violet; the chapter colours are pulled back a little so nothing looks neon.
# - motion: graphics move on twos (12 fps, like stop-motion / "posterize time"), the camera is handheld (slow drift,
#   micro-jitter, a reframe now and then, springy punch-ins) instead of one perfect push-in per scene.
# - typing: irregular key rhythm (pauses on spaces and punctuation) instead of a metronome at 30 characters a second.
import random

STEP_FPS = 12
FREE = "../../truetype/freefont/"
BLACK, LIGHT = FREE + "FreeSansBold.ttf", FREE + "FreeSans.ttf"
try:
    FONTS.update(BLACK=BLACK, LIGHT=LIGHT)
except NameError:
    pass

# ---------------------------------------------------------------- tight tracking on every FreeSans string
_PTEXT, _PLEN = ImageDraw.ImageDraw.text, ImageDraw.ImageDraw.textlength


def _trk(font):
    p = getattr(font, "path", "") or ""
    return -max(0.6, getattr(font, "size", 20) * 0.014) if "freefont" in p else 0.0


def _tlen(self, text, font=None, *a, **k):
    n = _PLEN(self, text, font=font, *a, **k)
    tr = _trk(font) if font is not None else 0.0
    return n + tr * max(0, len(text) - 1) if tr and isinstance(text, str) else n


def _text(self, xy, text, fill=None, font=None, anchor=None, *a, **k):
    tr = _trk(font) if font is not None else 0.0
    if not tr or not isinstance(text, str) or len(text) < 2 or "\n" in text:
        return _PTEXT(self, xy, text, fill, font, anchor, *a, **k)
    anc = anchor or "la"
    total = _tlen(self, text, font)
    x0 = xy[0] - (total / 2 if anc[0] == "m" else total if anc[0] == "r" else 0)
    for idx, ch in enumerate(text):
        if ch != " ":
            _PTEXT(self, (x0 + _PLEN(self, text[:idx], font=font) + tr * idx, xy[1]), ch, fill, font, "l" + anc[1], *a, **k)


ImageDraw.ImageDraw.text, ImageDraw.ImageDraw.textlength = _text, _tlen

# ---------------------------------------------------------------- colour: flat background, no violet, nothing neon


def _calm(c, k=0.16):
    g = sum(c) / 3
    return tuple(int(v + (g - v) * k) for v in c)


CAT_COL[:] = [_calm(c) for c in CAT_COL]
BRAND = (238, 150, 46)
_FLAT = Image.new("RGB", (W, H), BG)


def black():
    return _FLAT.copy()


def cam(im, t, dur, cy=500, z=0.035):
    """The scene only says where it wants the camera; the handheld camera is applied later, at full frame rate."""
    _SD["camreq"] = (cy, z)
    return im


# ---------------------------------------------------------------- handheld camera


def _noise(t, seed, freqs):
    r = random.Random(seed)
    return sum(math.sin(2 * math.pi * f * t + r.uniform(0, 6.28)) * r.uniform(0.6, 1.0) for f in freqs) / len(freqs)


def handheld(im, t, dur, i, cy=500, z=0.035, hits=(), chap=False):
    r = random.Random(i * 97 + 5)
    u = clamp(t / max(dur, 0.1))
    ease = 1 - (1 - u) ** (1.6 + r.random())                     # decelerates, never a straight line
    s = 1.028 + r.uniform(0, 0.012) + max(z, 0.02) * r.uniform(0.9, 1.5) * ease
    ang = r.uniform(0, 2 * math.pi)
    amp = r.uniform(10, 34)
    dx = amp * math.cos(ang) * (ease - 0.5)
    dy = amp * 0.6 * math.sin(ang) * (ease - 0.5)
    dx += 2.2 * _noise(t, i * 3 + 1, (0.37, 0.83, 1.61))           # operator breathing
    dy += 1.6 * _noise(t, i * 3 + 2, (0.29, 0.71, 1.9))
    rot = 0.07 * _noise(t, i * 3 + 3, (0.23, 0.6))
    if dur > 4.5 and r.random() < 0.55:                             # one small reframe, with overshoot
        tr0 = r.uniform(0.35, 0.7) * dur
        q = t - tr0
        if q > 0:
            sp = 1 - math.exp(-q * 7) * math.cos(q * 11)
            dx += r.choice((-1, 1)) * r.uniform(8, 16) * sp
    if t < 0.4:                                                     # settle after the cut
        s += (0.02 if chap else 0.008) * math.exp(-t * 9) * math.cos(t * 16)
    for at, g in hits:                                              # springy punch-in, shake only sometimes
        q = t - at
        if 0 <= q < 0.9:
            g = min(g, 1.0)
            s += 0.05 * g * math.exp(-q * 6.5) * math.cos(q * 13)
            if q < 0.16 and (int(at * 10) % 3):
                k = int(t * 60)
                dx += ((k * 7919) % 9 - 4) * 1.4 * g
                dy += ((k * 104729) % 7 - 3) * 1.4 * g
    cx = clamp(W / 2 + dx, W / 2 - W * (1 - 1 / s) / 2 + 6, W / 2 + W * (1 - 1 / s) / 2 - 6)
    cyy = clamp(cy + dy, H / 2 - H * (1 - 1 / s) / 2 + 6 + (cy - H / 2), H / 2 + H * (1 - 1 / s) / 2 - 6 + (cy - H / 2))
    cyy = clamp(cyy, H / (2 * s) + 4, H - H / (2 * s) - 4)
    co, si = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    a, b, d_, e = co / s, si / s, -si / s, co / s
    c = cx - (a * W / 2 + b * H / 2)
    f = cyy - (d_ * W / 2 + e * H / 2)
    return im.transform((W, H), Image.AFFINE, (a, b, c, d_, e, f), resample=Image.BILINEAR)


# ---------------------------------------------------------------- typing with a human rhythm
_TT = {}


def _char_times(txt, cps):
    key = (txt, round(cps, 3))
    if key not in _TT:
        h, acc, out = 7, 0.0, [0.0]
        for k, ch in enumerate(txt[:-1]):
            h = (h * 31 + ord(ch) + k * 17) % 1000003
            r = 0.5 + (h % 1000) / 1000
            if ch == " ":
                r *= 1.7
            elif ch in ",.:;·→":
                r *= 2.6
            acc += r
            out.append(acc)
        scale = (max(1, len(txt) - 1) / cps) / acc if acc else 1.0
        _TT[key] = [x * scale for x in out]
    return _TT[key]


def typed(txt, t, t0, cps=28, gt0=None):
    if _SD["dur"] is not None:
        cps = max(cps, len(txt) / max(0.3, _SD["dur"] - 0.4 - t0))
    times = _char_times(txt, cps)
    if gt0 is not None:
        ticks.extend(gt0 + t0 + tk for k, tk in enumerate(times) if txt[k] != " ")
    if t < t0:
        return ""
    q = t - t0
    n = 0
    while n < len(times) and times[n] <= q:
        n += 1
    return txt[:max(1, n)]


# ---------------------------------------------------------------- big text: off-centre column, drift, paper stickers
PAPER, INKC = (240, 236, 226), (20, 20, 20)


def _sticker(txt, font, size, rot):
    f = F(font, size)
    w = _tmp.textlength(txt, font=f)
    pad = int(size * 0.28)
    hgt = int(size * 1.25)
    lay = Image.new("RGBA", (int(w) + 2 * pad, hgt + pad), (0, 0, 0, 0))
    dd = ImageDraw.Draw(lay)
    dd.rectangle([0, 0, lay.width - 1, lay.height - 1], fill=PAPER + (255,))
    dd.text((pad, hgt * 0.86 + pad * 0.3), txt, font=f, fill=INKC + (255,), anchor="ls")
    return lay.rotate(rot, resample=Image.BICUBIC, expand=True)


def bigs(items, events=()):
    def build(dur, i):
        r = random.Random(i * 31 + 7)
        left = r.randint(170, 250)
        sticker_scene = r.random() < 0.38
        R = []
        for k, (txt, cue, font, size, col, x, y) in enumerate(items):
            t0 = trig(i, cue) + r.uniform(0, 0.06)
            if is_mono(font):
                typed(txt, 0, t0, 30, starts[i])
            col = accent(col) if font == BLACK else col
            cnt = font == BLACK and counts(txt) and r.random() < 0.6
            st = sticker_scene and font == LIGHT and col != DIM
            xx = left + r.randint(-7, 9) if abs(x - W / 2) < 2 else x
            R.append((k, txt, t0, F(font, size), font, size, col, xx, y + r.randint(-4, 4), cnt, st, r.uniform(-1.8, 1.8),
                      abs(x - W / 2) < 2))

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            for k, txt, t0, f, font, size, col, x, y, cnt, st, rot, left_al in R:
                if t < t0:
                    continue
                lift = (6 + 4 * k) * prog(t, t0, dur)
                if is_mono(font):
                    shown = typed(txt, t, t0, 30)
                    if left_al:
                        d.text((x, y - lift), shown, font=f, fill=col, anchor="ls")
                    else:
                        mid_text(d, y - lift, txt, shown, f, col, x)
                elif st:
                    lay = _sticker(txt, font, size, rot)
                    sc = 1 + 0.06 * (1 - prog(t, t0, t0 + 0.17))
                    if sc > 1.001:
                        lay = lay.resize((int(lay.width * sc), int(lay.height * sc)), Image.BILINEAR)
                    px = int(x - 12) if left_al else int(x - lay.width / 2)
                    im.paste(lay, (px, int(y - lay.height * 0.78 - lift)), lay)
                elif cnt:
                    a = prog(t, t0, t0 + 0.15)
                    s = count_text(txt, ease_out(prog(t, t0, t0 + 0.9)))
                    d.text((x, y + 10 * (1 - a) - lift), s, font=f, fill=col + (int(255 * a),), anchor="ls" if left_al else "ms")
                else:
                    if left_al:
                        rise(im, txt, font, size, col, x + d.textlength(txt, font=f) / 2, y, t, t0, lift=lift)
                    else:
                        rise(im, txt, font, size, col, x, y, t, t0, lift=lift)
            return cam(im, t, dur)
        return frame, [(n, trig(i, cue), g) for n, cue, g in events]
    return build


def term(rows, size=44, cps=28, cy=480):
    """Terminal rows, now on a left column that changes from scene to scene, each row a few pixels off."""
    def build(dur, i):
        r = random.Random(i * 13 + 3)
        fm = F(MONO, size)
        R = [(txt, trig(i, cue) + r.uniform(0, 0.05), accent(col) if txt[:1] in ">+" else col, r.randint(-5, 6)) for txt, cue, col in rows]
        for txt, t0, _, _ in R:
            typed(txt, 0, t0, cps, starts[i])
        wmax = max(_tmp.textlength(txt, font=fm) for txt, _, _, _ in R)
        x0 = min(r.randint(180, 300), W - wmax - 120)
        lh = size * r.uniform(1.75, 2.0)
        y0 = cy - (len(R) - 1) * lh / 2 + r.randint(-20, 20)

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            last = None
            for k, (txt, t0, col, off) in enumerate(R):
                s = typed(txt, t, t0, cps)
                if s:
                    u = ease_out(prog(t, t0, t0 + 0.3))
                    x = x0 + off - 30 * (1 - u)
                    y = y0 + k * lh
                    d.text((x, y), s, font=fm, fill=col + (int(255 * (0.35 + 0.65 * u)),), anchor="ls")
                    last = (s, y, x)
            if last:
                caret(d, last[2] + d.textlength(last[0], font=fm), last[1], t, size)
            return cam(im, t, dur, cy)
        return frame, []
    return build


def k_cchap(n, title):
    """Chapter card, rebuilt off-centre: title on a left column, the box number large and cropped on the right,
    the progress squares under the title, letters dropping in slightly uneven."""
    def build(dur, i):
        r = random.Random(n * 41)
        NB = len(CATS)
        word = globals().get("BOX_WORD", "BOX")
        lab = f"{word} {n:02d} / {NB}"
        typed(lab, 0, 0.1, 20, starts[i])
        ac = CAT_COL[n - 1]
        ft, fk, fbig = F(BLACK, 118), F(MONO, 28), F(BLACK, 700)
        x0 = r.randint(150, 210)
        yb = 600 + r.randint(-20, 20)
        offs = [r.randint(-3, 3) for _ in title]

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            d.text((W - 120 + r.randint(-10, 10), 900), f"{n:02d}", font=fbig, fill=mix(BG, ac, 0.22), anchor="rs")
            d.text((x0 + 4, yb - 150), typed(lab, t, 0.1, 20), font=fk, fill=DIM, anchor="ls")
            x = x0
            for k, ch in enumerate(title):
                a = prog(t, 0.3 + k * 0.03, 0.42 + k * 0.03)
                if a > 0:
                    d.text((x, yb + offs[k] - 10 * (1 - a)), ch, font=ft, fill=FG + (int(255 * a),), anchor="ls")
                x += d.textlength(ch, font=ft) + _trk(ft)
            w = (x - x0) * ease_out(prog(t, 0.25, 0.8))
            d.rectangle([x0 + 2, yb + 34, x0 + 2 + w, yb + 40], fill=ac)
            for k in range(NB):
                xx = x0 + 4 + k * 34
                a = int(255 * prog(t, 0.05 + k * 0.03, 0.2 + k * 0.03))
                if k < n - 1:
                    d.rectangle([xx, yb + 80, xx + 22, yb + 102], fill=CAT_COL[k] + (int(a * 0.8),))
                elif k == n - 1:
                    d.rectangle([xx, yb + 80, xx + 22, yb + 102], fill=ac + (a,))
                else:
                    d.rectangle([xx, yb + 80, xx + 22, yb + 102], outline=FAINT + (a,), width=2)
            return cam(im, t, dur, 520, 0.03)
        return frame, [("boom", 0.0, 0.45)]
    return build


if "k_pchap" not in globals():                 # the POV videos keep their own age card
    KINDS["chap"] = k_cchap
