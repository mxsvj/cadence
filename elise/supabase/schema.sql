-- ═══════════════════════════════════════════════════════════════════════════
-- Élise : la base de données.
--
-- À coller EN ENTIER dans Supabase → SQL Editor → New query, puis « Run ».
-- On peut le relancer sans risque : il ne crée que ce qui manque et remet
-- les règles de sécurité à jour.
-- ═══════════════════════════════════════════════════════════════════════════


-- ─── Les messages de la conversation ───────────────────────────────────────
-- Tous les messages, d'Élise (assistant) comme de l'utilisateur (user).
-- L'identifiant croît avec le temps : il donne l'ordre de la conversation.
create table if not exists public.messages (
  id         bigint generated always as identity primary key,
  user_id    uuid not null default auth.uid() references auth.users (id) on delete cascade,
  role       text not null check (role in ('user', 'assistant')),
  content    text not null check (char_length(content) between 1 and 8000),
  created_at timestamptz not null default now()
);
create index if not exists messages_user_id_id_idx on public.messages (user_id, id);

-- Qui a écrit : la personne (user), l'IA (ai) ou quelqu'un de l'équipe (team),
-- pour l'afficher sous chaque message ; et s'il s'agit d'une offre de contenu.
alter table public.messages add column if not exists author    text not null default 'user';
alter table public.messages add column if not exists author_id uuid references auth.users (id) on delete set null;
alter table public.messages add column if not exists kind      text not null default 'text';
update public.messages set author = 'ai' where role = 'assistant' and author = 'user';
alter table public.messages drop constraint if exists messages_author_check;
alter table public.messages add constraint messages_author_check
  check ((role = 'user' and author = 'user') or (role = 'assistant' and author in ('ai', 'team')));
alter table public.messages drop constraint if exists messages_kind_check;
alter table public.messages add constraint messages_kind_check check (kind in ('text', 'offer'));


-- ─── La fiche : ce qu'Élise sait de l'utilisateur ──────────────────────────
-- Une phrase courte par fait. Jamais de santé, religion, orientation
-- sexuelle ni argent : le tri est fait avant l'enregistrement.
create table if not exists public.user_facts (
  id         bigint generated always as identity primary key,
  user_id    uuid not null default auth.uid() references auth.users (id) on delete cascade,
  fact       text not null check (char_length(fact) between 1 and 300),
  created_at timestamptz not null default now()
);
-- Pas deux fois le même fait (majuscules comprises).
create unique index if not exists user_facts_user_id_fact_key
  on public.user_facts (user_id, lower(fact));


-- ─── Le résumé des anciennes conversations ─────────────────────────────────
-- Une ligne par utilisateur. last_message_id retient jusqu'où le résumé
-- va : les messages suivants n'y sont pas encore.
create table if not exists public.summaries (
  user_id         uuid primary key default auth.uid() references auth.users (id) on delete cascade,
  summary         text not null,
  last_message_id bigint not null default 0,
  updated_at      timestamptz not null default now()
);


-- ─── Sécurité : chacun ne voit et ne touche que ses propres données ───────
alter table public.messages   enable row level security;
alter table public.user_facts enable row level security;
alter table public.summaries  enable row level security;

-- Les visiteurs non connectés n'ont accès à rien. Les personnes connectées
-- n'ont que les droits utiles (par exemple, un message ne se modifie pas).
revoke all on public.messages, public.user_facts, public.summaries from anon, authenticated;
grant select, insert, delete         on public.messages   to authenticated;
grant select, insert, delete         on public.user_facts to authenticated;
grant select, insert, update, delete on public.summaries  to authenticated;

drop policy if exists "Lire ses messages"      on public.messages;
drop policy if exists "Écrire ses messages"    on public.messages;
drop policy if exists "Effacer ses messages"   on public.messages;
create policy "Lire ses messages"    on public.messages for select to authenticated
  using ((select auth.uid()) = user_id);
create policy "Écrire ses messages"  on public.messages for insert to authenticated
  with check ((select auth.uid()) = user_id and role = 'user' and author = 'user' and kind = 'text');
create policy "Effacer ses messages" on public.messages for delete to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "Lire sa fiche"          on public.user_facts;
drop policy if exists "Compléter sa fiche"     on public.user_facts;
drop policy if exists "Effacer sa fiche"       on public.user_facts;
create policy "Lire sa fiche"      on public.user_facts for select to authenticated
  using ((select auth.uid()) = user_id);
create policy "Compléter sa fiche" on public.user_facts for insert to authenticated
  with check ((select auth.uid()) = user_id);
create policy "Effacer sa fiche"   on public.user_facts for delete to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "Lire son résumé"        on public.summaries;
drop policy if exists "Créer son résumé"       on public.summaries;
drop policy if exists "Mettre à jour son résumé" on public.summaries;
drop policy if exists "Effacer son résumé"     on public.summaries;
create policy "Lire son résumé"          on public.summaries for select to authenticated
  using ((select auth.uid()) = user_id);
create policy "Créer son résumé"         on public.summaries for insert to authenticated
  with check ((select auth.uid()) = user_id);
create policy "Mettre à jour son résumé" on public.summaries for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);
create policy "Effacer son résumé"       on public.summaries for delete to authenticated
  using ((select auth.uid()) = user_id);


-- Le bouton « Effacer toutes mes données » est défini tout en bas : il a
-- besoin des tables qui suivent.


-- ═══════════════════════════════════════════════════════════════════════════
-- Le tableau de bord des gains (page /admin)
-- ═══════════════════════════════════════════════════════════════════════════

