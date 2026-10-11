# Données YouTube live : « Investing in Europe, explained » (finance faceless en anglais)

- **Date de collecte :** 2026-10-11
- **Projet évalué :** une nouvelle chaîne faceless en anglais sur l'investissement depuis l'Europe : ETF UCITS, brokers européens, « pourquoi un Européen ne peut pas acheter VOO », capitalisation ou distribution, fiscalité pays par pays. Le créateur est un débutant français qui dispose de 5 à 10 h par semaine et veut en tirer un revenu.
- **Source :** uniquement le connecteur YouTube HasData (`search` et `channel`, onglet `videos`). Les outils transcript et vidéo n'ont pas été utilisés.
- **Paramètres de recherche :** `gl=us`, `hl=en`, `sortBy=views`, `date=year`, `videoType=video`. Les appels chaîne ont été faits avec `tab=videos`, `gl=us` et `hl=en`.
- **Appels utilisés : 19 sur 20 autorisés** (8 recherches et 11 appels chaîne). Aucun n'a échoué, aucune erreur d'authentification.
- **Règle appliquée :** aucun chiffre n'est extrapolé. Une donnée que l'outil n'a pas renvoyée est notée « inconnu ». L'outil chaîne arrondit les vues (par exemple « 114K » devient 114 000). L'outil search donne les vues exactes.
- **Ratio** = vues de la vidéo ÷ abonnés actuels de la chaîne. Les abonnés sont ceux d'aujourd'hui, pas ceux du jour de publication.
- **OUTLIER :** une chaîne de moins de 100 000 abonnés qui a, sur les 12 derniers mois, une vidéo à plus de 3× ses abonnés **ou** une vidéo à plus de 100 000 vues.
- **Âges :** ils sont relatifs à la date de collecte (« 4mo » = il y a environ 4 mois).

> **Biais important : les titres sont traduits automatiquement.** Avec `hl=en`, YouTube affiche les titres traduits en anglais. Exemples : FINANZFOKUS (allemand, chapitres en allemand), Pankracy (polonais), OptionsWelten (allemand), JP Azevedo (portugais), Finance Labs (français), Riki Ruiz (espagnol), FinanzNerd (allemand). Un titre en anglais ne prouve donc pas que la vidéo est en anglais. La langue a été déduite des chapitres, des descriptions et des noms de chaîne.

---

## Journal des appels

| # | Type | Requête / chaîne | Résultat |
|---|---|---|---|
| 1 | search | UCITS ETF | OK (totalResults : 34 771) |
| 2 | search | investing in Europe | OK (378 407) |
| 3 | search | can Europeans buy VOO | OK (**6**, seulement 6 vidéos) |
| 4 | search | accumulating vs distributing ETF | OK (447) |
| 5 | search | best broker Europe | OK (195 656) |
| 6 | search | VWCE | OK (392 993) |
| 7 | search | Trade Republic review | OK (313 895) |
| 8 | search | S&P 500 ETF Europe | OK (208 889) |
| 9 | channel | @thetomcrosshill | OK |
| 10 | channel | @AngeloColomboFi | OK |
| 11 | channel | @SmartCapitalDecoded | OK |
| 12 | channel | @FreedomByFIRE_EU | OK |
| 13 | channel | @DamienTalksMoney | OK |
| 14 | channel | @ZietInvests | OK |
| 15 | channel | @SmartMoneywithKai | OK |
| 16 | channel | @FinancialInterestcom | OK |
| 17 | channel | @MrIsmailElYacoubi | OK |
| 18 | channel | @TobyNewbatt | OK |
| 19 | channel | @TheLeanLedger101 | OK |

Les `totalResults` sont des estimations de YouTube. Ils ne mesurent ni l'offre ni la demande de façon fiable et sont donnés à titre indicatif.

---

## 1. Ce que montrent les 8 recherches

### 1.1 « UCITS ETF »

Les résultats sont très mélangés : allemand, français, américain, indien, britannique, et seulement 3 vidéos sur 20 viennent de chaînes anglophones centrées sur l'Europe.

