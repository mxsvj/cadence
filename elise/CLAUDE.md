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
- Essais : `npm test` (logique + `supabase/schema.sql` sur PGlite) et
  `npm run test:e2e` (build, serveur Next avec `tests/e2e/faux-services.mjs`
  chargé par `NODE_OPTIONS=--import` : faux Supabase adossé à PGlite avec le
  vrai schéma, faux Gemini ; parcours Chromium dans `tests/e2e/parcours.mjs`).
- Les variables `NEXT_PUBLIC_*` sont figées au moment du build : les changer
  sur Vercel demande un redéploiement.
