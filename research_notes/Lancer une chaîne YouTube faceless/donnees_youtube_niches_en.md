# Données YouTube live — 3 niches anglophones pour une chaîne faceless

- **Date de collecte :** 2026-10-09
- **Source :** connecteur YouTube HasData (`search` + `channel`, onglet `videos`). Les outils transcript et vidéo n'ont pas été utilisés.
- **Paramètres de recherche :** `gl=us`, `hl=en`, `sortBy=views`, `date=year`, `videoType=video`, sauf mention contraire.
- **Appels utilisés : 37 sur 39** (12 recherches et 25 appels chaîne). Ce total compte la recherche initiale « buying a house in France » faite avant cette session, ainsi qu'un appel en erreur 400, compté par prudence.
- **Règle appliquée :** aucun chiffre n'est extrapolé. Une donnée que l'outil n'a pas renvoyée est notée « inconnu ». Quand l'API a renvoyé une valeur visiblement corrompue (par exemple `viewsOriginal` = « 1mo ago » avec `views` = 1 000 000), elle est notée « inconnu (erreur de parsing) ».
- **Ratio** = vues de la vidéo ÷ abonnés actuels de la chaîne. Les abonnés sont mesurés aujourd'hui, pas au moment de la publication.
- **Définition d'un OUTLIER :** une chaîne de moins de 100 000 abonnés qui a, sur les 12 derniers mois, une vidéo à plus de 3× ses abonnés **ou** une vidéo à plus de 100 000 vues.
- **Âges :** ils sont relatifs (« 4mo » = il y a environ 4 mois). « 1y » est ambigu : environ 12 mois, peut-être un peu plus.

---

## Journal des appels

| # | Type | Requête / chaîne | Résultat |
|---|---|---|---|
| 1 | search | buying a house in France | fait avant cette session (données fournies) |
| 2 | search | cheap houses in France | OK (totalResults estimé : 3 757) |
| 3 | search | French property market explained | OK (204 738) |
| 4 | search | moving to France | OK (428 982) |
| 5 | search | cost of living in France | OK (346 661) |
| 6 | search | French visa long stay | OK (30 440) |
| 7 | search | hybrid athlete training | OK (301 493) |
| 8 | search | calisthenics and running | OK (299 602) |
| 9 | search | boxing workout for runners | OK (410 719) |
| 10 | search | adult swimming technique | OK (2 745) |
| 11–18 | channel | frenchconnectionshcb, french_lifestyle_johnny_benoit, TheFrenchPropertyGuide, LifeBeyondBorders-c6l, Harry_Renovating_In_France, PropertywithLauraHamilton, HouseHuntingWithBaptiste (**erreur 400**), Diego_Leon | OK sauf Baptiste |
| 19–25 | channel | BaguetteBound, AmericanToFrance, the_expat, HorizonSocietyYT, LesFrenchiesTravel, FrugalQueeninFrance, ANNASDIARY-q2t | OK |
| 26–34 | channel | ColinHJS, BUILTSIMPLETRAINING, enduranceID, coachmikenitro, BuiltByBasics69, sharmaneha-d9o (Limit Forge), joshlancasterj2, InfiniteGrit, swimWOD | OK |
| 35 | search (shorts) | hybrid athlete, `videoType=shorts` | **aucun Short renvoyé** (seulement des publicités) → inconnu |
| 36 | search | French healthcare system explained for expats (ajout hors plan, pour couvrir le volet santé/admin de B) | OK (totalResults : **10**) |
| 37 | channel | HouseHuntingWithBaptiste (relance, sans gl/hl) | OK |

Les `totalResults` sont des estimations de YouTube. Ils ne mesurent pas fiablement l'offre ni la demande et ne sont donnés qu'à titre indicatif.

---

## Niche A — « Buying a house in France » (public US/UK)

### A.1 Ce que montrent les recherches

**« buying a house in France »** (données fournies) : en tête, on trouve des contenus hors sujet ou de rénovation (Yes Theory, Italie, 3,86M ; @BelgraveVilla 4,19M ; @Diego_Leon 2,03M et 1,06M ; @HorizonSocietyYT 1,90M). Viennent ensuite des agences ou experts : French Connections HCB (363K et 358K), Viager de Johnny Benoit (288K), The Financial Diet (166K), Harry (112K), Languedoc Property Finders (84K), Laura Hamilton (63K), French Property Guide (45K) et Life Beyond Borders (38K).

**« cheap houses in France »** :

