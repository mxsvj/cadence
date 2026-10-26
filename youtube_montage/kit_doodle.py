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
        intro="Leave €10,000 alone for 30 years at 7% a year and it turns into about €76,000 (about €42,000 in today's money, after 2% "
              "inflation: still four times what went in). That's compound interest. "
              "Here are 7 simple ideas: interest on interest, the rule of 72, why time beats money, why most people quit during the boring years, "
              "and how debt, fees and inflation compound against you.",
        chapters={"c1": "1 · Interest on interest", "c2": "2 · The rule of 72", "c3": "3 · Time beats money", "c4": "4 · The boring years",
                  "c5": "5 · It works against you too", "c6": "6 · Fees compound too", "c7": "7 · Inflation: compounding in reverse",
                  "f0": "Final message"},
        first="Why compound interest feels like magic",
        sources=[("UBS Global Investment Returns Yearbook 2025 (Dimson, Marsh, Staunton): world equities ≈5.2% a year above inflation, 1900–2024",
                  "https://www.jbs.cam.ac.uk/?p=280729"),
                 ("European Central Bank: 2% inflation target", "https://www.ecb.europa.eu/mopo/strategy/html/index.en.html")],
        notes="All examples are hypothetical: 7% a year before fees and inflation; the €10,000 example compounds yearly, the monthly-deposit "
              "examples compound monthly (7%/12 a month). Rule of 72: €10,000 "
              "becomes about €20,000, €39,000 and €76,000 after 10, 20 and 30 years. €200 a month from 25 to 65: about €525,000 (€96,000 put "
              "in); from 35 to 65: about €244,000 (€72,000 put in); €400 a month from 35 to 65: about €488,000 (€144,000 put in), still less "
              "than Anna. At 2% inflation, cash loses about 45% of its buying power in 30 years. Fees: 0.2% vs 1.8% a year on the same deposits for 30 years, about "
              "€235,000 vs €173,000, about €62,000 less. The stock chart in chapter 7 is an illustration, not real data. Past returns are not "
              "a promise of future returns. All figures are before tax.",
        tags="compound interest, compound interest explained, rule of 72, how compound interest works, investing for beginners, start investing early, "
             "time in the market, investing fees, inflation explained, credit card debt, personal finance europe, long term investing, "
             "index funds, money explained simply",
        hashtags="#compoundinterest #investing #personalfinance",
        thumbs="A4 (« €10,000 → €76,000 », recommandée : c'est la première image de la vidéo), A2 (Anna contre Ben) et A3 (« 72 »)",
        next="How to Save Money So Easily It Feels Illegal"),
    "tricks": dict(
        module="build_tricks", file="shop_tricks",
        title="7 Tricks Shops Use to Make You Spend More (and How to Beat Them)",
        variants=["Why You Buy Things You Don't Need", "How Shops Hack Your Brain Into Spending More"],
        intro="This price says €9.99. Your brain reads nine, but it's ten. Shops test prices, buttons and timers on millions of people. Here are "
              "7 tricks they use: prices ending in 9, decoys, fake countdowns, fake discounts, free-shipping thresholds, buy now pay later and the "
              "store map. The research behind each one, the EU rules that protect you, and how to beat them.",
        chapters={"c1": "1 · The price that ends in 9", "c2": "2 · The decoy", "c3": "3 · The fake countdown", "c4": "4 · The fake discount",
                  "c5": "5 · Free shipping", "c6": "6 · Buy now, pay later", "c7": "7 · The store map", "f0": "Final message"},
        first="€9.99 isn't nine",
        sources=[("Anderson & Simester (2003), Effects of $9 price endings on retail sales", "https://doi.org/10.1023/A:1023581927405"),
                 ("Dan Ariely, Predictably Irrational (2008), the Economist subscription decoy", "https://en.wikipedia.org/wiki/Decoy_effect"),
                 ("European Commission (Jan 2023): sweep of 399 online shops, 148 with manipulative practices, 42 fake timers",
                  "https://ec.europa.eu/commission/presscorner/detail/en/ip_23_418"),
                 ("Directive (EU) 2019/2161 (Omnibus): announced discounts vs the lowest price of the previous 30 days",
                  "https://eur-lex.europa.eu/eli/dir/2019/2161/oj"),
                 ("Di Maggio, Katz & Williams (2022), Buy Now, Pay Later Credit (NBER w30508)", "https://www.nber.org/papers/w30508"),
                 ("Directive (EU) 2023/2225, the new Consumer Credit Directive (applies from 20 November 2026)", "https://eur-lex.europa.eu/eli/dir/2023/2225/oj"),
                 ("The Food (Promotion and Placement) (England) Regulations 2021", "https://www.legislation.gov.uk/uksi/2021/1368/contents/made")],
        notes="The catalogue experiment and the decoy experiment were run in the US (prices in dollars). The new Consumer Credit Directive "
              "applies from 20 November 2026; national rules implementing EU directives can differ.",
        tags="shopping tricks, how shops trick you, psychology of pricing, charm pricing, decoy effect, fake discounts, countdown timer, dark patterns, "
             "buy now pay later, free shipping trick, impulse buying, stop impulse buying, consumer rights europe, save money europe, personal finance",
        hashtags="#personalfinance #savemoney #psychology",
        thumbs="B1 (« €9.99 », recommandée), B2 (faux compte à rebours) et B3 (le leurre « nobody picks this »)",
        next="How to Save Money So Easily It Feels Illegal"),
    "first1000": dict(
        module="build_first1000", file="first_1000",
        title="How to Invest Your First €1,000 (8 Steps, in Order)",
        variants=["How to Invest Your First €1,000 (Step by Step, for Europeans)", "Your First €1,000: What to Do With It, Step by Step"],
        intro="Everyone has a plan for your first €1,000. Most of them are wrong. Here are 8 steps, in order: kill expensive debt, keep a small "
              "cushion (and if €1,000 is all you have, that's your cushion), use the right account (PEA, ISA, ISK…), pick a broker regulated where "
              "you live, buy the whole market with one global index ETF, automate it, don't touch it, and keep learning. Investing can lose money.",
        chapters={"c1": "1 · Kill expensive debt first", "c2": "2 · Keep a small safety cushion", "c3": "3 · Use the right account",
                  "c4": "4 · Pick a regulated, low-cost broker", "c5": "5 · Buy the whole market", "c6": "6 · Automate it",
                  "c7": "7 · Then don't touch it", "c8": "8 · Keep learning, slowly", "f0": "Final message"},
        first="Everyone has a plan for your first €1,000",
        sources=[("Investor Compensation Schemes Directive 97/9/EC (at least €20,000 per investor)", "https://eur-lex.europa.eu/eli/dir/1997/9/oj"),
                 ("S&P 500 drawdown history (price index): 2020 bottom 23 March, record again 18 August 2020. After 2000: −49% to October "
                  "2002, back to the 2000 peak in May 2007, then −57% to March 2009, and above the 2000 peak for good from March 2013",
                  "https://dqydj.com/sp-500-drawdown-history/"),
                 ("UCITS Directive 2009/65/EC", "https://eur-lex.europa.eu/eli/dir/2009/65/oj")],
        notes="Hypothetical examples at 7% a year (effective annual rate): €1,000 left alone for 30 years ≈ €7,600; with €100 a month added "
              "≈ €125,000 in total, of which about €37,000 is money you put in. Before fees, inflation and tax. Investing can lose money. "
              "Pick a broker authorised by a financial regulator (in the EU, a broker authorised in another member state is fine). The EU "
              "investor compensation scheme covers at least €20,000 per investor when a firm fails and cannot return your assets (some "
              "countries pay 90% of the claim); it does not cover market losses. In a PEA, only PEA-eligible ETFs can be held (global trackers there are synthetic). "
              "No brand, broker or fund is recommended. Tax accounts and rules differ by country.",
        tags="how to invest 1000 euros, invest your first 1000, investing for beginners europe, how to start investing, index fund, global etf, "
             "ucits etf, pea, isa, isk, broker europe, emergency fund, pay off debt first, savings plan, personal finance europe",
        hashtags="#investing #personalfinance #europe",
        thumbs="C2 (« 8 steps », recommandée), C3 (« buy everything ») et C1 (« €1,000, now what? »)",
        next="Compound Interest Explained So Simply It Feels Illegal"),
    "debt": dict(
        module="build_debt", file="pay_off_debt",
        title="The Minimum Payment Trap (and How to Escape It)",
        variants=["Why Your Debt Barely Moves (and How to Fix It)", "How to Get Out of Debt Faster (Avalanche vs Snowball)"],
        intro="The minimum payment is the most expensive button in your card app. On a €3,000 card at 20%, paying a fixed €60 a month takes about "
              "9 years; €150 a month clears it in about 2. Here are 6 steps to escape the minimum payment trap: put all your debts on one page, "
              "pay more than the minimum, pick an order (avalanche or snowball), one debt at a time, make the interest smaller, and don't refill "
              "the card. If debt feels unmanageable, free debt advice exists in most countries: use it.",
        chapters={"c1": "1 · Put it all on one page", "c2": "2 · Escape the minimum payment", "c3": "3 · Pick an order",
                  "c4": "4 · One debt at a time", "c5": "5 · Make the interest smaller", "c6": "6 · Don't refill the card", "f0": "Final message"},
        first="The most expensive button in your card app",
        sources=[("Gal & McShane (2012), Can Fighting Small Battles Help Win the War? Evidence from Consumer Debt Management (Journal of Marketing Research)",
                  "https://www.kellogg.northwestern.edu/academics-research/research/detail/2012/can-fighting-small-battles-help-win-the-war-evidence"),
                 ("Kettle, Trudel, Blanchard & Häubl (2016), Repayment Concentration and Consumer Motivation to Get Out of Debt (Journal of Consumer Research)",
                  "https://www.ualberta.ca/en/folio/2017/01/the-secret-to-paying-off-credit-card-debt.html")],
        notes="Illustrative examples, interest calculated monthly. €3,000 at 20% a year: a fixed €60 a month takes 109 months (about 9 years) and "
              "about €3,500 of interest; €150 a month takes 25 months and about €680. A minimum of 2% of the balance (at least €20) would take about "
              "36 years and about €11,200 of interest. Three debts: store credit €800 at 9%, card €2,200 at 21%, car loan €3,500 at 7%; with €300 a "
              "month in total, the avalanche pays about €670 of interest over 24 months, the snowball about €750 over 25 months and clears its first "
              "debt in month 5 instead of 12. Consolidation: €6,500 at 12% over 3 years costs about €1,270 of interest; at 9% over 6 years about "
              "€1,940. Minimum-payment rules differ by country and by card: in France, revolving credit up to €3,000 must be repaid within 36 "
              "months; the UK and the Netherlands set their own minimums; many continental cards are charge cards with no minimum at all. "
              "Free debt advice: MABS (Ireland), MoneyHelper or StepChange (UK), "
              "Schuldnerberatung (Germany, Austria), Point conseil budget (France), Geldfit (Netherlands).",
        tags="how to pay off debt, pay off debt fast, debt avalanche, debt snowball, avalanche vs snowball, minimum payment trap, credit card debt, "
             "get out of debt, debt consolidation, emergency fund, personal finance europe, money tips, budgeting",
        hashtags="#debtfree #personalfinance #money",
        pinned="Free, independent debt advice (no fees, no loans to sell you): Ireland: MABS · UK: MoneyHelper, StepChange · Germany and Austria: "
               "Schuldnerberatung (your local council or Caritas/Diakonie) · France: Point conseil budget · Netherlands: Geldfit. "
               "Which service helped you? Add yours for your country below.",
        thumbs="D2 (bouton « PAY MINIMUM », recommandée) et D1 (rocher « DEBT »)",
        next=None, tail=4.5),                # ends on its own outro question, no end screen
}

