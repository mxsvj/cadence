// Parcours complet d'un utilisateur, sur téléphone puis sur ordinateur, contre
// le serveur local branché sur les faux Supabase et Gemini (faux-services.mjs).
// Se lance avec lancer.mjs (npm run test:e2e).
import { chromium } from "playwright-core";
import { readFileSync, mkdirSync } from "node:fs";
import assert from "node:assert/strict";

const BASE = process.env.E2E_BASE;
const SHOTS = `${process.env.E2E_SHOTS}/`;
mkdirSync(SHOTS, { recursive: true });
// L'état du faux Supabase (vide tant qu'il n'a reçu aucune requête).
const state = () => {
  try {
    return JSON.parse(readFileSync(process.env.E2E_STATE, "utf8"));
  } catch {
    return { users: [], tables: {}, llm: [] };
  }
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function until(check, what, timeout = 8000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    if (check()) return;
    await sleep(150);
  }
  throw new Error(`Délai dépassé : ${what}`);
}
const step = (s) => console.log(`✓ ${s}`);
// Les montants en français s'écrivent avec des espaces insécables (« 9,00 € »).
const plain = (text) => (text ?? "").replace(/[\u00a0\u202f]/g, " ");
// SQL d'administration, exécuté dans la base du faux Supabase.
async function sql(query, params = []) {
  const res = await fetch(`http://127.0.0.1:${process.env.E2E_CONTROL_PORT}`, {
    method: "POST",
    body: JSON.stringify({ sql: query, params }),
  });
  const body = await res.json();
  if (!res.ok) throw new Error(body.error);
  return body;
}

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH ?? "/opt/pw-browsers/chromium" });
const phone = { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, locale: "fr-FR" };
const desktop = { viewport: { width: 1280, height: 900 }, locale: "fr-FR" };

// Le navigateur ne connaît pas fake-supabase.test (envoi et lecture des
// fichiers) : on relaie ses requêtes vers le faux Supabase du serveur.
const CORS = { "access-control-allow-origin": "*", "access-control-allow-methods": "*", "access-control-allow-headers": "*" };
async function newContext(options) {
  const context = await browser.newContext(options);
  await context.route("http://fake-supabase.test/**", async (route) => {
    const req = route.request();
    if (req.method() === "OPTIONS") return route.fulfill({ status: 204, headers: CORS });
    const res = await fetch(`http://127.0.0.1:${process.env.E2E_CONTROL_PORT}`, {
      method: req.method(),
      headers: { ...req.headers(), "x-relay-url": req.url() },
      body: req.postDataBuffer() ?? undefined,
    });
    await route.fulfill({
      status: res.status,
      headers: { ...CORS, "content-type": res.headers.get("content-type") ?? "application/octet-stream" },
      body: Buffer.from(await res.arrayBuffer()),
    });
  });
  return context;
}

async function signUp(p, email, name, birthdate = "1982-03-14") {
  await p.goto(`${BASE}/connexion`);
  await p.getByText("Première visite ? Créer un compte").click();
  await p.fill('input[name="email"]', email);
  await p.fill('input[name="password"]', "motdepasse");
  await p.fill('input[name="nom"]', name);
  await p.fill('input[name="naissance"]', birthdate);
  await p.click('button[type="submit"]');
}

async function logIn(p, email) {
  await p.goto(`${BASE}/connexion`);
  await p.fill('input[name="email"]', email);
  await p.fill('input[name="password"]', "motdepasse");
  await p.click('button[type="submit"]');
  await p.waitForURL(`${BASE}/`);
}

const ctx = await newContext(phone);
const page = await ctx.newPage();
const consoleErrors = [];
page.on("console", (m) => m.type() === "error" && consoleErrors.push(m.text()));
page.on("pageerror", (e) => consoleErrors.push(String(e)));

// 1. Sans être connecté, on arrive sur la connexion.
await page.goto(BASE);
await page.waitForURL(`${BASE}/connexion`);
await page.screenshot({ path: `${SHOTS}1-connexion.png` });
step("un visiteur non connecté est envoyé sur /connexion");
for (const asset of ["/manifest.webmanifest", "/icon-192.png", "/icon.png", "/apple-icon.png"]) {
  const res = await page.request.get(`${BASE}${asset}`, { maxRedirects: 0 });
  assert.equal(res.status(), 200, asset);
}
step("icônes et manifeste accessibles sans connexion (installation sur l'écran d'accueil)");