| Vidéo | Chaîne | Vues | Âge |
|---|---|---|---|
| Men Transform Abandoned French House Under $80,000 | Quantum Makers (vérifiée, abonnés non appelés) | 3 661 392 | 4mo |
| We Bought an Abandoned 300 Years Old Stone House | Diego León | 2 033 159 | 11mo |
| 10 Countries Where Cheap Land ALSO Buys You Citizenship | Horizon Society | 1 900 278 | 11mo |
| We Bought The CHEAPEST House in France (FULL TIMELAPSE) | Diego León | 1 056 751 | 4mo |
| Full Home Tour After Two Years of Transformation | Restoring La Chartreuse (abonnés inconnus) | 623 232 | 9mo |
| House hunting in Verteuil-sur-Charente (with prices) Ep.2 | French Connections HCB | 357 702 | 7mo |
| Quitting 9-to-5 to build genius off-grid homestead | Kirsten Dirksen (vérifiée) | 311 406 | 8mo |
| Buying a House in France? Beware of The "Viager" System | French Lifestyle by Johnny Benoit | 288 314 | 8mo |
| The cheapest houses in France are located in Haute-Marne (2:27) | France 3 Grand Est (vérifiée, TV) | 145 721 | 5mo |
| France's housing crisis… | FRANCE 24 English (vérifiée) | 129 974 | 8mo |
| My Dad Bought a House for €10,000 (France) | Harry Renovating in France | 111 584 | 5mo |
| Why There Are So Many Châteaux in France (And A Warning…) | The French Property Guide | 99 487 | 4mo |
| This Could be Yours!! 6 Bedroom Mini Chateau | My French Manor Tales (abonnés inconnus) | 92 201 | 10mo |
| You Can OWN a French Manor House From $90K | House Hunting with Baptiste | 80 186 | 6mo |
| The Biggest Mistakes Brits Make Buying Property in France | Property with Laura Hamilton | 62 680 | 5mo |

**« French property market explained »** : le format explicatif marché/process en anglais est **peu fourni**.
- Les premiers résultats repris sont Viager (288K) et Châteaux (99K).
- Viennent ensuite des **chaînes en français dont les titres sont traduits automatiquement** : Pretto 61K ; Immobilier 123 avec 67K, 39K, 29K et 3K ; Charbel Lakisse 39K ; Immobilier Danger 8K ; BFM Business 1,8K.
- Côté anglophone, les explicatifs restent bas : French Property Guide « Why Are Houses In Rural France So Cheap? » 15 660 (6mo), Dan Newton (French Estate Agent) 7 470 et 6 550, Ryan Weston-Bennett 5 492, France Unfiltered 2 871, Frédéric Moreau 2 546, French Tax Online « Who Does What in a French Property Purchase? » **327** (11mo).

### A.2 Chaînes (onglet videos)

| Chaîne | Abonnés | Vidéo marquante | Vues | Âge | Ratio | Rythme / notes |
|---|---|---|---|---|---|---|
| French Connections HCB (@frenchconnectionshcb) | 67 300 | House hunting in Bonnieux (with prices) Ep.1 | 362 754 | 8mo | **5,39×** | 430 vidéos. Environ 30 vidéos en 4 mois (~2/sem.). Agence de relocation, face-cam et interviews. Vidéos récentes : 568 à 91K (« Tash moved to France… » 91K, 1mo = 1,35×). |
| idem | | House hunting in Verteuil-sur-Charente Ep.2 | 357 702 | 7mo | 5,32× | |
| French Lifestyle by Johnny Benoit | 19 700 | Buying a House in France? Beware of The "Viager" System (6:29) | 288 316 | 8mo | **14,6×** | 196 vidéos, ~2/sem. Récentes : 3,1K à 27K (« Where to Buy Property in France to Avoid the Heat » 27K, 4mo = 1,37×). Une vidéo affiche « 1 000 000 » : erreur de parsing, donc inconnu. |
| The French Property Guide | 11 900 | Why There Are So Many Châteaux in France (And A Warning…) | 99 487 | 4mo | **8,36×** | 60 vidéos, ~1/sem. puis ralentissement (« Why I stopped making YouTube videos », 3 sem.). Ancien agent immobilier (Tom). |
| idem | | I Found a €25,000 Property… 3rd Most Beautiful Village | 45 000 (valeur arrondie de la recherche) | 10mo | 3,78× | Autres : « 5 Best Places to Retire in France - Based on Data! » 33K (5mo) = 2,77× ; « Why This French House Hasn't Sold In 2 Years » 17K. |
| Life Beyond Borders (@LifeBeyondBorders-c6l) | 31 200 | 10 French Villas from €65K! You Can Actually Move Into | 38 000 | 10mo | 1,22× | 63 vidéos, ~2 à 3/mois. **Format liste d'annonces « 10 homes from €X »** (faceless probable, non vérifié). Meilleure vidéo hors France : « 10 Homes in Portugal from €38K » 104K (1y) = 3,33× ; « 10 Spain Villas from €73K » 95K (9mo) = 3,04×. Vidéos France récentes : 2K à 12K. |
| Harry Renovating in France | 14 100 | Goodbye, Concrete. | 247 000 | 2 sem. | **17,5×** | 29 vidéos, ~2/mois. Vlog de rénovation face-cam. « This Makes me Nervous » 119K (1mo) = 8,44×. |
| idem | | My Dad Bought a House for €10,000 (France) | 111 584 | 5mo | 7,91× | |
| Property with Laura Hamilton | 24 100 | I Bought a Property in Spain… Here's What Really Happened | 360 000 | 6mo | 14,9× (Espagne) | 72 vidéos, ~1/sem. Présentatrice TV (mots-clés « A Place in the Sun »), donc notoriété préexistante. |
| idem | | The Biggest Mistakes Brits Make Buying Property in France | 62 680 | 5mo | 2,60× | Pas outlier sur la France. |
| Diego León | 176 000 | We Bought an Abandoned 300 Years Old Stone House | 2 033 159 | 11mo | 11,6× | 242 vidéos, ~1/sem. Rénovation. **Plus de 100K abonnés, donc hors définition outlier.** Épisodes courants : 38K à 95K. |
| idem | | We Bought The CHEAPEST House in France (FULL TIMELAPSE) | 1 056 751 | 4mo | 6,0× | |
| House Hunting with Baptiste | 7 270 | You Can OWN a French Manor House From $90K | 80 186 | 6mo | **11,0×** | 108 vidéos, ~2 à 3/sem. **Format liste d'annonces** (faceless probable, non vérifié). Toutes les autres vidéos récentes font entre 250 et 4,7K : succès isolé. |

