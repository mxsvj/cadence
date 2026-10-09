#!/bin/bash
# Toutes les suites, l'une après l'autre. À lancer depuis test/ :  bash tout.sh
cd "$(dirname "$0")" || exit 1
[ -d node_modules ] || npm install --silent
KO=""
for s in syntaxe.js fumee.js structure.js seance.js images.js journal.js; do
  echo ""; echo "══════════ $s ══════════"
  node "$s" 2>&1 | tail -4
  [ "${PIPESTATUS[0]}" -eq 0 ] || KO="$KO $s"
done
echo ""; echo "════════════════════════════════════════"
if [ -n "$KO" ]; then echo "❌ suites en échec :$KO"; exit 1; else echo "✅ toutes les suites passent"; fi
