"""Story mode for the doodle engine: a voice per character (Kokoro), a 'through the door' or 'on the radio' colour on a line,
extra silence after a line, sound cues that always play because the story needs them (knocks, a phone buzz), and as many
tape stops as the story has shocks. Everything else (drawing, captions, framing, mix) is the explainer engine unchanged.

    V = Story("door1", tapes=[("And that's when", "Don't open")], keys=dict(prog=[...], roots=[...], bpm=58))
    V.L("s2", '"Maya? It\\'s Mum."', voice=MUM, fx="door", after=1.2)
    S.add(snd="knock3", at=S.e(0) + 0.2)      # inside a scene: three knocks, always heard"""
import hashlib
import wave

from doodle_video import *  # noqa: F401,F403
from doodle_video import cl, kokoro_say, run, sentences, write_wav

FX = {"door": "lowpass=f=3000,highpass=f=160,aecho=0.8:0.45:24:0.18",
      "radio": "highpass=f=330,lowpass=f=3300,acompressor=threshold=-26dB:ratio=4:attack=5:release=80,volume=1.4",
      "whisper": "highpass=f=120",
      # a child: +5 semitones with the formants kept, then everything up 12 % (formants too), same speed: about 265 Hz
      "child": "rubberband=pitch=1.335:formant=preserved,asetrate=26880,aresample=24000,atempo=0.8929,highpass=f=170"}
FX["hall"] = "aecho=0.8:0.55:70|130:0.3|0.2"                                    # said out in the stairwell
FX["child_hall"] = FX["child"] + "," + FX["hall"]
FX["child_far"] = FX["child"] + ",lowpass=f=2600,aecho=0.8:0.6:90|170:0.35|0.25"   # from a flat upstairs
FX["self_door"] = FX["door"]                                                     # Maya's own words, coming back through the door
FX["phone"] = "highpass=f=350,lowpass=f=3400,acompressor=threshold=-24dB:ratio=3:attack=5:release=80"
# a child crying from a flat upstairs: higher still, far, shaking
FX["child_far2"] = FX["child"] + ",rubberband=pitch=1.12,lowpass=f=2400,aecho=0.8:0.6:90|170:0.35|0.25,tremolo=f=6:d=0.35,vibrato=f=5.5:d=0.25"
TARGET = -20.0          # every line's speech level (dBFS RMS over its voiced 20 ms windows), plus the line's own gain


def _read(path):
    with wave.open(path) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def knock_s(rng, vel=1.0):
    """A knuckle on a wooden door: a bright crack (what a phone speaker plays), the panel's low modes ringing for a few
    tens of ms, and the door rattling in its frame."""
    m = int(0.3 * SR)
    tt = np.arange(m) / SR
    body = sum(a * np.sin(2 * np.pi * f * rng.uniform(0.97, 1.03) * tt + rng.uniform(0, 6)) * np.exp(-tt / d)
               for f, a, d in ((92, 1.0, 0.075), (168, 0.75, 0.05), (305, 0.5, 0.03), (540, 0.3, 0.018), (1150, 0.25, 0.01)))
    nz = rng.standard_normal(m)
    hp = nz - np.convolve(nz, np.ones(10) / 10, "same")
    crack = np.convolve(hp, np.ones(3) / 3, "same") * np.exp(-tt / 0.006) * 1.6
    rattle = np.zeros(m)
    for d in (0.028, 0.051, 0.07):
        k0 = int(d * SR)
        rattle[k0:] += hp[: m - k0] * np.exp(-(tt[: m - k0]) / 0.004) * rng.uniform(0.15, 0.3)
    x = (0.8 * body + crack + rattle) * (1 - np.exp(-tt / 0.0012))
    return (x / np.max(np.abs(x)) * vel).astype(np.float32)


def buzz_s(rng, vel=1.0):
    """A phone vibrating on a table: two rattly pulses."""
    out = []
    for k in range(2):
        m = int(0.36 * SR)
        tt = np.arange(m) / SR
        x = np.tanh(2.5 * np.sin(2 * np.pi * 172 * tt)) + 0.35 * rng.standard_normal(m) * (np.sin(2 * np.pi * 172 * tt) > 0.6)
        env = np.minimum(1, tt / 0.02) * np.clip((0.36 - tt) / 0.04, 0, 1)
        out += [x * env, np.zeros(int(0.17 * SR))]
    x = np.concatenate(out)
    return (x / np.max(np.abs(x)) * vel).astype(np.float32)