### A.3 Outliers niche A
1. **French Lifestyle by Johnny Benoit** : Viager, 288 316 vues, **14,6×** (19,7K abonnés).
2. **Harry Renovating in France** : « Goodbye, Concrete. » 247K (**17,5×**) et « My Dad Bought a House for €10,000 » 111,6K (7,9×).
3. **House Hunting with Baptiste** : « French Manor House From $90K » 80,2K (**11,0×**).
4. **The French Property Guide** : « Châteaux » 99,5K (**8,4×**) et « €25,000 Property » 45K (3,8×).
5. **French Connections HCB** : « Bonnieux » 362,8K (**5,4×** et plus de 100K vues).
6. Life Beyond Borders : « Portugal from €38K » 104K (3,3×). Ce n'est **pas** une vidéo sur la France ; ses vidéos France plafonnent à 1,2×.
- Hors définition (plus de 100K abonnés) : Diego León, 2,03M (11,6×).

### A.4 Saturation (A)
- **Grosses chaînes :** les contenus viraux du mot-clé viennent de gros acteurs (Yes Theory, Quantum Makers, Kirsten Dirksen, médias TV ; abonnés non appelés) ou de **rénovation**, un autre format qui exige d'être sur le terrain. Sur l'achat en France proprement dit, les chaînes présentes sont **petites ou moyennes (7K à 176K)**.
- **Formats :** agences (FCHCB, Languedoc Property Finders, Dan Newton, French Tax Online), experts face-cam (Johnny Benoit, Tom, Laura Hamilton), vlogs de rénovation (Diego, Harry, Restoring La Chartreuse), listes d'annonces (Life Beyond Borders, Baptiste).
- **Faceless :** le format « liste d'annonces » existe (probablement faceless, à vérifier visuellement). Il donne des **succès isolés** (Baptiste 80K, Life Beyond Borders 38K à 104K) mais une base faible (250 à 12K). Aucun explicatif faceless « process / frais / marché » en anglais n'a été repéré. Sur « market explained », les chaînes **francophones à titres traduits** remontent en tête, ce qui ressemble à un manque d'offre anglophone. La demande réelle reste inconnue.
- Lecture : peu de concurrence directe sur l'explicatif. Les petites chaînes atteignent 5 à 15× leurs abonnés. Le plafond observé tourne autour de 100 à 360K hors rénovation.

---

## Niche B — « Moving to France » (expats anglophones)

### B.1 Ce que montrent les recherches

**« moving to France »** : les résultats sont **dominés par des vlogs face-cam et des chaînes voyage**.
- Hors sujet en tête : chanson Abraham H., 1 909 011.
- Mumbo Jumbo « I moved to France » 1 582 413 (3mo, vérifiée).
- FCHCB : Bonnieux 362 754, Verteuil 357 695, Carolyn 190 997, Rachel château 155 426.
- The Financial Diet « The New American Dream: Moving To Europe » 358 341 (vérifiée).
- Les Frenchies : 295 246 et 250 875.
- ON World Travel « LYON » 267 871 (vérifiée).
- Anaïs Laure : 243 982 et 215 396.
- FINDING ANNA : 235 590.
- Hadassah Naomi : 216 808.
- Sophie Nadeau : 212 106 (vérifiée).
- Ainsley Durose : 183 752 (vérifiée).
- inspiroue : 161 333.
- Traveling with Kristin « Brutally Honest Advice for Americans Moving to Europe » 144 977 (vérifiée).
- The New Travel : 149 960 (vérifiée).

