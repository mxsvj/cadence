/* Le corps et sa rampe de récupération.

   Deux choses à garder : les couleurs d'état forment une rampe ordinale
   valide dans *chaque* thème (c'est la décision prise après avoir mesuré que
   le feu tricolore échouait au daltonisme), et les tracés des muscles
   tiennent dans la silhouette. Les deux se sont déjà cassés en silence. */
const { ouvrir, remplir, compteur } = require('./commun.js');
const fs = require('fs');

/* --- couleur : sRGB -> OKLab, repris du validateur de la méthode dataviz --- */
const lin = v => (v /= 255) <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
function rgb(h){
  h = h.trim().replace('#','');
  if(h.length === 3) h = [...h].map(c => c + c).join('');
  return [0,2,4].map(i => parseInt(h.slice(i, i+2), 16));
}
function oklch(hex){
  const [r,g,bl] = rgb(hex).map(lin);
  const l = Math.cbrt(0.4122214708*r + 0.5363325363*g + 0.0514459929*bl);
  const m = Math.cbrt(0.2119034982*r + 0.6806995451*g + 0.1073969566*bl);
  const s = Math.cbrt(0.0883024619*r + 0.2817188376*g + 0.6299787005*bl);
  const L = 0.2104542553*l + 0.7936177850*m - 0.0040720468*s;
  const A = 1.9779984951*l - 2.4285922050*m + 0.4505937099*s;
  const B = 0.0259040371*l + 0.7827717662*m - 0.8086757660*s;
  let H = Math.atan2(B, A) * 180 / Math.PI; if(H < 0) H += 360;
  return [L, Math.hypot(A, B), H];
}
const relLum = hex => { const [r,g,b] = rgb(hex).map(lin);
                        return 0.2126*r + 0.7152*g + 0.0722*b; };
