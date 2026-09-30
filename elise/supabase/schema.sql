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
-- « relance » : le message de l'IA qui prend des nouvelles après une absence.
alter table public.messages add constraint messages_kind_check check (kind in ('text', 'offer', 'relance'));


-- ─── La fiche : ce qu'Élise sait de l'utilisateur ──────────────────────────
-- Une phrase courte par fait. Jamais de santé, religion, orientation
-- sexuelle ni argent : le tri est fait avant l'enregistrement.
create table if not exists public.user_facts (
  id         bigint generated always as identity primary key,
  user_id    uuid not null default auth.uid() references auth.users (id) on delete cascade,
  fact       text not null check (char_length(fact) between 1 and 300),
  created_at timestamptz not null default now()
);
-- Pas deux fois le même fait (majuscules comprises) dans une même
-- conversation : voir « une conversation par créatrice », plus bas.


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
-- (Renforcée plus bas : seulement avec une créatrice en ligne.)
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
-- p_debut, p_fin : la période, en dates (heure de Paris) ; p_debut vide =
-- depuis le premier achat, p_fin vide = aujourd'hui. p_creator : une
-- créatrice (vide : toutes). p_net : les montants après les frais de
-- paiement estimés (1,5 % + 0,25 € par achat, tarif Stripe des cartes
-- européennes), sinon les montants payés (brut). La courbe compte par jour
-- jusqu'à 3 mois, par semaine jusqu'à 2 ans, par mois au-delà.
drop function if exists public.admin_dashboard(text, integer);
create or replace function public.admin_dashboard(p_debut date default null, p_fin date default null,
                                                  p_creator bigint default null, p_net boolean default false)
returns jsonb
language plpgsql
stable
security definer
set search_path = ''
as $$
declare
  aujourdhui date    := (now() at time zone 'Europe/Paris')::date;
  fin        date    := least(coalesce(p_fin, aujourdhui), aujourdhui);
  debut      date;
  tout       boolean := p_debut is null;
  duree      integer;
  pas        text;
  resultat   jsonb;
