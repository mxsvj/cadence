"""Turn an assembled build (build_x.py) into its "human pass" version (build_x_h.py): python3 humanize.py build_etf.py
Adds human.py before the tail, varies the pauses between lines, and patches the tail (cuts, camera, sound, captions)."""
import os
import sys

D = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(D, sys.argv[1])
s = open(src_path).read()


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, (a[:70], s.count(a))
    s = s.replace(a, b)


# voice cache (older builds regenerate every line)
if "reuse the audio already made" not in s:
    rep('''def kokoro_say(text, path):
    if not _KOKORO:''', '''def kokoro_say(text, path):
    if os.path.exists(path) and os.path.exists(path + ".txt") and open(path + ".txt").read() == text:
        return                                     # same line, same text: reuse the audio already made
    if not _KOKORO:''')
    rep('''        w.writeframes(pcm.tobytes())


def tts(''', '''        w.writeframes(pcm.tobytes())
    open(path + ".txt", "w").write(text)


def tts(''')

# pauses: no more metronome, each gap depends on what was just said and what comes next
rep('voice = [tts(i, l["tts"]) for i, l in enumerate(LINES)]', '''def gap_for(i):
    """Breath after line i: shorter after a chapter card or a short line, longer before a new chapter or after a big number."""
    import random as _r
    rr = _r.Random(i * 7919 + 13)
    sc = LINES[i]["scene"]
    kind = sc[0] if isinstance(sc, tuple) else sc
    nxt = LINES[i + 1]["scene"] if i + 1 < len(LINES) else None
    g = GAP
    if kind == "chap":
        g -= 0.4
    if isinstance(nxt, tuple) and nxt[0] == "chap":
        g += 0.5
    if kind == "big" and any(len(it) > 2 and it[2] == "BLACK" for it in sc[1]):
        g += 0.35
    words = len(LINES[i]["sub"].split())
    g += -0.22 if words <= 6 else 0.12 if words >= 22 else 0.0
    return max(0.5, g + rr.uniform(-0.18, 0.18))


voice = [tts(i, l["tts"]) for i, l in enumerate(LINES)]''')
rep("    n = round((len(v) / SR + GAP + (LEAD", "    n = round((len(v) / SR + gap_for(i) + (LEAD")

# human.py goes right before the tail
TAIL_MARK = "# --------------------------------------------------------------------------- overlays: disclaimer"
rep(TAIL_MARK, open(os.path.join(D, "human.py")).read() + "\n\n" + TAIL_MARK)

# tail: no dust in front of every shot
rep('''    for x0, y0, vy, vx, r, ph in DUST:              # dust drifting in front of the scene (parallax with the camera)
        x, y = (x0 + vx * t) % W, (y0 - vy * t) % H
        d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 200, 210, int(38 + 28 * math.sin(t * 1.3 + ph))))
''', "")
# tail: glitches only on some chapter cuts, a black frame on others, plain hard cuts everywhere else
rep('''    G = [(at, 0.32, g) for n, at, g in events if n == "glitch"] + [(c - 0.05, 0.12, 0.6) for c in cut_g]
    G += [(starts[j] - 0.03, 0.08, 0.3) for j in range(1, K) if starts[j] not in cut_g]     # a flick of glitch on every other cut''',
    '''    _gr = random.Random(5)
    G = [(at, 0.32, g) for n, at, g in events if n == "glitch"]
    DIPB = []
    for c in cut_g:
        x_ = _gr.random()
        if x_ < 0.4:
            G.append((c - 0.05, _gr.uniform(0.06, 0.15), _gr.uniform(0.3, 0.65)))
        elif x_ < 0.7:
            DIPB.append(c)                       # one black frame, like a rough cut that was kept''')
# tail: graphics on twos (12 fps), handheld camera at full rate on top
rep('''        im = fns[i](t - starts[i]).convert("RGB")''', '''        ts = t - starts[i]
        tq = math.floor(ts * STEP_FPS + 1e-6) / STEP_FPS
        if _LAST[0] != (i, tq):
            _SD["camreq"] = (500, 0.035)
            _LAST[:] = [(i, tq), fns[i](tq).convert("RGB"), _SD["camreq"]]
        im = handheld(_LAST[1], ts, frames[i] / FPS, i, _LAST[2][0], _LAST[2][1], HITS[i], is_chap[i])
        if any(c <= t < c + 1.2 / FPS for c in DIPB):
            im = Image.new("RGB", (W, H), (0, 0, 0))''')