def heli_s(rng, shape, dur=6.0):
    """Rotor blades (a low thump about five times a second through band-limited noise) and a faint turbine. shape: "in" grows
    and holds, "out" starts close and fades with its pitch dropping, "turn" swells as it comes back."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    u = t / dur
    nz = rng.standard_normal(n)
    lp = np.convolve(nz, np.ones(30) / 30, "same")
    band = lp - np.convolve(lp, np.ones(400) / 400, "same")
    rate = 5.2 * (1 - 0.06 * u if shape == "out" else 1.0)
    blade = (0.5 + 0.5 * np.cos(2 * np.pi * np.cumsum(np.full(n, rate)) / SR)) ** 6
    x = band * blade * 3.0 + 0.6 * np.sin(2 * np.pi * 55 * t) * blade + 0.05 * np.sin(2 * np.pi * 310 * t)
    env = {"in": np.minimum(1, u / 0.7) ** 2, "out": (1 - u) ** 1.6, "turn": np.minimum(1, u / 0.6) ** 1.5}[shape]
    env = env * np.clip(u / 0.03, 0, 1) * np.clip((1 - u) / 0.08, 0, 1)
    x = x * env
    return (x / np.abs(x).max()).astype(np.float32)


def rain_s(rng, dur=5.5):
    """Heavy rain on leaves: bright noise with a slow swell, and drops ticking on top."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    nz = rng.standard_normal(n)
    hiss = nz - np.convolve(nz, np.ones(8) / 8, "same")
    hiss = np.convolve(hiss, np.ones(3) / 3, "same")
    drops = np.zeros(n)
    for _ in range(int(dur * 35)):
        j = int(rng.uniform(0, n - 300))
        drops[j:j + 300] += rng.uniform(0.3, 1.0) * np.sin(2 * np.pi * rng.uniform(1800, 4200) * np.arange(300) / SR) * np.exp(-np.arange(300) / 40)
    env = np.clip(t / 1.2, 0, 1) * np.clip((dur - t) / 1.6, 0, 1) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.3 * t))
    x = (hiss + 0.5 * drops) * env
    return (x / np.abs(x).max()).astype(np.float32)


