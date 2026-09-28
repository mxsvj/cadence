-- ═══════════════════════════════════════════════════════════════════════════
-- Devenir administrateur (accès au tableau de bord, page /admin).
--
-- 1. Créer d'abord son compte sur le site Élise, comme n'importe qui.
-- 2. Remplacer l'adresse ci-dessous par celle de ce compte.
-- 3. Coller le tout dans Supabase → SQL Editor → New query, puis « Run ».
--    Le message attendu est « Success. 1 row affected » (ou 0 si c'était
--    déjà fait).
-- ═══════════════════════════════════════════════════════════════════════════
insert into public.admins (user_id)
select id from auth.users where email = 'ton.adresse@exemple.fr'
on conflict do nothing;
