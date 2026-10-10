/* Le thème : noir et blanc par défaut, et l'encre qui se pose sur l'accent.

   C'est ce dernier point qui avait cassé : l'accent blanc portait un libellé
   blanc, codé en dur. Un bouton parfaitement invisible, et rien pour le dire.
   On mesure donc le contraste de chaque accent, au repos et au survol. */
const { ouvrir, compteur } = require('./commun.js');
const fs = require('fs');
const path = require('path');

const lin = v => (v /= 255) <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
function rgb(c){
  c = c.trim();
  if (c[0] === '#') { let h = c.slice(1);
    if (h.length === 3) h = [...h].map(x => x + x).join('');
    return [0,2,4].map(i => parseInt(h.slice(i, i+2), 16)); }
  return c.match(/\d+/g).slice(0,3).map(Number);
}
const relLum = c => { const [r,g,b] = rgb(c).map(lin); return 0.2126*r + 0.7152*g + 0.0722*b; };
function contraste(a, b){
  const [hi, lo] = [relLum(a), relLum(b)].sort((x,y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

(async () => {
const { b, p, erreurs } = await ouvrir();
const { ok, bilan } = compteur();

console.log('\n== 1. noir et blanc par défaut ==');
const def = await p.evaluate(() => {
  const v = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  state.theme = 'dark'; state.accent = ''; poserAccent(); render();
  const sombre = { bg:v('--bg'), acc:v('--acc'), txt:v('--acc-txt') };
  state.theme = 'light'; poserAccent(); render();
  const clair = { bg:v('--bg'), acc:v('--acc'), txt:v('--acc-txt') };
  state.theme = 'dark'; poserAccent(); render();
  return { sombre, clair };
});
ok(/^#0{6}$|^rgb\(0, 0, 0\)$/i.test(def.sombre.bg), 'le fond sombre est noir (' + def.sombre.bg + ')');
ok(relLum(def.sombre.acc) > 0.7, 'l\'accent est blanc en thème sombre (' + def.sombre.acc + ')');
ok(relLum(def.clair.acc) < 0.1, 'et noir en thème clair (' + def.clair.acc + ')');
/* c'est tout l'intérêt du jeton : l'encre s'inverse avec lui */
ok(relLum(def.sombre.txt) < 0.1 && relLum(def.clair.txt) > 0.7,
   'l\'encre posée sur l\'accent s\'inverse avec le thème');

console.log('\n== 2. chaque accent porte une encre lisible ==');
const accents = await p.evaluate(() => ACCENTS.map(a => ({ id:a.id, n:a.n, c:a.c, h:a.h, t:a.t })));
for (const a of accents) {
  if (!a.id) continue;                     /* le défaut est mesuré plus haut */
  const r = contraste(a.t, a.c), s = contraste(a.t, a.h);
  ok(r >= 4.5 && s >= 4.5, a.n.toLowerCase() + ' : ' + r.toFixed(2) + ':1 au repos, ' +
     s.toFixed(2) + ':1 au survol');
}

console.log('\n== 3. le texte courant tient sur son fond ==');
for (const theme of ['dark','light']) {
  const t = await p.evaluate(th => {
    state.theme = th; render();
    const v = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
    return { txt:v('--txt'), mut:v('--mut'), mut2:v('--mut2'), bg:v('--bg'), surf:v('--surf') };
  }, theme);
  ok(contraste(t.txt, t.surf) >= 4.5,
     theme + ' : texte sur carte ' + contraste(t.txt, t.surf).toFixed(2) + ':1');
  ok(contraste(t.mut, t.surf) >= 4.5,
     theme + ' : gris sur carte ' + contraste(t.mut, t.surf).toFixed(2) + ':1');
  /* mut2 ne porte que des mentions secondaires : 3:1 suffit */
  ok(contraste(t.mut2, t.surf) >= 3,
     theme + ' : gris secondaire ' + contraste(t.mut2, t.surf).toFixed(2) + ':1');
}

console.log('\n== 4. plus aucune encre codée en dur sur l\'accent ==');
const src = fs.readFileSync(path.resolve(__dirname, '..', 'index.html'), 'utf8');
const fautes = src.split('\n')
  .map((l, i) => [i + 1, l])
  .filter(([, l]) => /background:var\(--acc[^)]*\)/.test(l) && /color:#(fff|FFF)/.test(l));
ok(fautes.length === 0, 'aucune règle « fond accent + texte blanc en dur »' +
   (fautes.length ? ' — ligne ' + fautes[0][0] : ''));
ok(!/rgba\(59,\s*130,\s*246/.test(src), 'plus aucun bleu d\'origine codé en rgba');

console.log('\n== 5. la couleur de barre système suit le thème ==');
const meta = await p.evaluate(() => {
  state.theme = 'dark'; render();
  const a = document.querySelector('meta[name="theme-color"]').getAttribute('content');
  state.theme = 'light'; render();
  const b = document.querySelector('meta[name="theme-color"]').getAttribute('content');
  state.theme = 'dark'; render();
  return { a, b };
});
ok(relLum(meta.a) < 0.05, 'sombre : ' + meta.a);
ok(relLum(meta.b) > 0.8, 'clair : ' + meta.b);

console.log('\n== 6. rien ne casse ==');
ok(erreurs.length === 0, 'aucune erreur de page' + (erreurs.length ? ' : ' + erreurs[0] : ''));

await b.close();
process.exit(bilan() ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