// 2. Mauvais identifiants.
await page.fill('input[name="email"]', "karim@example.com");
await page.fill('input[name="password"]', "mauvais");
await page.click('button[type="submit"]');
await page.getByText("Adresse e-mail ou mot de passe incorrect.").waitFor();
step("mauvais identifiants : message clair");

// 3. Inscription : 18 ans minimum, puis prénom et date de naissance.
const minor = new Date();
minor.setFullYear(minor.getFullYear() - 16);
await signUp(page, "karim@example.com", "Karim", minor.toISOString().slice(0, 10));
await page.waitForTimeout(800);
assert.equal(new URL(page.url()).pathname, "/connexion");
assert.equal(state().users.length, 0);
step("une personne de moins de 18 ans ne peut pas s'inscrire");
await page.fill('input[name="naissance"]', "1982-03-14");
await page.click('button[type="submit"]');
await page.waitForURL(`${BASE}/`);
await page.getByText("Bonjour, je suis Élise.").waitFor();
await page.screenshot({ path: `${SHOTS}2-premier-message.png` });
let s = state();
assert.equal(s.tables.messages.length, 1);
assert.equal(s.tables.messages[0].role, "assistant");
step("inscription → premier message d'Élise, enregistré en base");

// 4. Recharger ne duplique pas le premier message.
await page.reload();
await page.getByText("Bonjour, je suis Élise.").waitFor();
assert.equal(state().tables.messages.length, 1);
step("recharger la page ne répète pas le premier message");

// 5. Un premier échange.
const input = page.getByLabel("Votre message");
await input.fill("Bonsoir, moi c'est Karim. Tu peux me tutoyer. J'ai un chat. Et je prends des antidépresseurs.");
await page.getByLabel("Envoyer").click();
await page.getByText("C'est noté. Merci de me le dire. (réponse de test n° 1)").waitFor();
assert.equal(await input.inputValue(), "");
assert.equal(await page.getByText("Élise · IA").count(), 2);
await page.screenshot({ path: `${SHOTS}3-echange.png` });
step("message envoyé, réponse à gauche marquée « Élise · IA », sans le gras Markdown");

// 6. La fiche : nouveaux faits, sans doublon ni donnée sensible.
await until(() => state().tables.user_facts.length >= 3, "faits enregistrés");
await sleep(500);
s = state();
const facts = s.tables.user_facts.map((f) => f.fact);
assert.deepEqual(facts.sort(), ["A un chat, Filou.", "Préfère le tutoiement.", "Se prénomme Karim."]);
step(`fiche : ${facts.join(" / ")} — l'antidépresseur a été écarté, le doublon aussi`);

// 7. Ce que le modèle a reçu pour répondre.
const firstChat = s.llm.find((r) => !r.json);
assert.match(firstChat.system, /^# Règles de base de l'IA/);
assert.match(firstChat.system, /## Ton personnage[\s\S]*Nom : Élise/);
assert.match(firstChat.system, /Prénom ou pseudo : Karim/);
assert.match(firstChat.system, /Tu ne sais encore rien/);
assert.deepEqual(firstChat.contents.map((c) => c.role), ["user", "model", "user"]);
step("le modèle a reçu : persona + fiche + résumé + conversation");

// 8. Quota atteint : rien n'est perdu.
await input.fill("Test QUOTA");
await page.getByLabel("Envoyer").click();
await page.getByText("Beaucoup de messages en ce moment. Réessayez dans une minute.").waitFor();
assert.equal(await input.inputValue(), "Test QUOTA");
assert.equal(state().tables.messages.length, 3);
await page.screenshot({ path: `${SHOTS}4-quota.png` });
step("quota atteint : message gentil, le texte revient dans la zone de saisie, rien d'enregistré");
await input.fill("");

// 9. Beaucoup de messages : le résumé se déclenche au-delà de 40.
for (let i = 1; i <= 20; i++) {
  const res = await page.evaluate(async (i) => {
    const r = await fetch("/api/chat", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ content: `Message numéro ${i}` }) });
    return r.status;
  }, i);
  assert.equal(res, 200);
  await sleep(250);
}
await until(() => state().tables.summaries.length === 1, "résumé créé", 15000);
s = state();
const msgs = s.tables.messages;
const summary = s.tables.summaries[0];
const unsummarized = msgs.filter((m) => m.id > summary.last_message_id).length;
assert.equal(msgs.length, 43);
// Le résumé part dès que 41 messages attendent : il garde les 20 derniers de
// ce moment-là. Un ou deux échanges ont pu arriver depuis.
assert.ok(unsummarized >= 20 && unsummarized <= 22, `non résumés : ${unsummarized}`);
assert.ok(summary.last_message_id >= 21);
assert.match(summary.summary, /Résumé de test/);
step(`43 messages → les ${msgs.length - unsummarized} plus anciens résumés, ${unsummarized} récents gardés tels quels`);

