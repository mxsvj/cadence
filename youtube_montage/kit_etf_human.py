"""Kit for the human-pass ETF video: same text as the ETF kit, chapters re-timed (the pauses changed), SRT from its captions."""
import os, re, subprocess
D = os.path.dirname(os.path.abspath(__file__))
os.environ["LONG_PREVIEW"] = "1"
ns = {"__file__": os.path.join(D, "build_etf_h.py")}
exec(open(os.path.join(D, "build_etf_h.py")).read(), ns)
LINES, starts = ns["LINES"], ns["starts"]
NAMES = ["Index ETFs", "Country & region ETFs", "Sector ETFs", "Thematic ETFs", "Factor ETFs (smart beta)", "Dividend ETFs",
         "Bond ETFs", "Money market ETFs", "Commodities (gold ETCs)", "Leveraged & inverse", "Active ETFs", "Crypto ETPs"]
mmss = lambda t: f"{int(t // 60)}:{int(t % 60):02d}"
ch = ["0:00 Intro"]
for i, l in enumerate(LINES):
    s = l["scene"]
    if isinstance(s, tuple) and s[0] == "chap":
        ch.append(f"{mmss(starts[i])} {s[1]:02d} · {NAMES[s[1] - 1]}")
out_i = next(i for i, l in enumerate(LINES) if l.get("hide"))
ch.append(f"{mmss(starts[out_i])} How to read an ETF name")
src = open("/home/user/cadence/youtube_montage/scripts/every_etf_youtube_upload.txt").read()
a = src.index("CHAPTERS\n") + len("CHAPTERS\n")
b = src.index("\n\n", a)
txt = src[:a] + "\n".join(ch) + src[b:]
txt = txt.replace("every_etf_subtitles_en.srt", "every_etf_human_subtitles_en.srt")
os.makedirs("kit_etf_h", exist_ok=True)
open("kit_etf_h/every_etf_human_youtube_upload.txt", "w").write(txt)
subprocess.run(["python3", "ass2srt.py", "h_etf/subs.ass", "kit_etf_h/every_etf_human_subtitles_en.srt"], check=True)
print("\n".join(ch))