begin
  if not public.is_admin() then
    raise exception 'Réservé aux administrateurs.' using errcode = '42501';
  end if;
  -- « Depuis le début » : à partir du premier achat de la sélection.
  debut := coalesce(p_debut,
                    (select min((p.created_at at time zone 'Europe/Paris')::date) from public.purchases p
                     where p_creator is null or p.creator_id = p_creator),
                    fin);
  if debut > fin then
    debut := fin;
  end if;
  duree := fin - debut + 1;
  pas := case when duree <= 92 then 'day' when duree <= 731 then 'week' else 'month' end;

  with achats as (
    select p.id, p.kind, p.quantity, p.created_at, p.is_demo, p.creator_id,
           case when p_net then greatest(p.amount_cents - round(p.amount_cents * 0.015)::integer - 25, 0)
                else p.amount_cents end                                        as amount_cents,
           coalesce(p.user_id::text, 'demo:' || p.customer_label, 'supprime') as client,
           coalesce(u.email, p.customer_label, 'Compte supprimé')             as nom,
           (p.created_at at time zone 'Europe/Paris')::date                   as jour
    from public.purchases p
    left join auth.users u on u.id = p.user_id
    where p_creator is null or p.creator_id = p_creator
  ),
  periode as (
    select * from achats where jour between debut and fin
  ),
  pas_de_la_periode as (
    select d::date as jour
    from generate_series(date_trunc(pas, debut::timestamp), fin::timestamp, ('1 ' || pas)::interval) as d
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
    'debut', debut,
    'fin', fin,
    'jours', duree,
    'pas', case pas when 'day' then 'jour' when 'week' then 'semaine' else 'mois' end,
    'net', coalesce(p_net, false),
    'createur', p_creator,
    'createurs', (select coalesce(jsonb_agg(jsonb_build_object(
                    'id', c.id,
                    'nom', coalesce(nullif(trim(c.persona ->> 'nom'), ''), nullif(trim(c.persona ->> 'pseudo'), ''), 'Élise'))
                    order by c.id), '[]'::jsonb)
                  from public.creators c),
    'demo', exists (select 1 from public.purchases where is_demo),
    'totaux', jsonb_build_object(
      'depuis_le_debut',   (select coalesce(sum(amount_cents), 0) from achats),
      'periode',           (select coalesce(sum(amount_cents), 0) from periode),
      -- La même durée juste avant (rien à comparer pour « depuis le début »).
      'periode_precedente', case when tout then null else
                              (select coalesce(sum(amount_cents), 0) from achats
                               where jour between debut - duree and debut - 1) end,
      'pourboires', (select jsonb_build_object('nombre', count(*), 'cents', coalesce(sum(amount_cents), 0))
                       from periode where kind = 'tip'),
      'messages',   (select jsonb_build_object('nombre', coalesce(sum(quantity), 0), 'achats', count(*),
                                               'cents', coalesce(sum(amount_cents), 0))
                       from periode where kind = 'message'),
      'contenus',   (select jsonb_build_object('nombre', count(*), 'cents', coalesce(sum(amount_cents), 0))
                       from periode where kind = 'contenu'),
      'abonnements', (select jsonb_build_object(
                         'actifs', (select count(distinct client) from achats
                                     where kind = 'abonnement' and created_at > now() - interval '31 days'),
                         'nombre', count(*),
                         'cents',  coalesce(sum(amount_cents), 0))
                       from periode where kind = 'abonnement')
    ),
    -- Un point par jour, semaine ou mois (la date de son début).
    'serie', (
      select jsonb_agg(to_jsonb(s) order by s.jour)
      from (
        select j.jour,
               coalesce(sum(p.amount_cents), 0)                                   as total,
               coalesce(sum(p.amount_cents) filter (where p.kind = 'tip'), 0)        as pourboires,
               coalesce(sum(p.amount_cents) filter (where p.kind = 'message'), 0)    as messages,
               coalesce(sum(p.amount_cents) filter (where p.kind = 'abonnement'), 0) as abonnements,
               coalesce(sum(p.amount_cents) filter (where p.kind = 'contenu'), 0)    as contenus
        from pas_de_la_periode j
        left join periode p on date_trunc(pas, p.jour::timestamp)::date = j.jour
        group by j.jour
      ) s
    ),
    'derniers', coalesce((
      select jsonb_agg(jsonb_build_object(
               'id', d.id, 'client', d.client, 'nom', d.nom, 'type', d.kind,
               'quantite', d.quantity, 'cents', d.amount_cents, 'date', d.created_at, 'demo', d.is_demo,
               'createur', (select coalesce(nullif(trim(c.persona ->> 'nom'), ''), nullif(trim(c.persona ->> 'pseudo'), ''), 'Élise')
                            from public.creators c where c.id = d.creator_id))
             order by d.created_at desc, d.id desc)
      from (select * from achats order by created_at desc, id desc limit 12) d
    ), '[]'::jsonb),
    -- La LTV : ce qu'un client a dépensé au total, sur tout l'historique.
    'ltv', (
      select jsonb_build_object(
        'clients',            count(*),
        'moyenne_cents',      coalesce(round(avg(total_cents)), 0),
        'mediane_cents',      coalesce(round(percentile_cont(0.5) within group (order by total_cents)), 0),
        'max_cents',          coalesce(max(total_cents), 0),
        'achats_par_client',  coalesce(round(avg(achats), 1), 0),
        'panier_moyen_cents', coalesce(round(sum(total_cents)::numeric / nullif(sum(achats), 0)), 0),
        'duree_moyenne_jours', coalesce(round(avg(extract(epoch from dernier_achat - premier_achat) / 86400 + 1)), 0)
      )
      from clients
    ),
    -- Combien de clients dans chaque tranche de LTV.
    'repartition', (
      select jsonb_agg(jsonb_build_object(
               'min_cents', t.min_cents, 'max_cents', t.max_cents,
               'clients', (select count(*) from clients c
                           where c.total_cents >= t.min_cents and (t.max_cents is null or c.total_cents < t.max_cents)))
             order by t.min_cents)
      from (values (0, 1000), (1000, 2500), (2500, 5000), (5000, 10000), (10000, null::integer)) as t(min_cents, max_cents)
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
  insert into public.purchases (customer_label, kind, quantity, amount_cents, is_demo, created_at, creator_id)
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
    p_quand,
    (select c.id from public.creators c order by random() limit 1)
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

revoke execute on function public.is_admin(), public.admin_dashboard(date, date, bigint, boolean),
  public.admin_simuler_achat(), public.admin_remplir_demo(integer), public.admin_vider_demo()
  from public, anon;
grant execute on function public.is_admin(), public.admin_dashboard(date, date, bigint, boolean),
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
-- Quand le proposer : le sujet de conversation que ce contenu illustre
-- (« quand il parle de voyages »). Vide : quand la conversation s'y prête.
alter table public.script_steps add column if not exists moment text not null default '';
alter table public.script_steps drop constraint if exists script_steps_moment_check;
alter table public.script_steps add constraint script_steps_moment_check check (char_length(moment) <= 300);

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

-- Les emojis de la créatrice avec chaque personne : au choix de l'IA selon la
-- discussion (libre), seulement ceux de la liste (choisis), ou aucun. À
-- l'arrivée de ce réglage, une liste déjà remplie devient « choisis ».
do $$
begin
  if not exists (select 1 from information_schema.columns
                 where table_schema = 'public' and table_name = 'creator_contacts' and column_name = 'emoji_mode') then
    alter table public.creator_contacts add column emoji_mode text not null default 'libre'
      check (emoji_mode in ('libre', 'choisis', 'aucun'));
    update public.creator_contacts set emoji_mode = 'choisis' where emojis <> '';
  end if;
end;
$$;

-- Un script de vente appartient à une créatrice, ou sert à toutes (null).
alter table public.scripts add column if not exists creator_id bigint references public.creators (id) on delete set null;

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
  if exists (select 1 from information_schema.columns
             where table_schema = 'public' and table_name = 'creators' and column_name = 'active') then
    update public.creators set active = true where id = nouvelle;
  end if;
  update public.ai_settings set creator_id = nouvelle where id = 1;
  insert into public.creator_contacts (creator_id, user_id, ai_enabled, emojis, emoji_mode)
  select nouvelle, c.user_id, c.ai_enabled, c.emojis, case when c.emojis <> '' then 'choisis' else 'libre' end
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


-- ─── Plusieurs créatrices en ligne, une conversation avec chacune ─────────
-- Chaque personne choisit avec quelle créatrice parler (celles « en ligne »).
-- Chaque conversation (personne, créatrice) a ses messages, sa mémoire, son
-- résumé et ses offres, sans rien partager avec les autres.
do $$
begin
  if not exists (select 1 from information_schema.columns
                 where table_schema = 'public' and table_name = 'creators' and column_name = 'active') then
    alter table public.creators add column active boolean not null default false;
    -- La première fois : celle que l'IA incarnait jusqu'ici passe en ligne.
    update public.creators set active = true where id = (select creator_id from public.ai_settings where id = 1);
    if not exists (select 1 from public.creators where active) then
      update public.creators set active = true where id = (select min(id) from public.creators);
    end if;
  end if;
  -- Sans aucune créatrice, le personnage par défaut (« Élise ») en devient une.
  if not exists (select 1 from public.creators) then
    insert into public.creators (persona, first_message, active) values ('{"nom": "Élise"}'::jsonb, '', true);
  end if;
end;
$$;

-- La créatrice de chaque conversation. Ce qui existait avant revient à celle
-- que l'IA incarnait (sinon à la première en ligne).
alter table public.messages   add column if not exists creator_id bigint references public.creators (id) on delete cascade;
alter table public.user_facts add column if not exists creator_id bigint references public.creators (id) on delete cascade;
alter table public.summaries  add column if not exists creator_id bigint references public.creators (id) on delete cascade;
alter table public.offers     add column if not exists creator_id bigint references public.creators (id) on delete cascade;
alter table public.creator_contacts add column if not exists last_read_message_id bigint not null default 0;
do $$
declare
  repli bigint := coalesce(
    (select s.creator_id from public.ai_settings s where s.id = 1 and s.creator_id is not null),
    (select min(c.id) from public.creators c where c.active),
    (select min(c.id) from public.creators c));
begin
  if exists (select 1 from public.messages where creator_id is null) then
    -- Ce que l'équipe avait déjà lu reste lu.
    insert into public.creator_contacts (creator_id, user_id, last_read_message_id)
    select repli, c.user_id, c.last_read_message_id from public.contacts c where c.last_read_message_id > 0
    on conflict (creator_id, user_id) do update set last_read_message_id = excluded.last_read_message_id;
  end if;
  update public.messages   set creator_id = repli where creator_id is null;
  update public.user_facts set creator_id = repli where creator_id is null;
  update public.summaries  set creator_id = repli where creator_id is null;
  update public.offers     set creator_id = repli where creator_id is null;
end;
$$;
alter table public.messages   alter column creator_id set not null;
alter table public.user_facts alter column creator_id set not null;
alter table public.summaries  alter column creator_id set not null;
alter table public.offers     alter column creator_id set not null;

create index if not exists messages_conversation_idx on public.messages (user_id, creator_id, id);
create index if not exists offers_conversation_idx on public.offers (user_id, creator_id);
drop index if exists public.user_facts_user_id_fact_key;
create unique index if not exists user_facts_conversation_fact_key
  on public.user_facts (user_id, creator_id, lower(fact));
-- Un résumé par conversation.
do $$
begin
  if exists (select 1 from pg_constraint
             where conname = 'summaries_pkey' and conrelid = 'public.summaries'::regclass and cardinality(conkey) = 1) then
    alter table public.summaries drop constraint summaries_pkey;
    alter table public.summaries add constraint summaries_pkey primary key (user_id, creator_id);
  end if;
end;
$$;

-- Chaque achat est rattaché à une créatrice (pour le tableau de bord) : celle
-- de l'offre achetée ; les achats de démonstration d'avant, à une au hasard.
alter table public.purchases add column if not exists creator_id bigint references public.creators (id) on delete set null;
create index if not exists purchases_creator_idx on public.purchases (creator_id, created_at);
update public.purchases p set creator_id = o.creator_id
from public.offers o
where p.offer_id = o.id and p.creator_id is null;
update public.purchases p
set creator_id = (select c.id from public.creators c where p.id is not null order by random() limit 1)
where p.is_demo and p.creator_id is null;

-- Une créatrice que les personnes peuvent choisir.
create or replace function public.creatrice_disponible(p_creator bigint)
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (select 1 from public.creators where id = p_creator and active);
$$;

-- Ce que les personnes voient des créatrices en ligne, pour choisir : jamais
-- le reste du profil ni les consignes de l'équipe.
create or replace function public.creatrices_disponibles()
returns jsonb
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce(jsonb_agg(jsonb_build_object(
           'id', c.id,
           'nom', coalesce(nullif(trim(c.persona ->> 'nom'), ''), nullif(trim(c.persona ->> 'pseudo'), ''), 'Élise'),
           'age', case when (c.persona ->> 'age') ~ '^[0-9]{1,2}$' then (c.persona ->> 'age')::integer end,
           'ville', nullif(trim(c.persona ->> 'ville'), ''),
           'profession', nullif(trim(c.persona ->> 'profession'), ''))
         order by c.id), '[]'::jsonb)
  from public.creators c
  where c.active;
$$;


-- ─── Les alertes de l'équipe ───────────────────────────────────────────────
-- Ce qui mérite qu'un humain regarde une conversation tout de suite : une
-- contre-offre sur un contenu payant, une personne qui demande un humain ou
-- dont le message demande de l'attention. On ne garde que le type d'alerte,
-- la raison en un mot et des montants : jamais le texte des messages, jamais
-- rien sur la santé.
create table if not exists public.team_alerts (
  id          bigint generated always as identity primary key,
  user_id     uuid not null references auth.users (id) on delete cascade,
  creator_id  bigint not null references public.creators (id) on delete cascade,
  kind        text not null check (kind in ('contre_offre', 'urgence')),
  offer_id    bigint references public.offers (id) on delete set null,
  detail      jsonb not null default '{}'::jsonb check (octet_length(detail::text) <= 1000),
  created_at  timestamptz not null default now(),
  -- Envoyée sur Discord ou Telegram (null : pas encore).
  notified_at timestamptz,
  -- Traitée par l'équipe (null : à traiter).
  handled_at  timestamptz,
  handled_by  uuid references auth.users (id) on delete set null
);
create index if not exists team_alerts_open_idx on public.team_alerts (user_id, creator_id) where handled_at is null;

alter table public.team_alerts enable row level security;
revoke all on public.team_alerts from anon, authenticated;
grant select on public.team_alerts to authenticated;
drop policy if exists "L'équipe voit les alertes" on public.team_alerts;
create policy "L'équipe voit les alertes" on public.team_alerts for select to authenticated
  using ((select public.is_admin()));

-- « Prendre la main » : dans cette conversation, l'IA se tait (quel que soit
-- le mode) et l'équipe répond, jusqu'à ce qu'elle rende la main.
alter table public.creator_contacts add column if not exists manual boolean not null default false;


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

-- Une personne n'écrit qu'à une créatrice en ligne.
drop policy if exists "Écrire ses messages" on public.messages;
create policy "Écrire ses messages" on public.messages for insert to authenticated
  with check ((select auth.uid()) = user_id and role = 'user' and author = 'user' and kind = 'text'
              and public.creatrice_disponible(creator_id));

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
-- Les anciennes versions, d'avant les conversations par créatrice.
drop function if exists public.script_de(uuid);
drop function if exists public.prochaine_etape(uuid);
drop function if exists public.proposer_etape(uuid, bigint, integer, text, text, uuid);
drop function if exists public.admin_proposer(uuid, bigint, integer, text);
drop function if exists public.admin_personne(uuid);
drop function if exists public.admin_envoyer(uuid, text);
drop function if exists public.admin_marquer_lu(uuid);

-- Le script d'une conversation : celui de la fiche de la personne (s'il est
-- à cette créatrice ou à toutes), sinon le premier de la créatrice, sinon le
-- premier qui sert à toutes.
create or replace function public.script_de(p_user uuid, p_creator bigint)
returns bigint
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce(
    (select c.script_id from public.contacts c
       join public.scripts s on s.id = c.script_id
      where c.user_id = p_user and (s.creator_id is null or s.creator_id = p_creator)),
    (select s.id from public.scripts s where s.creator_id = p_creator order by s.position, s.id limit 1),
    (select s.id from public.scripts s where s.creator_id is null order by s.position, s.id limit 1));
