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
  with check ((select auth.uid()) = user_id);
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


-- ─── Le bouton « Effacer toutes mes données » ──────────────────────────────
-- Efface d'un seul coup, et seulement pour la personne connectée, ses
-- messages, sa fiche et son résumé. Le compte lui-même reste.
create or replace function public.effacer_mes_donnees()
returns void
language sql
security invoker
set search_path = ''
as $$
  delete from public.messages   where user_id = (select auth.uid());
  delete from public.user_facts where user_id = (select auth.uid());
  delete from public.summaries  where user_id = (select auth.uid());
$$;
revoke execute on function public.effacer_mes_donnees() from public, anon;
grant  execute on function public.effacer_mes_donnees() to authenticated;


-- ═══════════════════════════════════════════════════════════════════════════
-- Le tableau de bord des gains (page /admin)
-- ═══════════════════════════════════════════════════════════════════════════

-- ─── Les achats : pourboires, messages achetés, abonnements ────────────────
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
  kind           text not null check (kind in ('tip', 'message', 'abonnement')),
  quantity       integer not null default 1 check (quantity > 0),
  amount_cents   integer not null check (amount_cents > 0),
  currency       text not null default 'EUR' check (currency = 'EUR'),
  is_demo        boolean not null default false,
  created_at     timestamptz not null default now()
);
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
           bool_or(kind = 'abonnement' and created_at > now() - interval '31 days') as abonne,
           sum(amount_cents)                                                 as total_cents,
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
               coalesce(sum(p.amount_cents) filter (where p.kind = 'abonnement'), 0) as abonnements
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
    case when tirage < 0.45 then 'tip' when tirage < 0.85 then 'message' else 'abonnement' end,
    case when tirage >= 0.45 and tirage < 0.85 then (array[5, 10, 20])[pack + 1] else 1 end,
    case when tirage < 0.45 then (array[200, 300, 500, 1000])[1 + floor(random() * 4)::integer]
         when tirage < 0.85 then (array[199, 349, 599])[pack + 1]
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
