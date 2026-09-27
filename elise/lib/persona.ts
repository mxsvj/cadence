import "server-only";
import { readFileSync } from "node:fs";
import path from "node:path";

// La persona vit dans `elise-persona.md`, à la racine du projet, pour qu'on
// puisse la modifier sans toucher au code. next.config.ts veille à ce que le
// fichier soit bien embarqué dans le déploiement.

const FIRST_MESSAGE_HEADING = /^##\s+Premier message\s*$/im;

let cached: string | null = null;

/** Le fichier persona complet : c'est l'instruction système du modèle. */
export function getPersona(): string {
  cached ??= readFileSync(path.join(process.cwd(), "elise-persona.md"), "utf8");
  return cached;
}

/** Le texte placé sous le titre « ## Premier message », jusqu'au titre suivant. */
export function getFirstMessage(): string {
  const persona = getPersona();
  const match = FIRST_MESSAGE_HEADING.exec(persona);
  if (!match) {
    throw new Error("elise-persona.md doit contenir un titre « ## Premier message ».");
  }
  const rest = persona.slice(match.index + match[0].length);
  const end = rest.search(/^#{1,2}\s/m);
  const message = (end === -1 ? rest : rest.slice(0, end))
    .replace(/<!--[\s\S]*?-->/g, "")
    .trim()
    // Les retours à la ligne du fichier ne sont là que pour la lisibilité :
    // on ne garde que les sauts de paragraphe.
    .replace(/([^\n])\n(?!\n)/g, "$1 ");
  if (!message) throw new Error("La section « ## Premier message » de elise-persona.md est vide.");
  return message;
}