$$;

-- La première étape du script ni vendue, ni offerte, ni en cours d'offre
-- (un contenu déjà obtenu avec une créatrice ne se revend pas avec une autre).
create or replace function public.prochaine_etape(p_user uuid, p_creator bigint)
returns public.script_steps
language sql
stable
security definer
set search_path = ''
as $$
  select st.* from public.script_steps st
  where st.script_id = public.script_de(p_user, p_creator)
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

-- Proposer un contenu dans une conversation : uniquement l'étape suivante,
-- une seule offre en attente à la fois (toutes créatrices confondues), prix
-- ramené entre le minimum et le maximum. Une étape gratuite est offerte tout
-- de suite. Usage interne (IA ou équipe).
create or replace function public.proposer_etape(p_user uuid, p_creator bigint, p_step bigint, p_prix_cents integer,
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
  suivante := public.prochaine_etape(p_user, p_creator);
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

  insert into public.offers (user_id, creator_id, step_id, content_type, photo_count, video_count,
                             price_cents, personalized, status, proposed_by)
  values (p_user, p_creator, suivante.id, suivante.content_type,
          (select count(*) from jsonb_array_elements(suivante.media) m where m ->> 'kind' = 'image')::integer,
          (select count(*) from jsonb_array_elements(suivante.media) m where m ->> 'kind' = 'video')::integer,
          prix,
          suivante.is_paid and prix <> suivante.price_cents,
          case when suivante.is_paid then 'proposee' else 'offerte' end, p_par)
  returning * into offre;

  insert into public.messages (user_id, creator_id, role, author, author_id, kind, offer_id, content)
  values (p_user, p_creator, 'assistant', p_par, case when p_par = 'team' then p_auteur end, 'offer', offre.id,
          coalesce(nullif(trim(p_message), ''), case when suivante.is_paid then 'Un contenu pour vous.' else 'Un petit cadeau pour vous.' end))
  returning id into message;

  return jsonb_build_object('offre', to_jsonb(offre), 'message_id', message);
end;
$$;

-- L'équipe propose depuis la messagerie, dans une conversation.
create or replace function public.admin_proposer(p_user uuid, p_creator bigint, p_step bigint, p_prix_cents integer, p_message text)
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
  return public.proposer_etape(p_user, p_creator, p_step, p_prix_cents, p_message, 'team', (select auth.uid()));
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
-- Acheter une offre à son prix affiché.
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
  o     public.offers;
  achat bigint;
begin
  select * into o from public.offers where id = p_offre and user_id = (select auth.uid()) for update;
  if not found then
    raise exception 'Offre introuvable.' using errcode = 'P0002';
  end if;
  if o.status <> 'proposee' then
    raise exception 'Cette offre n''est plus disponible.' using errcode = 'P0001';
  end if;

  insert into public.purchases (user_id, kind, amount_cents, is_demo, offer_id, creator_id)
  values (o.user_id, 'contenu', o.price_cents, true, o.id, o.creator_id)
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
  o        public.offers;
  minimum  integer;
  resultat jsonb;
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
    resultat := jsonb_build_object('statut', 'acceptee', 'prix_cents', o.price_cents);
  else
    select st.min_price_cents into minimum from public.script_steps st where st.id = o.step_id;
    if p_montant_cents >= coalesce(minimum, o.price_cents) then
      update public.offers
      set price_cents = p_montant_cents, personalized = true, last_bid_cents = p_montant_cents, last_bid_status = 'acceptee'
      where id = o.id;
      resultat := jsonb_build_object('statut', 'acceptee', 'prix_cents', p_montant_cents);
    else
      update public.offers
      set bids_refused = bids_refused + 1, last_bid_cents = p_montant_cents, last_bid_status = 'refusee'
      where id = o.id;
      resultat := jsonb_build_object('statut', 'refusee', 'prix_cents', o.price_cents, 'essais_restants', 2 - o.bids_refused);
    end if;
  end if;

  -- L'équipe est prévenue de chaque contre-offre (une alerte par offre,
  -- mise à jour à chaque nouvelle proposition).
  perform public.alerter_equipe(o.user_id, o.creator_id, 'contre_offre', o.id,
    jsonb_build_object('montant_cents', p_montant_cents, 'prix_cents', o.price_cents,
                       'statut', resultat ->> 'statut', 'essais_restants', resultat -> 'essais_restants'));
  return resultat;
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
-- La liste des conversations (une par personne et par créatrice), la plus
-- récente d'abord.
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
    select distinct on (m.user_id, m.creator_id) m.user_id, m.creator_id, m.id, m.author, m.kind, m.content, m.created_at
    from public.messages m
    order by m.user_id, m.creator_id, m.id desc
  )
  select coalesce(jsonb_agg(jsonb_build_object(
           'user_id', d.user_id,
           'creator_id', d.creator_id,
           'creatrice', coalesce(nullif(trim(cr.persona ->> 'nom'), ''), nullif(trim(cr.persona ->> 'pseudo'), ''), 'Élise'),
           'email', u.email,
           'nom', coalesce(p.display_name, split_part(u.email, '@', 1)),
           'dernier', jsonb_build_object('id', d.id, 'auteur', d.author, 'type', d.kind,
                                         'texte', left(d.content, 160), 'date', d.created_at),
           'non_lus', (select count(*) from public.messages m
                       where m.user_id = d.user_id and m.creator_id = d.creator_id and m.role = 'user'
                         and m.id > coalesce(cc.last_read_message_id, 0)),
           -- En mode hybride : cette créatrice a-t-elle le droit de lui répondre ?
           'ia_autorisee', coalesce(cc.ai_enabled, true),
           -- L'équipe a pris la main : l'IA se tait dans cette conversation.
           'manuel', coalesce(cc.manual, false),
           -- Les alertes à traiter : urgence, contre_offre.
           'alertes', (select coalesce(jsonb_agg(distinct a.kind), '[]'::jsonb) from public.team_alerts a
                       where a.user_id = d.user_id and a.creator_id = d.creator_id and a.handled_at is null),
           'depense_cents', (select coalesce(sum(pu.amount_cents), 0) from public.purchases pu where pu.user_id = d.user_id))
         order by d.id desc), '[]'::jsonb)
  into resultat
  from dernier d
  join auth.users u on u.id = d.user_id
  join public.creators cr on cr.id = d.creator_id
  left join public.profiles p on p.user_id = d.user_id
  left join public.creator_contacts cc on cc.creator_id = d.creator_id and cc.user_id = d.user_id;
  return resultat;
