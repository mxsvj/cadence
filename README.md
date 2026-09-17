# Cadence

Tracker d'habitudes en un seul fichier, pensé pour l'écran d'accueil d'un iPhone.

- `index.html` — toute l'application : HTML, CSS et JavaScript. Aucune dépendance
  hors les polices Google *Barlow Condensed* et *Manrope*.
- `api/_store.js` — accès à Redis, partagé par les fonctions. Le préfixe `_`
  empêche l'hébergeur d'en faire une route.
- `api/board.js` — le classement entre amis.
- `api/crew.js` — les groupes : code d'invitation, membres, défis.
- `api/account.js` — le compte Google et la sauvegarde des données.
- `api/push.js` — les notifications : abonnements, minuteur, envoi.
- `api/food.js` — les aliments : recherche et code-barres, via Open Food Facts.
- `sw.js` — le service worker. Il n'a qu'un rôle, afficher les notifications
  reçues ; il ne met **rien** en cache, exprès (voir plus bas).
- `manifest.json`, `icon-192.png`, `icon-512.png` — ce qu'il faut pour que
  l'app s'installe sur l'écran d'accueil.
- `.github/workflows/rappels.yml` — le réveil régulier du minuteur.
- `.github/workflows/verifier.yml` — à lancer à la main après un déploiement :
  il appelle la page et le contrôle de santé de chaque fonction, puis demande un
  vrai code-barres à Open Food Facts. C'est la façon la plus rapide de savoir si
  une panne vient du code, de la base ou du déploiement.

## Ce qui est stocké, et où

Sur le téléphone (`localStorage`) : les habitudes et leurs étapes, l'historique des
validations, les notes du journal, les humeurs, le poids, les badges, le profil.
Rien de tout cela ne sort de l'appareil.

En ligne (base Redis), sans compte : uniquement de quoi afficher le classement —
blaze, avatar, points du jour, de la semaine et du mois, XP. Ces enregistrements
expirent après 90 jours sans activité. L'identifiant de chaque joueur est un
tirage au hasard qui fait office de clé : le code ami se donne à ses potes, pas
en public.

Le Crew ajoute, pour chaque groupe : son nom, son code, la liste des identifiants
de ses membres et ses défis en cours. Les fiches des membres sont celles du
classement — le groupe ne duplique rien, il les rassemble. Tout expire après six
mois sans activité.

En ligne, avec un compte Google : en plus, la totalité des données ci-dessus,
rangées telles quelles sous le compte, pour les retrouver sur un autre téléphone.
Le serveur ne les inspecte pas, il les horodate et les rend. Si les rappels sont
activés, s'y ajoutent les adresses d'abonnement des appareils et le décalage
horaire de chacun — c'est ce qui permet de prévenir à la bonne heure.

## Mettre le compte Google en service

Sans configuration, l'application fonctionne : elle propose simplement de tout
garder dans le navigateur, et le bouton de connexion indique qu'il n'est pas
configuré.