rep("    for k in range(K0, K1):\n", "    _LAST = [None, None, None]\n    for k in range(K0, K1):\n")
# sound: not every hit gets a boom, some land in a sudden silence, some have no sound at all; far fewer key ticks
rep('''    for name, at, g in events:
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
        put(tick, at, 0.06 * srng.uniform(0.7, 1.0))''', '''    _ar = random.Random(11)
    for name, at, g in events:
        if name == "boom":
            if at in SILENT_AT or at in MUTE_AT:
                continue
            put(boom, at, 0.6 * g * _ar.uniform(0.7, 1.1))
        elif name == "glitch":
            put(gl, at, 0.22 * g)
        elif _ar.random() < 0.45:
            put(tick, at + _ar.uniform(-0.012, 0.012), 0.12 * g * _ar.uniform(0.5, 1.1))
    for at, du, g in G:
        put(gl[: int(du * SR)], at, 0.1 * g)
    for at in ticks:
        if _ar.random() < 0.33:
            put(tick, at + _ar.uniform(-0.01, 0.01), 0.06 * _ar.uniform(0.4, 1.0))
    for at in SILENT_AT:                          # the silence also takes the effects with it
        a0, a1 = int((at - 0.03) * SR), int((at + 0.55) * SR)
        sfx[a0:a1] *= 0''')
# music: one or two tape-stops into a chapter card, and abrupt silences on some key numbers
rep('''    write_wav(os.path.join(E, "music.wav"), (music * env * 0.5).astype(np.float32))''', '''    _hr = random.Random(17)
    BOOMS = [at for n_, at, g in events if n_ == "boom" and g >= 0.5]
    SILENT_AT = [at for at in BOOMS if _hr.random() < 0.16]
    MUTE_AT = [at for at in BOOMS if at not in SILENT_AT and _hr.random() < 0.16]
    mus = music * env * 0.5
    for at in SILENT_AT:                          # cut to silence, no fade: the number lands in the void
        a0, a1 = int((at - 0.03) * SR), int((at + 0.55) * SR)
        mus[a0:a1] = 0
        mus[a1:a1 + 400] *= np.linspace(0, 1, len(mus[a1:a1 + 400]))

    def tape_stop(x, t0, t1):
        a, b = int(t0 * SR), int(t1 * SR)
        seg = x[a:b].copy()
        if len(seg) < 10:
            return
        sp = np.linspace(1, 0, len(seg)) ** 1.4
        pos = np.cumsum(sp)
        pos -= pos[0]
        x[a:b] = np.interp(pos, np.arange(len(seg)), seg) * np.linspace(1, 0.5, len(seg))

    chap_j = [j for j in range(2, K) if is_chap[j]]
    for j in _hr.sample(chap_j, min(2, len(chap_j))):
        c = starts[j]
        tape_stop(mus, c - 0.6, c)
        mus[int(c * SR):int((c + 0.3) * SR)] = 0
    write_wav(os.path.join(E, "music.wav"), mus.astype(np.float32))''')
# captions: no karaoke, no centred white line; a paper sticker on the left, each chunk placed and tilted a little differently
rep('''            txt = "".join(f"{{\\\\k{max(1, round((wb - wa) * 100))}}}{cl(w)} " for w, wa, wb in ws).rstrip()
            ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b + 0.05)},Sub,,0,0,0,,{{\\\\fad(120,80)}}{txt}")''',
    '''            txt = " ".join(cl(w) for w, wa, wb in ws)
            x_, y_, r_ = 128 + _cr.randint(0, 38), 1018 + _cr.randint(-7, 5), _cr.uniform(-0.8, 0.8)
            ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b + 0.05)},Sub,,0,0,0,,{{\\\\an1\\\\pos({x_},{y_})\\\\frz{r_:.2f}\\\\fad(50,30)}}{txt}")''')
rep("    ev = []\n    for i in range(K):\n        for part, a, b in timed_chunks(i):", "    ev, _cr = [], random.Random(21)\n    for i in range(K):\n        for part, a, b in timed_chunks(i):")
rep('styles="Style: Sub,Inter Medium,44,&H00F0F0F0,&H00707070,&H00000000,&H96000000,0,0,0,0,100,100,0.5,0,1,0,2,2,220,220,70,1"',
    'styles="Style: Sub,FreeSans,42,&H00141414,&H00141414,&H00E2ECF0,&H00000000,-1,0,0,0,100,100,-1,0,3,10,0,1,0,0,0,1"')
# outputs next to the originals, never over them
rep('E = os.path.join(D, ', 'E = os.path.join(D, "h_" + ')
s = s.replace('"_dark_16x9.mp4"', '"_human_16x9.mp4"').replace('_dark_16x9.mp4")', '_human_16x9.mp4")').replace('_sample.mp4"', '_human_sample.mp4"')
out = src_path.replace(".py", "_h.py")
open(out, "w").write(s)
print("wrote", os.path.basename(out))
