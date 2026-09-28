// Essaie supabase/schema.sql sur un vrai PostgreSQL (PGlite, en mémoire) :
// cloisonnement des données entre personnes, droits, effacement.
import assert from "node:assert/strict";
import { before, describe, it } from "node:test";
import { freshDatabase } from "./db";

const A = "11111111-1111-1111-1111-111111111111";
const B = "22222222-2222-2222-2222-222222222222";
let db: Awaited<ReturnType<typeof freshDatabase>>["db"];
let as: Awaited<ReturnType<typeof freshDatabase>>["as"];

const count = async (user: string, table: string) =>
  (await as<{ n: number }>(user, `select count(*)::int as n from public.${table}`))[0].n;

before(async () => {
  ({ db, as } = await freshDatabase([
    { id: A, email: "a@example.com" },
    { id: B, email: "b@example.com" },
  ]));

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