1. Sur [console.cloud.google.com](https://console.cloud.google.com), créer un
   projet, puis **APIs & Services → Credentials → Create credentials → OAuth
   client ID**, type **Web application**.
2. Dans **Authorized JavaScript origins**, ajouter l'adresse du site
   (`https://…vercel.app`), sans barre oblique finale.
3. Reporter l'identifiant client obtenu dans `api/account.js`, ou le déclarer
   sur Vercel comme variable d'environnement `GOOGLE_CLIENT_ID` — celle-ci
   prend le pas sur la valeur inscrite dans le code.
4. Ouvrir `/api/account` : la réponse doit contenir `"google":true`.
5. Passer l'écran de consentement **en production**. Tant qu'il reste en
   « test », seules les adresses inscrites comme utilisateurs de test peuvent
   se connecter. Les autorisations demandées se limitent au nom, à la photo et
   à l'adresse : aucune validation par Google n'est nécessaire.

L'identifiant client n'est pas un secret : il figure dans le code de toute page
qui propose une connexion Google. Ce qui protège le compte, c'est la liste des
origines autorisées côté Google, et la vérification du jeton côté serveur — on
refuse un jeton émis pour une autre application, expiré, ou que Google ne
reconnaît pas.

## Mettre le classement en service

L'application fonctionne sans rien faire : tant qu'aucune base n'est branchée, la
route répond `501`, et chacun s'échange son code à la main comme avant.

Pour activer le classement automatique :

1. Sur Vercel, ouvrir le projet → **Storage** → ajouter une base **Redis**
   (l'offre gratuite suffit largement), puis la relier à ce projet.
2. Vercel injecte les identifiants tout seul, quel que soit le produit choisi.
   La fonction sait joindre Redis de deux façons et prend celle qui est
   disponible :
   - **en HTTP**, si la base expose une API REST — `KV_REST_API_URL` /
     `KV_REST_API_TOKEN`, ou `UPSTASH_REDIS_REST_URL` /
     `UPSTASH_REDIS_REST_TOKEN` (cas d'Upstash) ;
   - **en TCP**, si elle ne fournit qu'une chaîne de connexion — `REDIS_URL`
     ou `KV_URL` (cas du Redis natif de Vercel). Ce chemin utilise `ioredis`,
     installé par Vercel à la construction — avec `web-push`, ce sont les deux
     seules dépendances du projet.

   Le champ `transport` de la vérification indique lequel des deux est en
   service.
3. Redéployer, puis ouvrir **`/api/board?check=1`** dans un navigateur. Cette
   adresse ne se contente pas de lire la configuration : elle écrit une clé dans
   la base, la relit, l'efface, et rapporte le résultat.
   - `"redis":"ok"` — tout est en place, le classement se synchronise seul.
   - `"redis":"absente"` — les variables ne sont pas arrivées au déploiement.
   - `"redis":"injoignable"` — les identifiants sont là mais la base ne répond pas.

   Le champ `cles` indique le nombre d'entrées dans la base : il augmente dès que
   quelqu'un ouvre l'application.

Dès lors, un seul des deux amis a besoin de coller un code : le lien est posé dans
les deux sens, et chacun voit l'autre apparaître dans son classement.

## Mettre les notifications en service

Rien à configurer : les clés de signature (VAPID) sont fabriquées au premier
appel et rangées dans la base. La clé privée ne figure donc nulle part dans le
dépôt, et il n'y a aucun secret à déclarer sur Vercel.

Il faut en revanche que la base Redis soit branchée (section précédente) : les
abonnements et les horaires des habitudes y vivent.

Côté téléphone, trois conditions — l'app doit rappeler chacune à l'écran quand
elle n'est pas remplie :

1. **l'app posée sur l'écran d'accueil.** Depuis iOS 16.4, une page web ouverte
   dans un onglet Safari ne peut pas notifier ; une app installée, si. C'est ce
   que `"display": "standalone"` dans le manifeste rend possible.
2. **un compte relié.** Savoir *quand* prévenir demande de connaître les
   habitudes et leurs horaires : ils viennent des données du compte.
3. **les rappels activés** dans Profil › Rappels, une fois par appareil.

Le bouton **Tester** envoie une notification tout de suite : c'est la façon de
vérifier la chaîne complète depuis le téléphone.

### Le minuteur

`POST /api/push` avec `{"action":"tick"}` regarde qui a une tâche dont l'heure
vient de passer (dans les 45 minutes), et envoie **une** notification par tâche
et par jour. L'appel est sans effet s'il est rejoué : une trace par compte et
par jour empêche les doublons, et un verrou de 45 secondes écarte deux appels
rapprochés. Il n'a donc pas besoin d'être protégé par un secret.

Le déclencheur est une action programmée GitHub (`.github/workflows/rappels.yml`)
plutôt qu'une tâche planifiée Vercel : l'offre gratuite de Vercel ne permet
qu'un passage par jour. Sur un dépôt public, les actions programmées sont
gratuites. Deux choses à savoir :

- GitHub désactive les actions programmées d'un dépôt resté 60 jours sans
  activité ; un commit suffit à les relancer.
- L'heure n'est pas garantie à la minute près : un passage peut arriver avec
  quelques minutes de retard. La fenêtre de 45 minutes est là pour ça.

L'adresse appelée est inscrite dans le fichier du workflow : si le site change
d'adresse, c'est la ligne `CIBLE` qu'il faut corriger.

### Pourquoi le service worker ne met rien en cache

C'est délibéré. Une app servie depuis un cache local finit par afficher une
vieille version pendant des jours, et c'est exactement le genre de panne qu'on
ne peut plus diagnostiquer à distance. Chaque ouverture va chercher la page sur
le réseau. Le numéro de version affiché en bas du profil permet de vérifier d'un
coup d'œil quelle version est ouverte.

## Les années de salle

Dans l'onglet Stats, sous le mois : une case par jour de l'année, d'autant plus
verte que la journée a été remplie. Le mois donne le détail, l'année donne la
forme générale — les trous se voient mieux de loin.

Tout le style tient dans une seule feuille, ce qui rend les collisions de noms
silencieuses : deux règles peuvent porter la même classe sans se gêner, jusqu'au
jour où les deux décident de la mise en page. C'est arrivé — la liste des
muscles s'appelait `.mgrid` comme la grille du mois et passait après dans la
feuille, ce qui mettait le mois sur deux colonnes. Un contrôle vérifie
désormais qu'aucune classe ne reçoit deux fois des règles de placement, et
mesure le nombre de colonnes réellement obtenu.

Un jour actif se lit dans le journal et non dans le calendrier : une habitude
créée aujourd'hui n'était pas « prévue » le mois dernier, mais ce qui a été
validé ce jour-là a bien eu lieu.

## L'entraînement

Le sport a son onglet, et **une séance n'est plus une tâche du jour**. C'est le
changement de la v14, et il répare une confusion : une heure de salle n'est pas
une case à cocher. Elle ne se coche pas, elle se compose, se déroule série par
série et laisse des charges derrière elle.

Concrètement, les séances quittent trois endroits et en gagnent un :

- `habitsFor()` les écarte, donc elles n'occupent plus de créneau dans le
  « 3 tâches sur 5 » ni dans le dénominateur des statistiques ;
- `scheduledFor()` les écarte aussi, sinon l'écran de choix proposerait de
  « planifier » une séance qu'on ne retrouverait ensuite nulle part ;
- `visibleHabits()` les écarte : elles se gèrent dans Sport, avec leurs
  exercices sous la main, pas dans la liste des habitudes ;
- `seancesFor()` et `seancesVisibles()` les rassemblent pour le nouvel onglet.

En revanche `dayPoints()` lit le journal brut, donc **les points restent** : l'XP,
le rang, le classement entre amis et les défis du Crew continuent de voir les
séances. Ce sont deux comptes distincts, pas deux mondes.

Deux détails qui découlent du même principe. Le Sport n'est **pas verrouillé**
par la validation de la journée : le verrou existe pour qu'on pose sa journée
avant d'aller consulter des chiffres, et s'entraîner n'est pas consulter. Et les
jours d'une séance sont devenus **facultatifs** : sans jour elle reste dans la
bibliothèque et se lance quand on veut, alors qu'une habitude récurrente sans
jour ne reviendrait jamais — là, c'est toujours une erreur.

Six onglets tiennent dans 390 px en retirant la gouttière, en resserrant le
bourrage latéral et en descendant le libellé d'un point. La suite `sport.js`
mesure la barre plutôt que de la croire : aucun onglet ne déborde de l'écran,
aucun libellé n'est tronqué.

### Ce qu'il y a dans l'onglet

Une séance n'est pas un objet à part : c'est une tâche du jour avec
`kind:'seance'` et une liste d'exercices. Tout ce qui existait — le choix de la
journée, les points, la série, le classement, les rappels — continue de marcher
sans une ligne de plus, et une séance validée vaut exactement une tâche validée.

Le catalogue compte une quarantaine d'exercices, chacun avec ses muscles
moteurs, ses muscles secondaires, son matériel et ce qu'il compte (répétitions,
secondes ou minutes). On peut en ajouter à la main ; ils rejoignent le catalogue
sans distinction.

Ce qui a été réellement fait est rangé dans le journal du jour, avec les
identifiants d'exercice recopiés : le carnet survit à une séance modifiée ou
supprimée. Une séance cochée sans avoir été déroulée inscrit ce qui était prévu —
sinon le carnet et la récupération resteraient vides alors que la séance a bien
eu lieu.

### La silhouette

Elle est refaite en **deux couches**, et c'est ce qui la rend lisible :

1. un corps complet en teinte neutre — tête, cou, tronc, bras, jambes. Il est
   toujours là, donc la silhouette se lit comme un corps même quand aucun
   muscle n'est coloré ;
2. les muscles par-dessus, en retrait d'environ un point du bord. Ce lisieré
   neutre qui dépasse **est** le trait de séparation : on obtient la définition
   sans dessiner un seul contour.

La première version posait un fuseau par membre et une plaque par masse du
tronc. C'était commode à régler, mais un pectoral rectangulaire ne ressemble à
rien. Désormais chaque muscle porte sa forme, et surtout **ses chefs sont
séparés** : les six faisceaux du grand droit, les trois masses de la cuisse
(vaste externe, droit fémoral, et le vaste interne en goutte au-dessus du
genou), les deux jumeaux du mollet dont l'interne descend plus bas, les deux
colonnes de l'érecteur du rachis. Seize formes sur la face, quatorze sur le
dos, là où il y en avait huit et neuf.

Le tronc garde des tracés écrits à la main, où la forme compte (le pectoral et
sa ligne du bas qui redescend vers le sternum, le V des dorsaux, le losange du
trapèze). Les membres, eux, restent construits avec `fuseau()` — un chef de
muscle est un fuseau, et c'est le bon outil.

Un `<use>` qui pointe dans le vide ou un `d` mal fermé ne dessine rien du tout,
et ça ne se voit qu'à l'œil : `sport.js` demande donc au navigateur la boîte
englobante de chaque tracé rendu et échoue si l'un d'eux est plat.

### Comment elle est construite

Elle est construite, pas dessinée à la main : deux primitives — un fuseau pour
les membres, une plaque pour les masses du tronc — et la moitié gauche
seulement, la droite est son reflet. L'anatomie se corrige en changeant trois
nombres plutôt qu'une courbe de Bézier. Le même dessin sert en grand pour la
récupération et en tout petit sur chaque exercice.

### La récupération

Pour chaque muscle : quand il a travaillé pour la dernière fois, et à quel titre.
Un muscle moteur prend la durée pleine, un muscle secondaire en prend 60 %. Les
durées sont des ordres de grandeur admis, et l'écran le dit. Le code couleur est
un feu tricolore et pas la palette de la marque : sur un muscle, le rouge veut
dire « n'y touche pas » dans toutes les applis de sport, et c'est plus fort que
la cohérence chromatique.

## La nutrition

Le besoin du jour se calcule en trois morceaux, tous affichés à l'écran :

1. **le repos** — Mifflin-St Jeor (poids, taille, âge, sexe) ;
2. **la journée hors sport** — le repos multiplié par 1,25 (assis), 1,45 (debout)
   ou 1,65 (métier physique). Ces coefficients ne couvrent que le NEAT : les
   séances arrivent au point suivant, et les compter deux fois est l'erreur la
   plus fréquente de ce genre de calcul ;
3. **les séances du carnet** — en MET (Compendium of Physical Activities), pas
   en kcal par minute.

### Pourquoi les chiffres ont changé en v13

La première version sous-estimait le maintien, et de beaucoup. Deux corrections :

- **les coefficients d'activité** valaient 1,15 / 1,30 / 1,45, c'est-à-dire moins
  que le plancher sédentaire admis (1,2 chez Harris-Benedict comme dans les
  tables FAO/OMS). Ils valent maintenant 1,25 / 1,45 / 1,65 ;
- **la dépense d'une séance** était forfaitaire : 8 kcal la minute en force,
  10 en cardio, quel que soit le corps. Elle passe au MET : `kcal/min =
  (MET − 1) × 3,5 × poids / 200`. Le poids de corps compte enfin — à effort
  égal, 95 kg dépense bien plus que 60 — et on retire un MET parce que ces
  minutes-là sont déjà comptées au point 2.

Deux pièges évités au passage. D'abord, les valeurs du Compendium se rapportent
à la **séance entière**, repos entre les séries compris, pas aux seules secondes
sous la barre : n'appliquer le MET qu'au temps sous tension donnerait quarante
calories pour une heure de muscu. On déduit donc le mélange d'exercices du temps
d'effort, puis on l'applique à toute la durée. Ensuite, un repos déclaré est
plafonné à trois minutes par série pour l'estimation : au-delà, on discute.

Résultat pour 80 kg / 180 cm / 30 ans, assis : le maintien passe de 2 047 à
2 225 kcal, et une heure de muscu de 480 à 390 kcal.

### Le calibrage sur la balance

C'est la partie qui rend le chiffre vraiment juste. Aucune formule ne connaît un
métabolisme : deux personnes du même gabarit peuvent avoir trois cents calories
d'écart. Mais l'app a déjà les deux mesures qu'il faut — ce qui est mangé et ce
que la balance en fait :

```
maintien réel = apport moyen − pente du poids × 7 700 kcal/kg
```

Conditions : quatre semaines de fenêtre, au moins quatre pesées espacées de
deux semaines, et au moins quatorze journées de repas notées. La pente vient
d'une régression par moindres carrés sur toutes les pesées, pas d'une différence
entre la première et la dernière : l'eau d'une seule journée suffirait à tout
renverser. Les journées où le carnet tombe sous 60 % du métabolisme de repos
sont écartées — personne ne vit à ce régime, c'est un carnet incomplet.

La mesure englobe les séances de la fenêtre : on la compare donc à ce que la
formule prévoyait sur la même fenêtre, séances comprises, et on ne garde que
l'**écart**, borné à ±600 kcal. Le besoin du jour reste ainsi sensible à la
séance d'aujourd'hui tout en étant recalé sur le bon métabolisme. L'écart se
coupe d'un bouton, et un maintien saisi à la main court-circuite tout le calcul.

Un objectif de sèche ne descend jamais sous le métabolisme de repos : en
dessous, ce n'est plus un déficit.

### La base d'aliments

`api/food.js` interroge **Open Food Facts** : base ouverte, tenue par des
bénévoles, sous licence ODbL, sans compte ni clé d'API. Trois millions de
produits, et rien à payer — c'est ce qui la rend compatible avec une app qui
doit rester gratuite.

Le détour par le serveur n'est pas gratuit non plus en lignes de code ; il se
justifie par trois choses : Open Food Facts demande un en-tête `User-Agent` qui
identifie l'application et un navigateur ne laisse pas le choisir ; une fiche
brute pèse parfois plusieurs centaines de kilo-octets alors que cinq champs
suffisent ; et la base est tenue par des bénévoles, donc on met en cache
(trente jours pour un code-barres, sept pour une recherche). Quand l'énergie
n'est donnée qu'en kilojoules — c'est fréquent — elle est convertie. Une fiche
sans nom ou sans calories est écartée plutôt qu'affichée à moitié.

**Deux chemins pour chercher un mot.** Open Food Facts a d'abord eu
`/cgi/search.pl`, qui interroge directement leur base ; c'est lent, et ils le
rendent volontairement fragile parce qu'il les met à genoux. En production il
rend régulièrement un 503 — c'est exactement ce qui a fait échouer la
vérification du déploiement, et c'est le genre de défaut qu'aucun test local
n'aurait montré. Ils poussent désormais `search.openfoodfacts.org`, un index
séparé fait pour ça. Cadence demande l'index d'abord et garde l'ancien en
second : si l'un tombe, chercher un yaourt continue de marcher. Les deux
réponses n'ont pas la même enveloppe (`hits` contre `products`) mais les
fiches qu'elles contiennent portent les mêmes noms de champs. La lecture d'un
code-barres, elle, passe par l'API v2 des produits, qui n'a jamais bronché.

Un mot est reclassé avant d'être rendu. Le moteur d'Open Food Facts cherche
dans tous les champs d'une fiche : demander « skyr » lui remonte d'abord des
fromages blancs dont la description cite le mot quelque part — c'est ce que
la vérification sur le vrai service a montré. Cadence retrie donc sur ce que
l'utilisateur voit vraiment, le nom du produit : ceux qui commencent par ce
qu'il a tapé, puis ceux qui le contiennent, puis le reste dans l'ordre
d'origine. La comparaison ignore les accents, parce que les fiches sont
saisies à la main et qu'ils y sont une loterie.

Le code-barres se lit avec `BarcodeDetector`, natif dans Chrome. Safari sur
iPhone ne l'a pas encore : l'app propose alors de taper les chiffres sous les
barres, ce qui donne exactement le même résultat sans embarquer une
bibliothèque de plus. La caméra est coupée par `closeSheet()`, quelle que soit
la manière dont la feuille se ferme.

Les valeurs sont toujours **pour 100 g** : un paquet ne sait pas combien on en a
mis dans l'assiette. La quantité reste à la main, et corriger les calories à la
main coupe la règle de trois.

### Pourquoi pas la photo du plat

C'est la demande la plus fréquente, et la réponse est non — pas gratuitement,
et pas honnêtement.

Reconnaître un plat demande un modèle d'image. Les bons sont facturés à l'appel,
ce qui est exactement la raison pour laquelle le coach a été retiré. Un modèle
embarqué (MobileNet sur Food-101, une dizaine de mégaoctets) serait gratuit,
mais ne résoudrait pas le vrai problème : **le gros de l'erreur n'est pas
l'identification, c'est la portion.** Des pâtes, c'est 300 ou 900 kcal selon
l'assiette, et une photo monoculaire ne donne pas un poids. La littérature sur
l'estimation par image tourne autour de 30 à 50 % d'erreur moyenne.

Ajouter ce bouton ferait joli et rendrait les chiffres *moins* justes — alors
que la demande de départ était justement plus de précision. Le code-barres, lui,
ne se trompe pas. L'aide de l'app dit la même chose, dans les mêmes termes.

**Apple Santé reste hors de portée.** Une app web n'a aucun accès à HealthKit,
même installée sur l'écran d'accueil : Apple ne l'ouvre qu'aux apps natives.

## Les icônes

Il n'y a plus un seul emoji à l'écran. Cent treize dessins vivent dans une
planche `<symbol>` en haut du fichier, tous sur la même grille : `viewBox`
24×24, `fill:none`, `stroke:currentColor`, épaisseur 1,9, bouts arrondis.
`ic(nom)` rend un `<svg class="ic"><use href="#i-nom">`, dimensionné à `1em` :
un dessin prend donc la taille et la couleur de ce qui l'entoure, et aucune
règle de style n'a eu à bouger pour le rendre à la place d'un emoji.

La traduction se fait **à l'affichage**, pas une fois pour toutes dans les
données. Un emoji choisi avant ce changement est rangé tel quel dans le
`localStorage` et peut revenir d'un autre téléphone par la sauvegarde ou du
serveur par le classement : `icoDe()` le traduit au moment du rendu, et un emoji
inconnu retombe sur un dessin neutre plutôt que de disparaître. Les cent appels
à `toast()` passent encore un emoji — c'est la façon la plus courte d'écrire
« ça a marché » au fil du code — et `toast()` le traduit en un seul endroit.

Le fichier `.ics` et les notifications système, eux, ne reçoivent plus rien :
un nom d'icône dans un titre d'événement n'aurait aucun sens, et un SVG ne
rentre pas dans une notification de l'OS.

La suite `visual.js` garde la porte : elle balaie le texte rendu des cinq
onglets et de quatre feuilles et échoue si un seul caractère emoji en sort,
vérifie que chaque nom d'icône cité dans les données existe dans la planche, et
qu'aucun `<use>` ne pointe dans le vide — un `<use>` orphelin ne dessine rien
du tout, et ça ne se voit qu'à l'œil.

## Le Crew

Le classement entre amis reste ce qu'il était : chacun colle le code de l'autre
et les deux se voient. Un groupe est autre chose — un endroit où tout le monde se
voit d'un coup, et où l'on se lance un défi commun. D'où un code par groupe, et
pas un code par personne.

L'appartenance vit sur le serveur, pas dans le téléphone : sinon quitter un
groupe depuis un appareil ne quitterait rien. La liste locale ne retient que les
codes.

Les défis se jouent du lundi au dimanche et portent sur ce que les fiches des
joueurs savent déjà dire : des répétitions d'un exercice, des séances, des séries
ou des points. Rien à calculer côté serveur, donc rien à maintenir en double.
N'importe quel membre peut en poser un : un groupe entre potes n'a pas de chef,
et le seul dégât possible est une ligne en trop.

Le code d'invitation est tiré dans un alphabet sans `0`/`O` ni `1`/`I`/`L` : il se
lit à voix haute ou se recopie d'une capture d'écran, il ne doit pas prêter à
confusion. Il n'est accepté que s'il était libre, donc deux créations simultanées
ne peuvent pas tomber sur le même.

## L'onglet Athlète

L'onglet Profil se dédouble : le joueur d'un côté (rang, badges, Crew, compte),
le corps de l'autre. Tout mettre à la suite faisait une page interminable.

**Le gabarit** rassemble ce qui sert à calculer : taille, âge, poids, sexe,
journée type, objectif.

**La couleur d'accent** se choisit parmi sept teintes. Le socle froid ne bouge
pas ; seuls `--acc`, `--acc-hi`, `--acc-soft` et `--glow` sont surchargés sur la
racine, et le code JavaScript relit le jeton pour en tirer ses demi-teintes. La
feuille de style reste donc la référence, ce choix ne fait que la surcharger.

**La saison** est une période avec un début, une durée et une ligne d'arrivée.
Elle n'ajoute ni points ni badges. Les jours se comptent de minuit à minuit,
pas d'instant à instant : sinon l'heure qu'il est déciderait du numéro du jour.

**Les zones sensibles** ne cachent rien et n'interdisent rien. Un exercice qui
charge une zone déclarée porte un repère, franc si le muscle est moteur, discret
s'il ne fait que suivre.

### Le classement de force

Cinq mouvements : squat barre, développé couché, soulevé de terre, développé
militaire, tractions. Le maximum est estimé depuis les séries inscrites
(formule d'Epley, bornée à dix répétitions au-delà desquelles elle dérive),
rapporté au poids de corps, puis comparé à des paliers observés en salle :
débutant, novice, intermédiaire, avancé, élite. Les rapports féminins sont plus
bas, et l'écart est plus marqué sur le haut du corps.

**Ce sont des repères, pas une note** — l'écran le dit, et le README le répète :
ils ne disent rien de la technique ni de la santé.

### Ce qui n'a pas été repris

Deux fonctions de l'app de référence ne sont pas là, et pour des raisons
différentes :

- le **coach** qui répond en langage naturel a été construit, puis retiré. Il
  marchait, mais chaque réponse est facturée au message par un fournisseur d'IA
  et Cadence doit rester gratuite. Le code est dans l'historique : le commit
  « Le coach : l'API Claude » et son annulation. Le reprendre, c'est un
  `git revert` et une clé `ANTHROPIC_API_KEY` chez l'hébergeur ;
- le **scan morphologique** est une fonction payante sans méthode publiée : il
  n'y a rien à reproduire honnêtement ;
- la **photo du plat** ne peut pas être à la fois gratuite et honnête — voir
  *Pourquoi pas la photo du plat* plus haut. Le code-barres la remplace, et il
  donne un chiffre juste au lieu d'un chiffre plausible.

Les compléments, eux, sont là — c'est une case à cocher, Cadence ne dose rien et
ne conseille rien là-dessus.

## Développement

Un serveur local sert l'application et la vraie fonction, branchée sur un Redis en
mémoire — pratique pour dérouler le scénario à deux téléphones sans rien déployer.
Les suites de tests pilotent Chromium avec Playwright : parcours complet, tutoriel
et verrouillage, états de démarrage, rendu clair et sombre, géométrie du
projecteur, et synchronisation entre deux appareils.

Les services extérieurs sont doublés, jamais appelés pour de vrai : un faux
service de notification qui déchiffre ce qu'il reçoit, et un faux Open Food
Facts qui répond comme le vrai — mêmes chemins, mêmes noms de champs, mêmes
pièges (l'énergie en kilojoules, une fiche sans nom, une fiche sans calories) et
trois modes : normal, vide, en panne. Une suite ne doit jamais dépendre d'un
serveur qu'on ne contrôle pas.

L'onglet Athlète a sa propre suite : couleur d'accent jusqu'au style calculé des
boutons, grille de l'année, décompte de la saison, estimation de maximum et
paliers de force, repères de zone sensible, objectif de poids, compléments.

Le Crew se déroule lui aussi à deux téléphones contre un vrai Redis : l'un crée
le groupe, l'autre colle le code, les deux se voient, et un défi lancé d'un côté
se remplit avec ce que l'autre inscrit vraiment dans son carnet.

Les notifications se testent de bout en bout sans dépendre d'Apple ni de Google :
un faux service de notification reçoit les envois, les déchiffre avec la clé de
l'appareil simulé, et permet de vérifier le contenu réellement livré — puis de
rejouer les cas pénibles (appareil devenu injoignable, panne passagère, deux
minuteurs rapprochés, fuseau horaire décalé).