end;
$$;

-- Qui est cette personne (l'adresse e-mail n'est lisible que d'ici), et où
-- en est la vente dans sa conversation avec cette créatrice.
create or replace function public.admin_personne(p_user uuid, p_creator bigint)
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
    'creator_id', p_creator,
    'email', u.email,
    'nom', coalesce(p.display_name, split_part(u.email, '@', 1)),
    'age', case when p.birthdate is null then null else extract(year from age(p.birthdate))::integer end,
    'inscrit_le', u.created_at,
    'depense_cents', (select coalesce(sum(amount_cents), 0) from public.purchases where user_id = u.id),
    'depense_mois_cents', public.depense_du_mois(u.id),
    'script_id', public.script_de(u.id, p_creator),
    'prochaine_etape', (select to_jsonb(e) from public.prochaine_etape(u.id, p_creator) e where e.id is not null))
  into resultat
  from auth.users u
  left join public.profiles p on p.user_id = u.id
  where u.id = p_user;
  return resultat;
end;
$$;

-- Écrire dans une conversation au nom de l'équipe ; le message est signé
-- « Équipe ».
create or replace function public.admin_envoyer(p_user uuid, p_creator bigint, p_texte text)
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
  insert into public.messages (user_id, creator_id, role, author, author_id, kind, content)
  values (p_user, p_creator, 'assistant', 'team', (select auth.uid()), 'text', trim(p_texte))
  returning id into nouveau;
  perform public.admin_marquer_lu(p_user, p_creator);
  return nouveau;
