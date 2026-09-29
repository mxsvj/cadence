// Essaie supabase/schema.sql sur un vrai PostgreSQL (PGlite, en mémoire) :
// cloisonnement des données entre personnes et entre créatrices, droits,
// effacement. La base neuve a une créatrice en ligne (n° 1, « Élise »).
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

  // Les messages de l'IA sont écrits par le serveur (clé secrète).
  await as("service", `insert into public.messages (user_id, creator_id, role, author, content) values ('${A}', 1, 'assistant', 'ai', 'Bonjour A')`);
  await as(A, `insert into public.messages (creator_id, role, content) values (1, 'user', 'Salut')`);
  await as("service", `insert into public.messages (user_id, creator_id, role, author, content) values ('${B}', 1, 'assistant', 'ai', 'Bonjour B')`);
  await as(A, `insert into public.user_facts (creator_id, fact) values (1, 'Se prénomme Karim.')`);
  await as(B, `insert into public.user_facts (creator_id, fact) values (1, 'Se prénomme Léa.')`);
  await as(A, `insert into public.summaries (creator_id, summary, last_message_id) values (1, 'Résumé A', 1)`);
  await as(B, `insert into public.summaries (creator_id, summary) values (1, 'Résumé B')`);
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
    await assert.rejects(as(A, `insert into public.messages (user_id, creator_id, role, content) values ('${B}', 1, 'user', 'intrus')`));
    await assert.rejects(as(A, `insert into public.user_facts (user_id, creator_id, fact) values ('${B}', 1, 'intrus')`));
    await assert.rejects(as(A, `update public.summaries set user_id = '${B}' where user_id = '${A}'`));
    await as(A, `update public.summaries set summary = 'piraté' where user_id = '${B}'`); // ne touche rien
    assert.equal((await as<{ summary: string }>(B, `select summary from public.summaries`))[0].summary, "Résumé B");
  });

  it("interdit d'écrire au nom de l'IA ou de l'équipe, ou de fabriquer une offre", async () => {
    await assert.rejects(as(A, `insert into public.messages (creator_id, role, author, content) values (1, 'assistant', 'ai', 'faux')`));
    await assert.rejects(as(A, `insert into public.messages (creator_id, role, author, content) values (1, 'assistant', 'team', 'faux')`));
    await assert.rejects(as(A, `insert into public.messages (creator_id, role, kind, content) values (1, 'user', 'offer', 'faux')`));
    // Et la base refuse un auteur incohérent, même venant du serveur.
    await assert.rejects(as("service", `insert into public.messages (user_id, creator_id, role, author, content) values ('${A}', 1, 'assistant', 'user', 'x')`));
  });

  it("interdit de modifier un message", async () => {
    await assert.rejects(as(A, `update public.messages set content = 'modifié'`));
  });

  it("refuse les doublons dans une fiche, majuscules comprises, mais pas d'une fiche à l'autre", async () => {
    await assert.rejects(as(A, `insert into public.user_facts (creator_id, fact) values (1, 'se prénomme karim.')`));
    await as(B, `insert into public.user_facts (creator_id, fact) values (1, 'Se prénomme Karim.')`);
  });

  it("contrôle les rôles et les messages vides", async () => {
    await assert.rejects(as(A, `insert into public.messages (creator_id, role, content) values (1, 'system', 'x')`));
    await assert.rejects(as(A, `insert into public.messages (creator_id, role, content) values (1, 'user', '')`));
    await assert.rejects(as(A, `insert into public.messages (role, content) values ('user', 'sans créatrice')`));
  });

  it("met le résumé à jour", async () => {
    await as(A, `insert into public.summaries (creator_id, summary, last_message_id) values (1, 'Résumé A2', 2)
      on conflict (user_id, creator_id) do update set summary = excluded.summary, last_message_id = excluded.last_message_id`);
    const [row] = await as<{ summary: string; last_message_id: number }>(A, `select summary, last_message_id from public.summaries`);
    assert.equal(row.summary, "Résumé A2");
    assert.equal(Number(row.last_message_id), 2);
  });

  it("ne donne rien aux visiteurs non connectés", async () => {
    await assert.rejects(as(null, `select * from public.messages`));
    await assert.rejects(as(null, `insert into public.messages (creator_id, role, content) values (1, 'user', 'x')`));
    await assert.rejects(as(null, `select public.creatrices_disponibles()`));
    await assert.rejects(as(null, `select public.effacer_mes_donnees()`));
  });

  it("une conversation par créatrice : messages, fiche et résumé ne se mélangent pas", async () => {
    await db.exec(`insert into public.creators (persona, first_message, active) values ('{"nom": "Katherine", "age": 24}', '', true)`);
    await as(A, `insert into public.messages (creator_id, role, content) values (2, 'user', 'Coucou Katherine')`);
    // Le même fait peut être connu des deux créatrices, séparément.
    await as(A, `insert into public.user_facts (creator_id, fact) values (2, 'Se prénomme Karim.')`);
    await as(A, `insert into public.summaries (creator_id, summary) values (2, 'Résumé avec Katherine')`);
    const byCreator = await as<{ creator_id: number; n: number }>(
      A,
      `select creator_id, count(*)::int as n from public.messages group by creator_id order by creator_id`,
    );
    assert.deepEqual(byCreator.map((r) => [Number(r.creator_id), r.n]), [[1, 2], [2, 1]]);
    assert.equal(await count(A, "summaries"), 2);
  });

  it("les personnes voient les créatrices en ligne (le strict nécessaire) et n'écrivent qu'à elles", async () => {
    const list = (await as<{ r: { id: number; nom: string; age: number | null }[] }>(A, `select public.creatrices_disponibles() as r`))[0].r;
    assert.deepEqual(list.map((c) => [c.id, c.nom, c.age]), [[1, "Élise", null], [2, "Katherine", 24]]);
    assert.ok(list.every((c) => !("persona" in c) && !("first_message" in c)));
    await db.exec(`update public.creators set active = false where id = 2`);
    await assert.rejects(as(A, `insert into public.messages (creator_id, role, content) values (2, 'user', 'Tu es là ?')`), /row-level security/);
    assert.deepEqual((await as<{ r: { id: number }[] }>(A, `select public.creatrices_disponibles() as r`))[0].r.map((c) => c.id), [1]);
    await db.exec(`update public.creators set active = true where id = 2`);
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