-- ─── Les achats : pourboires, messages achetés, abonnements, contenus ──────
-- Une ligne par paiement. Plus tard, c'est le service de paiement qui les
-- écrira, côté serveur : personne ne peut en créer depuis le site.
-- Les achats de démonstration (is_demo) n'ont pas de compte : customer_label
-- porte un prénom fictif. Un achat est une trace comptable : « Effacer toutes
-- mes données » n'y touche pas, et il survit à la suppression du compte
-- (user_id devient vide).
create table if not exists public.purchases (
  id             bigint generated always as identity primary key,
  user_id        uuid references auth.users (id) on delete set null,
  customer_label text,
  kind           text not null,
  quantity       integer not null default 1 check (quantity > 0),
  amount_cents   integer not null check (amount_cents > 0),
  currency       text not null default 'EUR' check (currency = 'EUR'),
  is_demo        boolean not null default false,
  created_at     timestamptz not null default now()
);
alter table public.purchases drop constraint if exists purchases_kind_check;
alter table public.purchases add constraint purchases_kind_check
  check (kind in ('tip', 'message', 'abonnement', 'contenu'));
create index if not exists purchases_created_at_idx on public.purchases (created_at desc);
create index if not exists purchases_user_id_idx on public.purchases (user_id);


-- ─── Les administrateurs : qui voit le tableau de bord ─────────────────────
-- Pour le devenir, voir supabase/admin.sql.
create table if not exists public.admins (
  user_id uuid primary key references auth.users (id) on delete cascade
);

alter table public.purchases enable row level security;
alter table public.admins    enable row level security;
revoke all on public.purchases, public.admins from anon, authenticated;
grant select on public.purchases to authenticated;
grant select on public.admins    to authenticated;

-- Chacun peut voir ses propres achats ; tout le reste passe par les
-- fonctions ci-dessous, qui vérifient d'abord qu'on est administrateur.
drop policy if exists "Voir ses achats" on public.purchases;
create policy "Voir ses achats" on public.purchases for select to authenticated
  using ((select auth.uid()) = user_id);
drop policy if exists "Se savoir administrateur" on public.admins;
create policy "Se savoir administrateur" on public.admins for select to authenticated
  using ((select auth.uid()) = user_id);

create or replace function public.is_admin()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (select 1 from public.admins where user_id = (select auth.uid()));
$$;


-- ─── Les chiffres du tableau de bord ───────────────────────────────────────
-- p_client : un client précis (valeur « client » renvoyée dans la liste), ou
-- null pour tout le monde. p_jours : la période, en jours, jusqu'à aujourd'hui.
-- Les jours sont comptés à l'heure de Paris.
create or replace function public.admin_dashboard(p_client text default null, p_jours integer default 30)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  jours       integer := least(greatest(coalesce(p_jours, 30), 1), 365);
  aujourdhui  date    := (now() at time zone 'Europe/Paris')::date;
  debut       date    := aujourdhui - (jours - 1);
  resultat    jsonb;
begin
  if not public.is_admin() then
    raise exception 'Réservé aux administrateurs.' using errcode = '42501';
  end if;

  with achats as (
    select p.id, p.kind, p.quantity, p.amount_cents, p.created_at, p.is_demo,
           coalesce(p.user_id::text, 'demo:' || p.customer_label, 'supprime') as client,
           coalesce(u.email, p.customer_label, 'Compte supprimé')             as nom,
           (p.created_at at time zone 'Europe/Paris')::date                   as jour
    from public.purchases p
    left join auth.users u on u.id = p.user_id
  ),
  choix as (
    select * from achats where p_client is null or client = p_client
  ),
  periode as (
    select * from choix where jour between debut and aujourdhui
  ),
  jours_de_la_periode as (
    select d::date as jour from generate_series(debut, aujourdhui, interval '1 day') as d
  ),
  clients as (
    select client,
           min(nom)                                                          as nom,
           bool_or(is_demo)                                                  as demo,
           coalesce(sum(amount_cents) filter (where kind = 'tip'), 0)        as pourboires_cents,
           count(*) filter (where kind = 'tip')                              as pourboires_nombre,
           coalesce(sum(quantity) filter (where kind = 'message'), 0)        as messages_nombre,
           coalesce(sum(amount_cents) filter (where kind = 'message'), 0)    as messages_cents,
           coalesce(sum(amount_cents) filter (where kind = 'contenu'), 0)    as contenus_cents,
           count(*) filter (where kind = 'contenu')                          as contenus_nombre,
           bool_or(kind = 'abonnement' and created_at > now() - interval '31 days') as abonne,
           sum(amount_cents)                                                 as total_cents,
           count(*)                                                          as achats,
           min(created_at)                                                   as premier_achat,
           max(created_at)                                                   as dernier_achat
    from achats
    group by client
  )
  select jsonb_build_object(
    'genere_le', now(),
    'jours', jours,
    'client', p_client,
    'demo', exists (select 1 from achats where is_demo),
    'totaux', jsonb_build_object(
      'depuis_le_debut',   (select coalesce(sum(amount_cents), 0) from choix),
      'periode',           (select coalesce(sum(amount_cents), 0) from periode),
      'periode_precedente',(select coalesce(sum(amount_cents), 0) from choix
                              where jour between debut - jours and debut - 1),
      'pourboires', (select jsonb_build_object('nombre', count(*), 'cents', coalesce(sum(amount_cents), 0))
                       from periode where kind = 'tip'),
      'messages',   (select jsonb_build_object('nombre', coalesce(sum(quantity), 0), 'achats', count(*),
                                               'cents', coalesce(sum(amount_cents), 0))
                       from periode where kind = 'message'),
      'contenus',   (select jsonb_build_object('nombre', count(*), 'cents', coalesce(sum(amount_cents), 0))
                       from periode where kind = 'contenu'),
      'abonnements', (select jsonb_build_object(
                         'actifs', (select count(distinct client) from choix
                                     where kind = 'abonnement' and created_at > now() - interval '31 days'),
                         'nombre', count(*),
                         'cents',  coalesce(sum(amount_cents), 0))
                       from periode where kind = 'abonnement')
    ),
    'serie', (
      select jsonb_agg(to_jsonb(s) order by s.jour)
      from (
        select j.jour,
               coalesce(sum(p.amount_cents), 0)                                   as total,
               coalesce(sum(p.amount_cents) filter (where p.kind = 'tip'), 0)        as pourboires,
               coalesce(sum(p.amount_cents) filter (where p.kind = 'message'), 0)    as messages,
               coalesce(sum(p.amount_cents) filter (where p.kind = 'abonnement'), 0) as abonnements,
               coalesce(sum(p.amount_cents) filter (where p.kind = 'contenu'), 0)    as contenus
        from jours_de_la_periode j
        left join periode p on p.jour = j.jour
        group by j.jour
      ) s
    ),
    'derniers', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', id, 'client', client, 'nom', nom, 'type', kind,
               'quantite', quantity, 'cents', amount_cents, 'date', created_at, 'demo', is_demo)
             order by created_at desc, id desc)
      from (select * from choix order by created_at desc, id desc limit 12) d
    ), '[]'::jsonb),
    -- La LTV (valeur d'un client sur toute sa vie) : ce qu'il a dépensé au
    -- total. On la calcule sur tout l'historique, pas seulement la période.
    'ltv', (
      select jsonb_build_object(
        'clients',            count(*),
        'moyenne_cents',      coalesce(round(avg(total_cents)), 0),
        'mediane_cents',      coalesce(round(percentile_cont(0.5) within group (order by total_cents)), 0),
        'max_cents',          coalesce(max(total_cents), 0),
        'achats_par_client',  coalesce(round(avg(achats), 1), 0),
        'panier_moyen_cents', coalesce(round(sum(total_cents)::numeric / nullif(sum(achats), 0)), 0),
        'duree_moyenne_jours', coalesce(round(avg(extract(epoch from dernier_achat - premier_achat) / 86400 + 1)), 0),
        'inscrits',           (select count(*) from auth.users),
        'payants',            (select count(distinct user_id) from public.purchases where user_id is not null and not is_demo)
      )
      from clients
      where p_client is null or client = p_client
    ),
    'clients', coalesce((
      select jsonb_agg(to_jsonb(c) order by c.total_cents desc, c.nom)
      from (select * from clients order by total_cents desc, nom limit 200) c
    ), '[]'::jsonb)
  ) into resultat;

  return resultat;
