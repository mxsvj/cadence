// Le tableau de bord des gains, côté base : accès réservé aux
// administrateurs, calculs justes, données de démonstration.
import assert from "node:assert/strict";
import { before, describe, it } from "node:test";
import { freshDatabase } from "./db";

const ADMIN = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
const KARIM = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb";
const LEA = "cccccccc-cccc-cccc-cccc-cccccccccccc";

type Dashboard = {
  debut: string;
  fin: string;
  jours: number;
  pas: "jour" | "semaine" | "mois";
  net: boolean;
  createurs: { id: number; nom: string }[];
  demo: boolean;
  totaux: {
    depuis_le_debut: number;
    periode: number;
    periode_precedente: number | null;
    pourboires: { nombre: number; cents: number };
    messages: { nombre: number; achats: number; cents: number };
    abonnements: { actifs: number; nombre: number; cents: number };
  };
  serie: { jour: string; total: number; pourboires: number; messages: number; abonnements: number }[];
  derniers: { id: number; client: string; nom: string; type: string; quantite: number; cents: number; createur: string | null }[];
  ltv: { clients: number; moyenne_cents: number } & Record<string, number>;
  repartition: { min_cents: number; max_cents: number | null; clients: number }[];
  clients: {
    client: string;
    nom: string;
    pourboires_cents: number;
    messages_nombre: number;
    abonne: boolean;
    total_cents: number;
  }[];
};

let db: Awaited<ReturnType<typeof freshDatabase>>["db"];
let as: Awaited<ReturnType<typeof freshDatabase>>["as"];

type Options = { jours?: number | null; debut?: string; fin?: string; creator?: number | null; net?: boolean };

/** jours : les N derniers jours ; jours: null sans debut = depuis le début. */
async function dashboard(user: string, o: Options = {}): Promise<Dashboard> {
  const jours = o.jours === undefined ? 30 : o.jours;
  const [row] = await as<{ d: Dashboard }>(
    user,
    `select public.admin_dashboard(
       case when $1::integer is null then $2::date else (now() at time zone 'Europe/Paris')::date - ($1::integer - 1) end,
       $3::date, $4::bigint, $5::boolean) as d`,
    [o.debut ? null : jours, o.debut ?? null, o.fin ?? null, o.creator ?? null, o.net ?? false],
  );
  return row.d;
}

// Un achat « réel », comme l'écrira plus tard le service de paiement.
async function achat(user: string, kind: string, cents: number, joursAvant: number, quantity = 1) {
  await db.query(
    `insert into public.purchases (user_id, kind, quantity, amount_cents, created_at)
     values ($1, $2, $3, $4, now() - make_interval(days => $5))`,
    [user, kind, quantity, cents, joursAvant],
  );
}

before(async () => {
  ({ db, as } = await freshDatabase([
    { id: ADMIN, email: "admin@example.com" },
    { id: KARIM, email: "karim@example.com" },
    { id: LEA, email: "lea@example.com" },
  ]));
  await db.query("insert into public.admins (user_id) values ($1)", [ADMIN]);

  await achat(KARIM, "tip", 500, 0);
  await achat(KARIM, "message", 349, 1, 10);
  await achat(KARIM, "abonnement", 999, 3);
  await achat(LEA, "tip", 200, 2);
  await achat(LEA, "abonnement", 999, 45); // abonnement ancien : plus actif
  await achat(LEA, "message", 199, 40, 5); // hors des 30 derniers jours
});

