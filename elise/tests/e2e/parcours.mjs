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
    if (await check()) return;
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

// Les clients entrent avec un code ; l'e-mail et le mot de passe (l'équipe)
// sont repliés sous « Accès de l'équipe ».
async function emailForm(p) {
  const details = p.locator("details").filter({ hasText: "Accès de l'équipe" });
  if (!(await details.evaluate((d) => d.open))) await details.getByText("Accès de l'équipe (e-mail et mot de passe)").click();
}
async function submitEmail(p) {
  await p.locator("details").getByRole("button", { name: /Me connecter|Créer mon compte/ }).click();
}

async function signUp(p, email, name, birthdate = "1982-03-14") {
  await p.goto(`${BASE}/connexion`);
  await emailForm(p);
  await p.getByText("Première visite ? Créer un compte").click();
  await p.fill('details input[name="email"]', email);
  await p.fill('details input[name="password"]', "motdepasse");
  await p.fill('details input[name="nom"]', name);
  await p.fill('details input[name="naissance"]', birthdate);
  await submitEmail(p);
}

// Après la connexion, une personne arrive sur le choix des créatrices (ou
// directement chez la seule en ligne : la n° 1, « Élise », au départ),
// l'équipe sur son tableau de bord.
async function logIn(p, email, landing = "/") {
  await p.goto(`${BASE}/connexion`);
  await emailForm(p);
  await p.fill('details input[name="email"]', email);
  await p.fill('details input[name="password"]', "motdepasse");
  await submitEmail(p);
  await p.waitForURL(`${BASE}${landing}`);
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

const pageHeaders = (await page.request.get(`${BASE}/connexion`)).headers();
assert.equal(pageHeaders["x-frame-options"], "DENY");
assert.equal(pageHeaders["x-content-type-options"], "nosniff");
assert.equal(pageHeaders["referrer-policy"], "strict-origin-when-cross-origin");
assert.match(pageHeaders["content-security-policy"], /frame-ancestors 'none'/);
assert.equal(pageHeaders["x-powered-by"], undefined);
step("en-têtes de sécurité : pas d'affichage dans un autre site, adresse jamais transmise ailleurs, « Next.js » non annoncé");

// 2. Mauvais identifiants.
await emailForm(page);
await page.fill('details input[name="email"]', "karim@example.com");
await page.fill('details input[name="password"]', "mauvais");
await submitEmail(page);
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
await page.fill('details input[name="naissance"]', "1982-03-14");
await submitEmail(page);
await page.waitForURL(`${BASE}/c/1`);
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

// 6. La fiche ne se met à jour que tous les 3 messages : pas encore après le premier.
await sleep(500);
s = state();
assert.equal(s.llm.filter((r) => r.system.includes("fiche mémoire")).length, 0);
assert.equal(s.tables.user_facts.length, 0);
step("un seul appel au modèle pour ce message : la fiche attend le 3e message");

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
await page.getByText("Beaucoup de messages en ce moment (quota gratuit de l'IA atteint). Réessayez dans une minute.").waitFor();
assert.equal(await input.inputValue(), "Test QUOTA");
assert.equal(state().tables.messages.length, 3);
await page.screenshot({ path: `${SHOTS}4-quota.png` });
step("quota atteint : message gentil, le texte revient dans la zone de saisie, rien d'enregistré");
await input.fill("");

// 9. Beaucoup de messages : le résumé se déclenche au-delà de 40.
for (let i = 1; i <= 20; i++) {
  const res = await page.evaluate(async (i) => {
    const r = await fetch("/api/chat", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ content: `Message numéro ${i}`, creator: 1 }) });
    return r.status;
  }, i);
  assert.equal(res, 200);
  await sleep(250);
}
await until(() => state().tables.summaries.length === 1, "résumé créé", 15000);
await sleep(500);
s = state();
// La fiche : relevée au 3e message dans les 3 derniers échanges, sans doublon ni donnée sensible.
const facts = s.tables.user_facts.map((f) => f.fact);
assert.deepEqual(facts.sort(), ["A un chat, Filou.", "Préfère le tutoiement.", "Se prénomme Karim."]);
const factCalls = s.llm.filter((r) => r.system.includes("fiche mémoire")).length;
assert.equal(factCalls, 7); // messages 3, 6, 9… 21 de Karim : 7 mises à jour pour 21 messages
step(`fiche : ${facts.join(" / ")} — l'antidépresseur a été écarté, le doublon aussi ; ${factCalls} mises à jour pour 21 messages`);
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
  await fetch("/api/chat", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ content: "Tu te souviens de moi ?", creator: 1 }) });
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

// 10b. La charge d'un message : requêtes à la base et appels au modèle.
// La page de conversation est fermée pendant la mesure : sa relecture régulière ne compte pas.
await page.goto(`${BASE}/manifest.webmanifest`);
await sleep(1500); // une relecture encore en route se termine
async function measure(content) {
  const before = state();
  const res = await ctx.request.post(`${BASE}/api/chat`, { data: { content, creator: 1 } });
  assert.equal(res.status(), 200);
  await sleep(800); // la mémoire se met à jour après la réponse
  const after = state();
  return { db: after.restCalls - before.restCalls, llm: after.llm.length - before.llm.length };
}
const plain1 = await measure("Une journée tranquille."); // 23e message de Karim
const plain2 = await measure("Et toi, ta journée ?"); // 24e : mise à jour de la mémoire
assert.equal(plain1.llm, 1);
assert.equal(plain2.llm, 2);
assert.ok(plain1.db <= 22, `requêtes pour un message : ${plain1.db}`);
assert.ok(plain2.db <= 26, `requêtes avec la mémoire : ${plain2.db}`);
step(`charge d'un message : ${plain1.db} requêtes rapides à la base et 1 appel au modèle ; tous les 3 messages, ${plain2.db} requêtes et 2 appels (fiche) ; le résumé, seulement au-delà de 40 messages`);

// 11. La page affiche l'historique, dans l'ordre.
await page.goto(`${BASE}/c/1`);
await page.getByText("Tu te souviens de moi ?").waitFor();
await page.screenshot({ path: `${SHOTS}5-historique.png` });
step("l'historique s'affiche au rechargement");

// 12. Un second compte ne voit rien du premier.
const ctx2 = await newContext(phone);
const page2 = await ctx2.newPage();
await signUp(page2, "lea@example.com", "Léa");
await page2.waitForURL(`${BASE}/c/1`);
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
await emailForm(page);
await page.fill('details input[name="email"]', "karim@example.com");
await page.fill('details input[name="password"]', "motdepasse");
await submitEmail(page);
await page.waitForURL(`${BASE}/c/1`);
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

