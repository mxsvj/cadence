"""'Can Europeans buy VOO?' in the dark video-essay style (inspired by the EGO channel's editing):
black screen, typed monospace text, hard cuts with glitches, grain and vignette, ambient drone with silences,
quiet grey-to-white karaoke captions. Reuses the voice, timings and helpers of build_finance_demo.py."""
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw

D = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(D, "build_finance_demo.py")).read()
ns = {"__file__": os.path.join(D, "build_finance_demo.py")}
exec(src[: src.index("# --------------------------------------------------------------------------- render shots")], ns)
globals().update({k: v for k, v in ns.items() if not k.startswith("__")})

E = os.path.join(D, "dark")
os.makedirs(E, exist_ok=True)
BG, FG, DIM, FAINT, ERR = (7, 7, 9), (236, 236, 236), (118, 118, 126), (58, 58, 66), (232, 58, 64)
MONO = "../../truetype/dejavu/DejaVuSansMono.ttf"
K = len(LINES)
NF = sum(frames)
rng = np.random.default_rng(7)
ticks = []                              # typewriter key times (global seconds)


def typed(txt, t, t0, cps=26, gt0=None):
    """Prefix of txt typed since t0; with gt0 (scene start), registers one key tick per character instead."""
    if gt0 is not None:
        ticks.extend(gt0 + t0 + k / cps for k in range(len(txt)) if txt[k] != " ")
    return "" if t < t0 else txt[: int((t - t0) * cps) + 1]


def caret(d, x, y, t, size):
    if t % 0.9 < 0.5:
        d.rectangle([x + 4, y - size * 0.8, x + 4 + size * 0.55, y + size * 0.15], fill=FG)


def mid_text(d, y, full, shown, font, fill):
    """Typed text that stays centered on its full length."""
    d.text((W / 2 - d.textlength(full, font=font) / 2, y), shown, font=font, fill=fill, anchor="ls")


def letters(d, xy, txt, font, t, t0, step=0.04, fade=0.25, fill=FG):
    """Centered text whose letters fade in one after the other."""
    x = xy[0] - d.textlength(txt, font=font) / 2
    for k, ch in enumerate(txt):
        a = prog(t, t0 + k * step, t0 + k * step + fade)
        if a > 0:
            d.text((x, xy[1]), ch, font=font, fill=fill + (int(255 * a),), anchor="ls")
        x += d.textlength(ch, font=font)


def black():
    return Image.new("RGB", (W, H), BG)


