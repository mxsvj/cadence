// Les créatrices, côté base : réservées à l'équipe, plusieurs en ligne à la
// fois, des réglages propres à chacune avec chaque personne, et la reprise
// du personnage réglé avant leur arrivée.
import assert from "node:assert/strict";
import { before, describe, it } from "node:test";
import { freshDatabase, schemaSql } from "./db";

const ADMIN = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
const KARIM = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb";
const LEA = "cccccccc-cccc-cccc-cccc-cccccccccccc";

let base: Awaited<ReturnType<typeof freshDatabase>>;
const one = async <T>(user: string | null, sql: string, params: unknown[] = []) =>
  (await base.as<{ r: T }>(user, sql, params))[0].r;

before(async () => {
  base = await freshDatabase([
    { id: ADMIN, email: "admin@example.com" },
    { id: KARIM, email: "karim@example.com" },
    { id: LEA, email: "lea@example.com" },
  ]);
  await base.db.query("insert into public.admins (user_id) values ($1)", [ADMIN]);
});

describe("le personnage réglé avant les créatrices", () => {
  it("devient une créatrice en ligne, avec ses réglages par personne, une seule fois", async () => {
    // Une base d'avant les créatrices : pas encore de créatrice du tout.
    await base.db.exec("delete from public.creators");
    await base.db.query(
      "update public.ai_settings set persona = $1::jsonb, first_message = 'Coucou, c''est {nom} !' where id = 1",
      [JSON.stringify({ nom: "Chloé", age: 29 })],
    );
    await base.db.query("insert into public.contacts (user_id, ai_enabled, emojis) values ($1, false, '🌸')", [KARIM]);
    await base.db.exec(schemaSql);
    await base.db.exec(schemaSql);

    const creators = await base.as<{ id: number; persona: { nom: string }; first_message: string; active: boolean }>(
      ADMIN,
      "select id, persona, first_message, active from public.creators",
    );
    assert.equal(creators.length, 1);
    assert.equal(creators[0].persona.nom, "Chloé");
    assert.equal(creators[0].active, true);
    assert.equal(creators[0].first_message, "Coucou, c'est {nom} !");
    const [settings] = await base.as<{ creator_id: number }>(ADMIN, "select creator_id from public.ai_settings");
    assert.equal(Number(settings.creator_id), Number(creators[0].id));
    const rows = await base.as<{ user_id: string; ai_enabled: boolean; emojis: string; emoji_mode: string }>(
      ADMIN,
      "select user_id, ai_enabled, emojis, emoji_mode from public.creator_contacts",
    );
    assert.deepEqual(rows, [{ user_id: KARIM, ai_enabled: false, emojis: "🌸", emoji_mode: "choisis" }]);
  });

  it("à l'arrivée du réglage des emojis, une liste déjà remplie devient « seulement ceux-là »", async () => {
    await base.db.exec("alter table public.creator_contacts drop column emoji_mode");
    await base.db.exec(schemaSql);
    const [row] = await base.as<{ emoji_mode: string }>(ADMIN, "select emoji_mode from public.creator_contacts where user_id = $1", [KARIM]);
    assert.equal(row.emoji_mode, "choisis");
    await assert.rejects(base.as(ADMIN, "update public.creator_contacts set emoji_mode = 'beaucoup'"), /check constraint/);
  });
});

