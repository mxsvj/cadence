"""Publishing calendar for the doodle videos and their Shorts: calendrier.ics (Google Calendar, phone), a readable
calendrier.txt, and two zips of Shorts named by publishing date, for the same filing script as the videos."""
import datetime as dt
import os
import zipfile
from zoneinfo import ZoneInfo

D = os.path.dirname(os.path.abspath(__file__))
SH = os.path.join(D, "shorts_doodle")
OUT = os.path.join(D, "livraison_shorts")
PARIS = ZoneInfo("Europe/Paris")

LONG = {"compound": "Compound Interest Explained So Simply It Feels Illegal",
        "tricks": "7 Tricks Shops Use to Make You Spend More (and How to Beat Them)",
        "first1000": "How to Invest Your First €1,000 (8 Steps, in Order)",
        "debt": "The Minimum Payment Trap (and How to Escape It)"}
# (date, hour, kind, key, short index or None, note). Compound Interest went out on Sunday 18 October.
PLAN = [
    ("2026-10-18", 18, "short", "compound", 0, ""),
    ("2026-10-18", 19, "setup", None, None, "Mise en place (30 min) : passe les 3 anciennes vidéos en privé, change la photo de profil et la bannière, "
                                             "Ensuite, publie toi-même chaque vidéo et chaque Short le jour indiqué (un rappel sonne 15 min avant)."),
    ("2026-10-19", 18, "short", "compound", 1, ""),
    ("2026-10-20", 18, "short", "compound", 2, ""),
    ("2026-10-20", 19, "stats", "compound", None, ""),
    ("2026-10-22", 16, "long", "tricks", None, ""),
    ("2026-10-23", 18, "short", "tricks", 0, ""),
    ("2026-10-24", 18, "short", "tricks", 1, ""),
    ("2026-10-24", 19, "stats", "tricks", None, ""),
    ("2026-10-25", 16, "long", "first1000", None, ""),
    ("2026-10-26", 18, "short", "tricks", 2, ""),
    ("2026-10-27", 18, "short", "first1000", 0, ""),
    ("2026-10-27", 19, "stats", "first1000", None, ""),
    ("2026-10-28", 18, "short", "first1000", 1, ""),
    ("2026-10-29", 16, "long", "debt", None, "Juste après la sortie : poste et épingle le commentaire « free debt advice » (texte dans « tags et reglages.txt »)."),
    ("2026-10-30", 18, "short", "first1000", 2, ""),
    ("2026-10-31", 18, "short", "debt", 0, ""),
    ("2026-10-31", 19, "stats", "debt", None, ""),
    ("2026-11-01", 18, "short", "debt", 1, ""),
    ("2026-11-02", 18, "short", "debt", 2, ""),
    ("2026-11-04", 19, "review", None, None, "Bilan des 2 semaines : envoie à Claude les captures de YouTube Studio (Analytics → Vue d'ensemble, Audience, "
                                              "et pour chaque vidéo : Portée + Engagement). On décide des 4 prochaines vidéos à partir de là."),
]
DESC = {
    "compound": [
        "Divide 72 by your yearly return and you get roughly how many years your money takes to double. At 7% a year: about 10 years. "
        "€10,000 → €20,000 → €39,000 → €76,000.\nExample only, not financial advice.",
        "Anna invests €200 a month from 25, Ben from 35. Both stop at 65, both earn 7% a year. Anna ends with about €525,000, Ben with about "
        "€244,000. Even if Ben doubles to €400 a month, he ends with about €488,000. Starting early beats starting big.\n"
        "Hypothetical example, before fees, inflation and tax. Not financial advice.",
        "€200 a month for 30 years at 7% a year: with 0.2% fees, about €235,000. With 1.8% fees, about €173,000. Same money in, about €62,000 "
        "less out. Check the fees before you invest.\nHypothetical example, before tax. Not financial advice."],
    "tricks": [
        "Your brain reads the first digit and mostly stops there, so €9.99 feels like nine. In one US catalogue test, raising a dress from $34 "
        "to $39 sold about a third more. The fix: round prices up in your head.",
        "Online only $59. Print only $125. Print and online $125. Nobody picks print only: it's there to make the bundle look like a steal. In "
        "a famous class experiment, 84% chose the bundle; without the decoy, 68% chose the cheap online option.",
        "Was €199, now €99? In the EU, since 2022, a shop announcing a discount has to compare it with its lowest price of the previous 30 "
        "days. Here that's €120, so the real discount is about 17%, not 50%."],
    "first1000": [
        "Your bank offers a fund, a friend talks about crypto, someone online has a secret strategy. Your first €1,000 isn't about getting "
        "rich: it's about building the habit that will. The 8 steps are in the full video.\nInvesting can lose money. Not financial advice.",
        "€1,000 left alone for 30 years at 7% a year grows to about €7,600. Add €100 a month and it's about €125,000, of which about €37,000 "
        "is money you put in.\nExample only, not guaranteed; before fees, inflation and tax. Not financial advice.",
        "In early 2020, stocks fell about a third in a few weeks, and the S&P 500 was back at its record about five months after the bottom. "
        "It isn't always that fast: after 2000 it took about 7 years, then 2008 hit, 13 years in all. You can lose money.\nNot financial advice."],
    "debt": [
        "On a €3,000 card at 20% a year, a fixed €60 a month takes about 9 years. €150 a month clears it in about 2. The lower the minimum, "
        "the longer you pay.\nIllustrative example. Not financial advice.",
        "Avalanche: highest interest rate first, it saves the most. Snowball: smallest balance first, quick wins. With €300 a month on three "
        "debts, the avalanche saves about €80; the snowball clears its first debt in month 5 instead of 12. Similar rates? Start small. One "
        "much higher? Kill it first.\nIllustrative example. Not financial advice.",
        "Many minimums are a slice of what you owe, like 2%. As the debt shrinks, the payment shrinks too, and the same €3,000 card can take "
        "over 30 years and about €11,000 in interest. At €150 a month: about €680 of interest, and 2 years. Rules vary by country.\n"
        "Illustrative example. Not financial advice."],
}
TAGS = {"compound": "#compoundinterest #investing #personalfinance", "tricks": "#savemoney #psychology #shopping",
        "first1000": "#investing #personalfinance #europe", "debt": "#debt #creditcard #personalfinance"}