// 10. La réponse suivante reçoit le résumé, la fiche et exactement 20 messages.
await page.evaluate(async () => {
  await fetch("/api/chat", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ content: "Tu te souviens de moi ?" }) });
});
await sleep(800);
s = state();
const lastChat = s.llm.filter((r) => !r.json && !r.system.includes("carnet")).at(-1);
assert.match(lastChat.system, /Résumé de test/);
assert.match(lastChat.system, /- Se prénomme Karim\./);
const sent = lastChat.contents.filter((c) => c.parts[0].text !== "(La personne ouvre la conversation.)");
assert.equal(sent.length, 20);
assert.equal(sent.at(-1).parts[0].text, "Tu te souviens de moi ?");
step("la réponse suivante reçoit la fiche, le résumé et les 20 derniers messages");

// 11. La page affiche l'historique, dans l'ordre.
await page.reload();
await page.getByText("Tu te souviens de moi ?").waitFor();
await page.screenshot({ path: `${SHOTS}5-historique.png` });
step("l'historique s'affiche au rechargement");

// 12. Un second compte ne voit rien du premier.
const ctx2 = await newContext(phone);
const page2 = await ctx2.newPage();
await signUp(page2, "lea@example.com", "Léa");
await page2.waitForURL(`${BASE}/`);
await page2.getByText("Bonjour, je suis Élise.").waitFor();
assert.equal(await page2.getByText("Karim").count(), 0);
assert.equal(await page2.getByText("Élise · IA").count(), 1);
step("un second compte ne voit que sa propre conversation");

// 13. Effacer toutes mes données.
await page.getByLabel("Menu").click();
await page.screenshot({ path: `${SHOTS}6-menu.png` });
await page.getByText("Effacer toutes mes données").click();
await page.getByText("Tout effacer ?").waitFor();
await page.screenshot({ path: `${SHOTS}7-confirmation.png` });
await page.getByText("Oui, tout effacer").click();
await until(() => state().tables.user_facts.every((f) => f.user_id !== state().users[0].id), "fiche effacée");
await page.getByText("Tu te souviens de moi ?").waitFor({ state: "detached" });
await page.getByText("Bonjour, je suis Élise.").waitFor();
s = state();
const karim = s.users.find((u) => u.email === "karim@example.com").id;
const lea = s.users.find((u) => u.email === "lea@example.com").id;
assert.equal(s.tables.messages.filter((m) => m.user_id === karim).length, 1);
assert.equal(s.tables.user_facts.filter((m) => m.user_id === karim).length, 0);
assert.equal(s.tables.summaries.filter((m) => m.user_id === karim).length, 0);
assert.equal(s.tables.messages.filter((m) => m.user_id === lea).length, 1);
await page.screenshot({ path: `${SHOTS}8-apres-effacement.png` });
step("« Effacer » vide messages, fiche et résumé ; Élise se représente ; l'autre compte est intact");

// 14. Déconnexion, puis reconnexion.
await page.getByLabel("Menu").click();
await page.getByText("Se déconnecter").click();
await page.waitForURL(`${BASE}/connexion`);
await page.goto(BASE);
await page.waitForURL(`${BASE}/connexion`);
await page.fill('input[name="email"]', "karim@example.com");
await page.fill('input[name="password"]', "motdepasse");
await page.click('button[type="submit"]');
await page.waitForURL(`${BASE}/`);
step("déconnexion puis reconnexion");

// 15. Le tableau de bord n'existe pas pour qui n'est pas administrateur.
let res = await page.goto(`${BASE}/admin`);
assert.equal(res.status(), 404);
await page.goto(BASE);
await page.getByLabel("Menu").click();
assert.equal(await page.getByRole("link", { name: "Tableau de bord" }).count(), 0);
await page.keyboard.press("Escape");
assert.equal(await page.evaluate(async () => (await fetch("/api/admin/dashboard")).status), 404);
step("pas administrateur : ni page, ni lien, ni chiffres");

