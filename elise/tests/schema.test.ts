// Essaie supabase/schema.sql sur un vrai PostgreSQL (PGlite, en mémoire),
// avec une imitation minimale de ce que Supabase fournit : le schéma auth,
// auth.uid(), et les rôles anon et authenticated.
import { PGlite } from "@electric-sql/pglite";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { before, describe, it } from "node:test";

const A = "11111111-1111-1111-1111-111111111111";
const B = "22222222-2222-2222-2222-222222222222";
const db = new PGlite();

// Exécute `sql` comme le ferait Supabase pour la personne `user` (ou un
// visiteur non connecté si `user` est null), dans une transaction.
async function as<T = Record<string, unknown>>(user: string | null, sql: string): Promise<T[]> {
  await db.exec("begin");
  try {
    if (user) {
      await db.exec(`set local role authenticated; select set_config('request.jwt.claim.sub', '${user}', true);`);
    } else {
      await db.exec("set local role anon;");
    }
    return (await db.query<T>(sql)).rows;
  } finally {
    await db.exec("commit"); // annule tout si la requête a échoué
  }
}
const count = async (user: string, table: string) =>
  (await as<{ n: number }>(user, `select count(*)::int as n from public.${table}`))[0].n;

before(async () => {
  await db.exec(`
    create role anon nologin;
    create role authenticated nologin;
    create schema auth;
    create table auth.users (id uuid primary key);
    create function auth.uid() returns uuid language sql stable as $$
      select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid
    $$;
    grant usage on schema auth to anon, authenticated;
    grant usage on schema public to anon, authenticated;
    -- Comme Supabase : droits larges par défaut, que le script resserre.
    alter default privileges in schema public grant all on tables to anon, authenticated;
    alter default privileges in schema public grant all on functions to anon, authenticated;
    insert into auth.users values ('${A}'), ('${B}');
  `);
  const schema = readFileSync(path.join(import.meta.dirname, "..", "supabase", "schema.sql"), "utf8");
  await db.exec(schema);
  await db.exec(schema); // relançable sans erreur

  await as(A, `insert into public.messages (role, content) values ('assistant', 'Bonjour A'), ('user', 'Salut')`);
  await as(B, `insert into public.messages (role, content) values ('assistant', 'Bonjour B')`);
  await as(A, `insert into public.user_facts (fact) values ('Se prénomme Karim.')`);
  await as(B, `insert into public.user_facts (fact) values ('Se prénomme Léa.')`);
  await as(A, `insert into public.summaries (summary, last_message_id) values ('Résumé A', 1)`);
  await as(B, `insert into public.summaries (summary) values ('Résumé B')`);
});

describe("supabase/schema.sql", () => {
  it("remplit user_id tout seul et ne montre à chacun que ses lignes", async () => {
    const rows = await as<{ content: string; user_id: string }>(A, `select content, user_id from public.messages order by id`);
    assert.deepEqual(rows.map((r) => r.content), ["Bonjour A", "Salut"]);
    assert.ok(rows.every((r) => r.user_id === A));
    assert.deepEqual((await as<{ fact: string }>(B, `select fact from public.user_facts`)).map((r) => r.fact), ["Se prénomme Léa."]);
    assert.deepEqual((await as<{ summary: string }>(A, `select summary from public.summaries`)).map((r) => r.summary), ["Résumé A"]);
  });

  it("interdit d'écrire au nom de quelqu'un d'autre", async () => {
    await assert.rejects(as(A, `insert into public.messages (user_id, role, content) values ('${B}', 'user', 'intrus')`));
    await assert.rejects(as(A, `insert into public.user_facts (user_id, fact) values ('${B}', 'intrus')`));
    await assert.rejects(as(A, `update public.summaries set user_id = '${B}' where user_id = '${A}'`));
    await as(A, `update public.summaries set summary = 'piraté' where user_id = '${B}'`); // ne touche rien
    assert.equal((await as<{ summary: string }>(B, `select summary from public.summaries`))[0].summary, "Résumé B");
  });

  it("interdit de modifier un message", async () => {
    await assert.rejects(as(A, `update public.messages set content = 'modifié'`));
  });

  it("refuse les doublons dans une fiche, majuscules comprises, mais pas d'une fiche à l'autre", async () => {
    await assert.rejects(as(A, `insert into public.user_facts (fact) values ('se prénomme karim.')`));
    await as(B, `insert into public.user_facts (fact) values ('Se prénomme Karim.')`);
  });

  it("contrôle les rôles et les messages vides", async () => {
    await assert.rejects(as(A, `insert into public.messages (role, content) values ('system', 'x')`));
    await assert.rejects(as(A, `insert into public.messages (role, content) values ('user', '')`));
  });

  it("met le résumé à jour", async () => {
    await as(A, `insert into public.summaries (summary, last_message_id) values ('Résumé A2', 2)
      on conflict (user_id) do update set summary = excluded.summary, last_message_id = excluded.last_message_id`);
    const [row] = await as<{ summary: string; last_message_id: number }>(A, `select summary, last_message_id from public.summaries`);
    assert.equal(row.summary, "Résumé A2");
    assert.equal(Number(row.last_message_id), 2);
  });

  it("ne donne rien aux visiteurs non connectés", async () => {
    await assert.rejects(as(null, `select * from public.messages`));
    await assert.rejects(as(null, `insert into public.messages (role, content) values ('user', 'x')`));
    await assert.rejects(as(null, `select public.effacer_mes_donnees()`));
  });

  it("« Effacer toutes mes données » vide tout pour A et rien pour B", async () => {
    await as(A, `select public.effacer_mes_donnees()`);
    for (const table of ["messages", "user_facts", "summaries"]) {
      assert.equal(await count(A, table), 0, `${table} de A`);
      assert.ok((await count(B, table)) > 0, `${table} de B`);
    }
  });

  it("supprime les données avec le compte", async () => {
    await db.exec(`delete from auth.users where id = '${B}'`);
    assert.equal((await db.query<{ n: number }>(`select count(*)::int as n from public.messages`)).rows[0].n, 0);
  });
});