end;
$$;

-- Ce que l'équipe a lu, conversation par conversation.
create or replace function public.admin_marquer_lu(p_user uuid, p_creator bigint)
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
  insert into public.creator_contacts (creator_id, user_id, last_read_message_id)
  values (p_creator, p_user,
          coalesce((select max(id) from public.messages where user_id = p_user and creator_id = p_creator), 0))
  on conflict (creator_id, user_id) do update set last_read_message_id = excluded.last_read_message_id;
end;
$$;


-- ─── Les alertes : prévenir, envoyer, traiter ─────────────────────────────
-- Prévenir l'équipe (usage interne : contre-offres ci-dessus, et le serveur
-- pour les urgences). Une contre-offre met à jour l'alerte encore
-- ouverte de la même offre ; une urgence n'est créée que si la conversation
-- n'en a pas déjà une à traiter.
-- Renvoie l'alerte créée ou mise à jour (null : rien de nouveau).
create or replace function public.alerter_equipe(p_user uuid, p_creator bigint, p_kind text, p_offer bigint, p_detail jsonb)
returns bigint
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  alerte bigint;
begin
  if p_kind = 'contre_offre' then
    update public.team_alerts
    set detail = coalesce(p_detail, '{}'::jsonb), created_at = now(), notified_at = null
    where kind = 'contre_offre' and offer_id = p_offer and handled_at is null
    returning id into alerte;
    if alerte is not null then
      return alerte;
    end if;
  elsif p_kind = 'urgence' then
    if exists (select 1 from public.team_alerts
               where kind = 'urgence' and user_id = p_user and creator_id = p_creator and handled_at is null) then
      return null;
    end if;
  end if;
  insert into public.team_alerts (user_id, creator_id, kind, offer_id, detail)
  values (p_user, p_creator, p_kind, p_offer, coalesce(p_detail, '{}'::jsonb))
  returning id into alerte;
  return alerte;
