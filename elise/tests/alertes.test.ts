// Les alertes de l'équipe, côté base : contre-offre, urgence, « prendre la main », et qui peut lire ou traiter quoi.
import assert from "node:assert/strict";
import { before, describe, it } from "node:test";
import { freshDatabase, schemaSql } from "./db";

const ADMIN = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
const KARIM = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb";
const LEA = "cccccccc-cccc-cccc-cccc-cccccccccccc";

let base: Awaited<ReturnType<typeof freshDatabase>>;
let steps: number[] = [];

type Alert = { id: number; kind: string; user_id: string; creator_id: number; offer_id: number | null; detail: Record<string, unknown> };

const one = async <T>(user: string | null, sql: string, params: unknown[] = []) =>
  (await base.as<{ r: T }>(user, sql, params))[0].r;
const open = async (user = KARIM) =>
  base.as<Alert>("service", "select * from public.team_alerts where user_id = $1 and handled_at is null order by id", [user]);
async function propose(user: string, step: number) {
  return (
    await one<{ offre: { id: number } }>("service", "select public.proposer_etape($1, 1, $2, null, 'Regarde', 'ai', null) as r", [user, step])
  ).offre.id;
}

before(async () => {
  base = await freshDatabase([
    { id: ADMIN, email: "admin@example.com" },
    { id: KARIM, email: "karim@example.com" },
    { id: LEA, email: "lea@example.com" },
  ]);
  await base.db.query("insert into public.admins (user_id) values ($1)", [ADMIN]);
  for (const [id, name] of [[KARIM, "Karim"], [LEA, "Léa"]]) {
    await base.db.query("insert into public.profiles (user_id, display_name, birthdate) values ($1, $2, '1980-01-01')", [id, name]);
    await base.db.query(
      "insert into public.messages (user_id, creator_id, role, author, content) values ($1, 1, 'user', 'user', 'Bonjour')",
      [id],
    );
  }
  const [{ id: script }] = await base.as<{ id: number }>(ADMIN, "insert into public.scripts (name) values ('Principal') returning id");
  const rows = await base.as<{ id: number }>(
    ADMIN,
    `insert into public.script_steps
       (script_id, position, title, content_type, content_text, ai_description, is_paid, price_cents, min_price_cents, max_price_cents)
     values
       ($1, 1, 'Carnet', 'texte', 'Page 1.', 'Un carnet', true, 800, 500, 1200),
       ($1, 2, 'Suite', 'texte', 'Page 2.', 'La suite', true, 1000, 600, 1500)
     returning id`,
    [script],
  );
  steps = rows.map((r) => r.id);
});

describe("alertes : contre-offres", () => {
  it("chaque contre-offre prévient l'équipe, dans une seule alerte par offre", async () => {
    const offer = await propose(KARIM, steps[0]);
    await base.as(KARIM, "select public.faire_une_offre($1, 300)", [offer]);
    let alerts = await open();
    assert.equal(alerts.length, 1);
    assert.equal(alerts[0].kind, "contre_offre");
    assert.equal(Number(alerts[0].offer_id), offer);
    assert.deepEqual(alerts[0].detail, { montant_cents: 300, prix_cents: 800, statut: "refusee", essais_restants: 2 });

    // Une deuxième proposition met à jour la même alerte, et la renvoie sur Discord/Telegram.
    await base.db.query("update public.team_alerts set notified_at = now()");
    await base.as(KARIM, "select public.faire_une_offre($1, 600)", [offer]);
    alerts = await open();
    assert.equal(alerts.length, 1);
    assert.equal(alerts[0].detail.statut, "acceptee");
    assert.equal(alerts[0].detail.montant_cents, 600);
    const [{ notified_at }] = await base.db.query<{ notified_at: string | null }>("select notified_at from public.team_alerts").then((r) => r.rows);
    assert.equal(notified_at, null);
  });

  it("une contre-offre refusée par la base ne crée rien", async () => {
    const before = (await open()).length;
    await assert.rejects(base.as(LEA, "select public.faire_une_offre($1, 900)", [(await open())[0].offer_id]), /introuvable/);
    assert.equal((await open()).length, before);
  });
});

describe("alertes : achats sans plafond", () => {
  it("un achat ne crée aucune alerte, et il n'y a plus d'alerte « plafond »", async () => {
    const [pending] = await open();
    await base.as(KARIM, "select public.acheter_offre($1)", [pending.offer_id]); // 6 €
    const offer = await propose(KARIM, steps[1]); // 10 €, au prix habituel
    await base.as(KARIM, "select public.acheter_offre($1)", [offer]);
    const [{ total }] = await base.as<{ total: number }>("service", "select sum(amount_cents)::integer as total from public.purchases where user_id = $1", [KARIM]);
    assert.equal(total, 1600);
    assert.deepEqual((await open()).map((a) => a.kind), ["contre_offre"]);
    await assert.rejects(
      base.as("service", "select public.alerter_equipe($1, 1, 'plafond', null, '{}')", [KARIM]),
      /check constraint/,
    );
  });
});

