"""'Can Europeans buy VOO?' long version (~6 min) in the dark video-essay style (inspired by the EGO channel):
black screen, typed monospace text, hard cuts with glitches, grain and vignette, ambient drone with silences,
quiet grey-to-white karaoke captions."""
import math
import os
import re
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(D, "assets_long")
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
def L(scene, sub, tts=None):
    return dict(scene=scene, sub=sub, tts=tts or sub)


LINES = [
    L("wall", "If you watch American finance YouTube, you've heard it a thousand times: just buy **VOO.**",
      "If you watch American finance YouTube, you've heard it a thousand times: just buy V O O."),
    L("search", "So you open your broker in Europe, you type VOO, and... nothing. Not available in your region.",
      "So you open your broker in Europe, you type V O O, and... nothing. Not available in your region."),
    L("reason", "There's a reason for that. And there's a simple way around it."),
    L("agenda", "In this video: what VOO actually is, why Europe blocks it, and the European version you can buy instead, "
                "for almost the same price.",
      "In this video: what V O O actually is, why Europe blocks it, and the European version you can buy instead, "
      "for almost the same price."),
    L("ch1", "Part one. What is VOO?", "Part one. What is V O O?"),
    L("basket", "VOO is an ETF. Think of it as a basket. With one click, you buy a tiny piece of many companies at once.",
      "V O O is an E T F. Think of it as a basket. With one click, you buy a tiny piece of many companies at once."),
    L("sp500", "This basket follows the S&P 500: about 500 big American companies. "
               "Apple, Microsoft, Nvidia, Amazon, and hundreds more.",
      "This basket follows the S and P five hundred: about five hundred big American companies. "
      "Apple, Microsoft, Nvidia, Amazon, and hundreds more."),
    L("cheap", "VOO is run by Vanguard, and it's famous for one reason: it's incredibly cheap. 0.03% a year. On $10,000, that's $3.",
      "V O O is run by Vanguard, and it's famous for one reason: it's incredibly cheap. "
      "Zero point zero three percent a year. On ten thousand dollars, that's three dollars."),
    L("since2010", "It launched in 2010. Today, it's one of the world's biggest funds.",
      "It launched in twenty ten. Today, it's one of the world's biggest funds."),
    L("index", "And it's an index fund: nobody picks the winners. You simply own the whole market, the good and the bad."),
    L("usa", "That's why every American video says: buy it. But those videos are made for Americans."),
    L("ch2", "Part two. Why Europe blocks it."),
    L("priips", "In 2018, the European Union started applying a rule called PRIIPs. "
                "It's there to protect everyday investors, people like you and me.",
      "In twenty eighteen, the European Union started applying a rule called preeps. "
      "It's there to protect everyday investors, people like you and me."),
    L("kid", "The rule says: if a product is sold to regular investors, it must come with a short document. "
             "It's called a KID. Key Information Document.",
      "The rule says: if a product is sold to regular investors, it must come with a short document. "
      "It's called a kid. Key Information Document."),
    L("anatomy", "Three pages, maximum. What the product is. How risky it is, on a scale from one to seven. What it costs. "
                 "And what could happen to your money."),
    L("compare", "The idea is simple: every product explained the same way, so you can compare them."),
    L("everywhere", "And it applies everywhere in the European Union, from France to Germany to Spain."),
    L("nokid", "Most American funds simply don't make this document. Europe is a small market for them, "
               "and the template clashes with US rules.",
      "Most American funds simply don't make this document. Europe is a small market for them, "
      "and the template clashes with U.S. rules."),
    L("nosale", "No KID, no sale. So your broker isn't being difficult. It's following the law.",
      "No kid, no sale. So your broker isn't being difficult. It's following the law."),
    L("brokers", "And it's not just one broker. Trade Republic, Degiro, Interactive Brokers: for regular clients, they all block it."),
    L("ch3", "Part three. Is there a loophole?"),
    L("pro", "Technically, yes. If you're classified as a professional client, you can buy US funds.",
      "Technically, yes. If you're classified as a professional client, you can buy U.S. funds."),
    L("criteria", "But you need two out of three: a portfolio above €500,000, about ten large trades per quarter, "
                  "for a whole year, or a year working in finance.",
      "But you need two out of three: a portfolio above five hundred thousand euros, about ten large trades per quarter, "
      "for a whole year, or a year working in finance."),
    L("notforus", "And you give up some of your protections. For most of us, that's not the way. There's a much simpler one."),
    L("ch4", "Part four. The European twin."),
    L("ucits", "Europe has its own fund rules. They're called UCITS, and they've existed since 1985.",
      "Europe has its own fund rules. They're called you-sits, and they've existed since nineteen eighty-five."),
    L("twin", "Many fund companies, including Vanguard itself, make S&P 500 ETFs under those rules. "
              "Same index, same companies, with a KID. So you're allowed to buy them.",
      "Many fund companies, including Vanguard itself, make S and P five hundred E T Fs under those rules. "
      "Same index, same companies, with a kid. So you're allowed to buy them."),
    L("tickers", "Don't be confused by the names. One fund can have several tickers, depending on the stock exchange. "
                 "CSPX in London, SXR8 in Germany: same fund, different name tag.",
      "Don't be confused by the names. One fund can have several tickers, depending on the stock exchange. "
      "C S P X in London, S X R 8 in Germany: same fund, different name tag."),
    L("ireland", "Most of them are based in Ireland. And that's not random."),
    L("hubs", "Ireland and Luxembourg are Europe's two big fund hubs. But for American stocks, Ireland has an edge."),
    L("tax30", "When an American company pays a dividend to a fund outside the US, the US keeps part of it as tax. Usually 30%.",
      "When an American company pays a dividend to a fund outside the U.S., the U.S. keeps part of it as tax. Usually thirty percent."),
    L("tax15", "But Ireland signed a tax treaty with the US. For an Irish fund, it's only 15%. "
               "That's money that stays invested for you.",
      "But Ireland signed a tax treaty with the U.S. For an Irish fund, it's only fifteen percent. "
      "That's money that stays invested for you."),
    L("estate", "And there's a bonus. If you're not American and you die holding US funds, the US can tax your estate "
                "above $60,000, depending on your country. Irish funds generally avoid that.",
      "And there's a bonus. If you're not American and you die holding U.S. funds, the U.S. can tax your estate "
      "above sixty thousand dollars, depending on your country. Irish funds generally avoid that."),
    L("domicile", "So, the twin of VOO is an S&P 500 UCITS ETF, usually domiciled in Ireland. "
                  "Domiciled just means where the fund is legally based.",
      "So, the twin of V O O is an S and P five hundred you-sits E T F, usually domiciled in Ireland. "
      "Domiciled just means where the fund is legally based."),
    L("ch5", "Part five. What does it cost you?"),
    L("fees", "The big ones, from iShares and Vanguard, charge 0.07% a year. Some are around 0.05%.",
      "The big ones, from eye-shares and Vanguard, charge zero point zero seven percent a year. Some are around zero point zero five."),
    L("four", "Compared to VOO, that's a difference of about €4 a year on €10,000. About the price of a coffee.",
      "Compared to V O O, that's a difference of about four euros a year on ten thousand euros. About the price of a coffee."),
    L("nobill", "And you never get a bill. The fee comes out of the fund, a tiny bit every day. It's already in the price."),
    L("bank", "For comparison, many funds sold by banks charge more than 1% a year. That's where the real money goes.",
      "For comparison, many funds sold by banks charge more than one percent a year. That's where the real money goes."),
    L("mistakes", "Now, three things beginners often get wrong."),
    L("currency", "One. Buying it in euros doesn't remove the dollar. The companies are American, "
                  "so the value still moves with the dollar. Only funds marked hedged try to cancel that."),
    L("price", "Two. The price of one share doesn't matter. A share at €500? Not more expensive than one at €50. "
               "What matters is the fee, and what's inside.",
      "Two. The price of one share doesn't matter. A share at five hundred euros? Not more expensive than one at fifty euros. "
      "What matters is the fee, and what's inside."),
    L("accdist", "Three. You'll see two versions: accumulating and distributing. "
                 "Accumulating reinvests the dividends for you. Distributing pays them into your account."),
    L("depends", "Which one is better depends on where you live and how you're taxed. That's for the next video."),
    L("checklist", "So, here's the checklist. Search for an S&P 500 UCITS ETF. Check the yearly fee. "
                   "Check that it's based in Ireland. And pick accumulating or distributing.",
      "So, here's the checklist. Search for an S and P five hundred you-sits E T F. Check the yearly fee. "
      "Check that it's based in Ireland. And pick accumulating or distributing."),
    L("risk", "One last thing. The S&P 500 is only American companies, and it can drop hard. In 2022, it lost almost 20%.",
      "One last thing. The S and P five hundred is only American companies, and it can drop hard. "
      "In twenty twenty-two, it lost almost twenty percent."),
    L("past", "Over the long run, it has gone up. But the past guarantees nothing. Only invest money you won't need for years."),
    L("plan", "And remember: this video is about one index. It's a starting point, not a full plan."),
    L("subscribe", "If this saved you a headache, subscribing really helps. It's free, and it tells me to make more of these."),
    L("end", "Next video: accumulating or distributing, which one should you pick? This is not financial advice. See you there."),
]
# how long each displayed token takes to say (keeps the karaoke in sync when the caption shows a figure)
SAY = {"VOO": "vee oh oh", "PRIIPs": "preeps", "2018": "twenty eighteen", "US": "you ess", "S&P": "S and P",
       "500": "five hundred", "UCITS": "you sits", "ETF": "ee tee eff", "ETFs": "ee tee effs", "KID": "kid",
       "0.07%": "zero point zero seven percent", "0.03%": "zero point zero three percent", "0.05%": "zero point zero five",
       "$10,000": "ten thousand dollars", "$3": "three dollars", "€500,000": "five hundred thousand euros", "1985": "nineteen eighty five",
       "30%": "thirty percent", "15%": "fifteen percent", "€4": "four euros", "€10,000": "ten thousand euros",
       "2022": "twenty twenty two", "20%": "twenty percent", "iShares": "eye shares", "2010": "twenty ten",
       "$60,000": "sixty thousand dollars", "CSPX": "see ess pee ex", "SXR8": "ess ex ar eight", "1%": "one percent",
       "€500": "five hundred euros", "€50": "fifty euros"}