describe("les créatrices", () => {
  let second: number;

  it("ne sont visibles et modifiables que par l'équipe", async () => {
    assert.deepEqual(await base.as(KARIM, "select * from public.creators"), []);
    assert.deepEqual(await base.as(KARIM, "select * from public.creator_contacts"), []);
    await assert.rejects(base.as(KARIM, "insert into public.creators (persona) values ('{}')"), /row-level security/);
    await assert.rejects(base.as(null, "select * from public.creators"), /permission denied/);
  });

  it("l'équipe en crée une autre, avec ses propres réglages pour chaque personne", async () => {
    [{ id: second }] = await base.as<{ id: number }>(
      ADMIN,
      "insert into public.creators (persona, first_message) values ($1::jsonb, '') returning id",
      [JSON.stringify({ nom: "Inès" })],
    );
    await base.as(ADMIN, "insert into public.creator_contacts (creator_id, user_id, ai_enabled, emojis) values ($1, $2, true, '☕')", [
      second,
      KARIM,
    ]);
    const rows = await base.as<{ creator_id: number; emojis: string }>(
      ADMIN,
      "select creator_id, emojis from public.creator_contacts where user_id = $1 order by creator_id",
      [KARIM],
    );
    assert.deepEqual(rows.map((r) => r.emojis), ["🌸", "☕"]);
  });

  it("la messagerie : une conversation par créatrice, avec « IA coupée » selon chacune", async () => {
    const [{ id: first }] = await base.as<{ id: number }>(ADMIN, "select min(id) as id from public.creators");
    await base.as(ADMIN, "update public.creators set active = true");
    await base.as(KARIM, "insert into public.messages (creator_id, role, content) values ($1, 'user', 'Bonjour Chloé')", [first]);
    await base.as(KARIM, "insert into public.messages (creator_id, role, content) values ($1, 'user', 'Bonjour Inès')", [second]);
    const inbox = await one<{ user_id: string; creator_id: number; creatrice: string; ia_autorisee: boolean; non_lus: number }[]>(
      ADMIN,
      "select public.admin_boite() as r",
    );
    const karim = inbox.filter((c) => c.user_id === KARIM).map((c) => [c.creatrice, c.ia_autorisee, c.non_lus]);
    assert.deepEqual(karim, [
      ["Inès", true, 1], // la plus récente d'abord
      ["Chloé", false, 1], // Chloé : IA coupée avec Karim
    ]);
    // Lire la conversation avec Inès ne marque pas celle avec Chloé.
    await base.as(ADMIN, "select public.admin_marquer_lu($1, $2)", [KARIM, second]);
    const after = await one<{ user_id: string; creator_id: number; non_lus: number }[]>(ADMIN, "select public.admin_boite() as r");
    assert.deepEqual(
      after.filter((c) => c.user_id === KARIM).map((c) => c.non_lus),
      [0, 1],
    );
  });

  it("supprimer une créatrice supprime ses conversations et ses réglages, pas les autres", async () => {
    await base.as(ADMIN, "delete from public.creators where id = $1", [second]);
    assert.deepEqual(await base.as(ADMIN, "select * from public.creator_contacts where creator_id = $1", [second]), []);
    const left = await base.as<{ content: string }>(KARIM, "select content from public.messages");
    assert.deepEqual(left.map((m) => m.content), ["Bonjour Chloé"]);
  });

  it("« Tout effacer » retire aussi les emojis choisis pour la personne", async () => {
    await base.as(KARIM, "select public.effacer_mes_donnees()");
    const rows = await base.as<{ emojis: string; emoji_mode: string }>(
      ADMIN,
      "select emojis, emoji_mode from public.creator_contacts where user_id = $1",
      [KARIM],
    );
    assert.ok(rows.length > 0);
    assert.ok(rows.every((r) => r.emojis === "" && r.emoji_mode === "libre"));
  });
});

describe("les scripts de chaque créatrice", () => {
  let chloe: number;
  let ines: number;
  const scripts: Record<string, number> = {};
  // Le script de la conversation de cette personne avec cette créatrice.
  const scriptOf = async (user: string, creator: number) =>
    Number((await base.db.query<{ r: number }>("select public.script_de($1, $2) as r", [user, creator])).rows[0].r);
  let sansScript: number;

  before(async () => {
    [{ id: chloe }] = await base.as<{ id: number }>(ADMIN, "select id from public.creators order by id limit 1");
    [{ id: ines }] = await base.as<{ id: number }>(ADMIN, "insert into public.creators (persona) values ('{\"nom\": \"Inès\"}') returning id");
    [{ id: sansScript }] = await base.as<{ id: number }>(ADMIN, "insert into public.creators (persona) values ('{\"nom\": \"Zoé\"}') returning id");
    for (const [name, position, creator] of [
      ["Pour toutes", 1, null],
      ["Chloé 1", 2, chloe],
      ["Chloé 2", 3, chloe],
      ["Inès 1", 4, ines],
    ] as const) {
      const [{ id }] = await base.as<{ id: number }>(
        ADMIN,
        "insert into public.scripts (name, position, creator_id) values ($1, $2, $3) returning id",
        [name, position, creator],
      );
      scripts[name] = Number(id);
    }
  });

  it("sans script dans la fiche : le premier de la créatrice de la conversation, sinon le premier pour toutes", async () => {
    assert.equal(await scriptOf(LEA, chloe), scripts["Chloé 1"]);
    assert.equal(await scriptOf(LEA, ines), scripts["Inès 1"]);
    assert.equal(await scriptOf(LEA, sansScript), scripts["Pour toutes"]);
  });

  it("le script de la fiche ne sert qu'avec sa créatrice (ou s'il sert à toutes)", async () => {
    await base.as(ADMIN, "insert into public.contacts (user_id, script_id) values ($1, $2)", [LEA, scripts["Chloé 2"]]);
    assert.equal(await scriptOf(LEA, chloe), scripts["Chloé 2"]);
    assert.equal(await scriptOf(LEA, ines), scripts["Inès 1"]);
    await base.as(ADMIN, "update public.contacts set script_id = $2 where user_id = $1", [LEA, scripts["Pour toutes"]]);
    assert.equal(await scriptOf(LEA, ines), scripts["Pour toutes"]);
  });

  it("supprimer une créatrice laisse ses scripts à toutes", async () => {
    await base.as(ADMIN, "delete from public.creators where id = $1", [ines]);
    const [row] = await base.as<{ creator_id: number | null }>(ADMIN, "select creator_id from public.scripts where id = $1", [scripts["Inès 1"]]);
    assert.equal(row.creator_id, null);
  });
});