**« cost of living in France »** : les résultats sont **dominés par du contenu général ou d'autres pays**.
- CNBC Make It (Shenzhen) 2,55M ; Horizon Society 1,90M ; CNN 526K ; JT Reacts 484K ; IWrocker 392K ; The Unretirees (Portugal) 284K ; Traveling with Kristin 239K ; Sunset Trucker « FRANCE VS CANADA » 194K.
- Sur la France spécifiquement : TFD « living in france makes me feel insane » 188 464 (1mo) ; **Frugal Queen in France 107 587 (6mo)** ; The Expat « 10 Best French Cities to Retire » 65 177 (6mo).

**« French visa long stay »** : le **plafond est bas**. La première vidéo fait 70 232 vues, et c'est un contenu sur le permis de travail visant le Bangladesh (Raj Nabab). Schengen Inde 55 088 ; Beneath the Surface 30 832 ; Baguette Bound « Moving to France in a Nutshell » 30 962 ; Tommy Sikes « #1 Reason Your French Visa Gets Denied » 30 288 ; Wali Global 27 674 ; FCHCB 15 257. **Baguette Bound apparaît 6 fois.**

**« French healthcare system explained for expats »** (recherche ajoutée) : **seulement 10 résultats**. Le maximum est Johnny Benoit « French Hospitals… » à 9 351 vues (3 sem.), puis Fired Up in France (Carte Vitale, mutuelle, budget) 6 177, Delights by Dawn 4 393, Living Well in France 1 489 et Feather Insurance 85. Il y a donc **très peu d'offre**, et une demande visible faible.

### B.2 Chaînes

| Chaîne | Abonnés | Vidéo marquante | Vues | Âge | Ratio | Rythme / notes |
|---|---|---|---|---|---|---|
| French Connections HCB | 67 300 | Bonnieux Ep.1 (voir A) | 362 754 | 8mo | 5,39× | Commune aux niches A et B. Vidéos visa et admin récentes : 605 à 3,6K (« French Visitor Visa vs Entrepreneur Visa » 605). |
| Baguette Bound | 51 300 | We Thought We Wanted City Life in France; This Happened Instead | 115 000 | 8mo | 2,24× | 118 vidéos, ~1/sem. Famille américaine face-cam et tutoriels (formulaire visa « screen by screen » 9,2K). |
| idem | | We're American Immigrants Living in France… | 101 000 | 8mo | 1,97× | « French Grocery Stores: The Unwritten Rules » 85K (3mo) = 1,66× ; « Can Americans Even Get a French Bank Account? » 25K. |
| Tommy Sikes, CFP (@AmericanToFrance) | 28 600 | The #1 Reason Your French Visa Gets Denied | 30 288 | 8mo | 1,06× | 27 vidéos seulement, **rythme très faible** (dernière vidéo il y a 4 mois). Niche retraite et fiscalité US–France. |
| The Expat (@the_expat) | 51 500 | 7 Countries Where Buying Cheap Property Gives You a Residency Visa | 129 000 | 2mo | 2,50× | 281 vidéos, ~2/sem. Listes multi-pays (faceless non vérifié). Sur la France : « 10 Best French Cities to Retire to in 2026 » 65 177 (6mo) = 1,27× ; « Why Americans Go Broke Retiring in France » 14K (13j). Deux vidéos ont une erreur de parsing : inconnu. |
| Horizon Society (@HorizonSocietyYT) | 14 900 | 10 Countries Where Cheap Land ALSO Buys You Citizenship | 1 900 278 | 11mo | **127,5×** | 124 vidéos, ~2 à 3/sem. Listes explicatives multi-pays (faceless non vérifié). **Succès isolé** : sa reprise « …Residency in 2026 » fait 4,9K (2mo) et les vidéos récentes 83 à 7,8K. |
| Les Frenchies | 479 000 | We Didn't Expect This After 5 Years in France | 295 246 | 6mo | 0,62× | 334 vidéos, ~2/sem. Couple voyage face-cam, grosse chaîne. Meilleure vidéo récente : 600K (1mo). |
| Frugal Queen in France | 50 100 | Do we regret moving to the south of france? The truth about our budget | 107 587 | 6mo | 2,15× | 913 vidéos, 3/sem. Couple de retraités britanniques, face-cam. Vidéos récentes : 3K à 27K. |
| FINDING ANNA (@ANNASDIARY-q2t) | 5 210 | I Fell in Love Online and Moved to a Tiny Village in France…4 Years Later, Reality Hit Me Hard!! | 235 590 | 3mo | **45,2×** | 26 vidéos, ~1/mois. Récit personnel face-cam. Les autres vidéos font 1,6K à 13K (plusieurs : vues inconnues, erreur de parsing). |