TRANS = []
LEAD, GAP, TAIL = 0.4, 0.8, 2.6
SHORT_LAST = 2


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
    while cut > 1 and not cl(words[cut - 1]).endswith(",") and cl(words[cut - 1]).lower().strip(",") in WEAK:
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
    hits = [a for w, a, b in WT[i] if cl(w).lower().strip("\"“”").rstrip(".,:?!;") == word.lower()]
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


# --------------------------------------------------------------------------- dark style: palette, typing, small helpers
BG, FG, DIM, FAINT, ERR = (7, 7, 9), (236, 236, 236), (118, 118, 126), (58, 58, 66), (232, 58, 64)
MONO, MONOB = "../../truetype/dejavu/DejaVuSansMono.ttf", "../../truetype/dejavu/DejaVuSansMono-Bold.ttf"
BLACK, LIGHT = "InterDisplay-Black.otf", "Inter-Light.otf"
ticks = []                              # typewriter key times (global seconds)
_tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))


_SD = {"dur": None}                    # duration of the scene being built or drawn (set by the render loop)


def typed(txt, t, t0, cps=28, gt0=None):
    """Prefix of txt typed since t0; with gt0 (scene start), registers one key tick per character instead.
    Types faster when needed so the line is complete before the scene cuts."""
    if _SD["dur"] is not None:
        cps = max(cps, len(txt) / max(0.3, _SD["dur"] - 0.4 - t0))
    if gt0 is not None:
        ticks.extend(gt0 + t0 + k / cps for k in range(len(txt)) if txt[k] != " ")
    return "" if t < t0 else txt[: int((t - t0) * cps) + 1]


def caret(d, x, y, t, size):
    if t % 0.9 < 0.5:
        d.rectangle([x + 4, y - size * 0.8, x + 4 + size * 0.55, y + size * 0.15], fill=FG)


def mid_text(d, y, full, shown, font, fill, x=W / 2):
    """Typed text that stays centered (on x) on its full length."""
    d.text((x - d.textlength(full, font=font) / 2, y), shown, font=font, fill=fill, anchor="ls")


def letters(d, xy, txt, font, t, t0, step=0.04, fade=0.25, fill=FG):
    """Centered text whose letters fade in one after the other."""
    x = xy[0] - d.textlength(txt, font=font) / 2
    for k, ch in enumerate(txt):
        a = prog(t, t0 + k * step, t0 + k * step + fade)
        if a > 0:
            d.text((x, xy[1]), ch, font=font, fill=fill + (int(255 * a),), anchor="ls")
        x += d.textlength(ch, font=font)


def star_pts(cx, cy, r, rot=-90):
    return [(cx + (r if k % 2 == 0 else r * 0.42) * math.cos(math.radians(rot + 36 * k)),
             cy + (r if k % 2 == 0 else r * 0.42) * math.sin(math.radians(rot + 36 * k))) for k in range(10)]


def black():
    return Image.new("RGB", (W, H), BG)


def trig(i, spec):
    """Scene-local time of a cue: seconds, a word, or (word, nth[, offset])."""
    if isinstance(spec, (int, float)):
        return float(spec)
    if isinstance(spec, tuple):
        return lw(i, spec[0], spec[1]) + (spec[2] if len(spec) > 2 else 0)
    return lw(i, spec)


def cam(im, t, dur, cy=500, z=0.035):
    return camera(im, 1 + z * t / dur, W / 2, cy)


def is_mono(font):
    return font in (MONO, MONOB)


def dot_grid(cols, rows, sp, r, col):
    g = Cv(None, size=(cols * sp, rows * sp))
    for rr in range(rows):
        for c in range(cols):
            x, y = c * sp + sp / 2, rr * sp + sp / 2
            g.ellipse([x - r, y - r, x + r, y + r], col)
    return g.out()


def reveal_rows(im, grid, cx, cy, u):
    hh = int(grid.height * ease_out(u))
    if hh > 0:
        comp(im, grid.crop((0, 0, grid.width, hh)), cx - grid.width / 2, cy - grid.height / 2)


# --------------------------------------------------------------------------- generic scenes
def term(rows, size=44, cps=28, cy=480):
    """Terminal block: each (text, cue, colour) row is typed when its cue is said."""
    def build(dur, i):
        fm = F(MONO, size)
        R = [(txt, trig(i, cue), col) for txt, cue, col in rows]
        for txt, t0, _ in R:
            typed(txt, 0, t0, cps, starts[i])
        x0 = (W - max(_tmp.textlength(txt, font=fm) for txt, _, _ in R)) / 2
        lh = size * 1.9
        y0 = cy - (len(R) - 1) * lh / 2

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            last = None
            for k, (txt, t0, col) in enumerate(R):
                s = typed(txt, t, t0, cps)
                if s:
                    d.text((x0, y0 + k * lh), s, font=fm, fill=col, anchor="ls")
                    last = (s, y0 + k * lh)
            if last:
                caret(d, x0 + d.textlength(last[0], font=fm), last[1], t, size)
            return cam(im, t, dur, cy)
        return frame, []
    return build


