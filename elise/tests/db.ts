// Une base PostgreSQL neuve (PGlite, en mémoire) avec supabase/schema.sql
// chargé, et une imitation minimale de ce que Supabase fournit : le schéma
// auth, auth.uid(), et les rôles anon et authenticated.
import { PGlite } from "@electric-sql/pglite";
import { readFileSync } from "node:fs";
import path from "node:path";

export const schemaSql = readFileSync(path.join(import.meta.dirname, "..", "supabase", "schema.sql"), "utf8");

export async function freshDatabase(users: { id: string; email: string }[]) {
  const db = new PGlite();
  await db.exec(`
    create role anon nologin;
    create role authenticated nologin;
    create schema auth;
    create table auth.users (id uuid primary key, email text);
    create function auth.uid() returns uuid language sql stable as $$
      select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid
    $$;
    grant usage on schema auth to anon, authenticated;
    grant usage on schema public to anon, authenticated;
    -- Comme Supabase : droits larges par défaut, que le script resserre.
    alter default privileges in schema public grant all on tables to anon, authenticated;
    alter default privileges in schema public grant all on functions to anon, authenticated;
  `);
  for (const u of users) await db.query("insert into auth.users (id, email) values ($1, $2)", [u.id, u.email]);
  await db.exec(schemaSql);
  await db.exec(schemaSql); // relançable sans erreur

  // Exécute `sql` comme le ferait Supabase pour la personne `user` (ou un
  // visiteur non connecté si `user` est null), dans une transaction.
  async function as<T = Record<string, unknown>>(user: string | null, sql: string, params: unknown[] = []): Promise<T[]> {
    await db.exec("begin");
    try {
      if (user) {
        await db.exec(`set local role authenticated; select set_config('request.jwt.claim.sub', '${user}', true);`);
      } else {
        await db.exec("set local role anon;");
      }
      return (await db.query<T>(sql, params)).rows;
    } finally {
      await db.exec("commit"); // annule tout si la requête a échoué
    }
  }

  return { db, as };
}