### B.3 Outliers niche B
1. **Horizon Society** : 1,90M, **127,5×**. Contenu multi-pays (propriété = citoyenneté), pas centré sur la France.
2. **FINDING ANNA** : 235,6K, **45,2×**. Récit personnel.
3. **French Connections HCB** : 362,8K, 5,4×.
4. **The Expat** : 129K vues (critère des plus de 100K), 2,5×. Multi-pays.
5. **Baguette Bound** : 115K et 101K (critère des plus de 100K), 2,2× et 2,0×.
6. **Frugal Queen in France** : 107,6K (critère des plus de 100K), 2,15×.

### B.4 Saturation (B)
- **Grosses chaînes et chaînes vérifiées** très présentes : Mumbo Jumbo, The Financial Diet, ON World Travel, Sophie Nadeau, Traveling with Kristin, The New Travel, Les Frenchies (479K), et des médias (CNBC, CNN, France24).
- **Formats :** une très large majorité de vlogs face-cam (installation à Paris, vie au village) et d'agences de relocation qui vendent un service (FCHCB, Baguette Bound avec cours, Tommy Sikes CFP).
- **Faceless :** seules les **listes multi-pays** (Horizon Society, The Expat) sont repérées. Aucun explicatif faceless **centré sur la France** (visa, Carte Vitale, impôts, banque) n'a été vu.
- **Contenu admin et pratique :** l'offre est faible, mais **les plafonds de vues aussi**. Visa : 71K au maximum. Santé : 9,4K au maximum. Les vidéos admin de FCHCB récentes font 0,6 à 3,6K.
- Les outliers à forte audience reposent sur une **histoire personnelle d'expatrié**, difficile à reproduire en faceless par un Français qui n'est pas expatrié, ou sur des **listes multi-pays** qui sortent du sujet France.

---

## Niche C — « Hybrid athlete with no gym » (course, natation, calisthenics, boxe)

### C.1 Ce que montrent les recherches

**« hybrid athlete training »** : les résultats sont **dominés par de gros créateurs vérifiés** (abonnés non appelés).
- Colin James « Doing Less Actually Gets You More Jacked » 1 663 586 (8mo, non vérifiée).
- eugene teo 1 494 587, 461 552, 423 782, 331 081 (vérifiée).
- Jon Hamilton « Special Forces… Unbreakable Endurance » 1 477 141 (11mo).
- OnPointFresh « how to build a HYBRID athlete physique » 1 452 016 (vérifiée).
- **Nick Bare** : 1 041 900, 549 238, 510 467, 462 471, 422 272, 388 957 (vérifiée, 6 vidéos dans les résultats).
- Daniel Buyeske 785K ; Ben Parkes 693K ; Colin James « Lifting + Running Plan » 622 854 ; Dan Churchill 589K et 449K ; Ryan Humiston 460K ; JT Performance 422K.

**« calisthenics and running »** :
- Jeremy Ethier : 3 883 841 et 1 897 032, avec « I did 30 minutes of cardio a day… running every day for 30 days » (vérifiée).
- **BUILTSIMPLE « After 20 Years of Training, I'd Only Do 5 Things » 2 199 814 (4mo)**.
- OnPointFresh 1,45M ; Joe Bartolozzi 1,38M ; Yellow Dude « What 100 squats in a row do to your body » 1 345 034 et « I jumped rope every day for 30 days » 876 163 (vérifiée).
- Rewirs 1,32M ; Browney 1,31M ; GORNATION 823K ; Gritty Soldier 667K ; Fitness Power Hour 495K.
- Built By Basics « No Gym? No Problem! » 363 098.
- Strength Side 361K ; Chris Heria 328K et 196K (vérifiée).
- **Josh Lancaster « The Right Way to Combine Lifting & Running » 309 714 (7mo)**.

**« boxing workout for runners »** : la requête est **captée par des « interactive warm-up » animés de type jeu**, faceless, visant plutôt les enfants et l'EPS : Subway Surfers 5,56M (officiel) ; ImmerZone Fitness 3,22M ; Interactive Studio 3,19M ; BlazeZone 2,96M ; Pixel Move 2,40M et 1,84M. Ensuite : GRIDFIT (musique) 1,02M ; JT Performance 422K ; cardio dance 384K ; vlogs boxe + course (Vincent Edrian 85K) ; FITNESS TV 89K ; Sweet Science of Fighting « I'm Begging You To Stop Running For Boxing » **3,7K** ; Limit Forge « Mike Tyson… Prison Strength » 9,9K (2j). **Aucune vidéo dédiée boxe + course à forte audience.**