// 16. Karim devient administrateur, comme avec supabase/admin.sql.
await sql("insert into public.admins (user_id) select id from auth.users where email = $1", ["karim@example.com"]);
await page.goto(BASE);
await page.getByLabel("Menu").click();
await page.getByRole("link", { name: "Tableau de bord" }).click();
await page.waitForURL(`${BASE}/admin`);
await page.getByText("Aucun achat pour l'instant.").waitFor();
await page.getByText(/^En direct ·/).waitFor();
await page.screenshot({ path: `${SHOTS}10-tableau-vide.png`, fullPage: true });
step("administrateur : lien dans le menu, tableau de bord vide mais prêt");

// 17. Soixante jours de démonstration.
await page.getByRole("button", { name: "Remplir 60 jours de démo" }).click();
await page.getByText("Données de démonstration.").waitFor();
await page.getByText("60 jours d'achats fictifs ajoutés.").waitFor();
s = state();
assert.ok(s.tables.purchases.length > 60 && s.tables.purchases.every((p) => p.is_demo));
assert.ok((await page.locator("svg[role=img] path").count()) >= 2);
step(`démo : ${s.tables.purchases.length} achats fictifs, courbe tracée`);

// 18. Un vrai achat arrive, comme l'écrira le service de paiement : il
// s'affiche en direct, sans recharger la page.
await sql("insert into public.purchases (user_id, kind, amount_cents) select id, 'tip', 700 from auth.users where email = $1", ["lea@example.com"]);
const latestCard = page.locator("section", { has: page.getByRole("heading", { name: "Dernier achat" }) });
await latestCard.getByText("lea@example.com").waitFor({ timeout: 10000 });
await latestCard.getByText("Pourboire de 7,00 €").waitFor();
await page.screenshot({ path: `${SHOTS}11-tableau-direct.png`, fullPage: true });
step("un nouvel achat apparaît en direct dans « Dernier achat », sans recharger");

// 19. Le bouton « Simuler un achat ».
const before = state().tables.purchases.length;
await page.getByRole("button", { name: "Simuler un achat" }).click();
await page.getByText("Achat fictif ajouté.").waitFor();
await until(() => state().tables.purchases.length === before + 1, "achat simulé");
step("« Simuler un achat » ajoute un achat fictif");

// 20. Une personne à la fois.
await page.locator("#filtre-personne").selectOption({ label: "lea@example.com" });
await page.getByText("Gains · 30 derniers jours · lea@example.com").waitFor();
await page.getByText("1 pourboire", { exact: true }).waitFor();
assert.equal(await page.getByText("7,00 €").count() > 0, true);
await page.screenshot({ path: `${SHOTS}12-une-personne.png`, fullPage: true });
await page.getByRole("button", { name: "Voir tout le monde" }).click();
await page.getByText("Gains · 30 derniers jours", { exact: true }).waitFor();
step("filtre sur une personne : ses pourboires, ses messages, son abonnement");

// 21. Sept jours, l'infobulle, et le tableau des valeurs.
await page.getByRole("button", { name: "7 jours" }).click();
const chart = page.locator('svg[aria-label*="sur 7 jours"]');
await chart.waitFor();
await chart.scrollIntoViewIfNeeded(); // le doigt ne touche que ce qui est à l'écran
const box = await chart.boundingBox();
await page.touchscreen.tap(box.x + box.width * 0.5, box.y + 100);
await page.locator("div[role=status]", { hasText: "Abonnements" }).waitFor();
await page.screenshot({ path: `${SHOTS}12b-infobulle-telephone.png` });
await page.getByRole("button", { name: "Voir le tableau" }).click();
assert.equal(await page.locator("figure table tbody tr").count(), 7);
await page.getByRole("button", { name: "Voir la courbe" }).click();
await chart.waitFor();
step("7 jours : courbe, infobulle au toucher, tableau de 7 lignes");

// 22. Sur ordinateur, clair puis sombre.
for (const colorScheme of ["light", "dark"]) {
  const deskCtx = await newContext({ ...desktop, colorScheme });
  const desk = await deskCtx.newPage();
  desk.on("pageerror", (e) => consoleErrors.push(String(e)));
  await desk.goto(`${BASE}/connexion`);
  await desk.fill('input[name="email"]', "karim@example.com");
  await desk.fill('input[name="password"]', "motdepasse");
  await desk.click('button[type="submit"]');
  await desk.waitForURL(`${BASE}/`);
  await desk.goto(`${BASE}/admin`);
  const svg = desk.locator("svg[role=img]");
  await svg.waitFor();
  await svg.scrollIntoViewIfNeeded();
  const b = await svg.boundingBox();
  await desk.mouse.move(b.x + b.width * 0.8, b.y + 120);
  await desk.locator("div[role=status]", { hasText: "Abonnements" }).waitFor();
  await desk.screenshot({ path: `${SHOTS}13-tableau-ordinateur-${colorScheme === "dark" ? "sombre" : "clair"}.png`, fullPage: true });
  await deskCtx.close();
}
step("tableau de bord sur ordinateur, clair et sombre");

