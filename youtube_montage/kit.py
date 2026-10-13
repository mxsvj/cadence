"""Upload kit and script document for a boxes video: python3 kit.py <name> <repo scripts dir>
Chapter times come from the build itself (the voice audio is cached, so this runs in seconds)."""
import os
import sys

D = os.path.dirname(os.path.abspath(__file__))
NAME, OUTDIR = sys.argv[1], sys.argv[2]
sys.path.insert(0, D)
from kit_meta import ADVICE, META, SETTINGS  # noqa: E402

m = META[NAME]
os.environ["LONG_PREVIEW"] = "1"
ns = {"__file__": os.path.join(D, f"build_{NAME}.py")}
exec(open(os.path.join(D, f"build_{NAME}.py")).read(), ns)
LINES, starts, TOTAL = ns["LINES"], ns["starts"], ns["TOTAL"]
mmss = lambda t: f"{int(t // 60)}:{int(t % 60):02d}"
ch = ["0:00 Intro"]
for i, l in enumerate(LINES):
    s = l["scene"]
    if isinstance(s, tuple) and s[0] == "chap":
        ch.append(f"{mmss(starts[i])} {s[1]:02d} · {s[2].rstrip('.')}")
oi = next((i for i, l in enumerate(LINES) if l.get("hide")), None)
if oi is not None:
    ch.append(f"{mmss(starts[oi])} {m['outro']}")
srt = f"{m['slug']}_subtitles_en.srt"
src = "\n".join(f"{lab}: {url}" for lab, url in m["sources"])
txt = f"""TITRE (≤ 100 caractères, les 60 premiers sont les plus visibles)
{m['title']}

Variantes à tester :
{chr(10).join(m['variants'])}


DESCRIPTION (à coller telle quelle)
{m['intro']}

{ADVICE}

CHAPTERS
{chr(10).join(ch)}

SOURCES (checked October 2026)
{src}

Charts marked "illustration" are illustrations, not real price data. Nothing in this video is a recommendation to buy or sell anything.

Voice-over: synthetic (AI) voice.

{m['hashtags']}


TAGS (YouTube → Détails → Afficher plus → Tags ; 500 caractères max, {len(m['tags'])} ici)
{m['tags']}


{SETTINGS.format(srt=srt, next=m['next'], thumbs=m['thumbs'])}
"""
open(os.path.join(OUTDIR, f"{m['slug']}_youtube_upload.txt"), "w").write(txt)

out = [f"# {m['title']} — voice-over script", "",
       f"Format « boîtes », {len(ns['CATS'])} chapitres, style sombre avec une couleur par chapitre, voix Emma (Kokoro). Durée : {mmss(TOTAL)}.",
       "Chaque ligne = un plan. Les chiffres sont vérifiés (sources en bas) ; les formulations prudentes (« about », « often », « usually ») sont voulues.",
       "", "## Intro", ""]
for l in LINES:
    s = l["scene"]
    if isinstance(s, tuple) and s[0] == "chap":
        out += ["", f"## {s[1]:02d} — {s[2].rstrip('.')}", ""]
    elif l.get("hide") and "## Outro" not in out:
        out += ["", "## Outro", ""]
    out.append(f"- {l['sub']}")
out += ["", "## Sources (vérifiées en octobre 2026)", ""] + [f"- [{lab}]({url})" for lab, url in m["sources"]] + [f"- {x}" for x in m["md_extra"]] + [""]
open(os.path.join(OUTDIR, f"{m['slug']}_script.md"), "w").write("\n".join(out))
print("\n".join(ch), "\nTOTAL", mmss(TOTAL))
