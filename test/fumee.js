/* Le test de fumée : on ouvre, on remplit, on visite tout et on clique sur
   tout ce qui porte une action. Une fonction supprimée mais encore appelée
   ne se voit qu'à ce moment-là. */
const { chromium } = require('playwright-core');
(async () => {
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args:['--no-sandbox'] });
const ctx = await b.newContext({ viewport:{width:390,height:844}, isMobile:true, hasTouch:true, locale:'fr-FR' });
await ctx.route('**://**', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
const p = await ctx.newPage();
const errs = [];
p.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
p.on('console', m => { if(m.type()==='error' && !/net::ERR|Failed to load|fonts/i.test(m.text())) errs.push('CONSOLE: ' + m.text()); });
await p.goto('file://' + require('path').resolve(__dirname, '..', 'index.html')); await p.waitForTimeout(900);
await p.locator('[data-act="cskip"]').click(); await p.waitForTimeout(350);

await p.evaluate(() => {
  const j = n => dk(addDays(nowD(), -n));
  state.habits.push({ id:'s1', name:'Haut du corps', icon:'dumbbell', kind:'seance', days:[0,1,2,3,4,5,6],
    time:'18:30', color:COLORS[0],
    exos:[{x:'tractions',s:4,r:8,w:0,rest:90},{x:'devcouche',s:4,r:8,w:65,rest:120}] });
  for(let n = 12; n >= 0; n--){
    const k = j(n);
    state.plannedDays[k] = true; state.log[k] = state.log[k] || {};
    state.weight[k] = 74 + n * 0.05;
    state.meals[k] = [{ n:'Poulet riz', kcal:760, prot:52 }];
    state.habits.forEach(h => { if(n % 3) state.log[k][h.id] = { done:true, doneAt:'08:12', steps:[] }; });
  }
  state.body = { taille:180, age:21, sexe:'h', act:'moyen', obj:'prise' };
  save(); render();
});
await p.waitForTimeout(500);

const onglets = await p.evaluate(() => TABS.map(t => t[0]));
console.log('onglets : ' + onglets.join(', '));
for(const t of onglets){
  await p.locator('.tab[data-tab="' + t + '"]').click(); await p.waitForTimeout(450);
}

/* Chaque plein écran (feuille, mode focus, mode séance) bloque les clics
   suivants : on referme tout entre deux actions. */
const ferme = async pg => { await pg.evaluate(() => {
  try{ if(typeof closeSheet==='function') closeSheet(); }catch(e){}
  try{ if(typeof focusQuit==='function') focusQuit(); }catch(e){}
  try{ if(typeof runClose==='function') runClose(); }catch(e){}
  ['#focus','#run','#sheet','#modal'].forEach(sel => {
    const el = document.querySelector(sel); if(el) el.classList.remove('open');
  });
}).catch(()=>{}); };

/* on clique sur toutes les actions visibles, onglet par onglet */
let clics = 0;
for(const t of onglets){
  await ferme(p);
  await p.locator('.tab[data-tab="' + t + '"]').click(); await p.waitForTimeout(350);
  const actes = await p.evaluate(() => [...new Set([...document.querySelectorAll('[data-act]')]
      .map(e => e.getAttribute('data-act')))].filter(a =>
      !['tab','del','habdel','exodel','logout','retuto','import','export','runquit'].includes(a)));
  for(const a of actes){
    const el = p.locator('[data-act="' + a + '"]').first();
    if(await el.count() === 0) continue;
    try{ await el.click({ timeout:1200, force:true }); clics++; await p.waitForTimeout(110); }catch(e){}
    await ferme(p);
    await p.waitForTimeout(60);
  }
}
console.log(clics + ' actions cliquées');
await b.close();
if(errs.length){ console.log('\n' + errs.length + ' ERREUR(S) :'); [...new Set(errs)].forEach(e => console.log('  ' + e)); process.exit(1); }
console.log('aucune erreur');
})().catch(e => { console.error(e); process.exit(1); });
