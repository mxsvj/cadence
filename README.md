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
- `sw.js` — le service worker. Il n'a qu'un rôle, afficher les notifications
  reçues ; il ne met **rien** en cache, exprès (voir plus bas).
- `manifest.json`, `icon-192.png`, `icon-512.png` — ce qu'il faut pour que
  l'app s'installe sur l'écran d'accueil.
- `.github/workflows/rappels.yml` — le réveil régulier du minuteur.

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

## L'entraînement

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

Objectif calculé, pas mesuré : Mifflin-St Jeor pour le métabolisme de repos
(poids, taille, âge, sexe), un coefficient pour la journée hors sport, puis la
dépense des séances réellement inscrites au carnet. Sèche, maintien et prise
déplacent le total ; les protéines suivent le poids.

**Apple Santé est hors de portée.** Une app web n'a aucun accès à HealthKit, même
installée sur l'écran d'accueil : Apple ne l'ouvre qu'aux apps natives. D'où
l'estimation, annoncée comme telle à l'écran.

Il n'y a pas non plus de base d'aliments ni de lecture de code-barres : cela
suppose un abonnement à une base externe. L'app retient en revanche ce qui a déjà
été saisi, pour ne pas le retaper.

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

**Les années de salle** : une case par jour, d'autant plus verte que la journée
a été remplie. Un jour actif se lit dans le journal et non dans le calendrier —
une habitude créée aujourd'hui n'était pas « prévue » le mois dernier, mais ce
qui a été validé ce jour-là a bien eu lieu.

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

Deux fonctions de l'app de référence sont restées de côté, et pour des raisons
différentes :

- le **coach** qui répond en langage naturel suppose un fournisseur d'IA payé au
  message ;
- le **scan morphologique** est une fonction payante sans méthode publiée : il
  n'y a rien à reproduire honnêtement.

Les compléments, eux, sont là — c'est une case à cocher, Cadence ne dose rien et
ne conseille rien là-dessus.

## Développement

Un serveur local sert l'application et la vraie fonction, branchée sur un Redis en
mémoire — pratique pour dérouler le scénario à deux téléphones sans rien déployer.
Les suites de tests pilotent Chromium avec Playwright : parcours complet, tutoriel
et verrouillage, états de démarrage, rendu clair et sombre, géométrie du
projecteur, et synchronisation entre deux appareils.

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
