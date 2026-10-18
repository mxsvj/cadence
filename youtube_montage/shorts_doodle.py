"""Vertical Shorts (1080x1920) cut from the doodle videos: a hook title on top, the drawing in the middle in an inked frame,
big captions under it, the bottom quarter left free for YouTube's buttons. Frames are re-rendered from the scenes (not
cropped from the 16:9 file) and the sound is the finished mix, cut on line boundaries with 30 ms fades.
Usage: python3 shorts_doodle.py compound|tricks|first1000|debt [index]"""
import importlib
import os
import subprocess
import sys

import cairocffi as cairo
import numpy as np

from doodle_video import *  # noqa: F401,F403
from doodle_video import stk

SW, SH = 1080, 1920
BAND_Y, BAND_H = 545, 690             # where the drawing goes: under the title, above the captions
PAD = 46
CAP_Y, CAP_W, CAP_SIZE = 1300, 860, 82
OUT = os.path.join(D, "shorts_doodle")

# (first line, last line, hook title line 1, hook title line 2 in orange, short title for YouTube)
SHORTS = {
    "compound": [(12, 15, "how fast does", "money double?", "The Rule of 72: How Fast Your Money Doubles"),
                 (17, 22, "start at 25 or 35?", "the gap is huge.", "Start at 25 or 35? The Gap Is Huge"),
                 (34, 36, "a 1.8% fee costs", "€62,000.", "This 1.8% Fee Costs You €62,000")],
    "tricks": [(5, 8, "€9.99", "isn't nine.", "Why €9.99 Isn't Nine Euros"),
               (10, 14, "the option", "nobody picks.", "The Price Option Nobody Picks (and Why It Exists)"),
               (22, 26, "\"half price!\"", "really?", "\"Half Price!\" Is It Really?")],
    "first1000": [(0, 5, "your first €1,000:", "most plans are wrong.", "Your First €1,000: Most Plans Are Wrong"),
                  (23, 26, "€100 a month", "for 30 years?", "€100 a Month for 30 Years"),
                  (28, 31, "the market crashed.", "now what?", "The Market Crashed. Now What?")],
    "debt": [(0, 2, "the most expensive", "button in your app.", "The Most Expensive Button in Your Card App"),
             (16, 20, "avalanche or", "snowball?", "Avalanche or Snowball? Which Debt First"),
             (10, 14, "a 2% minimum", "= 30+ years.", "A 2% Minimum Payment Can Take 30+ Years")],
}
MODULES = {"compound": "build_compound", "tricks": "build_tricks", "first1000": "build_first1000", "debt": "build_debt"}


def portrait_paper(seed):
    _s, arr, pw, ph = make_paper(seed=seed)
    rot = np.ascontiguousarray(np.rot90(arr)[:SH, :SW])
    return cairo.ImageSurface.create_for_data(rot, cairo.FORMAT_RGB24, SW, SH, SW * 4), rot


def wrap(text, size, width):
    lines, cur = [], ""
    for w in text.split():
        cand = (cur + " " + w).strip()
        if cur and text_w(cand, size) > width:
            lines.append(cur)
            cur = w
        else:
            cur = cand
    return lines + ([cur] if cur else [])


