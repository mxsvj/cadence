/* Les images des exercices : une photo quand elle existe, un corps dessiné
   sinon. Trois façons de se tromper — un exercice sans image, deux exercices
   qui partagent la même, une image qui sort du cadre. */
const { ouvrir, compteur } = require('./commun.js');
const fs = require('fs');

(async () => {
const { b, p, erreurs } = await ouvrir();
const { ok, bilan } = compteur();

console.log('\n== 1. le dossier des photos ==');
const surDisque = fs.readdirSync(__dirname + '/../exos').filter(f => f.endsWith('.jpg'))
                    .map(f => f.replace('.jpg',''));
const declarees = await p.evaluate(() => Object.keys(PHOTOS));
ok(declarees.length === 34, '34 photos déclarées (' + declarees.length + ')');
const orph = surDisque.filter(f => declarees.indexOf(f) < 0);
const manq = declarees.filter(f => surDisque.indexOf(f) < 0);
ok(!orph.length, 'aucun fichier inutilisé' + (orph.length ? ' : ' + orph : ''));
ok(!manq.length, 'aucun fichier manquant' + (manq.length ? ' : ' + manq : ''));
const poids = surDisque.reduce((n,f) => n + fs.statSync(__dirname+'/../exos/'+f+'.jpg').size, 0);
ok(poids < 1200*1024, 'le dossier tient sous un méga : ' + Math.round(poids/1024) + ' Ko');

console.log('\n== 2. chaque exercice a son image ==');
const cov = await p.evaluate(() => {
  const ids = EXOS.map(x => x.id);
  const rend = id => vignetteExo(exoOr(id), 52);
  return { nex:ids.length,
           sansPose: ids.filter(i => !POSES[i]),
           photo:  ids.filter(i => rend(i).indexOf('exophoto') >= 0),
           dessin: ids.filter(i => rend(i).indexOf('exodraw')  >= 0),
           vide:   ids.filter(i => !rend(i)),
           inconnues: Object.keys(PHOTOS).filter(k => ids.indexOf(k) < 0) };
});
ok(cov.sansPose.length === 0, 'chaque exercice a une pose dessinée' +
   (cov.sansPose.length ? ' : ' + cov.sansPose : ''));
ok(cov.inconnues.length === 0, 'aucune photo ne vise un exercice inexistant');
ok(cov.photo.length === 34, '34 affichent leur photo (' + cov.photo.length + ')');
ok(cov.dessin.length === 9, 'les 9 sans photo libre gardent leur dessin (' + cov.dessin.length + ')');
ok(cov.vide.length === 0, 'aucun ne rend le vide');

console.log('\n== 3. les dessins ne mentent pas ==');
const dbl = await p.evaluate(() => {
  const vu = {}, d = [];
  EXOS.forEach(x => { const s = bonhomme(POSES[x.id]); if(vu[s]) d.push(vu[s]+'≡'+x.id); vu[s] = x.id; });
  return d;
});
ok(dbl.length === 0, 'deux exercices ne partagent jamais le même dessin' +
   (dbl.length ? ' : ' + dbl : ''));

console.log('\n== 4. tout tient dans le cadre ==');
/* Le corps est un aplat : son contour est son étendue, il peut aller au bord.
   Le matériel est tracé : il déborde de la moitié de son épaisseur. */
const box = await p.evaluate(() => {
  const ns = 'http://www.w3.org/2000/svg', svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', '0 0 40 40');
  svg.setAttribute('style', 'position:absolute;left:-999px;width:200px;height:200px');
  document.body.appendChild(svg);
  const cadre = el => { const r = el.getBBox(); return [r.x, r.y, r.x+r.width, r.y+r.height]; };
  const out = EXOS.map(x => {
    svg.innerHTML = bonhomme(POSES[x.id]);
    const mt = svg.querySelector('.mt');
    return { id:x.id, co:cadre(svg.querySelector('.co')), mt: mt ? cadre(mt) : null,
             masses:(bonhomme(POSES[x.id]).match(/<path/g)||[]).length };
  });
  svg.remove(); return out;
});
const dehors = (r, m) => r && (r[0] < m || r[1] < m || r[2] > 40-m || r[3] > 40-m);
const dc = box.filter(r => dehors(r.co, 0.2));
ok(!dc.length, 'aucun corps ne sort du cadre' + (dc.length ? ' : ' + dc.map(r=>r.id) : ''));
const dm = box.filter(r => dehors(r.mt, 1.1));
ok(!dm.length, 'aucun matériel ne sort du cadre' + (dm.length ? ' : ' + dm.map(r=>r.id) : ''));
const maigre = box.filter(r => r.masses < 8);
ok(!maigre.length, 'chaque corps est fait d\'au moins huit masses' +
   (maigre.length ? ' : ' + maigre.map(r=>r.id+'('+r.masses+')') : ''));
const petit = box.filter(r => (r.co[2]-r.co[0]) < 10 || (r.co[3]-r.co[1]) < 10);
ok(!petit.length, 'aucun ne se recroqueville dans un coin');

console.log('\n== 5. les photos se chargent vraiment ==');
const chargees = await p.evaluate(() => Promise.all(Object.keys(PHOTOS).map(id =>
  new Promise(r => { const im = new Image();
    im.onload  = () => r({ id, w:im.naturalWidth, h:im.naturalHeight });
    im.onerror = () => r({ id, w:0, h:0 });
    im.src = 'exos/' + id + '.jpg'; }))));
const absentes = chargees.filter(c => !c.w);
ok(!absentes.length, 'chaque photo déclarée existe' + (absentes.length ? ' : ' + absentes.map(c=>c.id) : ''));
ok(!chargees.filter(c => c.w && c.w !== c.h).length, 'et elles sont carrées');
ok(!chargees.filter(c => c.w && c.w < 300).length, 'assez définies pour le mode séance');

console.log('\n== 6. un exercice maison retombe sur la silhouette ==');
const maison = await p.evaluate(() =>
  vignetteExo({ id:'perso1', n:'Mon exo', m:['pecs'], s:[], eq:'rien', u:'rep' }, 52));
ok(maison.indexOf('class="silh') >= 0, 'il reçoit la silhouette de ses muscles');

console.log('\n== 7. rien ne casse ==');
ok(erreurs.length === 0, 'aucune erreur de page' + (erreurs.length ? ' : ' + erreurs[0] : ''));

await b.close();
process.exit(bilan() ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
