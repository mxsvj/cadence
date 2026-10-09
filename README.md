# Cadence

Carnet d'entraînement en un seul fichier, pensé pour l'écran d'accueil d'un
iPhone. On y compose ses séances, on les déroule série par série, et tout
s'inscrit : les charges, la récupération muscle par muscle, les calories.

Il a d'abord été un tracker d'habitudes avec du sport dedans, puis six onglets,
puis un jeu de points. Il est redevenu une chose : un carnet. Les habitudes y
tiennent en une bande sur l'accueil, et c'est assez.

- `index.html` — toute l'application : HTML, CSS et JavaScript. Aucune dépendance
  hors les polices Google *Barlow Condensed* et *Manrope*.
- `api/_store.js` — accès à Redis, partagé par les fonctions. Le préfixe `_`
  empêche l'hébergeur d'en faire une route.
- `api/account.js` — le compte Google et la sauvegarde des données.
- `api/push.js` — les notifications : abonnements, minuteur, envoi.
- `api/food.js` — les aliments : recherche et code-barres, via Open Food Facts.
- `sw.js` — le service worker. Il n'a qu'un rôle, afficher les notifications
  reçues ; il ne met **rien** en cache, exprès (voir plus bas).
- `manifest.json`, `icon-192.png`, `icon-512.png` — ce qu'il faut pour que
  l'app s'installe sur l'écran d'accueil.
- `.github/workflows/rappels.yml` — le réveil régulier du minuteur.
- `test/` — les suites, à lancer avec `bash test/tout.sh`. Elles vivaient dans
  un dossier temporaire de session ; un redémarrage de machine les a effacées,
  d'où leur place ici.
- `.github/workflows/verifier.yml` — à lancer à la main après un déploiement :
  il appelle la page et le contrôle de santé de chaque fonction, puis demande un
  vrai code-barres à Open Food Facts. C'est la façon la plus rapide de savoir si
  une panne vient du code, de la base ou du déploiement.

## Trois onglets

Il y en avait six : Jour, Sport, Stats, Habitudes, Journal, Profil. Six endroits
où chercher la même chose — l'état de la journée se racontait sur quatre d'entre
eux, en anneau, en points, en tuiles de records et en phrases de bilan.

**Entraînement** est l'accueil : la séance du jour, les habitudes en une bande,
la semaine, la récupération, les records, la charge sur l'année, le carnet, la
régularité. **Journal** : poids, nutrition, repas, humeur. **Profil** : le
compte, les rappels, l'aide.

Il n'y a plus de portail « valide ta journée » avant d'accéder au reste. Le
verrou servait à forcer un rituel ; se faire barrer la route pour consulter sa
séance n'avait pas de sens.

## Ce qui est parti, et pourquoi

**Le jeu social.** XP, douze rangs, vingt-quatre badges, Crew, classement entre
amis, défis de la semaine. Dans une app qu'une personne utilise seule, c'était
quatre écrans vides — « pas encore de groupe », « 1 joueur », aucun ami — et
dix-neuf badges gris sur vingt-quatre. Ça supposait de convaincre des proches
d'installer une application web ; ça n'arrive pas. Partis avec : `api/board.js`,
`api/crew.js` et toute la synchronisation qui allait avec.

**Les points.** Dix par tâche, cinq de bonus dans l'heure. Ils ne servaient qu'à
nourrir l'XP. Ce qui reste, et qui veut dire quelque chose : la série en cours,
la meilleure série, le pourcentage de régularité.

**Les niveaux de force.** La carte affichait « Novice » sur les cinq mouvements
et « 130 kg pour Intermédiaire » en dessous, d'après des seuils rapportés au
poids de corps. Les records restent — ce sont tes charges ; la comparaison à des
inconnus est partie.

**Les redites.** L'état de la journée apparaissait en anneau, en points, en
série, dans six tuiles de records, dans trois cartes de bilan et dans une liste
des sept derniers jours. Il reste le calendrier du mois et deux séries.

Au total : environ 1 800 lignes en moins, sans perdre une seule fonction qui
servait.

## Ce qui est stocké, et où

Sur le téléphone (`localStorage`) : les habitudes et leurs étapes, l'historique
des validations, le carnet de séances, les notes du journal, les humeurs, le
poids, les repas, le profil. Rien de tout cela ne sort de l'appareil.

