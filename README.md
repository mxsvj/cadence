# Cadence

Tracker d'habitudes en un seul fichier, pensé pour l'écran d'accueil d'un iPhone.

- `index.html` — toute l'application : HTML, CSS et JavaScript. Aucune dépendance
  hors les polices Google *Barlow Condensed* et *Manrope*.
- `api/board.js` — une fonction sans serveur, uniquement pour le classement entre amis.

## Ce qui est stocké, et où

Sur le téléphone (`localStorage`) : les habitudes et leurs étapes, l'historique des
validations, les notes du journal, les humeurs, le poids, les badges, le profil.
Rien de tout cela ne sort de l'appareil.

En ligne (base Redis) : uniquement de quoi afficher le classement — blaze, avatar,
points du jour, de la semaine et du mois, XP. Ces enregistrements expirent après
90 jours sans activité.

Il n'y a ni compte ni mot de passe. L'identifiant de chaque joueur est un tirage au
hasard qui fait office de clé : le code ami se donne à ses potes, pas en public.

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
     seule dépendance du projet, installée par Vercel à la construction.

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

## Développement

Un serveur local sert l'application et la vraie fonction, branchée sur un Redis en
mémoire — pratique pour dérouler le scénario à deux téléphones sans rien déployer.
Les suites de tests pilotent Chromium avec Playwright : parcours complet, tutoriel
et verrouillage, états de démarrage, rendu clair et sombre, géométrie du
projecteur, et synchronisation entre deux appareils.
