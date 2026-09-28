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