**« adult swimming technique »** :
- **enduranceID** : 2 035 362, 863 122, 142 354.
- Baby Swim 541K ; Adult Swim (dessin animé, hors sujet) 399K ; Fares Ksebati 421K (vérifiée).
- **Coach Mike Nitro** : 319 280 et 120 895.
- Swim like Pro 287K et 124K ; Swimming By Sanuj 264K (vérifiée) ; Rocket Swimming 209K, 143K, 110K, 79K, 71K (vérifiée).
- Skills N' Talents 86K ; Kaitlin Frehling 81K ; **swimWOD 57 561** ; Siska Training 52K.

**Shorts « hybrid athlete »** : aucun Short renvoyé par l'API, donc **inconnu**.

### C.2 Chaînes

| Chaîne | Abonnés | Vidéo marquante | Vues | Âge | Ratio | Rythme / notes |
|---|---|---|---|---|---|---|
| Colin James (@ColinHJS) | 54 100 | Doing Less Actually Gets You More Jacked (5:38) | 1 663 586 | 8mo | **30,8×** | 79 vidéos, ~1,5/sem., formats courts (3 à 15 min). Musculation + course. |
| idem | | The Lifting + Running Plan I Actually Stick To | 622 854 | 10mo | 11,5× | Autres : « If I Had To Start Running Again… » 481K (4mo) = 8,9× ; « You're Training For A Body You Don't Want » 462K (1mo) = 8,5× ; « The Part of Getting Really Fit… » 255K (1mo) = 4,7× ; « The Hybrid Plan I'd Send My Brother » 200K (4mo) = 3,7×. |
| BUILTSIMPLE (@BUILTSIMPLETRAINING) | 72 100 | After 20 Years of Training, I'd Only Do 5 Things (5:40) | 2 199 814 | 4mo | **30,5×** | 121 vidéos, ~2/sem. **Poids du corps, anneaux, équipement minimal.** « The Only Exercise I'd Keep to Grow My Chest » 332K (1mo) = 4,6× ; « If I Wanted 25 Pull-Ups… » 198K (4 sem.) = 2,7× ; « How I'd Combine Running and Calisthenics With a Full-Time Job » 17K (4mo) = 0,24×. |
| enduranceID | 96 500 | Do This to STOP Sinking Legs in Swimming | 2 035 362 | 10mo | **21,1×** | 653 vidéos, ~1,5/sem. « The Only Beginner Swim Guide… » 863K (11mo) = 8,9× ; « I Bet You Will Swim Freestyle After This » 401K (5mo) = 4,2× ; récentes : 11K à 103K. |
| Coach Mike Nitro | 44 700 | How To Breathe In Freestyle With Perfect Technique | 390 000 | 1y | 8,7× | 232 vidéos, **rythme faible** (dernière vidéo il y a 4 mois, ~10 en 12 mois). « The Lazy Way to Swim Faster » 319 280 (7mo) = **7,1×** ; « How to Stop Sinking Legs » 360K (1y) ; « How To Swim As An Adult » 108K (1y). |
| Jon Hamilton (@InfiniteGrit) | 79 800 | This Is How Special Forces Operators Build Unbreakable Endurance | 1 477 141 | 11mo | **18,5×** | 597 vidéos, ~3/sem. Tactique, forces spéciales. « 5 Things I Picked Up in Special Forces… » 283K (1mo) = 3,5×. **Série « My Swimming Sucks… Week 1–4 » : 1,5K à 3K seulement.** |
| Josh Lancaster | 5 480 | The Right Way to Combine Lifting & Running (Hybrid Training Explained) | 309 714 | 7mo | **56,5×** | ~2/sem. en long format (1,1K vidéos au total, Shorts compris ou non : inconnu). Autres : 21K (4mo) = 3,8× ; 18K = 3,3× ; récentes : 133 à 8,7K. Positionnement coaching « ambitious men ». |
| Built By Basics (@BuiltByBasics69) | 60 300 | Complete Home Workout for Beginners - Full Body, No Equipment | 822 000 | 7mo | **13,6×** | **14 vidéos seulement**, aucune depuis 5 mois. Mélange anglais et hindi (« Grow Forearms HINDI » 1,3M = 21,6×). « No Gym? No Problem! Build a Killer Body at Home » 363 098 (6mo) = 6,0×. |
| Limit Forge (@sharmaneha-d9o) | 3 840 | 5 Shaolin Exercises to Build Hands So Strong… | 57 000 | 1mo | **14,8×** | 54 vidéos, ~3/sem. Pas de description, mots-clés en série, titres sur un même modèle (« Soviet / Shaolin / Spetsnaz / Prison »). Profil typique de chaîne faceless, **non vérifié visuellement**. « This ONE Shaolin Drill Builds BRUTAL Striking Power (No Bag) » 44K (2 sem.) = 11,5×. Plusieurs vidéos affichent 1M ou 2M : erreur de parsing, donc inconnu. |
| swimWOD | 1 710 | Why Your Rotation Is Killing Your Freestyle Speed (6:54) | 57 561 | 2mo | **33,7×** | 37 vidéos, ~2 à 4/mois. Marque sans personne nommée (faceless possible, non vérifié). « Why You Can't Stay Horizontal… (The Physics Nobody Explains) » 25K (4mo) = 14,6×. Les autres : 146 à 12K. |
| Nick Bare, Jeremy Ethier, eugene teo, OnPointFresh, Chris Heria | inconnu (non appelées) | | 0,3M à 3,9M | | inconnu | Badges vérifiés : probablement de grosses chaînes, nombre d'abonnés non mesuré. |