class Story(Video):
    KNOCK_GAP = 0.85        # slow, polite

    def __init__(self, slug, tapes=(), swells=(), dips=(), silences=(), **kw):
        """tapes: (line it stops after, line it comes back on, "tape" | "cut"); swells: (line, last line, seconds after it):
        a low rumble that rises and is chopped off; dips: (line, line or None for the end, gain) on the music;
        silences: (line, next line): no music at all from the end of the first to the start of the second (room tone only)."""
        super().__init__(slug, **kw)
        self.tapes, self.swells, self.dips, self.silences = list(tapes), list(swells), list(dips), list(silences)

    def L(self, g, sub, voice="af_heart", fx=None, speed=None, after=0.0, gain=0.0, who=None):
        self.LINES.append(dict(g=g, sub=sub, voice=voice, fx=fx, speed=speed, after=after, gain=gain, who=who))

    def speak(self, sub):
        return super().speak(sub.replace('"', ""))

    def tts(self, i, sub):
        """As Video.tts, with the line's own voice, speed and colour (cached under a key of all three)."""
        l = self.LINES[i]
        voice, speed, fx = l["voice"], l["speed"] or self.speed, l["fx"]
        key = hashlib.md5(f"{voice}|{speed}|{FX.get(fx, '')}".encode()).hexdigest()[:6]
        lang = "en-us" if voice.startswith("a") else "en-gb"
        parts, spans, t = [], [], 0.0
        for k, snt in enumerate(sentences(sub)):
            raw = os.path.join(self.A, "voice", f"l{i:02d}s{k}_{key}_raw.wav")
            out = os.path.join(self.A, "voice", f"l{i:02d}s{k}_{key}.wav")
            kokoro_say(self.speak(snt), raw, voice=voice, lang=lang, speed=speed)
            if not (os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(raw)):
                af = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,"
                      "areverse" + (("," + FX[fx]) if fx else ""))
                run(["ffmpeg", "-y", "-i", raw, "-af", af, "-ar", str(SR), "-ac", "1", out])
            v = _read(out).copy()
            if fx == "whisper":                                       # breath instead of voice: keep a little tone, mostly shaped noise
                rw = np.random.default_rng(i * 31 + k)
                env = np.convolve(np.abs(v), np.ones(441) / 441, "same")
                nz = rw.standard_normal(len(v))
                band = np.convolve(nz - np.convolve(nz, np.ones(6) / 6, "same"), np.ones(3) / 3, "same")
                breath = band * env
                breath *= np.sqrt(np.mean(v ** 2)) / max(1e-9, np.sqrt(np.mean(breath ** 2)))
                v = (0.3 * v + 0.9 * breath).astype(np.float32)
            win = int(0.02 * SR)
            rms = np.sqrt(np.convolve(v ** 2, np.ones(win) / win, "same")[::win])
            act = rms[rms > 0.1 * rms.max()]
            g = 10 ** ((TARGET + l["gain"]) / 20) / max(1e-6, np.sqrt(np.mean(act ** 2)))
            v *= min(g, 0.98 / max(1e-6, np.abs(v).max()))           # level-matched between characters, never clipped
            f = min(int(0.03 * SR), len(v) // 4)
            v[:f] *= np.linspace(0, 1, f)
            v[-f:] *= np.linspace(1, 0, f)
            if parts:
                gap = 0.24 if spans[-1][2].rstrip("*")[-1:] == ":" else 0.34
                parts.append(np.zeros(int(gap * SR), np.float32))
                t += gap
            spans.append((t, t + len(v) / SR, snt))
            parts.append(v)
            t += len(v) / SR
        self.SPANS[i] = spans
        return np.concatenate(parts)

    def gap_for(self, i):
        return super().gap_for(i) + self.LINES[i]["after"]

    def _line(self, prefix):
        return next(j for j, l in enumerate(self.LINES) if l["sub"].startswith(prefix))

    def music(self):
        """A low D drone that breathes, and a lone high note every few seconds (a music box nobody wound). Then the dips,
        the tape stops ("tape": winds down in 0.7 s) or hard cuts ("cut"), and the bed pulled out under every knock."""
        n = int(self.TOTAL * SR) + SR
        tt = np.arange(n) / SR
        rng = np.random.default_rng(5 + self.seed)
        mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
        mus = sum(a * np.sin(2 * np.pi * f * tt + p) for f, a, p in ((73.42, 1.0, 0), (73.58, 0.8, 1), (110.0, 0.45, 2), (146.83, 0.22, 3)))
        mus = (mus * (0.7 + 0.3 * np.sin(2 * np.pi * 0.045 * tt + 1.0)) * 0.22).astype(np.float32)
        t = 1.6
        while t < self.TOTAL:
            f = mtof(int(rng.choice([74, 77, 81, 84, 76, 70])))
            k = np.arange(int(3.2 * SR)) / SR
            x = (np.sin(2 * np.pi * f * k) + 0.3 * np.sin(2 * np.pi * 2.01 * f * k)) * np.exp(-k / 1.1) * (1 - np.exp(-k / 0.004)) * 0.14
            i0 = int(t * SR)
            mus[i0:i0 + len(x)] += x[: n - i0].astype(np.float32)
            t += rng.uniform(4.5, 8.5)
        mus /= max(1e-6, np.abs(mus).max())
        duck = np.ones(n, np.float32)
        for a_, b_ in [(self.q_at(a) - 0.05, self.q_at(b) - 0.2) for a, b in self.hush]:
            duck[int(a_ * SR):int(b_ * SR)] *= 0.16
        for a, b, gn in self.dips:
            duck[int(self.q_at(a) * SR):(int(self.q_at(b) * SR) if b else n)] *= gn
        for kind, at in [ev for sc in self.SC for ev in sc.snd]:
            if kind in ("knock3", "knock1"):
                duck[int((at - 0.12) * SR):int((at + (2 * self.KNOCK_GAP + 0.4 if kind == "knock3" else 0.5)) * SR)] *= 0.2
        for a_line, b_line in self.silences:
            duck[int((self.line_times[self._line(a_line)][1] + 0.05) * SR):int((self.line_times[self._line(b_line)][0] - 0.25) * SR)] = 0.0
        w = int(0.08 * SR)                                              # 80 ms ramps, so a dip never clicks
        c = np.concatenate([[0.0], np.cumsum(duck, dtype=np.float64)])
        duck = ((c[w:] - c[:-w]) / w).astype(np.float32)
        duck = np.concatenate([duck, np.ones(n - len(duck), np.float32)])
        env = np.minimum(1, tt / 2.0) * np.clip((self.TOTAL - tt) / 2.5, 0, 1)
        mus *= (env * duck).astype(np.float32)
        room = np.convolve(np.random.default_rng(78).standard_normal(n), np.ones(24) / 24, "same").astype(np.float32) * 0.02
        for tp in self.tapes:
            a_line, b_line, mode = (tp + ("tape",))[:3]
            ts = self.line_times[self._line(a_line)][1] + 0.05
            tb = self.line_times[self._line(b_line)][0] - 0.35
            a_, b_, c_ = int((ts - (0.7 if mode == "tape" else 0.06)) * SR), int(ts * SR), int(tb * SR)
            seg = mus[a_:b_].copy()
            if mode == "tape":
                pos = np.cumsum(np.linspace(1, 0, len(seg)) ** 1.3)
                pos -= pos[0]
                mus[a_:b_] = np.interp(pos, np.arange(len(seg)), seg) * np.linspace(1, 0.3, len(seg))
            else:
                mus[a_:b_] = seg * np.linspace(1, 0, len(seg))
            mus[b_:c_] = 0.0
            r = min(int(0.9 * SR), len(mus) - c_)
            mus[c_:c_ + r] *= np.linspace(0, 1, r)
        for a_line, b_line, off in self.swells:                       # a rumble that builds, then stops dead on the cut
            t0, t1 = self.line_times[self._line(a_line)][0], self.line_times[self._line(b_line)][1] + off
            i0, i1 = int(t0 * SR), int(t1 * SR)
            k = np.arange(i1 - i0) / SR
            u = k / max(1e-6, k[-1])
            sub = (np.sin(2 * np.pi * 41 * k) + 0.6 * np.sin(2 * np.pi * 82.4 * k + 1) + 0.25 * np.sin(2 * np.pi * 123.5 * k + 2)
                   + 0.3 * np.convolve(rng.standard_normal(len(k)), np.ones(60) / 60, "same") * 8)
            env_s = u ** 2 * 0.55 * (1 + 0.15 * np.sin(2 * np.pi * 0.9 * k))
            env_s[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
            hi = (np.sin(2 * np.pi * 1480 * k) + np.sin(2 * np.pi * 1568 * k) + 0.6 * np.sin(2 * np.pi * 2217 * k + 1)) * 0.12   # a high, beating layer phones can play
            mus[i0:i1] += ((sub + hi * u) * env_s).astype(np.float32)
        mus = mus * 0.6 + room                                         # room tone: never digital zero, even in the silences
        write_wav(os.path.join(self.E, "music.wav"), mus[: int(self.TOTAL * SR)])

    def sfx(self):
        """Only the sounds the story needs: knocks, the phone, a helicopter, rain. No scribbles, no pops."""
        fx = np.zeros(int(self.TOTAL * SR), np.float32)
        rng = np.random.default_rng(31 + self.seed)

        def put(x, at, g):
            i0 = int(at * SR)
            if 0 <= i0 < len(fx):
                fx[i0:i0 + len(x)] += (x * g)[: len(fx) - i0]

        for kind, at in [ev for sc in self.SC for ev in sc.snd]:
            if kind == "knock3":
                for k in range(3):
                    put(knock_s(rng), at + k * self.KNOCK_GAP + rng.uniform(-0.03, 0.03), 1.06 * (1.0, 0.92, 1.04)[k])
            elif kind == "knock1":
                put(knock_s(rng), at, 1.06)
            elif kind == "knock1m":                                    # a knock heard from behind a wall
                put(np.convolve(knock_s(rng), np.ones(14) / 14, "same").astype(np.float32), at, 0.8)
            elif kind == "buzz":
                put(buzz_s(rng), at, 0.16)
            elif kind == "clink":                                      # an empty bottle knocked over on a tiled floor
                m = int(0.5 * SR)
                tt = np.arange(m) / SR
                x = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt / d) for f, a, d in ((2480, 1.0, 0.09), (3910, 0.6, 0.06), (6150, 0.3, 0.03)))
                x[int(0.11 * SR):] += 0.5 * x[: m - int(0.11 * SR)]                    # it bounces once
                put((x / np.abs(x).max()).astype(np.float32), at, 0.5)
                m2 = int(1.1 * SR)                                     # then rolls: a low rumble with glassy ticks, slowing down
                t2 = np.arange(m2) / SR
                rum = np.convolve(rng.standard_normal(m2), np.ones(40) / 40, "same") * 3
                ticks = np.zeros(m2)
                tk = 0.0
                while tk < 1.0:
                    j = int(tk * SR)
                    ticks[j:j + 400] += np.sin(2 * np.pi * 3100 * np.arange(min(400, m2 - j)) / SR) * np.exp(-np.arange(min(400, m2 - j)) / 60)
                    tk += 0.06 + 0.2 * tk
                roll = (rum * 0.6 + ticks * 0.5) * np.clip((1.1 - t2) / 1.1, 0, 1)
                put((roll / np.abs(roll).max()).astype(np.float32), at + 0.2, 0.25)
            elif kind in ("heli_in", "heli_out", "heli_turn"):
                put(heli_s(rng, kind[5:]), at, 0.42)
            elif kind == "rain":
                put(rain_s(rng), at, 0.16)
        write_wav(os.path.join(self.E, "sfx.wav"), fx)

    CUE = {"knock3": ("[three slow knocks]", 2.0), "knock1": ("[a knock]", 1.0), "buzz": ("[phone buzzing]", 1.0),
           "clink": ("[a bottle rolls on the floor]", 1.4), "heli_in": ("[a helicopter, getting closer]", 1.6),
           "heli_out": ("[the helicopter fades away]", 1.6), "heli_turn": ("[the helicopter turns back]", 1.6), "rain": ("[heavy rain]", 1.4)}

    def write_srt(self, path):
        """As Video.write_srt, but a cue never mixes two speakers, and the knocks and the buzz get their own cues
        (for people watching on mute)."""
        def stamp(t):
            ms = int(round(t * 1000))
            return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
        raw = [((f"{self.LINES[i]['who']}: " if self.LINES[i]["who"] and j == 0 else "") + part, a, b, i)
               for i in range(len(self.LINES)) for j, (part, a, b) in enumerate(self.timed_chunks(i))]       # who speaks, for viewers on mute
        cues, k = [], 0
        while k < len(raw):
            txt, a, b, i = raw[k]
            while (b - a < 0.9 and k + 1 < len(raw) and raw[k + 1][3] == i and raw[k + 1][1] - b < 0.7
                   and len(txt) + len(raw[k + 1][0]) < 60):
                k += 1
                txt, b = txt + " " + raw[k][0], raw[k][2]
            cues.append((cl(txt), a, b))
            k += 1
        spoken = [(a, b) for _, a, b in cues]
        for kind, at in [ev for sc in self.SC for ev in sc.snd]:
            if kind in self.CUE and not any(a < at + 0.5 and at < b for a, b in spoken):   # only in the gaps: never cut a line short
                cues.append((self.CUE[kind][0], at, at + self.CUE[kind][1]))
        cues.sort(key=lambda c: c[1])
        out = []
        for c, (part, a, b) in enumerate(cues):
            nxt = cues[c + 1][1] - 0.04 if c + 1 < len(cues) else b + 1.0
            end = min(max(b + 0.3, a + 1.0), nxt)
            out.append(f"{c + 1}\n{stamp(a)} --> {stamp(end)}\n{part}\n")
        open(path, "w").write("\n".join(out))
