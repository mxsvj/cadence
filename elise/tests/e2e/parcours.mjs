// Parcours complet d'un utilisateur, sur téléphone puis sur ordinateur, contre
// le serveur local branché sur les faux Supabase et Gemini (faux-services.mjs).
// Se lance avec lancer.mjs (npm run test:e2e).
import { chromium } from "playwright-core";
import { readFileSync, mkdirSync } from "node:fs";
import assert from "node:assert/strict";

const BASE = process.env.E2E_BASE;
const SHOTS = `${process.env.E2E_SHOTS}/`;
mkdirSync(SHOTS, { recursive: true });
const state = () => JSON.parse(readFileSync(process.env.E2E_STATE, "utf8"));
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
const ctx = await browser.newContext(phone);
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

// 3. Inscription.
await page.getByText("Première visite ? Créer un compte").click();
await page.fill('input[name="email"]', "karim@example.com");
await page.fill('input[name="password"]', "motdepasse");
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
await page.screenshot({ path: `${SHOTS}3-echange.png` });
step("message envoyé, réponse d'Élise à gauche, sans le gras Markdown");

// 6. La fiche : nouveaux faits, sans doublon ni donnée sensible.
await until(() => state().tables.user_facts.length >= 3, "faits enregistrés");
await sleep(500);
s = state();
const facts = s.tables.user_facts.map((f) => f.fact);
assert.deepEqual(facts.sort(), ["A un chat, Filou.", "Préfère le tutoiement.", "Se prénomme Karim."]);
step(`fiche : ${facts.join(" / ")} — l'antidépresseur a été écarté, le doublon aussi`);

// 7. Ce que le modèle a reçu pour répondre.
const firstChat = s.llm.find((r) => !r.json);
assert.match(firstChat.system, /^# Élise — fiche persona/);
assert.match(firstChat.system, /Tu ne sais encore rien/);
assert.deepEqual(firstChat.contents.map((c) => c.role), ["user", "model", "user"]);
step("le modèle a reçu : persona + fiche + résumé + conversation");

// 8. Quota atteint : rien n'est perdu.
await input.fill("Test QUOTA");
await page.getByLabel("Envoyer").click();
await page.getByText("Élise reçoit beaucoup de messages en ce moment").waitFor();
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
const ctx2 = await browser.newContext(phone);
const page2 = await ctx2.newPage();
await page2.goto(`${BASE}/connexion`);
await page2.getByText("Première visite ? Créer un compte").click();
await page2.fill('input[name="email"]', "lea@example.com");
await page2.fill('input[name="password"]', "motdepasse");
await page2.click('button[type="submit"]');
await page2.waitForURL(`${BASE}/`);
await page2.getByText("Bonjour, je suis Élise.").waitFor();
assert.equal(await page2.getByText("Karim").count(), 0);
assert.equal(await page2.locator("main p").count(), 2); // intitulé du jour + premier message
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
await page.getByText("En direct").waitFor();
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
  const deskCtx = await browser.newContext({ viewport: { width: 1280, height: 900 }, colorScheme, locale: "fr-FR" });
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

// 24. Sur ordinateur et en mode sombre, pour le coup d'œil.
const desk = await browser.newContext({ viewport: { width: 1280, height: 800 }, colorScheme: "dark", locale: "fr-FR" });
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
