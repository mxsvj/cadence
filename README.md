# Cadence

Tracker d'habitudes en un seul fichier, pensé pour l'écran d'accueil d'un iPhone.

- `index.html` — toute l'application : HTML, CSS et JavaScript. Aucune dépendance
  hors les polices Google *Barlow Condensed* et *Manrope*.
- `api/_store.js` — accès à Redis, partagé par les fonctions. Le préfixe `_`
  empêche l'hébergeur d'en faire une route.
- `api/board.js` — le classement entre amis.
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

## Développement

Un serveur local sert l'application et la vraie fonction, branchée sur un Redis en
mémoire — pratique pour dérouler le scénario à deux téléphones sans rien déployer.
Les suites de tests pilotent Chromium avec Playwright : parcours complet, tutoriel
et verrouillage, états de démarrage, rendu clair et sombre, géométrie du
projecteur, et synchronisation entre deux appareils.

Les notifications se testent de bout en bout sans dépendre d'Apple ni de Google :
un faux service de notification reçoit les envois, les déchiffre avec la clé de
l'appareil simulé, et permet de vérifier le contenu réellement livré — puis de
rejouer les cas pénibles (appareil devenu injoignable, panne passagère, deux
minuteurs rapprochés, fuseau horaire décalé).
