/* Le bouton + : il s'efface quand on descend, il revient quand on remonte.
   C'est du comportement, pas du style — donc on fait vraiment défiler. */
const { ouvrir, remplir, compteur } = require('./commun.js');

(async () => {
const { b, p, erreurs } = await ouvrir();
const { ok, bilan } = compteur();
await remplir(p);

const etat = () => p.evaluate(() => {
  const f = document.querySelector('#fab'), r = f.getBoundingClientRect();
  return { escamote: f.classList.contains('away'), cache: f.classList.contains('hide'),
           opacite: +getComputedStyle(f).opacity, bas: r.bottom, y: window.pageYOffset };
});
const vers = async y => { await p.evaluate(v => window.scrollTo(0, v), y); await p.waitForTimeout(420); };

console.log('\n== 1. en haut, il est là ==');
await vers(0);
let e = await etat();
ok(!e.cache, 'le bouton existe sur l\'accueil');
ok(!e.escamote, 'il n\'est pas escamoté');
ok(e.opacite > 0.9, 'et il est bien visible (opacité ' + e.opacite + ')');

console.log('\n== 2. on descend : il s\'efface ==');
await vers(1400);
e = await etat();
ok(e.escamote, 'il s\'escamote');
ok(e.opacite < 0.1, 'il devient transparent (opacité ' + e.opacite + ')');
ok(e.bas > 844 - 10, 'et il glisse sous le bord de l\'écran');
ok(await p.evaluate(() => getComputedStyle(document.querySelector('#fab')).pointerEvents) === 'none',
   'il ne capte plus les appuis : on peut toucher ce qu\'il couvrait');

console.log('\n== 3. on remonte : il revient ==');
await vers(1100);
e = await etat();
ok(!e.escamote, 'il revient dès qu\'on remonte');
ok(e.opacite > 0.9, 'et redevient visible');

console.log('\n== 4. tout en haut, il est là quoi qu\'il arrive ==');
await vers(1400); await vers(0);
ok(!(await etat()).escamote, 'de retour en haut de page');

console.log('\n== 5. changer d\'onglet ne le laisse pas escamoté ==');
await vers(1400);
ok((await etat()).escamote, 'escamoté avant de changer d\'onglet');
await p.locator('.tab[data-tab="journal"]').click(); await p.waitForTimeout(400);
ok((await etat()).cache, 'il disparaît sur le Journal, où il ne sert à rien');
await p.evaluate(() => window.scrollTo(0,0)); await p.waitForTimeout(200);
await p.locator('.tab[data-tab="sport"]').click(); await p.waitForTimeout(450);
e = await etat();
ok(!e.cache && !e.escamote, 'et il est de nouveau là, visible, en revenant sur l\'accueil');

console.log('\n== 6. il reste cliquable ==');
await p.locator('#fab').click(); await p.waitForTimeout(450);
ok(await p.locator('#modal.open').count() === 1, 'un appui ouvre bien le formulaire');

console.log('\n== 7. rien ne casse ==');
ok(erreurs.length === 0, 'aucune erreur de page' + (erreurs.length ? ' : ' + erreurs[0] : ''));

await b.close();
process.exit(bilan() ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