function contraste(a, b){
  const [hi, lo] = [relLum(a), relLum(b)].sort((x,y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}
/* « rgb(109, 79, 78) » -> « #6D4F4E » */
const enHex = s => '#' + s.match(/\d+/g).slice(0,3)
  .map(n => (+n).toString(16).padStart(2,'0').toUpperCase()).join('');

(async () => {
const { b, p, erreurs } = await ouvrir();
const { ok, bilan } = compteur();
await remplir(p);

console.log('\n== 1. les états passent par des jetons, pas des hex en dur ==');
const src = fs.readFileSync(require('path').resolve(__dirname, '..', 'index.html'), 'utf8');
const blocEtats = src.slice(src.indexOf('var ETATS ='), src.indexOf('var ETATS =') + 260);
ok(/var\(--et-chaud\)/.test(blocEtats) && /var\(--et-recup\)/.test(blocEtats) &&
   /var\(--et-pret\)/.test(blocEtats), 'ETATS pointe sur --et-chaud/recup/pret');
ok(!/#[0-9A-Fa-f]{6}/.test(blocEtats), 'et ne contient plus aucun hex en dur');

/* chaque thème a ses propres pas : un simple miroir du sombre ne tiendrait pas */
for(const theme of ['dark','light']){
  console.log('\n== 2. rampe ordinale valide en thème ' + theme + ' ==');
  const t = await p.evaluate(th => {
    state.theme = th; render();
    const cs = getComputedStyle(document.documentElement);
    const v = n => cs.getPropertyValue(n).trim();
    const carte = document.querySelector('.bodywrap').closest('section.card');
    return { pret:v('--et-pret'), recup:v('--et-recup'), chaud:v('--et-chaud'),
             corps:v('--corps'), surf:getComputedStyle(carte).backgroundColor };
  }, theme);
  const rampe = [t.pret, t.recup, t.chaud].map(c => c[0] === '#' ? c : enHex(c));
  const surf  = t.surf[0] === '#' ? t.surf : enHex(t.surf);
  const Ls = rampe.map(c => oklch(c)[0]);

  /* clarté monotone : l'ordre des pas doit se lire dans la clarté */
  const monte = Ls.every((l,i) => i === 0 || l > Ls[i-1]);
  const descend = Ls.every((l,i) => i === 0 || l < Ls[i-1]);
  ok(monte || descend, 'clarté monotone (' + Ls.map(l => l.toFixed(2)).join(' → ') + ')');

  /* des pas visiblement distincts */
  const ecarts = Ls.slice(1).map((l,i) => Math.abs(l - Ls[i]));
  ok(Math.min(...ecarts) >= 0.06,
     'écart entre pas >= 0,06 (min ' + Math.min(...ecarts).toFixed(3) + ')');

  /* une seule teinte : c'est ce qui rend la rampe lisible sous daltonisme */
  const H = rampe.map(c => oklch(c)[2]);
  let spread = Math.max(...H) - Math.min(...H); if(spread > 180) spread = 360 - spread;
  ok(spread <= 40, 'teinte unique (étalement ' + spread.toFixed(0) + '°)');

  /* le pas le plus proche du fond doit encore se voir */
  const crs = rampe.map(c => contraste(c, surf));
  ok(Math.min(...crs) >= 2.0,
     'tous les pas >= 2:1 sur la carte (min ' + Math.min(...crs).toFixed(2) + ':1)');

  /* « prêt » est le pas le plus proche du corps : un corps reposé reste calme,
     mais il doit rester distinguable du corps neutre */
  const dPret = contraste(rampe[0], t.corps), dChaud = contraste(rampe[2], t.corps);
  ok(dPret < dChaud, '« prêt » est plus proche du corps que « chaud » (' +
     dPret.toFixed(2) + ' < ' + dChaud.toFixed(2) + ')');
  ok(dPret >= 1.1, 'mais reste visible sur le corps (' + dPret.toFixed(2) + ':1)');
}

console.log('\n== 3. la couleur n\'est jamais seule à porter le sens ==');
await p.evaluate(() => { state.theme = 'dark'; render(); });
const leg = await p.evaluate(() =>
  [...document.querySelectorAll('.mleg span')].map(e => e.textContent.trim()));
ok(leg.length === 3, 'trois entrées de légende');
ok(leg.every(x => x.length > 2), 'chacune nommée : ' + leg.join(' / '));

console.log('\n== 4. les tracés tiennent dans la silhouette ==');
for(const face of ['av','ar']){
  const hs = await p.evaluate(f => {
    bodyFace = f; render();
    const svg = document.querySelector('.bodywrap .silh');
    const bb = [...svg.querySelectorAll('path')].map(x => {
      const r = x.getBBox();
      return { x:r.x, y:r.y, x2:r.x + r.width, y2:r.y + r.height };
    });
    return { n:bb.length,
             deborde: bb.filter(r => r.x < -0.5 || r.y < -0.5 || r.x2 > 120.5 || r.y2 > 258.5).length,
             vide: bb.filter(r => (r.x2 - r.x) < 0.3 || (r.y2 - r.y) < 0.3).length };
  }, face);
  ok(hs.n >= 20, face + ' : la silhouette a ses tracés (' + hs.n + ')');
  ok(hs.deborde === 0, face + ' : aucun tracé ne sort du cadre 120×258');
  ok(hs.vide === 0, face + ' : aucun tracé dégénéré');
}

console.log('\n== 5. aucun muscle ne dépasse du corps ==');
/* Un muscle qui sort de la silhouette ne se voit pas forcément à l'œil — il
   peut sortir du côté de l'axe, là où le miroir le recouvre. On échantillonne
   donc le contour de chaque tracé et on demande au navigateur s'il tombe dans
   le corps. Quatre débordements réels sont passés sous le nez comme ça. */
const fuite = await p.evaluate(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', '0 0 120 258');
  svg.style.cssText = 'position:absolute;left:-9999px;width:120px;height:258px';
  document.body.appendChild(svg);
  const tracer = d => { const e = document.createElementNS(NS,'path');
                        e.setAttribute('d', d); svg.appendChild(e); return e; };
  const out = {};
  for (const f of ['av','ar']) {
    const corps = SIL[f].neutre.map(tracer);
    const fautifs = [];
    for (const [id, v] of Object.entries(SIL[f].m)) {
      let dehors = 0;
      (Array.isArray(v) ? v : [v]).forEach(d => {
        const e = tracer(d), L = e.getTotalLength();
        for (let i = 0; i <= 160; i++) {
          const pt = e.getPointAtLength(L * i / 160);
          if (!corps.some(c => c.isPointInFill(pt))) dehors++;
        }
        e.remove();
      });
      if (dehors) fautifs.push(id + ' (' + dehors + ' pts)');
    }
    corps.forEach(c => c.remove());
    out[f] = fautifs;
  }
  svg.remove();
  return out;
});
ok(fuite.av.length === 0, 'face : aucun muscle hors du corps' +
   (fuite.av.length ? ' — ' + fuite.av.join(', ') : ''));
ok(fuite.ar.length === 0, 'dos : aucun muscle hors du corps' +
   (fuite.ar.length ? ' — ' + fuite.ar.join(', ') : ''));

console.log('\n== 6. chaque muscle reçoit bien sa couleur d\'état ==');
const peint = await p.evaluate(() => {
  bodyFace = 'av'; render();
  const g = [...document.querySelectorAll('.bodywrap .silh g')];
  const f = g.map(x => x.getAttribute('fill'));
  return { total:f.length,
           corps: f.filter(c => c === 'var(--corps)').length,
           etats: f.filter(c => /var\(--et-/.test(c)).length,
           orphelins: f.filter(c => /^#/.test(c)).length };
});
ok(peint.corps >= 1, 'le corps neutre est peint en --corps');
ok(peint.etats >= 5, 'les muscles portent une couleur d\'état (' + peint.etats + ')');
ok(peint.orphelins === 0, 'aucun hex en dur dans la silhouette');

console.log('\n== 7. le relief est bien posé sur chaque masse ==');
const rel = await p.evaluate(() => {
  bodyFace = 'av'; render();
  const svg = document.querySelector('.bodywrap .silh');
  const g = [...svg.querySelectorAll('g')];
  return { degrades: svg.querySelectorAll('defs linearGradient').length,
           plein: g.filter(x => !/^url\(/.test(x.getAttribute('fill') || '')).length,
           relief: g.filter(x => /^url\(#rlf/.test(x.getAttribute('fill') || '')).length,
           traits: g.filter(x => x.getAttribute('stroke')).length };
});
ok(rel.degrades === 2, 'les deux dégradés de relief sont définis (' + rel.degrades + ')');
/* chaque masse est posée deux fois : l'aplat, puis le relief par-dessus */
ok(rel.relief === rel.plein, 'chaque masse a son calque de relief (' +
   rel.relief + ' pour ' + rel.plein + ' aplats)');
ok(rel.traits >= 10, 'les muscles portent le trait qui creuse le sillon (' + rel.traits + ')');

console.log('\n== 8. l\'ordre de tracé du dos est respecté ==');
/* Les dorsaux doivent passer AVANT le trapèze : dans l'autre sens le trapèze
   disparaît dessous et le dos n'est plus qu'un bouclier. */
const ordre = await p.evaluate(() => Object.keys(SIL.ar.m));
ok(ordre.indexOf('dos') < ordre.indexOf('trapezes'),
   'les dorsaux sont tracés avant le trapèze (' + ordre.slice(0,3).join(', ') + '…)');

console.log('\n== 9. les muscles à plusieurs chefs gardent leurs chefs ==');
const chefs = await p.evaluate(() => {
  const out = {};
  for(const f of ['av','ar'])
    for(const [k, v] of Object.entries(SIL[f].m))
      out[k] = Array.isArray(v) ? v.length : 1;
  return out;
});
for(const [m, n] of Object.entries({ abdos:5, quadris:3, mollets:3 }))
  if(chefs[m] !== undefined)
    ok(chefs[m] >= n - 1, m + ' a plusieurs tracés (' + chefs[m] + ')');

console.log('\n== 10. rien ne casse ==');
ok(erreurs.length === 0, 'aucune erreur de page' + (erreurs.length ? ' : ' + erreurs[0] : ''));

await b.close();
process.exit(bilan() ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
