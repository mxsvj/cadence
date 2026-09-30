// Les codes d'accès des clients (comme une carte de médiathèque) : 8 lettres
// et chiffres, affichés « ABCD-EFGH ». L'alphabet évite les caractères qu'on
// confond (0/O, 1/I/L). Ce module ne contient aucun secret : il sert aussi
// dans le navigateur.

export const CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789";
export const CODE_LENGTH = 8;

/** Un code tiré au hasard (tirage sans biais), déjà mis en forme. */
export function newCode(): string {
  const out: string[] = [];
  const limit = 256 - (256 % CODE_ALPHABET.length); // au-delà, on retire : chaque caractère a la même chance
  while (out.length < CODE_LENGTH) {
    const bytes = new Uint8Array(16);
    globalThis.crypto.getRandomValues(bytes);
    for (const b of bytes) {
      if (b < limit && out.length < CODE_LENGTH) out.push(CODE_ALPHABET[b % CODE_ALPHABET.length]);
    }
  }
  return formatCode(out.join(""));
}

/** Ce que la personne a tapé, sans espaces ni tirets, en majuscules ; null si ce n'est pas un code complet. */
export function normalizeCode(input: unknown): string | null {
  if (typeof input !== "string") return null;
  const clean = input.toUpperCase().replace(/[^A-Z0-9]/g, "");
  if (clean.length !== CODE_LENGTH) return null;
  return [...clean].every((c) => CODE_ALPHABET.includes(c)) ? clean : null;
}

/** « ABCDEFGH » → « ABCD-EFGH ». */
export function formatCode(code: string): string {
  const clean = code.toUpperCase().replace(/[^A-Z0-9]/g, "");
  return `${clean.slice(0, 4)}-${clean.slice(4)}`;
}