Sans compte, **rien ne part en ligne** : plus de classement, donc plus de fiche
publique.

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

## Brancher la base Redis

Elle sert au compte Google (sauvegarde), aux rappels et au cache des aliments.
Sans elle, l'application marche quand même : tout vit dans le navigateur.

1. Sur Vercel, ouvrir le projet → **Storage** → ajouter une base **Redis**
   (l'offre gratuite suffit largement), puis la relier à ce projet.
2. Vercel injecte les identifiants tout seul, quel que soit le produit choisi.
   Les fonctions savent joindre Redis de deux façons et prennent celle qui est
   disponible :
   - **en HTTP**, si la base expose une API REST — `KV_REST_API_URL` /
     `KV_REST_API_TOKEN`, ou `UPSTASH_REDIS_REST_URL` /
     `UPSTASH_REDIS_REST_TOKEN` (cas d'Upstash) ;
   - **en TCP**, si elle ne fournit qu'une chaîne de connexion — `REDIS_URL`
     ou `KV_URL` (cas du Redis natif de Vercel). Ce chemin utilise `ioredis`,
     installé par Vercel à la construction — avec `web-push`, ce sont les deux
     seules dépendances du projet.
3. Redéployer, puis ouvrir **`/api/account`** ou **`/api/food`** : le champ
   `store` (ou `cache`) à `true` dit que la base répond.

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

Les jours d'une séance sont **facultatifs** : sans jour elle reste dans la
bibliothèque et se lance quand on veut, alors qu'une habitude récurrente sans
jour ne reviendrait jamais — là, c'est toujours une erreur.

L'entraînement est depuis devenu l'accueil, et la suite `structure.js` mesure la
barre d'onglets plutôt que de la croire : aucun onglet ne déborde de l'écran,
aucun libellé n'est tronqué. C'est elle qui a trouvé la barre restée calée sur
six colonnes alors qu'il n'y en avait plus que trois.

### Ce qu'il y a dans l'onglet

Une séance n'est pas un objet à part : c'est une tâche du jour avec
`kind:'seance'` et une liste d'exercices. Tout ce qui existait — le choix de la
journée, la série, les rappels — continue de marcher sans une ligne de plus.

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
   muscle n'est coloré. Il a son propre jeton, `--corps` : tracé en `--line`,
   il était à un cheveu du fond de la carte et la tête flottait dans le noir ;
2. les muscles par-dessus, en retrait d'environ un point du bord. Ce lisieré
   neutre qui dépasse **est** le trait de séparation : on obtient la définition
   sans dessiner un seul contour.

La première version posait un fuseau par membre et une plaque par masse du
tronc. C'était commode à régler, mais un pectoral rectangulaire ne ressemble à
rien. Désormais chaque muscle porte sa forme, et surtout **ses chefs sont
séparés** : les quatre étages du grand droit plus l'oblique, les deux
faisceaux du deltoïde, les deux chefs du pectoral, les trois masses de la
cuisse (vaste externe large en dehors, droit fémoral étroit au milieu, vaste
interne bas en dedans), les deux jumeaux du mollet plus le soléaire, les trois
chefs du triceps, les deux faisceaux du trapèze, les deux colonnes de
l'érecteur du rachis. **Vingt-trois formes sur la face, vingt sur le dos**, là
où il y en avait huit et neuf.

#### Un corps d'athlète, pas un mannequin

La silhouette était celle d'une personne mince : les muscles avaient beau
être justes, ils n'avaient pas la place d'être gros. Le corps lui-même a donc
été épaissi, mesures à l'appui (relevées sur le tracé rendu, pas estimées) :

| | avant | après | |
|---|---|---|---|
| épaules (demi-largeur) | 31,8 | 35,6 | +12 % |
| bras | 10,9 | 13,2 | +21 % |
| avant-bras | 8,2 | 9,6 | +17 % |
| dorsaux (demi-largeur) | 19,0 | 21,8 | +15 % |
| **taille** (demi-largeur) | 15,4 | 15,2 | **−1 %** |
| cuisse | 17,6 | 21,2 | +20 % |
| mollet | 15,0 | 17,8 | +19 % |

La taille ne bouge pas pendant que tout s'élargit : c'est ce rapport-là qui
fait le V, pas la largeur d'épaules seule.

Les quarante-trois formes n'ont pas été reprises à la main. Chaque point d'un
muscle a été **reporté à sa position relative dans le membre** — du bord
externe au bord interne. Un muscle qui occupait 70 % de la cuisse en occupe
toujours 70 %, mais la cuisse est plus épaisse ; un facteur supplémentaire
les fait mordre un peu plus sur les bords.

Deux pièges s'y cachaient, tous deux attrapés à la mesure :

- les bornes du membre doivent venir de la **géométrie rendue**, pas d'une
  interpolation entre les repères du profil. `lisse()` trace une courbe qui
  rentre en deçà de la corde, et un muscle calé sur la corde sort du corps ;
- les jours de l'axe — écart sternal, ligne blanche — gardent leur largeur en
  **absolu**. Les étirer avec le tronc soude les deux pectoraux.

#### Le relief

Un aplat de couleur reste un autocollant, si juste soit le contour : ce qui
fait lire un muscle, c'est son **volume**. Chaque masse reçoit donc un dégradé
clair-en-haut / sombre-en-bas, et un trait sombre sur le pourtour qui creuse
le sillon entre deux chefs.

Le dégradé est en **alpha pur** — du blanc et du noir transparents. Il se pose
donc aussi bien sur la couleur d'état que sur le corps neutre, et il suit les
deux thèmes sans qu'on ait à l'écrire deux fois. Il est en coordonnées de
boîte englobante : chaque masse est éclairée pour elle-même. Un seul dégradé
sur tout le corps n'aurait donné du volume à personne.

Le sillon doit se lire comme une **ombre**, pas comme un trou. C'est tout
l'enjeu des abdominaux : des étages séparés laissaient voir le corps entre
eux, et le ventre devenait une gaufre. Ils sont maintenant **jointifs**,
posés sur une colonne continue ; leurs traits se confondent en un seul sillon,
et le dégradé de chaque étage fait le bombé.

#### Les formes

Trois outils, parce qu'un muscle n'est pas un fuseau :

- `chefLong()` — un chef de muscle long : un ventre renflé, une pointe
  effilée, et une largeur réglable aux deux bouts. C'est ce qui donne aux
  quadriceps, aux ischios et aux mollets leur galbe au lieu d'un bâton ;
- `brique()` — un étage du grand droit : coins arrondis, **bord central
  droit**, et un léger rétrécissement vers le bas. Les coins arrondis des deux
  côtés donnaient une gaufre, pas des abdominaux ;
- `goutte()` — la larme du vaste interne, juste au-dessus du genou.

Le tronc garde des tracés écrits à la main, là où la forme porte le sens : le
pectoral en éventail depuis le sternum, le V des dorsaux qui se resserre sur
les lombaires, la masse ronde du fessier.

**L'ordre de tracé fait partie du dessin.** Au dos, les dorsaux passent avant
le trapèze : dans l'autre sens le trapèze disparaît dessous et il ne reste
qu'un bouclier. C'est le chevauchement qui creuse le V. Le même procédé sert
ailleurs : le chef claviculaire du pectoral et le faisceau antérieur du
deltoïde sont posés **par-dessus** leur masse, et c'est leur trait qui dessine
le sillon — on n'a jamais à tracer une rainure séparée.

Un `<use>` qui pointe dans le vide ou un `d` mal fermé ne dessine rien du tout,
et ça ne se voit qu'à l'œil : `corps.js` demande donc au navigateur la boîte
englobante de chaque tracé rendu, et échoue si l'un d'eux est plat ou sort du
cadre 120×258.

Il vérifie aussi qu'**aucun muscle ne sort du corps** : il échantillonne le
contour de chaque tracé et demande au navigateur si le point tombe dans la
silhouette. Ça n'est pas une précaution théorique — quatre débordements réels
sont passés sous le nez, dont un du côté de l'axe où le miroir les recouvrait.

### Comment elle est construite

Elle est construite, pas dessinée à la main. Un contour est une **liste de
repères anatomiques** — sommet du crâne, tempe, mâchoire, trapèze, aisselle,
taille, hanche, genou, cheville — que `lisse()` relie par une courbe de
Catmull-Rom convertie en Bézier cubique. La courbe passe par les points :
corriger une épaule, c'est corriger un nombre, pas une poignée de contrôle.
Seule la moitié gauche est décrite, la droite est son reflet.

Deux tracés continus par moitié : le tronc avec la tête et la jambe d'un côté,
le bras de l'autre. Le bras est à part pour qu'il pende le long du corps avec un
vrai jour entre les deux — fusionné au tronc, il ferait une moufle.

Une masse qui touche l'axe du corps passe par `contreAxe()` : on lisse le profil
externe, et on referme d'un trait droit. Fermer la courbe sur elle-même ferait
gonfler le bord central — un pectoral en forme de cœur.

### Le dessin d'un exercice

La silhouette dit quels muscles travaillent. Elle ne dit pas **quel geste** on
fait — et dans une liste de six exercices, c'est le geste qu'on cherche du
regard. Chaque exercice du catalogue porte donc son propre dessin.

Quarante-trois dessins à la main auraient dérivé les uns des autres. On décrit
plutôt quarante-trois **positions** : sept articulations (tête, épaule, coude,
main, bassin, genou, pied) et, par-dessus, un corps. La pose ne peut pas être
incohérente avec l'exercice, puisqu'elle *est* l'exercice — et corriger un
bras, c'est corriger deux nombres.

#### Un corps, pas un bonhomme en bâtons

La première version reliait les articulations par des traits. Ça dit où sont
les articulations et rien d'autre : aucune épaule, aucune taille, un mollet
aussi épais qu'un poignet. Ça ne ressemblait pas à quelqu'un.

Chaque segment est maintenant une **masse** : un fuseau plein, plus épais à la
racine qu'au bout, avec un ventre réglable au milieu — c'est lui qui donne le
galbe du mollet et du biceps. Les deux bouts sont ronds, et **le bout rond est
l'articulation** : deux segments qui se rejoignent au coude se fondent l'un
dans l'autre, il ne reste aucune jointure à voir.

Le tronc, lui, n'est pas un fuseau. Construit ainsi, son bout rond posait un
dôme au-dessus des épaules, la tête s'y enfonçait et le bonhomme avait l'air
voûté, sans cou. Il est décrit par ses repères — base du cou, pointe d'épaule,
aisselle, taille, hanche, bas du bassin — en coordonnées « le long de l'axe du
tronc » et « en travers », de sorte que la moitié droite est la même liste au
signe près. `lisse()`, déjà écrit pour la silhouette, fait passer une courbe
par tous les points.

Deux détails qui font la différence entre un corps et un pantin :

- **le poing est centré sur la main**, pas planté au bout du bras. C'est lui
  qui doit envelopper la barre ; posé au-delà, il la traversait. La barre fixe
  est donc dessinée *dans* les mains et non au-dessus ;
- **le pied part vers l'avant et vers le bas** quand la jambe est debout, et
  prolonge le tibia quand elle est allongée. À l'horizontale pure, une figure
  vue de face avait deux palmes ; sur une pompe, les orteils s'appuient dans le
  sol, ce qui est bien ce qu'ils font.

Chaque masse est son propre tracé. Deux tracés distincts se recouvrent en
s'additionnant, là où deux sous-chemins d'un même tracé peuvent se trouer s'ils
ne tournent pas dans le même sens — un bug invisible à l'écriture et évident à
l'écran.

#### Le matériel

Il se place à partir de la pose, pas à côté d'elle : la barre fixe dans les
mains, les haltères dans les mains, le banc sous le bassin, l'estrade sous les
pieds, la corde qui part des mains et passe sous les pieds. Une pose peut en
cumuler plusieurs (`banc+barbell`, `sol+estrade`). Il reste tracé au trait,
quand le corps est un aplat : le contraste entre les deux suffit à les
distinguer sans une seule couleur.

Une figure vue de face donne son axe de symétrie et les deux bras se
dessinent ; vue de profil, le second membre n'apparaît que s'il se voit
vraiment (course, fentes, pistol squat).

Un exercice créé à la main n'a pas de pose ; la vignette retombe alors sur la
silhouette teintée des muscles qu'on lui a déclarés, qui reste vraie.

#### Ce que les tests attrapent

`dessins.js` couvre les façons de se tromper : un exercice sans dessin (ou un
dessin sans exercice), deux exercices qui partagent la même image donc une
image qui ment, et un dessin qui sort du cadre.

Ce dernier se mesure **calque par calque**, en demandant au navigateur la boîte
englobante réelle : le corps est un aplat, son contour est son étendue et il
peut aller jusqu'au bord ; le matériel est tracé, il déborde de la moitié de
son épaisseur et il faut la lui laisser. C'est cette mesure qui a trouvé la
barre du développé couché qui sortait à gauche, puis les deux squats dont le
pied touchait le bord du cadre.

### Les photos

Trente-quatre des quarante-trois exercices sont illustrés par une **photo**,
tirée du jeu de données ouvert
[free-exercise-db](https://github.com/yuhonas/free-exercise-db). Les neuf
autres gardent leur dessin construit.

**Sur la licence, disons les choses telles qu'elles sont.** Le dépôt se
présente comme domaine public, mais il ne contient aucun fichier de licence —
seulement un badge. Son amont,
[wrkout/exercises.json](https://github.com/wrkout/exercises.json), n'en a pas
davantage et vend par ailleurs un jeu de données commercial. « Domaine
public » y est donc une affirmation d'un tiers plutôt qu'une cession du
titulaire des droits. C'est un risque assumé en connaissance de cause, pas une
garantie ; la source est créditée en bas de l'onglet Sport. Les GIF d'un jeu
proprement licencié coûtent de 299 à 599 $, ce qui est exclu tant que
l'application reste gratuite.

#### Ce qu'il a fallu faire aux images

Le jeu de données donne deux prises par exercice : la position de départ et la
position finale. **Ni l'une ni l'autre n'est systématiquement la bonne** — la
position de départ d'une planche montre un homme à genoux, celle d'un squat un
homme debout. La prise est donc choisie à l'œil, exercice par exercice
(`prise.js`) : souvent la seconde, parfois la première quand c'est elle qui
porte le mouvement (dips, écarté, soulevé de terre, ATR).

Le recadrage a demandé trois essais, et l'échec est instructif :

1. le recadrage automatique de `sharp` (`strategy.attention`) choisit la zone
   la plus « dense » de l'image. Sur des photos de salle, c'est un rack de
   disques bien plus souvent que l'athlète ;
2. un cadrage écrit à la main en `[gauche, haut, côté]` — la moitié était
   fausse, parce qu'un rectangle à trois nombres se juge très mal à l'œil sur
   une planche quadrillée, et parce que j'avais lu les verticales en
   pourcentage de largeur et les horizontales en pourcentage de hauteur ;
3. ce qui marche : **un carré du côté du petit bord**, qui glisse le long du
   grand. Rien n'est jamais coupé en haut ni en bas, et il ne reste qu'un seul
   nombre à régler par photo — où se trouve l'athlète. La seule erreur
   possible est de désigner le mauvais côté de l'image, et elle se voit tout
   de suite.

Les images sortent en 360 × 360, JPEG qualité 72 : **499 Ko pour trente-quatre
photos**, soit une quinzaine de kilo-octets chacune. Elles sont servies depuis
`/exos/` et chargées en différé, donc elles ne retardent jamais l'affichage.

#### Une photo a besoin de place

Une vignette de 30 px suffisait pour un dessin — six traits, ça se lit petit.
Une photo de salle à 30 px n'est qu'une tache rouge. Les vignettes de liste
sont donc passées à **52 px** et le mode séance à **150 px**. C'est le vrai
coût des photos, et il se paie en hauteur de ligne.

`dessins.js` vérifie le dossier dans les deux sens — aucune photo déclarée
manquante, aucun fichier inutilisé — puis demande au navigateur si chaque
image se charge vraiment, si elle est carrée et si elle est assez définie. Une
image absente ne se verrait qu'en production, sinon.

### La récupération

Pour chaque muscle : quand il a travaillé pour la dernière fois, et à quel titre.
Un muscle moteur prend la durée pleine, un muscle secondaire en prend 60 %. Les
durées sont des ordres de grandeur admis, et l'écran le dit.

#### Pourquoi le feu tricolore est parti

C'était rouge vif / ambre vif / vert printemps, à saturation maximale. Deux
défauts, mesurés plutôt que supposés :

- **le rouge et le vert se confondent sous daltonisme** — ΔE 4,1 en
  deutéranopie, là où il en faut 8. Sur une carte dont le seul message est
  « ce muscle est cuit / ce muscle est frais », c'est le message même qui
  disparaît pour une personne sur douze. Toutes les variantes rouge-vert
  essayées échouent pareil : le problème est la paire, pas la nuance ;
- **l'ambre et le vert sortaient de la bande de luminosité du mode sombre**
  (0,84 et 0,77 pour une bande 0,48–0,67). Un corps au repos était un
  mannequin vert fluo : l'état le plus fréquent criait le plus fort.

#### Ce qu'il y a à la place

Les trois états sont **ordonnés** — chaud, en récupération, prêt — et
intervertir cet ordre changerait le sens. Une grandeur ordonnée ne se code pas
sur trois teintes qui se disputent l'attention, mais sur une **rampe d'une
seule teinte** dont la clarté suit l'intensité. Plus de paire à confondre : la
lecture tient à la clarté, qui survit à tous les daltonismes.

Et c'est la **fatigue** qui porte la couleur, pas le repos. « Prêt » est le pas
le plus proche du corps neutre, donc un corps reposé reste calme et le corps
s'allume là où on a travaillé. L'état fréquent se tait, l'état rare se voit —
c'est l'inverse de ce que faisait le feu tricolore.

Rouge, parce que sur un muscle le rouge veut dire « n'y touche pas » dans
toutes les applis de sport. Et il ne marche pas sur les plates-bandes du bleu
de l'app, qui reste le signal « sélectionné ».

Chaque thème a ses **propres pas**, choisis contre sa propre surface — un
simple miroir du mode sombre ne tiendrait pas :

| état | sombre | clair |
|---|---|---|
| prêt à travailler | `#6D4F4E` | `#B99896` |
| en récupération | `#B45C5B` | `#B85F5E` |
| chaud | `#FF6367` | `#AC0024` |

Les deux rampes passent les quatre contrôles ordinaux : clarté monotone, écart
entre pas ≥ 0,06 (0,12 ici), teinte unique (étalement 1° et 0°), et pas le plus
proche du fond ≥ 2:1 (2,34:1 et 2,63:1). `corps.js` les refait à chaque
exécution, donc une retouche qui casse la rampe échoue au test.

La couleur n'est jamais seule à porter le sens : la légende et la liste
« muscle par muscle » nomment chaque état en toutes lettres.

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

## L'onglet Athlète

L'onglet Profil se dédouble : les réglages d'un côté (compte, rappels, aide),
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

```bash
bash test/tout.sh
```

Huit suites, 146 vérifications, pilotant Chromium avec Playwright. Elles ne
dépendent d'aucun serveur : la page est ouverte en `file://` et toute requête
sortante est coupée.

| suite | ce qu'elle garde |
|---|---|
| `syntaxe.js` | le script de la page se parse |
| `fumee.js` | on visite tout et on clique sur **toutes** les actions sans une erreur |
| `structure.js` | trois onglets, l'entraînement en accueil, aucune trace du jeu social |
| `seance.js` | composer une séance, la dérouler série par série, la retrouver au carnet |
| `images.js` | une image par exercice, jamais la même deux fois, jamais hors cadre |
| `corps.js` | la rampe de récupération reste une rampe valide dans les deux thèmes, et les muscles tiennent dans la silhouette |
| `journal.js` | poids, besoins caloriques, repas, humeur |
| `fab.js` | le bouton + s'efface en descendant et revient en remontant |

`fumee.js` est la plus bête et la plus utile : elle énumère tous les `data-act`
de chaque onglet et appuie dessus. Une fonction supprimée mais encore appelée ne
se voit qu'à ce moment-là, et c'est ce qui arrive après une grosse coupe.

Une première version de ces suites — vingt fichiers, 832 vérifications — vivait
dans un dossier temporaire de session. Un redémarrage de machine l'a effacée.
D'où celle-ci, dans le dépôt : plus petite, mais elle existera encore demain.

Le déploiement se vérifie à part, avec `.github/workflows/verifier.yml` : il
appelle le vrai site, les quatre fonctions, cinq photos d’exercices et un vrai
code-barres chez Open Food Facts. C'est la façon la plus rapide de savoir si une
panne vient du code, de la base ou du déploiement.
