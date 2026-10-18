# Modèle de montage YouTube (chaîne anglaise, sans visage)

Démo : « The real price of a €100,000 house in France ». La voix est une voix de synthèse de démonstration ; dans les vraies vidéos, elle est remplacée par la voix off ElevenLabs.

## Style retenu

- **Sous-titres : karaoké.** Tout ce que dit la voix est sous-titré mot pour mot, dans un bandeau foncé. Chaque mot passe au jaune quand il est prononcé. Les lignes sont coupées aux virgules et aux fins de phrase, et calées sur les pauses de la voix.
- **Mouvement** : zoom lent permanent, transitions entre les plans (glissements, montée, ouverture en cercle, fondu au noir), apparitions animées avec rebond, surlignage synchronisé avec la voix, zooms « punch » sur les mots clés.
- **Habillage** : compteur « REAL COST » en haut à gauche, barre des chapitres en haut au centre, rappel « Abonne-toi » animé vers le premier tiers.
- **Son** : musique lo-fi chill qui baisse automatiquement sous la voix. Bruitages (whoosh, pop, impact, tic-tac, clochette, clic) **baissés de 6 dB**. Volume final à −14 LUFS, le niveau standard de YouTube.
- **Livrables** : vidéo 16:9 en 1080p, Short 9:16 (fond flouté, titre en haut), écran de fin de 20 s prêt pour YouTube Studio.
- **Miniature : style A.** Panneau bleu nuit en diagonale à gauche avec le chiffre d'accroche barré en rouge, la question en 2 mots (le premier en jaune), une pastille jaune et une flèche jaune vers l'élément clé de l'illustration à droite.

## Fabrication

1. `python3 build_scenes.py` : dessine les plans, anime les scènes, génère la voix provisoire, les bruitages et les transitions. Les fichiers intermédiaires vont dans `assets2/`.
2. `python3 build_final.py` : ajoute les zooms punch, le compteur, la barre des chapitres, le rappel d'abonnement, la musique lo-fi et les sous-titres. Les vidéos finales vont dans `out5/`.
3. `python3 build_thumbnails.py` : génère 3 miniatures dans le même style (prix barré, compteur, titre), à comparer avec l'outil « Test & compare » de YouTube Studio.

`build_sport_demo.py` est la démo sport (« The right way to combine running and calisthenics ») : même style, silhouettes animées, tout en un seul script.

`build_finance_demo.py` est la démo finance (« Can Europeans buy VOO? »). C'est la base la plus à jour : partir de ce script pour les prochaines vidéos. Par rapport aux autres démos :

- les fondus sur le texte et les formes semi-transparentes fonctionnent ;
- le karaoké reste calé quand le sous-titre affiche un chiffre (« 0.07% ») alors que la voix le dit en toutes lettres (table `SAY`) ;
- une mention « Not financial advice » s'affiche au début, et un récap « KEY POINTS » remplace le compteur.

`build_finance_thumbnail.py` génère sa miniature en style A.

Les scripts utilisent ffmpeg, Pillow, numpy et la police Inter. RHVoice n'est utilisé que pour la voix provisoire.

`build_finance_dark.py` monte la même vidéo VOO en style sombre, inspiré du montage de la chaîne EGO :

- fond noir et texte tapé façon terminal ;
- coupes sèches avec glitch, grain et vignette ;
- nappe d'ambiance qui change d'accord à chaque partie, avec des silences avant les révélations ;
- sous-titres karaoké discrets (gris → blanc, sans bandeau) ;
- mention « not financial advice » au début et rappel d'abonnement façon terminal ;
- Short 9:16 sur fond noir, avec le titre en haut.

Il réutilise la voix et les calculs de `build_finance_demo.py`.

`build_finance_dark_thumbnail.py` génère sa miniature : le style A en version sombre, avec le rouge comme seule couleur d'accent et une fenêtre de terminal « ERROR » comme élément clé.

`build_finance_dark_thumbnails_bc.py` génère deux autres miniatures sombres à tester contre la première avec « Test & compare » :

- B : « VOO » glitché au centre du cercle d'étoiles européen, avec un tampon rouge « BLOCKED » ;
- C : « VOO » barré → « ??? », avec deux grilles de points et « SAME 500 STOCKS ».

