/* Une séance, de bout en bout : la composer, la dérouler série par série,
   et retrouver ce qu'on a soulevé dans le carnet. C'est le cœur de l'app ;
   si ça casse, le reste n'a plus d'intérêt. */
const { ouvrir, remplir, compteur } = require('./commun.js');

(async () => {
const { b, p, erreurs } = await ouvrir();
const { ok, bilan } = compteur();
await remplir(p);

console.log('\n== 1. le catalogue ==');
const cat = await p.evaluate(() => ({ n: EXOS.length, ids: EXOS.map(x => x.id) }));
ok(cat.n === 43, '43 exercices (' + cat.n + ')');
ok(new Set(cat.ids).size === cat.n, 'aucun identifiant en double');
const muscles = await p.evaluate(() =>
  EXOS.filter(x => !(x.m||[]).length).map(x => x.id));
ok(muscles.length === 0, 'chacun déclare au moins un muscle moteur' +
   (muscles.length ? ' : ' + muscles : ''));

console.log('\n== 2. composer une séance ==');
await p.evaluate(() => openSeance(null)); await p.waitForTimeout(400);
ok(await p.locator('#modal.open').count() === 1, 'le formulaire s\'ouvre');
await p.evaluate(() => openPicker()); await p.waitForTimeout(400);
const lignes = await p.locator('.pickrow').count();
ok(lignes === 43, 'le sélecteur propose les 43 exercices (' + lignes + ')');
await p.evaluate(() => { const i = document.querySelector('#pickq');
  i.value = 'squat'; i.dispatchEvent(new Event('input', {bubbles:true})); });
await p.waitForTimeout(350);
const filtre = await p.locator('.pickrow').count();
ok(filtre > 0 && filtre < 43, 'la recherche filtre (' + filtre + ')');
await p.locator('.pickrow').first().click(); await p.waitForTimeout(400);
ok(await p.locator('.exorow').count() >= 1, 'l\'exercice choisi rejoint la séance');
await p.evaluate(() => closeSheet()); await p.waitForTimeout(250);

console.log('\n== 3. dérouler la séance du jour ==');
await p.evaluate(() => { state.log[today()] = {}; save(); render(); }); await p.waitForTimeout(300);
await p.evaluate(() => runOpen('s1')); await p.waitForTimeout(500);
ok(await p.locator('#run.open').count() === 1, 'le mode séance s\'ouvre');
ok(await p.evaluate(() => runCur().i) === 'tractions', 'sur le premier exercice');
const total = await p.evaluate(() => run.x.reduce((n, y) => n + y.nb, 0));
ok(total === 6, '3 séries × 2 exercices à faire (' + total + ')');
for(let i = 0; i < total; i++){
  const btn = p.locator('[data-act="runok"]');
  if(await btn.count() === 0) break;
  await btn.click(); await p.waitForTimeout(160);
  const skip = p.locator('[data-act="runskiprest"]');
  if(await skip.count()) { await skip.click(); await p.waitForTimeout(140); }
}
await p.waitForTimeout(500);
const fini = await p.evaluate(() => {
  const e = (state.log[today()]||{}).s1;
  return e ? { done:e.done, series:(e.sea&&e.sea.x||[]).reduce((n,x)=>n+x.s.length,0) } : null;
});
ok(fini && fini.done, 'la séance se valide toute seule à la fin');
ok(fini && fini.series === 6, 'et les six séries sont inscrites (' + (fini&&fini.series) + ')');

console.log('\n== 4. ce qui est inscrit se retrouve ==');
await p.evaluate(() => { if(typeof runClose === 'function') runClose(); state.tab='sport'; render(); });
await p.waitForTimeout(450);
const dansCarnet = await p.evaluate(() => carnet().some(s => s.key === today() && s.id === 's1'));
ok(dansCarnet, 'la séance du jour est au carnet');
const charges = await p.evaluate(() => {
  const s = carnet().find(x => x.key === today());
  return (s.sea.x||[]).map(x => (x.s||[]).map(t => t.w).join('/')).join(' | ');
});
ok(/65/.test(charges), 'avec les charges telles qu\'elles ont été posées (' + charges + ')');

console.log('\n== 5. une séance sans jour reste disponible ==');
const biblio = await p.evaluate(() => seancesVisibles().map(h => h.id));
ok(biblio.indexOf('s2') >= 0, 'la séance sans jour est dans la bibliothèque');
ok(await p.evaluate(() => seancesFor(today()).map(h => h.id).indexOf('s2') < 0),
   'mais pas dans « Aujourd\'hui »');

console.log('\n== 6. une séance n\'est pas une tâche du jour ==');
const compte = await p.evaluate(() => ({
  taches: habitsFor(today()).map(h => h.id),
  jour:   dayStat(today())
}));
ok(compte.taches.indexOf('s1') < 0, 'elle ne compte pas dans les tâches');
ok(compte.jour.total === 2, 'le compteur du jour ne voit que les deux habitudes (' + compte.jour.total + ')');

console.log('\n== 7. la récupération lit le carnet ==');
const recup = await p.evaluate(() => {
  const r = recuperation();
  return { chauds: r.filter(m => m.etat === 'chaud').map(m => m.id), n: r.length };
});
ok(recup.n === 13, 'treize muscles suivis (' + recup.n + ')');
ok(recup.chauds.length > 0, 'ceux travaillés aujourd\'hui sont chauds : ' + recup.chauds.join(', '));
ok(recup.chauds.indexOf('dos') >= 0, 'dont le dos, après des tractions');

console.log('\n== 8. rien ne casse ==');
ok(erreurs.length === 0, 'aucune erreur de page' + (erreurs.length ? ' : ' + erreurs[0] : ''));

await b.close();
process.exit(bilan() ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
