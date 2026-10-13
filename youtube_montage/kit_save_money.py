"""Upload kit for 'How to Save Money So Easily It Feels Illegal': title, description with chapters and sources, tags, settings,
script with sources (markdown) and the English .srt. Reads the real timings from build_save.py (voice cached)."""
import os
import shutil

import build_save_money_illegal as B

OUTD = os.path.join(B.D, "kit_save")
os.makedirs(OUTD, exist_ok=True)
SLUG = "save_money_illegal"
TITLE = "How to Save Money So Easily It Feels Illegal"
VARIANTS = ["How to Save Money Without Willpower (8 Science-Backed Systems)", "8 Saving Systems That Feel Like Cheating"]
SOURCES = [
    ("Madrian & Shea (2001), The Power of Suggestion: automatic enrolment in a 401(k) plan", "https://www.nber.org/papers/w7682"),
    ("Prelec & Simester (2001), Always Leave Home Without It: the credit-card effect", "https://doi.org/10.1023/A:1008196717017"),
    ("Soman & Cheema (2011), Earmarking and Partitioning: Increasing Saving by Low-Income Households", "https://doi.org/10.1509/jmkr.48.SPL.S14"),
    ("Thaler & Benartzi (2004), Save More Tomorrow", "https://doi.org/10.1086/380085"),
    ("Hershfield et al. (2011), Increasing Saving Behavior Through Age-Progressed Renderings of the Future Self", "https://doi.org/10.1509/jmkr.48.SPL.S23"),
]
CHAP_NAMES = {"c1": "1 · Pay yourself first", "c2": "2 · Make saving the default", "c3": "3 · Make spending hurt a little",
              "c4": "4 · The 72-hour rule", "c5": "5 · Give every euro a job", "c6": "6 · Fix big things once",
              "c7": "7 · Save your next raise", "c8": "8 · Meet your future self", "f0": "Final message"}


def mmss(t):
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


chap = ["0:00 Why your money disappears"]
for i, l in enumerate(B.LINES):
    if l["g"] in CHAP_NAMES and (i == 0 or B.LINES[i - 1]["g"] != l["g"]):
        chap.append(f"{mmss(B.starts[i])} {CHAP_NAMES[l['g']]}")

desc = f"""You get paid, you feel rich for a week, and then the money is gone. It's not about how much you earn, and it's not about discipline: your brain is built to spend now. Here are 8 simple systems, backed by behavioural research, that make saving almost automatic.

Education only, not financial advice.

CHAPTERS
""" + "\n".join(chap) + """

SOURCES (checked October 2026)
""" + "\n".join(f"{a}: {u}" for a, u in SOURCES) + """
The 37% → 86% figure is for new employees of one large US company (3 to 15 months in the job). The "×2" card effect is the paper's upper estimate ("up to 100%").

Voice-over: synthetic (AI) voice.

#personalfinance #savingmoney #moneytips"""

tags = ("how to save money, save money fast, saving money tips, pay yourself first, automatic savings, money psychology, behavioral finance, "
        "72 hour rule, sinking funds, savings pots, lifestyle creep, save more tomorrow, future self, emergency fund, personal finance europe, "
        "frugal living, money habits, simple, budgeting without budget")
assert len(tags) <= 500

kit = f"""TITRE (≤ 100 caractères, les 60 premiers sont les plus visibles)
{TITLE}

Variantes à tester :
{VARIANTS[0]}
{VARIANTS[1]}


DESCRIPTION (à coller telle quelle)
{desc}


TAGS (YouTube → Détails → Afficher plus → Tags ; 500 caractères max, {len(tags)} ici)
{tags}


RÉGLAGES
- Public : Non, cette vidéo n'est pas conçue pour les enfants.
- Catégorie : Éducation.
- Langue de la vidéo : anglais. Sous-titres : importe {SLUG}_subtitles_en.srt (Sous-titres → Ajouter une langue → Anglais → Importer un fichier → Avec minutage).
- Contenu modifié ou synthétique : la voix est synthétique mais n'imite aucune personne réelle ; lis la consigne affichée au moment de l'upload.
- Écran de fin (dernières {B.TOTAL - B.starts[-1]:.0f} s) : « s'abonner » sur le bouton orange dessiné à gauche, « vidéo suivante » (Every ETF Explained) sur le cadre dessiné à droite.
- Miniatures « Test & compare » : S1 (« feels ILLEGAL »), S2 (« saving on autopilot ») et S3 (« your brain: NOW »).
- Publication : planifiée un dimanche ou un jeudi vers 16 h (heure de Paris).
"""
open(os.path.join(OUTD, f"{SLUG}_youtube_upload.txt"), "w").write(kit)

md = [f"# {TITLE}", "", f"Durée : {mmss(B.TOTAL)} · style doodle (inspiré de « simple, actually ») · voix Kokoro bf_emma", "",
      "Faits vérifiés en octobre 2026 :", ""]
md += [f"- {a} : {u}" for a, u in SOURCES]
md += ["", "## Texte dit (= sous-titres)", ""]
last = None
for i, l in enumerate(B.LINES):
    if l["g"] in CHAP_NAMES and l["g"] != last:
        md += ["", f"### {CHAP_NAMES[l['g']]}", ""]
    last = l["g"]
    md.append(f"{mmss(B.starts[i])} {l['sub']}")
open(os.path.join(OUTD, f"{SLUG}_script.md"), "w").write("\n".join(md) + "\n")
shutil.copy(os.path.join(B.E, "subtitles_en.srt"), os.path.join(OUTD, f"{SLUG}_subtitles_en.srt"))
print(kit)