Il lit `thumbs/thumb_A_voo_dark.jpg` pour la planche de comparaison : lancer `build_finance_dark_thumbnail.py` avant.

`build_finance_dark_thumbnails_de.py` en génère deux de plus :

- D : « €4 / year » en très grand, avec « VOO vs EU TWIN » et « THE ONLY DIFFERENCE » ;
- E : une appli de broker en mode sombre où VOO est verrouillé, avec « LOCKED OUT? » et « EU INVESTORS ».

`build_finance_long.py` monte la version longue (environ 6 min) de la vidéo VOO en style sombre :

- 50 plans, 5 parties ;
- le texte de la voix off est dans `scripts/voo_long_script.md`, avec les sources des faits ;
- le script est autonome : voix provisoire, plans, son et sous-titres dans un seul fichier.

`build_pov_demo.py` est une démo du format histoire « POV » (1 min), dans le style sombre :

- sujet : « POV: you're 25 in Europe and invest €200 a month » ;
- compteur d'âge en haut à droite, chiffres hypothétiques à 7 % par an signalés comme tels, disclaimer à la fin ;
- format inspiré des chaînes « POV » qui cartonnent en finance (par exemple Ollie Finance), avec notre propre montage.

`build_pov_long.py` monte la version longue (environ 15 min) de l'histoire POV, en style sombre :

- 141 plans répartis en 15 chapitres, de 25 à 55 ans : crash, dettes, logement, frais cachés, arnaques, licenciement, records…
- une grille de 360 cases revient comme fil rouge : une case par mois de 200 € ;
- le texte de la voix off est dans `scripts/pov_25_europe_15min_script.md`, avec tous les chiffres et hypothèses.

`build_every_crypto.py` monte « Every Crypto Explained in 12 Minutes » (environ 11 min 40), en style sombre :