def bigs(items, events=()):
    """Free layout: (text, cue, font, size, colour, x, y) items; mono text is typed, the rest fades in."""
    def build(dur, i):
        R = []
        for txt, cue, font, size, col, x, y in items:
            t0 = trig(i, cue)
            if is_mono(font):
                typed(txt, 0, t0, 30, starts[i])
            R.append((txt, t0, F(font, size), font, col, x, y))

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            for txt, t0, f, font, col, x, y in R:
                if t < t0:
                    continue
                if is_mono(font):
                    mid_text(d, y, txt, typed(txt, t, t0, 30), f, col, x)
                else:
                    a = prog(t, t0, t0 + 0.15)
                    d.text((x, y + 12 * (1 - a)), txt, font=f, fill=col + (int(255 * a),), anchor="ms")
            return cam(im, t, dur)
        return frame, [(n, trig(i, cue), g) for n, cue, g in events]
    return build


def chapter(n, title):
    def build(dur, i):
        fk, ft = F(MONO, 30), F(LIGHT, 104)
        lab = f"PART {n:02d}"
        typed(lab, 0, 0.1, 20, starts[i])

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            mid_text(d, 430, lab, typed(lab, t, 0.1, 20), fk, DIM)
            letters(d, (W / 2, 580), title, ft, t, 0.35, step=0.035)
            w = 520 * ease_out(prog(t, 0.3, 1.0))
            d.line([(W / 2 - w / 2, 640), (W / 2 + w / 2, 640)], fill=FG + (110,), width=2)
            return cam(im, t, dur, 450, 0.03)
        return frame, [("boom", 0.0, 0.45)]
    return build


def checklist(head_cue, items, head="> checklist"):
    def build(dur, i):
        fm = F(MONO, 42)
        th = trig(i, head_cue)
        typed(head, 0, th, 30, starts[i])
        R = [(txt, trig(i, cue)) for txt, cue in items]
        for k, (txt, _) in enumerate(R):
            typed("[ ] " + txt, 0, th + 0.4 + k * 0.4, 60, starts[i])
        x0 = (W - max(_tmp.textlength("[ ] " + txt, font=fm) for txt, _ in R)) / 2

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            d.text((x0, 330), typed(head, t, th, 30), font=fm, fill=FG, anchor="ls")
            for k, (txt, t0) in enumerate(R):
                s = typed("[ ] " + txt, t, th + 0.4 + k * 0.4, 60)
                if not s:
                    continue
                done = t >= t0
                col = FG if done else DIM
                d.text((x0, 460 + k * 84), ("[x] " if done else "[ ] ")[:len(s)], font=fm, fill=col, anchor="ls")
                d.text((x0 + d.textlength("[ ] ", font=fm), 460 + k * 84), s[4:], font=fm, fill=col, anchor="ls")
            return cam(im, t, dur, 520, 0.03)
        return frame, [("boom", t0, 0.3) for _, t0 in R]
    return build


