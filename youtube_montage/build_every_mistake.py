"""'Every Investing Mistake Explained' in the dark video-essay style (inspired by the EGO channel):
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
A = os.path.join(D, "assets_mistakes")
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
# "Every Investing Mistake Explained". Facts checked in October 2026 (sources in scripts/every_mistake_script.md).
SAY = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten",
       "11": "eleven", "12": "twelve", "1.2": "one point two", "€200": "two hundred euros", "7%": "seven percent", "25": "twenty-five",
       "€244,000": "two hundred and forty-four thousand euros", "55": "fifty-five", "35": "thirty-five",
       "€104,000": "a hundred and four thousand euros", "2020": "twenty twenty", "1.8%": "one point eight percent", "30": "thirty",
       "0.03%": "zero point zero three percent", "€60,000": "sixty thousand euros", "J.P": "J P", "S&P": "S and P", "500": "five hundred",
       "1995": "nineteen ninety-five", "2014": "twenty fourteen", "9.9%": "nine point nine percent", "6.1%": "six point one percent",
       "2.2%": "two point two percent", "2019": "twenty nineteen", "1926": "nineteen twenty-six", "2016": "twenty sixteen",
       "4%": "four percent", "€1.9": "one point nine", "66,000": "sixty-six thousand", "11.4%": "eleven point four percent",
       "17.9%": "seventeen point nine percent", "2021": "twenty twenty-one", "ETF": "E T F", "ETFs": "E T F's", "CFDs": "C F D's",
       "US": "U S"}


def speak(sub):
    out = []
    for w in sub.replace("**", "").split():
        core = w.rstrip(".,:;?!")
        out.append(SAY.get(core, core) + w[len(core):])
    return " ".join(out)


def L(scene, sub, hide=False):
    return dict(scene=scene, sub=sub, tts=speak(sub), hide=hide)


LINES = [
    # ------------------------------------------------------------------ intro
    L(("big", [("the wrong fund?", "wrong", "MONO", 42, "DIM", 960, 440), ("no. the classic mistakes.", "classic", "LIGHT", 86, "FG", 960, 580)]),
      "Most investors don't lose money because they picked the wrong fund. They lose it through a few classic mistakes."),
    L(("boxes", (), "twelve"), "There are twelve of them. And almost every investor makes at least one."),
    L(("term", [("> easy to make", "easy", "FG"), ("> can cost you thousands", "thousands", "ERR")], 54),
      "Each one is easy to make. And each one can cost you thousands of euros."),
    L(("big", [("−1.2 pts / year", "1.2", "BLACK", 170, "ERR", 960, 520), ("what investors earned vs their own funds (Morningstar)", ("1.2", 0, 0.6), "MONO", 30, "DIM", 960, 620)],
       [("boom", "1.2", 0.8)]),
      "Morningstar found that fund investors earned about 1.2 percentage points a year less than their own funds, just because of when they bought and sold."),
    L(("term", [("hype: none", "hype", "DIM"), ("stock picks: none", "picks", "DIM"), ("not financial advice", "advice", "ERR")]),
      "No hype, and no stock picks. This is education, not financial advice."),
    L(("boxes", [0], 0.1), "Let's open the first box."),
    # ------------------------------------------------------------------ 01 waiting to start
    L(("chap", 1, "Waiting to start"), "Mistake 1. Waiting to start."),
    L(("term", [("> wait for the right moment", "moment", "DIM"), ("> wait for a better salary", "salary", "DIM"), ("> the most expensive mistake", "expensive", "ERR")], 50),
      "It feels safer to wait for the right moment, or a better salary. But waiting is often the most expensive mistake of all."),
    L(("bars", [("start at 25", "≈ €244,000", 1.0, "FG", "25"), ("start at 35", "≈ €104,000", 0.43, "GREY", "35")]),
      "With €200 a month at 7% a year, starting at 25 gives about €244,000 at 55. Starting at 35 gives about €104,000."),
    L(("big", [("more than half.", "half", "LIGHT", 110, "ERR", 960, 520), ("lost to ten years of waiting (hypothetical)", "waiting", "MONO", 34, "DIM", 960, 640)]),
      "Ten years of waiting cost more than half of the final amount."),
    L(("term", [("the first euros: the most time to grow", "first", "FG"), ("you don't need a lot to start", "lot", "DIM")], 48),
      "The first euros you invest have the most time to grow. And you don't need a lot to start. Many brokers accept a few euros a month."),
    # ------------------------------------------------------------------ 02 no safety cushion
    L(("chap", 2, "No safety cushion"), "Mistake 2. No safety cushion."),
    L(("term", [("investing without an emergency fund", "emergency", "FG"), ("= driving without a spare tyre", "tyre", "DIM")], 48),
      "Investing without an emergency fund is like driving without a spare tyre. The first flat forces you to stop."),
    L(("term", [("job lost + market crash", "crash", "ERR"), ("→ forced to sell at the bottom", "sell", "ERR")], 50),
      "Lose your job during a crash, and you may have to sell at the worst possible moment."),
    L(("big", [("3–6 months", "three", "BLACK", 170, "FG", 960, 520), ("of expenses, set aside first", "expenses", "MONO", 36, "DIM", 960, 620)]),
      "A common rule of thumb: three to six months of expenses in a savings account, before you invest."),
    L(("big", [("it protects your nerves.", "nerves", "LIGHT", 90, "FG", 960, 560)]),
      "A cushion doesn't just protect your money. It protects your nerves."),
    # ------------------------------------------------------------------ 03 money you need soon
    L(("chap", 3, "Money you need soon"), "Mistake 3. Investing money you need soon."),
    L(("term", [("> a house deposit next year", "house", "FG"), ("> a wedding", "wedding", "FG"), ("→ not in shares", "belong", "ERR")], 50),
      "Money for a house deposit next year, or a wedding, doesn't belong in the stock market."),
    L(("chart", [100, 102, 104, 103, 95, 82, 70, 66, 72, 78], "−1/3", "third", "ERR"),
      "Markets can drop by a third in a few weeks, like in 2020. And they don't care about your deadline."),
    L(("big", [("need it soon?", "need", "LIGHT", 100, "FG", 960, 460), ("keep it out of shares.", "stays", "LIGHT", 80, "DIM", 960, 600)]),
      "A simple rule: money you need within a few years stays out of the stock market."),
    L(("term", [("short goal → savings account", "savings", "FG"), ("or a money market fund", "money", "DIM")], 50),
      "For short goals, a savings account or a money market fund is usually the calmer place."),
    # ------------------------------------------------------------------ 04 high fees
    L(("chap", 4, "High fees"), "Mistake 4. Paying high fees."),
    L(("big", [("1.8%", "1.8%", "BLACK", 200, "ERR", 960, 520), ("a year. sounds small.", "small", "MONO", 36, "DIM", 960, 620)]),
      "A fee of 1.8% a year sounds small. Over thirty years, it isn't."),
    L(("big", [("€200 / month · 30 years", "€200", "MONO", 34, "DIM", 960, 380), ("€60,000+", "€60,000", "BLACK", 190, "ERR", 960, 580),
               ("0.03% vs 1.8% fees (hypothetical, 7% / year)", ("€60,000", 0, 0.6), "MONO", 30, "DIM", 960, 670)], [("boom", "€60,000", 0.8)]),
      "On €200 a month for 30 years, the gap between a 0.03% ETF and a 1.8% fund can be more than €60,000."),
    L(("term", [("> fund: yearly fee", "yearly", "FG"), ("> entry fees", "entry", "FG"), ("> broker fees", "broker", "FG"), ("> currency fees", "currency", "FG")], 50),
      "Fees hide in many places. The fund's yearly fee, entry fees, broker fees, currency fees."),
    L(("big", [("every euro in fees", "euro", "MONO", 40, "DIM", 960, 450), ("stops compounding for you.", "compounding", "LIGHT", 80, "FG", 960, 580)]),
      "Every euro paid in fees is a euro that stops compounding for you."),
    L(("big", [("control what you pay.", "pay", "LIGHT", 96, "FG", 960, 560)]),
      "You can't control the market. You can control what you pay."),
    # ------------------------------------------------------------------ 05 timing the market
    L(("chap", 5, "Timing the market"), "Mistake 5. Timing the market."),
    L(("term", [("sell before the crash", "crash", "FG"), ("buy back before the recovery", "recovery", "FG"), ("→ almost nobody gets both right", "nobody", "ERR")], 48),
      "Sell before the crash, buy back before the recovery. It sounds easy. Almost nobody gets both right."),
    L(("cols", [("9.9%", "invested", 1.0, "FG", "9.9%"), ("6.1%", "missed 10 days", 0.62, "ERR", "6.1%")], "S&P 500, 1995–2014 (J.P. Morgan)", 0.2),
      "In one J.P. Morgan study of the S&P 500 from 1995 to 2014, staying invested earned about 9.9% a year. Missing just the ten best days cut that to 6.1%."),
    L(("big", [("stay in.", "stay", "LIGHT", 130, "FG", 960, 560)]),
      "And many of the best days came right after the worst ones. To catch them, you have to stay in."),
    L(("term", [("even professionals rarely manage it", "professionals", "FG"), ("most active funds lag their index", "lag", "DIM")], 48),
      "Even professionals rarely manage it. Over the long run, most active funds lag their index."),
    # ------------------------------------------------------------------ 06 panic selling
    L(("chap", 6, "Panic selling"), "Mistake 6. Panic selling."),
    L(("big", [("−34%", "third", "BLACK", 200, "ERR", 960, 520), ("S&P 500 · February–March 2020", "2020", "MONO", 34, "DIM", 960, 620)]),
      "In early 2020, the S&P 500 fell by about a third in a few weeks. Millions of people sold."),
    L(("chart", [100, 68, 72, 79, 85, 92, 98, 101, 104], "≈ 5 months", "five", "FG"),
      "About five months after the bottom, it was back at its old high. Those who sold missed the rebound."),
    L(("term", [("drop on paper: temporary", "temporary", "DIM"), ("sell → loss: permanent", "permanent", "ERR")], 52),
      "Selling turns a temporary drop into a permanent loss."),
    L(("big", [("write your plan down.", "plan", "LIGHT", 96, "FG", 960, 470), ("before the crash, not during it", "during", "MONO", 36, "DIM", 960, 600)]),
      "Writing your plan down before a crash makes it much easier to follow during one."),
    # ------------------------------------------------------------------ 07 chasing winners
    L(("chap", 7, "Chasing winners"), "Mistake 7. Chasing last year's winners."),
    L(("term", [("last year's best fund", "best", "FG"), ("a sure thing?", "isn't", "DIM")], 52),
      "Last year's best fund looks like a sure thing. It usually isn't."),
    L(("big", [("2.2%", "2.2%", "BLACK", 200, "ERR", 960, 520), ("of 2019's top US stock funds stayed on top 2 more years (S&P)", ("2.2%", 0, 0.6), "MONO", 28, "DIM", 960, 620)],
       [("boom", "2.2%", 0.8)]),
      "Of the US stock funds in the top quarter in 2019, only 2.2% stayed in the top quarter in each of the next two years."),
    L(("term", [("in the headlines", "headlines", "FG"), ("→ the gains are often already made", "behind", "DIM")], 50),
      "By the time a fund or a theme is in the headlines, a lot of the gains are often behind it."),
    L(("term", [("buy after the gains", "after", "FG"), ("sell after the losses", "losses", "ERR"), ("= the 1.2-point gap", "gap", "DIM")], 50),
      "Investors pile in after the gains, and pile out after the losses. That's exactly how the 1.2 point gap happens."),
    # ------------------------------------------------------------------ 08 one big bet
    L(("chap", 8, "One big bet"), "Mistake 8. Putting everything on one bet."),
    L(("big", [("4%", "4%", "BLACK", 220, "FG", 960, 520), ("of US stocks created all the net gains, 1926–2016", ("4%", 0, 0.6), "MONO", 30, "DIM", 960, 620)],
       [("boom", "4%", 0.8)]),
      "From 1926 to 2016, just 4% of US stocks created all the net wealth of the stock market. More than half did worse than short-term government bills."),
    L(("term", [("DE · Wirecard, in the DAX", "Wirecard", "FG"), ("€1.9 billion: missing", "missing", "ERR"), ("2020: collapsed", "collapsed", "ERR")], 50),
      "In 2020, Wirecard, a company in Germany's top index, collapsed after €1.9 billion turned out to be missing."),
    L(("big", [("one company: a bet.", "bet", "MONO", 44, "DIM", 960, 460), ("thousands: a plan.", "plan", "MONO", 44, "FG", 960, 570)]),
      "Owning one company, even a famous one, is a bet. Owning thousands is a plan."),
    L(("term", [("your employer's shares", "work", "FG"), ("company fails → job + savings gone", "fails", "ERR")], 48),
      "That includes the company you work for. If it fails, you can lose your job and your savings at the same time."),
    # ------------------------------------------------------------------ 09 trading too much
    L(("chap", 9, "Trading too much"), "Mistake 9. Trading too much."),
    L(("cols", [("11.4%", "most active", 0.64, "ERR", "11.4%"), ("17.9%", "market", 1.0, "FG", "17.9%")], "1991–1996 (Barber & Odean)", 0.2),
      "A famous study of more than 66,000 households found that those who traded the most earned 11.4% a year. The market earned 17.9%."),
    L(("term", [("every trade: fees, spreads, taxes", "trade", "FG"), ("checking daily → the urge to act", "checking", "DIM")], 48),
      "Every trade costs fees, spreads, sometimes taxes. And checking your account every day makes you want to act."),
    L(("big", [("do nothing.", "nothing", "LIGHT", 130, "FG", 960, 560)]),
      "Often, the best thing to do is nothing."),
    L(("big", [("more trades,", "more", "LIGHT", 100, "FG", 960, 460), ("less money.", "less", "LIGHT", 100, "ERR", 960, 600)]),
      "In that study, the more people traded, the less they earned."),
    # ------------------------------------------------------------------ 10 following hype
    L(("chap", 10, "Following hype"), "Mistake 10. Following the hype."),
    L(("term", [("> a social media tip", "social", "FG"), ("> the stock everyone talks about", "talking", "FG"), ("> a friend who got rich", "rich", "FG")], 50),
      "A tip from social media, the stock everyone is talking about, a friend who got rich last month."),
    L(("chart", [17, 19, 20, 40, 150, 347, 225, 90, 50, 45], "×10, then gone", "gone", "ERR"),
      "In January 2021, GameStop shares rose more than tenfold in a few weeks. Within a month, most of those gains were gone."),
    L(("big", [("everyone knows?", "everyone", "LIGHT", 100, "FG", 960, 460), ("you're not early.", "early", "LIGHT", 100, "DIM", 960, 600)]),
      "If you hear about it from everyone, you're probably not early."),
    L(("term", [("> guaranteed returns", "guaranteed", "ERR"), ("> urgency: buy now", "urgency", "ERR"), ("> a famous face", "famous", "ERR")], 52),
      "Hype is also where scams hide. Guaranteed returns, urgency, a famous face."),
    # ------------------------------------------------------------------ 11 not understanding it
    L(("chap", 11, "Not understanding it"), "Mistake 11. Buying what you don't understand."),
    L(("term", [("leveraged ETFs", "Leveraged", "FG"), ("CFDs", "CFDs", "FG"), ("structured products", "structured", "FG"), ("can't explain it → warning sign", "warning", "ERR")], 48),
      "Leveraged ETFs, CFDs, structured products with a fancy coupon. If you can't explain how it makes money, that's a warning sign."),
    L(("big", [("for the seller first.", "seller", "LIGHT", 90, "FG", 960, 560)]),
      "Complex products are often built to make money for the seller first."),
    L(("term", [("explain it in 2 sentences?", "sentences", "FG"), ("no → don't buy it yet", "wait", "DIM")], 52),
      "A simple test: could you explain it to a friend in two sentences? If not, wait."),
    # ------------------------------------------------------------------ 12 the wrong account
    L(("chap", 12, "The wrong account"), "Mistake 12. Using the wrong account."),
    L(("term", [("regular account: taxed", "regular", "DIM"), ("tax-free account available?", "tax-free", "FG"), ("→ thousands over time", "thousands", "ERR")], 50),
      "Investing in a regular account when your country offers a tax-free one can cost you thousands over time."),
    L(("big", [("same ETF.", "Same", "LIGHT", 100, "DIM", 960, 440), ("different account.", "Different", "LIGHT", 100, "FG", 960, 580)]),
      "Same ETF, same market. Different account, different result."),
    L(("term", [("a \"tax-free\" product", "sold", "FG"), ("+ high fees", "fees", "ERR"), ("= the tax break disappears", "disappear", "DIM")], 50),
      "But watch out for products sold as tax-free that come with high fees. The tax break can disappear in the costs."),
    L(("big", [("every account in Europe →", "every", "LIGHT", 70, "FG", 960, 560)]),
      "We explain every type of investment account in Europe in another video."),
    # ------------------------------------------------------------------ outro
    L(("boxes", "all", 0.2), "Those are the twelve mistakes. The good news: most of them are fixed by doing less, not more.", True),
    L(("term", [("start early", "Start", "FG"), ("keep a cushion", "cushion", "FG"), ("pay low fees", "fees", "FG"), ("stay invested", "stay", "FG")], 56),
      "Start early. Keep a cushion. Pay low fees. And stay invested.", True),
    L(("term", [("markets can fall for years", "years", "DIM"), ("recommendations: none", "recommendation", "DIM"), ("not financial advice", "advice", "ERR")], 50),
      "Markets can go down for years, and nothing here is a recommendation. This is not financial advice.", True),
    L(("big", [("which one have you made?", "mistake", "LIGHT", 80, "FG", 960, 560)]),
      "Which mistake have you already made? Most of us have made at least one.", True),
    L(("end", "Every Investment Account in Europe Explained"),
      "If this helped, subscribe. Next up, every investment account in Europe, explained.", True),
]
TRANS = []
LEAD, GAP, TAIL = 0.5, 1.30, 3.0
SHORT_LAST = 2
# voice: Kokoro (open-source, Apache 2.0, free for commercial use), British voice 'bf_emma'
KOKORO_DIR = os.environ.get("KOKORO_DIR", os.path.join(D, "kokoro"))
VOICE, VOICE_LANG, VOICE_SPEED = "bf_emma", "en-gb", 0.92
_KOKORO = []


def kokoro_say(text, path):
    if os.path.exists(path) and os.path.exists(path + ".txt") and open(path + ".txt").read() == text:
        return                                     # same line, same text: reuse the audio already made
    if not _KOKORO:
        from kokoro_onnx import Kokoro
        _KOKORO.append(Kokoro(os.path.join(KOKORO_DIR, "kokoro-v1.0.onnx"), os.path.join(KOKORO_DIR, "voices-v1.0.bin")))
    a, sr = _KOKORO[0].create(text, voice=VOICE, speed=VOICE_SPEED, lang=VOICE_LANG)
    pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    open(path + ".txt", "w").write(text)


def tts(i, text):
    raw, out = os.path.join(A, "voice", f"l{i:02d}_raw.wav"), os.path.join(A, "voice", f"l{i:02d}.wav")
    kokoro_say(text, raw)
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
SC = {(l["scene"] if isinstance(l["scene"], str) else i): (starts[i], starts[i] + frames[i] / FPS) for i, l in enumerate(LINES)}


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

# --------------------------------------------------------------------------- POV story scenes
def person(d, cx, cy, s, col):
    """Minimal 'you' glyph: head + shoulders."""
    d.ellipse([cx - 20 * s, cy - 78 * s, cx + 20 * s, cy - 38 * s], fill=col)
    d.pieslice([cx - 44 * s, cy - 30 * s, cx + 44 * s, cy + 58 * s], 180, 360, fill=col)


def bars(rows, extra=None):
    """Horizontal bars: (label, value text, fraction, colour, cue); extra = (text, cue) shown big on the right."""
    def build(dur, i):
        fm = F(MONO, 32)
        R = [(lab, val, fr, col, trig(i, cue)) for lab, val, fr, col, cue in rows]
        for lab, _, _, _, t0 in R:
            typed(lab, 0, t0, 30, starts[i])
        ex = (extra[0], trig(i, extra[1])) if extra else None
        X0, L = 340, 1000

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            for k, (lab, val, fr, col, t0) in enumerate(R):
                y = 400 + k * 190
                d.text((X0, y - 24), typed(lab, t, t0, 30), font=fm, fill=FG, anchor="ls")
                g = ease_out(prog(t, t0, t0 + 0.6))
                if g > 0:
                    d.rectangle([X0, y, X0 + max(8, L * fr * g), y + 60], fill=col)
                    d.text((X0 + max(8, L * fr * g) + 24, y + 46), val, font=F(MONOB, 40), fill=col, anchor="ls")
            if ex and t >= ex[1]:
                d.text((1620, 560), ex[0], font=F(BLACK, 170), fill=FG + (int(255 * prog(t, ex[1], ex[1] + 0.15)),), anchor="ms")
            return cam(im, t, dur, 500)
        ev = [("boom", t0, 0.35) for *_, t0 in R] + ([("boom", ex[1], 0.7)] if ex else [])
        return frame, ev
    return build


def sc_start(dur, i):
    tp, t25, teu, t200 = lw(i, "pov"), lw(i, "25"), lw(i, "europe"), lw(i, "€200")
    loc = "location = EU"
    typed(loc, 0, teu, 30, starts[i])
    fb, fm, fl = F(BLACK, 150), F(MONO, 34), F(MONOB, 26)

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        if t >= tp:
            d.text((W / 2, 260), "POV", font=fb, fill=FG + (int(255 * prog(t, tp, tp + 0.15)),), anchor="ms")
        if t >= t25:
            a = prog(t, t25, t25 + 0.3)
            person(d, 640, 640, 1.6, FG + (int(255 * a),))
        mid_text(d, 800, loc, typed(loc, t, teu, 30), fm, DIM, 640)
        if t >= t200:
            a = int(255 * prog(t, t200, t200 + 0.3))
            d.rounded_rectangle([1180, 520, 1500, 680], 14, outline=FG + (a,), width=3)
            d.text((1340, 610), "S&P 500 ETF", font=F(MONO, 30), fill=FG + (a,), anchor="ms")
            k = 0
            while t200 + 0.2 + k * 0.55 <= t:
                u = prog(t, t200 + 0.2 + k * 0.55, t200 + 0.2 + k * 0.55 + 0.5)
                if u < 1:
                    x = 760 + (1170 - 760) * ease_out(u)
                    d.rounded_rectangle([x - 50, 580, x + 50, 620], 20, fill=FG + (int(255 * (1 - u * 0.6)),))
                    d.text((x, 608), "€200", font=fl, fill=BG, anchor="ms")
                k += 1
        return cam(im, t, dur, 520)
    return frame, [("tick", t200 + 0.7 + k * 0.55, 0.4) for k in range(int(max(0, dur - lw(i, "€200") - 0.7) / 0.55))]


def sc_friends(dur, i):
    tu, td = lw(i, "upgrade"), lw(i, "don't")
    lab = "€200 → ETF"
    typed(lab, 0, td, 26, starts[i])
    xs = [480, 720, 960, 1200, 1440]

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        for k, x in enumerate(xs):
            you = k == 2
            person(d, x, 600, 1.3, FG if you else (96, 96, 104))
            if not you and t >= tu + k * 0.12:
                u = ease_back(prog(t, tu + k * 0.12, tu + k * 0.12 + 0.3))
                w, h = 34 * u, 60 * u
                d.rounded_rectangle([x - w / 2, 430 - h / 2, x + w / 2, 430 + h / 2], 6, outline=FG, width=3)
                d.text((x + 34, 410), "new", font=F(MONO, 20), fill=DIM, anchor="ls")
        mid_text(d, 760, lab, typed(lab, t, td, 26), F(MONO, 38), FG, 960)
        return cam(im, t, dur, 540)
    return frame, [("tick", tu + k * 0.12, 0.5) for k in range(4)]


def sc_drop(dur, i):
    td, tf, tk = lw(i, "drops"), lw(i, "fifth"), lw(i, "keep")
    path = [100, 104, 109, 113, 118, 112, 101, 94, 97, 103, 110, 116]
    keep = "> keep buying"
    typed(keep, 0, tk, 26, starts[i])
    X0, X1, Y0, Y1 = 400, 1400, 300, 740

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        d.line([(X0, Y0), (X0, Y1), (X1, Y1)], fill=FAINT, width=2)
        d.text((X1, Y1 + 40), "(illustration)", font=F(MONO, 22), fill=FAINT, anchor="rs")
        u = min(prog(t, 0.2, td + 0.6) * 0.62 + 0.38 * prog(t, tk, tk + 1.5), 1)
        n = len(path) - 1
        pts = [(X0 + 30 + k * (X1 - X0 - 60) / n, Y1 - 40 - (v - 90) / 30 * (Y1 - Y0 - 80)) for k, v in enumerate(path)]
        m = u * n
        k = int(m)
        show = pts[: k + 1] + ([(pts[k][0] + (pts[k + 1][0] - pts[k][0]) * (m - k), pts[k][1] + (pts[k + 1][1] - pts[k][1]) * (m - k))] if k < n else [])
        if len(show) > 1:
            d.line(show, fill=FG, width=5, joint="curve")
        if t >= tf:
            d.text((1640, 520), "−20%", font=F(BLACK, 110), fill=ERR + (int(255 * prog(t, tf, tf + 0.15)),), anchor="ms")
            d.text((1640, 580), "on paper", font=F(MONO, 30), fill=DIM, anchor="ms")
        mid_text(d, 850, keep, typed(keep, t, tk, 26), F(MONO, 40), FG)
        return cam(im, t, dur, 520)
    return frame, [("glitch", td, 0.5), ("boom", tf, 0.7)]


def sc_age55(dur, i):
    t72, t244 = lw(i, "€72,000"), lw(i, "€244,000")
    put = "put in: €72,000"
    typed(put, 0, t72, 26, starts[i])

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        mid_text(d, 340, put, typed(put, t, t72, 26), F(MONO, 44), DIM)
        if t >= t244:
            v = 243994 * ease_out(prog(t, t244, t244 + 1.2))
            d.text((W / 2, 600), f"€{int(round(v, -3)):,}", font=F(BLACK, 210), fill=FG, anchor="ms")
            d.text((W / 2, 690), "account value (hypothetical)", font=F(MONO, 30), fill=DIM + (int(255 * prog(t, t244 + 0.8, t244 + 1.1)),), anchor="ms")
        return cam(im, t, dur, 520, 0.05)
    return frame, [("tick", t244 + k * 0.1, 0.45 * (1 - k / 13)) for k in range(12)] + [("boom", t244 + 1.2, 1.0)]


def sc_pov_end(dur, i):
    fk, ft = F(MONO, 26), F(LIGHT, 76)
    typed("next >", 0, 0.05, 30, starts[i])
    ph = Cv(None)
    ph.rect([240, 430, 1040, 880], None, r=6, outline=FAINT, width=2)
    ph.text((640, 665), "next video", MONO, 30, DIM, anchor="mm")
    ph.ellipse([1260, 460, 1650, 850], None, outline=FAINT, width=2)
    ph.text((1455, 655), "subscribe", MONO, 30, DIM, anchor="mm")
    ph = ph.out()

    def frame(t):
        im = black()
        d = ImageDraw.Draw(im, "RGBA")
        mid_text(d, 130, "next >", typed("next >", t, 0.05, 30), fk, DIM)
        letters(d, (W / 2, 250), "Which S&P 500 ETF can Europeans buy?", ft, t, 0.2, step=0.025)
        comp(im, ph, 0, 0, prog(t, 1.0, 1.6))
        return cam(im, t, dur, 540, 0.02)
    return frame, [("boom", 0.0, 0.5)]


SCENES = {
    "start": sc_start, "friends": sc_friends,
    "age35": bars([("put in", "€24,000", 0.69, (110, 110, 118), "put"), ("your account", "≈ €35,000", 0.99, FG, "account")]),
    "drop": sc_drop,
    "age45": bars([("you add / year", "€2,400", 0.33, (110, 110, 118), "put"), ("your money earns / year", "≈ €7,300", 1.0, FG, "earns")],
                  extra=("×3", "three")),
    "age55": sc_age55,
    "nobody": bigs([("Nobody noticed.", 0.2, LIGHT, 110, FG, W / 2, 540), ("not even you", "even", MONO, 38, DIM, W / 2, 660)]),
    "trick": term([("time", "time", FG), ("+ a cheap fund", "cheap", FG), ("+ not stopping", "stopping", FG)], size=60),
    "disclaimer": term([("hypothesis: 7% / year", "7%", FG), ("real returns: up and down", "real", DIM),
                        ("guaranteed: nothing", "guaranteed", DIM), ("not financial advice", "advice", ERR)]),
    "end": sc_pov_end,
}
AGE = {"start": 25, "friends": 25, "age35": 35, "drop": 38, "age45": 45, "age55": 55, "nobody": 55, "trick": 55}

# --------------------------------------------------------------------------- POV long version: scenes described in the script as (kind, args...)
COLS = {"FG": FG, "DIM": DIM, "ERR": ERR, "GREY": (110, 110, 118)}
FONTS = {"MONO": MONO, "MONOB": MONOB, "BLACK": BLACK, "LIGHT": LIGHT}


def k_term(rows, size=44):
    return term([(t, c, COLS[col]) for t, c, col in rows], size=size)


def k_big(items, events=()):
    return bigs([(t, c, FONTS[f], s, COLS[col], x, y) for t, c, f, s, col, x, y in items], events)


def k_bars(rows, extra=None):
    return bars([(lab, v, fr, COLS[col], c) for lab, v, fr, col, c in rows], extra)


def k_chap(age, title):
    def build(dur, i):
        fk, ft = F(MONO, 30), F(LIGHT, 104)
        lab = f"AGE {age}"
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


def k_grid(m0, m1, label, cue):
    """30 years x 12 months of €200: one square per month, filled up to m1."""
    def build(dur, i):
        t0 = trig(i, cue)
        typed(label, 0, t0, 30, starts[i])
        X0, Y0, STEP, SZ = 570, 330, 26, 20
        fl, fa = F(MONO, 40), F(MONO, 26)
        t_fill = (max(0.2, t0 - 0.3), max(0.2, t0 - 0.3) + 1.6)

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            n = int(round(m0 + (m1 - m0) * ease_out(prog(t, *t_fill))))
            for k in range(360):
                x, y = X0 + (k // 12) * STEP, Y0 + (k % 12) * STEP
                if k < n:
                    d.rectangle([x, y, x + SZ, y + SZ], fill=FG if k < n - 1 else ERR)
                else:
                    d.rectangle([x, y, x + SZ, y + SZ], outline=FAINT, width=1)
            d.text((X0 - 24, Y0 + 12 * STEP / 2 + 8), "25", font=fa, fill=DIM, anchor="rs")
            d.text((X0 + 30 * STEP + 18, Y0 + 12 * STEP / 2 + 8), "55", font=fa, fill=DIM, anchor="ls")
            d.text((X0, Y0 - 40), "1 square = 1 month = €200", font=F(MONO, 26), fill=DIM, anchor="ls")
            mid_text(d, 760, label, typed(label, t, t0, 30), fl, FG)
            return cam(im, t, dur, 480)
        k_ticks = min(14, max(1, m1 - m0))
        return frame, [("tick", t_fill[0] + j * 1.4 / k_ticks, 0.4) for j in range(k_ticks)]
    return build


def k_chart(path, note=None, note_cue=None, note_col="FG"):
    def build(dur, i):
        tn = trig(i, note_cue) if note else None
        X0, X1, Y0, Y1 = 420, 1380, 300, 760
        lo, hi = min(path), max(path)
        pad = (hi - lo) * 0.12 or 1
        lo, hi = lo - pad, hi + pad
        n = len(path) - 1
        pts = [(X0 + 30 + k * (X1 - X0 - 60) / n, Y1 - (v - lo) / (hi - lo) * (Y1 - Y0)) for k, v in enumerate(path)]
        t_end = max(1.4, min(dur * 0.75, (tn + 0.3) if tn else dur * 0.75))
        col = COLS.get(note_col, FG)

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            d.line([(X0, Y0 - 20), (X0, Y1 + 20), (X1, Y1 + 20)], fill=FAINT, width=2)
            d.text((X1, Y1 + 60), "(illustration)", font=F(MONO, 22), fill=FAINT, anchor="rs")
            m = prog(t, 0.2, t_end) * n
            k = int(m)
            show = pts[: k + 1] + ([(pts[k][0] + (pts[k + 1][0] - pts[k][0]) * (m - k), pts[k][1] + (pts[k + 1][1] - pts[k][1]) * (m - k))] if k < n else [])
            if len(show) > 1:
                d.line(show, fill=FG, width=5, joint="curve")
            if tn is not None and t >= tn:
                f = F(BLACK, 110) if len(note) <= 8 else F(MONO, 40)
                d.text((1640, 560), note, font=f, fill=col + (int(255 * prog(t, tn, tn + 0.15)),), anchor="ms")
            return cam(im, t, dur, 520)
        return frame, ([("boom", tn, 0.6)] if tn is not None else [])
    return build


def k_people(n, you, tags):
    def build(dur, i):
        T = [(idx, txt, trig(i, cue), COLS[col]) for idx, txt, cue, col in tags]
        for _, txt, t0, _ in T:
            typed(txt, 0, t0, 30, starts[i])
        xs = [W / 2 + (k - (n - 1) / 2) * 240 for k in range(n)]
        ft = F(MONO, 26)

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            for k, x in enumerate(xs):
                person(d, x, 620, 1.3, FG if k == you else (96, 96, 104))
            for idx, txt, t0, col in T:
                y = 760 if idx == you else (440 if idx % 2 == 0 else 400)
                mid_text(d, y, txt, typed(txt, t, t0, 30), ft, col, xs[idx])
            return cam(im, t, dur, 560)
        return frame, [("tick", t0, 0.5) for _, _, t0, _ in T]
    return build


KINDS = dict(term=k_term, big=k_big, bars=k_bars, chap=k_chap, grid=k_grid, chart=k_chart, people=k_people)
NAMED = {"start": sc_start, "search": sc_search, "age55": sc_age55, "end": sc_pov_end}


def scene_of(line):
    s = line["scene"]
    return NAMED[s] if isinstance(s, str) else KINDS[s[0]](*s[1:])

# --------------------------------------------------------------------------- "Every Crypto Explained": extra scene kinds (on top of the POV long-version kinds)
CATS = ["BITCOIN", "ETHEREUM", "OTHER CHAINS", "LAYER 2s", "STABLECOINS", "EXCHANGE TOKENS",
        "DeFi", "MEMECOINS", "NFTs", "PRIVACY COINS", "SCAM COINS", "DIGITAL EURO"]


def mix(c0, c1, u):
    return tuple(int(a + (b - a) * u) for a, b in zip(c0, c1))


def k_cchap(n, title):
    """Chapter card: progress row of 12 squares, 'BOX 03 / 12', title."""
    def build(dur, i):
        fk, ft = F(MONO, 30), F(LIGHT, 104)
        lab = f"BOX {n:02d} / 12"
        typed(lab, 0, 0.1, 20, starts[i])

        fbig = F(BLACK, 620)
        ac = CAT_COL[n - 1]

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            # giant chapter number drifting behind the card, and a scan line sweeping down after the cut
            d.text((W / 2 + 140 - 160 * t / dur, 800), f"{n:02d}", font=fbig, fill=mix(BG, ac, 0.16), anchor="ms")
            ys = 120 + 840 * ease_out(prog(t, 0.0, 0.6))
            if t < 0.6:
                d.rectangle([0, ys - 2, W, ys + 2], fill=FG + (int(90 * (1 - t / 0.6)),))
            x0 = W / 2 - 12 * 40 / 2 + 7
            for k in range(12):
                x = x0 + k * 40
                a = int(255 * prog(t, 0.05 + k * 0.03, 0.2 + k * 0.03))
                if k < n - 1:
                    d.rectangle([x, 318, x + 26, 344], fill=CAT_COL[k] + (int(a * 0.75),))
                elif k == n - 1:
                    d.rectangle([x, 318, x + 26, 344], fill=(FG if t % 0.8 < 0.4 and t < 1.6 else ac) + (a,))
                else:
                    d.rectangle([x, 318, x + 26, 344], outline=FAINT + (a,), width=2)
            mid_text(d, 450, lab, typed(lab, t, 0.1, 20), fk, DIM)
            letters(d, (W / 2, 590), title, ft, t, 0.35, step=0.035)
            w = 520 * ease_out(prog(t, 0.3, 1.0))
            d.line([(W / 2 - w / 2, 650), (W / 2 + w / 2, 650)], fill=ac + (200,), width=3)
            return cam(im, t, dur, 470, 0.03)
        return frame, [("boom", 0.0, 0.45)]
    return build


def k_boxes(hi=(), cue=0.2, label=None, label_cue=None):
    """The 12 boxes (4 x 3); hi = indices to light up, or 'all'."""
    def build(dur, i):
        t0 = trig(i, cue)
        tl = trig(i, label_cue) if label else None
        if label:
            typed(label, 0, tl, 30, starts[i])
        BW, BH, SX, SY = 330, 112, 360, 140
        X0, Y0 = W / 2 - 2 * SX + (SX - BW) / 2, 290
        lit = set(range(12)) if hi == "all" or not hi else set(hi)
        fl, fn = F(MONO, 26), F(MONO, 20)

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            for k in range(12):
                u = prog(t, t0 + k * 0.09, t0 + k * 0.09 + 0.25)
                if u <= 0:
                    continue
                a = int(255 * u)
                x, y = X0 + (k % 4) * SX, Y0 + (k // 4) * SY
                on = k in lit
                col = CAT_COL[k] if on else (78, 78, 86)
                y += 14 * (1 - ease_out(u))
                d.rectangle([x, y, x + BW, y + BH], outline=col + (a,), width=3 if on and hi else 2)
                if on and hi and hi != "all":
                    p = 0.5 + 0.5 * math.sin(t * 4 + k)
                    d.rectangle([x - 7, y - 7, x + BW + 7, y + BH + 7], outline=col + (int(90 * p * u),), width=2)
                d.text((x + 16, y + 30), f"{k + 1:02d}", font=fn, fill=(DIM if on else FAINT) + (a,), anchor="ls")
                d.text((x + BW / 2, y + BH / 2 + 12), CATS[k], font=fl, fill=col + (a,), anchor="mm")
            # a faint scan line keeps sweeping over the grid
            if t >= t0:
                ys = Y0 - 20 + ((t - t0) * 0.45 % 1) * (2 * SY + BH + 40)
                d.rectangle([X0 - 30, ys - 1, X0 + 3 * SX + BW + 30, ys + 1], fill=FG + (40,))
            if label:
                mid_text(d, 800, label, typed(label, t, tl, 30), F(MONO, 36), FG)
            return cam(im, t, dur, 500)
        return frame, [("tick", t0 + k * 0.09, 0.35) for k in range(12)]
    return build


def k_coin(tick, name, cue=0.2, notes=()):
    """A coin drawn as a ring with its ticker; notes = typed (text, cue, colour) lines on the right."""
    def build(dur, i):
        t0 = trig(i, cue)
        N = [(txt, trig(i, c), COLS[col]) for txt, c, col in notes]
        typed(name, 0, t0 + 0.5, 24, starts[i])
        for txt, tn, _ in N:
            typed(txt, 0, tn, 30, starts[i])
        cx, cy, R = (620 if N else W / 2), 460, 175
        cc = COIN_COL.get(tick, _SD["acc"])
        ft, fn = F(BLACK, 110 if len(tick) <= 3 else 84), F(MONO, 40)

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            u = ease_out(prog(t, t0, t0 + 0.7))
            cyf = cy + 8 * math.sin(t * 1.3)             # the coin floats
            if u > 0:
                d.arc([cx - R, cyf - R, cx + R, cyf + R], -90, -90 + 360 * u, fill=cc, width=6)
                a = int(255 * prog(t, t0 + 0.3, t0 + 0.6))
                d.ellipse([cx - R + 24, cyf - R + 24, cx + R - 24, cyf + R - 24], outline=FAINT + (a,), width=2)
                # ring of ticks turning around the coin
                for j in range(40):
                    ang = math.radians(j * 9 + 22 * (t - t0))
                    r0, r1 = R + 16, R + (30 if j % 5 == 0 else 23)
                    d.line([(cx + r0 * math.cos(ang), cyf + r0 * math.sin(ang)), (cx + r1 * math.cos(ang), cyf + r1 * math.sin(ang))],
                           fill=(cc if j % 5 == 0 else mix(BG, cc, 0.35)) + (a,), width=2)
                s = 1 + 0.25 * (1 - ease_back(prog(t, t0 + 0.3, t0 + 0.7)))
                d.text((cx, cyf), tick, font=F(BLACK, int((110 if len(tick) <= 3 else 84) * s)), fill=cc + (a,), anchor="mm")
            mid_text(d, cy + R + 90, name, typed(name, t, t0 + 0.5, 24), fn, DIM, cx)
            for k, (txt, tn, col) in enumerate(N):
                s = typed(txt, t, tn, 30)
                if s:
                    v = ease_out(prog(t, tn, tn + 0.35))
                    d.text((960 + 40 * (1 - v), 400 + k * 90 - (len(N) - 1) * 30), s, font=fn, fill=col + (int(255 * (0.3 + 0.7 * v)),), anchor="ls")
            return cam(im, t, dur, 480)
        return frame, [("boom", t0, 0.5)]
    return build


def k_chain(n=6, label=None, label_cue=None, broken=None, label_col="FG"):
    """Blocks linked one after the other; 'broken' cue cuts the chain in the middle and turns it red."""
    def build(dur, i):
        tl = trig(i, label_cue) if label else None
        tb = trig(i, broken) if broken else None
        if label:
            typed(label, 0, tl, 30, starts[i])
        BW, BH, SP, cy = 170, 130, 250, 460
        ac = _SD["acc"]
        X0 = W / 2 - (n - 1) * SP / 2
        step = min(0.4, max(0.15, dur * 0.4 / n))
        fn = F(MONO, 22)

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            bad = tb is not None and t >= tb
            for k in range(n):
                tk = 0.15 + k * step
                u = prog(t, tk, tk + 0.2)
                if u <= 0:
                    continue
                a = int(255 * u)
                x = X0 + k * SP
                dy = 18 * ease_out(prog(t, tb, tb + 0.3)) if bad and k >= n // 2 else 0
                dy += -22 * (1 - ease_back(u)) + 4 * math.sin(t * 2.2 + k * 0.9)     # drops into place, then bobs
                col = ERR if bad and k >= n // 2 else ac
                if k:
                    xa, xb = x - SP + BW / 2, x - BW / 2
                    if bad and k == n // 2:
                        d.line([(xa, cy), (xa + 22, cy)], fill=ERR + (a,), width=4)
                        d.line([(xb - 22, cy + dy), (xb, cy + dy)], fill=ERR + (a,), width=4)
                    else:
                        d.line([(xa, cy + (dy if k > n // 2 else 0)), (xb, cy + dy)], fill=col + (a,), width=4)
                d.rectangle([x - BW / 2, cy - BH / 2 + dy, x + BW / 2, cy + BH / 2 + dy], outline=col + (a,), width=3)
                d.text((x - BW / 2 + 16, cy - BH / 2 + 34 + dy), f"#{k + 1}", font=fn, fill=DIM + (a,), anchor="ls")
                for r in range(3):
                    yy = cy - 4 + r * 22 + dy
                    d.line([(x - BW / 2 + 16, yy), (x + BW / 2 - 16 - (50 if r == 2 else 0), yy)], fill=FAINT + (a,), width=6)
            # a pulse runs along the links once the chain is built (it stops at the break)
            t_built = 0.15 + n * step
            if t >= t_built:
                last = n // 2 - 1 if bad else n - 1
                pos = ((t - t_built) * 1.6) % (last + 0.6)
                if pos <= last:
                    px = X0 + pos * SP
                    k_ = int(pos)
                    py = cy + 4 * math.sin(t * 2.2 + k_ * 0.9)
                    d.ellipse([px - 16, py - 16, px + 16, py + 16], fill=ac + (60,))
                    d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=FG)
            if label:
                mid_text(d, 760, label, typed(label, t, tl, 30), F(MONO, 38), COLS[label_col])
            return cam(im, t, dur, 480)
        ev = [("tick", 0.15 + k * step, 0.4) for k in range(n)] + ([("glitch", tb, 0.6)] if tb is not None else [])
        return frame, ev
    return build


def k_cols(items, title=None, title_cue=0.2):
    """Vertical columns: (value on top, label below, fraction, colour, cue)."""
    def build(dur, i):
        R = [(top, bot, fr, accent(COLS[col]), trig(i, cue)) for top, bot, fr, col, cue in items]
        tt = trig(i, title_cue) if title else None
        if title:
            typed(title, 0, tt, 30, starts[i])
        n, SP, CW, BASE, HM = len(R), 220, 120, 740, 400
        X0 = W / 2 - (n - 1) * SP / 2

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            d.line([(X0 - CW, BASE), (X0 + (n - 1) * SP + CW, BASE)], fill=FAINT, width=2)
            for k, (top, bot, fr, col, t0) in enumerate(R):
                g = ease_out(prog(t, t0, t0 + 0.5))
                if g <= 0:
                    continue
                x, h = X0 + k * SP, max(4, HM * fr * g)
                d.rectangle([x - CW / 2, BASE - h, x + CW / 2, BASE], fill=col)
                d.text((x, BASE - h - 22), count_text(top, g) if "." in top or float(top) >= 3 else top, font=F(MONOB, 34), fill=col, anchor="ms")
                d.text((x, BASE + 50), bot, font=F(MONO, 28), fill=DIM, anchor="ms")
            if title:
                mid_text(d, 250, title, typed(title, t, tt, 30), F(MONO, 34), DIM)
            return cam(im, t, dur, 500)
        return frame, [("boom", t0, 0.3) for *_, t0 in R]
    return build


def k_tickers(names, die=None, keep=(), label=None, label_cue=None, cols=6):
    """Wall of tickers fading in; at 'die', all but 'keep' go dark and get struck through."""
    def build(dur, i):
        td = trig(i, die) if die else None
        tl = trig(i, label_cue) if label else None
        if label:
            typed(label, 0, tl, 30, starts[i])
        n = len(names)
        rows = -(-n // cols)
        SX, SY = 250, 90
        X0, Y0 = W / 2 - (cols - 1) * SX / 2, 450 - (rows - 1) * SY / 2
        order = list(np.random.default_rng(i).permutation(n))
        gap = min(0.12, dur * 0.4 / n)
        app = {k: 0.15 + r * gap for r, k in enumerate(order)}
        f = F(MONO, 34)

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            for k, nm in enumerate(names):
                a = prog(t, app[k], app[k] + 0.2)
                if a <= 0:
                    continue
                row = k // cols
                x = X0 + (k % cols) * SX + (1 if row % 2 else -1) * 9 * t
                y = Y0 + row * SY - 7 * t
                u = prog(t, td + order.index(k) * 0.02, td + order.index(k) * 0.02 + 0.3) if td is not None and nm not in keep else 0
                fl_ = u == 0 and (int(t * 10) + k * 7) % 31 == 0
                tint = mix(FG, CAT_COL[sum(map(ord, nm)) % 10], 0.6)
                d.text((x + (5 if fl_ else 0), y), nm, font=f, fill=(DIM if fl_ else mix(tint, FAINT, u)) + (int(255 * a),), anchor="mm")
                if u > 0:
                    w = d.textlength(nm, font=f) + 16
                    d.line([(x - w / 2, y), (x - w / 2 + w * u, y)], fill=ERR, width=3)
            if label:
                mid_text(d, 800, label, typed(label, t, tl, 30), F(MONO, 36), DIM)
            return cam(im, t, dur, 480)
        ev = [("tick", app[k], 0.3) for k in order[:16]] + ([("glitch", td, 0.5)] if td is not None else [])
        return frame, ev
    return build


def k_eu(center, cue=0.2, label=None, label_cue=None, center_col="FG"):
    """Ring of 12 EU stars with a word in the middle."""
    def build(dur, i):
        t0 = trig(i, cue)
        tl = trig(i, label_cue) if label else None
        if label:
            typed(label, 0, tl, 30, starts[i])
        cx, cy, R = W / 2, 440, 230
        fc = F(BLACK, 110 if len(center) <= 5 else 80)

        def frame(t):
            _SD["glow"] = EU_BLUE
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            for k in range(12):
                u = prog(t, t0 + k * 0.05, t0 + k * 0.05 + 0.25)
                if u <= 0:
                    continue
                ang = math.radians(-90 + 30 * k + 7 * (t - t0))
                d.polygon(star_pts(cx + R * math.cos(ang), cy + R * math.sin(ang), 22 * ease_back(u)), fill=EU_YELLOW + (int(255 * u),))
            a = prog(t, t0 + 0.6, t0 + 0.8)
            if a > 0:
                sz = int((110 if len(center) <= 5 else 80) * (1.35 - 0.35 * ease_back(prog(t, t0 + 0.6, t0 + 0.95))))
                d.text((cx, cy), center, font=F(BLACK, sz), fill=COLS[center_col] + (int(255 * a),), anchor="mm")
            if label:
                mid_text(d, 800, label, typed(label, t, tl, 30), F(MONO, 36), FG)
            return cam(im, t, dur, 470)
        return frame, [("tick", t0 + k * 0.05, 0.3) for k in range(12)] + [("boom", t0 + 0.6, 0.5)]
    return build


def k_bundle(top_cue, post_cue):
    """Layer 2: transactions fly into a box on top of Ethereum, then one block drops onto the chain."""
    def build(dur, i):
        t1, t2 = trig(i, top_cue), trig(i, post_cue)
        rng = np.random.default_rng(i)
        span = max(0.6, t2 - t1 - 0.5)
        dots = sorted([(rng.uniform(0, 1), rng.uniform(-1, 1), t1 + 0.2 + rng.uniform(0, span)) for _ in range(44)], key=lambda q: q[2])
        bx, by, CY = W / 2, 300, 690
        ac = _SD["acc"]
        XS = [W / 2 + (k - 2.5) * 190 for k in range(6)]
        f, fs = F(MONO, 34), F(MONO, 26)

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            for k, x in enumerate(XS):
                if k:
                    d.line([(XS[k - 1] + 55, CY), (x - 55, CY)], fill=FG if k < 5 else FAINT, width=3)
                if k < 5:
                    d.rectangle([x - 55, CY - 40, x + 55, CY + 40], outline=FG, width=2)
                else:
                    d.rectangle([x - 55, CY - 40, x + 55, CY + 40], outline=FAINT, width=2)
            d.text((XS[0] - 55, CY + 90), "ETHEREUM  (layer 1)", font=fs, fill=DIM, anchor="ls")
            if t >= t1:
                a = int(255 * prog(t, t1, t1 + 0.3))
                d.rounded_rectangle([bx - 260, by - 65, bx + 260, by + 65], 12, outline=ac + (a,), width=3)
                d.text((bx, by + 12), "LAYER 2", font=f, fill=FG + (a,), anchor="ms")
                got = sum(1 for *_, ts in dots if t >= ts + 0.8)
                d.text((bx, by + 110), f"{got * 75:,} transactions bundled", font=fs, fill=DIM + (a,), anchor="ms")
            for side, yo, ts in dots:
                u = prog(t, ts, ts + 0.8)
                if 0 < u < 1:
                    sx, sy = (150 if side < 0.5 else W - 150), by + yo * 160
                    tx = bx - 262 if side < 0.5 else bx + 262
                    x, y = sx + (tx - sx) * ease_out(u), sy + (by - sy) * ease_out(u)
                    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=ac + (int(255 * (1 - 0.5 * u)),))
            if t >= t2:
                u = ease_out(prog(t, t2, t2 + 0.6))
                x, y = bx + (XS[5] - bx) * u, (by + 65) + (CY - by - 65) * u
                d.rectangle([x - 55, y - 40, x + 55, y + 40], fill=ac)
            return cam(im, t, dur, 480)
        return frame, [("tick", ts + 0.8, 0.15) for *_, ts in dots[::4]] + [("boom", t2 + 0.6, 0.6)]
    return build


def k_timeline(points):
    """Horizontal timeline: (date, label, cue or None, colour); points without a cue stay faint."""
    def build(dur, i):
        P = [(dt, lab, (trig(i, c) if c is not None else None), accent(COLS[col])) for dt, lab, c, col in points]
        for _, lab, tp, _ in P:
            if tp is not None:
                typed(lab, 0, tp, 30, starts[i])
        n, X0, X1, Y = len(P), 380, 1540, 500

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            d.line([(X0 - 80, Y), (X1 + 80, Y)], fill=FAINT, width=2)
            # the bright part of the line grows to the latest point reached
            xs_ = [X0 + k * (X1 - X0) / (n - 1) for k in range(n)]
            reach = X0 - 80
            for k, (_, _, tp, _) in enumerate(P):
                if tp is not None and t >= tp - 0.4:
                    reach = max(reach, (xs_[k - 1] if k else X0 - 80) + (xs_[k] - (xs_[k - 1] if k else X0 - 80)) * ease_out(prog(t, tp - 0.4, tp)))
            d.line([(X0 - 80, Y), (reach, Y)], fill=DIM, width=3)
            for k, (dt, lab, tp, col) in enumerate(P):
                x = X0 + k * (X1 - X0) / (n - 1)
                on = tp is not None and t >= tp
                if on:
                    rr = 13 + 46 * prog(t, tp, tp + 0.7)
                    d.ellipse([x - rr, Y - rr, x + rr, Y + rr], outline=col + (int(160 * (1 - prog(t, tp, tp + 0.7))),), width=3)
                    d.ellipse([x - 13, Y - 13, x + 13, Y + 13], fill=col)
                else:
                    d.ellipse([x - 13, Y - 13, x + 13, Y + 13], outline=FAINT, width=3)
                d.text((x, Y - 52), dt, font=F(MONOB, 34), fill=col if on else FAINT, anchor="ms")
                if on:
                    mid_text(d, Y + 84, lab, typed(lab, t, tp, 30), F(MONO, 28), col, x)
            return cam(im, t, dur, 500)
        return frame, [("tick", tp, 0.5) for *_, tp, _ in P if tp is not None]
    return build


def k_end(title):
    def build(dur, i):
        fk, ft = F(MONO, 26), F(LIGHT, 76)
        typed("next >", 0, 0.05, 30, starts[i])
        ph = Cv(None)
        ph.rect([240, 430, 1040, 880], None, r=6, outline=FAINT, width=2)
        ph.text((640, 665), "next video", MONO, 30, DIM, anchor="mm")
        ph.ellipse([1260, 460, 1650, 850], None, outline=FAINT, width=2)
        ph.text((1455, 655), "subscribe", MONO, 30, DIM, anchor="mm")
        ph = ph.out()

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            mid_text(d, 130, "next >", typed("next >", t, 0.05, 30), fk, DIM)
            letters(d, (W / 2, 250), title, ft, t, 0.2, step=0.025)
            comp(im, ph, 0, 0, prog(t, 1.0, 1.6))
            return cam(im, t, dur, 540, 0.02)
        return frame, [("boom", 0.0, 0.5)]
    return build


KINDS.update(chap=k_cchap, boxes=k_boxes, coin=k_coin, chain=k_chain, cols=k_cols, tickers=k_tickers, eu=k_eu,
             bundle=k_bundle, timeline=k_timeline, end=k_end)
# --------------------------------------------------------------------------- motion layer: more camera and text movement, same dark style
# Loaded after the scene files: redefines cam(), bigs(), term() and k_chart() so every scene picks up the extra motion.
ease_io = lambda u: u * u * (3 - 2 * u)
_SD.update(i=0, hits=(), settle=0.045)


def cam(im, t, dur, cy=500, z=0.035):
    """Push-in with a slow drift (its direction alternates from scene to scene), a settle right after the hard cut,
    and a punch-in with a short shake on each hit of the scene."""
    i = _SD["i"]
    u = clamp(t / max(dur, 0.1))
    zz = 1.035 + max(z, 0.035) * 1.7 * ease_io(u)
    zz += _SD["settle"] * (1 - ease_out(prog(t, 0, 0.45)))
    sx = sy = 0.0
    for at, g in _SD["hits"]:
        if at - 0.01 <= t < at + 0.55:
            g = min(g, 1.0)
            zz += 0.05 * g * prog(t, at, at + 0.05) * (1 - ease_out(prog(t, at + 0.05, at + 0.55)))
            if t < at + 0.18:
                k = int(t * 60)
                sx += ((k * 7919) % 13 - 6) * 1.3 * g
                sy += ((k * 104729) % 11 - 5) * 1.3 * g
    side = 1 if i % 2 else -1
    cx = W / 2 + side * 70 * (u - 0.5) + sx
    cyy = cy + ((i % 3) - 1) * 24 * (u - 0.5) + sy + 3 * math.sin(t * 0.9 + i)
    return camera(im, zz, cx, cyy)


_LAYERS = {}


def text_layer(txt, font, size, col):
    """Text pre-rendered on a transparent layer, with its offset from the (left, baseline) anchor point."""
    key = (txt, font, size, col)
    if key not in _LAYERS:
        f = F(font, size)
        x0, y0, x1, y1 = _tmp.textbbox((0, 0), txt, font=f, anchor="ls")
        lay = Image.new("RGBA", (int(x1 - x0) + 10, int(y1 - y0) + 10), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((5 - x0, 5 - y0), txt, font=f, fill=col + (255,), anchor="ls")
        _LAYERS[key] = (lay, x0 - 5, y0 - 5)
    return _LAYERS[key]


def rise(im, txt, font, size, col, x, y, t, t0, span=0.45, lift=0.0):
    """Centered text that slides up out of a mask line (its own baseline box), then keeps lifting slowly."""
    u = ease_out(prog(t, t0, t0 + span))
    if u <= 0:
        return
    lay, ox, oy = text_layer(txt, font, size, col)
    w = _tmp.textlength(txt, font=F(font, size))
    px, py = int(x - w / 2 + ox), int(y + oy - lift)
    dy = int((1 - u) * lay.height * 0.9)
    if lay.height - dy <= 0:
        return
    piece = lay.crop((0, 0, lay.width, lay.height - dy))
    if u < 1:
        piece = with_alpha(piece, 0.35 + 0.65 * u)
    im.paste(piece, (px, py + dy), piece)


_NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


def counts(txt):
    """Worth counting up: has a number of at least 3, or with decimals."""
    return any(float(m.replace(",", "")) >= 3 or "." in m for m in _NUM.findall(txt))


def count_text(txt, f):
    """txt with every number scaled by f (0..1), keeping its decimals and thousands separators."""
    def one(m):
        s = m.group(0)
        raw = s.replace(",", "")
        dec = len(raw.split(".")[1]) if "." in raw else 0
        v = float(raw) * f
        return f"{v:,.{dec}f}" if "," in s else f"{v:.{dec}f}"
    return _NUM.sub(one, txt)


def bigs(items, events=()):
    """Free layout: (text, cue, font, size, colour, x, y) items. Mono text is typed, numbers in the black font count up,
    the rest slides up out of a mask; everything then lifts slowly, each item at its own speed."""
    def build(dur, i):
        R = []
        for k, (txt, cue, font, size, col, x, y) in enumerate(items):
            t0 = trig(i, cue)
            if is_mono(font):
                typed(txt, 0, t0, 30, starts[i])
            col = accent(col) if font == BLACK else col
            R.append((k, txt, t0, F(font, size), font, size, col, x, y, font == BLACK and counts(txt)))

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            for k, txt, t0, f, font, size, col, x, y, cnt in R:
                if t < t0:
                    continue
                lift = (10 + 6 * k) * prog(t, t0, dur)
                if is_mono(font):
                    mid_text(d, y - lift, txt, typed(txt, t, t0, 30), f, col, x)
                elif cnt:
                    a = prog(t, t0, t0 + 0.15)
                    s = count_text(txt, ease_out(prog(t, t0, t0 + 0.9)))
                    d.text((x, y + 14 * (1 - a) - lift), s, font=f, fill=col + (int(255 * a),), anchor="ms")
                else:
                    rise(im, txt, font, size, col, x, y, t, t0, lift=lift)
            return cam(im, t, dur)
        return frame, [(n, trig(i, cue), g) for n, cue, g in events]
    return build


def term(rows, size=44, cps=28, cy=480):
    """Terminal block: each (text, cue, colour) row slides in from the left and is typed when its cue is said."""
    def build(dur, i):
        fm = F(MONO, size)
        R = [(txt, trig(i, cue), accent(col) if txt[:1] in ">+" else col) for txt, cue, col in rows]
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
                    u = ease_out(prog(t, t0, t0 + 0.35))
                    x = x0 - 36 * (1 - u)
                    y = y0 + k * lh
                    if u < 1:
                        d.rectangle([x - 18, y - size * 0.95, x - 12, y + size * 0.25], fill=col + (int(255 * (1 - u)),))
                    d.text((x, y), s, font=fm, fill=col + (int(255 * (0.3 + 0.7 * u)),), anchor="ls")
                    last = (s, y, x)
            if last:
                caret(d, last[2] + d.textlength(last[0], font=fm), last[1], t, size)
            return cam(im, t, dur, cy)
        return frame, []
    return build


def k_chart(path, note=None, note_cue=None, note_col="FG"):
    """Line chart drawn over time, with a glowing dot riding its tip; the note slides in from the right."""
    def build(dur, i):
        tn = trig(i, note_cue) if note else None
        X0, X1, Y0, Y1 = 340, 1300, 300, 760
        lo, hi = min(path), max(path)
        pad = (hi - lo) * 0.12 or 1
        lo, hi = lo - pad, hi + pad
        n = len(path) - 1
        pts = [(X0 + 30 + k * (X1 - X0 - 60) / n, Y1 - (v - lo) / (hi - lo) * (Y1 - Y0)) for k, v in enumerate(path)]
        t_end = max(1.4, min(dur * 0.75, (tn + 0.3) if tn else dur * 0.75))
        col = COLS.get(note_col, FG)
        lc = _SD["acc"]

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            for g in range(1, 4):
                gy = Y0 + g * (Y1 - Y0) / 4
                d.line([(X0, gy), (X1, gy)], fill=FAINT + (60,), width=1)
            d.line([(X0, Y0 - 20), (X0, Y1 + 20), (X1, Y1 + 20)], fill=FAINT, width=2)
            d.text((X1, Y1 + 60), "(illustration)", font=F(MONO, 22), fill=FAINT, anchor="rs")
            m = prog(t, 0.2, t_end) * n
            k = int(m)
            show = pts[: k + 1] + ([(pts[k][0] + (pts[k + 1][0] - pts[k][0]) * (m - k), pts[k][1] + (pts[k + 1][1] - pts[k][1]) * (m - k))] if k < n else [])
            if len(show) > 1:
                d.line(show, fill=lc, width=5, joint="curve")
            if t >= 0.2:
                tx, ty = show[-1]
                tip = col if (tn is not None and t >= tn) else lc
                r = 18 + 6 * math.sin(t * 6)
                d.ellipse([tx - r, ty - r, tx + r, ty + r], fill=tip + (40,))
                d.ellipse([tx - 8, ty - 8, tx + 8, ty + 8], fill=tip)
            if tn is not None and t >= tn:
                f = F(BLACK, 110) if len(note) <= 8 else F(MONO, 40)
                u = ease_out(prog(t, tn, tn + 0.3))
                d.text((1570 + 60 * (1 - u), 560), note, font=f, fill=col + (int(255 * u),), anchor="ms")
            return cam(im, t, dur, 520)
        return frame, ([("boom", tn, 0.6)] if tn is not None else [])
    return build


KINDS["chart"] = k_chart
# --------------------------------------------------------------------------- colour layer: one accent colour per box and a soft glow behind each scene
# Same edit, same black background: the accent of the current box colours the key element of each scene (big numbers,
# coins, chains, curves, prompts), and a faint glow of that colour sits behind the scene. Red stays for losses and scams.
CAT_COL = [(247, 147, 26), (130, 140, 255), (40, 210, 180), (0, 190, 255), (60, 200, 120), (243, 190, 50),
           (255, 80, 170), (170, 220, 60), (175, 110, 255), (255, 120, 80), ERR, (70, 110, 255)]
BRAND = (150, 120, 255)                       # intro and outro
COIN_COL = {"BTC": (247, 147, 26), "ETH": (130, 140, 255), "DOGE": (216, 180, 74), "BNB": (243, 186, 47),
            "XMR": (255, 102, 0), "ZEC": (244, 183, 40)}
EU_BLUE, EU_YELLOW = (40, 80, 230), (255, 204, 0)
_SD.update(acc=BRAND, glow=None)


class _Cols(dict):
    """COLS with an extra 'ACC' entry that always gives the accent of the scene being built."""
    def __getitem__(self, k):
        return _SD["acc"] if k == "ACC" else dict.__getitem__(self, k)

    def get(self, k, default=None):
        return _SD["acc"] if k == "ACC" else dict.get(self, k, default)


COLS = _Cols(COLS)
_GLOW = {}


def glow_bg(col, k=0.13):
    if (col, k) not in _GLOW:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        f = np.exp(-(((xx - W / 2) / 820) ** 2 + ((yy - H * 0.44) / 520) ** 2))
        img = np.array(BG, np.float32) + f[..., None] * np.array(col, np.float32) * k
        _GLOW[(col, k)] = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    return _GLOW[(col, k)]


def black():
    return glow_bg(_SD["glow"] or _SD["acc"]).copy()


def accent(col):
    """FG becomes the scene's accent; every other colour is kept."""
    return _SD["acc"] if col == FG else col


