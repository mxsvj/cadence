// Le temps qu'une vraie personne mettrait à répondre sur son téléphone : lire
// le message reçu, réfléchir un instant, puis taper la réponse. La page garde
// l'indicateur « … écrit » jusque-là (le temps de réponse du modèle compris),
// au lieu d'afficher la réponse d'un coup. La réponse reste marquée « IA » :
// ce n'est qu'un rythme.

/** Lire le message reçu : environ 20 caractères par seconde, entre 1 et 6 secondes. */
const READ_CHARS_PER_SECOND = 20;
const READ_MS = [1000, 6000] as const;
/** Réfléchir avant de taper : 1 à 3 secondes. */
const THINK_MS = [1000, 3000] as const;
/** Taper sur un téléphone : environ 3,5 caractères par seconde (une quarantaine de mots par minute), à 15 % près. */
const TYPE_CHARS_PER_SECOND = 3.5;
const TYPE_VARIATION = 0.15;
/** Au moins 3 secondes, au plus 90 : même un long message finit par arriver. */
const MIN_MS = 3000;
const MAX_MS = 90_000;

const clamp = (n: number, [min, max]: readonly [number, number]) => Math.min(max, Math.max(min, n));

/**
 * Le délai total avant d'afficher la réponse `reply` au message `incoming`,
 * en millisecondes ; 0 si HUMAN_TYPING=off.
 */
export function typingDelayMs(
  reply: string,
  { incoming = "", random = Math.random, setting = process.env.HUMAN_TYPING }: { incoming?: string; random?: () => number; setting?: string } = {},
): number {
  if (setting?.trim().toLowerCase() === "off") return 0;
  const read = clamp((incoming.trim().length / READ_CHARS_PER_SECOND) * 1000, READ_MS);
  const think = THINK_MS[0] + random() * (THINK_MS[1] - THINK_MS[0]);
  const speed = TYPE_CHARS_PER_SECOND * (1 + (random() * 2 - 1) * TYPE_VARIATION);
  const typing = (reply.trim().length / speed) * 1000;
  return Math.round(clamp(read + think + typing, [MIN_MS, MAX_MS]));
}