// 23. Effacer la démo : les achats fictifs partent, le vrai reste.
await page.getByRole("button", { name: "Effacer la démo" }).click();
await page.getByRole("button", { name: "Confirmer : effacer la démo" }).click();
await page.getByText("Achats fictifs effacés.").waitFor();
await until(() => state().tables.purchases.length === 1, "démo effacée");
assert.equal(state().tables.purchases[0].amount_cents, 700);
await page.getByText("Données de démonstration.").waitFor({ state: "detached" });
step("« Effacer la démo » retire les achats fictifs et garde le vrai");

// ═══ Le personnage, la messagerie de l'équipe, la vente ═════════════════

// 24. L'équipe règle le personnage (onglet IA), sur ordinateur.
const adminCtx = await newContext(desktop);
const admin = await adminCtx.newPage();
admin.on("pageerror", (e) => consoleErrors.push(String(e)));
await logIn(admin, "karim@example.com");
await admin.goto(`${BASE}/admin/ia`);
await admin.getByLabel("Nom", { exact: true }).fill("Chloé");
await admin.getByLabel("Âge").fill("29");
await admin.getByLabel("Ville", { exact: true }).fill("Annecy");
await admin.getByLabel("Langue maternelle").selectOption("it");
await admin.getByText("Se dire dans la même région que la personne").click();
await admin.getByRole("button", { name: "Ajouter un groupe" }).click();
await admin.getByLabel("Nom du groupe").fill("Tatouages");
await admin.getByLabel("Détail").fill("une hirondelle sur le poignet");
await admin.getByRole("button", { name: "Ajouter une catégorie" }).click();
await admin.getByLabel("Catégorie").fill("Musique");
await admin.getByLabel("Préférences").fill("jazz, bossa nova");
await admin.getByLabel("Messages avant la première offre").fill("0");
await admin.getByLabel("Messages entre deux offres").fill("0");
await admin.getByRole("button", { name: "Enregistrer les réglages" }).click();
await admin.getByText("Réglages enregistrés.").waitFor();
s = state();
assert.equal(s.tables.ai_settings[0].persona.nom, "Chloé");
assert.equal(s.tables.ai_settings[0].persona.pres_de_la_personne, true);
await admin.screenshot({ path: `${SHOTS}14-ia.png`, fullPage: true });
step("onglet IA : profil du personnage enregistré (nom, âge, ville, langue, groupes, centres d'intérêt)");

// 25. Un script de vente de trois étapes (onglet Contenus).
const photo = await admin.screenshot({ clip: { x: 0, y: 0, width: 160, height: 100 } });
await admin.goto(`${BASE}/admin/contenus`);
await admin.getByLabel("Nom du nouveau script").fill("Principal");
await admin.getByRole("button", { name: "Créer" }).click();
await admin.getByText("Script créé.").waitFor();

