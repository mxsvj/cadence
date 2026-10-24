"""Story mode for the doodle engine: a voice per character (Kokoro), a 'through the door' or 'on the radio' colour on a line,
extra silence after a line, sound cues that always play because the story needs them (knocks, a phone buzz), and as many
tape stops as the story has shocks. Everything else (drawing, captions, framing, mix) is the explainer engine unchanged.

    V = Story("door1", tapes=[("And that's when", "Don't open")], keys=dict(prog=[...], roots=[...], bpm=58))
    V.L("s2", '"Maya? It\\'s Mum."', voice=MUM, fx="door", after=1.2)
    S.add(snd="knock3", at=S.e(0) + 0.2)      # inside a scene: three knocks, always heard"""
import hashlib
import wave

from doodle_video import *  # noqa: F401,F403
from doodle_video import kokoro_say, run, sentences, write_wav

FX = {"door": "lowpass=f=1700,highpass=f=150,aecho=0.8:0.5:26:0.2,volume=1.3",
      "radio": "highpass=f=330,lowpass=f=3300,acompressor=threshold=-26dB:ratio=4:attack=5:release=80,volume=1.4",
      "whisper": "highpass=f=120,volume=1.15"}


def _read(path):
    with wave.open(path) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def knock_s(rng, vel=1.0):
    """A knuckle on a wooden door: a click, then the panel's low modes ringing for a few tens of ms."""
    m = int(0.28 * SR)
    tt = np.arange(m) / SR
    body = sum(a * np.sin(2 * np.pi * f * rng.uniform(0.97, 1.03) * tt + rng.uniform(0, 6)) * np.exp(-tt / d)
               for f, a, d in ((92, 1.0, 0.075), (168, 0.75, 0.05), (305, 0.45, 0.03), (540, 0.22, 0.018)))
    click = np.convolve(rng.standard_normal(m), np.ones(4) / 4, "same") * np.exp(-tt / 0.0035) * 0.9
    x = (body + click) * (1 - np.exp(-tt / 0.0012))
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


class Story(Video):
    def __init__(self, slug, tapes=(), **kw):
        super().__init__(slug, **kw)
        self.tapes = list(tapes)

    def L(self, g, sub, voice="af_heart", fx=None, speed=None, after=0.0):
        self.LINES.append(dict(g=g, sub=sub, voice=voice, fx=fx, speed=speed, after=after))

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
        """The bed, then each tape stop: the music winds down in 0.7 s as the line ends and stays out (room tone only) until
        the line it comes back on."""
        super().music()
        path = os.path.join(self.E, "music.wav")
        mus = _read(path).copy()
        room = np.convolve(np.random.default_rng(78).standard_normal(len(mus)), np.ones(24) / 24, "same").astype(np.float32) * 0.02
        for a_line, b_line in self.tapes:
            ts = self.line_times[self._line(a_line)][1] + 0.05
            tb = self.line_times[self._line(b_line)][0] - 0.35
            a_, b_, c_ = int((ts - 0.7) * SR), int(ts * SR), int(tb * SR)
            seg = mus[a_:b_].copy()
            pos = np.cumsum(np.linspace(1, 0, len(seg)) ** 1.3)
            pos -= pos[0]
            mus[a_:b_] = np.interp(pos, np.arange(len(seg)), seg) * np.linspace(1, 0.3, len(seg))
            mus[b_:c_] = room[b_:c_]
            r = min(int(0.9 * SR), len(mus) - c_)
            mus[c_:c_ + r] = mus[c_:c_ + r] * np.linspace(0, 1, r) + room[c_:c_ + r] * np.linspace(1, 0, r)
        write_wav(path, mus)

    def sfx(self):
        super().sfx()
        path = os.path.join(self.E, "sfx.wav")
        fx = _read(path).copy()
        rng = np.random.default_rng(31 + self.seed)

        def put(x, at, g):
            i0 = int(at * SR)
            if 0 <= i0 < len(fx):
                fx[i0:i0 + len(x)] += (x * g)[: len(fx) - i0]

        for kind, at in [ev for sc in self.SC for ev in sc.snd]:
            if kind == "knock3":
                for k, dt in enumerate((0.0, 0.5, 1.0)):
                    put(knock_s(rng), at + dt + rng.uniform(-0.03, 0.03), 0.62 * (1.0, 0.92, 1.04)[k])
            elif kind == "buzz":
                put(buzz_s(rng), at, 0.16)
        write_wav(path, fx)