| Vidéo | Chaîne (pays/langue) | Vues | Âge |
|---|---|---|---|
| That's how I would start investing in 2026. (titre traduit) | FINANZFOKUS (DE) | 711 471 | 10mo |
| Mon top 7 des ETF PEA pour 2026 ! | Finary (FR) | 529 403 | 9mo |
| Is Vanguard's New ETF the Only Index Fund You Need? | Damien Talks Money (UK) | 450 959 | 1mo |
| 🚨MAJOR BUY: Best Quantum Computing ETF on the Planet | Investing Simplified – Professor G (US) | 393 678 | 4mo |
| NEU! Der beste ETF für Buy & Hold in 2026 | Finanzfluss (DE) | 391 596 | 5mo |
| Neuer Vanguard ETF: Ist er besser als der FTSE All-World? | Finanzfluss (DE) | 356 111 | 2w |
| Best App for Global Stocks in India? | Amit Upadhyaya (IN) | 295 879 | 5mo |
| Vanguards New UK ETFs Just Destroyed the Competition | Toby Newbatt (UK) | 277 942 | 1mo |
| The Best ETFs to Hold FOREVER (titre traduit) | Pankracy (PL) | 277 732 | 6mo |
| Quel ETF acheter ? Top 10 des meilleurs ETF en 2026 | Matthieu Louvet (FR) | 241 636 | 9mo |
| Invest in These ETFs to Maximize Return (Ireland-Domiciled ETFs) | Ziet Invests (MY, EN) | 240 267 | 11mo |
| **How Many ETFs Should You Really Own? (European investor)** | **Tom Crosshill (EU, EN)** | 207 804 | 3mo |
| The Best ETFS For Investors in 2026 | Toby Newbatt (UK) | 202 500 | 8mo |
| **The Best World ETF To Hold Forever (2026)** | **Angelo Colombo (EU, EN)** | 166 389 | 9mo |
| **The Best ETF Investing Strategies in 2026 (European Investor)** | **Tom Crosshill** | 134 247 | 9mo |
| Mejores ETFs para Invertir en 2026 | Javi Linares (ES) | 128 593 | 8mo |
| Best Index Funds For Long Term | PensionCraft (UK) | 123 002 | 5mo |

### 1.2 « investing in Europe »

La requête est **trop large**. Elle remonte de gros généralistes britanniques (Mark Tilbury, 2 887 062 et 768 066 vues ; Nischa, 1 940 270, 1 805 635 et 1 220 747), de la macroéconomie et de l'actualité (TLDR News EU 958 400, DW News 1 166 490, Finance Bureau 721 597, Patrick Boyle 522 214) et du hors sujet (Horizon Society, citoyenneté, 1 905 908 ; PBS NewsHour, 595 628).

La seule chaîne anglophone qui parle spécifiquement aux Européens est **Tom Crosshill** :
- « 18 Years of ETF Investing: My Worst Mistakes (European Investor) » : **669 882 vues** en 11mo ;
- « How Much € Do You Need Invested to Live Off Dividends » : **601 582 vues** en 7mo.

On trouve aussi Finanzfluss (DE, 1 059 969), Finary (FR, 529 403) et Matthieu Louvet (FR, 436 928).

### 1.3 « can Europeans buy VOO » (le sujet phare du concept)

**totalResults = 6.** Toutes les vidéos sont en anglais et viennent de toutes petites chaînes.

| Vidéo | Chaîne | Vues | Âge | Durée |
|---|---|---|---|---|
| Why You (Probably) Can't Buy VOO: UCITS vs. US ETFs Explained | Smart Money (@SmartCapitalDecoded) | **8 097** | 5mo | 2:05 |
| STOP Buying VOO: The S&P 500 Concentration Trap. | Real Wealth Hack (abonnés : inconnu) | 3 905 | 7mo | 11:35 |
| CSPX vs VOO Dividend Tax for European Investors | Freedom by FIRE | 601 | 1mo | 5:19 |
| Why You Can't Buy VOO in Europe (UCITS Explained) \| Lean Ledger Ep. 2 | The Lean Ledger | 375 | 1mo | 4:40 |
| Stop Buying VOO - I Bought These 2 ETFs Instead | Two Tickers To Freedom (abonnés : inconnu, CH) | 119 | 5mo | 9:53 |
| Why Europeans Can't Buy VOO (And the ETF You Should Buy Instead) | Freedom by FIRE | 49 | 8mo | 4:59 |