def caret(d, x, y, t, size):
    if t % 0.9 < 0.5:
        d.rectangle([x + 4, y - size * 0.8, x + 4 + size * 0.55, y + size * 0.15], fill=_SD["acc"])
# --------------------------------------------------------------------------- "Every ETF Explained": the 12 boxes and the extra scene kinds
CATS = ["INDEX", "COUNTRY & REGION", "SECTOR", "THEMATIC", "FACTOR", "DIVIDEND", "BONDS", "MONEY MARKET", "COMMODITIES",
        "LEVERAGED", "ACTIVE", "CRYPTO ETPs"]
COIN_COL["GOLD"] = (222, 180, 70)


def k_basket(label=None, label_cue=None, slice_cue=None, cols=10, rows=5):
    """An ETF as a basket: small squares (companies) drop into a box; at slice_cue each one gets a dot = your slice."""
    def build(dur, i):
        ac = _SD["acc"]
        tl = trig(i, label_cue) if label else None
        ts = trig(i, slice_cue) if slice_cue else None
        if label:
            typed(label, 0, tl, 30, starts[i])
        n, SZ, GAP = cols * rows, 40, 16
        BW, BH = cols * (SZ + GAP) + GAP, rows * (SZ + GAP) + GAP
        bx0, by0 = W / 2 - BW / 2, 470 - BH / 2
        order = list(np.random.default_rng(i).permutation(n))
        gap = min(0.05, dur * 0.35 / n)
        land = {k: 0.3 + r * gap for r, k in enumerate(order)}

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            a = int(255 * prog(t, 0.0, 0.3))
            d.rounded_rectangle([bx0 - 10, by0 - 10, bx0 + BW + 10, by0 + BH + 10], 14, outline=ac + (a,), width=4)
            d.text((bx0 - 10, by0 - 30), "1 ETF", font=F(MONOB, 28), fill=ac + (a,), anchor="ls")
            for k in range(n):
                u = prog(t, land[k], land[k] + 0.35)
                if u <= 0:
                    continue
                x = bx0 + GAP + (k % cols) * (SZ + GAP)
                y = by0 + GAP + (k // cols) * (SZ + GAP) - 220 * (1 - ease_out(u))
                d.rectangle([x, y, x + SZ, y + SZ], fill=FG + (int(255 * min(1, u * 2)),))
                if ts is not None and t >= ts + (k % cols) * 0.02:
                    v = ease_back(prog(t, ts + (k % cols) * 0.02, ts + (k % cols) * 0.02 + 0.3))
                    r = 9 * v
                    d.rectangle([x + SZ - 4 - 2 * r, y + 4, x + SZ - 4, y + 4 + 2 * r], fill=ac)
            if label:
                mid_text(d, 800, label, typed(label, t, tl, 30), F(MONO, 36), FG)
            return cam(im, t, dur, 480)
        ev = [("tick", land[k], 0.15) for k in order[::4]] + ([("boom", ts, 0.5)] if ts is not None else [])
        return frame, ev
    return build


def k_name(parts, title_cue=0.2):
    """ETF name decoder: the full name typed, then each part underlined with its meaning. parts = (text, meaning, cue)."""
    def build(dur, i):
        ac = _SD["acc"]
        full = " ".join(p for p, _, _ in parts)
        t0 = trig(i, title_cue)
        typed(full, 0, t0, 40, starts[i])
        fm, fl = F(MONO, 40), F(MONO, 26)
        x0 = (W - _tmp.textlength(full, font=fm)) / 2
        P, x, row = [], x0, 0
        for txt, meaning, cue in parts:
            w = _tmp.textlength(txt, font=fm)
            P.append((x, w, meaning, trig(i, cue) if cue is not None else None, row))
            row += cue is not None                     # alternate rows among the parts that get a meaning, so neighbours never collide
            x += w + _tmp.textlength(" ", font=fm)
        for _, _, meaning, tc, _ in P:
            if tc is not None:
                typed(meaning, 0, tc, 30, starts[i])

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            d.text((x0, 430), typed(full, t, t0, 40), font=fm, fill=FG, anchor="ls")
            for x, w, meaning, tc, k in P:
                if tc is None or t < tc:
                    continue
                u = ease_out(prog(t, tc, tc + 0.3))
                d.rectangle([x, 446, x + w * u, 452], fill=ac)
                ly = 520 if k % 2 == 0 else 590
                d.line([(x + w / 2, 456), (x + w / 2, ly - 30)], fill=ac + (int(160 * u),), width=2)
                mid_text(d, ly, meaning, typed(meaning, t, tc, 30), fl, DIM, x + w / 2)
            d.text((W / 2, 760), "(example, not a recommendation)", font=F(MONO, 22), fill=FAINT, anchor="ms")
            return cam(im, t, dur, 480, 0.02)
        return frame, [("tick", tc, 0.4) for *_, tc, _ in P if tc is not None]
    return build


def k_lines(series, note=None, note_cue=None, note_col="ERR"):
    """Several lines on one chart: series = (label, values, colour). Used for the 2x leveraged example."""
    def build(dur, i):
        tn = trig(i, note_cue) if note else None
        X0, X1, Y0, Y1 = 340, 1300, 300, 760
        allv = [v for _, vals, _ in series for v in vals]
        lo, hi = min(allv), max(allv)
        pad = (hi - lo) * 0.15 or 1
        lo, hi = lo - pad, hi + pad
        S_ = []
        for lab, vals, col in series:
            n = len(vals) - 1
            pts = [(X0 + 40 + k * (X1 - X0 - 80) / n, Y1 - (v - lo) / (hi - lo) * (Y1 - Y0)) for k, v in enumerate(vals)]
            S_.append((lab, pts, accent(COLS[col])))
        y100 = Y1 - (100 - lo) / (hi - lo) * (Y1 - Y0)
        col_n = COLS.get(note_col, ERR)

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            d.line([(X0, Y0 - 20), (X0, Y1 + 20), (X1, Y1 + 20)], fill=FAINT, width=2)
            for xx in range(int(X0), int(X1), 24):
                d.line([(xx, y100), (xx + 12, y100)], fill=FAINT, width=2)
            d.text((X0 - 14, y100 + 8), "100", font=F(MONO, 22), fill=DIM, anchor="rs")
            for j, (lab, pts, col) in enumerate(S_):
                n = len(pts) - 1
                m = prog(t, 0.2 + j * 0.3, max(1.6, dur * 0.55) + j * 0.3) * n
                k = int(m)
                show = pts[: k + 1] + ([(pts[k][0] + (pts[k + 1][0] - pts[k][0]) * (m - k), pts[k][1] + (pts[k + 1][1] - pts[k][1]) * (m - k))] if k < n else [])
                if len(show) > 1:
                    d.line(show, fill=col, width=5, joint="curve")
                    tx, ty = show[-1]
                    d.ellipse([tx - 7, ty - 7, tx + 7, ty + 7], fill=col)
                    if k >= n:
                        d.text((tx + 18, ty + 9), lab, font=F(MONOB, 28), fill=col, anchor="ls")
            if tn is not None and t >= tn:
                u = ease_out(prog(t, tn, tn + 0.3))
                f = F(BLACK, 110) if len(note) <= 8 else F(MONO, 40)
                d.text((1600 + 60 * (1 - u), 560), note, font=f, fill=col_n + (int(255 * u),), anchor="ms")
            return cam(im, t, dur, 520)
        return frame, ([("boom", tn, 0.6)] if tn is not None else [])
    return build


KINDS.update(basket=k_basket, name=k_name, lines=k_lines)
# --------------------------------------------------------------------------- any number of boxes: chapter card and box grid sized to len(CATS)
BOX_WORD = "BOX"                  # word on the chapter cards ("BOX 03 / 10"); a video's conf can change it (e.g. "MISTAKE")
def k_cchap(n, title):
    """Chapter card: progress row of len(CATS) squares, 'BOX 03 / 10', title, the number drifting large behind."""
    def build(dur, i):
        NB = len(CATS)
        fk, ft = F(MONO, 30), F(LIGHT, 104)
        lab = f"{BOX_WORD} {n:02d} / {NB}"
        typed(lab, 0, 0.1, 20, starts[i])
        fbig = F(BLACK, 620)
        ac = CAT_COL[n - 1]

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            d.text((W / 2 + 140 - 160 * t / dur, 800), f"{n:02d}", font=fbig, fill=mix(BG, ac, 0.16), anchor="ms")
            ys = 120 + 840 * ease_out(prog(t, 0.0, 0.6))
            if t < 0.6:
                d.rectangle([0, ys - 2, W, ys + 2], fill=FG + (int(90 * (1 - t / 0.6)),))
            x0 = W / 2 - NB * 40 / 2 + 7
            for k in range(NB):
                x = x0 + k * 40
                a = int(255 * prog(t, 0.05 + k * 0.03, 0.2 + k * 0.03))
                if k < n - 1:
                    d.rectangle([x, 318, x + 26, 344], fill=CAT_COL[k] + (int(a * 0.75),))
                elif k == n - 1:
                    d.rectangle([x, 318, x + 26, 344], fill=(FG if t % 0.8 < 0.4 and t < 1.6 else ac) + (a,))
                else:
                    d.rectangle([x, 318, x + 26, 344], outline=FAINT + (a,), width=2)
            mid_text(d, 450, lab, typed(lab, t, 0.1, 20), fk, DIM)
            letters(d, (W / 2, 590), title, ft, t, 0.35, step=0.035)
            w = 520 * ease_out(prog(t, 0.3, 1.0))
            d.line([(W / 2 - w / 2, 650), (W / 2 + w / 2, 650)], fill=ac + (200,), width=3)
            return cam(im, t, dur, 470, 0.03)
        return frame, [("boom", 0.0, 0.45)]
    return build


def k_boxes(hi=(), cue=0.2, label=None, label_cue=None):
    """The boxes in a grid (4 x 3 for 12, 5 x 2 for 10...); hi = indices to light up, or 'all'."""
    def build(dur, i):
        NB = len(CATS)
        NC = 4 if NB in (8, 12) else 5 if NB in (10, 15) else 3 if NB in (6, 9) else 4
        NR = -(-NB // NC)
        t0 = trig(i, cue)
        tl = trig(i, label_cue) if label else None
        if label:
            typed(label, 0, tl, 30, starts[i])
        BW, BH = (330, 112) if NC <= 4 else (300, 112)
        SX, SY = BW + 30, 140
        X0, Y0 = W / 2 - (NC * SX - 30) / 2, 470 - (NR * SY - 28) / 2
        lit = set(range(NB)) if hi == "all" or not hi else set(hi)
        fl, fn = F(MONO, 26 if NC <= 4 else 24), F(MONO, 20)

        def frame(t):
            im = black()
            d = ImageDraw.Draw(im, "RGBA")
            for k in range(NB):
                u = prog(t, t0 + k * 0.09, t0 + k * 0.09 + 0.25)
                if u <= 0:
                    continue
                a = int(255 * u)
                x, y = X0 + (k % NC) * SX, Y0 + (k // NC) * SY
                on = k in lit
                col = CAT_COL[k] if on else (78, 78, 86)
                y += 14 * (1 - ease_out(u))
                d.rectangle([x, y, x + BW, y + BH], outline=col + (a,), width=3 if on and hi else 2)
                if on and hi and hi != "all":
                    p = 0.5 + 0.5 * math.sin(t * 4 + k)
                    d.rectangle([x - 7, y - 7, x + BW + 7, y + BH + 7], outline=col + (int(90 * p * u),), width=2)
                d.text((x + 16, y + 30), f"{k + 1:02d}", font=fn, fill=(DIM if on else FAINT) + (a,), anchor="ls")
                d.text((x + BW / 2, y + BH / 2 + 12), CATS[k], font=fl, fill=col + (a,), anchor="mm")
            if t >= t0:
                ys = Y0 - 20 + ((t - t0) * 0.45 % 1) * (NR * SY - 28 + 40)
                d.rectangle([X0 - 30, ys - 1, X0 + NC * SX, ys + 1], fill=FG + (40,))
            if label:
                mid_text(d, 800, label, typed(label, t, tl, 30), F(MONO, 36), FG)
            return cam(im, t, dur, 500)
        return frame, [("tick", t0 + k * 0.09, 0.35) for k in range(NB)]
    return build


KINDS.update(chap=k_cchap, boxes=k_boxes)
# --------------------------------------------------------------------------- "Every Investing Mistake Explained": the 12 boxes
CATS = ["WAITING TO START", "NO SAFETY CUSHION", "MONEY NEEDED SOON", "HIGH FEES", "TIMING THE MARKET", "PANIC SELLING",
        "CHASING WINNERS", "ONE BIG BET", "TRADING TOO MUCH", "FOLLOWING HYPE", "NOT UNDERSTANDING", "WRONG ACCOUNT"]
# --------------------------------------------------------------------------- this video's output name, chapter-card word and the silences before its key numbers
OUT_NAME = "mistakes"
BOX_WORD = "MISTAKE"
DIP_AT = [("about 1.2 percentage points", "1.2"), ("more than €60,000", "€60,000"), ("only 2.2% stayed", "2.2%")]
# --------------------------------------------------------------------------- overlays: disclaimer, terminal-style subscribe reminder
E = os.path.join(D, OUT_NAME)
os.makedirs(E, exist_ok=True)
K = len(LINES)
NF = sum(frames)
SCN = [l["scene"] for l in LINES]
NFA_OFF = starts[2]
CHN, c_ = [], 0
for l in LINES:
    if isinstance(l["scene"], tuple) and l["scene"][0] == "chap":
        c_ += 1
    CHN.append(0 if l.get("hide") else c_)
SUB_T0 = starts[CHN.index(4) + 1] + 1.0      # terminal-style subscribe reminder, early in box 4
f_nfa, f_sub = F(MONO, 18), F(MONO, 26)


def scene_ctx(i):
    """Per-scene state read by the scene builders and frames: index, duration, accent colour of its box."""
    _SD.update(i=i, dur=frames[i] / FPS, acc=CAT_COL[CHN[i] - 1] if CHN[i] else BRAND, glow=None)


_drng = np.random.default_rng(31)
DUST = [(_drng.uniform(0, W), _drng.uniform(0, H), _drng.uniform(4, 16), _drng.uniform(-6, 6), _drng.uniform(0.8, 2.4), _drng.uniform(0, 6.3))
        for _ in range(46)]


def overlays(im, t):
    d = ImageDraw.Draw(im, "RGBA")
    for x0, y0, vy, vx, r, ph in DUST:              # dust drifting in front of the scene (parallax with the camera)
        x, y = (x0 + vx * t) % W, (y0 - vy * t) % H
        d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 200, 210, int(38 + 28 * math.sin(t * 1.3 + ph))))
    if t < NFA_OFF:
        a = min(prog(t, 0.3, 0.7), 1 - prog(t, NFA_OFF - 0.5, NFA_OFF))
        d.text((44, 56), "not financial advice · education only", font=f_nfa, fill=DIM + (int(255 * a),), anchor="ls")
    i_ = max(j for j in range(K) if starts[j] <= t + 1e-6)
    n_ = CHN[i_]
    if n_ and not (isinstance(SCN[i_], tuple) and SCN[i_][0] == "chap"):
        a = min(prog(t - starts[i_], 0, 0.3), 1.0) if i_ and CHN[i_ - 1] != n_ else 1.0
        d.rectangle([44, 50, 60, 66], fill=CAT_COL[n_ - 1] + (int(255 * a),))
        d.text((72, 66), f"{n_:02d}/{len(CATS)} · {CATS[n_ - 1]}", font=F(MONO, 22), fill=DIM + (int(255 * a),), anchor="ls")
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

    fns, events, HITS = [], [], []
    for i, l in enumerate(LINES):
        scene_ctx(i)
        fn, ev = scene_of(l)(frames[i] / FPS, i)
        fns.append(fn)
        HITS.append([(tt, g) for n_, tt, g in ev if n_ == "boom"])
        events += [(n, starts[i] + tt, g) for n, tt, g in ev]
    # glitch cuts into each chapter card and out of it; plain hard cuts elsewhere
    is_chap = [isinstance(s_, tuple) and s_[0] == "chap" for s_ in SCN]
    cut_g = [starts[j] for j in range(1, K) if is_chap[j] or is_chap[j - 1] or SCN[j] == "end"]
    G = [(at, 0.32, g) for n, at, g in events if n == "glitch"] + [(c - 0.05, 0.12, 0.6) for c in cut_g]
    G += [(starts[j] - 0.03, 0.08, 0.3) for j in range(1, K) if starts[j] not in cut_g]     # a flick of glitch on every other cut
    # SAMPLE="a:b" renders only lines a..b-1 (to review the edit quickly)
    SAMPLE = os.environ.get("SAMPLE")
    la, lb = (int(v) for v in SAMPLE.split(":")) if SAMPLE else (0, K)
    K0, K1 = round(starts[la] * FPS), (round(starts[lb] * FPS) if lb < K else NF)

    vid = os.path.join(E, "video.mp4")
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    for k in range(K0, K1):
        t = k / FPS
        i = max(j for j in range(K) if starts[j] <= t + 1e-6)
        scene_ctx(i)
        _SD.update(hits=HITS[i], settle=0.14 if is_chap[i] else 0.045)
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
    CHORDS[3] = (48, 52, 55, 60, 64)                # C major for the "it worked" part
    PART, p = [], 0
    for s_ in SCN:
        if isinstance(s_, tuple) and s_[0] == "chap":
            p += 1
        PART.append(p % len(CHORDS))
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
    jl = lambda txt: next(j for j, l in enumerate(LINES) if txt in l["sub"])
    DIPS = [(when(jl(phrase), word) - 0.3, 0.3) for phrase, word in DIP_AT]
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
    final = os.path.join(O, OUT_NAME + ("_sample.mp4" if SAMPLE else "_dark_16x9.mp4"))
    T0, T1 = K0 / FPS, K1 / FPS
    run(["ffmpeg", "-y", "-i", vid, "-ss", f"{T0:.3f}", "-t", f"{T1 - T0:.3f}", "-i", mix, "-vf",
         f"setpts=PTS+{T0:.3f}/TB,ass={subs}:fontsdir={FD},setpts=PTS-STARTPTS,fade=t=out:st={T1 - T0 - 0.8:.2f}:d=0.8",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest", final])
    print(f"done total={TOTAL:.2f}s")
