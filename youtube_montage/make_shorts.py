"""Vertical Shorts (1080x1920) cut from the finished long videos: a hook at the top, the clip in the middle,
big karaoke captions below it, and a footer pointing to the full video. Usage: python3 make_shorts.py [name ...]"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

from shorts_seg import cues, segment

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "shorts")
os.makedirs(OUT, exist_ok=True)
INTER = "/usr/share/fonts/opentype/inter/"
BLACKF, SEMI = INTER + "InterDisplay-Black.otf", INTER + "Inter-SemiBold.otf"
W, H = 1080, 1920
BG, WHITE, GREY, ORANGE, INK = (10, 10, 10), (245, 245, 242), (130, 130, 130), (247, 147, 26), (17, 17, 17)
VY = 640                     # top of the clip (the 16:9 frame, cropped to 1920x960 and scaled to 1080x540)
TIKTOK = "--tiktok" in sys.argv          # TikTok version: points to the YouTube channel, with an end card
LEAD, TAIL = 0.35, (2.4 if TIKTOK else 1.0)

SRC = {"crypto": ("out/crypto_dark_16x9.mp4", "crypto/mix.wav", "crypto/subs.ass", "Every Crypto Explained in 12 Minutes"),
       "etf": ("etf/video.mp4", "etf/mix.wav", "etf/subs.ass", "Every ETF Explained in 11 Minutes"),
       "pov2": ("pov2/video.mp4", "pov2/mix.wav", "pov2/subs.ass", "POV: You're 25 and Invest €200 a Month")}
SHORTS = [
    ("crypto_1_terra", "crypto", "But not every stablecoin", "lost their savings", ("$40 billion", "gone in days.")),
    ("crypto_2_ftx", "crypto", "That link can be deadly", "only as safe as that company", ("This exchange", "vanished in days.")),
    ("crypto_3_21m", "crypto", "And here's the key rule", "recovered each time", ("Only 21 million.", "Ever.")),
    ("etf_1_voo", "etf", "In Europe, most ETFs follow", "won't sell them to you", ("Why Europeans", "can't buy VOO")),
    ("etf_2_fees", "etf", "Some S&P 500 ETFs cost", "more than €60,000", ("0.03% vs 1.8%", "= €60,000+")),
    ("etf_3_leveraged", "etf", "The key word is daily", "not for holding", ("+10%, then −10%…", "and you lost 4%?")),
    ("pov_1_hook", "pov2", "POV: you're 25", "nobody talks about", ("POV: you're 25", "€200 a month")),
    ("pov_2_crash", "pov2", "Then the news changes", "locked in their loss", ("Your €14,300", "becomes €9,450")),
    ("pov_3_fees", "pov2", "At a family dinner", "every year counts", ("Her bank's fee", "cost €69,000")),
]


def font(path, size):
    return ImageFont.truetype(path, size)


def overlay(hook, title, path):
    """Static layer: black background with a hole for the clip, the hook on top, the footer at the bottom."""
    im = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([0, VY, W, VY + 540], fill=(0, 0, 0, 0))
    l1, l2 = hook
    f1 = font(BLACKF, 96)
    while d.textlength(max(l1, l2, key=len), font=f1) > W - 120:
        f1 = font(BLACKF, f1.size - 4)
    d.text((W / 2, 330), l1, font=f1, fill=WHITE, anchor="ms")
    x0, y0, x1, y1 = d.textbbox((W / 2, 470), l2, font=f1, anchor="ms")
    d.rectangle([x0 - 22, y0 - 16, x1 + 22, y1 + 18], fill=ORANGE)
    d.text((W / 2, 470), l2, font=f1, fill=INK, anchor="ms")
    # under the clip: the 'eu.' mark and where the full video is (kept out of the bottom area that YouTube's buttons cover)
    fe = font(BLACKF, 30)
    d.rounded_rectangle([60, VY + 556, 116, VY + 612], radius=12, fill=(28, 28, 28))
    ex1 = d.textbbox((70, VY + 597), "eu", font=fe, anchor="ls")[2]
    d.text((70, VY + 597), "eu", font=fe, fill=WHITE, anchor="ls")
    d.rectangle([ex1 + 2, VY + 589, ex1 + 9, VY + 596], fill=ORANGE)
    ft = font(SEMI, 30)
    t = "full video on YouTube · Euro Unboxed" if TIKTOK else "full video: " + title
    full = t
    while d.textlength(t + "…", font=ft) > W - 200:
        t = t[:-1]
    d.text((132, VY + 597), t if t == full else t.rstrip() + "…", font=ft, fill=GREY, anchor="ls")
    im.save(path)


def ass_time(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def captions(ass_src, t0, t1, path):
    """The long video's karaoke cues for [t0, t1], shifted to the Short's clock, restyled big under the clip."""
    ev = []
    for ln in open(ass_src, encoding="utf-8"):
        if not ln.startswith("Dialogue:"):
            continue
        p = ln.rstrip("\n").split(",", 9)
        a, b = cues.__globals__["secs"](p[1]), cues.__globals__["secs"](p[2])
        if a < t0 - 0.05 or a > t1:
            continue
        txt = p[9].replace("{\\fad(120,80)}", "")
        ev.append(f"Dialogue: 0,{ass_time(a - t0 + LEAD)},{ass_time(min(b, t1 + 0.3) - t0 + LEAD)},Big,,0,0,0,,{{\\fad(80,60)}}{txt}")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Big,Inter Display Black,70,&H00F2F5F5,&H00808080,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,8,90,90,{VY + 540 + 140},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    if TIKTOK:                                     # end card: where to find the full video
        e0 = t1 - t0 + LEAD + 0.15
        ev.append(f"Dialogue: 1,{ass_time(e0)},{ass_time(e0 + TAIL)},Big,,0,0,0,,{{\\fad(150,0)\\c&H001A93F7&}}Full video on YouTube\\N{{\\c&H00F2F5F5&}}Euro Unboxed")
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")


def make(name, vid, start, end, hook):
    video, mix, subs, title = SRC[vid]
    t0, t1, _ = segment(os.path.join(D, subs), start, end)
    a, dur = t0 - LEAD, (t1 - t0) + LEAD + TAIL
    ov, ass = os.path.join(OUT, f"{name}_overlay.png"), os.path.join(OUT, f"{name}.ass")
    overlay(hook, title, ov)
    captions(os.path.join(D, subs), t0, t1, ass)
    fc = (f"[0:v]crop=1920:960:0:0,scale={W}:540,pad={W}:{H}:0:{VY}:black[v];[v][2:v]overlay=0:0[o];"
          f"[o]ass={ass}:fontsdir={INTER},fade=t=in:st=0:d=0.25,fade=t=out:st={dur - 0.5:.2f}:d=0.5[vout];"
          f"[1:a]afade=t=in:st=0:d=0.25,afade=t=out:st={dur - 0.7:.2f}:d=0.7[aout]")
    out = os.path.join(OUT, f"short_{'tiktok_' if TIKTOK else ''}{name}.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.3f}", "-t", f"{dur:.3f}", "-i", os.path.join(D, video),
                    "-ss", f"{a:.3f}", "-t", f"{dur:.3f}", "-i", os.path.join(D, mix), "-i", ov, "-filter_complex", fc,
                    "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
                    "-r", "30", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
    print(f"{name}: {dur:.1f}s, {os.path.getsize(out) / 2**20:.1f} MiB", flush=True)


if __name__ == "__main__":
    want = set(a for a in sys.argv[1:] if not a.startswith("--"))
    for s in SHORTS:
        if not want or s[0] in want or s[1] in want:
            make(*s)