→ **L'offre récente est quasi nulle sur la formulation exacte**, et la meilleure vidéo plafonne à 8 097 vues. Le filtre `date=year` exclut les vidéos de plus d'un an, qui existent peut-être et captent peut-être cette recherche : c'est **inconnu**.

### 1.4 « accumulating vs distributing ETF »

**totalResults = 447.** Le sujet est **très fragmenté et surtout traité en langue locale**, avec des titres traduits : indonésien, portugais (Brésil et Portugal), néerlandais, bulgare, espagnol, italien, allemand, français.

| Vidéo | Chaîne | Vues | Âge |
|---|---|---|---|
| Trik Cara Baca & Pilih Saham ETF Dunia… | Pandeka Investasi ETF (ID) | 47 848 | 4mo |
| Accumulating vs. Distributing ETFs vs. Direct Stock Investment: I Ran the Numbers (titre traduit) | JP Azevedo (BR) | 25 377 | 3mo |
| Investing €10,000? This is how we build an ETF portfolio (titre traduit) | DoopieCash (NL) | 24 101 | 7mo |
| UCITS ETFs Explained: Smart Solution to US ETF Tax Trap for Indian Investors | CA Vamika (IN, EN) | 18 812 | 5mo |
| Кой ETF е най-изгоден в България? | Finance Academy Bulgaria (BG) | 18 103 | 3w |
| ACCUMULATING vs. DISTRIBUTING (titre traduit) | El Club de Inversión (ES) | 16 885 | 2mo |
| Before You Buy an S&P 500 Fund on Trading 212, Watch This | Ismail El Yacoubi (UK, EN) | 13 832 | 9mo |
| Accumulating vs Distributing: Don't Get It Wrong! | Financial Interest (UK, EN) | 7 017 | 11mo |
| Optimizing Your Portfolio: Accumulating vs Distributing ETFs (vu sur la chaîne) | The Lean Ledger | **5** | 1mo |

→ Sur les 12 derniers mois, **aucune vidéo anglophone à destination des Européens ne dépasse 13 832 vues** sur ce sujet. La demande semble se répartir **par pays et par langue**, parce que la fiscalité diffère d'un pays à l'autre.

### 1.5 « best broker Europe »

Environ la moitié des résultats est **hors sujet** : vlog voyage (1 786 253), scalping (1 699 607), documentaire DW sur les data brokers (1 029 663), jeu de camions, bateaux, forex et MT5. La première annonce payante est celle d'Interactive Brokers.

Pertinents :
- Tom Crosshill : « The Best Strategy to Invest €500/month in Europe », 259 077 vues (3mo) ; « The Best Way to Invest Your First €10K (European Investor) », 223 709 (5mo) ; « The Best Brokerages for Investing €100K+ », 46 601 (2mo) ; « How Safe Is Your Brokerage? », 44 341 (7mo).
- Smart Money with Kai : « Interactive Brokers Tutorial: Buying ETFs the Right Way », 58 883 (5mo).
- justETF Italia : 23 423 (7mo, en italien).
- Angelo Colombo : « Interactive Brokers vs Trade Republic: Which Is Better? », **13 915** (2mo), ce qui est faible pour lui.

### 1.6 « VWCE »

La requête est **dominée par l'Italie** : Mr. RIP, Metaskill, justETF Italia × Vanguard, Dani & Dati, Karim Mejri, Matteo Ongaro, Gianluca Ranieri Bandini. On trouve aussi du tchèque, du hongrois et du français.

En anglais :
- Toby Newbatt : « The S&P 500 vs Global », 229 662 (8mo) ;
- Angelo Colombo : 166 389 et 44 234 ;
- Tom Crosshill : « One ETF is NOT All You Need (European Investor) », 126 769 (6mo).