### C.3 Outliers niche C
1. **Josh Lancaster** : « Right Way to Combine Lifting & Running », 309,7K, **56,5×**.
2. **swimWOD** : « Why Your Rotation Is Killing Your Freestyle Speed », 57,6K, **33,7×**.
3. **Colin James** : « Doing Less… » 1,66M (**30,8×**), suivi d'au moins 6 autres vidéos au-dessus de 3×.
4. **BUILTSIMPLE** : « After 20 Years… 5 Things » 2,2M (**30,5×**).
5. **enduranceID** : « STOP Sinking Legs » 2,04M (**21,1×**).
6. **Jon Hamilton** : « Unbreakable Endurance » 1,48M (**18,5×**).
7. **Limit Forge** : « 5 Shaolin Exercises… » 57K (**14,8×**).
8. **Built By Basics** : « Complete Home Workout… No Equipment » 822K (**13,6×**).
9. **Coach Mike Nitro** : « Lazy Way to Swim Faster » 319K (**7,1×**).

### C.4 Saturation (C)
- **Très forte présence de grosses chaînes vérifiées**, avec des vues de 1 à 4M : Nick Bare (6 vidéos sur une seule recherche), Jeremy Ethier, eugene teo, OnPointFresh, Chris Heria. Le mot-clé « hybrid » est déjà pris.
- C'est pourtant la niche où les **outliers de petites chaînes sont les plus nombreux et les plus forts** : 9 chaînes de moins de 100K abonnés avec des ratios de 7× à 56×, dont deux de moins de 6K abonnés.
- **Formats :** explicatifs courts (4 à 8 min) au titre « If I… / The only… / Why your… » et démonstrations. Le **face-cam ou le physique à l'écran** semble fréquent (chaînes centrées sur un coach), mais ce n'est pas vérifiable sans voir les vidéos : inconnu.
- **Faceless observé :** les échauffements interactifs animés (millions de vues, mais public enfants et EPS, hors cible) et Limit Forge (petite chaîne, ratios de 11 à 15×).
- **Combinaison exacte** course + natation + calisthenics + boxe sans salle : **aucune chaîne dédiée vue** dans les résultats. Boxe + course : très peu de contenu dédié (3,7K à 89K). Les séries d'expérience hebdomadaires peuvent sous-performer : Jon Hamilton « My Swimming Sucks Week 1–4 » 1,5 à 3K, contre 283K pour ses explicatifs.

---

## Classement d'ouverture (de la plus ouverte à la plus saturée)

| Rang | Niche | Score d'ouverture /10 | Justification chiffrée |
|---|---|---|---|
| 1 | **A. Buying a house in France** | **6,5** | Pas de grosse chaîne installée sur l'achat en France (chaînes de 7K à 176K). Plusieurs petites chaînes à 5–17× (Viager 14,6× sur 19,7K abonnés ; Châteaux 8,4× ; Baptiste 11×). Les explicatifs anglais sont rares : sur « market explained », des chaînes francophones à titres traduits sont en tête et le meilleur explicatif anglophone fait 15K. Points faibles : plafond plus bas que C (environ 100 à 360K hors rénovation), listes d'annonces faceless irrégulières (base de 250 à 12K), demande réelle inconnue. |
| 2 | **C. Hybrid athlete no gym** | **5,5** | Demande énorme (vidéos de 1 à 4M) et le plus grand nombre d'outliers (9 chaînes, de 7 à 56×, jusqu'à 2,2M sur 72K abonnés). La combinaison exacte n'est pas couverte. Mais le haut des résultats est saturé par des créateurs vérifiés, le format repose sans doute sur le corps ou le visage à l'écran (inconnu), et l'expérience en série peut faire un flop (1,5 à 3K pour la série natation de Jon Hamilton). |
| 3 | **B. Moving to France** | **4,5** | Les résultats sont surtout des vlogs face-cam, des chaînes voyage vérifiées et des médias. Les outliers à forte audience viennent d'histoires personnelles d'expatriés (ANNA 45×) ou de listes multi-pays hors France (Horizon 127×, une seule fois : sa reprise fait 4,9K). Les sujets admin (visa, santé) sont peu couverts mais plafonnent bas (visa 71K, santé 9,4K, 10 résultats). Les niches A et B se recoupent : FCHCB et Johnny Benoit couvrent les deux. |

