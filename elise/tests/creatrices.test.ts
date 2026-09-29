// Les créatrices, côté base : réservées à l'équipe, une seule active, des
// réglages propres à chacune avec chaque personne, et la reprise du
// personnage réglé avant leur arrivée.
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
  it("devient une créatrice active, avec ses réglages par personne, une seule fois", async () => {
    await base.db.query(
      "update public.ai_settings set persona = $1::jsonb, first_message = 'Coucou, c''est {nom} !' where id = 1",
      [JSON.stringify({ nom: "Chloé", age: 29 })],
    );
    await base.db.query("insert into public.contacts (user_id, ai_enabled, emojis) values ($1, false, '🌸')", [KARIM]);
    await base.db.exec(schemaSql);
    await base.db.exec(schemaSql);

    const creators = await base.as<{ id: number; persona: { nom: string }; first_message: string }>(
      ADMIN,
      "select id, persona, first_message from public.creators",
    );
    assert.equal(creators.length, 1);
    assert.equal(creators[0].persona.nom, "Chloé");
    assert.equal(creators[0].first_message, "Coucou, c'est {nom} !");
    const [settings] = await base.as<{ creator_id: number }>(ADMIN, "select creator_id from public.ai_settings");
    assert.equal(Number(settings.creator_id), Number(creators[0].id));
    const rows = await base.as<{ user_id: string; ai_enabled: boolean; emojis: string }>(
      ADMIN,
      "select user_id, ai_enabled, emojis from public.creator_contacts",
    );
    assert.deepEqual(rows, [{ user_id: KARIM, ai_enabled: false, emojis: "🌸" }]);
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

  it("la messagerie montre « IA coupée » selon la créatrice active", async () => {
    await base.db.query(
      "insert into public.messages (user_id, role, author, kind, content) values ($1, 'user', 'user', 'text', 'Bonjour')",
      [KARIM],
    );
    const boite = async () =>
      (await one<{ user_id: string; ia_autorisee: boolean }[]>(ADMIN, "select public.admin_boite() as r")).find(
        (p) => p.user_id === KARIM,
      )!.ia_autorisee;
    assert.equal(await boite(), false); // la première : IA coupée avec Karim
    await base.as(ADMIN, "update public.ai_settings set creator_id = $1 where id = 1", [second]);
    assert.equal(await boite(), true); // la seconde lui répond
  });

  it("supprimer la créatrice active laisse l'IA sans créatrice, et ses réglages partent avec elle", async () => {
    await base.as(ADMIN, "delete from public.creators where id = $1", [second]);
    const [settings] = await base.as<{ creator_id: number | null }>(ADMIN, "select creator_id from public.ai_settings");
    assert.equal(settings.creator_id, null);
    const rows = await base.as(ADMIN, "select * from public.creator_contacts where creator_id = $1", [second]);
    assert.deepEqual(rows, []);
  });

  it("« Tout effacer » retire aussi les emojis choisis pour la personne", async () => {
    await base.as(KARIM, "select public.effacer_mes_donnees()");
    const rows = await base.as<{ emojis: string }>(ADMIN, "select emojis from public.creator_contacts where user_id = $1", [KARIM]);
    assert.ok(rows.every((r) => r.emojis === ""));
  });
});
