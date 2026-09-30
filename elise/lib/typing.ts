// Le temps qu'une vraie personne mettrait à répondre : lire le message, puis
// taper la réponse sur son téléphone. La page garde l'indicateur « … écrit »
// jusque-là (le temps de réponse du modèle compris), au lieu d'afficher la
// réponse d'un coup. La réponse reste marquée « IA » : ce n'est qu'un rythme.

/** Lire le message et commencer à répondre : entre 1 et 2,5 secondes. */
const READ_MS = [1000, 2500] as const;
/** Une personne qui écrit vite sur son téléphone : environ 7 caractères par seconde. */
const CHARS_PER_SECOND = 7;
/** Jamais moins de 2 secondes, jamais plus de 20 (au-delà, on croirait à une panne). */
const MIN_MS = 2000;
const MAX_MS = 20_000;

/** Le délai total avant d'afficher `text`, en millisecondes ; 0 si HUMAN_TYPING=off. */
export function typingDelayMs(text: string, random: () => number = Math.random, setting = process.env.HUMAN_TYPING): number {
  if (setting?.trim().toLowerCase() === "off") return 0;
  const read = READ_MS[0] + random() * (READ_MS[1] - READ_MS[0]);
  const typing = (text.trim().length / CHARS_PER_SECOND) * 1000;
  return Math.round(Math.min(MAX_MS, Math.max(MIN_MS, read + typing)));
}