- format « Every… explained » : 12 chapitres, une « boîte » par catégorie (Bitcoin, Ethereum, autres blockchains, layer 2, stablecoins, tokens d'exchange, DeFi, memecoins, NFT, privacy coins, arnaques, euro numérique) ;
- une grille de 12 boîtes revient comme fil rouge, et chaque carte de chapitre montre la progression (« BOX 05 / 12 ») ;
- nouveaux plans : pièce avec son ticker, chaîne de blocs (qui se casse en rouge pour une panne ou un piratage), colonnes du halving, mur de tickers qui s'éteignent, cercle d'étoiles européen (MiCA), regroupement des transactions par un layer 2, frise de l'euro numérique ;
- le texte de la voix off est dans `scripts/every_crypto_12min_script.md`, avec les sources des faits. Ton éducatif, sans hype ni prédiction de prix.
- plus de mouvement, sans changer le style :
  - caméra : zoom avant plus marqué qui glisse doucement (une fois à gauche, une fois à droite), petit recul juste après chaque coupe, zoom « punch » avec une courte secousse sur les chiffres clés ;
  - texte : les titres montent comme sortis d'un masque, les chiffres défilent jusqu'à leur valeur, les lignes du terminal glissent depuis la gauche ;
  - animations continues : pièces qui flottent avec une couronne de traits qui tourne, impulsion qui parcourt la chaîne de blocs, étoiles européennes qui tournent, mur de tickers qui dérive, ligne de balayage sur la grille des 12 boîtes, point lumineux au bout des courbes ;
  - décor : poussières qui flottent devant l'image, léger glitch sur toutes les coupes (plus fort aux chapitres) ;
- de la couleur, toujours sur fond noir : chaque boîte a sa couleur (Bitcoin orange, Ethereum indigo, autres blockchains turquoise, layer 2 cyan, stablecoins vert, tokens d'exchange jaune, DeFi rose, memecoins vert anis, NFT violet, privacy coins corail, arnaques rouge, euro numérique bleu) :
  - un halo discret de cette couleur derrière chaque plan ;
  - les grands chiffres, les pièces (aux couleurs de chaque crypto), les chaînes de blocs, les courbes et les lignes `>` du terminal prennent la couleur du chapitre ;
  - la grille des 12 boîtes et la barre de progression des chapitres sont multicolores, les étoiles de l'UE jaunes sur fond bleu ;
  - le rouge reste réservé aux pertes et aux arnaques, les sous-titres restent blancs ;
- `CRYPTO_SAMPLE=0:23 python3 build_every_crypto.py` ne rend que les plans 0 à 22 (environ 2 min 30), pour valider un réglage sans attendre le rendu complet.

La voix off de `build_every_crypto.py` est générée gratuitement avec Kokoro, une voix de synthèse open source (licence Apache 2.0, usage commercial autorisé), voix britannique « Emma » (`bf_emma`) :

- installation : `pip install kokoro-onnx`, puis télécharger `kokoro-v1.0.onnx` et `voices-v1.0.bin` depuis les releases GitHub de `thewh1teagle/kokoro-onnx` dans un dossier `kokoro/` à côté du script (ou indiquer le dossier avec `KOKORO_DIR`) ;
- la voix, la langue et la vitesse se règlent en haut de la partie voix du script (`VOICE`, `VOICE_LANG`, `VOICE_SPEED`) ;
- la table `SAY` écrit les chiffres en toutes lettres et corrige la prononciation de quelques mots (« meme coin », « Peh-peh », sigles épelés).

`scripts/every_crypto_elevenlabs.txt` est le texte à coller dans ElevenLabs pour la vraie voix off :

- 14 blocs (intro, 12 chapitres, outro), chacun donnant un fichier audio (`00_intro.mp3` … `13_outro.mp3`) ;
- les chiffres sont écrits en toutes lettres et les sigles délicats épelés (« Mee-ka », « Ah-vay »…) pour être bien prononcés ;
- une balise `<break time="1.2s" />` sépare les phrases, pour recouper chaque plan dans le fichier du chapitre.

`build_every_crypto_thumbnails.py` génère trois miniatures sombres pour cette vidéo, à tester avec « Test & compare » :

- A : « EVERY CRYPTO » en grand avec la pastille « IN 12 MIN », la grille des 12 boîtes, et une flèche vers la case rouge « scam coins » ;
- B : une pièce « BTC » glitchée devant un mur de tickers, la plupart barrés en rouge.
- C : des pièces BTC, ETH, USDT et DOGE autour d'une grosse pièce rouge « ??? », fêlée et glitchée.

`build_every_crypto_thumbnails_dg.py` en génère quatre autres :

- D : un terminal qui « explique » chaque boîte (`[ok] bitcoin`…), avec la ligne `[!!] scam coins` en rouge ;
- E : un « 12 » géant à côté de « TYPES OF CRYPTO » ;
- F : trois cartes de krach, LUNA −99 %, FTT −90 % et NFT −95 %, tirées de la vidéo ;
- G : « ONE OF THESE ISN'T CRYPTO » avec BTC, ETH, USDT et une pièce € entourée des étoiles européennes (la réponse est l'euro numérique, chapitre 12).

`build_channel_logos.py` génère quatre logos de chaîne sobres (photo de profil 1024×1024, à plat, une seule couleur d'accent) et un aperçu aux tailles YouTube :

- 1, « eu. » (Euro Unboxed) : blanc sur noir, point orange ;
- 2, « EURO / UNBOXED » sur deux lignes, filet orange ;
- 3, « eu » en italique à empattements (Charter), noir sur sable ;
- 4, « dm_ » (Dark Mode Money) : blanc sur noir, curseur vert.

`build_every_crypto_thumbnails_sober.py` génère trois miniatures sobres, assorties aux logos (noir, blanc et une touche d'orange, sans néon ni glitch) :

- S1 : « EVERY CRYPTO » en grand et la liste des 12 boîtes, « Scam coins » en orange ;
- S2 : « Every crypto, explained. » en italique à empattements sur fond sable, avec 12 carrés dont un orange ;
- S3 : un « 12. » géant avec le point carré orange du logo, et « types of crypto, explained. ».

`build_channel_banner.py` génère la bannière de la chaîne « Euro Unboxed » (2560×1440, texte centré dans la zone visible sur TV, ordinateur et mobile), en noir (avec le logo 1) ou en sable (avec le logo 3), et le filigrane vidéo « eu. ». La description de la chaîne, l'identifiant et les mots clés sont dans `scripts/channel_bio.txt`.

`build_every_etf.py` monte « Every ETF Explained in 11 Minutes » (10 min 52), avec le même style et la même voix que la vidéo crypto :

- 12 chapitres, une « boîte » par type d'ETF : indiciels, pays et régions, sectoriels, thématiques, factoriels (smart beta), dividendes, obligations, monétaires, matières premières (ETC sur l'or), à levier et inverses, gestion active, ETP crypto ;
- angle européen : règles UCITS, pourquoi les courtiers européens ne vendent pas VOO (pas de document d'informations clés), parts Acc et Dist, ETC sur l'or, ETP crypto ;
- nouveaux plans : un panier qui se remplit de petits carrés (1 ETF = une part de chaque entreprise), un décodeur de nom d'ETF (fournisseur, indice, UCITS, devise, Acc), un graphique à plusieurs courbes (growth contre value, indice contre ETF 2x) ;
- la durée suit le contenu : les lignes de remplissage ont été coupées et le titre annonce la vraie durée (11 minutes), même si la vidéo crypto en annonçait 12 ;
- le texte de la voix off est dans `scripts/every_etf_11min_script.md`, avec les sources des faits ; le titre, la description avec les chapitres, les tags et les réglages sont dans `scripts/every_etf_youtube_upload.txt`, et les sous-titres dans `scripts/every_etf_subtitles_en.srt` ;
- `ETF_SAMPLE=0:20 python3 build_every_etf.py` ne rend qu'une partie des plans, comme `CRYPTO_SAMPLE`.
- `python3 ass_to_srt.py etf/subs.ass scripts/every_etf_subtitles_en.srt` convertit les sous-titres karaoké de la vidéo finale en fichier SRT à importer sur YouTube (sans chevauchement entre deux sous-titres).

`build_every_etf_thumbnails_sober.py` génère les trois miniatures sobres de cette vidéo, dans le même système que celles de la vidéo crypto : S1 « EVERY ETF » avec la liste des 12 boîtes (« Leveraged » en orange), S2 « Every ETF, explained. » sur fond sable, S3 un « 12. » géant avec « types of ETFs, explained. ».

`build_pov_25_200.py` refait « POV: You're 25 and Invest €200 a Month » (13 min 31) dans le style des vidéos crypto et ETF :

- voix Emma (Kokoro) à la place de l'ancienne voix, mêmes mouvements de caméra et de texte ;
- une couleur par décennie de la vie racontée : vingtaine orange, trentaine turquoise, quarantaine violette, cinquantaine dorée ; le rouge reste pour les pertes ;
- nouvelle carte de chapitre : une rangée de 31 carrés (un par année, de 25 à 55 ans) remplie jusqu'à l'âge du chapitre, dans les couleurs des décennies, avec l'âge en grand derrière ;
- le chapitre « The comparison trap » et 13 phrases redondantes sont coupés (15 min → 13 min 31) ; la fin renvoie maintenant vers la vidéo ETF ;
- texte dans `scripts/pov_25_200_13min_script.md`, titre, description avec chapitres, tags et réglages dans `scripts/pov_25_200_youtube_upload.txt`, sous-titres dans `scripts/pov_25_200_subtitles_en.srt` ;
- `POV_SAMPLE=0:20 python3 build_pov_25_200.py` ne rend qu'une partie des plans.

`build_pov_25_200_thumbnails_sober.py` génère ses trois miniatures sobres : P1 « €200 / month » puis « 30 years later: €244,000 » en orange, P2 « 200 euros a month, for 30 years. » sur fond sable avec 30 carrés dont le dernier orange, P3 « 25 → 55. » avec le point carré orange du logo.

Quatre vidéos au même format « boîtes », faites d'une traite (même style sombre, une couleur par boîte, voix Emma) :

| Vidéo | Fichier de montage | Durée | Boîtes |
|---|---|---|---|
| Every Investment Account in Europe Explained | `build_every_account.py` | 8 min 06 | 10 : épargne, compte-titres, compte défiscalisé (ISA, ISK, PEA…), assurance-vie, retraite individuelle, plan d'entreprise, comptes enfants, robo-advisor, compte de trading (CFD), courtier étranger |
| Every Investing Mistake Explained | `build_every_mistake.py` | 7 min 34 | 12 erreurs, de « attendre pour commencer » au « mauvais compte » |
| Every Bank Fee Explained | `build_every_fee.py` | 6 min 34 | 10 frais, dont le piège « Pay in euros? » au distributeur et le trading « gratuit » |
| POV: You Invest €10,000 at the Worst Possible Moment | `build_pov_worst_moment.py` | 5 min 31 | 6 parties, du record d'octobre 2007 à 2024, avec les vraies données du S&P 500 |

- Le nombre de boîtes suit le sujet (10, 12 ou 6) : la grille des boîtes et la carte de chapitre s'adaptent toutes seules, et le mot de la carte change (« BOX », « MISTAKE », « PART ») ;
- la voix de chaque ligne est mise en cache : relancer un rendu ou le kit ne régénère que les lignes modifiées ;
- pour chaque vidéo, `scripts/` contient le texte avec ses sources (`*_script.md`), le titre, la description avec les vrais chapitres, les tags et les réglages (`*_youtube_upload.txt`, produit par `kit.py` à partir de `kit_meta.py`) et les sous-titres (`*_subtitles_en.srt`) ;
- `build_boxes_thumbnails_sober.py` génère trois miniatures sobres par vidéo (liste des boîtes, version sable, une idée forte : « ISA. PEA. ISK. Depot? », « 12. », « “Pay in euros?” No. », « −57% »).

`make_shorts.py` découpe des Shorts verticaux (1080×1920) dans les vidéos finies : une accroche en haut (un mot clé sur fond orange), l'extrait au milieu, de gros sous-titres karaoké en dessous et le titre de la vidéo complète. `shorts_seg.py` trouve le début et la fin de l'extrait dans les sous-titres à partir de deux phrases. Les 9 premiers (3 par vidéo : crypto, ETF, POV 200 €) et leur calendrier sont dans `scripts/shorts_week1_upload.txt`. `python3 make_shorts.py --tiktok` fait les versions TikTok : la mention renvoie vers « YouTube · Euro Unboxed » et une carte de fin de 2 secondes l'affiche en grand.

`humanize.py` applique une « passe humaine » à n'importe quel montage assemblé (`python3 humanize.py build_etf.py` → `build_etf_h.py`), pour retirer ce qui faisait « généré automatiquement » :

- typo : plus d'Inter ; une seule famille, FreeSans (Helvetica libre), toujours un peu resserrée (approche négative) ;
- mise en page : les grands textes ne sont plus centrés, chaque plan a sa propre colonne à gauche avec quelques pixels de décalage ; certaines phrases clés sont collées comme un sticker papier, légèrement de travers ; la carte de chapitre est asymétrique (titre à gauche, grand numéro à droite) ;
- couleur : plus de halo derrière les plans ni de violet ; les couleurs de chapitre sont un peu désaturées ; plus de poussières ;
- mouvement : les graphismes bougent à 12 images par seconde (comme « posterize time »), la caméra est « à l'épaule » (dérive lente, micro-tremblement, recadrage avec dépassement, zooms à ressort) ;
- frappe : rythme irrégulier, pauses sur les espaces et la ponctuation ;
- rythme : la pause entre deux phrases varie (plus courte après un chapitre, plus longue avant un nouveau chapitre ou après un grand chiffre) ;
- coupes : plus de glitch à chaque coupe ; quelques chapitres seulement en ont un, d'autres une image noire, le reste en coupe franche ;
- son : plus de bruit à chaque coupe ni à chaque touche ; certains chiffres tombent dans un silence brutal, d'autres n'ont aucun son, et la musique fait un « tape-stop » avant un ou deux chapitres ;
- sous-titres : plus de karaoké centré ; des étiquettes papier à gauche, placées et inclinées légèrement différemment à chaque fois.

## Style « doodle » (inspiré de la chaîne « simple, actually »)

`build_save_money_illegal.py` fabrique « How to Save Money So Easily It Feels Illegal » dans un style complètement différent des vidéos sombres : un explainer dessiné à la main, avec peu de mots à l'écran et un personnage bâton. Le moteur de dessin est dans `doodle.py` (cairo) :

- papier crème légèrement texturé, encre presque noire, l'orange de la chaîne comme seule couleur forte, quelques aplats pastel posés un peu à côté du trait (comme une mise en couleur rapide) ;
- chaque trait est tremblé à la main et « vibre » : il est redessiné de 3 façons légèrement différentes, en boucle, 8 fois par seconde, comme une vraie animation image par image ; tout ce qui bouge est à 12 images par seconde, seule la caméra à l'épaule tourne à 30 ;
- lettrage manuscrit Gochi Hand, écrit lettre par lettre à un rythme irrégulier, avec Patrick Hand pour les petites notes et le « 1 » de Caveat Brush (celui de Gochi ressemble à un 7). Les trois polices sont libres (SIL OFL) et se téléchargent toutes seules depuis Google Fonts au premier lancement ;
- un personnage bâton (avec une mèche, sa signature) : 19 poses (montrer, hausser les épaules, réfléchir, bras levés, marcher, allongé…), des visages (sourire, inquiet, surpris, endormi…), clignements des yeux et respiration, transitions de pose avec un léger dépassement ;
- une petite bibliothèque d'objets dessinés : pièce, billet, tirelire, bocal, enveloppe, téléphone, carte, calendrier, horloge, caddie, café, maison, voiture, cerveau, bulle, barres qui poussent ;
- pas de sous-titres incrustés (les mots clés sont écrits dans le dessin) : le texte dit est livré en `.srt` pour YouTube ;
- son : piano doux et basse ronde générés, joués légèrement à côté du temps ; coupe sèche à « here's the part nobody tells you », « tape-stop » avant « Final message » ; bruit de feutre ou petit « pop » seulement sur une partie des dessins.

Le script suit la structure de « simple, actually » : ouverture sur une scène (« You get paid. For about a week, you feel rich. »), « here's the part nobody tells you », 8 systèmes numérotés, « Final message ». Les chiffres viennent de 5 études (Madrian & Shea 2001, Prelec & Simester 2001, Soman & Cheema 2011, Thaler & Benartzi 2004, Hershfield et al. 2011), listées dans `scripts/save_money_illegal_script.md`.

- `STILLS=1 python3 build_save_money_illegal.py` dessine une planche de contrôle avec la fin de chaque scène (`qa_save/`) sans rendre la vidéo ;
- `SAMPLE=0:22 python3 build_save_money_illegal.py` ne rend que les lignes 0 à 21 ;
- `python3 kit_save_money.py` écrit le titre, la description avec les vrais chapitres, les tags et les réglages ;
- `build_save_money_thumbnails.py` dessine trois miniatures dans le même style : S1 « feels ILLEGAL », S2 « saving on autopilot », S3 « your brain: NOW ».

## Livraison sur le PC

`package_videos.py` prépare un zip par vidéo (moins de 30 Mo chacun) : dedans, un dossier avec la vidéo, les 3 miniatures (la recommandée en premier), `titre.txt`, `description.txt`, `sous-titres anglais.srt` et `tags et reglages.txt`, plus un zip pour les Shorts YouTube et un pour TikTok. `ranger_mes_videos.bat` (Windows, il lance `ranger_mes_videos.ps1`) ou `ranger_mes_videos.command` (Mac), posé à côté des zips, les range dans Bureau/YouTube : chaque vidéo devient un dossier numéroté à la suite des dossiers déjà présents, et une vidéo déjà rangée (même nom de dossier) est ignorée. `kit_etf_human.py` refait les chapitres et les sous-titres de la version « passe humaine » de la vidéo ETF.

### Vidéos doodle de la nuit du 13 au 14 octobre

`doodle_video.py` regroupe tout ce qui ne change pas d'une vidéo doodle à l'autre : voix en cache, respirations entre les phrases, repères sur les mots, scènes, cartes de chapitre, rendu, piano et basse (accords et tempo différents par vidéo), bruitages rares, sous-titres `.srt`. Une vidéo ne contient plus que son texte et ses dessins :

| Vidéo | Fichier | Durée |
|---|---|---|
| Compound Interest Explained So Simply It Feels Illegal | `build_compound.py` | 4 min 56 |
| 7 Tricks Shops Use to Make You Spend More (and How to Beat Them) | `build_tricks.py` | 4 min 53 |
| How to Invest Your First €1,000 (8 Steps, in Order) | `build_first1000.py` | 4 min 20 |
| The Minimum Payment Trap (and How to Escape It) | `build_debt.py` | 4 min 29 |

- `STILLS=1 python3 build_x.py` dessine la planche de contrôle (`qa_<nom>/`), `SAMPLE=a:b` ne rend que les lignes a à b−1 ;
- `python3 kit_doodle.py compound|tricks|first1000|debt` écrit le titre, la description avec les vrais chapitres et les sources, les tags, les réglages et les sous-titres ;
- `thumbs_doodle.py` dessine les miniatures (la recommandée en premier dans chaque kit : A4, B1, C2, D2), avec un cadre à l'encre pour le mode clair de YouTube ;
- `python3 package_videos.py night2` fait les zips de ces vidéos (numérotés à partir de 9) ; le même `ranger_mes_videos.bat` les range dans Bureau\YouTube à la suite.

#### Révision du 18 octobre (skill video-use : critiques, auto-évaluation, corrections)

Chaque vidéo est passée deux fois devant un critique (rapports `out/edit/verify/critic*_<nom>.md`, non versionnés), avec correction et nouveau rendu après chaque passage. Ce qui a changé dans le moteur, pour toutes les vidéos doodle :

- **Voix** : une prise Kokoro par phrase, fondus de 30 ms, une respiration entre les phrases ; les sous-titres et les repères de dessin tombent sur ce qui est vraiment dit. Dé-esseur sur la voix.
- **Sous-titres** : découpés par longueur (52 caractères au plus), de préférence à une virgule ou devant « and », « to »… ; une expression protégée (`keep=`) n'est jamais coupée ; un sous-titre de moins de 0,9 s est fusionné avec le suivant.
- **Musique** : une nappe continue (accord tenu une octave plus haut, clochettes deux octaves plus haut, pour les haut-parleurs de téléphone), baissée sous la voix ; les « silences » sont des creux à −16 dB, jamais un vrai zéro numérique (bruit de pièce). Limiteur avant l'AAC (crête vraie sous −1 dBTP).
- **Lettrage** : une seule écriture (Gochi Hand) ; les chiffres viennent de Caveat Brush (les 1, 5 et 9 de Gochi et de Kalam se lisaient « 7 », « S », « q » ou « / ») ; les lettres sont posées une par une à leur propre chasse (les ligatures déformaient « afford ») ; gris assombri (4,8:1 sur le papier).
- **Cadrage** : chaque dessin est cadré automatiquement (jusqu'à ×1,38, en gardant sa composition décentrée), sans jamais pousser un texte sous y = 890 (zone des sous-titres YouTube sur deux lignes) ni hors des marges ; `S.noframe = True` pour un cadrage fait à la main.
- **Mouvement** (règles du skill remotion-motion-graphics adaptées au dessin) : ce qui part rétrécit et s'efface en 0,25 s (`until=`), ce qui apparaît grossit en montant, une carte de chapitre arrive comme une nouvelle feuille qui glisse ; quand une scène commence sur une page vide, l'image précédente reste jusqu'au premier trait (coupe « le son d'abord »).
- **Écran de fin** : `endcard()` dessine dès le début de la dernière phrase un rond « s'abonner » à gauche et un cadre 16:9 « vidéo suivante » à droite, puis 12,5 s d'image fixe.
- **Contrôle** : `AUDIT=1 python3 build_x.py` écrit `qa_<nom>/audit.txt` : pages vides pendant que la voix parle, plus de 4 s sans nouvel élément, textes trop petits, trop pâles, au bord ou sous les sous-titres, textes lus moins d'une seconde avant la coupe. `REMIX=1` refait seulement le son. `verify_tools/self_eval.py <nom> <module>` mesure le volume, les crêtes, les silences et fait les planches aux coupes.
- **Livraison** : `web_copy.py` encode en deux passes à la taille visée (27 Mo) au lieu d'un CRF fixe, pour donner à YouTube le meilleur fichier qui passe la limite d'envoi.
- **Rangement** : un zip qui contient `remplace.txt` est une nouvelle version : le script de rangement déplace l'ancien dossier dans `YouTube\_anciennes versions` (rien n'est supprimé) et la nouvelle version reprend son numéro ; relancé, il ne refait rien.

Changements de contenu : accroches qui montrent la miniature dès la première image, chiffres recalculés (dont l'inflation et le « vrai » taux des remises), exemple dette où avalanche et boule de neige diffèrent, avertissements sur le risque et les règles nationales, titres qui tiennent leur promesse (« The Minimum Payment Trap », « 8 Steps, in Order »).
