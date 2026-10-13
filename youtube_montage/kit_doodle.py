"""Upload kit for a doodle video built with doodle_video.py: python3 kit_doodle.py compound|tricks|first1000
Writes kit_<slug>/<slug>_youtube_upload.txt, <slug>_script.md and <slug>_subtitles_en.srt from the real timings."""
import importlib
import os
import sys

META = {
    "compound": dict(
        module="build_compound", file="compound_interest",
        title="Compound Interest Explained So Simply It Feels Illegal",
        variants=["How Compound Interest Actually Works (Explained Simply)", "Why €200 a Month Can Turn Into €500,000"],
        intro="Put €10,000 away, never touch it, and 30 years later it's worth about €76,000 (at 7% a year). That's compound interest. "
              "Here are 7 simple ideas: interest on interest, the rule of 72, why time beats money, why most people quit during the boring years, "
              "and how debt, fees and inflation compound against you.",
        chapters={"c1": "1 · Interest on interest", "c2": "2 · The rule of 72", "c3": "3 · Time beats money", "c4": "4 · The boring years",
                  "c5": "5 · It works against you too", "c6": "6 · Fees compound too", "c7": "7 · Inflation: compounding in reverse",
                  "f0": "Final message"},
        first="Why compound interest feels like magic",
        sources=[("UBS Global Investment Returns Yearbook 2025 (Dimson, Marsh, Staunton): world equities ≈5.2% a year above inflation, 1900–2024",
                  "https://www.jbs.cam.ac.uk/?p=280729"),
                 ("European Central Bank: 2% inflation target", "https://www.ecb.europa.eu/mopo/strategy/html/index.en.html"),
                 ("Quote Investigator: the \"eighth wonder of the world\" quote and Einstein", "https://quoteinvestigator.com/2011/10/18/compound-interest/")],
        notes="All examples are hypothetical: 7% a year before fees, monthly deposits compounded monthly. €200 a month from 25 to 65: about €525,000 "
              "(€96,000 put in); from 35 to 65: about €244,000 (€72,000 put in). Fees: 0.2% vs 1.8% a year on the same deposits for 30 years, "
              "about €235,000 vs €173,000. Past returns are not a promise of future returns.",
        tags="compound interest, compound interest explained, rule of 72, how compound interest works, investing for beginners, start investing early, "
             "time in the market, investing fees, inflation explained, credit card debt, personal finance europe, long term investing, "
             "index funds, money explained simply",
        hashtags="#compoundinterest #investing #personalfinance",
        thumbs="A1 (boule de neige « TIME. »), A2 (Anna contre Ben) et A3 (« 72 »)",
        next="How to Save Money So Easily It Feels Illegal"),
    "tricks": dict(
        module="build_tricks", file="shop_tricks",
        title="7 Tricks Shops Use to Make You Spend More (and How to Beat Them)",
        variants=["Why You Buy Things You Don't Need", "How Shops Hack Your Brain Into Spending More"],
        intro="You go online to buy one thing and leave with four. That's not bad luck, it's design. Here are 7 tricks shops use: prices ending "
              "in 9, decoys, fake countdowns, fake discounts, free-shipping thresholds, buy now pay later and the store map. The research behind "
              "each one, the EU rules that protect you, and how to beat them.",
        chapters={"c1": "1 · The price that ends in 9", "c2": "2 · The decoy", "c3": "3 · The fake countdown", "c4": "4 · The fake discount",
                  "c5": "5 · Free shipping", "c6": "6 · Buy now, pay later", "c7": "7 · The store map", "f0": "Final message"},
        first="Why you buy things you don't need",
        sources=[("Anderson & Simester (2003), Effects of $9 price endings on retail sales", "https://doi.org/10.1023/A:1023581927405"),
                 ("Dan Ariely, Predictably Irrational (2008), the Economist subscription decoy", "https://en.wikipedia.org/wiki/Decoy_effect"),
                 ("European Commission (Jan 2023): sweep of 399 online shops, 148 with manipulative practices, 42 fake timers",
                  "https://ec.europa.eu/commission/presscorner/detail/en/ip_23_418"),
                 ("Directive (EU) 2019/2161 (Omnibus): announced discounts vs the lowest price of the previous 30 days",
                  "https://eur-lex.europa.eu/eli/dir/2019/2161/oj"),
                 ("Di Maggio, Katz & Williams (2022), Buy Now, Pay Later Credit (NBER w30508)", "https://www.nber.org/papers/w30508"),
                 ("Directive (EU) 2023/2225, the new Consumer Credit Directive (applies from 20 November 2026)", "https://eur-lex.europa.eu/eli/dir/2023/2225/oj"),
                 ("The Food (Promotion and Placement) (England) Regulations 2021", "https://www.legislation.gov.uk/uksi/2021/1368/contents/made")],
        notes="The catalogue experiment and the decoy experiment were run in the US (prices in dollars). National rules implementing EU directives can differ.",
        tags="shopping tricks, how shops trick you, psychology of pricing, charm pricing, decoy effect, fake discounts, countdown timer, dark patterns, "
             "buy now pay later, free shipping trick, impulse buying, stop impulse buying, consumer rights europe, save money europe, personal finance",
        hashtags="#personalfinance #savemoney #psychology",
        thumbs="B1 (« €9.99 »), B2 (faux compte à rebours) et B3 (le leurre)",
        next="How to Save Money So Easily It Feels Illegal"),
    "first1000": dict(
        module="build_first1000", file="first_1000",
        title="How to Invest Your First €1,000 So Simply It Feels Illegal",
        variants=["How to Invest Your First €1,000 (Step by Step, for Europeans)", "8 Steps to Invest Your First €1,000"],
        intro="You've saved your first €1,000. Now what? Here are 8 steps, in order: kill expensive debt, keep a small cushion, use the right "
              "account (PEA, ISA, ISK…), pick a regulated low-cost broker, buy the whole market with one global index ETF, automate it, don't touch "
              "it, and keep learning.",
        chapters={"c1": "1 · Kill expensive debt first", "c2": "2 · Keep a small safety cushion", "c3": "3 · Use the right account",
                  "c4": "4 · Pick a regulated, low-cost broker", "c5": "5 · Buy the whole market", "c6": "6 · Automate it",
                  "c7": "7 · Then don't touch it", "c8": "8 · Keep learning, slowly", "f0": "Final message"},
        first="Your first €1,000: now what?",
        sources=[("Investor Compensation Schemes Directive 97/9/EC (at least €20,000 per investor)", "https://eur-lex.europa.eu/eli/dir/1997/9/oj"),
                 ("S&P 500 drawdown history (2020: −34%, record again in August 2020)", "https://dqydj.com/sp-500-drawdown-history/"),
                 ("UCITS Directive 2009/65/EC", "https://eur-lex.europa.eu/eli/dir/2009/65/oj")],
        notes="Hypothetical examples at 7% a year: €1,000 left alone for 30 years ≈ €7,600; with €100 a month added ≈ €130,000. "
              "No brand, broker or fund is recommended. Tax accounts and rules differ by country.",
        tags="how to invest 1000 euros, invest your first 1000, investing for beginners europe, how to start investing, index fund, global etf, "
             "ucits etf, pea, isa, isk, broker europe, emergency fund, pay off debt first, savings plan, personal finance europe",
        hashtags="#investing #personalfinance #europe",
        thumbs="C1 (« €1,000 → ? »), C2 (« 8 steps ») et C3 (« buy everything »)",
        next="Compound Interest Explained So Simply It Feels Illegal"),
    "debt": dict(
        module="build_debt", file="pay_off_debt",
        title="How to Pay Off Debt So Fast It Feels Illegal",
        variants=["How to Get Out of Debt Faster (Avalanche vs Snowball)", "The Minimum Payment Trap (and How to Escape It)"],
        intro="You pay every month and the debt barely moves. Here are 6 steps to get out faster: look at the whole picture, escape the minimum "
              "payment, pick an order (avalanche or snowball), focus on one debt at a time, make the interest smaller, and don't refill the bucket.",
        chapters={"c1": "1 · Look at the whole monster", "c2": "2 · Escape the minimum payment", "c3": "3 · Pick an order",
                  "c4": "4 · One debt at a time", "c5": "5 · Make the interest smaller", "c6": "6 · Don't refill the bucket", "f0": "Final message"},
        first="Why debt barely moves",
        sources=[("Gal & McShane (2012), Can Fighting Small Battles Help Win the War? Evidence from Consumer Debt Management (Journal of Marketing Research)",
                  "https://insight.kellogg.northwestern.edu/article/to_beat_debt_consider_starting_small"),
                 ("Kettle, Trudel, Blanchard & Häubl (2016), Repayment Concentration and Consumer Motivation to Get Out of Debt (Journal of Consumer Research)",
                  "https://www.ualberta.ca/en/folio/2017/01/the-secret-to-paying-off-credit-card-debt.html")],
        notes="Example (hypothetical): €3,000 at 20% a year, interest calculated monthly. €60 a month: about 9 years and €3,500 of interest. "
              "€150 a month: about 2 years and €680 of interest. If debt feels unmanageable, look for a free debt advice service in your country.",
        tags="how to pay off debt, pay off debt fast, debt avalanche, debt snowball, avalanche vs snowball, minimum payment trap, credit card debt, "
             "get out of debt, debt consolidation, emergency fund, personal finance europe, money tips, budgeting",
        hashtags="#debtfree #personalfinance #money",
        thumbs="D1 (rocher « DEBT »), D2 (bouton « PAY MINIMUM ») et D3 (avalanche ou boule de neige)",
        next="How to Invest Your First €1,000 So Simply It Feels Illegal"),
}

