// Le personnage, la messagerie de l'équipe et la vente de contenus, côté
// base : âge minimum, secret des prix, ordre de vente, contre-offres,
// plafond, contenu verrouillé.
import assert from "node:assert/strict";
import { before, describe, it } from "node:test";
import { freshDatabase, schemaSql } from "./db";

const ADMIN = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
const KARIM = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb";
const LEA = "cccccccc-cccc-cccc-cccc-cccccccccccc";

let db: Awaited<ReturnType<typeof freshDatabase>>["db"];
let as: Awaited<ReturnType<typeof freshDatabase>>["as"];
let steps: number[] = [];

type Offer = { id: number; status: string; price_cents: number; personalized: boolean };
const one = async <T>(user: string | null, sql: string, params: unknown[] = []) =>
  (await as<{ r: T }>(user, sql, params))[0].r;

async function propose(by: "service" | typeof ADMIN, user: string, step: number, price: number | null, message = "Regarde") {
  const fn = by === "service" ? "public.proposer_etape($1, $2, $3, $4, 'ai', null)" : "public.admin_proposer($1, $2, $3, $4)";
  return one<{ offre: Offer; message_id: number }>(by, `select ${fn} as r`, [user, step, price, message]);
}

before(async () => {
  ({ db, as } = await freshDatabase([
    { id: ADMIN, email: "admin@example.com" },
    { id: KARIM, email: "karim@example.com" },
    { id: LEA, email: "lea@example.com" },
  ]));
  await db.query("insert into public.admins (user_id) values ($1)", [ADMIN]);

  // Un script de trois étapes, créé par l'équipe.
  const [{ id: script }] = await as<{ id: number }>(ADMIN, "insert into public.scripts (name) values ('Principal') returning id");
  const rows = await as<{ id: number }>(
    ADMIN,
    `insert into public.script_steps
       (script_id, position, title, content_type, content_text, ai_description, is_paid, price_cents, min_price_cents, max_price_cents)
     values
       ($1, 1, 'Bienvenue', 'texte', 'Un poème de bienvenue.', 'Un court poème', false, 0, 0, 0),
       ($1, 2, 'Premier carnet', 'texte', 'Le carnet de voyage, page 1.', 'Un carnet de voyage illustré', true, 800, 500, 1200),
       ($1, 3, 'Deuxième carnet', 'texte', 'La suite du carnet.', 'La suite', true, 1500, 1000, 2000)
     returning id`,
    [script],
  );
  steps = rows.map((r) => r.id);
});

describe("profil : 18 ans minimum", () => {
  it("refuse une personne mineure", async () => {
    const seventeen = new Date();
    seventeen.setFullYear(seventeen.getFullYear() - 17);
    await assert.rejects(
      as(LEA, "select public.enregistrer_profil('Léa', $1)", [seventeen.toISOString().slice(0, 10)]),
      /réservée aux personnes majeures/,
    );
  });

  it("accepte une personne majeure, et la date de naissance ne change plus", async () => {
    await as(LEA, "select public.enregistrer_profil('Léa', '1984-05-12')");
    await as(LEA, "select public.enregistrer_profil('Léa B.', '2015-01-01')").catch(() => {});
    await as(LEA, "select public.enregistrer_profil('Léa B.', '1990-01-01')");
    const [p] = await as<{ display_name: string; birthdate: Date }>(LEA, "select display_name, birthdate from public.profiles");
    assert.equal(p.display_name, "Léa B.");
    assert.equal(new Date(p.birthdate).getFullYear(), 1984);
  });

  it("un profil ne se crée pas autrement", async () => {
    await assert.rejects(as(KARIM, `insert into public.profiles (user_id, display_name, birthdate) values ('${KARIM}', 'K', '2015-01-01')`));
  });
});