# --------------------------------------------------------------------------- custom scenes
def sc_wall(dur, i):
    t_v = lw(i, "voo")
    cols, rows, bw, bh, gap = 11, 7, 140, 80, 22
    gx0, gy0 = (W - (cols * bw + (cols - 1) * gap)) / 2, (H - (rows * bh + (rows - 1) * gap)) / 2 - 30
    tile = Cv(None, size=(bw, bh))
    tile.rect([2, 2, bw - 2, bh - 2], None, r=8, outline=DIM, width=2)
    tile.text((bw / 2, bh / 2 + 6), "buy VOO.", MONO, 17, FG, anchor="ms")
    tile = tile.out()
    order = np.random.default_rng(7).permutation(cols * rows)
    appear = {int(c): 0.3 + (t_v - 0.6) * (r / (cols * rows)) ** 1.8 for r, c in enumerate(order)}
    voo = Cv(None, size=(900, 360))
    voo.text((450, 290), "VOO", BLACK, 300, FG, anchor="ms")
    voo = voo.out()

    def frame(t):
        im = black()
        wall = 1 - 0.88 * prog(t, t_v, t_v + 0.25)
        for c, ap in appear.items():
            if t >= ap:
                comp(im, tile, gx0 + (c % cols) * (bw + gap), gy0 + (c // cols) * (bh + gap), prog(t, ap, ap + 0.12) * wall)
        if t >= t_v:
            sprite_at(im, voo, W / 2, 470, 1.06 - 0.06 * ease_out(prog(t, t_v, t_v + 0.4)), prog(t, t_v, t_v + 0.08))
        z = 1.15 - 0.15 * ease_out(prog(t, 0, t_v)) + 0.04 * prog(t, t_v, dur)
        return camera(im, z, W / 2, 470 if t >= t_v else H / 2)
    return frame, [("boom", t_v, 0.9)]


def sc_search(dur, i):
    to, tt, tn, tna = (lw(i, w) for w in ("open", "type", "nothing", "not"))
    head, err = "> broker --region EU", "ERROR: NOT AVAILABLE IN YOUR REGION"
    typed(head, 0, to, 26, starts[i])
    typed("VOO", 0, tt, 8, starts[i])
    typed(err, 0, tna, 50, starts[i])
    fm, fb = F(MONO, 34), F(MONO, 64)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        mid_text(d, 330, head, typed(head, t, to, 26), fm, DIM)
        a = prog(t, to + 0.3, to + 0.6)
        if a > 0:
            d.rounded_rectangle([560, 420, 1360, 540], 14, outline=FG + (int(255 * a),), width=3)
            d.ellipse([600, 462, 634, 496], outline=DIM + (int(255 * a),), width=4)
            d.line([(629, 491), (646, 508)], fill=DIM + (int(255 * a),), width=4)
            s = typed("VOO", t, tt, 8)
            d.text((680, 503), s, font=fb, fill=FG, anchor="ls")
            if t < tna:
                caret(d, 680 + d.textlength(s, font=fb), 503, t, 64)
        if t >= tna:
            mid_text(d, 640, err, typed(err, t, tna, 50), fm, ERR)
        return cam(im, t, dur)
    return frame, [("glitch", tn, 0.8), ("boom", tna, 0.7)]


def sc_basket(dur, i):
    te, tb, tc, tm = (lw(i, w) for w in ("etf", "basket", "click", "many"))
    names = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "AVGO", "TSLA", "JPM", "LLY",
             "V", "XOM", "WMT", "MA", "COST", "HD", "PG", "NFLX", "JNJ", "KO"]
    l1, l2 = "VOO = ETF", "1 click"
    typed(l1, 0, te, 26, starts[i])
    typed(l2, 0, tc, 26, starts[i])
    fm, ft = F(MONO, 52), F(MONOB, 26)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        mid_text(d, 230, l1, typed(l1, t, te, 26), fm, FG)
        mid_text(d, 310, l2, typed(l2, t, tc, 26), F(MONO, 36), DIM)
        a = prog(t, tb, tb + 0.4)
        if a > 0:
            d.line([(660, 430), (700, 790), (1220, 790), (1260, 430)], fill=FG + (int(255 * a),), width=4, joint="curve")
        for k, nm in enumerate(names):
            t0 = tm + k * 0.07
            u = prog(t, t0, t0 + 0.35)
            if u <= 0:
                continue
            x, y = 760 + (k % 5) * 100, 750 - (k // 5) * 58
            yy = 380 + (y - 380) * ease_out(u)
            d.rounded_rectangle([x - 44, yy - 22, x + 44, yy + 22], 6, outline=DIM, width=2)
            d.text((x, yy + 9), nm, font=ft, fill=FG, anchor="ms")
        return cam(im, t, dur, 520)
    return frame, [("tick", tm + k * 0.07 + 0.3, 0.3) for k in range(20)]


def sc_sp500(dur, i):
    ts, t500 = lw(i, "s&p"), lw(i, "500", 1)
    named = [("Apple", lw(i, "apple")), ("Microsoft", lw(i, "microsoft")), ("Nvidia", lw(i, "nvidia")), ("Amazon", lw(i, "amazon"))]
    th = lw(i, "hundreds")
    g = dot_grid(25, 20, 18, 4, (110, 110, 118))
    fb, fm = F(BLACK, 110), F(MONO, 34)
    more = "+ hundreds more"
    for nm, t0 in named:
        typed(nm, 0, t0, 30, starts[i])
    typed(more, 0, th, 30, starts[i])

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        a = prog(t, ts, ts + 0.15)
        if a > 0:
            d.text((W / 2, 220), "S&P 500", font=fb, fill=FG + (int(255 * a),), anchor="ms")
        reveal_rows(im, g, W / 2, 470, prog(t, t500, t500 + 1.0))
        x = W / 2 - _tmp.textlength("  ·  ".join(n for n, _ in named), font=fm) / 2
        for k, (nm, t0) in enumerate(named):
            if t >= t0:
                cx, cy = W / 2 - 225 + 9 + k * 18, 470 - 180 + 9
                d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=FG)
                d.text((x, 730), typed(nm, t, t0, 30), font=fm, fill=FG, anchor="ls")
            x += _tmp.textlength(nm + "  ·  ", font=fm)
        mid_text(d, 790, more, typed(more, t, th, 30), fm, DIM)
        return cam(im, t, dur, 480)
    return frame, [("boom", ts, 0.4)] + [("tick", t500 + k * 0.08, 0.3) for k in range(12)]


def sc_cheap(dur, i):
    tv, tp, t10 = lw(i, "vanguard"), lw(i, "0.03%"), lw(i, "$10,000")
    l1, l3 = "fund manager: Vanguard", "$10,000 → $3 / year"
    typed(l1, 0, tv, 30, starts[i])
    typed(l3, 0, t10, 22, starts[i])
    fb, fm, fl = F(BLACK, 220), F(MONO, 36), F(MONO, 50)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        mid_text(d, 250, l1, typed(l1, t, tv, 30), fm, DIM)
        if t >= tp:
            v = 0.03 * ease_out(prog(t, tp, tp + 0.5))
            d.text((W / 2, 560), f"{v:.2f}%", font=fb, fill=FG + (int(255 * prog(t, tp, tp + 0.1)),), anchor="ms")
            d.text((W / 2, 640), "per year", font=fm, fill=DIM + (int(255 * prog(t, tp + 0.3, tp + 0.5)),), anchor="ms")
        mid_text(d, 780, l3, typed(l3, t, t10, 22), fl, FG)
        return cam(im, t, dur)
    return frame, [("boom", tp, 0.6)]


def sc_index(dur, i):
    ti, tn, tw, tbad = lw(i, "index"), lw(i, "nobody"), lw(i, "whole"), lw(i, "bad")
    dim_g, lit_g = dot_grid(25, 20, 18, 4, (90, 90, 98)), dot_grid(25, 20, 18, 4, FG)
    reds = np.random.default_rng(3).choice(500, 45, replace=False)
    l1, l2 = "index fund", "no stock picking"
    typed(l1, 0, ti, 26, starts[i])
    typed(l2, 0, tn, 30, starts[i])
    fm = F(MONO, 40)

    def frame(t):
        im = black()
        reveal_rows(im, dim_g, W / 2, 470, prog(t, ti, ti + 0.8))
        if t >= tw:
            comp(im, lit_g, W / 2 - lit_g.width / 2, 470 - lit_g.height / 2, prog(t, tw, tw + 0.4))
        d = ImageDraw.Draw(im, "RGBA")
        if t >= tbad:
            for k in reds[: int(45 * prog(t, tbad, tbad + 0.4))]:
                cx, cy = W / 2 - 225 + 9 + (k % 25) * 18, 470 - 180 + 9 + (k // 25) * 18
                d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=ERR)
        mid_text(d, 230, l1, typed(l1, t, ti, 26), fm, FG)
        mid_text(d, 740, l2, typed(l2, t, tn, 30), fm, DIM)
        return cam(im, t, dur, 480)
    return frame, []


def sc_priips(dur, i):
    t18, tu, tp, tpr = lw(i, "2018"), lw(i, "union"), lw(i, "priips"), lw(i, "protect")
    st = Cv(None, size=(70, 70))
    st.poly(star_pts(35, 37, 28), (205, 205, 212))
    st = st.out()
    l1, l2 = "since 2018", "goal: protect everyday investors"
    typed(l1, 0, t18, 26, starts[i])
    typed(l2, 0, tpr, 30, starts[i])
    fb, fm = F(BLACK, 170), F(MONO, 36)

    def frame(t):
        im = black()
        for j in range(12):
            a = math.radians(-90 + 30 * j + 6 * t)
            sprite_at(im, st, W / 2 + 280 * math.cos(a), 470 + 280 * math.sin(a), ease_back(prog(t, tu + j * 0.04, tu + 0.25 + j * 0.04)),
                      1 - 0.5 * prog(t, tp, tp + 0.3))
        d = ImageDraw.Draw(im, "RGBA")
        mid_text(d, 140, l1, typed(l1, t, t18, 26), fm, DIM)
        if t >= tp:
            d.text((W / 2, 530), "PRIIPs", font=fb, fill=FG + (int(255 * prog(t, tp, tp + 0.1)),), anchor="ms")
        mid_text(d, 830, l2, typed(l2, t, tpr, 30), fm, FG)
        return cam(im, t, dur, 470)
    return frame, [("boom", tp, 0.9)] + [("tick", tu + j * 0.04, 0.3) for j in range(12)]


def doc_outline(d, cx, cy, a=1.0, dashed=False, lit=None, w=300, h=380):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    if dashed:
        col = DIM + (int(255 * a),)
        for x in np.arange(x0, x1, 28):
            for y in (y0, y1):
                d.line([(x, y), (min(x + 14, x1), y)], fill=col, width=3)
        for y in np.arange(y0, y1, 28):
            for x in (x0, x1):
                d.line([(x, y), (x, min(y + 14, y1))], fill=col, width=3)
        return
    col = FG + (int(255 * a),)
    d.line([(x0, y0), (x1 - 50, y0), (x1, y0 + 50), (x1, y1), (x0, y1), (x0, y0)], fill=col, width=3)
    d.line([(x1 - 50, y0), (x1 - 50, y0 + 50), (x1, y0 + 50)], fill=col, width=3)
    for k in range(4):
        on = lit is None or k in lit
        c = (FG if on else FAINT) + (int(255 * a),)
        y = y0 + 90 + k * 68
        d.line([(x0 + 36, y), (x0 + 36 + (w - 72) * 0.55, y)], fill=c, width=8)
        d.line([(x0 + 36, y + 22), (x0 + 36 + (w - 72) * 0.85, y + 22)], fill=c, width=4)


def sc_kid(dur, i):
    tp, td, tk, tkey = lw(i, "product"), lw(i, "document"), lw(i, "kid"), lw(i, "key")
    rows = [("> sold_to = retail", tp, DIM), ("required: short document", td, FG), ("name: KID", tk, FG),
            ("= Key Information Document", tkey, FG)]
    for txt, t0, _ in rows:
        typed(txt, 0, t0, 30, starts[i])
    fm = F(MONO, 38)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        if t >= td:
            doc_outline(d, 600, 480, prog(t, td, td + 0.3))
        for k, (txt, t0, col) in enumerate(rows):
            d.text((860, 380 + k * 70), typed(txt, t, t0, 30), font=fm, fill=col, anchor="ls")
        return cam(im, t, dur)
    return frame, [("boom", tk, 0.4)]


def sc_anatomy(dur, i):
    t3, tw, tr, ts, tc, th = lw(i, "three"), lw(i, "what", 0), lw(i, "risky"), lw(i, "scale"), lw(i, "costs"), lw(i, "happen")
    rows = [("01  what it is", tw), ("02  how risky", tr), ("03  what it costs", tc), ("04  what could happen", th)]
    head = "max 3 pages"
    typed(head, 0, t3, 26, starts[i])
    for txt, t0 in rows:
        typed(txt, 0, t0, 30, starts[i])
    fm, fh = F(MONO, 40), F(MONO, 34)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        lit = [k for k, (_, t0) in enumerate(rows) if t >= t0]
        doc_outline(d, 520, 480, prog(t, 0.05, 0.35), lit=lit[-1:] if lit else [])
        d.text((800, 290), typed(head, t, t3, 26), font=fh, fill=DIM, anchor="ls")
        for k, (txt, t0) in enumerate(rows):
            d.text((800, 390 + k * 86), typed(txt, t, t0, 30), font=fm, fill=FG, anchor="ls")
        if t >= ts:
            for j in range(7):
                on = prog(t, ts + j * 0.1, ts + j * 0.1 + 0.1)
                x = 1180 + j * 46
                d.rectangle([x, 446, x + 36, 482], outline=DIM, width=2, fill=FG + (int(255 * on),) if on > 0 else None)
                d.text((x + 18, 510), str(j + 1), font=F(MONO, 22), fill=DIM, anchor="ms")
        return cam(im, t, dur)
    return frame, [("tick", ts + j * 0.1, 0.4) for j in range(7)]


def sc_compare(dur, i):
    te, ts, tc = lw(i, "every"), lw(i, "same"), lw(i, "compare")
    fl = F(MONO, 28)
    last = "same format → easy to compare"
    typed(last, 0, tc, 30, starts[i])

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        for k, cx in enumerate((560, 960, 1360)):
            t0 = te + k * 0.15
            if t >= t0:
                lit = None if t >= ts else []
                doc_outline(d, cx, 450, prog(t, t0, t0 + 0.3), lit=lit, w=260, h=330)
                d.text((cx, 670), f"fund {'ABC'[k]}", font=fl, fill=DIM, anchor="ms")
        mid_text(d, 780, last, typed(last, t, tc, 30), F(MONO, 38), FG)
        return cam(im, t, dur, 480)
    return frame, [("tick", te + k * 0.15, 0.4) for k in range(3)]


EU27 = ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU",
        "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"]