SETTINGS = """RÉGLAGES
- Public : Non, cette vidéo n'est pas conçue pour les enfants.
- Catégorie : Éducation.
- Langue de la vidéo : anglais. Sous-titres : importe {srt} (Sous-titres → Ajouter une langue → Anglais → Importer un fichier → Avec minutage).
- Contenu modifié ou synthétique : la voix est synthétique mais n'imite aucune personne réelle ; lis la consigne affichée au moment de l'upload.
{endscreen}
- Miniatures « Test & compare » : {thumbs}.
- Publication : planifiée un dimanche ou un jeudi vers 16 h (heure de Paris)."""


def main(key):
    m = META[key]
    D = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, D)
    V = importlib.import_module(m["module"]).V
    V.prepare(tail=m.get("tail", 12.5))
    out = os.path.join(D, f"kit_{key}")
    if m["next"]:
        endscreen = (f"- Écran de fin (dernières {min(20.0, V.TOTAL - V.starts[-1]):.0f} s, tout est déjà dessiné à ce moment-là) : l'élément « S'abonner » "
                     f"(rond) sur le cercle orange dessiné à gauche,\n  l'élément « Vidéo » → vidéo spécifique ({m['next']}) sur le cadre 16:9 dessiné "
                     "à droite. Publie cette vidéo-là avant celle-ci.")
    else:
        endscreen = "- Écran de fin : aucun. La vidéo se termine sur sa propre outro (une question), sans proposition de vidéo."
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
           f"{len(m['tags'])} ici)\n{m['tags']}\n\n\n" + SETTINGS.format(srt=srt, endscreen=endscreen, thumbs=m["thumbs"]) + "\n")
    if m.get("pinned"):
        kit += f"\n\nCOMMENTAIRE ÉPINGLÉ (poste-le toi-même juste après la publication, puis « Épingler »)\n{m['pinned']}\n"
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
