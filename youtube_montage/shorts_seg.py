"""Find a Short's time range in a finished video's karaoke captions: from the cue containing START to the one containing END."""
import re


def secs(s):
    h, m, x = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(x)


def cues(path):
    out = []
    for ln in open(path, encoding="utf-8"):
        if ln.startswith("Dialogue:"):
            p = ln.rstrip("\n").split(",", 9)
            out.append((secs(p[1]), secs(p[2]), re.sub(r"\{[^}]*\}", "", p[9])))
    return out


def segment(path, start, end):
    C = cues(path)
    i0 = next(k for k, c in enumerate(C) if start in c[2])
    i1 = next(k for k in range(i0, len(C)) if end in C[k][2])
    return C[i0][0], C[i1][1], " ".join(c[2] for c in C[i0:i1 + 1])