---

## Six angles de vidéo suggérés par les outliers

1. **A — « Le système français qui choque les acheteurs étrangers »**, en série : viager, notaire, compromis, préemption. Modèle : « Buying a House in France? Beware of The "Viager" System » (Johnny Benoit, 288K, 14,6×, 6:29). L'explicatif court d'un mécanisme juridique surprenant passe en faceless avec texte, schémas et annonces.
2. **A — « Pourquoi X existe en France (et le piège pour un acheteur) »**, par exemple : pourquoi les maisons rurales coûtent 20K€, pourquoi tant de châteaux, pourquoi les villages se vident. Modèle : « Why There Are So Many Châteaux in France (And A Warning About Buying One) » (French Property Guide, 99K, 8,4×).
3. **A — « What €100K buys you in [département] »**, en faceless avec carte, annonces, coûts cachés et accès. Modèles : « You Can OWN a French Manor House From $90K » (Baptiste, 80K, 11×) et « House hunting in Bonnieux (with prices) » (FCHCB, 363K, 5,4×).
4. **A et B — « Does buying a house in France get you a visa? »**, sur le mythe propriété = résidence. Modèles : « 10 Countries Where Cheap Land ALSO Buys You Citizenship » (Horizon Society, 1,9M, 127×) et « 7 Countries Where Buying Cheap Property Gives You a Residency Visa » (The Expat, 129K).
5. **C — « The no-gym hybrid week: run + swim + calisthenics + boxing in 5 h »**, avec données de montre GPS à l'écran. Modèles : « The Right Way to Combine Lifting & Running (Hybrid Training Explained) » (Josh Lancaster, 310K, 56,5×) et « The Lifting + Running Plan I Actually Stick To » (Colin James, 623K, 11,5×).
6. **C — « Why runners sink in the pool: swimming physics for runners »**, en faceless avec plans sous l'eau et animations. Modèles : « Why Your Rotation Is Killing Your Freestyle Speed » (swimWOD, 58K, 33,7× sur 1,7K abonnés) et « Do This to STOP Sinking Legs in Swimming » (enduranceID, 2,0M, 21×).
- Variante C : « Boxing without a bag — 30-day shadowboxing test (heart-rate data) ». Modèles : « This ONE Shaolin Drill Builds BRUTAL Striking Power (No Bag) » (Limit Forge, 44K, 11,5×) et « After 20 Years of Training, I'd Only Do 5 Things » (BUILTSIMPLE, 2,2M, 30,5×).

---

## Ce que les données n'ont pas pu dire
- **Demande réelle** (volumes de recherche) et **RPM / CPM** par niche : non fournis par l'outil. Les `totalResults` sont des estimations peu fiables.
- **Faceless ou non** : aucune vérification visuelle (outils vidéo et transcript interdits). Le format a été déduit des titres et descriptions seulement : « probable » partout, donc à vérifier.
- **Abonnés des grosses chaînes vérifiées** non appelées (Nick Bare, Jeremy Ethier, eugene teo, OnPointFresh, Yes Theory, Mumbo Jumbo, The Financial Diet, Quantum Makers, Kirsten Dirksen, Restoring La Chartreuse, My French Manor Tales) : inconnu.
- **Shorts** : la recherche Shorts n'a rien renvoyé, donc inconnu.
- **Marché britannique** : seul `gl=us` a été interrogé ; les résultats UK sont inconnus.
- **Dates exactes** (relatives seulement, « 1y » ambigu), **historique de croissance** et abonnés au moment du pic : inconnus. Les ratios utilisent les abonnés actuels.
- **Plusieurs vues corrompues dans l'API** (Johnny Benoit château Dordogne ; The Expat « Forbes » et « International Living » ; Limit Forge 1M/2M ; plusieurs vidéos FINDING ANNA ; Tommy Sikes ; Laura Hamilton « Air Conditioning » ; French Property Guide « Hamlet ») : notées inconnu.
- **Revenus annexes** (affiliation Wise, mutuelle Feather, cours, consultations) : présents dans les descriptions, montants inconnus.
- La personnalisation éventuelle des résultats de recherche : inconnue.