end;
$$;

-- Les alertes à envoyer sur Discord ou Telegram, marquées comme envoyées
-- (deux envois en même temps ne prennent jamais les mêmes). Seulement celles
-- du dernier jour, encore à traiter. Usage interne.
create or replace function public.alertes_a_envoyer(p_limite integer default 10)
returns jsonb
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  resultat jsonb;
begin
  with prises as (
    update public.team_alerts a
    set notified_at = now()
    where a.id in (select t.id from public.team_alerts t
                   where t.notified_at is null and t.handled_at is null and t.created_at > now() - interval '1 day'
                   order by t.id
                   limit greatest(p_limite, 0)
                   for update skip locked)
    returning a.*
  )
  select coalesce(jsonb_agg(jsonb_build_object(
           'id', p.id, 'kind', p.kind, 'user_id', p.user_id, 'creator_id', p.creator_id,
           'creatrice', coalesce(nullif(trim(c.persona ->> 'nom'), ''), nullif(trim(c.persona ->> 'pseudo'), ''), 'Élise'),
           'detail', p.detail)
         order by p.id), '[]'::jsonb)
  into resultat
  from prises p
  join public.creators c on c.id = p.creator_id;
  return resultat;
end;
$$;

-- Les alertes à traiter, les plus récentes d'abord, pour le bandeau et la
-- messagerie de l'équipe.
create or replace function public.admin_alertes()
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
  select coalesce(jsonb_agg(jsonb_build_object(
           'id', a.id, 'kind', a.kind, 'user_id', a.user_id, 'creator_id', a.creator_id, 'offer_id', a.offer_id,
           'nom', coalesce(p.display_name, split_part(u.email, '@', 1)),
           'creatrice', coalesce(nullif(trim(c.persona ->> 'nom'), ''), nullif(trim(c.persona ->> 'pseudo'), ''), 'Élise'),
           'detail', a.detail, 'date', a.created_at)
         order by a.created_at desc, a.id desc), '[]'::jsonb)
  into resultat
  from (select * from public.team_alerts where handled_at is null order by created_at desc, id desc limit 100) a
  join auth.users u on u.id = a.user_id
  join public.creators c on c.id = a.creator_id
  left join public.profiles p on p.user_id = a.user_id;
  return resultat;
end;
$$;

-- Marquer traitée une alerte (p_alerte) ou toutes celles d'une conversation.
-- Au passage, les alertes traitées depuis plus de 90 jours sont effacées.
create or replace function public.admin_traiter_alertes(p_user uuid, p_creator bigint, p_alerte bigint default null)
returns integer
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  nombre integer;
begin
  if not public.is_admin() then
    raise exception 'Réservé aux administrateurs.' using errcode = '42501';
  end if;
  update public.team_alerts
  set handled_at = now(), handled_by = (select auth.uid())
  where user_id = p_user and creator_id = p_creator and handled_at is null
    and (p_alerte is null or id = p_alerte);
  get diagnostics nombre = row_count;
  delete from public.team_alerts where handled_at < now() - interval '90 days';
  return nombre;
end;
$$;

