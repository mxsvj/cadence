/* Le petit outillage commun : ouvrir l'app, compter les vérifications. */
const { chromium } = require('playwright-core');
const CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const PAGE = 'file://' + require('path').resolve(__dirname, '..', 'index.html');

function compteur(){
  const ratés = []; let n = 0;
  return {
    ok(c, m){ n++; if(!c){ ratés.push(m); console.log('  ✗ ' + m); } else console.log('  ✓ ' + m); },
    bilan(){
      console.log('\n' + (ratés.length
        ? '❌ ' + ratés.length + ' ÉCHEC(S) sur ' + n + ' :\n  ' + ratés.join('\n  ')
        : '✅ ' + n + '/' + n + ' OK'));
      return ratés.length;
    }
  };
}

/* L'app, ouverte et prête : tutoriel passé, aucune requête vers l'extérieur. */
async function ouvrir(opts){
  const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  const ctx = await b.newContext({ viewport:{width:390,height:844}, isMobile:true,
                                   hasTouch:true, locale:'fr-FR', ...(opts||{}) });
  await ctx.route('**://**', r => r.request().url().startsWith('file:') ? r.continue() : r.abort());
  const p = await ctx.newPage();
  const erreurs = [];
  p.on('pageerror', e => erreurs.push('PAGEERROR: ' + e.message));
  p.on('console', m => { if(m.type()==='error' && !/net::ERR|Failed to load|fonts/i.test(m.text()))
                           erreurs.push('CONSOLE: ' + m.text()); });
  await p.goto(PAGE); await p.waitForTimeout(800);
  const passe = p.locator('[data-act="cskip"]');
  if(await passe.count()){ await passe.click(); await p.waitForTimeout(300); }
  return { b, p, erreurs };
}

/* Trois semaines de vie dans l'app : sans données, rien ne se juge. */
async function remplir(p){
  await p.evaluate(() => {
    const j = n => dk(addDays(nowD(), -n));
    state.habits = [
      { id:'h1', name:'Lire 20 min',   icon:'book', type:'rec', days:[0,1,2,3,4,5,6], time:'07:30', color:COLORS[2], steps:'' },
      { id:'h2', name:'Pas de sucre',  icon:'leaf', type:'rec', days:[0,1,2,3,4,5,6], time:'',      color:COLORS[4], steps:'' },
      { id:'s1', name:'Haut du corps', icon:'dumbbell', kind:'seance', days:[0,1,2,3,4,5,6],
        time:'18:30', color:COLORS[0],
        exos:[{x:'tractions',s:3,r:8,w:0,rest:90},{x:'devcouche',s:3,r:8,w:65,rest:120}] },
      { id:'s2', name:'Bas du corps', icon:'dumbbell', kind:'seance', days:[],
        time:'18:30', color:COLORS[3],
        exos:[{x:'squatbarre',s:5,r:6,w:90,rest:150},{x:'sdt',s:4,r:6,w:110,rest:150}] }
    ];
    state.body = { taille:180, age:21, sexe:'h', act:'moyen', obj:'prise' };
    for(let n = 20; n >= 1; n--){
      const k = j(n);
      state.plannedDays[k] = true; state.log[k] = state.log[k] || {};
      state.weight[k] = Math.round((74 + n * 0.04) * 10) / 10;
      state.meals[k] = [{ n:'Poulet riz', kcal:760, prot:52 }];
      if(n % 4) state.log[k].h1 = { done:true, doneAt:'08:12', steps:[] };
      if(n % 3) state.log[k].h2 = { done:true, doneAt:'21:00', steps:[] };
      if(n % 2){
        const h = habitById('s1');
        state.log[k].s1 = { done:true, doneAt:'19:40', steps:[],
          sea:{ d:2700, x: h.exos.map(e => ({ i:e.x, s: Array.from({length:e.s}, () => ({ r:e.r, w:e.w })) })) } };
      }
    }
    save(); render();
  });
  await p.waitForTimeout(400);
}

module.exports = { ouvrir, remplir, compteur, PAGE, CHROME };
