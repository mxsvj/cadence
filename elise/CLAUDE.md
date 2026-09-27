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