def sc_everywhere(dur, i):
    te = lw(i, "everywhere")
    hi = {"FR": lw(i, "france"), "DE": lw(i, "germany"), "ES": lw(i, "spain")}
    head = "> scope: European Union (27 countries)"
    typed(head, 0, 0.1, 34, starts[i])
    fm, fc = F(MONO, 34), F(MONOB, 48)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        mid_text(d, 260, head, typed(head, t, 0.1, 34), fm, DIM)
        for k, c in enumerate(EU27):
            a = prog(t, te + k * 0.03, te + k * 0.03 + 0.15)
            if a <= 0:
                continue
            x, y = 960 + (k % 9 - 4) * 150, 440 + (k // 9) * 110
            on = c in hi and t >= hi[c]
            d.text((x, y), c, font=fc, fill=(FG if on else (96, 96, 104)) + (int(255 * a),), anchor="ms")
            if on:
                w = 60 * ease_out(prog(t, hi[c], hi[c] + 0.2))
                d.line([(x - 30, y + 14), (x - 30 + w, y + 14)], fill=FG, width=3)
        return cam(im, t, dur, 480)
    return frame, [("tick", t0, 0.5) for t0 in hi.values()]


def sc_nokid(dur, i):
    tm, tx, ts, tc = lw(i, "most"), lw(i, "don't"), lw(i, "small"), lw(i, "clashes")
    lab, lab_x = "US_FUND/KID.pdf", "404: FILE NOT FOUND"
    rows = [("why?", ts - 0.4, DIM), ("1. EU = small market for them", ts, FG), ("2. EU template ≠ US rules", tc, FG)]
    for txt, t0, cps in ((lab, tm, 30), (lab_x, tx, 50)):
        typed(txt, 0, t0, cps, starts[i])
    for txt, t0, _ in rows:
        typed(txt, 0, t0, 30, starts[i])
    fl, fm = F(MONO, 28), F(MONO, 36)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        doc_outline(d, 560, 450, prog(t, tm, tm + 0.3), dashed=True)
        txt, col, t0, cps = (lab_x, ERR, tx, 50) if t >= tx else (lab, FG, tm, 30)
        mid_text(d, 700, txt, typed(txt, t, t0, cps), fl, col, 560)
        for k, (txt, t0, col) in enumerate(rows):
            d.text((880, 400 + k * 80), typed(txt, t, t0, 30), font=fm, fill=col, anchor="ls")
        return cam(im, t, dur, 480)
    return frame, [("glitch", tx, 0.6), ("boom", tx, 0.6)]


def sc_nosale(dur, i):
    tn, ts, tl = lw(i, "no", 0), lw(i, "sale"), lw(i, "law")
    last = "> broker.status = following_the_law"
    typed(last, 0, tl, 34, starts[i])
    fb = F(BLACK, 160)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        if t >= tn:
            d.text((W / 2, 430), "NO KID", font=fb, fill=FG + (int(255 * prog(t, tn, tn + 0.1)),), anchor="ms")
        if t >= ts:
            d.text((W / 2, 630), "= NO SALE", font=fb, fill=ERR + (int(255 * prog(t, ts, ts + 0.1)),), anchor="ms")
        mid_text(d, 800, last, typed(last, t, tl, 34), F(MONO, 38), DIM)
        return cam(im, t, dur, 520)
    return frame, [("boom", tn, 0.7), ("glitch", ts, 0.5)]


def sc_tax(second):
    def build(dur, i):
        fm, fs = F(MONO, 32), F(MONO, 30)
        X0, L = 460, 1000
        if not second:
            cues = dict(lab=lw(i, "outside"), bar=lw(i, "dividend"), cut=lw(i, "30%"), keeps=lw(i, "keeps"))
            rows = [("fund outside the US", 460, 0.30, cues)]
            top = ("$100 dividend", lw(i, "dividend"))
        else:
            cues = dict(lab=lw(i, "irish"), bar=lw(i, "irish"), cut=lw(i, "15%"), keeps=lw(i, "15%"))
            rows = [("fund outside the US", 330, 0.30, dict(lab=0, bar=0, cut=0, keeps=0)), ("Irish fund", 580, 0.15, cues)]
            top = ("US–Ireland tax treaty", lw(i, "treaty"))
        stays = lw(i, "stays") if second else None
        for lab, _, _, c in rows:
            if c["lab"] > 0:
                typed(lab, 0, c["lab"], 30, starts[i])
        typed(top[0], 0, top[1], 30, starts[i])

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            mid_text(d, 200, top[0], typed(top[0], t, top[1], 30), F(MONO, 36), DIM)
            for lab, y, rate, c in rows:
                d.text((X0, y - 24), lab if c["lab"] == 0 else typed(lab, t, c["lab"], 30), font=fm, fill=FG, anchor="ls")
                g = ease_out(prog(t, c["bar"], c["bar"] + 0.5))
                if g > 0:
                    d.rectangle([X0, y, X0 + L * g, y + 60], fill=FG)
                u = ease_out(prog(t, c["cut"], c["cut"] + 0.4))
                if u > 0:
                    d.rectangle([X0 + L * (1 - rate * u), y, X0 + L, y + 60], fill=ERR)
                    d.text((X0 + L + 24, y + 46), f"−${int(round(100 * rate))} US tax", font=fs, fill=ERR, anchor="ls")
            if stays is not None and t >= stays:
                d.text((X0, 760), typed("$85 stays invested for you", t, stays, 30), font=F(MONO, 40), fill=FG, anchor="ls")
            return cam(im, t, dur, 480)
        if second:
            typed("$85 stays invested for you", 0, stays, 30, starts[i])
        return frame, [("boom", rows[-1][3]["cut"], 0.6)]
    return build


def sc_four(dur, i):
    tc, t4, tco = lw(i, "compared"), lw(i, "€4"), lw(i, "coffee")
    eq, cof = "€10,000 × (0.07% − 0.03%) =", "≈ the price of 1 coffee"
    typed(eq, 0, tc, 30, starts[i])
    typed(cof, 0, tco, 30, starts[i])
    fe, f4, fy = F(MONO, 40), F(BLACK, 280), F(MONO, 48)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        mid_text(d, 330, eq, typed(eq, t, tc, 30), fe, DIM)
        if t >= t4:
            txt = f"€{max(1, round(4 * ease_out(prog(t, t4, t4 + 0.5))))}"
            w1, w2 = d.textlength(txt, font=f4), d.textlength(" / year", font=fy)
            x = W / 2 - (w1 + w2) / 2
            d.text((x, 650), txt, font=f4, fill=FG, anchor="ls")
            d.text((x + w1, 650), " / year", font=fy, fill=DIM, anchor="ls")
        mid_text(d, 790, cof, typed(cof, t, tco, 30), F(MONO, 38), FG)
        return cam(im, t, dur, 520, 0.05)
    return frame, [("boom", t4, 1.0)]


def sc_bars(rows, note=None):
    """Horizontal bars: (label, value text, fraction, colour, cue)."""
    def build(dur, i):
        fm = F(MONO, 32)
        R = [(lab, val, fr, col, trig(i, cue)) for lab, val, fr, col, cue in rows]
        for lab, _, _, _, t0 in R:
            typed(lab, 0, t0, 30, starts[i])
        nt = (note[0], trig(i, note[1]), note[2]) if note else None
        if nt:
            typed(nt[0], 0, nt[1], 30, starts[i])
        X0, L = 380, 1160

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            for k, (lab, val, fr, col, t0) in enumerate(R):
                y = 380 + k * 190
                d.text((X0, y - 24), typed(lab, t, t0, 30), font=fm, fill=FG, anchor="ls")
                g = ease_out(prog(t, t0, t0 + 0.6))
                if g > 0:
                    d.rectangle([X0, y, X0 + max(8, L * fr * g), y + 60], fill=col)
                    d.text((X0 + max(8, L * fr * g) + 24, y + 46), val, font=F(MONOB, 40), fill=col, anchor="ls")
            if nt:
                mid_text(d, 820, nt[0], typed(nt[0], t, nt[1], 30), F(MONO, 38), nt[2])
            return cam(im, t, dur, 480)
        return frame, [("boom", t0, 0.35) for *_, t0 in R]
    return build


def sc_currency(dur, i):
    te, td, ta, td2, th = lw(i, "euros"), lw(i, "dollar", 0), lw(i, "american"), lw(i, "dollar", 1), lw(i, "hedged")
    walk = np.cumsum(np.random.default_rng(5).normal(0, 1, 120))
    walk = (walk - walk.min()) / (walk.max() - walk.min())
    note = "only 'EUR hedged' versions try to cancel it"
    typed(note, 0, th, 34, starts[i])
    fb, fm = F(BLACK, 160), F(MONO, 32)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        for x, lab, big, t0 in ((600, "you pay in", "EUR", te), (1320, "you really own", "USD", td)):
            if t >= t0:
                a = int(255 * prog(t, t0, t0 + 0.15))
                d.text((x, 260), lab, font=fm, fill=DIM + (a,), anchor="ms")
                d.text((x, 420), big, font=fb, fill=FG + (a,), anchor="ms")
        u = prog(t, ta, td2 + 0.8)
        if u > 0:
            n = max(2, int(120 * u))
            pts = [(460 + k * 1000 / 119, 690 - 140 * walk[k]) for k in range(n)]
            d.line(pts, fill=FG, width=3)
            d.text((460, 740), "EUR / USD", font=F(MONO, 26), fill=DIM, anchor="ls")
        mid_text(d, 830, note, typed(note, t, th, 34), F(MONO, 36), FG)
        return cam(im, t, dur, 500)
    return frame, [("boom", td, 0.4)]


def sc_price(dur, i):
    tp, t5, t50, tf, ti = lw(i, "price"), lw(i, "€500"), lw(i, "€50"), lw(i, "fee"), lw(i, "inside")
    head, last = "share price ≠ cost", "→ check the fee, and what's inside"
    typed(head, 0, tp, 30, starts[i])
    typed(last, 0, ti, 34, starts[i])
    fb, fm = F(BLACK, 180), F(MONO, 34)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        mid_text(d, 250, head, typed(head, t, tp, 30), F(MONO, 40), FG)
        for x, txt, t0 in ((620, "€500", t5), (1300, "€50", t50)):
            if t >= t0:
                d.text((x, 500), txt, font=fb, fill=FG + (int(255 * prog(t, t0, t0 + 0.15)),), anchor="ms")
                d.text((x, 570), "per share", font=fm, fill=DIM, anchor="ms")
            if t >= tf:
                d.text((x, 650), "fee 0.07%", font=fm, fill=FG + (int(255 * prog(t, tf, tf + 0.2)),), anchor="ms")
        if t >= tf:
            d.text((W / 2, 650), "=", font=F(MONO, 60), fill=DIM, anchor="ms")
        mid_text(d, 800, last, typed(last, t, ti, 34), F(MONO, 38), DIM)
        return cam(im, t, dur)
    return frame, [("boom", t5, 0.4), ("boom", t50, 0.4)]


def sc_accdist(dur, i):
    ta, td, tr, tp = lw(i, "accumulating", 0), lw(i, "distributing", 0), lw(i, "reinvests"), lw(i, "pays")
    la, ld = "dividends → reinvested", "dividends → your account"
    typed(la, 0, tr, 30, starts[i])
    typed(ld, 0, tp, 30, starts[i])
    fb, fm = F(BLACK, 130), F(MONO, 32)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        for x, txt, t0 in ((600, "ACC", ta), (1320, "DIST", td)):
            if t >= t0:
                d.text((x, 320), txt, font=fb, fill=FG + (int(255 * prog(t, t0, t0 + 0.15)),), anchor="ms")
        u = ease_out(prog(t, tr, tr + 0.8))
        if u > 0:
            d.arc([510, 430, 690, 610], -60, -60 + 300 * u, fill=FG, width=6)
            if u > 0.95:
                ang = math.radians(240)
                hx, hy = 600 + 90 * math.cos(ang), 520 + 90 * math.sin(ang)
                d.polygon([(hx + 18, hy - 6), (hx - 10, hy - 18), (hx - 4, hy + 14)], fill=FG)
        v = ease_out(prog(t, tp, tp + 0.6))
        if v > 0:
            d.line([(1320, 420), (1320, 420 + 120 * v)], fill=FG, width=6)
            if v > 0.95:
                d.polygon([(1300, 535), (1340, 535), (1320, 565)], fill=FG)
                d.rounded_rectangle([1230, 575, 1410, 655], 10, outline=FG, width=4)
                d.line([(1370, 600), (1410, 600)], fill=FG, width=4)
        mid_text(d, 760, la, typed(la, t, tr, 30), fm, DIM, 600)
        mid_text(d, 760, ld, typed(ld, t, tp, 30), fm, DIM, 1320)
        return cam(im, t, dur, 480)
    return frame, [("boom", ta, 0.35), ("boom", td, 0.35)]


def sc_risk(dur, i):
    to, tdr, t22, t20 = lw(i, "only"), lw(i, "drop"), lw(i, "2022"), lw(i, "20%")
    path = [100, 94, 96, 88, 87, 80, 86, 91, 82, 78, 84, 81]
    head = "S&P 500 = 100% US companies"
    typed(head, 0, to, 30, starts[i])
    fm = F(MONO, 30)
    X0, X1, Y0, Y1 = 420, 1300, 330, 760

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        mid_text(d, 230, head, typed(head, t, to, 30), F(MONO, 40), FG)
        if t >= tdr:
            a = int(255 * prog(t, tdr, tdr + 0.3))
            d.line([(X0, Y0), (X0, Y1), (X1, Y1)], fill=FAINT + (a,), width=2)
            d.text((X0 + 10, Y0 + 10), "2022", font=fm, fill=DIM + (a,), anchor="lt")
            d.text((X1, Y1 + 40), "(simplified)", font=F(MONO, 22), fill=FAINT + (a,), anchor="rs")
        u = prog(t, t22, t22 + 1.4)
        if u > 0:
            n = len(path) - 1
            pts = [(X0 + 20 + k * (X1 - X0 - 40) / n, Y0 + 40 + (100 - v) / 25 * (Y1 - Y0 - 80)) for k, v in enumerate(path)]
            m = u * n
            k = int(m)
            show = pts[: k + 1] + ([(pts[k][0] + (pts[k + 1][0] - pts[k][0]) * (m - k), pts[k][1] + (pts[k + 1][1] - pts[k][1]) * (m - k))] if k < n else [])
            if len(show) > 1:
                d.line(show, fill=ERR, width=5, joint="curve")
        if t >= t20:
            d.text((1560, 600), "≈ −20%", font=F(BLACK, 120), fill=ERR + (int(255 * prog(t, t20, t20 + 0.15)),), anchor="ms")
        return cam(im, t, dur, 520)
    return frame, [("glitch", tdr, 0.4), ("boom", t20, 0.8)]


def sc_subscribe(dur, i):
    ts, tf = lw(i, "subscribing"), lw(i, "free")
    a, b = "[ subscribe ]", "[ subscribed ✓ ]"
    typed(a, 0, ts, 20, starts[i])
    fb = F(MONOB, 90)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        if t < tf:
            mid_text(d, 540, a, typed(a, t, ts, 20), fb, DIM)
        else:
            mid_text(d, 540, b, b, fb, FG)
            d.text((W / 2, 640), "it's free", font=F(MONO, 34), fill=DIM, anchor="ms")
        return cam(im, t, dur)
    return frame, [("boom", tf, 0.5)]


def sc_end(dur, i):
    tw, tn = lw(i, "which"), lw(i, "not")
    fk, ft, fs = F(MONO, 26), F(LIGHT, 84), F(MONO, 30)
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
        return cam(im, t, dur, 540, 0.02)
    return frame, [("boom", 0.0, 0.5)]


M, MB = MONO, MONOB
SCENES = {
    "wall": sc_wall, "search": sc_search,
    "reason": term([("> reason: exists", "reason", DIM), ("> workaround: simple", "simple", FG)]),
    "agenda": term([("01  what VOO actually is", "what", FG), ("02  why Europe blocks it", "why", FG),
                    ("03  what to buy instead", "version", FG), ("    (almost the same price)", "price", DIM)]),
    "ch1": chapter(1, "What is VOO?"), "basket": sc_basket, "sp500": sc_sp500, "cheap": sc_cheap,
    "since2010": bigs([("launched", 0.1, M, 36, DIM, W / 2, 330), ("2010", "2010", BLACK, 240, FG, W / 2, 580),
                       ("→ one of the world's biggest funds", "biggest", M, 40, FG, W / 2, 720)], [("boom", "2010", 0.5)]),
    "index": sc_index,
    "usa": term([("> every_us_video.says()", "every", DIM), ('  "just buy VOO"', ("every", 0, 0.9), FG),
                 ("> made_for", "made", DIM), ('  "Americans"', "americans", FG), ('  ≠ you', ("americans", 0, 0.7), ERR)]),
    "ch2": chapter(2, "Why Europe blocks it."), "priips": sc_priips, "kid": sc_kid, "anatomy": sc_anatomy,
    "compare": sc_compare, "everywhere": sc_everywhere, "nokid": sc_nokid, "nosale": sc_nosale,
    "brokers": term([("Trade Republic ........ blocked", "trade", FG), ("Degiro ................ blocked", "degiro", FG),
                     ("Interactive Brokers ... blocked", "interactive", FG), ("→ for regular clients: all of them", "all", ERR)]),
    "ch3": chapter(3, "Is there a loophole?"),
    "pro": term([("> client_type = retail", "technically", DIM), ("> client_type = professional", "professional", FG),
                 ("> US_funds = unlocked", "buy", FG)]),
    "criteria": term([("need 2 of 3:", "two", DIM), ("[ ] portfolio > €500,000", "portfolio", FG),
                      ("[ ] ~10 large trades per quarter, for 1 year", "trades", FG), ("[ ] 1 year working in finance", "finance", FG)]),
    "notforus": term([("- some investor protections", "protections", ERR), ("verdict: not for most beginners", "most", FG),
                      ("> there's a simpler way", "simpler", FG)]),
    "ch4": chapter(4, "The European twin."),
    "ucits": bigs([("EU fund rules", "rules", M, 40, DIM, W / 2, 300), ("UCITS", "ucits", BLACK, 220, FG, W / 2, 560),
                   ("since 1985", "1985", M, 40, FG, W / 2, 680)], [("boom", "ucits", 0.7)]),
    "twin": term([("> S&P 500 UCITS ETF", "s&p", FG), ("  index:     same", ("same", 0), FG), ("  companies: same", ("same", 1), FG),
                  ("  KID:       yes", "kid", FG), ("  you:       allowed ✓", "allowed", FG)]),
    "tickers": term([("1 fund, several tickers:", "tickers", DIM), ("CSPX   London    USD", "cspx", FG),
                     ("SXR8   Germany   EUR", "sxr8", FG), ("= same fund, different name tag", "same", FG)]),
    "ireland": bigs([("IRELAND", "ireland", BLACK, 190, FG, W / 2, 540), ("domicile = IE", ("ireland", 0, 0.5), M, 40, DIM, W / 2, 660),
                     ("(not random)", "random", M, 36, DIM, W / 2, 740)], [("boom", "ireland", 0.6)]),
    "hubs": bigs([("IE", ("ireland", 0), BLACK, 220, FG, 700, 520), ("Ireland", ("ireland", 0, 0.2), M, 32, DIM, 700, 600),
                  ("LU", "luxembourg", BLACK, 220, (96, 96, 104), 1220, 520), ("Luxembourg", ("luxembourg", 0, 0.2), M, 32, DIM, 1220, 600),
                  ("for US stocks: IE has an edge", "edge", M, 40, FG, W / 2, 780)]),
    "tax30": sc_tax(False), "tax15": sc_tax(True),
    "estate": term([("bonus:", "bonus", DIM), ("US funds + you die → US estate tax", "die", FG),
                    ("  above $60,000 (depends on your country)", "$60,000", DIM), ("Irish funds → generally not", "irish", FG)], size=40),
    "domicile": term([('twin(VOO) = "S&P 500 UCITS ETF"', "twin", FG), ('domicile = "IE"', ("domiciled", 0), FG),
                      ("# domicile: where the fund legally lives", "legally", DIM)]),
    "ch5": chapter(5, "What does it cost?"),
    "fees": term([(f"{'fund':<26}{'fee/yr':>8}", 0.1, DIM), (f"{'iShares  S&P 500 UCITS':<26}{'0.07%':>8}", "ishares", FG),
                  (f"{'Vanguard S&P 500 UCITS':<26}{'0.07%':>8}", "vanguard", FG), (f"{'some others':<26}{'~0.05%':>8}", "0.05%", FG),
                  (f"{'VOO (US, not for you)':<26}{'0.03%':>8}", ("0.07%", 0, 0.8), DIM)]),
    "four": sc_four,
    "nobill": term([("bill: none", "bill", FG), ("fee: taken from the fund, daily", "fee", FG), ("→ already in the price", "already", DIM)]),
    "bank": sc_bars([("typical bank fund", "1%+", 1.0, ERR, "banks"), ("S&P 500 UCITS ETF", "0.07%", 0.07, FG, 0.3)],
                    note=("← that's where the real money goes", "real", DIM)),
    "mistakes": bigs([("01   02   03", 0.1, M, 34, DIM, W / 2, 420), ("Three beginner mistakes.", 0.4, LIGHT, 96, FG, W / 2, 580)]),
    "currency": sc_currency, "price": sc_price, "accdist": sc_accdist,
    "depends": term([("best = depends(", "depends", FG), ("    where_you_live,", "live", FG), ("    your_taxes)", "taxed", FG),
                     ("→ next video", "next", DIM)]),
    "checklist": checklist("checklist", [('search "S&P 500 UCITS ETF"', "search"), ("check the yearly fee", "fee"),
                                         ("check domicile = Ireland", "ireland"), ("pick ACC or DIST", "pick")]),
    "risk": sc_risk,
    "past": bigs([("over the long run: up", "long", M, 38, DIM, W / 2, 320), ("past ≠ future", "past", BLACK, 150, FG, W / 2, 540),
                  ("invest money you won't need for years", "years", M, 40, FG, W / 2, 700)], [("boom", "past", 0.6)]),
    "plan": term([("scope(this_video) = 1 index", "one", FG), ("→ a starting point", "starting", FG), ("≠ a full plan", "plan", DIM)]),
    "subscribe": sc_subscribe, "end": sc_end,
}

# --------------------------------------------------------------------------- overlays: disclaimer, terminal-style subscribe reminder
E = os.path.join(D, "long")
os.makedirs(E, exist_ok=True)
K = len(LINES)
NF = sum(frames)
SCN = [l["scene"] for l in LINES]
NFA_OFF = starts[SCN.index("ch1")]
SUB_T0 = starts[SCN.index("ch4")] + 1.2
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
if __name__ == "__main__" and os.environ.get("LONG_PREVIEW") is None:
    yy, xx = np.mgrid[0:H, 0:W]
    vig = (1 - 0.38 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.4).clip(0.45, 1)[..., None].astype(np.float32)
    grng = np.random.default_rng(7)
    grain = [grng.normal(0, 3.2, (H, W, 1)).astype(np.float32) for _ in range(6)]

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
        _SD["dur"] = frames[i] / FPS
        fn, ev = SCENES[l["scene"]](frames[i] / FPS, i)
        fns.append(fn)
        events += [(n, starts[i] + tt, g) for n, tt, g in ev]
    # glitch cuts into each chapter card and out of it; plain hard cuts elsewhere
    cut_g = [starts[j] for j in range(1, K) if SCN[j].startswith("ch") or SCN[j - 1].startswith("ch") or SCN[j] == "end"]
    G = [(at, 0.32, g) for n, at, g in events if n == "glitch"] + [(c - 0.05, 0.12, 0.6) for c in cut_g]

    vid = os.path.join(E, "video.mp4")
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    for k in range(NF):
        t = k / FPS
        i = max(j for j in range(K) if starts[j] <= t + 1e-6)
        _SD["dur"] = frames[i] / FPS
        im = fns[i](t - starts[i]).convert("RGB")
        overlays(im, t)
        a = np.asarray(im, dtype=np.uint8)
        amt = max([g * (1 - (t - at) / du) for at, du, g in G if at <= t < at + du] + [0])
        if amt > 0.02 and k % 3 != 2:
            a = glitch(a, amt, k)
        f = a.astype(np.float32) * vig + grain[k % 6]
        enc.stdin.write(f.clip(0, 255).astype(np.uint8).tobytes())
        if k % 600 == 0:
            print("frame", k, "/", NF, flush=True)
    enc.stdin.close()
    enc.wait()
    print("video ok", NF, flush=True)

    # ----------------------------------------------------------------------- sound: drone that changes chord per part, silences, booms, glitches, keys
    n = int(TOTAL * SR)
    tt = np.arange(n) / SR
    mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
    CHORDS = [(45, 52, 57, 60, 64), (41, 48, 53, 57, 64), (38, 50, 53, 57, 62), (40, 52, 55, 59, 64),
              (45, 52, 57, 60, 64), (41, 48, 53, 57, 64), (45, 52, 57, 60, 64)]
    PART, p = [], 0
    for s_ in SCN:
        if s_.startswith("ch"):
            p += 1
        PART.append(6 if s_ in ("risk", "past", "plan", "subscribe", "end") else p)
    music = np.zeros(n)
    for c, notes in enumerate(CHORDS):
        lines_c = [j for j in range(K) if PART[j] == c]
        if not lines_c:
            continue
        a0, a1 = starts[lines_c[0]], starts[lines_c[-1]] + frames[lines_c[-1]] / FPS
        w = np.clip(np.minimum((tt - a0 + 0.6) / 1.2, (a1 + 0.6 - tt) / 1.2), 0, 1)
        pad = np.zeros(n)
        for j, m in enumerate(notes):
            for det in (-0.15, 0.15):
                f = mtof(m) + det
                pad += (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.07 * tt + j))
        pad += 1.4 * np.sin(2 * np.pi * mtof(notes[0] - 12) * tt)
        music += pad * w
    music += 0.6 * np.sin(2 * np.pi * mtof(88) * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * tt))
    music /= np.max(np.abs(music))
    env = np.minimum(1, tt / 2.5) * np.clip((TOTAL - tt) / 2.5, 0, 1)
    j1, j2, j3 = SCN.index("search"), SCN.index("four"), SCN.index("past")
    DIPS = [(when(j1, "nothing") + 0.5, 0.45), (when(j2, "€4") - 0.3, 0.3), (when(j3, "past") - 0.3, 0.3)]
    for c0, hw in DIPS:
        env *= 1 - np.clip(1 - np.abs(tt - c0) / hw, 0, 1) ** 0.3
    write_wav(os.path.join(E, "music.wav"), (music * env * 0.5).astype(np.float32))

    sfx = np.zeros(n + SR, dtype=np.float32)

    def put(x, at, g):
        i0 = int(max(0, at) * SR)
        sfx[i0:i0 + len(x)] += (x * g)[: len(sfx) - i0]

    srng = np.random.default_rng(9)
    bt = np.arange(int(1.6 * SR)) / SR
    boom = np.sin(2 * np.pi * np.cumsum(32 + 40 * np.exp(-bt / 0.08)) / SR) * np.exp(-bt / 0.5)
    gt = int(0.32 * SR)
    gl = srng.standard_normal(gt) * np.repeat(srng.integers(0, 2, gt // 441 + 1), 441)[:gt]
    gl = gl + 0.6 * np.sign(np.sin(2 * np.pi * 180 * np.arange(gt) / SR)) * np.repeat(srng.integers(0, 2, gt // 882 + 1), 882)[:gt]
    gl /= np.max(np.abs(gl))
    kt = np.arange(int(0.03 * SR)) / SR
    tick = np.sin(2 * np.pi * 2600 * kt) * np.exp(-kt / 0.005) + 0.4 * srng.standard_normal(len(kt)) * np.exp(-kt / 0.002)
    for name, at, g in events:
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
        put(tick, at, 0.06 * srng.uniform(0.7, 1.0))
    write_wav(os.path.join(E, "sfx.wav"), sfx[:n])
    mix = os.path.join(E, "mix.wav")
    run(["ffmpeg", "-y", "-i", os.path.join(A, "voice.wav"), "-i", os.path.join(E, "music.wav"), "-i", os.path.join(E, "sfx.wav"), "-filter_complex",
         "[0:a]aformat=channel_layouts=stereo,highpass=f=90,acompressor=threshold=-20dB:ratio=3:attack=5:release=90,asplit=2[v1][v2];"
         "[1:a]aformat=channel_layouts=stereo,volume=0.35[m];[m][v1]sidechaincompress=threshold=0.02:ratio=3:attack=30:release=600[md];"
         "[2:a]aformat=channel_layouts=stereo,volume=0.5[fx];"
         "[v2][md][fx]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
         "-map", "[out]", "-ar", str(SR), mix])

    # ----------------------------------------------------------------------- quiet karaoke captions (grey -> white, no box) + final render
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
    final = os.path.join(O, "long_dark_16x9.mp4")
    run(["ffmpeg", "-y", "-i", vid, "-i", mix, "-vf", f"ass={subs}:fontsdir={FD},fade=t=out:st={TOTAL - 0.8:.2f}:d=0.8",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest", final])
    print(f"done total={TOTAL:.2f}s")
