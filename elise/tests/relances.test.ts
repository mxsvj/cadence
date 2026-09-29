// Prendre des nouvelles après une absence, côté base : qui est concerné,
// un seul message par absence, le refus de la personne, et qui peut appeler
// quoi.
import assert from "node:assert/strict";
import { before, describe, it } from "node:test";
import { freshDatabase } from "./db";

const ADMIN = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
const KARIM = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb";
const LEA = "cccccccc-cccc-cccc-cccc-cccccccccccc";
const SAM = "dddddddd-dddd-dddd-dddd-dddddddddddd";
const NINA = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee";

let base: Awaited<ReturnType<typeof freshDatabase>>;

async function message(user: string, role: "user" | "assistant", hoursAgo: number, kind = "text", creator = 1) {
  await base.db.query(
    `insert into public.messages (user_id, creator_id, role, author, kind, content, created_at)
     values ($1, $6, $2, $3, $4, 'Bonjour', now() - make_interval(hours => $5))`,
    [user, role, role === "user" ? "user" : "ai", kind, hoursAgo, creator],
  );
}
const due = async (hours = 48) =>
  (await base.as<{ user_id: string }>("service", "select user_id from public.a_relancer($1, 50)", [hours])).map((r) => r.user_id).sort();

before(async () => {
  base = await freshDatabase(
    [ADMIN, KARIM, LEA, SAM, NINA].map((id, i) => ({ id, email: `p${i}@example.com` })),
  );
  await base.db.query("insert into public.admins (user_id) values ($1)", [ADMIN]);
  for (const [id, name] of [[ADMIN, "Équipe"], [KARIM, "Karim"], [LEA, "Léa"], [SAM, "Sam"], [NINA, "Nina"]]) {
    await base.db.query("insert into public.profiles (user_id, display_name, birthdate) values ($1, $2, '1980-01-01')", [id, name]);
  }
  await message(ADMIN, "user", 100); // l'équipe qui teste : jamais relancée
  await message(KARIM, "user", 60);
  await message(KARIM, "assistant", 59); // absent depuis 59 h
  await message(LEA, "user", 10); // revenue il y a 10 h
  await message(SAM, "assistant", 80); // n'a jamais écrit : seulement le message d'accueil
  await message(NINA, "user", 70);
});

describe("prendre des nouvelles", () => {
  it("concerne les personnes absentes depuis le délai, qui ont déjà écrit", async () => {
    assert.deepEqual(await due(48), [KARIM, NINA]);
    assert.deepEqual(await due(65), [NINA]);
  });

  it("une visite sans écrire compte comme un retour", async () => {
    await base.as(NINA, "select public.marquer_visite()");
    assert.deepEqual(await due(48), [KARIM]);
  });

  it("un seul message par absence : après la prise de nouvelles, plus rien tant qu'elle ne revient pas", async () => {
    await message(KARIM, "assistant", 0, "relance");
    assert.deepEqual(await due(1), [LEA]);
  });

  it("jamais sous une offre qui attend sa réponse", async () => {
    await base.db.query(
      "insert into public.offers (user_id, creator_id, content_type, price_cents, status, proposed_by) values ($1, 1, 'image', 500, 'proposee', 'ai')",
      [LEA],
    );
    assert.deepEqual(await due(1), []);
  });

  it("la personne peut refuser ces messages, et seulement pour elle-même", async () => {
    await base.db.query("update public.offers set status = 'retiree' where user_id = $1", [LEA]);
    assert.deepEqual(await due(1), [LEA]);
    await base.as(LEA, "select public.regler_relances(false)");
    assert.deepEqual(await due(1), []);
    const rows = await base.as<{ user_id: string; relances_ok: boolean }>(ADMIN, "select user_id, relances_ok from public.profiles order by display_name");
    assert.equal(rows.find((r) => r.user_id === LEA)?.relances_ok, false);
    assert.equal(rows.find((r) => r.user_id === KARIM)?.relances_ok, true);
    await base.as(LEA, "select public.regler_relances(true)");
    assert.deepEqual(await due(1), [LEA]);
  });

  it("seulement si l'IA a le droit d'écrire : pas en mode manuel, et en hybride si la personne est cochée", async () => {
    await base.as(ADMIN, "update public.ai_settings set mode = 'hybride' where id = 1");
    await base.as(ADMIN, "insert into public.creator_contacts (creator_id, user_id, ai_enabled) values (1, $1, false)", [LEA]);
    assert.deepEqual(await due(1), []);
    await base.as(ADMIN, "update public.creator_contacts set ai_enabled = true where user_id = $1", [LEA]);
    assert.deepEqual(await due(1), [LEA]);
    await base.as(ADMIN, "update public.ai_settings set mode = 'manuel' where id = 1");
    assert.deepEqual(await due(1), []);
    await base.as(ADMIN, "update public.ai_settings set mode = 'auto' where id = 1");
    assert.deepEqual(await due(1), [LEA]);
  });

  it("une seule par personne : sa dernière conversation, avec une créatrice en ligne", async () => {
    const [{ id: kath }] = await base.as<{ id: number }>(
      ADMIN,
      "insert into public.creators (persona, active) values ('{\"nom\": \"Katherine\"}', true) returning id",
    );
    await message(LEA, "user", 5, "text", kath); // Léa a parlé ensuite à Katherine
    const rows = await base.as<{ user_id: string; creator_id: number }>("service", "select * from public.a_relancer(1, 50)");
    assert.deepEqual(rows.map((r) => [r.user_id, Number(r.creator_id)]), [[LEA, Number(kath)]]);
    await base.as(ADMIN, "update public.creators set active = false where id = $1", [kath]);
    assert.deepEqual(await due(1), []); // Katherine n'est plus en ligne : pas de message
    await base.as(ADMIN, "update public.creators set active = true where id = $1", [kath]);
  });

  it("la liste n'est lisible que par le serveur", async () => {
    await assert.rejects(base.as(ADMIN, "select * from public.a_relancer(0, 50)"), /permission denied/);
    await assert.rejects(base.as(KARIM, "select * from public.a_relancer(0, 50)"), /permission denied/);
    await assert.rejects(base.as(null, "select public.regler_relances(false)"), /permission denied/);
  });

  it("une personne ne peut pas écrire elle-même un message « relance »", async () => {
    await assert.rejects(
      base.as(KARIM, "insert into public.messages (user_id, creator_id, role, author, kind, content) values ($1, 1, 'user', 'user', 'relance', 'x')", [KARIM]),
      /row-level security/,
    );
  });

  it("le délai réglé par l'équipe reste entre 24 h et 14 jours", async () => {
    await assert.rejects(base.as(ADMIN, "update public.ai_settings set relance_heures = 2 where id = 1"), /check constraint/);
    await base.as(ADMIN, "update public.ai_settings set relance_heures = 72, relance_active = true where id = 1");
  });
});
