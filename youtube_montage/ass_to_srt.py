"""Convert the karaoke captions (subs.ass) of a finished video into a plain SRT file for YouTube."""
import re, sys
src, dst = sys.argv[1], sys.argv[2]


def secs(s):
    h, m, x = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(x)


def stamp(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


ev = []
for ln in open(src, encoding="utf-8"):
    if not ln.startswith("Dialogue:"):
        continue
    parts = ln.rstrip("\n").split(",", 9)
    a, b, txt = secs(parts[1]), secs(parts[2]) - 0.05, re.sub(r"\{[^}]*\}", "", parts[9]).replace("\\N", " ").strip()
    if txt:
        ev.append((a, b, txt))
ev.sort()
ev = [(a, min(b, ev[k + 1][0] - 0.02) if k + 1 < len(ev) else b, txt) for k, (a, b, txt) in enumerate(ev)]   # no overlapping cues
with open(dst, "w", encoding="utf-8") as f:
    for k, (a, b, txt) in enumerate(ev, 1):
        f.write(f"{k}\n{stamp(a)} --> {stamp(b)}\n{txt}\n\n")
print(len(ev), "cues")