end;
$$;


-- ─── Les données de démonstration ──────────────────────────────────────────
-- Tant qu'aucun paiement n'est branché, le tableau de bord se remplit avec
-- des achats fictifs, marqués is_demo, qu'un bouton efface d'un coup.

-- Un achat fictif au hasard, à la date donnée (usage interne).
create or replace function public.achat_de_demo(p_quand timestamptz)
returns public.purchases
language plpgsql
volatile
security invoker
set search_path = ''
as $$
declare
  noms  constant text[] := array['Karim B.', 'Nathalie R.', 'Stéphane L.', 'Sandrine M.',
                                 'Olivier T.', 'Isabelle D.', 'Frédéric P.', 'Valérie C.'];
  tirage double precision := random();
  pack   integer := floor(random() * 3)::integer;
  achat  public.purchases;
begin
  insert into public.purchases (customer_label, kind, quantity, amount_cents, is_demo, created_at)
  values (
    noms[1 + floor(random() * array_length(noms, 1))::integer],
    case when tirage < 0.35 then 'tip' when tirage < 0.65 then 'message'
         when tirage < 0.9 then 'contenu' else 'abonnement' end,
    case when tirage >= 0.35 and tirage < 0.65 then (array[5, 10, 20])[pack + 1] else 1 end,
    case when tirage < 0.35 then (array[200, 300, 500, 1000])[1 + floor(random() * 4)::integer]
         when tirage < 0.65 then (array[199, 349, 599])[pack + 1]
         when tirage < 0.9  then (array[490, 790, 1290, 1990])[1 + floor(random() * 4)::integer]
         else 999 end,
    true,
    p_quand
  )
  returning * into achat;
  return achat;
end;
$$;
revoke execute on function public.achat_de_demo(timestamptz) from public, anon, authenticated;

-- « Simuler un achat » : un achat fictif, maintenant.
create or replace function public.admin_simuler_achat()
returns jsonb
language plpgsql
volatile
security definer
set search_path = ''
as $$
begin
  if not public.is_admin() then
    raise exception 'Réservé aux administrateurs.' using errcode = '42501';
  end if;
  return to_jsonb(public.achat_de_demo(now()));
end;
$$;

-- « Remplir avec des données de démo » : un historique fictif, de plus en
-- plus fourni à mesure qu'on se rapproche d'aujourd'hui.
create or replace function public.admin_remplir_demo(p_jours integer default 60)
returns integer
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  jours integer := least(greatest(coalesce(p_jours, 60), 1), 365);
  total integer := 0;
  d     integer;
  n     integer;
  quand timestamptz;
begin
  if not public.is_admin() then
    raise exception 'Réservé aux administrateurs.' using errcode = '42501';
  end if;
  for d in 0 .. jours - 1 loop
    n := floor(random() * 3 + 5.0 * (jours - d) / jours)::integer;
    for i in 1 .. n loop
      quand := now() - make_interval(days => d) - make_interval(secs => floor(random() * 86400));
      perform public.achat_de_demo(quand);
      total := total + 1;
    end loop;
  end loop;
  return total;
end;
$$;

-- « Effacer la démo » : retire tous les achats fictifs, rien d'autre.
create or replace function public.admin_vider_demo()
returns integer
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  n integer;
begin
  if not public.is_admin() then
    raise exception 'Réservé aux administrateurs.' using errcode = '42501';
  end if;
  delete from public.purchases where is_demo;
  get diagnostics n = row_count;
  return n;
end;
$$;

revoke execute on function public.is_admin(), public.admin_dashboard(text, integer),
  public.admin_simuler_achat(), public.admin_remplir_demo(integer), public.admin_vider_demo()
  from public, anon;
grant execute on function public.is_admin(), public.admin_dashboard(text, integer),
  public.admin_simuler_achat(), public.admin_remplir_demo(integer), public.admin_vider_demo()
  to authenticated;


-- ═══════════════════════════════════════════════════════════════════════════
-- Le personnage, la messagerie de l'équipe et les contenus à vendre
-- ═══════════════════════════════════════════════════════════════════════════