describe("alertes : urgences", () => {
  it("le serveur crée une urgence, une seule à la fois par conversation", async () => {
    const id = await one<number>("service", `select public.alerter_equipe($1, 1, 'urgence', null, '{"raison": "humain"}') as r`, [LEA]);
    assert.ok(id);
    assert.equal(await one("service", `select public.alerter_equipe($1, 1, 'urgence', null, '{"raison": "attention"}') as r`, [LEA]), null);
    assert.equal((await open(LEA)).length, 1);
  });

  it("une personne ne peut ni créer, ni lire, ni traiter une alerte", async () => {
    await assert.rejects(base.as(LEA, "select public.alerter_equipe($1, 1, 'urgence', null, '{}')", [LEA]), /permission denied/);
    await assert.rejects(base.as(LEA, "select public.alertes_a_envoyer(10)"), /permission denied/);
    await assert.rejects(base.as(LEA, "select public.admin_alertes()"), /Réservé/);
    await assert.rejects(base.as(LEA, "select public.admin_traiter_alertes($1, 1)", [LEA]), /Réservé/);
    await assert.rejects(base.as(LEA, "select public.admin_prendre_la_main($1, 1, true)", [LEA]), /Réservé/);
    assert.deepEqual(await base.as(LEA, "select * from public.team_alerts"), []);
    await assert.rejects(base.as(ADMIN, "select public.alerter_equipe($1, 1, 'urgence', null, '{}')", [LEA]), /permission denied/);
  });

  it("l'équipe voit les alertes à traiter, avec le prénom et la créatrice", async () => {
    const list = await one<{ kind: string; nom: string; creatrice: string }[]>(ADMIN, "select public.admin_alertes() as r");
    assert.deepEqual(
      list.map((a) => [a.kind, a.nom, a.creatrice]),
      [["urgence", "Léa", "Élise"], ["contre_offre", "Karim", "Élise"]],
    );
    const inbox = await one<{ nom: string; alertes: string[]; manuel: boolean }[]>(ADMIN, "select public.admin_boite() as r");
    assert.deepEqual(inbox.find((c) => c.nom === "Léa")?.alertes, ["urgence"]);
    assert.equal(inbox.find((c) => c.nom === "Léa")?.manuel, false);
  });

  it("chaque alerte n'est envoyée qu'une fois", async () => {
    const first = await one<{ kind: string; creatrice: string }[]>("service", "select public.alertes_a_envoyer(10) as r");
    assert.deepEqual(first.map((a) => a.kind).sort(), ["contre_offre", "urgence"]);
    assert.equal(first[0].creatrice, "Élise");
    assert.deepEqual(await one("service", "select public.alertes_a_envoyer(10) as r"), []);
  });
});

describe("prendre la main", () => {
  it("coupe l'IA dans cette conversation et bloque la prise de nouvelles", async () => {
    await base.db.query("update public.messages set created_at = now() - interval '3 days'");
    await base.as(ADMIN, "select public.admin_traiter_alertes($1, 1)", [LEA]);
    await base.as(ADMIN, "select public.admin_traiter_alertes($1, 1)", [KARIM]);
    const due = async () => (await base.as<{ user_id: string }>("service", "select user_id from public.a_relancer(48, 50)")).map((r) => r.user_id).sort();
    assert.deepEqual(await due(), [KARIM, LEA]);

    await base.as(ADMIN, "select public.admin_prendre_la_main($1, 1, true)", [LEA]);
    const [{ manual }] = await base.as<{ manual: boolean }>(ADMIN, "select manual from public.creator_contacts where user_id = $1", [LEA]);
    assert.equal(manual, true);
    assert.deepEqual(await due(), [KARIM]);
    const inbox = await one<{ nom: string; manuel: boolean }[]>(ADMIN, "select public.admin_boite() as r");
    assert.equal(inbox.find((c) => c.nom === "Léa")?.manuel, true);

    await base.as(ADMIN, "select public.admin_prendre_la_main($1, 1, false)", [LEA]);
    assert.deepEqual(await due(), [KARIM, LEA]);
  });

  it("une urgence à traiter bloque aussi la prise de nouvelles", async () => {
    await base.as("service", `select public.alerter_equipe($1, 1, 'urgence', null, '{"raison": "attention"}')`, [KARIM]);
    const due = (await base.as<{ user_id: string }>("service", "select user_id from public.a_relancer(48, 50)")).map((r) => r.user_id);
    assert.deepEqual(due, [LEA]);
  });

  it("« Effacer toutes mes données » efface aussi ses alertes", async () => {
    await base.as(KARIM, "select public.effacer_mes_donnees()");
    assert.deepEqual(await open(KARIM), []);
  });
});

describe("mise à jour d'une base qui avait le plafond de dépenses", () => {
  it("relancer schema.sql retire les colonnes, la fonction et les alertes « plafond »", async () => {
    await base.db.exec(`
      alter table public.contacts add column spending_cap_cents integer;
      alter table public.ai_settings add column spending_cap_cents integer not null default 10000;
      create function public.plafond_de(p_user uuid) returns integer language sql as $$ select 1000 $$;
      alter table public.team_alerts drop constraint team_alerts_kind_check;
      insert into public.team_alerts (user_id, creator_id, kind) values ('${LEA}', 1, 'plafond');
    `);
    await base.db.exec(schemaSql);
    const left = await base.db.query(`
      select column_name from information_schema.columns
      where table_schema = 'public' and column_name = 'spending_cap_cents'`);
    assert.deepEqual(left.rows, []);
    const fn = await base.db.query("select 1 from pg_proc where proname = 'plafond_de'");
    assert.deepEqual(fn.rows, []);
    const kinds = await base.db.query<{ kind: string }>("select distinct kind from public.team_alerts order by kind");
    assert.ok(kinds.rows.every((r) => r.kind === "contre_offre" || r.kind === "urgence"));
  });
});
