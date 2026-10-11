/* Focus : la liste, le bouton, et surtout ce que le raccourci de l'iPhone lit.

   Le blocage ne se voit pas dans la page : il tient au mot que l'API renvoie
   au raccourci, « bloque » ou « libre ». On monte donc un vrai petit serveur
   — les fichiers du dépôt et la vraie fonction api/focus.js, sur un Redis en
   mémoire — et on demande ce mot comme le ferait le raccourci, à chaque étape.

   Deux navigateurs jouent l'iPhone : « l'app » posée sur l'écran d'accueil,
   et « Safari », où atterrit le renvoi. Sur iPhone ils ne partagent pas leur
   stockage ; ici non plus, ce sont deux contextes séparés. */
const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright-core');
const { compteur, CHROME } = require('./commun.js');

/* ------------------------------------------------ Redis, en mémoire */
const base = new Map();
let avecBase = true;
const S = require('../api/_store.js');
S.hasStore = () => avecBase;
S.redis = cmds => Promise.resolve(cmds.map(c => {
  const op = String(c[0]).toUpperCase();
  if(op === 'GET') return base.has(c[1]) ? base.get(c[1]) : null;
  if(op === 'SET'){ base.set(c[1], String(c[2])); return 'OK'; }
  if(op === 'DEL'){ return base.delete(c[1]) ? 1 : 0; }
  throw new Error('commande inconnue : ' + op);
}));
const focusApi = require('../api/focus.js');   /* chargée après : elle prend le faux Redis */

/* ------------------------------------------------ le serveur */
const RACINE = path.resolve(__dirname, '..');
const TYPES = { '.html':'text/html; charset=utf-8', '.json':'application/json', '.png':'image/png', '.js':'text/javascript' };
let coupe = false;   /* pour jouer une panne de réseau côté API */
const srv = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://x');
  if(u.pathname === '/api/focus'){
    if(coupe && req.method === 'POST'){ req.socket.destroy(); return; }   /* l'app perd le réseau, pas le raccourci */
    return focusApi(req, res);
  }
  let f = path.join(RACINE, decodeURIComponent(u.pathname));
  if(!f.startsWith(RACINE)){ res.statusCode = 403; return res.end(); }
  if(fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
  if(!fs.existsSync(f)){ res.statusCode = 404; return res.end('absent'); }
  res.setHeader('Content-Type', TYPES[path.extname(f)] || 'application/octet-stream');
  fs.createReadStream(f).pipe(res);
});