-- ─── Les profils : prénom affiché et âge (18 ans minimum) ──────────────────
create table if not exists public.profiles (
  user_id      uuid primary key references auth.users (id) on delete cascade,
  display_name text not null check (char_length(display_name) between 1 and 60),
  birthdate    date not null check (birthdate >= date '1900-01-01'),
  created_at   timestamptz not null default now()
);

-- Seule porte d'entrée pour créer son profil : elle refuse les mineurs. La
-- date de naissance ne peut plus changer ensuite.
create or replace function public.enregistrer_profil(p_nom text, p_naissance date)
returns void
language plpgsql
volatile
security definer
set search_path = ''
as $$
begin
  if (select auth.uid()) is null then
    raise exception 'Connexion requise.' using errcode = '42501';
  end if;
  if p_naissance is null or p_naissance > (current_date - interval '18 years')::date then
    raise exception 'Élise est réservée aux personnes majeures (18 ans et plus).' using errcode = 'P0001';
  end if;
  insert into public.profiles (user_id, display_name, birthdate)
  values ((select auth.uid()), trim(p_nom), p_naissance)
  on conflict (user_id) do update set display_name = excluded.display_name;
end;
$$;


-- ─── Les scripts de vente : des étapes, dans l'ordre ───────────────────────
-- Le titre d'une étape n'est visible que de l'équipe. L'IA ne propose jamais
-- que l'étape suivante, dans l'ordre, et jamais sous le prix minimum.
create table if not exists public.scripts (
  id         bigint generated always as identity primary key,
  name       text not null check (char_length(name) between 1 and 120),
  position   integer not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists public.script_steps (
  id              bigint generated always as identity primary key,
  script_id       bigint not null references public.scripts (id) on delete cascade,
  position        integer not null default 0,
  title           text not null check (char_length(title) between 1 and 120),
  content_type    text not null default 'image' check (content_type in ('image', 'video', 'texte')),
  content_text    text not null default '' check (char_length(content_text) <= 10000),
  media_path      text,
  -- Ce à quoi ressemble le contenu, pour que l'IA puisse en parler sans le montrer.
  ai_description  text not null default '' check (char_length(ai_description) <= 3000),
  -- Le message qui accompagne l'offre : écrit par l'IA, ou fixé par l'équipe.
  message_mode    text not null default 'ia' check (message_mode in ('ia', 'fixe')),
  message_text    text not null default '' check (char_length(message_text) <= 2000),
  -- Qui décide du moment de proposer : l'IA, ou l'équipe depuis la messagerie.
  trigger_mode    text not null default 'ia' check (trigger_mode in ('ia', 'equipe')),
  is_paid         boolean not null default true,
  price_cents     integer not null default 0 check (price_cents >= 0),
  min_price_cents integer not null default 0 check (min_price_cents >= 0),
  max_price_cents integer not null default 0 check (max_price_cents >= 0),
  created_at      timestamptz not null default now(),
  constraint script_steps_prix_check check (
    not is_paid or (min_price_cents > 0 and min_price_cents <= price_cents and price_cents <= max_price_cents))
);
create index if not exists script_steps_script_idx on public.script_steps (script_id, position);

-- Chaque message du script peut contenir plusieurs photos et vidéos (au plus
-- 10), dans l'ordre : [{"path": "...", "kind": "image" | "video"}].
alter table public.script_steps add column if not exists media jsonb not null default '[]'::jsonb;
alter table public.script_steps drop constraint if exists script_steps_media_check;
alter table public.script_steps add constraint script_steps_media_check
  check (jsonb_typeof(media) = 'array' and jsonb_array_length(media) <= 10);
-- L'ancien format (un seul fichier, media_path) passe une fois dans la liste.
update public.script_steps
   set media = jsonb_build_array(jsonb_build_object(
         'path', media_path, 'kind', case when content_type = 'video' then 'video' else 'image' end)),
       media_path = null
 where media_path is not null and media = '[]'::jsonb;


-- ─── La fiche contact : ce que l'équipe règle pour chaque personne ────────
create table if not exists public.contacts (
  user_id              uuid primary key references auth.users (id) on delete cascade,
  -- Mode hybride : l'IA a-t-elle le droit de répondre à cette personne ?
  ai_enabled           boolean not null default true,
  -- Tout ce qui aide l'IA à savoir comment se comporter avec elle.
  notes                text not null default '' check (char_length(notes) <= 5000),
  emojis               text not null default '' check (char_length(emojis) <= 400),
  city                 text not null default '' check (char_length(city) <= 120),
  timezone             text not null default 'Europe/Paris' check (char_length(timezone) <= 64),
  script_id            bigint references public.scripts (id) on delete set null,
  -- Plafond de dépenses par mois propre à cette personne (sinon celui des réglages).
  spending_cap_cents   integer check (spending_cap_cents is null or spending_cap_cents >= 0),
  last_read_message_id bigint not null default 0,
  updated_at           timestamptz not null default now()
);


-- ─── Les réglages de l'IA (une seule ligne) ────────────────────────────────
create table if not exists public.ai_settings (
  id                 integer primary key default 1 check (id = 1),
  -- auto : l'IA répond à tout le monde ; hybride : seulement aux personnes
  -- cochées ; manuel : l'IA ne répond plus, l'équipe prend tout.
  mode               text not null default 'auto' check (mode in ('auto', 'hybride', 'manuel')),
  temperature        numeric(3, 2) not null default 0.80 check (temperature between 0 and 2),
  max_tokens         integer not null default 600 check (max_tokens between 100 and 4000),
  context_messages   integer not null default 20 check (context_messages between 6 and 60),
  -- Le profil du personnage (nom, âge, apparence, centres d'intérêt…).
  persona            jsonb not null default '{}'::jsonb check (octet_length(persona::text) <= 60000),
  first_message      text not null default '' check (char_length(first_message) <= 2000),
  extra_instructions text not null default '' check (char_length(extra_instructions) <= 5000),
  -- Garde-fous de la vente.
  spending_cap_cents integer not null default 10000 check (spending_cap_cents >= 0),
  sales_min_messages integer not null default 10 check (sales_min_messages >= 0),
  sales_gap_messages integer not null default 12 check (sales_gap_messages >= 0),
  updated_at         timestamptz not null default now()
);
insert into public.ai_settings (id) values (1) on conflict (id) do nothing;


-- ─── Les créatrices : les personnages que l'IA peut incarner ──────────────
-- Chaque créatrice a son profil (nom, âge, apparence, centres d'intérêt…),
-- son premier message, et ses réglages avec chaque personne. L'IA incarne
-- la créatrice choisie dans l'onglet IA (ai_settings.creator_id).
create table if not exists public.creators (
  id            bigint generated always as identity primary key,
  persona       jsonb not null default '{}'::jsonb check (octet_length(persona::text) <= 60000),
  first_message text not null default '' check (char_length(first_message) <= 2000),
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- Avec chaque personne : l'IA peut-elle lui répondre en mode hybride, et
-- avec quels emojis. Sans ligne ici : oui, et sans emoji imposé.
create table if not exists public.creator_contacts (
  creator_id bigint not null references public.creators (id) on delete cascade,
  user_id    uuid not null references auth.users (id) on delete cascade,
  ai_enabled boolean not null default true,
  emojis     text not null default '' check (char_length(emojis) <= 400),
  updated_at timestamptz not null default now(),
  primary key (creator_id, user_id)
);

alter table public.ai_settings add column if not exists creator_id bigint references public.creators (id) on delete set null;

-- Une seule fois : le personnage réglé avant les créatrices en devient une,
-- active, avec les réglages déjà faits pour chaque personne.
do $$
declare
  reglages public.ai_settings;
  nouvelle bigint;
begin
  if exists (select 1 from public.creators) then
    return;
  end if;
  select * into reglages from public.ai_settings where id = 1;
  if reglages.persona = '{}'::jsonb and reglages.first_message = '' then
    return;
  end if;
  insert into public.creators (persona, first_message)
  values (reglages.persona, reglages.first_message)
  returning id into nouvelle;
  update public.ai_settings set creator_id = nouvelle where id = 1;
  insert into public.creator_contacts (creator_id, user_id, ai_enabled, emojis)
  select nouvelle, c.user_id, c.ai_enabled, c.emojis
  from public.contacts c
  where not c.ai_enabled or c.emojis <> '';
end;
$$;


-- ─── Les offres : un contenu proposé à une personne, à son prix ───────────
-- Le prix peut être personnalisé (entre le minimum et le maximum de
-- l'étape) : il est alors affiché comme tel. La personne peut faire une
-- contre-offre, jamais acceptée sous le minimum, et au plus trois refusées.
create table if not exists public.offers (
  id              bigint generated always as identity primary key,
  user_id         uuid not null references auth.users (id) on delete cascade,
  step_id         bigint references public.script_steps (id) on delete set null,
  content_type    text not null check (content_type in ('image', 'video', 'texte')),
  price_cents     integer not null check (price_cents >= 0),
  personalized    boolean not null default false,
  status          text not null default 'proposee' check (status in ('proposee', 'achetee', 'offerte', 'retiree')),
  proposed_by     text not null check (proposed_by in ('ai', 'team')),
  bids_refused    integer not null default 0,
  last_bid_cents  integer,
  last_bid_status text check (last_bid_status in ('acceptee', 'refusee')),
  created_at      timestamptz not null default now(),
  purchased_at    timestamptz
);
create index if not exists offers_user_idx on public.offers (user_id, created_at desc);

-- Ce que contient l'offre, pour l'annoncer sans rien montrer : « 3 photos à
-- débloquer ». Les offres d'avant (un seul fichier) comptent pour un.
alter table public.offers add column if not exists photo_count integer not null default 0;
alter table public.offers add column if not exists video_count integer not null default 0;
update public.offers set photo_count = 1 where content_type = 'image' and photo_count = 0 and video_count = 0;
update public.offers set video_count = 1 where content_type = 'video' and photo_count = 0 and video_count = 0;

alter table public.messages  add column if not exists offer_id bigint references public.offers (id) on delete set null;
alter table public.purchases add column if not exists offer_id bigint references public.offers (id) on delete set null;


-- ─── Qui voit quoi ─────────────────────────────────────────────────────────
alter table public.profiles     enable row level security;
alter table public.scripts      enable row level security;
alter table public.script_steps enable row level security;
alter table public.contacts     enable row level security;
alter table public.ai_settings  enable row level security;
alter table public.offers       enable row level security;
alter table public.creators         enable row level security;
alter table public.creator_contacts enable row level security;

revoke all on public.profiles, public.scripts, public.script_steps, public.contacts,
  public.ai_settings, public.offers, public.creators, public.creator_contacts from anon, authenticated;
grant select, insert, update, delete on public.creators         to authenticated;
grant select, insert, update, delete on public.creator_contacts to authenticated;
grant select                         on public.profiles     to authenticated;
grant select, insert, update, delete on public.scripts      to authenticated;
grant select, insert, update, delete on public.script_steps to authenticated;
grant select, insert, update         on public.contacts     to authenticated;
grant select, update                 on public.ai_settings  to authenticated;
grant select, update                 on public.offers       to authenticated;

-- Chacun voit son profil et ses offres ; l'équipe voit tout. Scripts,
-- fiches contact et réglages ne sont visibles que de l'équipe : une personne
-- ne peut donc jamais lire un prix minimum ni les notes à son sujet.
drop policy if exists "Lire son profil" on public.profiles;
create policy "Lire son profil" on public.profiles for select to authenticated
  using ((select auth.uid()) = user_id or (select public.is_admin()));

drop policy if exists "Voir ses offres" on public.offers;
create policy "Voir ses offres" on public.offers for select to authenticated
  using ((select auth.uid()) = user_id or (select public.is_admin()));
drop policy if exists "L'équipe gère les offres" on public.offers;
create policy "L'équipe gère les offres" on public.offers for update to authenticated
  using ((select public.is_admin())) with check ((select public.is_admin()));

drop policy if exists "L'équipe gère les scripts" on public.scripts;
create policy "L'équipe gère les scripts" on public.scripts for all to authenticated
  using ((select public.is_admin())) with check ((select public.is_admin()));
drop policy if exists "L'équipe gère les étapes" on public.script_steps;
create policy "L'équipe gère les étapes" on public.script_steps for all to authenticated
  using ((select public.is_admin())) with check ((select public.is_admin()));
drop policy if exists "L'équipe gère les fiches contact" on public.contacts;
create policy "L'équipe gère les fiches contact" on public.contacts for all to authenticated
  using ((select public.is_admin())) with check ((select public.is_admin()));
drop policy if exists "L'équipe gère les créatrices" on public.creators;
create policy "L'équipe gère les créatrices" on public.creators for all to authenticated
  using ((select public.is_admin())) with check ((select public.is_admin()));
drop policy if exists "L'équipe règle chaque créatrice avec chacun" on public.creator_contacts;
create policy "L'équipe règle chaque créatrice avec chacun" on public.creator_contacts for all to authenticated
  using ((select public.is_admin())) with check ((select public.is_admin()));
drop policy if exists "L'équipe règle l'IA" on public.ai_settings;
create policy "L'équipe règle l'IA" on public.ai_settings for all to authenticated
  using ((select public.is_admin())) with check ((select public.is_admin()));

-- L'équipe lit toutes les conversations et ce que l'IA sait de chacun.
drop policy if exists "L'équipe lit les messages" on public.messages;
create policy "L'équipe lit les messages" on public.messages for select to authenticated
  using ((select public.is_admin()));
drop policy if exists "L'équipe lit les fiches" on public.user_facts;
create policy "L'équipe lit les fiches" on public.user_facts for select to authenticated
  using ((select public.is_admin()));
drop policy if exists "L'équipe voit les achats" on public.purchases;
create policy "L'équipe voit les achats" on public.purchases for select to authenticated
  using ((select public.is_admin()));


-- ─── La vente : l'étape suivante, toujours dans l'ordre ────────────────────
-- Le script d'une personne : celui de sa fiche, sinon le premier.
create or replace function public.script_de(p_user uuid)
returns bigint
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce(
    (select c.script_id from public.contacts c where c.user_id = p_user and c.script_id is not null),
    (select s.id from public.scripts s order by s.position, s.id limit 1));
$$;

-- La première étape du script ni vendue, ni offerte, ni en cours d'offre.
create or replace function public.prochaine_etape(p_user uuid)
returns public.script_steps
language sql
stable
security definer
set search_path = ''
as $$
  select st.* from public.script_steps st
  where st.script_id = public.script_de(p_user)
    and not exists (
      select 1 from public.offers o
      where o.user_id = p_user and o.step_id = st.id and o.status in ('proposee', 'achetee', 'offerte'))
  order by st.position, st.id
  limit 1;
$$;

-- Ce qu'une personne a dépensé ce mois-ci (heure de Paris).
create or replace function public.depense_du_mois(p_user uuid)
returns integer
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce(sum(amount_cents), 0)::integer from public.purchases
  where user_id = p_user
    and date_trunc('month', created_at at time zone 'Europe/Paris')
      = date_trunc('month', now() at time zone 'Europe/Paris');
$$;

create or replace function public.plafond_de(p_user uuid)
returns integer
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce(
    (select c.spending_cap_cents from public.contacts c where c.user_id = p_user),
    (select s.spending_cap_cents from public.ai_settings s where s.id = 1));
$$;

-- Proposer un contenu : uniquement l'étape suivante, une seule offre en
-- attente à la fois, prix ramené entre le minimum et le maximum. Une étape
-- gratuite est offerte tout de suite. Usage interne (IA ou équipe).
create or replace function public.proposer_etape(p_user uuid, p_step bigint, p_prix_cents integer,
                                                 p_message text, p_par text, p_auteur uuid)
returns jsonb
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  suivante public.script_steps;
  prix     integer;
  offre    public.offers;
  message  bigint;
begin
  suivante := public.prochaine_etape(p_user);
  if suivante.id is null then
    raise exception 'Il n''y a plus rien à proposer à cette personne dans son script.' using errcode = 'P0001';
  end if;
  if p_step is distinct from suivante.id then
    raise exception 'L''ordre de vente impose de proposer d''abord « % ».', suivante.title using errcode = 'P0001';
  end if;
  if exists (select 1 from public.offers where user_id = p_user and status = 'proposee') then
    raise exception 'Une offre attend déjà une réponse de cette personne.' using errcode = 'P0001';
  end if;
  if suivante.is_paid then
    prix := least(greatest(coalesce(p_prix_cents, suivante.price_cents), suivante.min_price_cents), suivante.max_price_cents);
  else
    prix := 0;
  end if;

  insert into public.offers (user_id, step_id, content_type, photo_count, video_count,
                             price_cents, personalized, status, proposed_by)
  values (p_user, suivante.id, suivante.content_type,
          (select count(*) from jsonb_array_elements(suivante.media) m where m ->> 'kind' = 'image')::integer,
          (select count(*) from jsonb_array_elements(suivante.media) m where m ->> 'kind' = 'video')::integer,
          prix,
          suivante.is_paid and prix <> suivante.price_cents,
          case when suivante.is_paid then 'proposee' else 'offerte' end, p_par)
  returning * into offre;

  insert into public.messages (user_id, role, author, author_id, kind, offer_id, content)
  values (p_user, 'assistant', p_par, case when p_par = 'team' then p_auteur end, 'offer', offre.id,
          coalesce(nullif(trim(p_message), ''), case when suivante.is_paid then 'Un contenu pour vous.' else 'Un petit cadeau pour vous.' end))
  returning id into message;

  return jsonb_build_object('offre', to_jsonb(offre), 'message_id', message);
end;
$$;

-- L'équipe propose depuis la messagerie.
create or replace function public.admin_proposer(p_user uuid, p_step bigint, p_prix_cents integer, p_message text)
returns jsonb
language plpgsql
volatile
security definer
set search_path = ''
as $$
begin
  if not public.is_admin() then
    raise exception 'Réservé aux administrateurs.' using errcode = '42501';
  end if;
  return public.proposer_etape(p_user, p_step, p_prix_cents, p_message, 'team', (select auth.uid()));
end;
$$;

-- L'équipe retire une offre restée sans réponse : l'étape redevient proposable.
create or replace function public.admin_retirer_offre(p_offre bigint)
returns void
language plpgsql
volatile
security definer
set search_path = ''
as $$
begin
  if not public.is_admin() then
    raise exception 'Réservé aux administrateurs.' using errcode = '42501';
  end if;
  update public.offers set status = 'retiree' where id = p_offre and status = 'proposee';
end;
$$;


-- ─── Côté personne : acheter, faire une offre, voir ce qu'on a acheté ─────
-- Acheter une offre à son prix affiché, dans la limite du plafond du mois.
-- Tant qu'aucun service de paiement n'est branché, l'achat est marqué
-- « démo » : aucun argent ne circule.
create or replace function public.acheter_offre(p_offre bigint)
returns jsonb
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  o       public.offers;
  plafond integer;
  achat   bigint;
begin
  select * into o from public.offers where id = p_offre and user_id = (select auth.uid()) for update;
  if not found then
    raise exception 'Offre introuvable.' using errcode = 'P0002';
  end if;
  if o.status <> 'proposee' then
    raise exception 'Cette offre n''est plus disponible.' using errcode = 'P0001';
  end if;
  plafond := public.plafond_de(o.user_id);
  if plafond is not null and public.depense_du_mois(o.user_id) + o.price_cents > plafond then
    raise exception 'Vous avez atteint le plafond de dépenses de ce mois-ci.' using errcode = 'P0001';
  end if;

  insert into public.purchases (user_id, kind, amount_cents, is_demo, offer_id)
  values (o.user_id, 'contenu', o.price_cents, true, o.id)
  returning id into achat;
  update public.offers set status = 'achetee', purchased_at = now() where id = o.id;
  return jsonb_build_object('offre', o.id, 'achat', achat, 'cents', o.price_cents);
end;
$$;

-- Faire une offre, comme sur un site de revente : acceptée si elle atteint
-- le prix minimum (sans jamais le révéler), refusée sinon. Au bout de trois
-- refus, on ne peut plus faire d'offre sur ce contenu.
create or replace function public.faire_une_offre(p_offre bigint, p_montant_cents integer)
returns jsonb
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  o       public.offers;
  minimum integer;
begin
  select * into o from public.offers where id = p_offre and user_id = (select auth.uid()) for update;
  if not found then
    raise exception 'Offre introuvable.' using errcode = 'P0002';
  end if;
  if o.status <> 'proposee' then
    raise exception 'Cette offre n''est plus disponible.' using errcode = 'P0001';
  end if;
  if p_montant_cents is null or p_montant_cents <= 0 then
    raise exception 'Indiquez un montant.' using errcode = 'P0001';
  end if;
  if o.bids_refused >= 3 then
    raise exception 'Vous avez déjà fait trois offres refusées pour ce contenu.' using errcode = 'P0001';
  end if;

  if p_montant_cents >= o.price_cents then
    -- Proposer plus que le prix affiché : on garde le prix affiché.
    update public.offers set last_bid_cents = p_montant_cents, last_bid_status = 'acceptee' where id = o.id;
    return jsonb_build_object('statut', 'acceptee', 'prix_cents', o.price_cents);
  end if;

  select st.min_price_cents into minimum from public.script_steps st where st.id = o.step_id;
  if p_montant_cents >= coalesce(minimum, o.price_cents) then
    update public.offers
    set price_cents = p_montant_cents, personalized = true, last_bid_cents = p_montant_cents, last_bid_status = 'acceptee'
    where id = o.id;
    return jsonb_build_object('statut', 'acceptee', 'prix_cents', p_montant_cents);
  end if;

  update public.offers
  set bids_refused = bids_refused + 1, last_bid_cents = p_montant_cents, last_bid_status = 'refusee'
  where id = o.id;
  return jsonb_build_object('statut', 'refusee', 'prix_cents', o.price_cents, 'essais_restants', 2 - o.bids_refused);
end;
$$;

-- Le contenu lui-même, seulement une fois acheté (ou offert). Sans achat,
-- rien ne sort : ni le texte, ni le fichier, ni un aperçu.
create or replace function public.mon_contenu(p_offre bigint)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  resultat jsonb;
begin
  select jsonb_build_object('type', st.content_type, 'texte', st.content_text, 'media', st.media)
  into resultat
  from public.offers o
  join public.script_steps st on st.id = o.step_id
  where o.id = p_offre and o.user_id = (select auth.uid()) and o.status in ('achetee', 'offerte');
  if resultat is null then
    raise exception 'Contenu verrouillé.' using errcode = '42501';
  end if;
  return resultat;
end;
$$;


-- ─── La messagerie de l'équipe ─────────────────────────────────────────────
-- La liste des conversations, la plus récente d'abord.
create or replace function public.admin_boite()
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  resultat jsonb;
begin
  if not public.is_admin() then
    raise exception 'Réservé aux administrateurs.' using errcode = '42501';
  end if;
  with dernier as (
    select distinct on (m.user_id) m.user_id, m.id, m.author, m.kind, m.content, m.created_at
    from public.messages m
    order by m.user_id, m.id desc
  )
  select coalesce(jsonb_agg(jsonb_build_object(
           'user_id', d.user_id,
           'email', u.email,
           'nom', coalesce(p.display_name, split_part(u.email, '@', 1)),
           'dernier', jsonb_build_object('id', d.id, 'auteur', d.author, 'type', d.kind,
                                         'texte', left(d.content, 160), 'date', d.created_at),
           'non_lus', (select count(*) from public.messages m
                       where m.user_id = d.user_id and m.role = 'user' and m.id > coalesce(c.last_read_message_id, 0)),
           -- En mode hybride, ce que la créatrice active a le droit de faire.
           'ia_autorisee', coalesce((select cc.ai_enabled
                                     from public.creator_contacts cc
                                     join public.ai_settings s on s.id = 1 and s.creator_id = cc.creator_id
                                     where cc.user_id = d.user_id), true),
           'depense_cents', (select coalesce(sum(pu.amount_cents), 0) from public.purchases pu where pu.user_id = d.user_id))
         order by d.id desc), '[]'::jsonb)
  into resultat
  from dernier d
  join auth.users u on u.id = d.user_id
  left join public.profiles p on p.user_id = d.user_id
  left join public.contacts c on c.user_id = d.user_id;
  return resultat;
end;
$$;

-- Qui est cette personne (l'adresse e-mail n'est lisible que d'ici).
create or replace function public.admin_personne(p_user uuid)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  resultat jsonb;
begin
  if not public.is_admin() then
    raise exception 'Réservé aux administrateurs.' using errcode = '42501';
  end if;
  select jsonb_build_object(
    'user_id', u.id,
    'email', u.email,
    'nom', coalesce(p.display_name, split_part(u.email, '@', 1)),
    'age', case when p.birthdate is null then null else extract(year from age(p.birthdate))::integer end,
    'inscrit_le', u.created_at,
    'depense_cents', (select coalesce(sum(amount_cents), 0) from public.purchases where user_id = u.id),
    'depense_mois_cents', public.depense_du_mois(u.id),
    'plafond_cents', public.plafond_de(u.id),
    'script_id', public.script_de(u.id),
    'prochaine_etape', (select to_jsonb(e) from public.prochaine_etape(u.id) e where e.id is not null))
  into resultat
  from auth.users u
  left join public.profiles p on p.user_id = u.id
  where u.id = p_user;
  return resultat;
end;
$$;

-- Écrire à une personne au nom de l'équipe ; le message est signé « Équipe ».
create or replace function public.admin_envoyer(p_user uuid, p_texte text)
returns bigint
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  nouveau bigint;
begin
  if not public.is_admin() then
    raise exception 'Réservé aux administrateurs.' using errcode = '42501';
  end if;
  if coalesce(trim(p_texte), '') = '' then
    raise exception 'Le message est vide.' using errcode = 'P0001';
  end if;
  insert into public.messages (user_id, role, author, author_id, kind, content)
  values (p_user, 'assistant', 'team', (select auth.uid()), 'text', trim(p_texte))
  returning id into nouveau;
  perform public.admin_marquer_lu(p_user);
  return nouveau;
end;
$$;

create or replace function public.admin_marquer_lu(p_user uuid)
returns void
language plpgsql
volatile
security definer
set search_path = ''
as $$
begin
  if not public.is_admin() then
    raise exception 'Réservé aux administrateurs.' using errcode = '42501';
  end if;
  insert into public.contacts (user_id, last_read_message_id)
  values (p_user, coalesce((select max(id) from public.messages where user_id = p_user), 0))
  on conflict (user_id) do update set last_read_message_id = excluded.last_read_message_id;
end;
$$;


-- ─── Le bouton « Effacer toutes mes données » ──────────────────────────────
-- Efface d'un seul coup, et seulement pour la personne connectée, ses
-- messages, sa fiche, son résumé, et les notes de l'équipe à son sujet. Le
-- compte reste, ses achats aussi (ce sont des traces comptables).
create or replace function public.effacer_mes_donnees()
returns void
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  moi uuid := (select auth.uid());
begin
  if moi is null then
    raise exception 'Connexion requise.' using errcode = '42501';
  end if;
  delete from public.messages   where user_id = moi;
  delete from public.user_facts where user_id = moi;
  delete from public.summaries  where user_id = moi;
  update public.contacts set notes = '', emojis = '', city = '', last_read_message_id = 0 where user_id = moi;
  update public.creator_contacts set emojis = '' where user_id = moi;
end;
$$;


-- ─── Les droits sur les fonctions ──────────────────────────────────────────
-- Par défaut, tout le monde peut appeler une fonction : on referme tout,
-- puis on rouvre ce qui doit l'être. Les fonctions internes ne sont
-- appelables que par le serveur (rôle service_role, clé secrète).
revoke execute on function
  public.enregistrer_profil(text, date), public.script_de(uuid), public.prochaine_etape(uuid),
  public.depense_du_mois(uuid), public.plafond_de(uuid),
  public.proposer_etape(uuid, bigint, integer, text, text, uuid),
  public.admin_proposer(uuid, bigint, integer, text), public.admin_retirer_offre(bigint),
  public.acheter_offre(bigint), public.faire_une_offre(bigint, integer), public.mon_contenu(bigint),
  public.admin_boite(), public.admin_personne(uuid), public.admin_envoyer(uuid, text),
  public.admin_marquer_lu(uuid), public.effacer_mes_donnees()
  from public, anon, authenticated;
grant execute on function
  public.enregistrer_profil(text, date), public.acheter_offre(bigint),
  public.faire_une_offre(bigint, integer), public.mon_contenu(bigint), public.effacer_mes_donnees(),
  public.admin_proposer(uuid, bigint, integer, text), public.admin_retirer_offre(bigint),
  public.admin_boite(), public.admin_personne(uuid), public.admin_envoyer(uuid, text),
  public.admin_marquer_lu(uuid)
  to authenticated;
grant execute on function
  public.script_de(uuid), public.prochaine_etape(uuid), public.depense_du_mois(uuid), public.plafond_de(uuid),
  public.proposer_etape(uuid, bigint, integer, text, text, uuid)
  to service_role;


-- ─── Le rangement des médias à vendre (privé) ──────────────────────────────
-- Rien n'y est public : un fichier ne sort que par un lien temporaire, créé
-- par le serveur pour une personne qui l'a acheté. 50 Mo au plus par fichier.
do $$
begin
  if exists (select 1 from pg_namespace where nspname = 'storage') then
    insert into storage.buckets (id, name, public, file_size_limit)
    values ('contenus', 'contenus', false, 52428800)
    on conflict (id) do nothing;
  end if;
end;
$$;