**Une actualité chaude ressort :** le nouveau Vanguard FTSE Global All-Cap (VGLA, TER 0,07 %).
- Mr. RIP (IT) : **118 418 vues en 2 jours** ;
- Finanzfluss (DE) : 356 111 en 2 semaines ;
- Damien Talks Money : 450 959 en 1 mois ;
- Toby Newbatt : 277 942 en 1 mois ;
- Angelo Colombo : 123 000 en 1 mois ;
- Investiční brambora (CZ) : 51 649 en 3 semaines ;
- Finance Labs (FR) : 28 899 en 4 semaines.

### 1.7 « Trade Republic review »

**Aucune chaîne finance anglophone native n'apparaît dans le top 20.** L'allemand et l'espagnol dominent :
- Adrián Sáenz (ES) : « 3 Años Usando Trade Republic », **437 462 vues en 1mo**, et « Invierto 1.000€ », 157 517 ;
- Galileo (DE, TV) : 311 034 ;
- Finanzfluss (DE) : 262 094, 167 007 et 103 185 ;
- Finanztip (DE) : 190 158 et 117 085 ;
- Riki Ruiz (ES) : 173 232 ;
- FinanzNerd (DE) : 131 832 ;
- TradingFreaks (DE) : 115 881 ;
- Invertir para Conseguir (ES) : 95 445 ;
- Finect (ES) : 76 831 ;
- Überfluss (DE) : 77 028 et 60 589.

**Signal de monétisation :** Trade Republic sponsorise des créateurs **hors finance**. Ils apparaissent dans la recherche à cause du lien dans leur description : TechDale (IT, tech, 391 129), iKnowReview (DE, Thermomix, 196 723), DRWAL Rębajło (PL, cinéma, 184 120), Vet Gezellig (NL, hôtel, 101 030). → **Budget d'affiliation et de sponsoring élevé côté broker.** Les montants restent inconnus.

### 1.8 « S&P 500 ETF Europe »

Les gros généralistes ressortent encore : Mark Tilbury (2 887 033 et 768 066), Professor G (664 259), warikoo (IN, 360 607). Le français est très présent : Finary (529 403, et « MSCI World ou S&P500 ? » 301 125), Edwyn Finance (« I invest €50/month… PEA Report », **422 764**, titre traduit) et Matthieu Louvet (241 636).

En anglais pour les Européens : 5 vidéos de Tom Crosshill, dont « The Most Popular ETF in Europe Explained | Step-by-Step Guide » (200 171, 10mo) et « The AI Bubble Is About to Burst? (European Investor) » (196 733, 11mo), ainsi qu'Angelo Colombo (166 406).

→ **Le top 20 ne contient aucune vidéo anglophone du type « quel ETF S&P 500 UCITS choisir (CSPX / VUAA / SXR8) ».**

---

## 2. Tableau des chaînes appelées (abonnés, vidéo phare, ratio)