# --------------------------------------------------------------------------- scenes
def dk_hook(dur, i):
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
        im = black()
        wall = 1 - 0.88 * prog(t, t_v, t_v + 0.25)
        for c, ap in appear.items():
            if t >= ap:
                comp(im, tile, gx0 + (c % cols) * (bw + gap), gy0 + (c // cols) * (bh + gap), prog(t, ap, ap + 0.12) * wall)
        if t >= t_v:
            sprite_at(im, voo, W / 2, 470, 1.06 - 0.06 * ease_out(prog(t, t_v, t_v + 0.4)), prog(t, t_v, t_v + 0.08))
        d = ImageDraw.Draw(im, "RGBA")
        s = typed(loc, t, t_eu, 22)
        if s:
            mid_text(d, 720, loc, s, fm, DIM)
            if t < t_c:
                caret(d, W / 2 - d.textlength(loc, font=fm) / 2 + d.textlength(s, font=fm), 720, t, 36)
        if t >= t_c:
            u = ease_out(prog(t, t_c, t_c + 0.15))
            d.line([(W / 2 - 340, 476), (W / 2 - 340 + 680 * u, 476)], fill=ERR, width=10)
            mid_text(d, 800, err, typed(err, t, t_c + 0.12, 60), fe, ERR)
        z = 1.15 - 0.15 * ease_out(prog(t, 0, t_v)) + 0.04 * prog(t, t_v, dur)
        return camera(im, z, W / 2, 470 if t >= t_v else H / 2)
    return frame, [("boom", t_v, 0.9), ("glitch", t_c, 1.0)]


def dk_priips(dur, i):
    t_d, t_e, t_p = lw(i, "difficult"), lw(i, "european"), lw(i, "priips")
    l1, l2 = "> blocked_by = broker", "> blocked_by = EU_RULE"
    typed(l1, 0, 0.2, 24, starts[i])
    typed(l2, 0, t_e - 0.1, 24, starts[i])
    fm, fb, fs = F(MONO, 44), F("InterDisplay-Black.otf", 230), F(MONO, 30)
    x0 = 520

    def frame(t):
        im = black()
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


def dk_chapter(n, title):
    def build(dur, i):
        fk, ft = F(MONO, 30), F("Inter-Light.otf", 104)
        lab = f"PART {n:02d}"
        typed(lab, 0, 0.1, 20, starts[i])

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            mid_text(d, 430, lab, typed(lab, t, 0.1, 20), fk, DIM)
            letters(d, (W / 2, 580), title, ft, t, 0.35, step=0.035)
            w = 520 * ease_out(prog(t, 0.3, 1.0))
            d.line([(W / 2 - w / 2, 640), (W / 2 + w / 2, 640)], fill=FG + (110,), width=2)
            return camera(im, 1 + 0.03 * t / dur)
        return frame, [("boom", 0.0, 0.45)]
    return build


def dk_kid(dur, i):
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
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        mid_text(d, 150, ts, typed(ts, t, t18, 30), fm, DIM)
        if t >= tf:
            doc(d, 640, 470, prog(t, tf, tf + 0.3), False, prog(t, tf + 0.2, tf + 1.6))
            d.text((640 - d.textlength(lab_l, font=fl) / 2, 730), typed(lab_l, t, tf + 0.3, 30), font=fl, fill=FG, anchor="ls")
            d.text((640 - d.textlength(lab_k, font=fl) / 2, 776), typed(lab_k, t, tk, 30), font=fl, fill=DIM, anchor="ls")
        if t >= tm:
            doc(d, 1280, 470, prog(t, tm, tm + 0.3), True, 0)
            txt, col, t0, cps = (lab_x, ERR, tx, 50) if t >= tx else (lab_r, FG, tm + 0.3, 30)
            d.text((1280 - d.textlength(txt, font=fl) / 2, 730), typed(txt, t, t0, cps), font=fl, fill=col, anchor="ls")
        return camera(im, 1 + 0.04 * t / dur, W / 2, 480)
    return frame, [("boom", tx, 0.7), ("glitch", tx, 0.6)]


def dk_twin(dur, i):
    tu, tie, t5 = lw(i, "ucits"), lw(i, "ireland"), lw(i, "500", 1)
    sp, r = 16, 3
    gw, gh = 25 * sp, 20 * sp
    g = Cv(None, size=(gw, gh))
    for row in range(20):
        for c in range(25):
            x, y = c * sp + sp / 2, row * sp + sp / 2
            g.ellipse([x - r, y - r, x + r, y + r], FG)
    grid = g.out()
    fl, fd = F(MONO, 28), F(MONO, 34)
    lab_l, lab_r = "VOO  ·  domicile = US", "S&P 500 UCITS ETF  ·  domicile = IE"
    diff = "diff(VOO, UCITS ETF) = 0 companies"
    for txt, t0 in ((lab_l, 0.4), (lab_r, tu + 0.2), (diff, t5)):
        typed(txt, 0, t0, 32, starts[i])
    LX, RX, GY = 600, 1320, 440

    def frame(t):
        im = black()
        for cx, t0 in ((LX, 0.1), (RX, tu)):
            u = ease_out(prog(t, t0, t0 + 1.2))
            hh = int(gh * u)
            if hh > 0:
                comp(im, grid.crop((0, 0, gw, hh)), cx - gw / 2, GY - gh / 2)
        d = ImageDraw.Draw(im, "RGBA")
        u = prog(t, tu, tu + 1.2)
        if 0 < u < 1:
            y = GY - gh / 2 + gh * ease_out(u)
            d.line([(RX - gw / 2 - 30, y), (RX + gw / 2 + 30, y)], fill=FG + (150,), width=2)
        for cx, txt, t0 in ((LX, lab_l, 0.4), (RX, lab_r, tu + 0.2)):
            d.text((cx - d.textlength(txt, font=fl) / 2, 680), typed(txt, t, t0, 32), font=fl, fill=DIM, anchor="ls")
        if t >= tie:
            x = RX - d.textlength(lab_r, font=fl) / 2 + d.textlength(lab_r[:-2], font=fl)
            w = d.textlength("IE", font=fl) * ease_out(prog(t, tie, tie + 0.25))
            d.text((x, 680), "IE", font=fl, fill=FG, anchor="ls")
            d.line([(x, 690), (x + w, 690)], fill=FG, width=3)
        mid_text(d, 820, diff, typed(diff, t, t5, 32), fd, FG)
        return camera(im, 1 + 0.035 * t / dur, W / 2, 500)
    return frame, [("boom", tie, 0.45), ("boom", t5 + len(diff) / 32, 0.6)]


def dk_fees(dur, i):
    t7, t3, t10, t4 = lw(i, "0.07%"), lw(i, "0.03%"), lw(i, "€10,000"), lw(i, "€4")
    fb, fm, fe, f4, fy = F("InterDisplay-Black.otf", 190), F(MONO, 30), F(MONO, 40), F("InterDisplay-Black.otf", 280), F(MONO, 48)
    cmd, l7, l3 = "> compare --yearly-fee", "S&P 500 UCITS (IE)", "VOO (US)"
    eq = "€10,000 × (0.07% − 0.03%) ="
    for txt, t0, cps in ((cmd, 0.2, 28), (l7, t7, 40), (l3, t3, 40), (eq, t10, 34)):
        typed(txt, 0, t0, cps, starts[i])

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        if t < t10:
            mid_text(d, 260, cmd, typed(cmd, t, 0.2, 28), fm, DIM)
            for cx, lab, fee, t0 in ((600, l7, 0.07, t7), (1320, l3, 0.03, t3)):
                if t >= t0:
                    d.text((cx - d.textlength(lab, font=fm) / 2, 430), typed(lab, t, t0, 40), font=fm, fill=DIM, anchor="ls")
                    v = fee * ease_out(prog(t, t0, t0 + 0.5))
                    d.text((cx, 640), f"{v:.2f}%", font=fb, fill=FG + (int(255 * prog(t, t0, t0 + 0.1)),), anchor="ms")
            return camera(im, 1 + 0.03 * t / dur, W / 2, 520)
        mid_text(d, 400, eq, typed(eq, t, t10, 34), fe, DIM)
        if t >= t4:
            txt = f"€{max(1, round(4 * ease_out(prog(t, t4, t4 + 0.5))))}"
            w1, w2 = d.textlength(txt, font=f4), d.textlength(" / year", font=fy)
            x = W / 2 - (w1 + w2) / 2
            d.text((x, 720), txt, font=f4, fill=FG, anchor="ls")
            d.text((x + w1, 720), " / year", font=fy, fill=DIM, anchor="ls")
        return camera(im, 1 + 0.05 * prog(t, t10, dur), W / 2, 560)
    return frame, [("boom", t7, 0.5), ("boom", t3, 0.35), ("glitch", t10, 0.45), ("boom", t4, 1.0)]


def dk_check(dur, i):
    tp = lw(i, "problem")
    head = "> no VOO? no problem."
    items = [('search "S&P 500 UCITS ETF"', lw(i, "search")), ("check the yearly fee (TER)", lw(i, "fees")),
             ("check where it's based", lw(i, "based"))]
    fm = F(MONO, 42)
    typed(head, 0, 0.1, 30, starts[i])
    for k, (txt, _) in enumerate(items):
        typed("[ ] " + txt, 0, tp + 0.1 + k * 0.45, 60, starts[i])
    x0 = 520

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        s = typed(head, t, 0.1, 30)
        d.text((x0, 380), s, font=fm, fill=FG, anchor="ls")
        if t < tp + 0.1:
            caret(d, x0 + d.textlength(s, font=fm), 380, t, 42)
        for k, (txt, t0) in enumerate(items):
            s = typed("[ ] " + txt, t, tp + 0.1 + k * 0.45, 60)
            if not s:
                continue
            done = t >= t0
            box = ("[x] " if done else "[ ] ")[:len(s)]
            d.text((x0, 520 + k * 84), box, font=fm, fill=FG if done else DIM, anchor="ls")
            d.text((x0 + d.textlength("[ ] ", font=fm), 520 + k * 84), s[4:], font=fm, fill=FG if done else DIM, anchor="ls")
        return camera(im, 1 + 0.03 * t / dur, W / 2, 520)
    return frame, [("boom", t0, 0.3) for _, t0 in items]


def dk_end(dur, i):
    tw, tn = lw(i, "which"), lw(i, "not")
    fk, ft, fs = F(MONO, 26), F("Inter-Light.otf", 84), F(MONO, 30)
    nxt, sub, nfa = "next >", "which one should you pick?", "not financial advice."
    for txt, t0 in ((nxt, 0.05), (sub, tw), (nfa, tn)):
        typed(txt, 0, t0, 30, starts[i])
    ph = Cv(None)
    ph.rect([240, 430, 1040, 880], None, r=6, outline=FAINT, width=2)
    ph.text((640, 665), "next video", MONO, 30, DIM, anchor="mm")
    ph.ellipse([1260, 460, 1650, 850], None, outline=FAINT, width=2)
    ph.text((1455, 655), "subscribe", MONO, 30, DIM, anchor="mm")
    ph = ph.out()

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        mid_text(d, 130, nxt, typed(nxt, t, 0.05, 30), fk, DIM)
        letters(d, (W / 2, 235), "Accumulating vs. distributing", ft, t, 0.2, step=0.03)
        mid_text(d, 300, sub, typed(sub, t, tw, 30), fs, DIM)
        mid_text(d, 370, nfa, typed(nfa, t, tn, 30), fk, DIM)
        comp(im, ph, 0, 0, prog(t, 1.0, 1.6))
        return camera(im, 1 + 0.02 * t / dur)
    return frame, [("boom", 0.0, 0.5)]


SCENES_DK = {"hook": dk_hook, "priips": dk_priips, "ch1": dk_chapter(1, "The missing document."), "kid": dk_kid,
             "ch2": dk_chapter(2, "The European twin."), "twin": dk_twin, "ch3": dk_chapter(3, "The real cost."),
             "fees": dk_fees, "check": dk_check, "end": dk_end}

# --------------------------------------------------------------------------- overlays: disclaimer, terminal-style subscribe reminder
NFA_OFF = starts[2]
SUB_T0 = starts[7] + 1.0
f_nfa, f_sub = F(MONO, 18), F(MONO, 26)


def overlays(im, t):
    d = ImageDraw.Draw(im, "RGBA")
    if t < NFA_OFF:
        a = min(prog(t, 0.3, 0.7), 1 - prog(t, NFA_OFF - 0.5, NFA_OFF))
        d.text((44, 56), "not financial advice · education only", font=f_nfa, fill=DIM + (int(255 * a),), anchor="ls")
    u = t - SUB_T0
    if 0 <= u <= 3.4:
        txt = "[ subscribed ✓ ]" if u >= 1.8 else "[ subscribe ]"
        shown = txt if u >= 1.8 else typed(txt, u, 0, 30)
        a = 1 - prog(u, 3.0, 3.4)
        d.text((W - 60 - d.textlength(txt, font=f_sub), 72), shown, font=f_sub, fill=(FG if u >= 1.8 else DIM) + (int(255 * a),), anchor="ls")


typed("[ subscribe ]", 0, 0, 30, SUB_T0)

# --------------------------------------------------------------------------- render: hard cuts, glitches, grain, vignette
yy, xx = np.mgrid[0:H, 0:W]
vig = (1 - 0.38 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.4).clip(0.45, 1)[..., None].astype(np.float32)
grain = [rng.normal(0, 3.2, (H, W, 1)).astype(np.float32) for _ in range(6)]


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
    fn, ev = SCENES_DK[l["scene"]](frames[i] / FPS, i)
    fns.append(fn)
    events += [(n, starts[i] + tt, g) for n, tt, g in ev]
G = [(at, 0.32, g) for n, at, g in events if n == "glitch"] + [(starts[i] - 0.05, 0.12, 0.6) for i in range(1, K)]

vid = os.path.join(E, "video.mp4")
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
for k in range(NF):
    t = k / FPS
    i = max(j for j in range(K) if starts[j] <= t + 1e-6)
    im = fns[i](t - starts[i]).convert("RGB")
    overlays(im, t)
    a = np.asarray(im, dtype=np.uint8)
    amt = max([g * (1 - (t - at) / du) for at, du, g in G if at <= t < at + du] + [0])
    if amt > 0.02 and k % 3 != 2:
        a = glitch(a, amt, k)
    f = a.astype(np.float32) * vig + grain[k % 6]
    enc.stdin.write(f.clip(0, 255).astype(np.uint8).tobytes())
    if k % 300 == 0:
        print("frame", k, "/", NF, flush=True)
enc.stdin.close()
enc.wait()
print("video ok", NF, flush=True)

# --------------------------------------------------------------------------- sound: drone that changes chord per part, silences, booms, glitches, keys
n = int(TOTAL * SR)
tt = np.arange(n) / SR
mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
CHORDS = [(45, 52, 57, 60, 64), (41, 48, 53, 57, 64), (38, 50, 53, 57, 62), (40, 52, 55, 59, 64), (45, 52, 57, 60, 64)]
PART = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]               # chord per line
music = np.zeros(n)
for c, notes in enumerate(CHORDS):
    lines_c = [j for j in range(K) if PART[j] == c]
    a0, a1 = starts[lines_c[0]], starts[lines_c[-1]] + frames[lines_c[-1]] / FPS
    w = np.clip(np.minimum((tt - a0 + 0.6) / 1.2, (a1 + 0.6 - tt) / 1.2), 0, 1)
    if not w.any():
        continue
    pad = np.zeros(n)
    for j, m in enumerate(notes):
        for det in (-0.15, 0.15):
            f = mtof(m) + det
            pad += (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.07 * tt + j))
    pad += 1.4 * np.sin(2 * np.pi * mtof(notes[0] - 12) * tt)
    music += pad * w
