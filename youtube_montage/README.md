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
- `CRYPTO_SAMPLE=0:23 python3 build_every_crypto.py` ne rend que les plans 0 à 22 (environ 2 min 30), pour valider un réglage sans attendre le rendu complet.

`build_every_crypto_thumbnails.py` génère trois miniatures sombres pour cette vidéo, à tester avec « Test & compare » :

- A : « EVERY CRYPTO » en grand avec la pastille « IN 12 MIN », la grille des 12 boîtes, et une flèche vers la case rouge « scam coins » ;
- B : une pièce « BTC » glitchée devant un mur de tickers, la plupart barrés en rouge.
- C : des pièces BTC, ETH, USDT et DOGE autour d'une grosse pièce rouge « ??? », fêlée et glitchée.

`build_every_crypto_thumbnails_dg.py` en génère quatre autres :

- D : un terminal qui « explique » chaque boîte (`[ok] bitcoin`…), avec la ligne `[!!] scam coins` en rouge ;
- E : un « 12 » géant à côté de « TYPES OF CRYPTO » ;
- F : trois cartes de krach, LUNA −99 %, FTT −90 % et NFT −95 %, tirées de la vidéo ;
- G : « ONE OF THESE ISN'T CRYPTO » avec BTC, ETH, USDT et une pièce € entourée des étoiles européennes (la réponse est l'euro numérique, chapitre 12).
