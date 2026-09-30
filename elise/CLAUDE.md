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
- Mémoire : 20 derniers messages envoyés au modèle ; fiche et résumé mis à
  jour dans `after()` tous les `MEMORY_EVERY` (3) messages de la personne
  (`memoryDue`, compté par `loadSaleContext` → `sale.userMessages`) : faits
  relevés dans les 6 derniers tours, filtrés par `lib/facts.ts` ; résumé quand
  plus de 40 messages ne sont pas résumés (`summaries.last_message_id` marque
  la limite ; le résumé déjà lu par `buildReply` est réutilisé). Environ 20
  requêtes courtes à la base par message (mesuré dans le parcours e2e,
  `restCalls`) et 1 appel au modèle (2 tous les 3 messages). Tout passe par
  le client Supabase de la personne connectée (RLS), jamais par une clé
  secrète.
- Tableau de bord `/admin` : table `purchases` (tip / message / abonnement,
  `is_demo` pour les achats fictifs), table `admins`, fonctions SQL
  `security definer` qui vérifient `is_admin()` (`admin_dashboard`,
  `admin_simuler_achat`, `admin_remplir_demo`, `admin_vider_demo`). Le
  « direct » est un rafraîchissement toutes les 4 s. Pas encore de paiement.
- Plusieurs créatrices en ligne (`creators.active`) : une conversation par
  (personne, créatrice). `creator_id` NOT NULL sur `messages`, `user_facts`,
  `summaries` (clé primaire (user_id, creator_id)), `offers` ; lu par
  conversation dans `creator_contacts.last_read_message_id`. `/` choisit
  (`creatrices_disponibles()`, redirige s'il n'y en a qu'une), `/c/[id]` est
  la conversation ; `/api/chat` reçoit `creator` (POST) ou `c` (GET) et
  refuse (410) une créatrice hors ligne ; la règle RLS d'écriture des
  messages exige `creatrice_disponible(creator_id)`. Toutes les lectures
  (`lib/memory.ts`, `lib/sales.ts`, `lib/relances.ts`, `lib/team.ts`)
  prennent la créatrice. Seuls le plafond, la pause après achat, les offres
  payantes par jour et « une offre en attente à la fois » valent pour la
  personne entière. `ai_settings.creator_id` ne sert plus (repli de la
  migration). La base neuve crée une créatrice « Élise » en ligne ;
  `supabase/katherine.sql` crée Katherine (profil + `persona.ton`).
- Personnage, messagerie et vente : `ai_settings` (mode auto/hybride/manuel),
  `creators` (persona jsonb dont `ton` = personnalité et façon d'écrire,
  ajoutée sous « Ta personnalité et ta façon d'écrire », premier message,
  `active`), `creator_contacts` (IA autorisée et emojis de chaque créatrice
  avec chaque personne : `emoji_mode` libre/choisis/aucun + `emojis`,
  nettoyés par `lib/emojis.ts` ; les colonnes `persona`, `first_message`,
  `temperature`, `max_tokens` d'`ai_settings` et `ai_enabled`, `emojis` de
  `contacts` ne servent plus), `contacts` (fiche par personne), `scripts`/`script_steps`
  (étapes ordonnées, prix min/max ; `scripts.creator_id` null = pour toutes,
  `script_de(personne, créatrice)` ne prend que ceux de la créatrice ou de
  toutes), `offers` (prix personnalisé,
  contre-offres), `profiles` (18 ans minimum). La clé secrète
  (`SUPABASE_SECRET_KEY`, `lib/supabase/admin.ts`) ne sert qu'au serveur ; les
  personnes n'écrivent que des messages `role='user'`. L'IA propose une offre
  par la balise `[[PROPOSER prix=…]]`, seulement si `lib/sales.ts` l'a permis
  (`saleBlock` : fin du script, étape de l'équipe, offre en attente, premiers
  messages, espacement, prise de nouvelles, plafond, pause après achat
  `sales_pause_hours`, offres payantes sur 24 h `sales_max_per_day` ; un
  cadeau gratuit n'est soumis qu'aux premiers) ; `describeBlock` en fait la
  phrase de la fiche. La consigne donne la place de l'étape (« le 2e sur 5 »)
  et un prix maximum ramené au reste du plafond. `proposer_etape` (SQL)
  impose l'ordre, borne le prix, et refuse un contenu payant au-delà du
  plafond du mois. Les achats sont
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
- Messages du script (`script_steps`) : `media` jsonb (au plus 10
  `{path, kind}`, l'ancien `media_path` y est repris par `schema.sql`),
  `content_text` facultatif s'il y a des médias, `content_type` déduit
  (`mainType`). Les offres gardent `photo_count` / `video_count` pour
  s'annoncer sans rien montrer ; `mon_contenu` rend `media`, et
  `/api/offres/[id]/contenu` signe chaque fichier pour 5 minutes. En mode
  `ia`, `message_text` est la consigne de l'équipe (reformulée par l'IA) ;
  en mode `fixe`, le texte envoyé mot pour mot.
- Réponses : créativité fixe `CHAT_TEMPERATURE = 1` (`lib/llm.ts`, valeur
  recommandée par Google pour ses modèles récents), pas de plafond de
  longueur (Gemini n'en reçoit pas, Claude 4096 jetons) : la persona dit à
  l'IA de choisir elle-même la longueur.
- Vitesse : `vercel.json` place les fonctions à Paris (`cdg1`, une seule
  région autorisée en Hobby), à côté de Supabase ; `app/admin/loading.tsx`
  s'affiche dès qu'on touche un onglet (sans lui, une page dynamique n'est
  pas préchargée et rien ne bouge avant la réponse du serveur) ;
  `adminGate` passe par `cache()` pour ne vérifier qu'une fois par requête.
- Espace équipe : barre d'onglets fixée en bas (`app/admin/nav.tsx`, 4 rem +
  marge de l'iPhone, réservés par `app/admin/layout.tsx`). Tout élément fixé
  en bas d'une page admin se pose au-dessus
  (`bottom-[calc(4rem+env(safe-area-inset-bottom))]`). L'onglet IA enregistre
  le mode et les créatrices en ligne (`saveSettings`, au moins une) ; l'onglet Créatrices,
  chaque créatrice (`saveCreator`, page unique Personnes → Profil → Premier
  message → Valider) ; l'onglet Paramètres, les réglages fins et les
  garde-fous (`saveParameters`).
- Page d'une créatrice : enregistrement automatique (700 ms après la
  dernière frappe, une sauvegarde à la fois, la première crée la ligne ;
  seules les personnes modifiées sont envoyées). `saveCreator` appelle
  `revalidatePath("/admin", "layout")` : sans ça, le bouton « retour » du
  navigateur remontre la liste gardée en cache (sans la créatrice). « Valider »
  exige le prénom et met la créatrice en ligne. Les
  lectures des colonnes récentes passent par `select("*")` pour que le site
  marche encore tant que `schema.sql` n'est pas relancé ; les erreurs de
  colonne absente affichent « relancez supabase/schema.sql » (`schemaOutdated`).
- Prendre des nouvelles : `lib/relances.ts` + `/api/relances` (tâche Vercel
  quotidienne `0 16 * * *` dans `vercel.json`, Hobby = une fois par jour à
  l'heure près ; `Authorization: Bearer CRON_SECRET`). `a_relancer()` (SQL,
  service_role) choisit les absents : `ai_settings.relance_active` /
  `relance_heures`, une seule par personne dans sa dernière conversation, avec
  une créatrice en ligne, `profiles.relances_ok` (menu de la personne,
  `regler_relances`), `profiles.vu_le` (`marquer_visite` à chaque ouverture
  de la conversation), dernier message pas déjà une `kind='relance'`, pas
  d'offre en attente, jamais un administrateur. Le message est écrit avec la
  consigne habituelle sans vente (`sale: null`) + `relanceTask` ; les
  balises sont retirées. `mayPropose` (`lib/sales.ts`) interdit toute offre
  tant que la personne n'a pas écrit `NO_SALE_AFTER_RELANCE` (3) messages
  depuis. Ces lectures passent par la clé secrète (pas de session). Pas de
  notification téléphone : le message attend dans la conversation.
- Contenus contextuels : `script_steps.moment` (« quand il parle de
  voyages ») ; `salesSection` ne laisse proposer l'étape que si la
  conversation porte sur ce sujet (sinon, seulement si le contenu enrichit
  le sujet en cours), « dans le doute, ne le propose pas ».
- Le faux PostgREST des essais (`faux-services.mjs`) renvoie un tableau pour
  les fonctions `returns table` / `setof`, comme le vrai.
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
- Alertes de l'équipe : table `team_alerts` (kind `contre_offre` | `plafond`
  | `urgence`, `detail` jsonb sans texte de message, `notified_at`,
  `handled_at`). Créées par `alerter_equipe` (SQL, interne) : dans
  `faire_une_offre` (une alerte ouverte par offre, mise à jour), dans
  `acheter_offre` (80 % du plafond, une fois par mois), et par la route
  `/api/chat` pour les urgences (`lib/urgency.ts` : `detectUrgency` sur le
  message — humain, age, reclamation, attention — et la balise `[[EQUIPE]]`
  que l'IA ajoute, consigne `teamSection` dans `lib/prompts.ts`, retirée par
  `parseTeamFlag` ; une seule urgence ouverte par conversation). Une urgence
  ouverte bloque toute vente (`saleBlock` → `urgence`) et la prise de
  nouvelles ; 80 % du plafond bloque les offres payantes de l'IA
  (`plafond_proche`, `NEAR_CAP_PERCENT` dans `lib/alerts.ts`, même seuil que
  le SQL). Envoi Discord/Telegram par `lib/notify.ts` (`flushAlerts` dans
  `after()`, `alertes_a_envoyer` réserve les alertes du dernier jour ;
  `allowed_mentions` vide ; jamais le prénom). Équipe : `admin_alertes`,
  `admin_traiter_alertes`, `admin_prendre_la_main` ; `admin_boite` renvoie
  `alertes` et `manuel`. `creator_contacts.manual` (« Prendre la main ») fait
  taire l'IA dans la conversation quel que soit le mode (`aiMayReply`).
  Écrans : `app/admin/alerts-store.ts` (une seule relecture toutes les 8 s
  pour le bandeau `alert-flash.tsx`, la pastille de `nav.tsx` et
  `open-alerts.tsx` du tableau de bord ; « déjà vu » dans localStorage),
  filtres et bandeau d'alertes dans `app/admin/messages/inbox.tsx`. Le bandeau
  ouvre une conversation de l'onglet Messages par l'événement
  `OPEN_CONVERSATION` (`app/admin/messages/events.ts`). Dans les essais e2e,
  Next.js a son propre `role="alert"` vide : chercher le bandeau par son
  bouton « Fermer l'alerte ».
- Production : en-têtes de sécurité dans `next.config.ts` (frame-ancestors,
  nosniff, referrer, permissions, HSTS, `poweredByHeader: false`) ; au plus
  `CHAT_RATE_LIMIT` (12) messages par minute et par personne sur `/api/chat`
  (`lib/rate-limit.ts`, en mémoire par instance) ; le faux Discord des essais
  est dans `faux-services.mjs` (`webhooks`). Pas encore de Stripe : les
  achats restent « démo ».