(async () => {
await new Promise(r => srv.listen(0, '127.0.0.1', r));
const ORIG = 'http://127.0.0.1:' + srv.address().port;
const { ok, bilan } = compteur();

/* Ce que fait le raccourci : un GET, un mot. */
const raccourci = async (k, extra) => {
  const r = await fetch(ORIG + '/api/focus?k=' + k + (extra || ''));
  return { code: r.status, mot: await r.text(), type: r.headers.get('content-type') };
};
const ecrire = (k, etat) => fetch(ORIG + '/api/focus', { method:'POST', headers:{ 'Content-Type':'application/json' },
  body: JSON.stringify({ action:'ecrire', k, etat }) }).then(r => r.json());

const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
const erreurs = [];
async function telephone(){
  const ctx = await b.newContext({ viewport:{ width:390, height:844 }, isMobile:true, hasTouch:true, locale:'fr-FR' });
  await ctx.route('**/*', r => r.request().url().startsWith(ORIG) ? r.continue() : r.abort());
  const p = await ctx.newPage();
  p.on('pageerror', e => erreurs.push('PAGEERROR: ' + e.message));
  p.on('console', m => { if(m.type() === 'error' && !/net::ERR|Failed to load|fonts/i.test(m.text()))
                           erreurs.push('CONSOLE: ' + m.text()); });
  return { ctx, p };
}
const attendre = p => p.waitForTimeout(350);
const taches = p => p.$$eval('#liste .t', l => l.map(x => x.textContent));
const ajouter = async (p, t) => { await p.fill('#nv', t); await p.press('#nv', 'Enter'); await attendre(p); };
const revenir = async p => { await p.evaluate(() => document.dispatchEvent(new Event('visibilitychange'))); await p.waitForTimeout(500); };

/* ================================================================ */
console.log('\n== 1. le serveur, seul ==');
let r = await fetch(ORIG + '/api/focus').then(x => x.json());
ok(r.ok && r.store === true, 'GET sans clé : le contrôle de santé répond, base branchée');
let m = await raccourci('pasunecle!');
ok(m.code === 400 && m.mot !== 'bloque', 'une clé mal formée ne bloque pas (' + m.code + ' « ' + m.mot + ' »)');
m = await raccourci('inconnue12345');
ok(m.code === 200 && m.mot === 'libre', 'une clé inconnue : « libre »');
ok(/^text\/plain/.test(m.type), 'la réponse est du texte brut, ce que Raccourcis lit le plus simplement');

console.log('\n== 2. premier lancement de l\'app ==');
const app = await telephone();
await app.p.goto(ORIG + '/focus/'); await app.p.waitForTimeout(700);
const K = await app.p.evaluate(() => localStorage.getItem('focus.cle'));
ok(/^[a-z0-9]{12}$/.test(K || ''), 'un code de 12 caractères est tiré (' + K + ')');
ok(!/[l1o0i]/.test(K), 'sans caractère qui se confond à la recopie');
ok(app.p.url().includes('?k=' + K), 'l\'adresse porte le code : poser l\'app depuis Safari le garde');
ok(await app.p.locator('[data-act="lancer"][disabled]').count() === 1, 'liste vide : le bouton Focus est inactif');
ok(await app.p.locator('.alerte').count() === 1, 'un avertissement dit que le blocage n\'est pas branché');
ok(await app.p.locator('#pastille:not([hidden])').count() === 1, 'et le cadenas porte une pastille');
await app.p.click('#haut [data-act="regl"]'); await app.p.waitForTimeout(600);
ok(/jamais vu/.test(await app.p.textContent('#etat')), 'la feuille de réglage dit que le raccourci n\'a jamais appelé');
await app.p.click('#feuille [data-act="fermer"]'); await attendre(app.p);

console.log('\n== 3. écrire sa liste ==');
await ajouter(app.p, 'Réviser le chapitre 4');
await ajouter(app.p, '   Envoyer   le mail à Paul  ');
await app.p.fill('#nv', 'Ranger le bureau'); await app.p.click('#ajout .plus'); await attendre(app.p);
await ajouter(app.p, '   ');
ok(JSON.stringify(await taches(app.p)) === JSON.stringify(['Réviser le chapitre 4', 'Envoyer le mail à Paul', 'Ranger le bureau']),
   'trois tâches, espaces nettoyés, une vide refusée');
ok(await app.p.inputValue('#nv') === '', 'le champ se vide après chaque ajout, et après des espaces seuls');
await app.p.locator('[data-act="suppr"]').nth(2).click(); await attendre(app.p);
ok((await taches(app.p)).length === 2, 'avant le focus, on peut retirer une tâche');
ok(await app.p.locator('[data-act="lancer"]:not([disabled])').count() === 1, 'le bouton Focus s\'active');
await ajouter(app.p, '<img src=x onerror=alert(1)>');
ok(await app.p.locator('#liste img').count() === 0, 'un texte de tâche n\'est jamais interprété comme du HTML');
await app.p.locator('[data-act="suppr"]').nth(2).click(); await attendre(app.p);
m = await raccourci(K);
ok(m.mot === 'libre', 'liste prête mais pas de focus : le raccourci lit « libre »');

console.log('\n== 4. FOCUS ==');
await app.p.click('[data-act="lancer"]'); await app.p.waitForTimeout(600);
ok(await app.p.locator('body.enfocus').count() === 1, 'l\'écran passe en mode focus');
ok(await app.p.locator('#chrono').count() === 1, 'un chrono tourne');
const c1 = await app.p.textContent('#chrono'); await app.p.waitForTimeout(1200);
ok(await app.p.textContent('#chrono') !== c1, 'et il avance (' + c1 + ' → ' + await app.p.textContent('#chrono') + ')');
ok(await app.p.locator('[data-act="suppr"]').count() === 0, 'plus aucun moyen de retirer une tâche');
m = await raccourci(K);
ok(m.mot === 'bloque', 'le raccourci lit « bloque » : Instagram renverra ici');
ok(await app.p.locator('.horsligne').count() === 0, 'le serveur a reçu le focus : pas d\'avertissement hors ligne');

console.log('\n== 5. le renvoi atterrit dans Safari ==');
const safari = await telephone();
await safari.p.goto(ORIG + '/focus/?k=' + K + '&r=1'); await safari.p.waitForTimeout(900);
ok(await safari.p.locator('body.enfocus').count() === 1, 'Safari, qui n\'a rien en mémoire, retrouve le focus en cours');
ok(JSON.stringify(await taches(safari.p)) === JSON.stringify(['Réviser le chapitre 4', 'Envoyer le mail à Paul']),
   'avec la même liste');
ok(/Pas maintenant : encore 2 tâches/.test(await safari.p.textContent('#toast')), 'un mot dit pourquoi on est là');
ok(!safari.p.url().includes('r=1'), 'et l\'adresse oublie le renvoi');
await safari.p.locator('[data-act="cocher"]').first().click(); await safari.p.waitForTimeout(500);
ok(await safari.p.locator('[aria-checked="true"]').count() === 1, 'on coche depuis Safari');
m = await raccourci(K);
ok(m.mot === 'bloque', 'une sur deux : toujours « bloque »');

console.log('\n== 6. retour dans l\'app ==');
await revenir(app.p);
ok(await app.p.locator('[aria-checked="true"]').count() === 1, 'la case cochée dans Safari est cochée ici');
ok(/1 sur 2/.test(await app.p.textContent('.compte')), 'le compte suit : 1 sur 2');
await ajouter(app.p, 'Relire la fiche');
ok((await taches(app.p)).length === 3, 'pendant le focus, on peut encore ajouter');
ok(/1 sur 3/.test(await app.p.textContent('.compte')), 'et le compte repart : 1 sur 3');
await app.p.locator('[data-act="cocher"]').first().click(); await attendre(app.p);
ok(await app.p.locator('[aria-checked="true"]').count() === 0, 'une case se décoche aussi : une erreur de pouce se rattrape');
await app.p.locator('[data-act="cocher"]').first().click(); await attendre(app.p);

console.log('\n== 7. la dernière case libère le téléphone ==');
await app.p.locator('[data-act="cocher"]').nth(1).click(); await attendre(app.p);
ok(await app.p.locator('body.enfocus').count() === 1, 'deux sur trois : toujours en focus');
await app.p.locator('[data-act="cocher"]').nth(2).click(); await app.p.waitForTimeout(600);
ok(await app.p.locator('body.enfocus').count() === 0, 'trois sur trois : le focus se lève tout seul');
ok(await app.p.locator('#feuille.open .fin').count() === 1, 'l\'écran de fin s\'ouvre');
ok(/3 tâches en/.test(await app.p.textContent('.fin')), 'il dit ce qui a été fait');
m = await raccourci(K);
ok(m.mot === 'libre', 'le raccourci lit « libre »');
await app.p.click('.fin [data-act="fermer"]'); await attendre(app.p);
ok((await taches(app.p)).length === 0, 'la liste est vide : ce qui était fait est rangé');
ok(/1 focus tenu/.test(await app.p.textContent('.stats')), 'et le compte des focus tenus dit 1');

console.log('\n== 8. la sortie de secours ==');
await ajouter(app.p, 'Une tâche impossible');
await ajouter(app.p, 'Une tâche facile');
await app.p.click('[data-act="lancer"]'); await attendre(app.p);
await app.p.locator('[data-act="cocher"]').nth(1).click(); await attendre(app.p);
await app.p.click('[data-act="secours"]'); await attendre(app.p);
ok(await app.p.locator('#abandon[disabled]').count() === 1, 'arrêter est d\'abord impossible');
await app.p.fill('#phrase', 'je laisse');
ok(await app.p.locator('#abandon[disabled]').count() === 1, 'une phrase incomplète ne suffit pas');
await app.p.click('#feuille [data-act="fermer"]'); await attendre(app.p);
ok(await app.p.locator('body.enfocus').count() === 1, '« Je continue » referme sans rien arrêter');
await app.p.click('[data-act="secours"]'); await attendre(app.p);
await app.p.fill('#phrase', '  Je   laisse tombér ');
ok(await app.p.locator('#abandon:not([disabled])').count() === 1, 'majuscule, espaces et accent du clavier tolérés');
await app.p.click('#abandon'); await attendre(app.p);
ok(await app.p.locator('body.enfocus').count() === 0, 'le focus s\'arrête');
ok(JSON.stringify(await taches(app.p)) === JSON.stringify(['Une tâche impossible']), 'le fait est rangé, le reste attend');
ok(/1 focus tenu · 1 abandonné/.test(await app.p.textContent('.stats')), 'l\'abandon est compté, à part');
ok((await raccourci(K)).mot === 'libre', 'le raccourci lit « libre »');

console.log('\n== 9. brancher le blocage ==');
await app.p.click('#haut [data-act="regl"]'); await app.p.waitForTimeout(600);
const urlA = await app.p.textContent('#urlA'), urlB = await app.p.textContent('#urlB');
ok(urlA === ORIG + '/api/focus?k=' + K, 'l\'adresse A est celle que lit le raccourci');
ok(urlB === ORIG + '/focus/?k=' + K + '&r=1', 'l\'adresse B ramène sur la liste, code compris');
ok(/Serveur : joignable/.test(await app.p.textContent('#etat')), 'le serveur est dit joignable');
ok(/Jamais Safari/.test(await app.p.textContent('.etapes')), 'le guide prévient de la boucle avec Safari');
await raccourci(K);                         /* l'automatisation tourne une première fois */
await app.p.click('#feuille [data-act="fermer"]'); await attendre(app.p);
await app.p.click('#haut [data-act="regl"]'); await app.p.waitForTimeout(600);
ok(/Raccourci : vu à l'instant/.test(await app.p.textContent('#etat')), 'après un appel, il est « vu à l\'instant »');
await app.p.click('#feuille [data-act="fermer"]'); await attendre(app.p);
ok(await app.p.locator('.alerte').count() === 0, 'l\'avertissement disparaît');
ok(await app.p.locator('#pastille[hidden]').count() === 1, 'et la pastille aussi');

console.log('\n== 10. un code d\'un autre appareil ==');
const K2 = 'qwertyzxcvbn';
await ecrire(K2, { maj: Date.now(), actif:false, debut:0, taches:[{ id:'a1', t:'Tâche de l\'autre téléphone', ok:false }], hist:[] });
await app.p.click('#haut [data-act="regl"]'); await app.p.waitForTimeout(400);
await app.p.fill('#nvcode', 'QWER-TYZX-CVBN'); await app.p.press('#nvcode', 'Enter'); await app.p.waitForTimeout(700);
ok(await app.p.evaluate(() => localStorage.getItem('focus.cle')) === K2, 'le code tapé avec tirets et majuscules est adopté');
ok(JSON.stringify(await taches(app.p)) === JSON.stringify(['Tâche de l\'autre téléphone']), 'sa liste remplace la nôtre');
ok((await app.p.textContent('#cle')) === 'qwer-tyzx-cvbn', 'la feuille montre le nouveau code');
await app.p.fill('#nvcode', 'abc'); await app.p.press('#nvcode', 'Enter'); await attendre(app.p);
ok(await app.p.evaluate(() => localStorage.getItem('focus.cle')) === K2, 'un code trop court est refusé');
await app.p.click('#feuille [data-act="fermer"]'); await attendre(app.p);

console.log('\n== 11. les garde-fous du serveur ==');
const K3 = 'garde4fou5aa';
const ilya13h = Date.now() - 13 * 3600 * 1000;
await ecrire(K3, { maj: Date.now(), actif:true, debut: ilya13h, taches:[{ id:'x', t:'oubliée', ok:false }], hist:[] });
ok((await raccourci(K3)).mot === 'libre', 'un focus de plus de 12 h ne bloque plus');
await ecrire(K3, { maj: Date.now() + 1, actif:true, debut: Date.now(), taches:[{ id:'x', t:'faite', ok:true }], hist:[] });
ok((await raccourci(K3)).mot === 'libre', 'une liste entièrement cochée ne bloque pas, même focus ouvert');
await ecrire(K3, { maj: Date.now() + 2, actif:true, debut: Date.now(), taches:[], hist:[] });
ok((await raccourci(K3)).mot === 'libre', 'une liste vide ne bloque pas');
r = await ecrire(K3, { maj: 1000, actif:false, debut:0, taches:[], hist:[] });
ok(r.ok === false && r.cause === 'perime' && r.etat.maj > 1000, 'un état plus ancien n\'écrase pas le plus récent');
r = await ecrire(K3, { maj: Date.now() + 3, actif:true, debut: Date.now(),
  taches: Array.from({ length: 60 }, (_, i) => ({ id: 't' + i, t: 'x'.repeat(200), ok:false })).concat([{ id:'<b>', t:'y' }]), hist:[] });
ok(r.ok && r.etat.taches.length === 40, 'au plus 40 tâches gardées (' + r.etat.taches.length + ')');
ok(r.etat.taches.every(t => t.t.length <= 140), 'au plus 140 caractères chacune');
r = await fetch(ORIG + '/api/focus', { method:'POST', headers:{ 'Content-Type':'application/json' },
  body: JSON.stringify({ action:'lire', k:'!!' }) });
ok(r.status === 400, 'lire avec une clé mal formée : refusé');
avecBase = false;
ok((await raccourci(K)).mot === 'libre', 'sans base, le raccourci lit « libre » : une panne n\'enferme personne');
r = await fetch(ORIG + '/api/focus', { method:'POST', headers:{ 'Content-Type':'application/json' },
  body: JSON.stringify({ action:'lire', k:K }) });
ok(r.status === 501, 'et l\'app apprend que la base manque (501)');
avecBase = true;

console.log('\n== 12. sans réseau ==');
await ajouter(app.p, 'Pendant la coupure');
coupe = true;
await app.p.click('[data-act="lancer"]'); await app.p.waitForTimeout(900);
ok(await app.p.locator('body.enfocus').count() === 1, 'le focus se lance quand même');
ok(await app.p.locator('.horsligne').count() === 1, 'mais l\'écran dit que le blocage ne le voit pas');
ok((await raccourci(K2)).mot === 'libre', 'le serveur, de fait, ne le sait pas');
coupe = false;
await revenir(app.p);
ok(await app.p.locator('.horsligne').count() === 0, 'le réseau revient : l\'avertissement part');
ok((await raccourci(K2)).mot === 'bloque', 'et le serveur a reçu le focus en attente');

console.log('\n== 13. l\'app retrouve son état à la réouverture ==');
await app.p.reload(); await app.p.waitForTimeout(700);
ok(await app.p.locator('body.enfocus').count() === 1, 'toujours en focus après un rechargement');
ok(app.p.url().includes('?k=' + K2), 'avec le code adopté dans l\'adresse');

console.log('\n== 14. un focus oublié se lève de lui-même ==');
await app.p.evaluate(() => {
  const e = JSON.parse(localStorage.getItem('focus.etat'));
  e.debut = Date.now() - 13 * 3600 * 1000; e.maj = Date.now() + 10;
  localStorage.setItem('focus.etat', JSON.stringify(e));
});
await app.p.reload(); await app.p.waitForTimeout(800);
ok(await app.p.locator('body.enfocus').count() === 0, 'au-delà de 12 h, l\'app le clôt');
ok(/12 h/.test(await app.p.textContent('#toast')), 'et dit pourquoi');
ok((await raccourci(K2)).mot === 'libre', 'le serveur suit');

console.log('\n== 15. la mise en page tient sur un petit écran ==');
const petit = await telephone();
await petit.p.setViewportSize({ width:320, height:568 });
await petit.p.goto(ORIG + '/focus/?k=' + K); await petit.p.waitForTimeout(600);
for(let i = 0; i < 4; i++) await ajouter(petit.p, 'Une tâche au nom franchement très long pour voir si la ligne se replie proprement ' + i);
const deb = await petit.p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
ok(deb <= 0, 'aucun défilement horizontal à 320 px (débord : ' + deb + ' px)');
await petit.p.click('#haut [data-act="regl"]'); await petit.p.waitForTimeout(500);
const debF = await petit.p.evaluate(() => { const f = document.querySelector('#feuille'); return f.scrollWidth - f.clientWidth; });
ok(debF <= 0, 'la feuille de réglage non plus, adresses comprises (débord : ' + debF + ' px)');

console.log('\n== 16. les fichiers de l\'app installée ==');
const man = await fetch(ORIG + '/focus/manifest.json').then(x => x.json());
ok(man.scope === '/focus/' && man.display === 'standalone', 'manifeste : portée /focus/, plein écran');
ok(!('start_url' in man), 'pas de start_url : l\'app installée rouvre l\'adresse d\'où on l\'a posée, code compris');
for(const ic of man.icons){
  const rr = await fetch(ORIG + ic.src);
  ok(rr.status === 200 && /image\/png/.test(rr.headers.get('content-type')), 'icône servie : ' + ic.src);
}

console.log('\n== 17. rien ne casse ==');
ok(erreurs.length === 0, 'aucune erreur de page' + (erreurs.length ? ' : ' + erreurs.join(' | ') : ''));

await b.close();
srv.close();
process.exit(bilan() ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