-- Prendre la main (l'IA se tait dans cette conversation) ou la rendre à l'IA.
create or replace function public.admin_prendre_la_main(p_user uuid, p_creator bigint, p_manuel boolean)
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
  insert into public.creator_contacts (creator_id, user_id, manual)
  values (p_creator, p_user, coalesce(p_manuel, false))
  on conflict (creator_id, user_id) do update set manual = excluded.manual, updated_at = now();
end;
$$;


-- ─── Les codes d'accès par client (ne servent plus) ─────────────────────────
-- Première version de l'entrée par code (un code par client). Remplacée par
-- le code d'entrée unique ci-dessous : la table et sa fonction restent, sans
-- effet, pour ne rien effacer d'une base déjà à jour.
create table if not exists public.access_codes (
  user_id      uuid primary key references auth.users (id) on delete cascade,
  code_hash    text not null unique check (char_length(code_hash) = 64),
  hint         text not null default '' check (char_length(hint) <= 4),
  label        text not null default '' check (char_length(label) <= 60),
  created_at   timestamptz not null default now(),
  created_by   uuid references auth.users (id) on delete set null,
  last_used_at timestamptz
);
-- Personne ne lit la table depuis le navigateur, pas même l'équipe : seul le
-- serveur (clé secrète) vérifie un code ; l'équipe voit la liste par
-- admin_codes(), sans les empreintes.
alter table public.access_codes enable row level security;
revoke all on public.access_codes from anon, authenticated;

-- La liste des codes pour l'équipe : à qui, créé quand, utilisé quand.
create or replace function public.admin_codes()
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
  select coalesce(jsonb_agg(jsonb_build_object(
           'user_id', c.user_id,
           'label', c.label,
           'nom', coalesce(p.display_name, nullif(c.label, ''), 'Sans prénom'),
           'hint', c.hint,
           'cree_le', c.created_at,
           'utilise_le', c.last_used_at)
         order by c.created_at desc), '[]'::jsonb)
  into resultat
  from (select * from public.access_codes order by created_at desc limit 500) c
  left join public.profiles p on p.user_id = c.user_id;
  return resultat;
end;
$$;
revoke execute on function public.admin_codes() from public, anon;
grant execute on function public.admin_codes() to authenticated;


-- ─── Le code d'entrée ─────────────────────────────────────────────────────
-- Un seul code, le même pour tout le monde (prototype de test) : on le tape
-- sur /connexion avec son prénom et sa date de naissance, et on parle à
-- l'IA. Chaque entrée crée un compte de test à part, avec sa propre
-- conversation. L'équipe voit le code et le change dans Paramètres.
create table if not exists public.entry_code (
  id         integer primary key default 1 check (id = 1),
  code       text not null check (code ~ '^[A-HJKMNP-Z2-9]{4}-[A-HJKMNP-Z2-9]{4}$'),
  updated_at timestamptz not null default now(),
  updated_by uuid references auth.users (id) on delete set null
);
-- Personne ne lit la table depuis le navigateur : le serveur (clé secrète)
-- vérifie le code, l'équipe le voit par admin_code_entree().
alter table public.entry_code enable row level security;
revoke all on public.entry_code from anon, authenticated;

-- Le code actuel ; s'il n'y en a pas encore, p_nouveau le devient.
create or replace function public.admin_code_entree(p_nouveau text)
returns jsonb
language plpgsql
volatile
security definer
set search_path = ''
as $$
declare
  actuel public.entry_code;
begin
  if not public.is_admin() then
    raise exception 'Réservé aux administrateurs.' using errcode = '42501';
  end if;
  insert into public.entry_code (id, code, updated_by)
  values (1, p_nouveau, (select auth.uid()))
  on conflict (id) do nothing;
  select * into actuel from public.entry_code where id = 1;
  return jsonb_build_object('code', actuel.code, 'change_le', actuel.updated_at);
end;
$$;

-- Un nouveau code : l'ancien ne marche plus (les personnes déjà entrées le restent).
create or replace function public.admin_changer_code_entree(p_code text)
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
  insert into public.entry_code (id, code, updated_by)
  values (1, p_code, (select auth.uid()))
  on conflict (id) do update set code = excluded.code, updated_at = now(), updated_by = excluded.updated_by;
  return jsonb_build_object('code', p_code, 'change_le', now());
end;
$$;
revoke execute on function public.admin_code_entree(text) from public, anon;
revoke execute on function public.admin_changer_code_entree(text) from public, anon;
grant execute on function public.admin_code_entree(text) to authenticated;
grant execute on function public.admin_changer_code_entree(text) to authenticated;


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
  delete from public.team_alerts where user_id = moi;
  update public.contacts set notes = '', emojis = '', city = '', last_read_message_id = 0 where user_id = moi;
  update public.creator_contacts set emojis = '', emoji_mode = 'libre', last_read_message_id = 0 where user_id = moi;
end;
$$;


-- ─── Prendre des nouvelles après une absence ──────────────────────────────
-- Coupé tant que l'équipe ne l'active pas (onglet Paramètres). Chaque
-- personne peut le refuser depuis son menu. Un seul message par absence :
-- tant qu'elle n'est pas revenue, l'IA n'écrit plus. Jamais de vente dedans,
-- et jamais sous une offre qui attend sa réponse.
alter table public.ai_settings add column if not exists relance_active boolean not null default false;
alter table public.ai_settings add column if not exists relance_heures integer not null default 48;
alter table public.ai_settings drop constraint if exists ai_settings_relance_heures_check;
alter table public.ai_settings add constraint ai_settings_relance_heures_check check (relance_heures between 24 and 336);

alter table public.profiles add column if not exists relances_ok boolean not null default true;
-- Dernière visite (même sans écrire), à dix minutes près.
alter table public.profiles add column if not exists vu_le timestamptz;

create or replace function public.regler_relances(p_ok boolean)
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
  update public.profiles set relances_ok = coalesce(p_ok, true) where user_id = (select auth.uid());
end;
$$;

create or replace function public.marquer_visite()
returns void
language sql
volatile
security definer
set search_path = ''
as $$
  update public.profiles set vu_le = now()
  where user_id = (select auth.uid()) and (vu_le is null or vu_le < now() - interval '10 minutes');
$$;

-- Les conversations où prendre des nouvelles : la dernière conversation de
-- chaque personne absente depuis p_heures (ni visite ni message), qui a déjà
-- écrit au moins une fois, qui accepte ces messages, avec une créatrice en
-- ligne qui a le droit de lui écrire (pas en mode manuel ; en hybride,
-- seulement si elle est cochée), et dont le dernier message n'est ni une
-- prise de nouvelles ni une offre en attente. Une seule par personne. Les
-- plus anciennes absences d'abord.
drop function if exists public.a_relancer(integer, integer);
create or replace function public.a_relancer(p_heures integer, p_limite integer default 50)
returns table (user_id uuid, creator_id bigint)
language sql
stable
security definer
set search_path = ''
as $$
  select p.user_id, dernier.creator_id
  from public.profiles p
  join lateral (
    select m.kind, m.created_at, m.creator_id from public.messages m
    where m.user_id = p.user_id
    order by m.id desc
    limit 1
  ) dernier on true
  where p.relances_ok
    and dernier.kind <> 'relance'
    and greatest(dernier.created_at, coalesce(p.vu_le, dernier.created_at)) < now() - make_interval(hours => p_heures)
    and exists (select 1 from public.messages m where m.user_id = p.user_id and m.role = 'user')
    and not exists (select 1 from public.offers o where o.user_id = p.user_id and o.status = 'proposee')
    and not exists (select 1 from public.admins a where a.user_id = p.user_id)
    and public.creatrice_disponible(dernier.creator_id)
    and not exists (select 1 from public.ai_settings s where s.id = 1 and s.mode = 'manuel')
    and not exists (select 1 from public.creator_contacts cc
                    join public.ai_settings s on s.id = 1 and s.mode = 'hybride'
                    where cc.creator_id = dernier.creator_id and cc.user_id = p.user_id and not cc.ai_enabled)
    -- Ni quand l'équipe a pris la main, ni sous une urgence à traiter.
    and not exists (select 1 from public.creator_contacts cc
                    where cc.creator_id = dernier.creator_id and cc.user_id = p.user_id and cc.manual)
    and not exists (select 1 from public.team_alerts a
                    where a.user_id = p.user_id and a.kind = 'urgence' and a.handled_at is null)
  order by dernier.created_at
  limit greatest(p_limite, 0);
$$;


-- ─── Plus de plafond de dépenses, de pause après un achat ni de quota ──────
-- Retirés à la demande du porteur du projet : plus de limite d'achat, plus
-- de pause après un achat, plus de nombre maximum d'offres payantes par
-- jour. Restent le rythme réglable (messages avant la première offre et
-- entre deux offres), une offre en attente à la fois, et aucune vente
-- pendant une urgence à traiter.
drop function if exists public.plafond_de(uuid);
alter table public.contacts    drop column if exists spending_cap_cents;
alter table public.ai_settings drop column if exists spending_cap_cents;
alter table public.ai_settings drop column if exists sales_pause_hours;
alter table public.ai_settings drop column if exists sales_max_per_day;
delete from public.team_alerts where kind not in ('contre_offre', 'urgence');
alter table public.team_alerts drop constraint if exists team_alerts_kind_check;
alter table public.team_alerts add constraint team_alerts_kind_check check (kind in ('contre_offre', 'urgence'));


-- ─── Les droits sur les fonctions ──────────────────────────────────────────
-- Par défaut, tout le monde peut appeler une fonction : on referme tout,
-- puis on rouvre ce qui doit l'être. Les fonctions internes ne sont
-- appelables que par le serveur (rôle service_role, clé secrète).
revoke execute on function
  public.enregistrer_profil(text, date), public.script_de(uuid, bigint), public.prochaine_etape(uuid, bigint),
  public.depense_du_mois(uuid),
  public.proposer_etape(uuid, bigint, bigint, integer, text, text, uuid),
  public.admin_proposer(uuid, bigint, bigint, integer, text), public.admin_retirer_offre(bigint),
  public.acheter_offre(bigint), public.faire_une_offre(bigint, integer), public.mon_contenu(bigint),
  public.admin_boite(), public.admin_personne(uuid, bigint), public.admin_envoyer(uuid, bigint, text),
  public.admin_marquer_lu(uuid, bigint), public.effacer_mes_donnees(),
  public.regler_relances(boolean), public.marquer_visite(), public.a_relancer(integer, integer),
  public.creatrice_disponible(bigint), public.creatrices_disponibles(),
  public.alerter_equipe(uuid, bigint, text, bigint, jsonb), public.alertes_a_envoyer(integer), public.admin_alertes(),
  public.admin_traiter_alertes(uuid, bigint, bigint), public.admin_prendre_la_main(uuid, bigint, boolean)
  from public, anon, authenticated;
grant execute on function
  public.enregistrer_profil(text, date), public.acheter_offre(bigint),
  public.faire_une_offre(bigint, integer), public.mon_contenu(bigint), public.effacer_mes_donnees(),
  public.admin_proposer(uuid, bigint, bigint, integer, text), public.admin_retirer_offre(bigint),
  public.admin_boite(), public.admin_personne(uuid, bigint), public.admin_envoyer(uuid, bigint, text),
  public.admin_marquer_lu(uuid, bigint), public.regler_relances(boolean), public.marquer_visite(),
  public.creatrice_disponible(bigint), public.creatrices_disponibles(),
  public.admin_alertes(), public.admin_traiter_alertes(uuid, bigint, bigint), public.admin_prendre_la_main(uuid, bigint, boolean)
  to authenticated;
grant execute on function
  public.script_de(uuid, bigint), public.prochaine_etape(uuid, bigint), public.depense_du_mois(uuid),
  public.proposer_etape(uuid, bigint, bigint, integer, text, text, uuid), public.a_relancer(integer, integer),
  public.alerter_equipe(uuid, bigint, text, bigint, jsonb), public.alertes_a_envoyer(integer)
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