describe("tableau de bord : qui y a accès", () => {
  it("is_admin distingue l'administrateur des autres", async () => {
    assert.equal((await as<{ a: boolean }>(ADMIN, "select public.is_admin() as a"))[0].a, true);
    assert.equal((await as<{ a: boolean }>(KARIM, "select public.is_admin() as a"))[0].a, false);
  });

  it("refuse les chiffres et la démo à quelqu'un qui n'est pas administrateur", async () => {
    await assert.rejects(as(KARIM, "select public.admin_dashboard()"), /Réservé aux administrateurs/);
    await assert.rejects(as(KARIM, "select public.admin_simuler_achat()"), /Réservé aux administrateurs/);
    await assert.rejects(as(KARIM, "select public.admin_remplir_demo()"), /Réservé aux administrateurs/);
    await assert.rejects(as(KARIM, "select public.admin_vider_demo()"), /Réservé aux administrateurs/);
    await assert.rejects(as(null, "select public.admin_dashboard()"));
  });

  it("chacun ne voit que ses propres achats, et personne ne peut en créer ni se nommer administrateur", async () => {
    const mine = await as<{ amount_cents: number }>(LEA, "select amount_cents from public.purchases order by id");
    assert.deepEqual(mine.map((r) => r.amount_cents), [200, 999, 199]);
    await assert.rejects(as(KARIM, "insert into public.purchases (kind, amount_cents) values ('tip', 100)"));
    await assert.rejects(as(KARIM, `insert into public.admins (user_id) values ('${KARIM}')`));
    await assert.rejects(as(KARIM, "select public.achat_de_demo(now())"));
  });

  it("« Effacer toutes mes données » ne touche pas aux achats", async () => {
    await as(KARIM, "select public.effacer_mes_donnees()");
    assert.equal((await as(KARIM, "select id from public.purchases")).length, 3);
  });
});