describe("ce qui reste caché aux personnes", () => {
  it("ni scripts, ni prix minimum, ni fiches contact, ni réglages", async () => {
    await as(ADMIN, `insert into public.contacts (user_id, notes) values ('${KARIM}', 'Aime les voyages')`);
    assert.equal((await as(KARIM, "select * from public.scripts")).length, 0);
    assert.equal((await as(KARIM, "select * from public.script_steps")).length, 0);
    assert.equal((await as(KARIM, "select * from public.contacts")).length, 0);
    assert.equal((await as(KARIM, "select * from public.ai_settings")).length, 0);
    await assert.rejects(as(KARIM, "select public.prochaine_etape($1)", [KARIM]));
    await assert.rejects(as(KARIM, "select public.proposer_etape($1, $2, 100, 'x', 'ai', null)", [KARIM, steps[1]]));
    // Une modification des réglages ne touche aucune ligne.
    await as(KARIM, "update public.ai_settings set mode = 'manuel'");
    assert.equal((await as<{ mode: string }>(ADMIN, "select mode from public.ai_settings"))[0].mode, "auto");
  });

  it("l'équipe, elle, voit et règle tout", async () => {
    assert.equal((await as(ADMIN, "select * from public.script_steps")).length, 3);
    await as(ADMIN, "update public.ai_settings set mode = 'hybride'");
    assert.equal((await as<{ mode: string }>(ADMIN, "select mode from public.ai_settings"))[0].mode, "hybride");
    await as(ADMIN, "update public.ai_settings set mode = 'auto'");
  });
});