| Chaîne | Abonnés | Nb vidéos | Vidéo de référence | Vues | Âge | Ratio | Rythme observé | Médiane des vues (dernières vidéos renvoyées) |
|---|---|---|---|---|---|---|---|---|
| **Tom Crosshill** (@thetomcrosshill), EU, EN, « professional investor, 18 years », vend une formation | 243 000 | 258 | 18 Years of ETF Investing: My Worst Mistakes (European Investor) | 669 882 | 11mo | 2,76× | ≈ 5 vidéos/mois (30 en ~6 mois) | **117 500** (30 vidéos) |
| idem | | | Compound Interest Won't Make You Rich. This Will (European Investor) | 410 000 | 4mo | 1,69× | | |
| idem | | | Taxes for European Investors Made Easy | **16 000** | 2mo | 0,07× | | |
| **Angelo Colombo** (@AngeloColomboFi), EU, EN, « 9 years… with my wife », affiliation IBKR | **71 000** | 142 | The Best World ETF To Hold Forever (2026) | 166 389 | 9mo | **2,34×** | ≈ 2 vidéos/mois | 32 000 (30 vidéos) |
| idem | | | 9 Years of ETF Investing: What I Learned | 146 000 | 4mo | 2,06× | | |
| idem | | | Vanguard FTSE Global All Cap ETF: Am I Switching? | 123 000 | 1mo | 1,73× | | |
| **Smart Money** (@SmartCapitalDecoded), description générique en « we », vidéos de 2 à 9 min | **640** | 25 | Why You (Probably) Can't Buy VOO: UCITS vs. US ETFs Explained | 8 097 | 5mo | **12,65×** | 2 à 3/mois, irrégulier | 102 (19 vidéos) |
| **Freedom by FIRE** (@FreedomByFIRE_EU), « No US-only advice… Most FIRE content is built for Americans » | **18** | 62 | VWCE vs IWDA for European Investors | 1 100 | 3mo | 61× (absolu insignifiant) | ≈ 1/semaine | 27 (25 vidéos) |
| **The Lean Ledger** (@TheLeanLedger101), « We break down… UCITS, EU tax drag », vidéos de 3 à 8 min, lancée il y a ~1 mois | 409 | 16 | Why You Can't Buy VOO in Europe (UCITS Explained) | 375 | 1mo | 0,92× | ≈ 3 à 4/semaine (rafale de lancement) | 22 (12 vidéos) |
| **Damien Talks Money** (@DamienTalksMoney), UK | 419 000 | 276 | Is Vanguard's New ETF the Only Index Fund You Need? | 450 959 | 1mo | 1,08× | hebdomadaire | 234 000 (30 vidéos) |
| **Toby Newbatt** (@TobyNewbatt), UK, vérifié | 203 000 | 433 | Vanguards New UK ETFs Just Destroyed the Competition | 277 942 | 1mo | 1,37× | ≈ 6/mois | 64 500 (30 vidéos) |
| idem | | | I Invested £200 A Month for 6 Months - Here's What I made | 48 000 | **10 jours** | 0,24× | | |
| **Smart Money with Kai** (@SmartMoneywithKai), licence média UAE, vérifié | 174 000 | 660 | Interactive Brokers Tutorial: Buying ETFs the Right Way | 58 883 | 5mo | 0,34× | hebdomadaire | 5 600 (30 vidéos) |
| **Financial Interest** (@FinancialInterestcom), UK | **19 300** | 138 | I Let AI Invest for Me on Trading 212, Here's What Happened | **440 000** | 1mo | **22,8×** | ≈ 1/semaine | 5 200 (29 vidéos) |
| idem | | | I Tried to Earn Dividends Every Day on Trading 212, Here's What Happened | 288 000 | 7mo | **14,9×** | | |
| idem | | | Accumulating vs Distributing: Don't Get It Wrong! | 7 017 | 11mo | 0,36× | | |
| **Ismail El Yacoubi** (@MrIsmailElYacoubi), UK | 14 400 | 91 | I invested £150 every month for an entire year on Trading 212 | 27 000 | 6mo | 1,88× | ≈ 4/mois | 1 550 (30 vidéos) |
| idem | | | Before You Buy an S&P 500 Fund on Trading 212, Watch This | 13 832 | 9mo | 0,96× | | |
| **Ziet Invests** (@ZietInvests), Malaisie, vérifié | 278 000 | 743 | Invest in These ETFs to Maximize Return (Ireland-Domiciled ETFs) | 240 267 | 11mo | 0,86× | plusieurs/semaine | non calculée (chaîne surtout business Malaisie) |

**Faceless ou non :** l'outil ne le dit pas, c'est **inconnu** pour toutes les chaînes. Les indices textuels suivants restent des suppositions :
- Crosshill, Colombo, Damien, Toby, Kai, Ziet et Ismail mettent en avant une personne : « I'm… », prénom, famille, expérience.
- Smart Money, The Lean Ledger et Freedom by FIRE ont une description impersonnelle (« we ») et des vidéos courtes. Ce sont les seules qui ressemblent à un format faceless.

