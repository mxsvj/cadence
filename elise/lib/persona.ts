import "server-only";
import { readFileSync } from "node:fs";
import path from "node:path";
import { DEFAULT_NAME } from "./persona-profile";

// Les règles de base de l'IA vivent dans `elise-persona.md`, à la racine du
// projet, pour qu'on puisse les modifier sans toucher au code. Le personnage
// (nom, âge, apparence…) se règle dans l'espace admin et s'y ajoute.
// next.config.ts veille à ce que le fichier parte avec le déploiement.

const FIRST_MESSAGE_HEADING = /^##\s+Premier message\s*$/im;

let cached: string | null = null;

/** Le fichier des règles de base : le début de l'instruction système. */
export function getPersona(): string {
  cached ??= readFileSync(path.join(process.cwd(), "elise-persona.md"), "utf8");
  return cached;
}

/**
 * Le texte placé sous le titre « ## Premier message », jusqu'au titre
 * suivant, où `{nom}` devient le nom du personnage.
 */
export function getFirstMessage(name: string = DEFAULT_NAME): string {
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
  return fillName(message, name);
}

/** Remplace `{nom}` par le nom du personnage. */
export function fillName(text: string, name: string): string {
  return text.replaceAll("{nom}", name);
}