FOLDER = {"compound": "Shorts - Compound Interest", "tricks": "Shorts - 7 Tricks Shops Use",
          "first1000": "Shorts - Invest Your First 1,000 euros", "debt": "Shorts - The Minimum Payment Trap"}


def short_info(key, idx):
    p = os.path.join(SH, f"short_{key}_{idx + 1}.txt")
    lines = open(p).read().splitlines()
    return lines[0], float(lines[1]), os.path.join(SH, f"short_{key}_{idx + 1}.mp4")


def safe(name):
    return name.replace(":", " -").replace("?", "").replace('"', "").replace("/", "-")


def ics_escape(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


rows, events, files = [], [], {k: [] for k in FOLDER}
texts = {k: [] for k in FOLDER}
for k, (day, hour, kind, key, idx, note) in enumerate(PLAN):
    start = dt.datetime.fromisoformat(day).replace(hour=hour, tzinfo=PARIS)
    when = start.strftime("%a %d/%m %Hh").replace("Mon", "lun").replace("Tue", "mar").replace("Wed", "mer").replace("Thu", "jeu") \
        .replace("Fri", "ven").replace("Sat", "sam").replace("Sun", "dim")
    if kind == "long":
        title = f"▶ Vidéo : {LONG[key]}"
        desc = (f"À publier maintenant (dossier YouTube de la vidéo) : titre, description, sous-titres, miniature « recommandée » + Test & "
                f"compare, écran de fin : tout est dans le dossier. {note}").strip()
    elif kind == "short":
        stitle, dur, path = short_info(key, idx)
        fname = f"{day} - {safe(stitle)}.mp4"
        files[key].append((fname, path))
        texts[key].append(f"{day} à {hour} h — fichier « {fname} » ({dur:.0f} s)\nTitre :\n{stitle}\nDescription :\n"
                          + DESC[key][idx].replace("\\n", "\n") + f"\nFull video on the channel: {LONG[key]}.\n{TAGS[key]}\n"
                          f"Vidéo associée : {LONG[key]}\n")
        title = f"▶ Short : {stitle}"
        desc = (f"Fichier : {fname} ({dur:.0f} s). Titre et description : dans « textes des Shorts.txt ». "
                f"Vidéo associée : {LONG[key]}.")
    elif kind == "stats":
        title = f"📊 Stats 48 h : {LONG[key][:40]}…"
        desc = ("YouTube Studio → la vidéo → Analytics : capture « Portée » (impressions, taux de clics) et « Engagement » (durée moyenne, courbe de "
                "rétention), et envoie-les à Claude pour ajuster miniature, titre ou début.")
    elif kind == "setup":
        title = "🛠 Mise en place de la chaîne"
        desc = note
    else:
        title = "📈 Bilan des 2 semaines"
        desc = note
    rows.append(f"{when}  {title.replace('▶ ', '').replace('📊 ', '').replace('🛠 ', '').replace('📈 ', '')}" + (f"\n            {desc}" if kind != "long" or note else ""))
    u = start.astimezone(dt.timezone.utc)
    alarm = "BEGIN:VALARM\r\nACTION:DISPLAY\r\nDESCRIPTION:Rappel\r\nTRIGGER:-PT15M\r\nEND:VALARM\r\n"
    events.append("BEGIN:VEVENT\r\n"
                  f"UID:euro-unboxed-{day}-{k}@cadence\r\nDTSTAMP:20261018T120000Z\r\n"
                  f"DTSTART:{u:%Y%m%dT%H%M%SZ}\r\nDTEND:{(u + dt.timedelta(minutes=30)):%Y%m%dT%H%M%SZ}\r\n"
                  f"SUMMARY:{ics_escape(title)}\r\nDESCRIPTION:{ics_escape(desc)}\r\n{alarm}END:VEVENT\r\n")

os.makedirs(OUT, exist_ok=True)
ics = "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Euro Unboxed//calendrier//FR\r\nCALSCALE:GREGORIAN\r\n" + "".join(events) + "END:VCALENDAR\r\n"
open(os.path.join(OUT, "calendrier Euro Unboxed.ics"), "w", newline="").write(ics)
txt = ("CALENDRIER EURO UNBOXED (heure de Paris)\n\n"
       "Tu publies toi-même, le jour et vers l'heure indiqués. Importe « calendrier Euro Unboxed.ics » dans Google Agenda (Paramètres → "
       "Importer) ou ouvre-le sur ton téléphone : un rappel sonne 15 min avant chaque publication. Si tu publies un peu plus tard, ce n'est "
       "pas grave : l'important est la régularité (une vidéo longue jeudi et dimanche, un Short par jour).\n"
       "Vidéos longues : jeudi et dimanche à 16 h. Shorts : un par jour à 18 h, chacun relié à sa vidéo longue (« Vidéo associée »).\n"
       "Compound Interest est sortie le dimanche 18 octobre. Ordre des vidéos suivantes imposé par les écrans de fin : chaque vidéo pointe vers "
       "une vidéo déjà en ligne. 7 Tricks pointe vers « How to Save Money So Easily It Feels Illegal » : laisse-la publique (elle est déjà dans "
       "le style doodle) ou publie-la avant le 22.\n\n"
       + "\n".join(rows) + "\n")
open(os.path.join(OUT, "calendrier.txt"), "w").write(txt)
head = ("Pour chaque Short, dans YouTube Studio (depuis l'ordinateur) : mets le fichier en ligne, colle le titre et la description, "
        "choisis la « Vidéo associée » (c'est ce lien qui envoie vers la vidéo longue ; si elle n'est pas encore publiée, ajoute-le le jour de "
        "sa sortie), puis « Publier » le jour indiqué.\n\n\n")
for n, (key, lst) in enumerate(files.items(), 13):
    zp = os.path.join(OUT, f"EuroUnboxed {n} - {FOLDER[key]}.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
        for fname, path in lst:
            z.write(path, f"{FOLDER[key]}/{fname}")
        z.writestr(f"{FOLDER[key]}/textes des Shorts.txt", "\ufeff" + head + "\n\n".join(texts[key]))
        z.writestr(f"{FOLDER[key]}/calendrier.txt", "\ufeff" + txt)
        z.write(os.path.join(OUT, "calendrier Euro Unboxed.ics"), f"{FOLDER[key]}/calendrier Euro Unboxed.ics")
    print(f"{os.path.getsize(zp) / 1048576:5.1f} MiB  {os.path.basename(zp)}  ({len(lst)} Shorts)")
print(txt)
