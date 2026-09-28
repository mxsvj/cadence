// Le tableau de bord des gains, côté base : accès réservé aux
// administrateurs, calculs justes, données de démonstration.
import assert from "node:assert/strict";
import { before, describe, it } from "node:test";
import { freshDatabase } from "./db";

const ADMIN = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
const KARIM = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb";
const LEA = "cccccccc-cccc-cccc-cccc-cccccccccccc";

type Dashboard = {
  jours: number;
  demo: boolean;
  totaux: {
    depuis_le_debut: number;
    periode: number;
    periode_precedente: number;
    pourboires: { nombre: number; cents: number };
    messages: { nombre: number; achats: number; cents: number };
    abonnements: { actifs: number; nombre: number; cents: number };
  };
  serie: { jour: string; total: number; pourboires: number; messages: number; abonnements: number }[];
  derniers: { id: number; client: string; nom: string; type: string; quantite: number; cents: number }[];
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

async function dashboard(user: string, client: string | null = null, jours = 30): Promise<Dashboard> {
  const [row] = await as<{ d: Dashboard }>(user, "select public.admin_dashboard($1, $2) as d", [client, jours]);
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
    const d = await dashboard(ADMIN, null, 7);
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

  it("filtre sur une personne", async () => {
    const tout = await dashboard(ADMIN);
    const lea = tout.clients.find((c) => c.nom === "lea@example.com")!;
    const d = await dashboard(ADMIN, lea.client, 90);
    assert.equal(d.totaux.depuis_le_debut, 1398);
    assert.equal(d.totaux.periode, 1398);
    assert.deepEqual(d.totaux.pourboires, { nombre: 1, cents: 200 });
    assert.equal(d.totaux.abonnements.actifs, 0);
    assert.ok(d.derniers.every((a) => a.nom === "lea@example.com"));
    assert.equal(d.clients.length, 2); // la liste des clients reste complète
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