SETTINGS = """RÉGLAGES
- Public : Non, cette vidéo n'est pas conçue pour les enfants.
- Catégorie : Éducation.
- Langue de la vidéo : anglais. Sous-titres : importe {srt} (Sous-titres → Ajouter une langue → Anglais → Importer un fichier → Avec minutage).
- Contenu modifié ou synthétique : la voix est synthétique mais n'imite aucune personne réelle ; lis la consigne affichée au moment de l'upload.
- Écran de fin (dernières {end:.0f} s) : « s'abonner » sur le bouton orange dessiné à gauche, « vidéo suivante » ({next}) sur le cadre dessiné à droite.
- Miniatures « Test & compare » : {thumbs}.
- Publication : planifiée un dimanche ou un jeudi vers 16 h (heure de Paris)."""


def main(key):
    m = META[key]
    D = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, D)
    V = importlib.import_module(m["module"]).V
    V.prepare()
    out = os.path.join(D, f"kit_{key}")
    os.makedirs(out, exist_ok=True)
    mmss = lambda t: f"{int(t) // 60}:{int(t) % 60:02d}"
    chap = [f"0:00 {m['first']}"]
    for i, l in enumerate(V.LINES):
        if l["g"] in m["chapters"] and (i == 0 or V.LINES[i - 1]["g"] != l["g"]):
            chap.append(f"{mmss(V.starts[i])} {m['chapters'][l['g']]}")
    srt = f"{m['file']}_subtitles_en.srt"
    desc = (m["intro"] + "\n\nEducation only, not financial advice.\n\nCHAPTERS\n" + "\n".join(chap) + "\n\nSOURCES (checked October 2026)\n"
            + "\n".join(f"{a}: {u}" for a, u in m["sources"]) + "\n" + m["notes"] + "\n\nVoice-over: synthetic (AI) voice.\n\n" + m["hashtags"])
    assert len(m["tags"]) <= 500
    kit = (f"TITRE (≤ 100 caractères, les 60 premiers sont les plus visibles)\n{m['title']}\n\nVariantes à tester :\n" + "\n".join(m["variants"])
           + f"\n\n\nDESCRIPTION (à coller telle quelle)\n{desc}\n\n\nTAGS (YouTube → Détails → Afficher plus → Tags ; 500 caractères max, "
           f"{len(m['tags'])} ici)\n{m['tags']}\n\n\n" + SETTINGS.format(srt=srt, end=V.TOTAL - V.starts[-1], next=m["next"], thumbs=m["thumbs"]) + "\n")
    open(os.path.join(out, f"{m['file']}_youtube_upload.txt"), "w").write(kit)
    md = [f"# {m['title']}", "", f"Durée : {mmss(V.TOTAL)} · style doodle · voix Kokoro bf_emma", "", "Sources (vérifiées en octobre 2026) :", ""]
    md += [f"- {a} : {u}" for a, u in m["sources"]] + ["", m["notes"], "", "## Texte dit (= sous-titres)", ""]
    last = None
    for i, l in enumerate(V.LINES):
        if l["g"] in m["chapters"] and l["g"] != last:
            md += ["", f"### {m['chapters'][l['g']]}", ""]
        last = l["g"]
        md.append(f"{mmss(V.starts[i])} {l['sub']}")
    open(os.path.join(out, f"{m['file']}_script.md"), "w").write("\n".join(md) + "\n")
    V.write_srt(os.path.join(out, srt))
    print(kit)


if __name__ == "__main__":
    main(sys.argv[1])