async function addStep({ title, type, text, file, description, fixed, team, price }) {
  await admin.getByRole("button", { name: "Ajouter une étape" }).click();
  const form = admin.locator("form", { has: admin.getByText("Titre (visible uniquement par l'équipe)") });
  await form.getByLabel("Titre (visible uniquement par l'équipe)").fill(title);
  await form.getByText(type, { exact: true }).click();
  if (text) await form.getByLabel("Texte à vendre").fill(text);
  if (file) {
    await form.getByLabel("Fichier à vendre").setInputFiles(file);
    await form.getByText("Fichier envoyé.", { exact: false }).waitFor();
  }
  await form.getByLabel("À quoi ça ressemble (pour l'IA)").fill(description);
  if (fixed) {
    await form.getByLabel("Un texte fixe, écrit par l'équipe").check();
    await form.getByLabel("Message fixe").fill(fixed);
  }
  if (team) await form.getByLabel("L'équipe, depuis l'onglet Messages").check();
  if (price) {
    await form.getByLabel("Prix habituel (€)").fill(price[0]);
    await form.getByLabel("Minimum accepté (€)").fill(price[1]);
    await form.getByLabel("Maximum (€)").fill(price[2]);
  } else {
    await form.getByLabel("Payant (sinon, offert)").uncheck();
  }
  await form.getByRole("button", { name: "Enregistrer l'étape" }).click();
  await until(() => (state().tables.script_steps ?? []).some((st) => st.title === title), `étape « ${title} » enregistrée`);
  await form.waitFor({ state: "detached" });
}
await addStep({ title: "Bienvenue", type: "Texte", text: "Un poème de bienvenue.", description: "un court poème" });
await addStep({
  title: "Carnet de voyage",
  type: "Photo",
  file: { name: "carnet.png", mimeType: "image/png", buffer: photo },
  description: "un carnet de voyage illustré",
  fixed: "Je t'ai préparé ceci.",
  price: ["8", "5", "12"],
});
await addStep({ title: "Lettre", type: "Texte", text: "Une lettre rien que pour toi.", description: "une lettre", team: true, price: ["4", "3", "6"] });
s = state();
assert.deepEqual(s.tables.script_steps.map((st) => st.title), ["Bienvenue", "Carnet de voyage", "Lettre"]);
assert.ok(s.tables.script_steps[1].media_path.endsWith(".png"));
await admin.screenshot({ path: `${SHOTS}15-contenus.png`, fullPage: true });
step("onglet Contenus : script de trois étapes dans l'ordre, fichier envoyé dans le stockage privé");

// 26. Sam s'inscrit : l'IA se présente sous le nom du personnage.
const samCtx = await newContext(phone);
const sam = await samCtx.newPage();
sam.on("pageerror", (e) => consoleErrors.push(String(e)));
await signUp(sam, "sam@example.com", "Sam");
await sam.waitForURL(`${BASE}/`);
await sam.getByText("Bonjour, je suis Chloé.").waitFor();
await sam.getByText("Chloé · IA").waitFor();
const samInput = sam.getByLabel("Votre message");
await samInput.fill("Salut Chloé, moi c'est Sam.");
await sam.getByLabel("Envoyer").click();
await sam.getByText(/réponse de test/).waitFor();
assert.equal(await sam.getByText("Chloé · IA").count(), 2);
step("nouvelle personne : premier message et réponses signés « Chloé · IA »");

// 27. Mode hybride : Sam n'est pas cochée, l'IA ne lui répond plus.
await admin.goto(`${BASE}/admin/ia`);
await admin.getByText("Hybride", { exact: true }).click();
await admin.getByRole("button", { name: "Enregistrer les réglages" }).click();
await admin.getByText("Réglages enregistrés.").waitFor();
await admin.getByLabel("L'IA peut parler à Sam").uncheck();
await until(() => state().tables.contacts.some((c) => !c.ai_enabled), "Sam décochée");
await samInput.fill("Tu es là ?");
await sam.getByLabel("Envoyer").click();
await sam.getByText("Message envoyé. La réponse arrivera ici dès que possible.").waitFor();
await sam.waitForTimeout(500);
assert.equal(await sam.getByText("Chloé · IA").count(), 2);
step("mode hybride : l'IA ne répond pas à une personne décochée, le message attend l'équipe");

// 28. L'équipe répond depuis l'onglet Messages ; Sam le reçoit, signé « Équipe ».
await admin.goto(`${BASE}/admin/messages`);
const samRow = admin.getByRole("button", { name: /Sam/ }).first();
await samRow.waitFor();
assert.match(await samRow.textContent(), /Tu es là \?/);
assert.match(await samRow.textContent(), /IA coupée/);
await samRow.click();
await admin.getByLabel("Réponse de l'équipe").fill("Oui, ici l'équipe !");
await admin.getByRole("button", { name: "Envoyer", exact: true }).click();
await sam.getByText("Oui, ici l'équipe !").waitFor({ timeout: 12000 });
await sam.getByText("Équipe", { exact: true }).waitFor();
await sam.screenshot({ path: `${SHOTS}16-reponse-equipe.png` });
step("l'équipe répond depuis la messagerie : Sam reçoit le message en direct, signé « Équipe »");

