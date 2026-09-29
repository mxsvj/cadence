# Élise

Prototype d'une IA de conversation bienveillante pour les adultes qui se sentent
seuls — d'abord les quadragénaires séparés ou divorcés.

**Prototype de test uniquement.** Pendant le développement, Élise répond avec
l'offre gratuite de l'API Gemini, dont Google peut réutiliser les données. On
n'y tape donc que des conversations fictives, jamais de vraies confidences.

## Règle d'or : zéro dépense

Tout tourne sur des offres gratuites, sans carte bancaire :

| Service  | Rôle                            | Offre                |
| -------- | ------------------------------- | -------------------- |
| Vercel   | héberge le site                 | Hobby                |
| Supabase | comptes et base de données      | Free                 |
| Gemini   | le modèle qui fait parler Élise | gratuite (AI Studio) |

Aucune étape ne demande d'activer la facturation. Si un écran le propose, on
refuse.

## Ce que fait cette version

- **Connexion / inscription** par e-mail et mot de passe (`/connexion`).
- **La conversation**, façon messagerie : Élise à gauche, soi à droite,
  lisible sur téléphone, mode sombre compris. Élise se présente d'elle-même
  au premier passage.
- **À chaque message**, le modèle reçoit la persona (`elise-persona.md`), la
  fiche de la personne, le résumé des anciennes conversations, la date, et
  les 20 derniers messages.
- **La fiche** : après chaque réponse, un second appel au modèle relève les
  nouveaux faits utiles (prénom, entourage, rythme de vie, goûts, événements à
  venir). Doublons écartés ; santé, religion, orientation sexuelle et argent
  jamais enregistrés (consigne au modèle, plus un filtre de mots en secours).
- **Le résumé** : quand plus de 40 messages ne sont pas encore résumés, les
  plus anciens (tous sauf les 20 derniers) rejoignent le résumé.
- **« Effacer toutes mes données »**, dans le menu `⋯` : supprime messages,
  fiche et résumé. Le compte reste ; Élise se présente à nouveau.
- **Sécurité** : chaque table est protégée ligne par ligne (Row Level
  Security) ; chacun ne voit que ses propres données, et les visiteurs non
  connectés n'ont accès à rien.
- **18 ans minimum** : prénom et date de naissance à l'inscription ; la base
  refuse les mineurs.
- **Toujours savoir qui répond** : chaque réponse est marquée « Nom · IA » ou
  « Équipe ».
- **Espace de l'équipe** (`/admin`, réservé aux administrateurs), en quatre
  onglets : Tableau de bord, Messages, IA, Contenus (détails plus bas).
- **Tableau de bord des gains** (`/admin`, réservé aux administrateurs) :
  pourboires, messages achetés, abonnements actifs, total des gains et
  évolution, courbe des gains par jour (7, 30 ou 90 jours), dernier achat en
  direct, et le détail par personne. Voir plus bas.

## Ce qu'il y a dans ce dossier

- `elise-persona.md` — qui est Élise, comment elle parle, ses limites, et son
  premier message. C'est le fichier à retoucher pour changer sa personnalité,
  sans toucher au code. Le titre `## Premier message` doit rester : l'application
  y cherche le message d'accueil.
- `supabase/schema.sql` — la base de données : tables, sécurité, fonction
  d'effacement, achats et calculs du tableau de bord. À coller dans Supabase ;
  on peut le relancer sans risque après chaque mise à jour.
- `supabase/admin.sql` — la ligne qui fait d'un compte un administrateur.
- `lib/llm.ts` — le seul fichier qui parle au modèle.
- `lib/memory.ts` — la mémoire : lecture, fiche, résumés, effacement.
- `lib/prompts.ts` — ce qu'on écrit au modèle en plus de la persona.
- `lib/facts.ts` — le tri des faits (doublons, sujets interdits).
- `app/` — les pages : conversation (`page.tsx`, `chat.tsx`), connexion
  (`connexion/`), serveur de conversation (`api/chat/route.ts`), tableau de
  bord (`admin/`, `api/admin/dashboard/route.ts`).
- `lib/dashboard.ts`, `lib/admin.ts` — le tableau de bord : types, formats,
  accès réservé.
- `lib/persona-profile.ts` — le profil du personnage (champs, langues, âge
  minimum) ; `lib/settings.ts` — réglages de l'IA et fiches contact.
- `lib/sales.ts`, `lib/offers.ts`, `lib/conversation.ts` — la vente : ce que
  l'IA a le droit de proposer, la balise d'offre, l'enregistrement.
- `lib/team.ts` et `app/admin/messages/` — la messagerie de l'équipe ;
  `app/admin/ia/` — l'onglet IA ; `app/admin/contenus/` — les scripts.
