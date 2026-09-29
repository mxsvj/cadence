@AGENTS.md

# Élise — contexte du projet

Prototype d'IA de conversation bienveillante pour adultes seuls (cible :
quadragénaires séparés ou divorcés). Le porteur du projet ne code pas :
tout expliquer simplement, en français, et ne demander que les actions
impossibles à faire à sa place (créer un compte, copier une clé).

- Budget zéro : uniquement des offres gratuites (Vercel Hobby, Supabase Free,
  Gemini via AI Studio sans facturation). Avant toute étape qui pourrait coûter,
  s'arrêter et annoncer le prix exact.
- Gemini gratuit réutilise les données : conversations fictives seulement.
- Tout appel au modèle passe par `lib/llm.ts` ; `LLM_PROVIDER` choisit
  `gemini` ou `claude` (Haiku 4.5).
- La persona est `elise-persona.md` (instruction système complète) ; son titre
  `## Premier message` fournit le message d'accueil.
- Faits sur l'utilisateur : jamais de santé, religion, orientation sexuelle ni
  argent.
- Le projet vit dans le sous-dossier `elise/` du dépôt `cadence` ; sur Vercel,
  c'est un projet séparé dont le « Root Directory » est `elise`.
- Supabase (`*.supabase.co`) n'est pas joignable depuis l'environnement cloud
  de Claude Code ; l'API Gemini l'est.
- Mémoire : 20 derniers messages envoyés au modèle ; résumé déclenché dans
  `after()` quand plus de 40 messages ne sont pas résumés
  (`summaries.last_message_id` marque la limite) ; faits extraits après chaque
  réponse, filtrés par `lib/facts.ts`. Tout passe par le client Supabase de
  la personne connectée (RLS), jamais par une clé secrète.
- Tableau de bord `/admin` : table `purchases` (tip / message / abonnement,
  `is_demo` pour les achats fictifs), table `admins`, fonctions SQL
  `security definer` qui vérifient `is_admin()` (`admin_dashboard`,
  `admin_simuler_achat`, `admin_remplir_demo`, `admin_vider_demo`). Le
  « direct » est un rafraîchissement toutes les 4 s. Pas encore de paiement.
- Personnage, messagerie et vente : `ai_settings` (mode auto/hybride/manuel,
  persona jsonb), `contacts` (fiche par personne), `scripts`/`script_steps`
  (étapes ordonnées, prix min/max), `offers` (prix personnalisé,
  contre-offres), `profiles` (18 ans minimum). La clé secrète
  (`SUPABASE_SECRET_KEY`, `lib/supabase/admin.ts`) ne sert qu'au serveur ; les
  personnes n'écrivent que des messages `role='user'`. L'IA propose une offre
  par la balise `[[PROPOSER prix=…]]`, seulement si `lib/sales.ts` l'a permis ;
  `proposer_etape` (SQL) impose l'ordre et borne le prix. Les achats sont
  « démo » tant qu'aucun paiement n'est branché.
- Lignes rouges posées par le porteur du projet et par Claude : l'IA se dit
  toujours IA, chaque réponse est marquée IA ou Équipe, jamais de rencontre
  (même « dans la même région »), jamais de vente par solitude/attachement,
  prix personnalisé toujours affiché, jamais sous le minimum, rien de visible
  avant achat, aucun contenu sexuel, 18 ans minimum.
- Essais : `npm test` (logique + `supabase/schema.sql` sur PGlite) et
  `npm run test:e2e` (build, serveur Next avec `tests/e2e/faux-services.mjs`
  chargé par `NODE_OPTIONS=--import` : faux Supabase adossé à PGlite avec le
  vrai schéma, faux Gemini ; parcours Chromium dans `tests/e2e/parcours.mjs`).
- Les variables `NEXT_PUBLIC_*` sont figées au moment du build : les changer
  sur Vercel demande un redéploiement.
- Un administrateur qui ouvre `/` est renvoyé vers `/admin` (`app/page.tsx`) ;
  `/?vue=conversation` garde la conversation accessible pour la tester.
- Vitesse : `vercel.json` place les fonctions à Paris (`cdg1`, une seule
  région autorisée en Hobby), à côté de Supabase ; `app/admin/loading.tsx`
  s'affiche dès qu'on touche un onglet (sans lui, une page dynamique n'est
  pas préchargée et rien ne bouge avant la réponse du serveur) ;
  `adminGate` passe par `cache()` pour ne vérifier qu'une fois par requête.
- Espace équipe : barre d'onglets fixée en bas (`app/admin/nav.tsx`, 4 rem +
  marge de l'iPhone, réservés par `app/admin/layout.tsx`). Tout élément fixé
  en bas d'une page admin se pose au-dessus
  (`bottom-[calc(4rem+env(safe-area-inset-bottom))]`). L'onglet IA enregistre
  mode et personnage (`saveSettings`) ; l'onglet Paramètres, les réglages fins
  et les garde-fous (`saveParameters`).
- Lien secret de l'équipe : `/acces?cle=<ADMIN_ACCESS_KEY>` (`app/acces/route.ts`,
  `lib/team-access.ts`) ouvre la session du premier compte de `admins` par
  `auth.admin.generateLink` + `verifyOtp`, sans e-mail envoyé, puis redirige
  vers `/admin`. Les règles de la base (RLS, `is_admin()`) restent la seule
  barrière : le lien ne fait qu'ouvrir une vraie session d'administrateur.
  Un refus mène à `/acces/refus?raison=cle|absente|equipe|panne`, pas à
  `/connexion` : une personne déjà connectée y serait renvoyée vers la
  conversation et ne verrait jamais la raison.
- Au premier déploiement, le porteur du projet a collé des exemples au lieu
  des vraies valeurs (`sb_publishable_…`, `/rest/v1/` en trop) : donner des
  valeurs à copier telles quelles, ou lui faire utiliser le bouton « copier ».