**Chaînes vues en recherche mais non appelées (abonnés : inconnu) :** Real Wealth Hack, Two Tickers To Freedom, PensionCraft, Professor G, Mark Tilbury, Nischa, Finanzfluss, Finary, Mr. RIP, Adrián Sáenz, FINANZFOKUS, Edwyn Finance, Matthieu Louvet, CA Vamika, Finance Labs, entre autres.

---

## 3. Outliers (selon la définition fixée)

| Chaîne | Abonnés | Vidéo | Vues | Âge | Ratio | Critère rempli |
|---|---|---|---|---|---|---|
| **Financial Interest** | 19 300 | I Let AI Invest for Me on Trading 212 | 440 000 | 1mo | 22,8× | >3× **et** >100K |
| Financial Interest | 19 300 | I Tried to Earn Dividends Every Day on Trading 212 | 288 000 | 7mo | 14,9× | >3× **et** >100K |
| **Angelo Colombo** | 71 000 | The Best World ETF To Hold Forever (2026) | 166 389 | 9mo | 2,34× | >100K |
| Angelo Colombo | 71 000 | 9 Years of ETF Investing: What I Learned | 146 000 | 4mo | 2,06× | >100K |
| Angelo Colombo | 71 000 | Vanguard FTSE Global All Cap ETF: Am I Switching? | 123 000 | 1mo | 1,73× | >100K |
| **Smart Money** (@SmartCapitalDecoded) | 640 | Why You (Probably) Can't Buy VOO | 8 097 | 5mo | 12,65× | >3× (petit en absolu) |
| Freedom by FIRE | 18 | VWCE vs IWDA for European Investors | 1 100 | 3mo | 61× | >3× techniquement, **non significatif** (18 abonnés) |

**Ne sont pas des outliers :**
- Tom Crosshill, Damien Talks Money, Toby Newbatt, Kai et Ziet dépassent 100 000 abonnés.
- Ismail El Yacoubi plafonne à 1,88× et à 27 000 vues.
- The Lean Ledger plafonne à 0,92×.

**Lecture :**
1. Le seul outlier fort, Financial Interest, est **britannique**. Son format est une **expérience sur une appli de broker** (« I let AI invest », « dividends every day »), pas un explainer.
2. Angelo Colombo montre qu'une chaîne anglophone pour Européens à 71 000 abonnés peut dépasser 120 000 à 166 000 vues sur un sujet ETF « evergreen » ou d'actualité Vanguard.
3. Le seul explainer faceless qui décolle un peu est la vidéo VOO de 2 min de Smart Money : 12,65×, mais seulement 8 097 vues. Le reste de la chaîne (budget, side hustles, sujets génériques) fait une médiane de **102 vues**. → **C'est le sujet spécifiquement européen qui marche, pas la chaîne.**

---

## 4. Saturation : qui occupe le terrain ?

**a) Les grosses chaînes finance américaines** apparaissent surtout sur les requêtes larges : Professor G (393 678 à 664 259), BWB (204 068), Angelo Castillo (554 920). Elles **ne traitent pas** les sujets UCITS, VOO-en-Europe, capitalisation/distribution ou Trade Republic. Elles ne bloquent donc pas les requêtes spécifiques.

**b) Les chaînes britanniques** sont les vrais voisins anglophones : Damien Talks Money (419 000 abonnés, médiane 234 000), Toby Newbatt (203 000, médiane 64 500), Mark Tilbury, Nischa, PensionCraft, Financial Interest. Elles sont centrées sur le Royaume-Uni (ISA, SIPP, Trading 212, InvestEngine), mais elles captent l'actualité Vanguard et les tutoriels Trading 212 que des Européens regardent aussi.

**c) Les chaînes anglophones « European investor »** forment un quasi-duopole :
- **Tom Crosshill** (243 000 abonnés, ≈ 5 vidéos/mois, médiane **117 500 vues**). Il apparaît dans 5 des 8 recherches et occupe souvent 2 à 5 places du top 20.
- **Angelo Colombo** (71 000, ≈ 2/mois, médiane 32 000).
Les deux misent sur l'expérience personnelle (« 18 years », « 9 years… with my wife ») et la crédibilité. Aucun n'est faceless selon leurs descriptions (à confirmer visuellement).

