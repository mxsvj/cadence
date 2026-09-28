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
4. Relever pour Vercel l'adresse du projet (**Project Settings → Data API**)
   et la **Publishable key** (**Project Settings → API Keys**). La **Secret
   key** ne sert à rien ici : ne la copier nulle part.

5. Plus tard, une fois inscrit sur le site : ouvrir `supabase/admin.sql`,
   y mettre son adresse e-mail, le coller dans le SQL Editor et **Run**. Le
   lien « Tableau de bord » apparaît alors dans le menu `⋯`.

### 3. Vercel

1. Sur [vercel.com](https://vercel.com), se connecter avec GitHub, puis **Add
   New → Project** et importer le dépôt `cadence`.
2. **Root Directory** : `elise`. Le reste (Next.js) est détecté tout seul.
3. **Environment Variables**, avant de cliquer sur Deploy :

   | Nom                                    | Valeur                         |
   | -------------------------------------- | ------------------------------ |
   | `LLM_PROVIDER`                         | `gemini`                       |
   | `GEMINI_API_KEY`                       | la clé Gemini                  |
   | `NEXT_PUBLIC_SUPABASE_URL`             | `https://….supabase.co`        |
   | `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | `sb_publishable_…`             |

4. **Deploy**. Toute modification ultérieure d'une variable demande un
   redéploiement (**Deployments → ⋯ → Redeploy**).

### 4. Relier Supabase au site

Dans Supabase, **Authentication → URL Configuration** : mettre l'adresse du
site Vercel (`https://….vercel.app`) dans **Site URL**, et
`https://….vercel.app/**` dans **Redirect URLs**. Ça ne sert que si la
confirmation par e-mail est un jour réactivée.

## Le tableau de bord des gains

Page `/admin`, accessible par le menu `⋯` de la conversation pour les
administrateurs seulement ; pour tous les autres, la page n'existe pas.

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
- **Paiements** : pas encore branchés. Le tableau de bord lit la table
  `purchases`, que remplira le futur service de paiement.

## Développer sur sa machine (facultatif)

```bash
cd elise
cp .env.example .env.local   # puis remplir les clés
npm install
npm run dev                  # http://localhost:3000
npm test                     # les essais automatiques
```
