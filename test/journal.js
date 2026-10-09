/* Le Journal : poids, nutrition, repas, humeur. La partie qui sert
   l'entraînement sans en faire partie. */
const { ouvrir, remplir, compteur } = require('./commun.js');

(async () => {
const { b, p, erreurs } = await ouvrir();
const { ok, bilan } = compteur();
await remplir(p);
await p.locator('.tab[data-tab="journal"]').click(); await p.waitForTimeout(500);

console.log('\n== 1. le poids ==');
ok(await p.locator('.spark, svg').count() > 0, 'la courbe est tracée');
const champ = await p.locator('#wval').count();
ok(champ === 1, 'on peut noter une pesée');
await p.evaluate(() => { document.querySelector('#wval').value = '73.2'; });
await p.locator('[data-act="wsave"]').click(); await p.waitForTimeout(400);
ok(await p.evaluate(() => state.weight[today()] === 73.2), 'et elle est enregistrée');
ok(await p.locator('[data-act="wtarget"]').count() === 1, 'et se fixer un objectif de poids');

console.log('\n== 2. les besoins caloriques ==');
const n = await p.evaluate(() => {
  const bj = besoinDuJour(today());
  return { kcal: bj.kcal, prot: bj.prot, base: bj.base, sport: bj.sport };
});
ok(n.kcal > 1500 && n.kcal < 5000, 'un objectif calorique plausible : ' + n.kcal + ' kcal');
ok(n.prot > 80 && n.prot < 300, 'et un objectif de protéines : ' + n.prot + ' g');
ok(n.sport >= 0, 'la dépense des séances est comptée à part (' + Math.round(n.sport) + ' kcal)');

console.log('\n== 3. la dépense d\'une séance tient debout ==');
const dep = await p.evaluate(() => {
  const h = habitById('s1');
  const sea = { d: 45*60, x: h.exos.map(e => ({ i:e.x, s: Array.from({length:e.s}, () => ({ r:e.r, w:e.w })) })) };
  return Math.round(depenseSeance(sea));
});
ok(dep > 150 && dep < 700, '45 min de musculation : ' + dep + ' kcal — un ordre de grandeur crédible');

console.log('\n== 4. les repas ==');
const avant = await p.evaluate(() => (state.meals[today()]||[]).length);
await p.evaluate(() => { state.meals[today()] = (state.meals[today()]||[]);
  state.meals[today()].push({ n:'Test', kcal:500, prot:40 }); save(); render(); });
await p.waitForTimeout(350);
ok(await p.evaluate(() => (state.meals[today()]||[]).length) === avant + 1, 'un repas s\'ajoute');
const consomme = await p.evaluate(() => totalRepas(today()));
ok(consomme.kcal >= 500, 'et il compte dans le total du jour (' + consomme.kcal + ' kcal)');
ok(consomme.prot >= 40, 'protéines comprises (' + consomme.prot + ' g)');

console.log('\n== 5. l\'humeur et la note ==');
const nh = await p.locator('[data-act="mood"]').count();
ok(nh === 5, 'cinq humeurs proposées (' + nh + ')');
if(nh){
  await p.locator('[data-act="mood"]').nth(3).click(); await p.waitForTimeout(300);
  ok(await p.evaluate(() => state.mood[today()] === 3), 'celle qu\'on choisit est retenue');
}

console.log('\n== 6. rien ne casse ==');
ok(erreurs.length === 0, 'aucune erreur de page' + (erreurs.length ? ' : ' + erreurs[0] : ''));

await b.close();
process.exit(bilan() ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