- `app/offer-card.tsx` et `app/api/offres/` — l'offre côté personne : achat,
  contre-offre, contenu débloqué.
- `proxy.ts` — renvoie vers la connexion quiconque n'est pas connecté.
- `tests/` — les essais automatiques : `npm test` (logique et base de
  données), `npm run test:e2e` (parcours complet dans un navigateur, contre
  un faux Supabase qui tourne sur la vraie base, et un faux Gemini).
- `scripts/essai-llm.ts` — un essai du modèle seul : `npm run essai:llm`.
- `.env.example` — la liste des réglages.

## Mettre Élise en ligne

### 1. La clé Gemini

Sur [aistudio.google.com/apikey](https://aistudio.google.com/apikey) : **Create
API key**, dans un nouveau projet. La clé doit être marquée **Free**. Ne jamais
cliquer sur **Set up billing**.

### 2. Supabase

1. Sur [supabase.com](https://supabase.com), **New project** : nom `elise`,
   région Paris, offre **Free** (0 $).
2. **SQL Editor → New query** : coller tout le contenu de
   `supabase/schema.sql`, puis **Run**. Le message attendu est
   « Success. No rows returned ».
3. **Authentication → Sign In / Providers** : désactiver **Confirm email**,
   puis **Save**. Sans ça, chaque inscription attend un e-mail de
   confirmation, et le service d'e-mail gratuit de Supabase n'en envoie que
   très peu, et seulement aux membres de l'équipe du projet.
4. Relever pour Vercel l'adresse du projet (**Project Settings → Data API**),
   la **Publishable key** et la **Secret key** (**Project Settings → API
   Keys**). La Secret key ne va que dans Vercel : jamais dans un message, un
   e-mail ou un fichier partagé.

5. Plus tard, une fois inscrit sur le site : ouvrir `supabase/admin.sql`,
   y mettre son adresse e-mail, le coller dans le SQL Editor et **Run**. Le
   lien « Tableau de bord » apparaît alors dans le menu `⋯`, et le lien secret
   de l'équipe (plus bas) ouvre ce compte-là.

### 3. Vercel

1. Sur [vercel.com](https://vercel.com), se connecter avec GitHub, puis **Add
   New → Project** et importer le dépôt `cadence`.
2. **Root Directory** : `elise`. Le reste (Next.js) est détecté tout seul.
3. **Environment Variables**, avant de cliquer sur Deploy :

   | Nom                                    | Valeur                           | Type   |
   | -------------------------------------- | -------------------------------- | ------ |
   | `LLM_PROVIDER`                         | `gemini`                         | Config |
   | `GEMINI_API_KEY`                       | la clé Gemini                    | Secret |
   | `NEXT_PUBLIC_SUPABASE_URL`             | `https://<projet>.supabase.co`   | Config |
   | `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | `sb_publishable_…`               | Config |
   | `SUPABASE_SECRET_KEY`                  | `sb_secret_…`                    | Secret |
   | `ADMIN_ACCESS_KEY`                     | le code du lien de l'équipe      | Secret |

   Les pièges vus au premier déploiement :
   - l'adresse Supabase s'arrête à `.supabase.co` : sans `/rest/v1/` ni `/`
     à la fin (sinon « Invalid path specified in request URL ») ;
   - les clés se copient avec le bouton « copier » de Supabase, jamais à la
     main : une clé raccourcie avec « … » provoque « Cannot convert argument
     to a ByteString » ;
   - les deux `NEXT_PUBLIC_…` sont publiques par nature : type **Config**
     (Vercel le demande pour les noms en `NEXT_PUBLIC_`).

4. **Deploy**. Toute modification ultérieure d'une variable demande un
   redéploiement (**Deployments → ⋯ → Redeploy**).

   `vercel.json` fait tourner le site à Paris (`cdg1`), près de la base
   Supabase : sinon Vercel le place à Washington et chaque page traverse
   l'Atlantique plusieurs fois. L'offre Hobby permet de choisir une région,
   sans frais.

### 4. Relier Supabase au site

Dans Supabase, **Authentication → URL Configuration** : mettre l'adresse du
site Vercel (`https://….vercel.app`) dans **Site URL**, et
`https://….vercel.app/**` dans **Redirect URLs**. Ça ne sert que si la
confirmation par e-mail est un jour réactivée.

## Le tableau de bord des gains

Page `/admin`, réservée aux administrateurs ; pour tous les autres, la page
n'existe pas. Un administrateur qui ouvre le site (ou l'appli installée sur
son téléphone) arrive directement dessus, jamais sur la conversation d'une
personne. « Tester la conversation », dans l'onglet Paramètres, ouvre
`/?vue=conversation` pour voir ce que voient les personnes ; le menu `⋯` y
ramène au tableau de bord.

- **Chiffres clés** sur la période choisie : gains (et évolution par rapport à
  la période précédente, total depuis le début), pourboires, messages achetés,
  abonnements actifs (dernier paiement il y a moins de 31 jours).
- **Courbe des gains par jour**, avec le détail d'un jour au survol ou au
  toucher, et un tableau des valeurs.
- **Dernier achat en direct** : la page redemande les chiffres toutes les
  4 secondes ; un nouvel achat s'affiche sans recharger.
- **Par personne** : pourboires, messages achetés, abonnement, total, dernier
  achat. Toucher un nom filtre toute la page sur cette personne.

Aucun paiement n'est encore branché. En attendant, la section
« Démonstration » crée des achats fictifs (marqués « démo ») et les efface
d'un clic, sans jamais toucher aux vrais. Les achats sont une trace
comptable : « Effacer toutes mes données » ne les supprime pas.

Les calculs sont faits dans la base (fonction `admin_dashboard`), qui vérifie
elle-même que la personne connectée est administratrice.

## L'espace de l'équipe

Six onglets, en bas de l'écran comme dans une appli : Tableau, Messages, IA,
Créatrices, Contenus, Paramètres.

### Le lien secret

`https://<adresse du site>/acces?cle=<ADMIN_ACCESS_KEY>` ouvre directement le
tableau de bord, sans e-mail ni mot de passe : le serveur ouvre la session du
compte administrateur (le premier de la table `admins`), puis affiche
`/admin`, sans la clé dans la barre d'adresse. La session reste ouverte sur
l'appareil ; le lien peut resservir à tout moment.

- Ce lien vaut un mot de passe : ne jamais le partager ni le publier.
- `ADMIN_ACCESS_KEY` : au moins 24 caractères, au hasard (en dessous, le lien
  reste désactivé). Pour changer de lien, changer la variable et redéployer :
  l'ancien lien cesse de marcher.
- Tant qu'aucun administrateur n'existe (`supabase/admin.sql`), le lien
  l'explique au lieu d'ouvrir la session.
- Les personnes qui parlent à Élise, elles, gardent leur compte par e-mail.

### Messages

La liste des conversations, la plus récente en haut, avec les messages non
lus, comme dans une messagerie. On ouvre une conversation pour la lire et
répondre au nom de l'équipe (la personne voit « Équipe »). À côté, la fiche de
la personne :

- **L'IA peut répondre à cette personne** (compte en mode hybride) ;
- **ville** et **fuseau horaire** (l'IA sait quelle heure il est chez elle) ;
- **emojis** que l'IA utilisera avec elle ;
- **comment se comporter avec elle** : 5 000 caractères de notes pour l'IA ;
- **script de vente** suivi, et **plafond de dépenses** mensuel propre ;
- ce que l'IA sait d'elle (sa fiche), sa LTV, et la **vente** : l'étape
  suivante du script, l'offre en attente (qu'on peut retirer), et l'envoi de
  l'étape suivante par l'équipe, avec un message écrit à la main ou rédigé par
  l'IA puis relu.

### IA

- **Qui répond** : automatique (l'IA répond à tout le monde), hybride
  (seulement aux personnes cochées), manuel (l'IA est coupée).
- **La créatrice que l'IA incarne** : l'une des créatrices, ou « Aucune »
  (le personnage par défaut, « Élise »). Bouton « Créer une créatrice ».

### Créatrices

Les personnages que l'IA peut incarner. « Créer une créatrice » ouvre
directement sa page complète, qu'on remplit en descendant :

- **Personnes** : ce que cette créatrice fait avec chacune, c'est-à-dire les
  cases du mode hybride et les emojis qu'elle utilise avec chacune ;
- **Profil du personnage** : nom, pseudo, genre, âge (18 ans minimum),
  anniversaire, profession, ville ou « dans la même région que la personne »,
  langue maternelle (toutes les langues), taille, poids, pointure, bonnet,
  cheveux, yeux, origine, silhouette, groupes personnalisés (tatouages,
  piercings…), centres d'intérêt par catégories libres, et un texte libre ;
- **Premier message** : son message d'accueil (`{nom}` devient son nom).

Puis **Valider** : tout ce qui est rempli appartient à cette créatrice, et
quand l'IA l'incarne, elle agit selon ce profil. La première créatrice
validée devient celle que l'IA incarne ; ensuite, on choisit dans l'onglet
IA. Dans la fiche d'une personne (onglet Messages), « L'IA peut répondre » et
les emojis sont ceux de la créatrice active.

L'IA reste une IA : elle le dit si on le lui demande, ne propose jamais de
rencontre (même « dans la même région »), n'utilise jamais les détails
physiques dans un registre sexuel.

### Paramètres

- **Réglages de l'IA** : nombre de messages relus, consignes
  supplémentaires. La créativité est réglée au maximum fiable (1,0) et l'IA
  choisit elle-même la longueur de chaque réponse : rien à régler.
- **Garde-fous de la vente** : plafond mensuel par personne, nombre de
  messages avant la première offre et entre deux offres.
- **Le site** : le modèle d'IA en service, et si le lien de l'équipe est
  activé.
- **Compte** : le compte connecté, « Tester la conversation » (ce que voient
  les personnes) et « Se déconnecter ».

### Contenus

Des scripts de vente faits de messages dans un ordre précis (« Message 1 ·
Gratuit », « Message 2 · Payant · 9 € »…). Pour chaque message :

- un titre, visible de l'équipe seulement ;
- ce qu'il contient : **jusqu'à 10 photos et vidéos**, un texte (lettre,
  légende, poème…), ou les deux ; la personne voit « 3 photos et 1 vidéo à
  débloquer », puis toute la galerie une fois payé ;
- ce à quoi il ressemble, pour que l'IA puisse en parler sans le montrer ;
- **ce que l'IA dit avec** : soit elle l'écrit elle-même en suivant la
  consigne de l'équipe (« dis que tu les as prises pour lui »), soit elle
  envoie un texte mot pour mot ;
- qui choisit le moment : l'IA ou l'équipe ;
- le prix : gratuit, ou payant avec prix habituel, minimum et maximum.

Le premier script est celui de tout le monde, sauf choix contraire dans la
fiche.

Les règles, vérifiées par la base de données elle-même :

- seul le **message suivant** peut être proposé, une offre à la fois ;
- le prix proposé reste **entre le minimum et le maximum** ; s'il diffère du
  prix habituel, il est affiché « prix personnalisé pour vous » ;
- la personne peut **faire une offre** : acceptée si elle atteint le minimum
  (jamais révélé), refusée sinon, trois refus au plus ;
- **rien du contenu** (ni fichier, ni aperçu, ni texte) n'est transmis avant
  l'achat ; les fichiers sont dans un dossier privé et ne sortent que par un
  lien valable cinq minutes ;
- un achat au-delà du **plafond du mois** est refusé ;
- l'IA ne vend jamais par la solitude, l'attachement, la culpabilité ou
  l'urgence, ne propose rien si la personne va mal ou parle de difficultés
  d'argent, et il n'y a jamais de contenu sexuel.

**Aucun vrai paiement n'est branché** : un achat est enregistré comme
« démo », sans débit. Pour encaisser pour de vrai, il faudra un prestataire de
paiement, et ce sera payant : chez Stripe par exemple, 1,5 % + 0,25 € par
paiement avec une carte européenne standard, davantage avec une carte premium
ou étrangère, sans abonnement.

## Passer de Gemini à Claude

Le jour venu, sur Vercel (**Settings → Environment Variables**) :

1. ajouter `ANTHROPIC_API_KEY` (clé créée sur console.anthropic.com — payant) ;
2. changer `LLM_PROVIDER` de `gemini` à `claude` ;
3. redéployer.

Le modèle par défaut est Claude Haiku 4.5. `CLAUDE_MODEL` permet d'en choisir
un autre, `GEMINI_MODEL` de même côté Gemini (par défaut `gemini-flash-latest`,
qui suit le Flash le plus récent).

## Limites connues de cette version

- **Quota Gemini gratuit** : environ 10 demandes par minute et un plafond par
  jour. Chaque message en coûte deux (la réponse, puis la fiche) ; au-delà,
  Élise demande poliment de réessayer une minute plus tard, et le message
  n'est pas perdu.
- **Supabase gratuit** met le projet en pause après 7 jours sans visite ; on le
  relance d'un clic depuis le tableau de bord.
- **Mot de passe oublié** : pas encore prévu (il faudrait un service d'e-mail).
- **Mémoire à mi-distance** : entre deux résumés, les messages plus anciens
  que les 20 derniers mais pas encore résumés (jusqu'à 20) ne sont plus relus
  mot à mot ; la fiche garde l'essentiel. Pour l'éviter, on peut envoyer au
  modèle tous les messages non résumés (réglage `CONTEXT_MESSAGES` dans
  `lib/memory.ts`).
- **Fuseau horaire** : Élise vit à l'heure de Paris.
- **Paiements** : pas encore branchés (achats « démo »). Le tableau de bord
  lit la table `purchases`, que remplira le futur service de paiement.
- **Stockage Supabase gratuit** : 1 Go de fichiers, 50 Mo par fichier.
- **Direct** : la conversation et la messagerie se mettent à jour toutes les
  4 à 5 secondes, pas instantanément.

## Développer sur sa machine (facultatif)

```bash
cd elise
cp .env.example .env.local   # puis remplir les clés
npm install
npm run dev                  # http://localhost:3000
npm test                     # les essais automatiques
```
