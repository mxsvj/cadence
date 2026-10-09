/* Le script de la page se parse-t-il encore ? C'est la vérification la moins
   chère et celle qui attrape le plus de bêtises. */
const fs = require('fs'), vm = require('vm');
const s = fs.readFileSync(__dirname + '/../index.html', 'utf8');
let n = 0;
for(const m of s.matchAll(/<script>([\s\S]*?)<\/script>/g)){
  n++;
  try{ new vm.Script(m[1], { filename: 'bloc' + n }); }
  catch(e){ console.log('BLOC ' + n + ' : ' + e.message); process.exit(1); }
}
console.log('✅ syntaxe OK (' + n + ' bloc)');