// 29. La fiche de Sam : l'IA peut lui répondre, ville, emojis, notes.
await admin.getByLabel("L'IA peut répondre à cette personne").check();
await admin.getByLabel("Ville", { exact: true }).fill("Lyon");
await admin.getByLabel("Emojis de cette personne").fill("🌸");
await admin.getByLabel("Comment se comporter avec elle", { exact: false }).fill("Aime les voyages.");
await admin.getByRole("button", { name: "Enregistrer la fiche" }).click();
await admin.getByText("Fiche enregistrée.").waitFor();
await admin.screenshot({ path: `${SHOTS}17-messages.png` });
s = state();
const samContact = s.tables.contacts.find((c) => c.city === "Lyon");
assert.deepEqual([samContact.ai_enabled, samContact.emojis, samContact.notes], [true, "🌸", "Aime les voyages."]);
step("fiche contact enregistrée : IA autorisée, ville, emojis, notes");

// 30. L'IA propose la première étape (gratuite) : offerte et visible tout de suite.
await samInput.fill("PROPOSE-MOI quelque chose");
await sam.getByLabel("Envoyer").click();
await sam.getByText("Un poème de bienvenue.").waitFor();
await sam.getByText("Offert", { exact: true }).waitFor();
s = state();
const salesPrompt = s.llm.filter((r) => !r.json && r.system.includes("## Vente")).at(-1).system;
assert.match(salesPrompt, /Nom : Chloé/);
assert.match(salesPrompt, /près de Lyon/);
assert.match(salesPrompt, /Tu ne proposes jamais de la rencontrer/);
assert.match(salesPrompt, /Tatouages : une hirondelle sur le poignet/);
assert.match(salesPrompt, /uniquement ceux-là : 🌸/);
assert.match(salesPrompt, /Aime les voyages\./);
assert.match(salesPrompt, /Le prochain contenu, dans l'ordre prévu : un court poème/);
assert.match(salesPrompt, /la solitude, l'attachement, la culpabilité ou l'urgence/);
assert.ok(!salesPrompt.includes("Bienvenue")); // le titre reste interne
step("l'IA propose la 1re étape du script ; elle a reçu personnage, fiche, emojis, notes et garde-fous");

// 31. La deuxième étape (payante) : verrouillée, sans aperçu, prix personnalisé affiché.
await samInput.fill("PROPOSE-MOI la suite");
await sam.getByLabel("Envoyer").click();
await sam.getByText("Je t'ai préparé ceci.").waitFor();
const card = sam.locator("div", { has: sam.getByText("Photo à débloquer") }).last();
await card.waitFor();
assert.match(plain(await card.textContent()), /9,00 €/);
assert.match(await card.textContent(), /prix personnalisé pour vous/);
assert.equal(await sam.locator("img").count(), 0);
const samApi = await sam.evaluate(async () => (await fetch("/api/chat?apres=0")).json());
assert.ok(samApi.offers.every((o) => !("min_price_cents" in o) && !("step_id" in o)));
await card.scrollIntoViewIfNeeded();
await sam.screenshot({ path: `${SHOTS}18-offre-verrouillee.png` });
step("offre payante : verrouillée, aucune image chargée, prix personnalisé affiché, minimum jamais transmis");

// 32. Contre-offres : refusée sous le minimum, acceptée au-dessus, puis achat.
await sam.getByRole("button", { name: "Faire une offre" }).click();
await sam.getByLabel("Montant de votre offre en euros").fill("3");
await sam.getByRole("button", { name: "Proposer", exact: true }).click();
await sam.getByText("Offre refusée : c'est en dessous du prix accepté. Il vous reste 2 essais.").waitFor();
await sam.getByRole("button", { name: "Faire une offre" }).click();
await sam.getByLabel("Montant de votre offre en euros").fill("6");
await sam.getByRole("button", { name: "Proposer", exact: true }).click();
await sam.getByText("Offre acceptée : le contenu est à vous pour 6,00 €.").waitFor();
await sam.getByRole("button", { name: "Confirmer" }).click();
await sam.getByText("Débloqué · 6,00 €").waitFor();
const unlocked = sam.getByAltText("Contenu débloqué");
await unlocked.waitFor();
assert.ok(await unlocked.evaluate((img) => img.complete && img.naturalWidth > 0));
await unlocked.scrollIntoViewIfNeeded();
await sam.screenshot({ path: `${SHOTS}19-contenu-debloque.png` });
s = state();
const bought = s.tables.purchases.find((p) => p.kind === "contenu");
assert.deepEqual([bought.amount_cents, bought.is_demo], [600, true]);
step("contre-offre à 3 € refusée, à 6 € acceptée ; achat (paiement de démo) ; la photo s'affiche");

// 33. L'étape 3 se propose par l'équipe : message écrit par l'IA, relu, envoyé.
await admin.reload();
await admin.getByText("Étape suivante :").waitFor();
assert.match(await admin.getByText("Étape suivante :").locator("..").textContent(), /Lettre/);
await admin.getByRole("button", { name: "Faire écrire par l'IA" }).click();
await admin.getByText("Relisez le message avant de l'envoyer.").waitFor();
assert.match(await admin.getByLabel("Message de l'offre").inputValue(), /Un petit carnet rien que pour toi/);
await admin.getByLabel("Prix de l'offre en euros").fill("5");
await admin.getByRole("button", { name: "Envoyer l'offre" }).click();
await admin.getByText("Offre envoyée.").waitFor();
const letter = sam.locator("div", { has: sam.getByText("Texte à débloquer") }).last();
await letter.waitFor({ timeout: 12000 });
assert.match(plain(await letter.textContent()), /5,00 €/);
step("l'équipe propose l'étape suivante avec un message rédigé par l'IA ; Sam la reçoit en direct");

// 34. Le plafond du mois : 8 € pour Sam, qui a déjà dépensé 6 €.
await admin.getByLabel("Plafond de dépenses par mois (€)").fill("8");
await admin.getByRole("button", { name: "Enregistrer la fiche" }).click();
await admin.getByText("Fiche enregistrée.").waitFor();
await sam.getByRole("button", { name: /Débloquer pour 5,00/ }).click();
await sam.getByRole("button", { name: "Confirmer" }).click();
await sam.getByText("Vous avez atteint le plafond de dépenses de ce mois-ci.").waitFor();
step("plafond mensuel : l'achat au-delà est refusé, avec un message clair");

// 35. Mode manuel : l'IA ne répond plus à personne.
await admin.goto(`${BASE}/admin/ia`);
await admin.getByText("Manuel", { exact: true }).click();
await admin.getByRole("button", { name: "Enregistrer les réglages" }).click();
await admin.getByText("Réglages enregistrés.").waitFor();
const aiReplies = await sam.getByText("Chloé · IA").count();
await samInput.fill("Et maintenant ?");
await sam.getByLabel("Envoyer").click();
await sam.getByText("Message envoyé. La réponse arrivera ici dès que possible.").waitFor();
assert.equal(await sam.getByText("Chloé · IA").count(), aiReplies);
step("mode manuel : plus aucune réponse de l'IA, tout passe par l'équipe");

// 36. Le tableau de bord compte les contenus et calcule la LTV.
await admin.goto(`${BASE}/admin`);
await admin.getByText("LTV · valeur d'un client").waitFor();
const contentTile = admin.locator("div", { has: admin.getByText("Contenus vendus", { exact: true }) }).last();
assert.match(plain(await contentTile.textContent()), /6,00 €/);
await admin.screenshot({ path: `${SHOTS}20-tableau-ltv.png`, fullPage: true });
step("tableau de bord : contenus vendus et section LTV");

// 37. Retour en mode automatique, puis sur ordinateur et en mode sombre, pour le coup d'œil.
await admin.goto(`${BASE}/admin/ia`);
await admin.getByText("Automatique", { exact: true }).click();
await admin.getByRole("button", { name: "Enregistrer les réglages" }).click();
await admin.getByText("Réglages enregistrés.").waitFor();
const desk = await newContext({ viewport: { width: 1280, height: 800 }, colorScheme: "dark", locale: "fr-FR" });
const deskPage = await desk.newPage();
await deskPage.goto(`${BASE}/connexion`);
await deskPage.fill('input[name="email"]', "lea@example.com");
await deskPage.fill('input[name="password"]', "motdepasse");
await deskPage.click('button[type="submit"]');
await deskPage.waitForURL(`${BASE}/`);
await deskPage.getByLabel("Votre message").fill("Salut Élise, moi c'est Léa.");
await deskPage.getByLabel("Votre message").press("Enter");
await deskPage.getByText(/réponse de test/).waitFor();
await deskPage.screenshot({ path: `${SHOTS}9-ordinateur-sombre.png` });
step("sur ordinateur, Entrée envoie le message ; mode sombre");

// Les 429 (quota simulé) et 404 (pages réservées) sont voulus.
assert.deepEqual(consoleErrors.filter((e) => !/status of (429|404)/.test(e)), []);
step("aucune erreur dans la console du navigateur");

await browser.close();
console.log("\nParcours complet réussi.");
