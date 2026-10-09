/* La forme de l'app : trois onglets, l'entraînement en accueil, et plus la
   moindre trace du jeu social. C'est la suite qui garde le cap pris — elle
   échoue si quelqu'un remet un onglet ou un compteur de points. */
const { ouvrir, remplir, compteur } = require('./commun.js');

(async () => {
const { b, p, erreurs } = await ouvrir();
const { ok, bilan } = compteur();
await remplir(p);

console.log('\n== 1. trois onglets, rien de verrouillé ==');
const tabs = await p.evaluate(() => TABS.map(t => t[0]));
ok(tabs.length === 3, 'trois onglets (' + tabs.length + ' : ' + tabs.join(', ') + ')');
ok(tabs[0] === 'sport', 'l\'entraînement est le premier');
ok(await p.evaluate(() => state.tab) === 'sport', 'et l\'app s\'ouvre dessus');
ok(await p.locator('.tab.lock').count() === 0, 'aucun onglet verrouillé');
ok(await p.evaluate(() => locked('journal') === false && locked('profil') === false),
   'et locked() ne verrouille plus rien');
/* la barre doit tenir dans un écran de téléphone */
const barre = await p.evaluate(() => {
  const t = [...document.querySelectorAll('#tabs .tab')];
  return { deborde: t.some(x => { const r = x.getBoundingClientRect();
             return r.left < -0.5 || r.right > innerWidth + 0.5; }),
           tronque: t.some(x => x.scrollWidth > x.clientWidth + 1) };
});
ok(!barre.deborde, 'la barre tient dans 390 px');
ok(!barre.tronque, 'et aucun libellé n\'est coupé');

console.log('\n== 2. le jeu social a bien disparu ==');
const restes = await p.evaluate(() => {
  const absent = n => typeof window[n] === 'undefined';
  return {
    fns: ['totalXP','badgeState','rankOf','periodScores','leaderboard','viewCrew',
          'addFriend','myCode','syncNow','dayPoints','computePts','classementForce',
          'viewJour','viewStats','viewHabitudes'].filter(n => !absent(n)),
    vars: ['BADGES','RANKS','NIVEAUX'].filter(n => !absent(n)),
    etat: ['friends','pendingDrop','crews','syncAt'].filter(k => k in state)
  };
});
ok(restes.fns.length === 0, 'aucune fonction du jeu social ne subsiste' +
   (restes.fns.length ? ' : ' + restes.fns : ''));
ok(restes.vars.length === 0, 'ni ses tables' + (restes.vars.length ? ' : ' + restes.vars : ''));
ok(restes.etat.length === 0, 'ni ses champs d\'état' + (restes.etat.length ? ' : ' + restes.etat : ''));

const src = require('fs').readFileSync(__dirname + '/../index.html', 'utf8');
ok(!/api\/board|api\/crew/.test(src), 'la page n\'appelle plus board ni crew');
ok(!require('fs').existsSync(__dirname + '/../api/board.js'), 'api/board.js est supprimé');
ok(!require('fs').existsSync(__dirname + '/../api/crew.js'), 'api/crew.js aussi');
const texte = await p.evaluate(() => document.body.innerText);
ok(!/\bXP\b|badge|classement|crew/i.test(texte), 'et plus un mot à l\'écran');

console.log('\n== 3. l\'accueil : la séance d\'abord ==');
const sections = await p.evaluate(() =>
  [...document.querySelectorAll('#view .sec h2')].map(e => e.textContent.trim()));
ok(sections[0] === 'Aujourd\'hui', 'la première section est « Aujourd\'hui » (' + sections[0] + ')');
ok(sections.indexOf('Aussi aujourd\'hui') === 1, 'les habitudes viennent juste après');
ok(sections.indexOf('Tes records') > 0, 'les records sont là');
ok(sections.indexOf('Force') < 0, 'mais plus la carte « Force » et ses niveaux');
ok(sections.indexOf('Ta régularité') > 0, 'la régularité a fondu dans l\'accueil');
ok(await p.locator('.exorow, .hrow').first().count() === 1, 'la séance du jour est affichée');

console.log('\n== 4. la bande des habitudes ==');
const bande = () => p.evaluate(() => {
  const l = [...document.querySelectorAll('.jline')];
  return { n:l.length, faits:l.filter(x => x.classList.contains('on')).length,
           entete:(document.querySelector('.sec h2 + span, #view .sec span')||{}).textContent };
});
let avant = await bande();
ok(avant.n === 2, 'les deux habitudes du jour sont dans la bande (' + avant.n + ')');
ok(avant.faits === 0, 'aucune n\'est faite au départ');
const premier = await p.locator('.jline').first().getAttribute('data-id');
await p.locator('.jline').first().click(); await p.waitForTimeout(350);
let apres = await bande();
ok(apres.faits === 1, 'un appui en valide une');
ok(await p.evaluate(id => isDone(today(), id), premier), 'et le journal du jour le sait');
await p.locator('.jline').first().click(); await p.waitForTimeout(350);
ok((await bande()).faits === 0, 'un second appui la dévalide');

console.log('\n== 5. la gestion des habitudes est une feuille ==');
await p.locator('[data-act="habgerer"]').first().click(); await p.waitForTimeout(400);
ok(await p.locator('#modal.open').count() === 1, 'elle s\'ouvre en feuille, pas en onglet');
const dedans = await p.locator('#sheet .hrow').count();
ok(dedans === 2, 'elle liste les deux habitudes, pas les séances (' + dedans + ')');
ok(await p.locator('#sheet [data-act="new"]').count() === 1, 'on peut en ajouter une');
ok(await p.locator('#sheet [data-act="replan"]').count() === 1, 'et préparer demain');
await p.evaluate(() => closeSheet()); await p.waitForTimeout(250);

console.log('\n== 6. le carnet ne déroule plus tout ==');
const nCarnet = await p.evaluate(() => carnet().length);
ok(nCarnet >= 9, 'le carnet contient ' + nCarnet + ' séances');
ok(await p.locator('.lgrow').count() === 8, 'l\'accueil n\'en montre que huit');
ok(await p.locator('[data-act="carnettout"]').count() === 1, 'avec un lien pour tout voir');
await p.locator('[data-act="carnettout"]').click(); await p.waitForTimeout(400);
ok(await p.locator('#sheet .lgrow').count() === nCarnet, 'qui les affiche toutes');
await p.evaluate(() => closeSheet()); await p.waitForTimeout(250);

console.log('\n== 7. les records, sans niveau ==');
const rec = await p.evaluate(() => {
  const c = [...document.querySelectorAll('.frow')].map(e => e.textContent);
  return { n:c.length, txt:c.join(' ') };
});
ok(rec.n >= 1, 'au moins un record affiché (' + rec.n + ')');
ok(/kg|rép/.test(rec.txt), 'avec une charge ou des répétitions');
ok(!/Novice|Débutant|Intermédiaire|Avancé|Élite/.test(rec.txt), 'et aucun niveau');

console.log('\n== 8. la récupération tient sans dérouler treize lignes ==');
ok(await p.locator('.bodywrap .silh').count() === 1, 'la silhouette est là');
ok(await p.locator('.mdet').count() === 1, 'le détail muscle par muscle se replie');
ok(await p.evaluate(() => !document.querySelector('.mdet').open), 'et il est replié par défaut');
ok(await p.locator('.mleg span').count() === 3, 'la légende garde ses trois états');

console.log('\n== 9. rien ne casse ==');
ok(erreurs.length === 0, 'aucune erreur de page' + (erreurs.length ? ' : ' + erreurs[0] : ''));

await b.close();
process.exit(bilan() ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