music += 0.6 * np.sin(2 * np.pi * mtof(88) * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * tt))
music /= np.max(np.abs(music))
env = np.minimum(1, tt / 2.5) * np.clip((TOTAL - tt) / 2.0, 0, 1)
DIPS = [(starts[0] + lw(0, "can't") + 0.45, 0.45), (starts[7] + lw(7, "€4") - 0.3, 0.3)]
for c0, hw in DIPS:
    env *= 1 - np.clip(1 - np.abs(tt - c0) / hw, 0, 1) ** 0.3
write_wav(os.path.join(E, "music.wav"), (music * env * 0.5).astype(np.float32))

sfx = np.zeros(n + SR, dtype=np.float32)


def put(x, at, g):
    i0 = int(max(0, at) * SR)
    sfx[i0:i0 + len(x)] += (x * g)[: len(sfx) - i0]


bt = np.arange(int(1.6 * SR)) / SR
boom = np.sin(2 * np.pi * np.cumsum(32 + 40 * np.exp(-bt / 0.08)) / SR) * np.exp(-bt / 0.5)
gt = int(0.32 * SR)
gl = rng.standard_normal(gt) * np.repeat(rng.integers(0, 2, gt // 441 + 1), 441)[:gt]
gl = gl + 0.6 * np.sign(np.sin(2 * np.pi * 180 * np.arange(gt) / SR)) * np.repeat(rng.integers(0, 2, gt // 882 + 1), 882)[:gt]
gl /= np.max(np.abs(gl))
kt = np.arange(int(0.03 * SR)) / SR
tick = np.sin(2 * np.pi * 2600 * kt) * np.exp(-kt / 0.005) + 0.4 * rng.standard_normal(len(kt)) * np.exp(-kt / 0.002)
for name, at, g in events:
    put(boom if name == "boom" else gl, at, (0.6 if name == "boom" else 0.22) * g)
for at, du, g in G:
    if du < 0.2:
        put(gl[: int(0.12 * SR)], at, 0.12)
for at in ticks:
    put(tick, at, 0.06 * rng.uniform(0.7, 1.0))
write_wav(os.path.join(E, "sfx.wav"), sfx[:n])
mix = os.path.join(E, "mix.wav")
run(["ffmpeg", "-y", "-i", os.path.join(A, "voice.wav"), "-i", os.path.join(E, "music.wav"), "-i", os.path.join(E, "sfx.wav"), "-filter_complex",
     "[0:a]aformat=channel_layouts=stereo,highpass=f=90,acompressor=threshold=-20dB:ratio=3:attack=5:release=90,asplit=2[v1][v2];"
     "[1:a]aformat=channel_layouts=stereo,volume=0.35[m];[m][v1]sidechaincompress=threshold=0.02:ratio=3:attack=30:release=600[md];"
     "[2:a]aformat=channel_layouts=stereo,volume=0.5[fx];"
     "[v2][md][fx]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
     "-map", "[out]", "-ar", str(SR), mix])


# --------------------------------------------------------------------------- quiet karaoke captions (grey -> white, no box) + final renders
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


def karaoke(until=K - 1):
    ev = []
    for i in range(until + 1):
        for part, a, b in timed_chunks(i):
            ws = [x for x in WT[i] if a - 1e-6 <= x[1] < b - 1e-6]
            txt = "".join(f"{{\\k{max(1, round((wb - wa) * 100))}}}{cl(w)} " for w, wa, wb in ws).rstrip()
            ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b + 0.05)},Sub,,0,0,0,,{{\\fad(120,80)}}{txt}")
    return ev


subs = os.path.join(E, "subs.ass")
with open(subs, "w") as f:
    f.write(HEAD.format(w=W, h=H, styles="Style: Sub,Inter Medium,44,&H00F0F0F0,&H00707070,&H00000000,&H96000000,0,0,0,0,100,100,0.5,0,1,0,2,2,220,220,70,1")
            + "\n".join(karaoke()) + "\n")
final = os.path.join(O, "dark_16x9.mp4")
run(["ffmpeg", "-y", "-i", vid, "-i", mix, "-vf", f"ass={subs}:fontsdir={FD},fade=t=out:st={TOTAL - 0.8:.2f}:d=0.8",
     "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", "-shortest", final])

se = starts[SHORT_LAST + 1]
ssubs = os.path.join(E, "short.ass")
with open(ssubs, "w") as f:
    f.write(HEAD.format(w=1080, h=1920, styles=
                        "Style: Sub,Inter Medium,60,&H00F0F0F0,&H00707070,&H00000000,&H96000000,0,0,0,0,100,100,0.5,0,1,0,2,2,90,90,470,1\n"
                        "Style: Title,Inter Light,74,&H00F0F0F0,&H00F0F0F0,&H00000000,&H00000000,0,0,0,0,100,100,0.5,0,1,0,0,8,80,80,330,1")
            + "\n".join(karaoke(SHORT_LAST)) + "\n"
            + "Dialogue: 1,0:00:00.00," + ass_time(se) + ",Title,,0,0,0,,{\\fad(400,0)}Why Europeans\\Ncan't buy VOO\n")
run(["ffmpeg", "-y", "-t", f"{se:.3f}", "-i", vid, "-t", f"{se:.3f}", "-i", mix, "-filter_complex",
     "[0:v]scale=1080:-2,pad=1080:1920:0:(oh-ih)/2-40:color=0x040405,"
     f"ass={ssubs}:fontsdir={FD},fade=t=out:st={se - 0.5:.2f}:d=0.5[v];[1:a]afade=t=out:st={se - 0.6:.2f}:d=0.6[au]",
     "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", os.path.join(O, "dark_short.mp4")])
print(f"done total={TOTAL:.2f}s short={se:.2f}s")
