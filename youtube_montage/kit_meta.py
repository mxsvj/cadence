"""Per-video data for kit.py: titles, description intro, sources, tags."""
ADVICE = "Education only, not financial advice. Rules and prices change; check your own country's rules."
SETTINGS = """RÉGLAGES
- Public : Non, cette vidéo n'est pas conçue pour les enfants.
- Catégorie : Éducation.
- Langue de la vidéo : anglais. Sous-titres : importe {srt} (Sous-titres → Ajouter une langue → Anglais → Importer un fichier → Avec minutage).
- Contenu modifié ou synthétique : la voix est synthétique mais n'imite aucune personne réelle ; lis la consigne affichée au moment de l'upload.
- Écran de fin : « vidéo suivante » à gauche ({next}), « s'abonner » à droite, sur les 10 dernières secondes.
- Miniatures « Test & compare » : {thumbs}.
- Publication : planifiée un dimanche ou un jeudi vers 16 h (heure de Paris)."""

META = {
    "accounts": dict(
        slug="every_account", title="Every Investment Account in Europe Explained",
        variants=["Every Investment Account in Europe, Explained (ISA, PEA, ISK, Depot…)", "10 Types of Investment Account Every European Should Know"],
        chapter_word="", outro="Recap · a common order",
        intro="ISA, ISK, PEA, Depot, PER, assurance-vie… every European country seems to have its own investment accounts. But almost all of them fit into 10 boxes: savings accounts, brokerage accounts, tax-free accounts, life insurance, personal and workplace pensions, kids' accounts, robo-advisors, CFD trading accounts and foreign brokers. Here's what each one does, and the traps to watch.",
        sources=[("EU deposit guarantee (€100,000)", "https://eur-lex.europa.eu/eli/dir/2014/49/oj"),
                 ("France: flat tax 31.4% from 2026, assurance-vie", "https://www.previssima.fr/actualite/assurance-vie-livret-a-pea-per-quels-placements-seront-impactes-par-la-hausse-de-la-csg-en-2026.html"),
                 ("Ireland: 38% exit tax and deemed disposal", "https://etf.ie/blog/budget-2026-etf/"),
                 ("Sweden: ISK in 2026", "https://www.thelocal.se/20251124/how-swedens-isk-savings-account-will-change-in-2026"),
                 ("UK: ISA limits", "https://www.ii.co.uk/analysis-commentary/cash-isa-limit-cut-ps12000-bid-boost-uk-stock-market-ii537373"),
                 ("Denmark: aktiesparekonto", "https://skat.dk/borger/aktier-og-andre-vaerdipapirer/aktiesparekonto"),
                 ("EU savings and investment accounts (2025)", "https://fondbolagen.se/regelverk/remissyttranden/remissyttranden-2025/recommendations-eu-accounts/"),
                 ("PEPP review", "https://pensionseurope.eu/press-release-press-release-pensionseuropes-position-paper-on-the-pepp-review/"),
                 ("Germany: Frühstart-Rente (planned)", "https://www.steuertipps.de/eltern-familie-ehe/fruehstart-rente-staatliches-vorsorgedepot-fuer-kinder"),
                 ("ESMA: CFD restrictions", "https://www.esma.europa.eu/node/84933"),
                 ("France: undeclared foreign accounts", "https://selectra.info/finance/actualites/marche/compte-etranger-non-declare-amende-1500")],
        md_extra=["Allemagne : abattement de 1 000 € par an sur les revenus du capital (Sparerpauschbetrag), puis environ 26,4 % (25 % + solidarité).",
                  "Espagne : déduction d'un plan de pension individuel limitée à 1 500 € par an ; formulaire 720 au-delà de 50 000 € d'actifs à l'étranger.",
                  "France : Livret A plafonné à 22 950 € ; assurance-vie, 152 500 € par bénéficiaire hors droits de succession (versements avant 70 ans, art. 990 I du CGI).",
                  "Pays-Bas : « Box 3 », impôt sur un rendement présumé de l'épargne.",
                  "Allemagne : en cas de conversion de salaire vers une retraite d'entreprise, l'employeur verse en général 15 % en plus."],
        tags="every investment account explained, investment accounts europe, isa explained, pea explained, isk sweden, tax free investment account, assurance vie, depot germany, personal pension europe, pepp, robo advisor, cfd trading, foreign broker tax, investing in europe, personal finance europe, savings account europe",
        hashtags="#investing #personalfinance #europe",
        thumbs="X3 (cartes sur fond bleu UE), A4 (cartes) et A1 (liste)", next="la vidéo ETF, annoncée dans la voix off"),
    "mistakes": dict(
        slug="every_mistake", title="Every Investing Mistake Explained",
        variants=["12 Investing Mistakes That Cost Europeans Thousands", "Every Investing Mistake (and How to Avoid It)"],
        chapter_word="", outro="Recap",
        intro="Most investors don't lose money because they picked the wrong fund. They lose it through a few classic mistakes: waiting to start, no safety cushion, high fees, timing the market, panic selling, chasing winners, one big bet, trading too much, following hype, buying what you don't understand and using the wrong account. Here are all 12, with the data behind them.",
        sources=[("Morningstar, Mind the Gap 2025", "https://www.morningstar.com/business/insights/research/mind-the-gap-2025"),
                 ("Missing the best days (J.P. Morgan, 1995–2014)", "https://www.atb.com/archive/articles/does-market-timing-work/"),
                 ("S&P SPIVA persistence scorecard 2021", "https://www.spglobal.com/spdji/en/spiva/article/us-persistence-scorecard-year-end-2021"),
                 ("Bessembinder: do stocks outperform Treasury bills?", "https://news.wpcarey.asu.edu/20180917-do-stocks-outperform-treasury-bills"),
                 ("Barber & Odean, Trading Is Hazardous to Your Wealth", "https://faculty.haas.berkeley.edu/odean/Papers%20current%20versions/Individual_Investor_Performance_Final.pdf")],
        md_extra=["Calculs : 200 €/mois à 7 % par an, capitalisation mensuelle : environ 244 000 € à 55 ans en commençant à 25 ans, environ 104 000 € en commençant à 35 ans ; écart de frais 0,03 % contre 1,8 % sur 30 ans : plus de 60 000 €.",
                  "Krach de 2020 : S&P 500 en baisse d'environ 34 % en février–mars, de retour à son record environ cinq mois après le point bas.",
                  "Wirecard (insolvable en juin 2020, 1,9 milliard d'euros introuvables) et GameStop (janvier 2021) : faits connus."],
        tags="investing mistakes, every investing mistake explained, beginner investing mistakes, panic selling, market timing, investing fees, emergency fund, diversification, overtrading, investing in europe, personal finance europe, etf investing, long term investing, behavioural finance",
        hashtags="#investing #personalfinance #etf",
        thumbs="X4 (« DON'T press it »), M5 (citation orange) et M6 (cases à cocher)", next="la vidéo des comptes d'investissement, annoncée dans la voix off"),
    "fees": dict(
        slug="every_fee", title="Every Bank Fee Explained",
        variants=["Every Bank Fee Europeans Pay (and How to Avoid Them)", "10 Bank Fees You Pay Without Noticing"],
        chapter_word="", outro="Recap",
        intro="Account fees, card fees, overdraft fees, currency markups, the \"pay in euros?\" trick at the cash machine, transfer fees, fund fees, entry fees, broker fees and \"free\" trading. Each fee is small. Together, they're not. Here's every box, with the EU rules that protect you.",
        sources=[("EU instant payments regulation", "https://openbankingtracker.com/regulation/psr-instant-payments"),
                 ("Currency conversion transparency (EU 2019/518)", "https://eur-lex.europa.eu/eli/reg/2019/518/oj"),
                 ("Cross-border euro payments (EU 2021/1230)", "https://eur-lex.europa.eu/eli/reg/2021/1230/oj"),
                 ("Account switching (EU 2014/92)", "https://eur-lex.europa.eu/eli/dir/2014/92/oj"),
                 ("Dynamic currency conversion, Norwegian Consumer Council", "https://storage02.forbrukerradet.no/media/2017/07/input-from-ncc-to-the-european-commission-on-dcc-30062017.pdf"),
                 ("BEUC on currency conversion", "https://beuc.eu/press-releases/end-sight-currency-conversion-scams"),
                 ("France: overdraft incident fee caps", "https://www.lafinancepourtous.com/2013/10/22/decouvert-bancaire-les-commissions-d-intervention-plafonnees-a-partir-du-1er-janvier-2014"),
                 ("France: PEA fee caps (AMF)", "https://www.amf-france.org/fr/actualites-publications/actualites/plafonnement-des-frais-pour-le-pea-que-faut-il-retenir"),
                 ("EU ban on payment for order flow", "https://legal.pwc.de/content/services/regcore-client-alert/pwc-legal-client-alert-germanys-pfof-ban-is-now-fully-in-force-july-2026.pdf")],
        md_extra=["Exemple de frais de compte (8 €/mois) et de frais d'entrée (3 %) : exemples hypothétiques.",
                  "ETF monde autour de 0,2 % par an de frais courants ; fonds bancaires souvent 1,5 % ou plus : ordres de grandeur."],
        tags="bank fees, every bank fee explained, hidden bank fees, currency conversion fee, dynamic currency conversion, pay in euros or local currency, overdraft fees, fund fees, entry fees, broker fees, payment for order flow, instant payments eu, personal finance europe, save money europe",
        hashtags="#personalfinance #banking #europe",
        thumbs="X5 (« NEVER press this »), F4 (relevé surligné) et F5 (distributeur)", next="la vidéo des erreurs d'investissement, annoncée dans la voix off"),
    "worst": dict(
        slug="pov_worst_moment", title="POV: You Invest €10,000 at the Worst Possible Moment",
        variants=["POV: You Invested €10,000 the Day Before the 2008 Crash", "I Bought the Top in 2007. Here's What Happened Next"],
        chapter_word="", outro="What decided it",
        intro="It's October 2007. You've saved €10,000 and you put it all into the stock market, on the very day of the record. Then comes 2008: Lehman Brothers, Iceland, Fortis, a 57% drop. Two versions of you: one sells at the bottom, one does nothing. Here's what happened to both, with real S&P 500 data.",
        sources=[("S&P 500 drawdown history", "https://dqydj.com/sp-500-drawdown-history/"),
                 ("S&P 500 total return back to its 2007 peak in April 2012 (Bloomberg data)", "https://www.washoecounty.gov/humanresources/board_committees/deferred_compensation/2024/files/02-14-2024%20Item%2012%20SP500%20Growth%20Drawdown%20and%20Trading%20Days%20Chart%20Set.pdf")],
        md_extra=["S&P 500 : record de clôture 1 565,15 le 9 octobre 2007, point bas 676,53 le 9 mars 2009 (−56,8 %), nouveau record 1 569,19 le 28 mars 2013 ; indice dividendes réinvestis revenu à son pic le 2 avril 2012 ; 5 881,63 fin 2024 (≈ 3,76 fois le record de 2007, hors dividendes).",
                  "Montants en euros : variation de l'indice appliquée à 10 000 €, sans effet de change.",
                  "Faits connus : faillite de Lehman Brothers (15 septembre 2008), banques islandaises (octobre 2008), sauvetage de Fortis (2008), aides à la Grèce (2010), à l'Irlande (2010) et au Portugal (2011), « whatever it takes » de Mario Draghi (juillet 2012), baisse d'environ 19 % en 2011, Nikkei (34 ans pour retrouver le record de 1989)."],
        tags="pov investing, worst time to invest, invested at the top, 2008 financial crisis, stock market crash 2008, lehman brothers, s&p 500 2007 2009, should i sell in a crash, stay invested, buy and hold, investing in europe, personal finance europe",
        hashtags="#investing #personalfinance #stockmarket",
        thumbs="X6 (« YOU BOUGHT HERE »), W4 (calendrier) et W1 (€10,000)", next="la vidéo POV 200 € par mois, annoncée dans la voix off"),
}