**d) Les chaînes en langue locale (non anglaises)** dominent dès que la requête est spécifique :
- **VWCE** → Italie (Mr. RIP : 118 418 vues en 2 jours) ;
- **Trade Republic** → Allemagne et Espagne (Adrián Sáenz 437 462 ; Finanzfluss ; Finanztip) ;
- **Capitalisation/distribution** → une chaîne par pays (BG, ES, IT, PT, NL, DE) ;
- **S&P 500 / PEA** → France (Finary, Edwyn Finance, Matthieu Louvet).

**e) Le format faceless ou explainer** existe mais reste **embryonnaire et sans traction** : Smart Money (640 abonnés), The Lean Ledger (409), Freedom by FIRE (18). Freedom by FIRE et The Lean Ledger affichent **presque mot pour mot le positionnement du projet** (« no US-only advice », « UCITS, EU tax drag »). Leurs médianes sont de 22 à 27 vues par vidéo, sur 16 à 62 vidéos.

**f) Demande en dehors de l'Europe :** le sujet UCITS / domiciliation irlandaise intéresse aussi des investisseurs **indiens et malaisiens** en anglais (Ziet Invests 240 267, Amit Upadhyaya 295 879, CA Vamika 18 812). L'audience « non-US investor » est donc plus large que l'Europe.

**Synthèse :** la niche anglophone « investir depuis l'Europe » a une **demande prouvée** (Crosshill, médiane 117 500) et **peu d'acteurs établis** (2). Mais :
1. ces deux acteurs vendent leur expérience, ce qu'un débutant ne peut pas faire ;
2. les clones faceless récents ne décollent pas ;
3. les sous-sujets les plus spécifiques sont captés par des chaînes en langue locale, parce que la fiscalité et les brokers diffèrent selon les pays.

---

## 5. Sous-thèmes peu servis en anglais (d'après les données)

1. **« Pourquoi je ne peux pas acheter VOO / QQQ / SCHD » et leurs équivalents UCITS (CSPX, VUAA, SXR8…)**
   - totalResults = 6 ; meilleure vidéo sur 12 mois : 8 097 vues ;
   - le seul explainer faceless qui dépasse 3× ses abonnés traite ce sujet ;
   - le top 20 de « S&P 500 ETF Europe » ne contient aucune vidéo anglophone de comparatif d'ETF S&P 500 UCITS.
2. **Les brokers européens hors Royaume-Uni (Trade Republic, Scalable, IBKR pour les Européens), en anglais**
   - aucune chaîne finance anglophone native dans le top 20 « Trade Republic review », alors que l'espagnol fait 437 462 et l'allemand plus de 100 000 ;
   - les brokers financent de l'affiliation (sponsoring Trade Republic visible chez des créateurs hors finance).
   - **Bémol :** « Interactive Brokers vs Trade Republic » de Colombo en anglais ne fait que 13 915 vues.
3. **Capitalisation vs distribution et fiscalité par pays, en anglais**
   - meilleure vidéo anglophone pour Européens sur 12 mois : < 13 832 vues ; les autres versions sont en langue locale.
   - **Bémol fort :** même Tom Crosshill ne fait que 16 000 vues avec « Taxes for European Investors Made Easy », soit 0,14× sa médiane. Le sujet est mal servi, **mais rien ne montre une forte demande en anglais**.

---

## 6. Angles de vidéos suggérés par les données