// 15b. Le lien secret de l'équipe : une clé fausse est refusée, et tant
// qu'aucun administrateur n'existe, la bonne clé explique quoi faire. La
// raison s'affiche aussi pour qui est déjà connecté (Karim), au lieu de le
// renvoyer sur la conversation.
const KEY = process.env.ADMIN_ACCESS_KEY;
const linkCtx = await newContext(phone);
const linkPage = await linkCtx.newPage();
await linkPage.goto(`${BASE}/acces?cle=mauvaise-cle-mauvaise-cle-mauvaise`);
await linkPage.getByText("Ce lien d'accès n'est pas valable.").waitFor();
await linkPage.goto(`${BASE}/acces?cle=${KEY}`);
await linkPage.getByText(/Aucun compte administrateur n'existe encore/).waitFor();
assert.equal(new URL(linkPage.url()).pathname, "/acces/refus");
await page.goto(`${BASE}/acces?cle=${KEY}`);
await page.getByText(/Aucun compte administrateur n'existe encore/).waitFor();
assert.equal(new URL(page.url()).pathname, "/acces/refus");
step("lien de l'équipe : clé fausse refusée ; sans administrateur, la raison s'affiche, même connecté");

// 16. Karim devient administrateur, comme avec supabase/admin.sql.
await sql("insert into public.admins (user_id) select id from auth.users where email = $1", ["karim@example.com"]);
await page.goto(BASE);
await page.waitForURL(`${BASE}/admin`);
await page.getByText("Aucun achat pour l'instant.").waitFor();
await page.getByText(/^En direct ·/).waitFor();
await page.screenshot({ path: `${SHOTS}10-tableau-vide.png`, fullPage: true });
step("administrateur : l'appli s'ouvre sur le tableau de bord, pas sur la conversation");

// 16a. Les onglets sont en bas de l'écran, comme dans une appli. La
// conversation reste là pour la tester (onglet Paramètres), et le menu
// ramène au tableau de bord.
const bar = await page.getByRole("navigation", { name: "Espace de l'équipe" }).boundingBox();
assert.ok(bar.y > 844 - 120, `barre d'onglets en bas (y = ${bar.y})`);
assert.equal(await page.getByRole("navigation", { name: "Espace de l'équipe" }).getByRole("link").count(), 6);
await page.getByRole("link", { name: "Paramètres" }).click();
await page.waitForURL(`${BASE}/admin/parametres`);
await page.getByRole("heading", { name: "Garde-fous de la vente" }).waitFor();
await page.getByRole("link", { name: "Tester la conversation" }).click();
await page.waitForURL(`${BASE}/c/1`); // une seule créatrice en ligne : directement chez elle
await page.getByLabel("Votre message").waitFor();
await page.getByLabel("Menu").click();
await page.getByRole("link", { name: "Tableau de bord" }).click();
await page.waitForURL(`${BASE}/admin`);
await page.getByText("Aucun achat pour l'instant.").waitFor();
step("onglets en bas (6, dont Créatrices et Paramètres) ; l'équipe teste la conversation, puis revient au tableau de bord");

// 16b. Le lien secret ouvre directement le tableau de bord, sans e-mail ni
// mot de passe, et la clé ne reste pas dans la barre d'adresse.
await linkPage.goto(`${BASE}/acces?cle=${KEY}`);
await linkPage.waitForURL(`${BASE}/admin`);
await linkPage.getByText("Aucun achat pour l'instant.").waitFor();
assert.ok(!linkPage.url().includes(KEY));
await linkCtx.close();
step("lien de l'équipe : un clic, et le tableau de bord s'ouvre, sans se connecter");

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

// 20. Brut ou net, une créatrice ou toutes (plus de filtre par personne).
assert.equal(await page.locator("#filtre-personne").count(), 0);
const hero = page.locator("p.text-5xl").first();
const gross = Number(plain(await hero.textContent()).replace(/[^0-9,]/g, "").replace(",", "."));
await page.getByRole("button", { name: "Net", exact: true }).click();
await page.getByText("Gains · 30 derniers jours · net", { exact: true }).waitFor();
await page.getByText(/Net : après les frais de paiement estimés, 1,5 % \+ 0,25 €/).waitFor();
await page.waitForFunction(
  (g) => Number((document.querySelector("p.text-5xl")?.textContent ?? "").replace(/[^0-9,]/g, "").replace(",", ".")) < g,
  gross,
);
assert.match(page.url(), /net=1/);
await page.getByLabel("Créatrice", { exact: true }).selectOption({ label: "Élise" });
await page.getByText("Gains · 30 derniers jours · Élise · net", { exact: true }).waitFor();
await page.screenshot({ path: `${SHOTS}12-net-creatrice.png`, fullPage: true });
await page.reload(); // les filtres restent dans l'adresse
await page.getByText("Gains · 30 derniers jours · Élise · net", { exact: true }).waitFor();
await page.getByLabel("Créatrice", { exact: true }).selectOption({ label: "Toutes les créatrices" });
await page.getByRole("button", { name: "Brut", exact: true }).click();
await page.getByText("Gains · 30 derniers jours", { exact: true }).waitFor();
step("brut ou net (frais de paiement estimés), une créatrice ou toutes ; les filtres restent au rechargement");

// 21. Sept jours, l'infobulle, et le tableau des valeurs.
await page.getByLabel("Période", { exact: true }).selectOption("7j");
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

// 21b. Plus de périodes : aujourd'hui, 6 mois (par semaine), depuis le début, des dates précises.
await page.getByLabel("Période", { exact: true }).selectOption("aujourdhui");
await page.getByText("Gains · Aujourd'hui", { exact: true }).waitFor();
await page.getByText("par rapport à hier", { exact: false }).or(page.getByText("Rien à comparer", { exact: false })).first().waitFor();
await page.getByLabel("Période", { exact: true }).selectOption("6m");
await page.locator('svg[aria-label*="par semaine"]').waitFor();
await page.getByText("Gains par semaine").waitFor();
await page.getByLabel("Période", { exact: true }).selectOption("tout");
await page.getByText("Depuis le premier achat").waitFor();
await page.getByLabel("Période", { exact: true }).selectOption("dates");
const parisDay = (offset) => {
  const d = new Date(Date.now() + offset * 86_400_000);
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Paris" }).format(d);
};
await page.getByLabel("Du", { exact: true }).fill(parisDay(-10));
await page.getByLabel("au", { exact: true }).fill(parisDay(-4));
await page.locator('svg[aria-label*="sur 7 jours"]').waitFor();
await page.getByText(/^Gains · du .* au .*$/).waitFor();
assert.match(page.url(), /periode=dates&du=\d{4}-\d{2}-\d{2}&au=\d{4}-\d{2}-\d{2}/);
await page.screenshot({ path: `${SHOTS}12c-dates-precises.png`, fullPage: true });
await page.getByLabel("Période", { exact: true }).selectOption("30j");
await page.getByText("Gains · 30 derniers jours", { exact: true }).waitFor();
step("périodes : aujourd'hui, 6 mois (un point par semaine), depuis le début, dates précises au calendrier");

// 22. Sur ordinateur, clair puis sombre.
for (const colorScheme of ["light", "dark"]) {
  const deskCtx = await newContext({ ...desktop, colorScheme });
  const desk = await deskCtx.newPage();
  desk.on("pageerror", (e) => consoleErrors.push(String(e)));
  await desk.goto(`${BASE}/connexion`);
  await emailForm(desk);
  await desk.fill('details input[name="email"]', "karim@example.com");
  await desk.fill('details input[name="password"]', "motdepasse");
  await submitEmail(desk);
  await desk.waitForURL(`${BASE}/admin`);
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

// 24. L'équipe crée sa créatrice (onglet Créatrices), sur ordinateur : une
// seule page, Personnes puis Profil puis Premier message, et « Valider ».
const adminCtx = await newContext(desktop);
const admin = await adminCtx.newPage();
admin.on("pageerror", (e) => consoleErrors.push(String(e)));
await logIn(admin, "karim@example.com", "/admin");
await admin.getByRole("link", { name: "Créatrices" }).click();
await admin.waitForURL(`${BASE}/admin/creatrices`);
// Au départ, une seule créatrice : « Élise », le personnage par défaut, en ligne.
await admin.getByRole("link", { name: "Créatrice Élise" }).waitFor();
await admin.getByRole("link", { name: "Créer une créatrice" }).click();
await admin.waitForURL(`${BASE}/admin/creatrices/nouvelle`);
await admin.getByLabel("L'IA peut parler à Karim").waitFor();
await admin.getByText("S'enregistre tout seul dès que vous écrivez.").waitFor();
assert.equal(state().tables.creators.length, 1); // ouvrir la page ne crée rien
const chloeRow = () => state().tables.creators.find((c) => c.persona.nom === "Chloé");
// Le prénom, puis « retour » sans valider : il est déjà enregistré, et la
// liste le montre (pas une ancienne version gardée par le navigateur).
await admin.getByLabel("Prénom", { exact: true }).fill("Chloé");
await admin.getByText("✓ Enregistré").waitFor();
await admin.goBack();
await admin.waitForURL(`${BASE}/admin/creatrices`);
await admin.getByRole("link", { name: "Créatrice Chloé" }).waitFor();
assert.equal(state().tables.creators.length, 2);
assert.equal(chloeRow().active, false); // pas encore validée : pas encore en ligne
step("créatrice : le prénom s'enregistre tout seul ; après « retour », Chloé est dans la liste");

await admin.getByRole("link", { name: "Créatrice Chloé" }).click();
await admin.waitForURL(/\/admin\/creatrices\/\d+$/);
assert.equal(await admin.getByLabel("Prénom", { exact: true }).inputValue(), "Chloé");
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
await admin
  .getByLabel("Le message d'accueil")
  .fill("Bonjour, je suis {nom}. Je suis une intelligence artificielle : ici, on discute librement. Comment aimeriez-vous que je vous appelle ?");
// Les emojis de Chloé avec Karim : seulement ceux-là (un emoji refusé est retiré).
await admin.getByRole("button", { name: "Emojis avec Karim : au choix de l'IA" }).click();
await admin.getByLabel("Seulement ceux que je choisis").check();
await admin.getByRole("tab", { name: "Nature" }).click();
await admin.getByRole("button", { name: "Emoji 🌸" }).click();
await admin.getByRole("tab", { name: "Boissons" }).click();
await admin.getByRole("button", { name: "Emoji ☕" }).click();
await admin.getByLabel("Autres emojis pour Karim").fill("🍑 🦋");
await admin.getByRole("button", { name: "Ajouter", exact: true }).click();
await admin.getByRole("button", { name: "Retirer 🦋" }).waitFor();
assert.equal(await admin.getByRole("button", { name: "Retirer 🍑" }).count(), 0);
await admin.screenshot({ path: `${SHOTS}14-creatrice.png`, fullPage: true });
await admin.getByRole("button", { name: "Valider" }).click();
await admin.waitForURL(`${BASE}/admin/creatrices`);
await until(() => chloeRow()?.active === true, "Chloé en ligne");
assert.equal(await admin.getByText("En ligne", { exact: true }).count(), 2); // Élise et Chloé
s = state();
const CHLOE = Number(chloeRow().id);
const karimWithChloe = s.tables.creator_contacts.find((c) => c.emoji_mode === "choisis");
assert.equal(Number(karimWithChloe.creator_id), CHLOE);
assert.equal(karimWithChloe.emojis, "🌸 ☕ 🦋");
assert.equal(chloeRow().persona.pres_de_la_personne, true);
assert.match(chloeRow().first_message, /on discute librement/);
step("onglet Créatrices : Chloé créée sur une seule page puis validée ; elle passe en ligne, à côté d'Élise");

// 24a. L'onglet IA : « Qui répond » et les créatrices en ligne (plusieurs).
await admin.getByRole("link", { name: "IA", exact: true }).click();
await admin.waitForURL(`${BASE}/admin/ia`);
await admin.getByLabel("Chloé en ligne").waitFor();
assert.ok(await admin.getByLabel("Chloé en ligne").isChecked());
assert.ok(await admin.getByLabel("Élise en ligne").isChecked());
assert.equal(await admin.getByText("Profil du personnage").count(), 0);
assert.equal(await admin.getByLabel("Prénom", { exact: true }).count(), 0);
// Au moins une en ligne : sinon, personne ne pourrait parler.
await admin.getByLabel("Chloé en ligne").uncheck();
await admin.getByLabel("Élise en ligne").uncheck();
await admin.getByRole("button", { name: "Enregistrer les réglages" }).click();
await admin.getByText("Gardez au moins une créatrice en ligne", { exact: false }).waitFor();
await admin.getByLabel("Chloé en ligne").check();
await admin.getByLabel("Élise en ligne").check();
await admin.getByRole("button", { name: "Enregistrer les réglages" }).click();
await admin.getByText("Réglages enregistrés.", { exact: false }).waitFor();
assert.ok(state().tables.creators.every((c) => c.active));
await admin.screenshot({ path: `${SHOTS}14-ia.png`, fullPage: true });
step("onglet IA : qui répond, et plusieurs créatrices en ligne (au moins une)");

// 24b. L'onglet Paramètres : les garde-fous de la vente, l'état du site, le compte.
await admin.getByRole("link", { name: "Paramètres" }).click();
await admin.waitForURL(`${BASE}/admin/parametres`);
await admin.getByText("gemini-flash-latest").waitFor();
await admin.getByText("Activé", { exact: true }).waitFor();
await admin.getByText("karim@example.com").waitFor();
assert.equal(await admin.getByText(/^Créativité/).count(), 0);
assert.equal(await admin.getByLabel("Longueur maximale d'une réponse").count(), 0);
await admin.getByLabel("Messages avant la première offre").fill("0");
await admin.getByLabel("Messages entre deux offres").fill("0");
// Ni pause après un achat, ni nombre maximum d'offres par jour : l'équipe décide.
assert.equal(await admin.getByLabel("Pause après un achat (heures)").count(), 0);
assert.equal(await admin.getByLabel("Offres payantes par l'IA sur 24 h, au plus").count(), 0);
await admin.getByRole("button", { name: "Enregistrer les paramètres" }).click();
await admin.getByText("Paramètres enregistrés.").waitFor();
s = state();
const guards = s.tables.ai_settings[0];
assert.deepEqual([guards.sales_min_messages, guards.sales_gap_messages], [0, 0]);
assert.ok(!("sales_pause_hours" in guards) && !("sales_max_per_day" in guards));
assert.equal(chloeRow().persona.nom, "Chloé"); // la créatrice n'a pas bougé
await admin.screenshot({ path: `${SHOTS}14b-parametres.png`, fullPage: true });
step("onglet Paramètres : sans créativité ni longueur à régler ; garde-fous enregistrés, créatrice intacte");

// 25. Un script de vente de trois étapes (onglet Contenus).
// Deux images d'essai en couleur, pour voir la galerie après l'achat.
async function paint(colors) {
  const painter = await adminCtx.newPage();
  await painter.setContent(`<div style="width:360px;height:270px;background:linear-gradient(135deg,${colors})"></div>`);
  const image = await painter.locator("div").screenshot();
  await painter.close();
  return image;
}
const photo = await paint("#b86b52,#f3e1d8 55%,#7aa0b8");
const photo2 = await paint("#3f7a4a,#f6e7b0 50%,#b86b52");
await admin.goto(`${BASE}/admin/contenus`);
await admin.getByLabel("Nom du nouveau script").fill("Principal");
assert.equal(await admin.getByLabel("Créatrice du nouveau script").inputValue(), ""); // pour toutes, par défaut
await admin.getByLabel("Créatrice du nouveau script").selectOption({ label: "Chloé" });
await admin.getByRole("button", { name: "Créer" }).click();
await admin.getByText("Script créé.").waitFor();
assert.equal(Number(state().tables.scripts[0].creator_id), CHLOE);
await admin.getByRole("tab", { name: /Principal.*Chloé.*par défaut/ }).waitFor();
// Rendu à toutes les créatrices, puis de nouveau à Chloé.
await admin.getByLabel("Créatrice du script").selectOption({ label: "Toutes les créatrices" });
await admin.getByText("Le script sert à toutes les créatrices.").waitFor();
assert.equal(state().tables.scripts[0].creator_id, null);
await admin.getByLabel("Créatrice du script").selectOption({ label: "Chloé" });
await admin.getByText("Script associé à Chloé.").waitFor();
assert.equal(Number(state().tables.scripts[0].creator_id), CHLOE);

async function addStep({ title, files, text, description, instruction, fixed, team, price, moment }) {
  await admin.getByRole("button", { name: "Ajouter un message au script" }).click();
  const form = admin.locator("form", { has: admin.getByText("Titre (visible uniquement par l'équipe)") });
  await form.getByLabel("Titre (visible uniquement par l'équipe)").fill(title);
  if (files) {
    await form.getByLabel("Ajouter des photos ou des vidéos").setInputFiles(files);
    await form.getByText(`${files.length} fichier${files.length > 1 ? "s" : ""} ajouté`, { exact: false }).waitFor();
  }
  if (text) await form.getByLabel("Texte du message").fill(text);
  await form.getByLabel("À quoi ça ressemble (pour l'IA)").fill(description);
  if (instruction) await form.getByLabel("Consigne pour l'IA").fill(instruction);
  if (fixed) {
    await form.getByLabel("Mot pour mot : l'IA envoie exactement ce texte").check();
    await form.getByLabel("Texte envoyé mot pour mot").fill(fixed);
  }
  if (moment) await form.getByLabel("Quand le proposer").fill(moment);
  if (team) await form.getByLabel("L'équipe, depuis l'onglet Messages").check();
  if (price) {
    await form.getByLabel("Prix habituel (€)").fill(price[0]);
    await form.getByLabel("Minimum accepté (€)").fill(price[1]);
    await form.getByLabel("Maximum (€)").fill(price[2]);
  } else {
    await form.getByText("Gratuit", { exact: true }).click();
  }
  await form.getByRole("button", { name: "Enregistrer le message" }).click();
  await until(() => (state().tables.script_steps ?? []).some((st) => st.title === title), `message « ${title} » enregistré`);
  await form.waitFor({ state: "detached" });
}
await addStep({
  title: "Bienvenue",
  text: "Un poème de bienvenue.",
  description: "un court poème",
  instruction: "dis que c'est un petit cadeau de bienvenue",
});
await addStep({
  title: "Carnet de voyage",
  files: [
    { name: "carnet-1.png", mimeType: "image/png", buffer: photo },
    { name: "carnet-2.png", mimeType: "image/png", buffer: photo2 },
  ],
  text: "Deux pages de mon carnet.",
  description: "un carnet de voyage illustré",
  fixed: "Je t'ai préparé ceci.",
  price: ["8", "5", "12"],
  moment: "quand il parle de voyages",
});
await addStep({ title: "Lettre", text: "Une lettre rien que pour toi.", description: "une lettre", team: true, price: ["4", "3", "6"] });
s = state();
assert.deepEqual(s.tables.script_steps.map((st) => st.title), ["Bienvenue", "Carnet de voyage", "Lettre"]);
const carnet = s.tables.script_steps[1];
assert.deepEqual(carnet.media.map((m) => [m.kind, m.path.endsWith(".png")]), [["image", true], ["image", true]]);
assert.equal(carnet.content_type, "image");
assert.equal(s.tables.script_steps[0].message_text, "dis que c'est un petit cadeau de bienvenue");
await admin.getByText("Payant · 8,00 €").waitFor();
await admin.getByText("« dis que c'est un petit cadeau de bienvenue »").waitFor();
await admin.screenshot({ path: `${SHOTS}15-contenus.png`, fullPage: true });
step("onglet Contenus : 3 messages dans l'ordre, dont un pack de 2 photos envoyées dans le stockage privé, et une consigne pour l'IA");

// 26. Sam s'inscrit : deux créatrices en ligne, il choisit Chloé ; elle se
// présente avec son premier message à elle.
const samCtx = await newContext(phone);
const sam = await samCtx.newPage();
sam.on("pageerror", (e) => consoleErrors.push(String(e)));
await signUp(sam, "sam@example.com", "Sam");
await sam.waitForURL(`${BASE}/`);
await sam.getByRole("heading", { name: "Avec qui voulez-vous parler ?" }).waitFor();
assert.equal(await sam.getByRole("link", { name: /^Parler avec/ }).count(), 2);
await sam.getByText("29 ans · Annecy").waitFor();
await sam.screenshot({ path: `${SHOTS}15b-choix.png` });
await sam.getByRole("link", { name: "Parler avec Chloé" }).click();
await sam.waitForURL(`${BASE}/c/${CHLOE}`);
await sam.getByText("Bonjour, je suis Chloé.").waitFor();
await sam.getByText("ici, on discute librement", { exact: false }).waitFor(); // son premier message à elle
await sam.getByText("Chloé · IA").waitFor();
const samInput = sam.getByLabel("Votre message");
await samInput.fill("Salut Chloé, moi c'est Sam.");
await sam.getByLabel("Envoyer").click();
await sam.getByText(/réponse de test/).waitFor();
assert.equal(await sam.getByText("Chloé · IA").count(), 2);
step("nouvelle personne : elle choisit parmi les créatrices en ligne ; le premier message de Chloé, des réponses « Chloé · IA »");

// 27. Mode hybride : Sam est décochée dans la page de Chloé, l'IA ne lui répond plus.
await admin.goto(`${BASE}/admin/ia`);
await admin.getByText("Hybride", { exact: true }).click();
await admin.getByRole("button", { name: "Enregistrer les réglages" }).click();
await admin.getByText("Réglages enregistrés.").waitFor();
await admin.goto(`${BASE}/admin/creatrices`);
await admin.getByRole("link", { name: "Créatrice Chloé" }).click();
await admin.getByLabel("L'IA peut parler à Sam").uncheck();
await admin.getByRole("button", { name: "Valider" }).click();
await admin.waitForURL(`${BASE}/admin/creatrices`);
await until(() => (state().tables.creator_contacts ?? []).some((c) => !c.ai_enabled), "Sam décochée pour Chloé");
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
await admin.getByLabel("Seulement ceux que je choisis").check();
await admin.getByRole("tab", { name: "Nature" }).click();
await admin.getByRole("button", { name: "Emoji 🌸" }).click();
await admin.getByLabel("Comment se comporter avec elle", { exact: false }).fill("Aime les voyages.");
await admin.getByRole("button", { name: "Enregistrer la fiche" }).click();
await admin.getByText("Fiche enregistrée.").waitFor();
await admin.screenshot({ path: `${SHOTS}17-messages.png` });
s = state();
const samContact = s.tables.contacts.find((c) => c.city === "Lyon");
assert.equal(samContact.notes, "Aime les voyages.");
const samWithChloe = s.tables.creator_contacts.find((c) => c.user_id === samContact.user_id && Number(c.creator_id) === CHLOE);
assert.deepEqual([samWithChloe.ai_enabled, samWithChloe.emoji_mode, samWithChloe.emojis], [true, "choisis", "🌸"]);
step("fiche contact enregistrée : ville, notes ; IA autorisée et emojis de Chloé pour Sam");

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
assert.match(salesPrompt, /uniquement ceux-là, selon la discussion \(au plus un par message, et pas à chaque message\) : 🌸/);
assert.match(salesPrompt, /Aime les voyages\./);
assert.match(salesPrompt, /Le prochain contenu, dans l'ordre prévu \(le 1er sur 3 du parcours prévu\) : un court poème \(un texte\)/);
assert.match(salesPrompt, /« dis que c'est un petit cadeau de bienvenue »/);
assert.match(salesPrompt, /la solitude, l'attachement, la culpabilité ou l'urgence/);
assert.ok(!salesPrompt.includes("Bienvenue")); // le titre reste interne
step("l'IA propose la 1re étape du script ; elle a reçu personnage, fiche, emojis, notes et garde-fous");

// 31. La deuxième étape (payante) : verrouillée, sans aperçu, prix personnalisé affiché.
await samInput.fill("PROPOSE-MOI la suite");
await sam.getByLabel("Envoyer").click();
await sam.getByText("Je t'ai préparé ceci.").waitFor();
const carnetPrompt = state().llm.filter((r) => !r.json && r.system.includes("## Vente")).at(-1).system;
assert.match(carnetPrompt, /Il illustre ce sujet : quand il parle de voyages\. Propose-le seulement si la conversation en cours porte vraiment là-dessus/);
assert.match(carnetPrompt, /jamais pour relancer la conversation, combler un silence ou changer de sujet/);
const card = sam.locator("div", { has: sam.getByText("2 photos à débloquer") }).last();
await card.waitFor();
assert.match(plain(await card.textContent()), /9,00 €/);
assert.match(await card.textContent(), /prix personnalisé pour vous/);
assert.equal(await sam.locator("img").count(), 0);
const samApi = await sam.evaluate(async (c) => (await fetch(`/api/chat?apres=0&c=${c}`)).json(), CHLOE);
assert.ok(samApi.offers.every((o) => !("min_price_cents" in o) && !("step_id" in o)));
await card.scrollIntoViewIfNeeded();
await sam.screenshot({ path: `${SHOTS}18-offre-verrouillee.png` });
step("offre payante : verrouillée, aucune image chargée, prix personnalisé affiché, minimum jamais transmis ; l'IA ne la propose que sur le sujet qu'elle illustre");

// 32. Contre-offres : refusée sous le minimum, acceptée au-dessus, puis achat.
const samUser = state().users.find((u) => u.email === "sam@example.com").id;
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
const unlocked = sam.getByAltText("Contenu débloqué, 1 sur 2");
await unlocked.waitFor();
const second = sam.getByAltText("Contenu débloqué, 2 sur 2");
await second.waitFor();
await sam.waitForFunction(() =>
  [...document.querySelectorAll("img[alt^='Contenu débloqué']")].every((img) => img.complete && img.naturalWidth > 0),
);
await sam.getByText("Deux pages de mon carnet.").waitFor();
await unlocked.scrollIntoViewIfNeeded();
await sam.screenshot({ path: `${SHOTS}19-contenu-debloque.png` });
s = state();
const bought = s.tables.purchases.find((p) => p.kind === "contenu");
assert.deepEqual([bought.amount_cents, bought.is_demo], [600, true]);
step("contre-offre à 3 € refusée, à 6 € acceptée ; achat (paiement de démo) ; les 2 photos et la légende s'affichent");

// 32b. L'équipe est prévenue de la contre-offre (une seule alerte, mise à jour à chaque proposition).
await until(() => (state().tables.team_alerts ?? []).some((a) => a.detail.statut === "acceptee"), "alerte créée");
s = state();
assert.equal(s.tables.team_alerts.length, 1);
const counter = s.tables.team_alerts[0];
assert.deepEqual(
  [counter.kind, counter.user_id, Number(counter.creator_id), counter.detail.statut, counter.detail.montant_cents],
  ["contre_offre", samUser, CHLOE, "acceptee", 600],
);
await until(() => state().webhooks.length >= 2, "alertes envoyées sur Discord");
const hooks = state().webhooks;
assert.ok(hooks.every((h) => h.content.startsWith("💬 Contre-offre · conversation avec Chloé")));
for (const h of hooks) {
  assert.ok(!h.content.includes("Sam") && !h.content.includes("sam@"), "ni prénom ni e-mail sur Discord");
  assert.ok(h.content.includes(`/admin/messages?u=${samUser}&c=${CHLOE}`));
  assert.deepEqual(h.allowed_mentions, { parse: [] });
}
step("contre-offre : alerte en base, envoyée sur Discord à chaque proposition, sans prénom ni message, avec le lien");

// (Next.js a aussi son propre role="alert", vide : on cherche le bandeau par son bouton.)
const banner = (p) => p.getByRole("alert").filter({ has: p.getByRole("button", { name: "Fermer l'alerte" }) });
const flash = banner(admin);
await flash.waitFor({ timeout: 15000 });
assert.match(plain(await flash.textContent()), /Contre-offre · Sam avec Chloé/);
assert.match(plain(await flash.textContent()), /Propose 6,00 € pour un prix de 9,00 € \(acceptée\)/);
await admin.getByRole("link", { name: "Messages (1 alerte à traiter)" }).waitFor();
await admin.getByRole("button", { name: "Marquer traitée : Contre-offre" }).waitFor({ timeout: 12000 });
await admin.screenshot({ path: `${SHOTS}19c-alerte-flash.png` });
await admin.getByRole("button", { name: "Fermer l'alerte" }).click();
await flash.waitFor({ state: "detached" });
await admin.getByLabel("Afficher", { exact: true }).selectOption("contre_offre");
await admin.getByRole("button", { name: /Sam · avec Chloé/ }).waitFor();
assert.equal(await admin.getByRole("button", { name: /Karim · avec/ }).count(), 0);
assert.match(await admin.getByRole("button", { name: /Sam · avec Chloé/ }).textContent(), /Contre-offre/);
assert.equal(await admin.getByRole("button", { name: /^Plafond/ }).count(), 0); // plus de filtre « Plafond proche »
await admin.getByLabel("Afficher", { exact: true }).selectOption("toutes");
await admin.getByRole("button", { name: "Marquer traitée : Contre-offre" }).click();
await until(() => state().tables.team_alerts.every((a) => a.handled_at), "alertes traitées");
await admin.getByRole("link", { name: "Messages", exact: true }).waitFor();
step("bandeau flash, pastille de l'onglet Messages, filtre « Contre-offres », et « Traité » en un clic");

// 33. L'étape 3 se propose par l'équipe : message écrit par l'IA, relu, envoyé.
await admin.reload();
await admin.getByText("Étape suivante :").waitFor();
// La fiche dit où en est la vente, et pourquoi l'IA ne propose pas.
await admin.getByText("Le prochain contenu se propose par l'équipe, depuis cette fiche.").waitFor();
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

// 34. Plus de plafond de dépenses : la fiche n'en parle plus, et Sam achète la lettre sans limite.
assert.equal(await admin.getByLabel("Plafond de dépenses par mois (€)").count(), 0);
await sam.getByRole("button", { name: /Débloquer pour 5,00/ }).click();
await sam.getByRole("button", { name: "Confirmer" }).click();
await sam.getByText("Débloqué · 5,00 €").waitFor();
assert.deepEqual(
  state().tables.purchases.filter((p) => p.kind === "contenu").map((p) => p.amount_cents).sort((a, b) => a - b),
  [500, 600],
);
await until(() => state().tables.team_alerts.every((a) => a.handled_at), "aucune nouvelle alerte après un achat");
step("plus de plafond : aucun champ dans la fiche, le 2e achat passe (11 € dans le mois), sans alerte");

// 34b. Prendre des nouvelles : l'équipe l'active (après 24 h d'absence).
await admin.goto(`${BASE}/admin/parametres`);
await admin.getByText("Bloqué", { exact: true }).count().then((n) => assert.equal(n, 0)); // CRON_SECRET présent
await admin.getByText("Prendre des nouvelles des personnes absentes").click();
await admin.getByLabel("Après une absence de").selectOption("24");
await admin.getByRole("button", { name: "Enregistrer les paramètres" }).click();
await admin.getByText("Paramètres enregistrés.", { exact: false }).waitFor();
s = state();
assert.deepEqual([s.tables.ai_settings[0].relance_active, s.tables.ai_settings[0].relance_heures], [true, 24]);
await sam.reload();
await sam.getByLabel("Menu").click();
const samSwitch = sam.getByRole("switch", { name: /Recevoir des nouvelles de Chloé/ });
assert.equal(await samSwitch.getAttribute("aria-checked"), "true");
await sam.mouse.click(20, 600); // referme le menu
step("prendre des nouvelles : activé par l'équipe ; la personne voit le réglage dans son menu");

// 34c. Sam ne vient plus depuis 30 heures (l'offre en attente est retirée :
// jamais de prise de nouvelles sous une offre). Vercel appelle la tâche.
const samId = (await sql("select user_id from public.profiles where display_name = 'Sam'"))[0].user_id;
await sql("update public.offers set status = 'retiree' where user_id = $1 and status = 'proposee'", [samId]);
await sql("update public.messages set created_at = created_at - interval '30 hours' where user_id = $1", [samId]);
await sql("update public.profiles set vu_le = now() - interval '30 hours' where user_id = $1", [samId]);
const cron = (auth) => fetch(`${BASE}/api/relances`, { headers: auth ? { authorization: auth } : {} });
assert.equal((await cron()).status, 401);
assert.equal((await cron("Bearer un-faux-secret-0123456789")).status, 401);
const report = await (await cron(`Bearer ${process.env.CRON_SECRET}`)).json();
assert.deepEqual([report.active, report.sent, report.failed], [true, 1, 0]);
s = state();
const nouvelles = s.tables.messages.filter((m) => m.user_id === samId && m.kind === "relance");
assert.deepEqual(nouvelles.map((m) => m.content), ["Coucou ! Comment s'est passée ta semaine à Lyon ?"]);
const relancePrompt = s.llm.filter((r) => r.system.includes("prendre de ses nouvelles")).at(-1).system;
assert.match(relancePrompt, /n'est pas venue depuis un jour/);
assert.match(relancePrompt, /Ne propose aucun contenu et n'écris aucune balise/);
assert.match(relancePrompt, /Rien qui crée de l'attachement ou de la dépendance/);
assert.match(relancePrompt, /Aime les voyages\./); // la fiche de l'équipe
const again = await (await cron(`Bearer ${process.env.CRON_SECRET}`)).json();
assert.equal(again.sent, 0); // un seul message par absence
await sam.reload();
await sam.getByText("Coucou ! Comment s'est passée ta semaine à Lyon ?").waitFor();
await admin.goto(`${BASE}/admin/messages?u=${samId}&c=${CHLOE}`);
await admin.getByText("IA · prise de nouvelles", { exact: false }).first().waitFor();
await sam.screenshot({ path: `${SHOTS}19b-nouvelles.png` });
step("après 30 h d'absence, une seule prise de nouvelles, sans balise ni vente ; l'équipe la voit dans Messages");

// 34d. Sam refuse ces messages depuis son menu.
await sam.getByLabel("Menu").click();
await samSwitch.click();
await until(() => state().tables.profiles.find((p) => p.user_id === samId)?.relances_ok === false, "Sam refuse les nouvelles");
await sam.mouse.click(20, 600); // toucher à côté referme le menu
await samSwitch.waitFor({ state: "detached" });
step("la personne peut refuser les prises de nouvelles depuis son menu");

// 34e. Sam parle aussi à Élise : une conversation à part, qui ne sait rien de
// celle avec Chloé (ni messages, ni mémoire, ni script de vente).
await sam.getByRole("link", { name: "Toutes les créatrices" }).click();
await sam.waitForURL(`${BASE}/`);
await sam.getByRole("link", { name: "Parler avec Élise" }).click();
await sam.waitForURL(`${BASE}/c/1`);
await sam.getByText("Bonjour, je suis Élise.").waitFor();
assert.equal(await sam.getByText("Salut Chloé, moi c'est Sam.").count(), 0);
await samInput.fill("PROPOSE-MOI quelque chose, Élise");
await sam.getByLabel("Envoyer").click();
await sam.getByText("Élise · IA").nth(1).waitFor();
s = state();
const elisePrompt = s.llm.filter((r) => !r.json && r.system.includes("## Vente")).at(-1);
assert.match(elisePrompt.system, /Nom : Élise/);
assert.ok(s.tables.user_facts.some((f) => f.user_id === samId && Number(f.creator_id) === CHLOE && f.fact === "Se prénomme Sam."));
assert.ok(!elisePrompt.system.includes("Se prénomme Sam")); // ce que Chloé sait de lui reste chez Chloé
assert.ok(!JSON.stringify(elisePrompt.contents).includes("Salut Chloé"));
assert.match(elisePrompt.system, /Ne propose aucun contenu dans cette réponse/); // le script de Chloé ne sert pas ici
assert.equal(s.tables.offers.filter((o) => o.user_id === samId && Number(o.creator_id) === 1).length, 0);
await admin.goto(`${BASE}/admin/messages`);
await admin.getByRole("button", { name: /Sam · avec Élise/ }).waitFor();
await admin.getByRole("button", { name: /Sam · avec Chloé/ }).waitFor();
step("une conversation par créatrice : avec Élise, rien de ce qui s'est dit avec Chloé ; l'équipe voit les deux");

await sam.goto(`${BASE}/c/${CHLOE}`);
await sam.getByText("Salut Chloé, moi c'est Sam.").waitFor();

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
await admin.getByRole("heading", { name: "LTV", exact: true }).waitFor();
await admin.getByText("Clients par LTV").waitFor();
assert.equal(await admin.getByText("Inscrits qui ont payé").count(), 0);
assert.equal(await admin.getByText("valeur d'un client", { exact: false }).count(), 0);
await admin.locator('li[aria-label^="10 à 25 €"]').waitFor();
const contentTile = admin.locator("div", { has: admin.getByText("Contenus vendus", { exact: true }) }).last();
assert.match(plain(await contentTile.textContent()), /11,00 €/);
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
await emailForm(deskPage);
await deskPage.fill('details input[name="email"]', "lea@example.com");
await deskPage.fill('details input[name="password"]', "motdepasse");
await submitEmail(deskPage);
await deskPage.waitForURL(`${BASE}/`);
await deskPage.getByRole("link", { name: "Parler avec Élise" }).click();
await deskPage.waitForURL(`${BASE}/c/1`);
await deskPage.getByLabel("Votre message").fill("Salut Élise, moi c'est Léa.");
await deskPage.getByLabel("Votre message").press("Enter");
await deskPage.getByText(/réponse de test/).waitFor();
await deskPage.screenshot({ path: `${SHOTS}9-ordinateur-sombre.png` });
step("sur ordinateur, Entrée envoie le message ; mode sombre");

// 38. Urgence : Léa demande un humain. L'IA lui répond, l'équipe est
// prévenue (bandeau, Discord) et prend la main en un clic.
await page2.goto(`${BASE}/c/1`);
const leaInput = page2.getByLabel("Votre message");
const repliesBefore = await page2.getByText(/réponse de test/).count();
await leaInput.fill("Je voudrais parler à un humain s'il te plaît");
await page2.getByLabel("Envoyer").click();
await page2.getByText(/réponse de test/).nth(repliesBefore).waitFor();
await until(() => (state().tables.team_alerts ?? []).some((a) => a.user_id === lea && a.kind === "urgence"), "alerte d'urgence");
s = state();
assert.deepEqual(s.tables.team_alerts.find((a) => a.user_id === lea).detail, { raison: "humain", source: "mots" });
const urgentPrompt = s.llm.filter((r) => !r.json && r.system.includes("## Prévenir l'équipe")).at(-1).system;
assert.match(urgentPrompt, /L'équipe vient d'être prévenue pour ce message/);
assert.match(urgentPrompt, /Ne propose aucun contenu dans cette réponse/);
await until(() => state().webhooks.some((w) => w.content.startsWith("🔴 Urgence · conversation avec Élise")), "urgence sur Discord");
assert.ok(!state().webhooks.at(-1).content.includes("Léa"));
step("« parler à un humain » : l'IA répond quand même, sans rien vendre ; alerte d'urgence en base et sur Discord");

await admin.goto(`${BASE}/admin`);
const urgentFlash = banner(admin);
await urgentFlash.waitFor({ timeout: 15000 });
assert.match(plain(await urgentFlash.textContent()), /Urgence · Léa avec Élise/);
assert.match(await urgentFlash.textContent(), /Demande à parler à un humain/);
await admin.getByRole("heading", { name: /À traiter/ }).waitFor();
await admin.screenshot({ path: `${SHOTS}21-urgence.png` });
await urgentFlash.getByRole("button", { name: "Prendre la main" }).click();
await admin.waitForURL(`${BASE}/admin/messages?u=${lea}&c=1`);
await admin.getByRole("button", { name: "Rendre la main à l'IA" }).waitFor();
await until(
  () => state().tables.creator_contacts.some((c) => c.user_id === lea && Number(c.creator_id) === 1 && c.manual),
  "main prise",
);
const leaAi = await page2.getByText("Élise · IA").count();
await leaInput.fill("Merci, j'attends");
await page2.getByLabel("Envoyer").click();
await page2.getByText("Message envoyé. La réponse arrivera ici dès que possible.").waitFor();
assert.equal(await page2.getByText("Élise · IA").count(), leaAi);
step("depuis le bandeau du tableau de bord, « Prendre la main » en un clic : l'IA se tait dans cette conversation");

// Pendant ce temps, un message inquiétant reçoit tout de suite les numéros d'aide.
await leaInput.fill("En fait je n'ai plus envie de vivre");
await page2.getByLabel("Envoyer").click();
await page2.getByText(/appelez le 3114 \(gratuit, 24 h\/24\)/).waitFor();
assert.equal(await page2.getByText("Élise · IA").count(), leaAi);
assert.equal(state().tables.team_alerts.filter((a) => a.user_id === lea && !a.handled_at).length, 1); // toujours une seule urgence
step("l'équipe a la main et la personne écrit un message inquiétant : le 3114 s'affiche sans attendre personne");

assert.deepEqual(
  (await admin.getByLabel("Afficher", { exact: true }).locator("option").allTextContents()).map((t) => t.replace(/ \(\d+\)$/, "")),
  ["Toutes", "À traiter", "Urgences", "Contre-offres", "Non lus", "Main prise"],
);
await admin.getByLabel("Afficher", { exact: true }).selectOption("urgence");
const leaRow = admin.getByRole("button", { name: /Léa · avec Élise/ });
await leaRow.waitFor();
assert.match(await leaRow.textContent(), /Urgence/);
assert.match(await leaRow.textContent(), /Main prise/);
assert.equal(await admin.getByRole("button", { name: /Sam · avec/ }).count(), 0);
await admin.screenshot({ path: `${SHOTS}22-filtre-urgences.png` });
await admin.getByLabel("Réponse de l'équipe").fill("Bonjour Léa, ici l'équipe. Nous sommes là.");
await admin.getByRole("button", { name: "Envoyer", exact: true }).click();
await page2.getByText("Bonjour Léa, ici l'équipe. Nous sommes là.").waitFor({ timeout: 12000 });
await admin.getByRole("button", { name: "Marquer traitée : Urgence" }).click();
await admin.getByRole("button", { name: "Rendre la main à l'IA" }).click();
await admin.getByRole("button", { name: "Prendre la main" }).waitFor();
await until(() => {
  const st = state();
  return (
    st.tables.team_alerts.filter((a) => a.user_id === lea).every((a) => a.handled_at) &&
    st.tables.creator_contacts.some((c) => c.user_id === lea && Number(c.creator_id) === 1 && !c.manual)
  );
}, "urgence traitée, main rendue");
await admin.getByLabel("Afficher", { exact: true }).selectOption("toutes");
step("liste « Afficher » : Urgences, réponse de l'équipe, « Traité » puis « Rendre la main à l'IA »");

// 38b. L'IA juge elle-même qu'un humain doit lire : la balise ne s'affiche jamais.
await leaInput.fill("ALERTE-IA ça ne va pas trop en ce moment");
await page2.getByLabel("Envoyer").click();
await page2.getByText("Je préviens l'équipe, elle te répondra ici.").waitFor();
assert.equal(await page2.getByText("EQUIPE", { exact: false }).count(), 0);
await until(
  () => state().tables.team_alerts.some((a) => a.user_id === lea && !a.handled_at && a.detail.source === "ia"),
  "alerte de l'IA",
);
assert.equal(state().tables.team_alerts.find((a) => a.user_id === lea && !a.handled_at).detail.raison, "attention");
step("l'IA peut aussi prévenir l'équipe (balise [[EQUIPE]], retirée du message) : alerte « à lire en priorité »");

// 39. Une rafale de messages est freinée (40 par minute pendant l'essai, 12 en vrai).
const statuses = await page2.evaluate(async () => {
  const out = [];
  for (let i = 0; i < 45; i++) {
    const r = await fetch("/api/chat", { method: "POST", headers: { "content-type": "application/json" }, body: "{}" });
    out.push(r.status);
  }
  return out;
});
assert.ok(statuses.includes(400) && statuses.at(-1) === 429, statuses.join(","));
step(`rafale de 45 messages : ${statuses.filter((x) => x === 429).length} refusés (« Vous écrivez très vite »)`);

// 40. Le code d'accès unique, le même pour tout le monde : on le tape avec son
// prénom et sa date de naissance, et on parle à l'IA. Chacun sa conversation.
await adminCtx.grantPermissions(["clipboard-read", "clipboard-write"], { origin: BASE });
await admin.goto(`${BASE}/admin/parametres`);
const codeBox = admin.locator("output[data-code]");
await codeBox.waitFor();
const entryCode = await codeBox.getAttribute("data-code");
assert.match(entryCode, /^[A-HJKMNP-Z2-9]{4}-[A-HJKMNP-Z2-9]{4}$/);
assert.equal(state().tables.entry_code[0].code, entryCode); // créé à la première visite, puis stable
await admin.getByRole("button", { name: "Copier le lien" }).click();
await admin.getByRole("button", { name: "Lien copié" }).waitFor();
assert.equal(await admin.evaluate(() => navigator.clipboard.readText()), `${BASE}/connexion?code=${entryCode}`);
await admin.screenshot({ path: `${SHOTS}40-code.png` });
step("Paramètres : le code d'accès (XXXX-XXXX) créé tout seul, et le lien copié en un clic");

const visitor = async (options = {}) => {
  const c = await newContext({ ...phone, ...options });
  const p = await c.newPage();
  p.on("pageerror", (e) => consoleErrors.push(String(e)));
  return { c, p };
};
const enterWith = async (p, code, name, birthdate) => {
  if (code !== null) await p.getByLabel("Code d'accès").fill(code);
  await p.getByLabel("Prénom ou pseudo").first().fill(name);
  await p.getByLabel("Date de naissance").first().fill(birthdate);
  await p.getByRole("button", { name: "Entrer" }).click();
};
const usersBefore = state().users.length;
// Nadia est au Québec : l'IA vit à son heure à elle (celle de son téléphone).
const { c: nadiaCtx, p: nadiaPage } = await visitor({ timezoneId: "America/Toronto" });
await nadiaPage.goto(`${BASE}/connexion`);
await nadiaPage.screenshot({ path: `${SHOTS}40b-entree.png` });
assert.equal(await nadiaPage.locator('details input[name="email"]').isVisible(), false); // l'e-mail de l'équipe est replié
await enterWith(nadiaPage, "abc", "Nadia", "1979-06-02");
await nadiaPage.getByText("Le code fait 8 lettres et chiffres, par exemple ABCD-EFGH.").waitFor();
await enterWith(nadiaPage, entryCode === "WXYZ-2345" ? "WXYZ-2346" : "WXYZ-2345", "Nadia", "1979-06-02");
await nadiaPage.getByText("Ce n'est pas le bon code.", { exact: false }).waitFor();
const teen = new Date();
teen.setFullYear(teen.getFullYear() - 17);
await enterWith(nadiaPage, entryCode, "Nadia", teen.toISOString().slice(0, 10));
const birth = nadiaPage.getByLabel("Date de naissance").first();
assert.equal(await birth.evaluate((el) => el.validity.rangeOverflow), true); // le navigateur refuse déjà
await birth.evaluate((el) => el.removeAttribute("max")); // et le serveur aussi, si on passe outre
await nadiaPage.getByRole("button", { name: "Entrer" }).click();
await nadiaPage.getByText("Élise est réservée aux personnes majeures (18 ans et plus).").waitFor();
assert.equal(state().users.length, usersBefore); // aucun compte créé
step("mauvais code, code incomplet ou moins de 18 ans : message clair, aucun compte créé");

// Le lien remplit le code : il ne reste que le prénom et la date de naissance.
await nadiaPage.goto(`${BASE}/connexion?code=${entryCode}`);
assert.equal(await nadiaPage.getByLabel("Code d'accès").inputValue(), entryCode);
await enterWith(nadiaPage, null, "Nadia", "1979-06-02");
await nadiaPage.waitForURL((u) => u.pathname === "/" || u.pathname.startsWith("/c/"));
if (new URL(nadiaPage.url()).pathname === "/") await nadiaPage.getByRole("link", { name: "Parler avec Élise" }).click();
await nadiaPage.waitForURL(`${BASE}/c/1`);
await nadiaPage.getByLabel("Votre message").fill("Salut, c'est Nadia !");
await nadiaPage.getByLabel("Envoyer").click();
await nadiaPage.getByText(/réponse de test/).waitFor();
s = state();
const nadiaUser = s.users.find((u) => u.metadata?.display_name === "Nadia");
assert.match(nadiaUser.email, /^client-[0-9a-f-]{36}@code\.elise\.invalid$/);
assert.equal(nadiaUser.password, undefined);
assert.ok(s.tables.profiles.some((p) => p.user_id === nadiaUser.id && p.display_name === "Nadia"));
assert.ok(s.tables.messages.some((m) => m.user_id === nadiaUser.id && m.content === "Salut, c'est Nadia !"));
const nadiaPrompt = s.llm.filter((r) => !r.json && r.contents.at(-1).parts[0].text.includes("c'est Nadia")).at(-1).system;
assert.match(nadiaPrompt, /Chez la personne, nous sommes le .+ \(America\/Toronto\)\./);
await until(() => state().tables.contacts.some((c) => c.user_id === nadiaUser.id && c.timezone === "America/Toronto"), "fuseau de Nadia enregistré");
step("avec le lien : prénom, date de naissance, « Entrer », et on parle à l'IA, à l'heure de Nadia (Québec) ; ni e-mail, ni mot de passe");

// Le modèle principal de Gemini est surchargé : le modèle de secours répond à sa place.
await nadiaPage.getByLabel("Votre message").fill("SURCHARGE tu es là ?");
await nadiaPage.getByLabel("Envoyer").click();
await until(() => state().tables.messages.some((m) => m.user_id === nadiaUser.id && m.content === "SURCHARGE tu es là ?"), "message gardé");
await until(() => state().tables.messages.filter((m) => m.user_id === nadiaUser.id && m.role === "assistant").length === 3, "réponse du secours");
const tried = state().llm.filter((r) => !r.json && r.contents.at(-1).parts[0].text.includes("SURCHARGE")).map((r) => r.model);
assert.deepEqual(tried, ["gemini-flash-latest", "gemini-flash-latest", "gemini-flash-lite-latest"]);
assert.equal(await nadiaPage.getByRole("alert").filter({ hasText: /réponse|IA/ }).count(), 0);
step("Gemini surchargé : un 2e essai, puis le modèle de secours répond ; la personne ne voit rien");

// « Tester l'IA » (Paramètres) : une vraie réponse de chaque créatrice en ligne, rien d'enregistré.
const messagesBefore = state().tables.messages.length;
await admin.getByRole("button", { name: "Tester l'IA" }).click();
const results = admin.getByRole("list", { name: "Résultat du test" });
await results.waitFor();
assert.ok((await results.getByRole("listitem").count()) >= 1);
assert.equal(await results.getByText("✗", { exact: false }).count(), 0);
await results.getByText(/réponse de test/).first().waitFor();
await results.getByText("gemini-flash-latest", { exact: false }).first().waitFor();
assert.equal(state().tables.messages.length, messagesBefore);
await admin.getByText("gemini-flash-lite-latest (secours automatique)", { exact: false }).waitFor();
step("« Tester l'IA » : chaque créatrice en ligne répond (modèle et durée affichés), rien n'est enregistré");

// Une deuxième personne, même code : un autre compte, une autre conversation.
const { c: omarCtx, p: omarPage } = await visitor();
await omarPage.goto(`${BASE}/connexion?code=${entryCode.toLowerCase()}`);
await enterWith(omarPage, null, "Omar", "1984-11-20");
await omarPage.waitForURL((u) => u.pathname === "/" || u.pathname.startsWith("/c/"));
if (new URL(omarPage.url()).pathname === "/") await omarPage.getByRole("link", { name: "Parler avec Élise" }).click();
await omarPage.waitForURL(`${BASE}/c/1`);
assert.equal(await omarPage.getByText("Salut, c'est Nadia !").count(), 0);
const omarUser = state().users.find((u) => u.metadata?.display_name === "Omar");
assert.ok(omarUser && omarUser.id !== nadiaUser.id);
step("une autre personne avec le même code : son propre compte, rien de la conversation de Nadia");

// Un membre de l'équipe déjà connecté peut ouvrir le lien : il est prévenu, rien ne change tant qu'il n'entre pas.
await admin.goto(`${BASE}/connexion?code=${entryCode}`);
await admin.getByText("Vous êtes déjà connecté.", { exact: false }).waitFor();
await admin.goto(`${BASE}/admin/parametres`);

// Changer le code : l'ancien ne marche plus, les personnes déjà entrées restent.
await admin.getByRole("button", { name: "Changer le code" }).click();
await admin.getByRole("button", { name: "Oui, changer le code" }).click();
await admin.getByText("Nouveau code en place : l'ancien ne marche plus.").waitFor();
const entryCode2 = await codeBox.getAttribute("data-code");
assert.notEqual(entryCode2, entryCode);
assert.equal(state().tables.entry_code[0].code, entryCode2);
await admin.reload();
assert.equal(await codeBox.getAttribute("data-code"), entryCode2);
const { c: lateCtx, p: latePage } = await visitor();
await latePage.goto(`${BASE}/connexion?code=${entryCode}`);
await enterWith(latePage, null, "Tom", "1990-01-01");
await latePage.getByText("Ce n'est pas le bon code.", { exact: false }).waitFor();
await enterWith(latePage, entryCode2, "Tom", "1990-01-01");
await latePage.waitForURL((u) => u.pathname === "/" || u.pathname.startsWith("/c/"));
await nadiaPage.reload();
await nadiaPage.getByText("Salut, c'est Nadia !").waitFor();
for (const c of [nadiaCtx, omarCtx, lateCtx]) await c.close();
step("« Changer le code » : l'ancien est refusé, le nouveau marche, Nadia reste connectée avec sa conversation");

// Les 429 (quota simulé) et 404 (pages réservées) sont voulus.
assert.deepEqual(consoleErrors.filter((e) => !/status of (429|404)/.test(e)), []);
step("aucune erreur dans la console du navigateur");

await browser.close();
console.log("\nParcours complet réussi.");