describe("tableau de bord : les chiffres", () => {
  it("additionne les gains de la période et depuis le début", async () => {
    const d = await dashboard(ADMIN);
    assert.equal(d.jours, 30);
    assert.equal(d.totaux.depuis_le_debut, 500 + 349 + 999 + 200 + 999 + 199);
    assert.equal(d.totaux.periode, 500 + 349 + 999 + 200);
    assert.equal(d.totaux.periode_precedente, 999 + 199);
    assert.deepEqual(d.totaux.pourboires, { nombre: 2, cents: 700 });
    assert.deepEqual(d.totaux.messages, { nombre: 10, achats: 1, cents: 349 });
    assert.deepEqual(d.totaux.abonnements, { actifs: 1, nombre: 1, cents: 999 });
    assert.equal(d.demo, false);
  });

  it("donne un point par jour, aujourd'hui compris, et les bons totaux", async () => {
    const d = await dashboard(ADMIN, { jours: 7 });
    assert.equal(d.pas, "jour");
    assert.equal(d.serie.length, 7);
    assert.equal(d.serie.reduce((s, p) => s + p.total, 0), 500 + 349 + 999 + 200);
    const today = d.serie[6];
    assert.equal(today.pourboires, 500);
    assert.equal(today.total, 500);
    for (const p of d.serie) assert.equal(p.total, p.pourboires + p.messages + p.abonnements);
  });

  it("liste les derniers achats, du plus récent au plus ancien", async () => {
    const d = await dashboard(ADMIN);
    assert.deepEqual(d.derniers.map((a) => a.cents), [500, 349, 200, 999, 199, 999]);
    assert.equal(d.derniers[0].nom, "karim@example.com");
    assert.equal(d.derniers[0].type, "tip");
  });

  it("récapitule chaque client", async () => {
    const d = await dashboard(ADMIN);
    const karim = d.clients.find((c) => c.nom === "karim@example.com")!;
    const lea = d.clients.find((c) => c.nom === "lea@example.com")!;
    assert.equal(d.clients[0].nom, "karim@example.com"); // le plus gros total d'abord
    assert.deepEqual(
      [karim.pourboires_cents, karim.messages_nombre, karim.abonne, karim.total_cents],
      [500, 10, true, 1848],
    );
    assert.deepEqual([lea.pourboires_cents, lea.messages_nombre, lea.abonne, lea.total_cents], [200, 5, false, 1398]);
  });

  it("aujourd'hui, hier, et des dates précises", async () => {
    const today = await dashboard(ADMIN, { jours: 1 });
    assert.equal(today.totaux.periode, 500);
    assert.equal(today.totaux.periode_precedente, 349); // hier
    const [{ hier }] = await as<{ hier: string }>(ADMIN, "select ((now() at time zone 'Europe/Paris')::date - 1)::text as hier");
    const yesterday = await dashboard(ADMIN, { debut: hier, fin: hier });
    assert.deepEqual([yesterday.debut, yesterday.fin, yesterday.jours], [hier, hier, 1]);
    assert.equal(yesterday.totaux.periode, 349);
    assert.equal(yesterday.serie.length, 1);
  });

  it("depuis le début : à partir du premier achat, sans période à comparer", async () => {
    const d = await dashboard(ADMIN, { jours: null });
    assert.equal(d.totaux.periode, d.totaux.depuis_le_debut);
    assert.equal(d.totaux.periode_precedente, null);
    assert.equal(d.jours, 46); // le premier achat date d'il y a 45 jours
  });

  it("sur plus de 3 mois, un point par semaine ; au-delà de 2 ans, par mois", async () => {
    const six = await dashboard(ADMIN, { jours: 183 });
    assert.equal(six.pas, "semaine");
    assert.ok(six.serie.length >= 26 && six.serie.length <= 28, String(six.serie.length));
    assert.equal(six.serie.reduce((t, p) => t + p.total, 0), six.totaux.periode);
    const trois = await dashboard(ADMIN, { jours: 1100 });
    assert.equal(trois.pas, "mois");
  });

  it("net : chaque achat moins les frais de paiement estimés (1,5 % + 0,25 €)", async () => {
    const brut = await dashboard(ADMIN, { jours: 7 });
    const net = await dashboard(ADMIN, { jours: 7, net: true });
    assert.equal(net.net, true);
    // 500 → 467 (0,075 € arrondis à 8 centimes + 25) ; 349 → 319 ; 999 → 959 ; 200 → 172
    assert.equal(net.totaux.periode, 467 + 319 + 959 + 172);
    assert.ok(net.totaux.periode < brut.totaux.periode);
    assert.ok(net.ltv.moyenne_cents < brut.ltv.moyenne_cents);
  });

  it("une créatrice à la fois ; la liste des créatrices est fournie", async () => {
    const [{ id: kath }] = await as<{ id: number }>(ADMIN, "insert into public.creators (persona) values ('{\"nom\": \"Katherine\"}') returning id");
    await db.query("update public.purchases set creator_id = $1 where kind = 'tip'", [kath]);
    await db.query("update public.purchases set creator_id = 1 where kind <> 'tip'");
    const d = await dashboard(ADMIN, { creator: kath, jours: 90 });
    assert.deepEqual(d.createurs.map((c) => c.nom), ["Élise", "Katherine"]);
    assert.equal(d.totaux.depuis_le_debut, 700);
    assert.deepEqual(d.totaux.pourboires, { nombre: 2, cents: 700 });
    assert.equal(d.totaux.abonnements.actifs, 0);
    assert.ok(d.derniers.every((a) => a.type === "tip" && a.createur === "Katherine"));
    const elise = await dashboard(ADMIN, { creator: 1, jours: 90 });
    assert.equal(elise.totaux.depuis_le_debut, 349 + 999 + 999 + 199);
  });

  it("la LTV, et combien de clients dans chaque tranche", async () => {
    const d = await dashboard(ADMIN);
    assert.equal(d.ltv.clients, 2);
    assert.equal("inscrits" in d.ltv, false);
    assert.equal("payants" in d.ltv, false);
    // Karim : 18,48 € ; Léa : 13,98 € → tous les deux entre 10 et 25 €.
    assert.deepEqual(
      d.repartition.map((t) => [t.min_cents, t.max_cents, t.clients]),
      [[0, 1000, 0], [1000, 2500, 2], [2500, 5000, 0], [5000, 10000, 0], [10000, null, 0]],
    );
  });
});

describe("tableau de bord : la démonstration", () => {
  it("simule un achat, remplit un historique, puis efface la démo sans toucher au réel", async () => {
    const [{ a }] = await as<{ a: { is_demo: boolean; kind: string; amount_cents: number } }>(
      ADMIN,
      "select public.admin_simuler_achat() as a",
    );
    assert.equal(a.is_demo, true);
    assert.ok(["tip", "message", "abonnement", "contenu"].includes(a.kind));
    assert.ok(a.amount_cents > 0);

    const [{ n }] = await as<{ n: number }>(ADMIN, "select public.admin_remplir_demo(30) as n");
    assert.ok(n > 30);
    const d = await dashboard(ADMIN);
    assert.equal(d.demo, true);
    assert.ok(d.clients.some((c) => c.client.startsWith("demo:")));
    assert.ok(d.serie.filter((p) => p.total > 0).length > 20);

    const [{ n: removed }] = await as<{ n: number }>(ADMIN, "select public.admin_vider_demo() as n");
    assert.equal(removed, n + 1);
    const after = await dashboard(ADMIN);
    assert.equal(after.demo, false);
    assert.equal(after.totaux.depuis_le_debut, 500 + 349 + 999 + 200 + 999 + 199);
  });
});
