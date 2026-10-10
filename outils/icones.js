/* Regénère les icônes de l'app (icon-192.png, icon-512.png).

   Elles avaient été produites une fois, source perdue : changer l'identité
   voulait dire les refaire à la main. Elles se refabriquent maintenant d'une
   commande, depuis la même définition que le reste du thème.

       node outils/icones.js

   Playwright vit dans test/node_modules : c'est le seul endroit du dépôt qui
   l'installe, inutile d'en poser une seconde copie ici.

   Le dessin : un anneau ouvert — la cadence, le cycle qui tourne — et le C
   de Cadence au centre. En noir et blanc, l'anneau et la lettre partagent la
   même encre ; c'est le fond qui fait tout le contraste. */
const { chromium } = require('../test/node_modules/playwright-core');
const CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const path = require('path');

const FOND  = '#000000';
const ENCRE = '#FFFFFF';

function svg(n){
  /* l'anneau est ouvert en haut à droite : un cycle en cours, pas un cercle fermé */
  return '<svg xmlns="http://www.w3.org/2000/svg" width="' + n + '" height="' + n +
    '" viewBox="0 0 512 512">' +
    '<rect width="512" height="512" fill="' + FOND + '"/>' +
    '<path d="M256 84 A172 172 0 1 0 428 256" fill="none" stroke="' + ENCRE +
      '" stroke-width="34" stroke-linecap="round"/>' +
    '<text x="256" y="330" font-size="236" text-anchor="middle" fill="' + ENCRE +
      '" font-family="Helvetica,Arial,sans-serif" font-weight="700">C</text>' +
    '</svg>';
}

(async () => {
  const b = await chromium.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  const racine = path.resolve(__dirname, '..');
  for (const n of [192, 512]) {
    const p = await b.newPage();
    await p.setViewportSize({ width: n, height: n });
    await p.setContent('<body style="margin:0">' + svg(n) + '</body>');
    await p.waitForTimeout(250);
    const f = path.join(racine, 'icon-' + n + '.png');
    await p.screenshot({ path: f, omitBackground: false });
    console.log('écrit : ' + f);
    await p.close();
  }
  await b.close();
})();