describe("vente : l'ordre, les prix", () => {
  it("commence par la première étape, qui est offerte car gratuite", async () => {
    await assert.rejects(propose("service", KARIM, steps[1], 800), /ordre de vente impose de proposer d'abord « Bienvenue »/);
    const { offre } = await propose("service", KARIM, steps[0], null);
    assert.equal(offre.status, "offerte");
    assert.equal(offre.price_cents, 0);
  });

  it("ramène le prix entre le minimum et le maximum, et le dit personnalisé", async () => {
    const { offre } = await propose("service", KARIM, steps[1], 99_999);
    assert.equal(offre.price_cents, 1200);
    assert.equal(offre.personalized, true);
    const [msg] = await as<{ author: string; kind: string; offer_id: number }>(
      KARIM,
      "select author, kind, offer_id from public.messages where kind = 'offer' order by id desc limit 1",
    );
    assert.deepEqual([msg.author, msg.kind, Number(msg.offer_id)], ["ai", "offer", Number(offre.id)]);
  });

  it("une seule offre en attente à la fois", async () => {
    await assert.rejects(propose("service", KARIM, steps[2], 1500), /ordre de vente|attend déjà/);
  });

  it("l'équipe peut retirer l'offre et en proposer une autre au prix de base", async () => {
    const [pending] = await as<{ id: number }>(ADMIN, `select id from public.offers where user_id = '${KARIM}' and status = 'proposee'`);
    await as(ADMIN, "select public.admin_retirer_offre($1)", [pending.id]);
    const { offre } = await propose(ADMIN, KARIM, steps[1], null, "Un carnet rien que pour toi");
    assert.equal(offre.price_cents, 800);
    assert.equal(offre.personalized, false);
    const [msg] = await as<{ author: string; author_id: string }>(
      KARIM,
      "select author, author_id from public.messages where kind = 'offer' order by id desc limit 1",
    );
    assert.equal(msg.author, "team");
  });
});

describe("vente : contre-offres, achat, contenu", () => {
  let offer: number;
  before(async () => {
    [{ id: offer }] = await as<{ id: number }>(KARIM, "select id from public.offers where status = 'proposee'");
  });

  it("rien n'est visible avant l'achat", async () => {
    await assert.rejects(as(KARIM, "select public.mon_contenu($1)", [offer]), /verrouillé/);
  });

  it("refuse une offre sous le minimum, sans le révéler, trois fois au plus", async () => {
    const r = await one<{ statut: string; essais_restants: number }>(KARIM, "select public.faire_une_offre($1, 300) as r", [offer]);
    assert.equal(r.statut, "refusee");
    assert.equal(r.essais_restants, 2);
    assert.ok(!JSON.stringify(r).includes("500"));
  });

  it("accepte une offre au minimum ou au-dessus, et le prix devient celui de l'offre", async () => {
    const r = await one<{ statut: string; prix_cents: number }>(KARIM, "select public.faire_une_offre($1, 600) as r", [offer]);
    assert.deepEqual([r.statut, r.prix_cents], ["acceptee", 600]);
    const [o] = await as<Offer>(KARIM, "select price_cents, personalized from public.offers where id = $1", [offer]);
    assert.deepEqual([o.price_cents, o.personalized], [600, true]);
  });

  it("personne d'autre ne peut faire d'offre ni acheter", async () => {
    await assert.rejects(as(LEA, "select public.faire_une_offre($1, 900)", [offer]), /introuvable/);
    await assert.rejects(as(LEA, "select public.acheter_offre($1)", [offer]), /introuvable/);
  });

  it("achète au prix convenu, puis le contenu se dévoile", async () => {
    const r = await one<{ cents: number }>(KARIM, "select public.acheter_offre($1) as r", [offer]);
    assert.equal(r.cents, 600);
    const c = await one<{ type: string; texte: string }>(KARIM, "select public.mon_contenu($1) as r", [offer]);
    assert.equal(c.texte, "Le carnet de voyage, page 1.");
    await assert.rejects(as(LEA, "select public.mon_contenu($1)", [offer]), /verrouillé/);
    await assert.rejects(as(KARIM, "select public.acheter_offre($1)", [offer]), /plus disponible/);
    const [p] = await as<{ kind: string; is_demo: boolean }>(KARIM, "select kind, is_demo from public.purchases");
    assert.deepEqual([p.kind, p.is_demo], ["contenu", true]);
  });

  it("l'étape suivante est la troisième, et le plafond du mois est respecté", async () => {
    await as(ADMIN, `update public.contacts set spending_cap_cents = 1000 where user_id = '${KARIM}'`);
    const { offre } = await propose("service", KARIM, steps[2], 1500);
    await assert.rejects(as(KARIM, "select public.acheter_offre($1)", [offre.id]), /plafond/);
    await as(ADMIN, `update public.contacts set spending_cap_cents = null where user_id = '${KARIM}'`);
    await as(KARIM, "select public.acheter_offre($1)", [offre.id]);
    await assert.rejects(propose("service", KARIM, steps[2], 1500), /plus rien à proposer/);
  });
});

describe("messagerie de l'équipe", () => {
  it("la liste des conversations, les non-lus, et une réponse signée « Équipe »", async () => {
    await as(LEA, "insert into public.messages (role, content) values ('user', 'Bonjour ?')");
    let inbox = await one<{ user_id: string; nom: string; non_lus: number }[]>(ADMIN, "select public.admin_boite() as r");
    const lea = inbox.find((c) => c.user_id === LEA)!;
    assert.equal(lea.nom, "Léa B.");
    assert.equal(lea.non_lus, 1);

    await as(ADMIN, "select public.admin_envoyer($1, 'Bonjour Léa, ici l''équipe.')", [LEA]);
    inbox = await one(ADMIN, "select public.admin_boite() as r");
    assert.equal(inbox.find((c) => c.user_id === LEA)!.non_lus, 0);
    const [m] = await as<{ author: string; content: string }>(LEA, "select author, content from public.messages order by id desc limit 1");
    assert.deepEqual([m.author, m.content], ["team", "Bonjour Léa, ici l'équipe."]);
  });

  it("la fiche d'une personne : âge, dépenses, prochaine étape", async () => {
    const p = await one<{ age: number; depense_cents: number; prochaine_etape: { title: string } | null }>(
      ADMIN,
      "select public.admin_personne($1) as r",
      [LEA],
    );
    assert.ok(p.age >= 40);
    assert.equal(p.depense_cents, 0);
    assert.equal(p.prochaine_etape?.title, "Bienvenue");
  });

  it("tout cela est fermé aux personnes", async () => {
    await assert.rejects(as(KARIM, "select public.admin_boite()"), /Réservé/);
    await assert.rejects(as(KARIM, "select public.admin_personne($1)", [LEA]), /Réservé/);
    await assert.rejects(as(KARIM, "select public.admin_envoyer($1, 'x')", [LEA]), /Réservé/);
    await assert.rejects(as(KARIM, "select public.admin_proposer($1, $2, 100, 'x')", [LEA, steps[0]]), /Réservé/);
  });

  it("« Effacer toutes mes données » efface aussi les notes de l'équipe, pas les achats", async () => {
    await as(KARIM, "select public.effacer_mes_donnees()");
    const [c] = await as<{ notes: string }>(ADMIN, `select notes from public.contacts where user_id = '${KARIM}'`);
    assert.equal(c.notes, "");
    assert.equal((await as(KARIM, "select id from public.purchases")).length, 2);
  });
});

describe("tableau de bord : contenus et LTV", () => {
  it("compte les contenus vendus et calcule la LTV", async () => {
    const d = await one<{
      totaux: { contenus: { nombre: number; cents: number } };
      ltv: { clients: number; moyenne_cents: number; payants: number; inscrits: number };
      clients: { nom: string; contenus_cents: number; achats: number }[];
    }>(ADMIN, "select public.admin_dashboard() as r");
    assert.deepEqual(d.totaux.contenus, { nombre: 2, cents: 2100 });
    assert.equal(d.ltv.clients, 1);
    assert.equal(d.ltv.moyenne_cents, 2100);
    assert.equal(d.ltv.inscrits, 3);
    assert.equal(d.ltv.payants, 0); // achats « démo » : pas encore de vrai client payant
    assert.equal(d.clients[0].contenus_cents, 2100);
    assert.equal(d.clients[0].achats, 2);
  });
});

describe("message du script avec plusieurs photos et vidéos", () => {
  const SAM = "dddddddd-dddd-dddd-dddd-dddddddddddd";
  let base: Awaited<ReturnType<typeof freshDatabase>>;
  let script: number;
  let pack: number;
  const media = [
    { path: "pack/a.jpg", kind: "image" },
    { path: "pack/b.jpg", kind: "image" },
    { path: "pack/c.mp4", kind: "video" },
  ];

  before(async () => {
    base = await freshDatabase([
      { id: ADMIN, email: "admin@example.com" },
      { id: SAM, email: "sam@example.com" },
    ]);
    await base.db.query("insert into public.admins (user_id) values ($1)", [ADMIN]);
    [{ id: script }] = await base.as<{ id: number }>(ADMIN, "insert into public.scripts (name) values ('Packs') returning id");
    [{ id: pack }] = await base.as<{ id: number }>(
      ADMIN,
      `insert into public.script_steps
         (script_id, position, title, content_type, media, is_paid, price_cents, min_price_cents, max_price_cents)
       values ($1, 1, 'Le pack', 'video', $2::jsonb, true, 900, 600, 1200) returning id`,
      [script, JSON.stringify(media)],
    );
  });

  it("l'offre annonce 2 photos et 1 vidéo, sans rien montrer", async () => {
    const [{ r }] = await base.as<{ r: { offre: { id: number } } }>(
      "service",
      "select public.proposer_etape($1, $2, null, 'Regarde', 'ai', null) as r",
      [SAM, pack],
    );
    const [offer] = await base.as<{ photo_count: number; video_count: number }>(
      SAM,
      "select photo_count, video_count from public.offers where id = $1",
      [r.offre.id],
    );
    assert.deepEqual([offer.photo_count, offer.video_count], [2, 1]);
    await assert.rejects(base.as(SAM, "select public.mon_contenu($1)", [r.offre.id]), /verrouillé/);
  });

  it("après l'achat, tout le pack s'ouvre, dans l'ordre", async () => {
    const [{ id }] = await base.as<{ id: number }>(SAM, "select id from public.offers where status = 'proposee'");
    await base.as(SAM, "select public.acheter_offre($1)", [id]);
    const [{ r }] = await base.as<{ r: { media: { path: string; kind: string }[] } }>(
      SAM,
      "select public.mon_contenu($1) as r",
      [id],
    );
    assert.deepEqual(r.media, media);
  });

  it("au plus 10 fichiers par message", async () => {
    const eleven = JSON.stringify(Array.from({ length: 11 }, (_, i) => ({ path: `x/${i}.jpg`, kind: "image" })));
    await assert.rejects(
      base.as(
        ADMIN,
        `insert into public.script_steps (script_id, position, title, content_type, media, is_paid)
         values ($1, 2, 'Trop', 'image', $2::jsonb, false)`,
        [script, eleven],
      ),
      /media_check/,
    );
  });

  it("l'ancien fichier unique passe dans la liste quand on relance le script", async () => {
    const [{ id }] = await base.as<{ id: number }>(
      ADMIN,
      `insert into public.script_steps (script_id, position, title, content_type, media_path, is_paid)
       values ($1, 3, 'Ancien', 'image', 'ancien/photo.png', false) returning id`,
      [script],
    );
    await base.db.exec(schemaSql);
    const [step] = await base.as<{ media: unknown; media_path: string | null }>(
      ADMIN,
      "select media, media_path from public.script_steps where id = $1",
      [id],
    );
    assert.deepEqual(step.media, [{ path: "ancien/photo.png", kind: "image" }]);
    assert.equal(step.media_path, null);
  });
});
