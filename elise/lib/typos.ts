// De temps en temps, une petite faute de frappe, comme quand on écrit vite
// sur son téléphone : deux lettres inversées, une lettre oubliée ou doublée,
// un accent qui saute. Ajoutée par le serveur (le modèle, à qui on le
// demande, en ferait toujours ou jamais). Jamais dans un nom, un chiffre, un
// prix, ni dans une réponse qui prévient l'équipe ou donne les numéros d'aide.

/** Environ une réponse sur cinq. */
export const TYPO_RATE = 0.2;
/** Seulement dans les mots assez longs pour rester lisibles. */
const MIN_LENGTH = 5;
/** Ce qui doit rester parfaitement lisible : dire qu'elle est une IA. */
const PROTECTED = new Set(["intelligence", "artificielle", "robot", "humaine", "humain"]);

const ACCENTS: Record<string, string> = { é: "e", è: "e", ê: "e", à: "a", â: "a", ç: "c", ù: "u", û: "u", î: "i", ô: "o" };

type Random = () => number;
const pick = <T>(list: T[], random: Random): T => list[Math.min(list.length - 1, Math.floor(random() * list.length))];

/** Une faute dans ce mot (en minuscules, au moins MIN_LENGTH lettres), ou null. */
export function typoIn(word: string, random: Random = Math.random): string | null {
  const kinds: (() => string)[] = [
    // Deux lettres voisines inversées (jamais la première).
    () => {
      const i = 1 + Math.floor(random() * (word.length - 2));
      return word.slice(0, i) + word[i + 1] + word[i] + word.slice(i + 2);
    },
    // Une lettre oubliée (jamais la première).
    () => {
      const i = 1 + Math.floor(random() * (word.length - 1));
      return word.slice(0, i) + word.slice(i + 1);
    },
    // Une lettre doublée.
    () => {
      const i = 1 + Math.floor(random() * (word.length - 1));
      return word.slice(0, i) + word[i] + word.slice(i);
    },
  ];
  const accented = [...word].findIndex((c) => c in ACCENTS);
  if (accented >= 0) kinds.push(() => word.slice(0, accented) + ACCENTS[word[accented]] + word.slice(accented + 1));
  const result = pick(kinds, random)();
  return result !== word ? result : null;
}

/**
 * La réponse, avec parfois une faute de frappe dans un mot ordinaire.
 * HUMAN_TYPOS=off les coupe (essais de bout en bout).
 */
export function addTypo(
  text: string,
  { random = Math.random, setting = process.env.HUMAN_TYPOS, rate = TYPO_RATE }: { random?: Random; setting?: string; rate?: number } = {},
): string {
  if (setting?.trim().toLowerCase() === "off" || random() >= rate) return text;
  // Des mots en minuscules seulement (pas un prénom), sans chiffre ni symbole.
  const words = [...text.matchAll(/(?<![\p{L}\p{N}@/._:-])[\p{Ll}]+(?![\p{L}\p{N}@/._:-])/gu)].filter(
    (m) => m[0].length >= MIN_LENGTH && !PROTECTED.has(m[0]),
  );
  if (!words.length) return text;
  const word = pick(words, random);
  const typo = typoIn(word[0], random);
  if (!typo) return text;
  return text.slice(0, word.index) + typo + text.slice(word.index! + word[0].length);
}