| Angle | Vidéo(s) qui le justifient |
|---|---|
| « Why you can't buy VOO in Europe — and the 3 UCITS ETFs that replace it » (court, explainer) | Smart Money, « Why You (Probably) Can't Buy VOO », 8 097 vues pour 640 abonnés (12,65×) ; totalResults = 6 |
| Série d'expérience « I invest €100/month in a world ETF on [broker] — month N results » | Toby Newbatt, « I Invested £200 A Month for 6 Months », 48 000 en 10 jours ; Ismail, « £150 every month for an entire year on Trading 212 », 27 000 (sa meilleure vidéo, 1,88×) ; Edwyn Finance (FR), « I invest €50/month… PEA Report », 422 764 |
| Expérience sur une appli : « I let AI build my ETF portfolio on Trade Republic / Scalable » | Financial Interest, « I Let AI Invest for Me on Trading 212 », 440 000 pour 19 300 abonnés (22,8×) ; « Dividends Every Day on Trading 212 », 288 000 (14,9×) |
| Paliers en euros : « How much € do you need to live off ETFs in Europe? » / « €100K → €1M » | Tom Crosshill, « How Much € Do You Need Invested to Live Off Dividends », 601 582 (2,48×) ; « Once Your Portfolio Hits This Number », 296 000 en 1mo ; « How Long to Go From €100K to €1 Million », 133 000 en 9 jours |
| Trade Republic expliqué en anglais pour les non-Allemands (« what nobody tells you ») | Adrián Sáenz (ES), « 3 Años Usando Trade Republic », 437 462 en 1mo ; Riki Ruiz, « The Hidden Truth of Trade Republic », 173 232 ; aucun anglophone natif dans le top 20 |

Pour les produits nouveaux (VGLA, baisses de frais Vanguard), les données montrent une **forte demande mais une prise immédiate** par les grosses chaînes : Mr. RIP 118 418 en 2 jours, Finanzfluss 356 111 en 2 semaines. Pour un débutant à 5 à 10 h par semaine, la réactivité nécessaire paraît difficile à tenir. C'est une interprétation, pas une mesure.

---

## 7. Note d'ouverture de la niche : 5/10

**Pour :**
- la demande en anglais est prouvée (Crosshill, médiane de 117 500 vues sur 30 vidéos ; Colombo à 71 000 abonnés dépasse 120 000 vues trois fois en 9 mois) ;
- il n'y a que 2 acteurs anglophones établis ;
- l'offre sur « VOO en Europe » est presque vide (6 résultats) ;
- l'affiliation broker est réelle (sponsoring Trade Republic, liens IBKR chez Colombo) ;
- l'audience « non-US » s'étend à l'Inde et à la Malaisie.

**Contre :**
1. les 3 chaînes au concept le plus proche (Freedom by FIRE, The Lean Ledger, Smart Money) ont des médianes de **22 à 102 vues** ;
2. les formats gagnants sont **incarnés et fondés sur l'expérience** (« 18 years », « 9 years », « I invested £X/month », « I let AI invest »), ce qui est difficile en faceless pour un débutant ;
3. les sujets spécifiques (VWCE, Trade Republic, fiscalité) sont captés par des chaînes **en langue locale** très puissantes ;
4. la fiscalité, cœur du concept, fait 16 000 vues même chez le leader ;
5. l'actualité produit est prise en quelques jours par de grosses chaînes.

---

## 8. Ce que les données ne permettent pas de savoir

- **Le volume de recherche réel** par mot-clé : `totalResults` n'est pas une mesure de demande.
- **La géographie de l'audience** : part d'Européens chez Crosshill ou Colombo, part d'Américains, d'Indiens, etc.
- **Le RPM/CPM** de cette audience (anglais mais européen) et les revenus d'affiliation réels.
- **Le caractère faceless** de chaque chaîne : l'outil ne le renvoie pas, seuls des indices textuels existent.
- **Les abonnés au moment de la publication** : les ratios utilisent les abonnés actuels.
- **Les vidéos de plus de 12 mois** (filtre `date=year`) : sur « can Europeans buy VOO », des vidéos plus anciennes captent peut-être la demande. **Inconnu.**
- **Les Shorts** : non interrogés.
- **Le biais `gl=us`** : un utilisateur basé en Europe voit peut-être d'autres résultats.
- **La langue réelle des vidéos** à titre traduit : déduite des chapitres ou descriptions, pas toujours certaine.
- **Le nombre total de vues des chaînes et leur courbe de croissance** : l'onglet `videos` ne les donne pas.
- **CTR, rétention, durée de visionnage** : non disponibles.