def crops(V, t0, t1):
    """Per scene: the part of the 16:9 page that actually has ink during the Short, padded, so the drawing is shown as big
    as the band allows (often a third bigger than the full frame) without cutting anything."""
    q, res = 4, {}
    for g, sc in enumerate(V.SC):
        a, b = max(t0, sc.t0), min(t1, sc.t0 + sc.dur)
        if b <= a:
            continue
        m = np.zeros((H // q, W // q), bool)
        for u in np.linspace(a, b, 8):
            m |= V._ink(sc, u - sc.t0, q=q)
        cols, rows = np.where(m.sum(0) >= 2)[0], np.where(m.sum(1) >= 2)[0]
        if len(cols) < 3:
            res[g] = (0, 0, W, H)
            continue
        x0, x1 = max(0, cols[0] * q - PAD), min(W, (cols[-1] + 1) * q + PAD)
        y0, y1 = max(0, rows[0] * q - PAD), min(H, (rows[-1] + 1) * q + PAD)
        res[g] = (x0, y0, x1 - x0, y1 - y0)
    return res


def captions(V, la, lb):
    raw = [c for i in range(la, lb + 1) for c in V.timed_chunks(i)]
    out, k = [], 0
    while k < len(raw):
        txt, a, b = raw[k]
        while b - a < 0.9 and k + 1 < len(raw) and raw[k + 1][1] - b < 0.7 and len(txt) + len(raw[k + 1][0]) < 60:
            k += 1
            txt, b = txt + " " + raw[k][0], raw[k][2]
        out.append((cl(txt), a, b))
        k += 1
    return out


def make(key, idx):
    V = importlib.import_module(MODULES[key]).V
    V.prepare()
    la, lb, h1, h2, ytitle = SHORTS[key][idx]
    t0 = V.line_times[la][0] - 0.05
    t1 = V.line_times[lb][1] + 0.7
    g0 = V.GI[la]
    V.LAG[g0] = 0.0                                       # a Short starts on its own drawing, never on the previous one
    sc0 = V.SC[g0]
    hook = next((st for st in np.arange(0.0, 2.6, 0.1) if V._ink(sc0, st, q=4).mean() >= 0.025), 2.5)
    vhook = sc0.t0 + min(hook + 0.4, 3.0)       # +0.4 s: let the first word being written finish; the first frame shows the first drawing already there (and never the scene before: line
                                # times are rounded to samples, so "the line's start" can fall a hair before its scene)
    caps = captions(V, la, lb)
    crop = crops(V, t0, t1)
    os.makedirs(OUT, exist_ok=True)
    name = f"short_{key}_{idx + 1}"
    paper, _p, PW, PH = make_paper(seed=3 + V.seed)
    ppaper, _keep = portrait_paper(5 + idx)
    frame = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, SW, SH)
    ts = 104
    title = [T(h1, SW / 2, 300, min(ts, 980 / text_w(h1, 1)), INK, at=-9, anchor="m", rot=-1.5),
             T(h2, SW / 2, 300 + 1.12 * ts, min(ts, 980 / text_w(h2, 1)), ORANGE, at=-9, anchor="m", rot=-1.5)]
    boxes, cap_cache = {}, {}
    vid = os.path.join(OUT, name + "_v.mp4")
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", f"{SW}x{SH}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-tune", "animation", "-pix_fmt", "yuv420p", vid],
                           stdin=subprocess.PIPE)
    n = int(round((t1 - t0) * FPS))
    for k in range(n):
        t = t0 + k / FPS
        V.frame(frame, paper, PW, PH, max(t, vhook))
        frame.flush()
        ctx = cairo.Context(out)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_surface(ppaper, 0, 0)
        ctx.paint()
        tq = math.floor((t - t0) * STEP_FPS) / STEP_FPS
        for e in title:
            e(ctx, tq)
        g = max(j for j in range(len(V.SC)) if V.GSTART[j] <= max(t, vhook) + 1e-6)
        cx, cy, cw, ch = crop.get(g, (0, 0, W, H))
        sc_ = min((SW - 60) / cw, BAND_H / ch)
        ox, oy = (SW - cw * sc_) / 2, BAND_Y + (BAND_H - ch * sc_) / 2
        ctx.save()
        ctx.rectangle(ox, oy, cw * sc_, ch * sc_)
        ctx.clip()
        ctx.translate(ox, oy)
        ctx.scale(sc_, sc_)
        ctx.translate(-cx, -cy)
        ctx.set_source_surface(frame, 0, 0)
        ctx.paint()
        ctx.restore()
        if g not in boxes:
            boxes[g] = Dr([stk(P_rect(ox - 10, oy - 10, cw * sc_ + 20, ch * sc_ + 20, 9, r=14), 8)], 0, 0, seed=g + 3)
        boxes[g](ctx, tq)
        cur = next((c for c in caps if c[1] <= t < max(c[2] + 0.25, c[1] + 1.0)), None)
        if cur:
            if cur[0] not in cap_cache:
                lines = wrap(cur[0], CAP_SIZE, CAP_W)
                cap_cache[cur[0]] = [T(ln, SW / 2 - 40, CAP_Y + j * CAP_SIZE * 1.15, CAP_SIZE, INK, at=-9, anchor="m") for j, ln in enumerate(lines[:3])]
            for e in cap_cache[cur[0]]:
                e(ctx, tq)
        if t > t1 - 2.4:
            if "_cta" not in cap_cache:
                cap_cache["_cta"] = T("full video on the channel.", SW / 2 - 40, CAP_Y + 3.4 * CAP_SIZE, 58, GREY, at=t1 - 2.4 - t0, anchor="m", cps=40)
            cap_cache["_cta"](ctx, tq)
        out.flush()
        enc.stdin.write(bytes(out.get_data()))
    enc.stdin.close()
    enc.wait()
    mix = os.path.join(V.E, "mix.wav")
    final = os.path.join(OUT, name + ".mp4")
    d = t1 - t0
    run(["ffmpeg", "-y", "-i", vid, "-ss", f"{t0:.3f}", "-t", f"{d:.3f}", "-i", mix,
         "-af", f"afade=t=in:st=0:d=0.03,afade=t=out:st={d - 0.45:.3f}:d=0.45,loudnorm=I=-14:TP=-2:LRA=11,"
                "alimiter=limit=0.7:attack=3:release=60:level=disabled:latency=1",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", "-shortest", final])
    os.remove(vid)
    with open(os.path.join(OUT, name + ".txt"), "w") as f:
        f.write(f"{ytitle}\n{d:.1f}\n" + "\n".join(f"{a - t0:.2f}\t{b - t0:.2f}\t{c}" for c, a, b in caps) + "\n")
    print(f"{final}: {d:.1f} s, {os.path.getsize(final) / 1048576:.1f} MiB", flush=True)


if __name__ == "__main__":
    key = sys.argv[1]
    for i in ([int(sys.argv[2])] if len(sys.argv) > 2 else range(len(SHORTS[key]))):
        make(key, i)
