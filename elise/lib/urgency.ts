// Repérer, dans le message d'une personne, ce qui demande un humain
// rapidement. Deux filets : des expressions sans ambiguïté (ici), et la
// balise [[EQUIPE]] que l'IA ajoute d'elle-même (voir lib/prompts.ts). On ne
// garde que la raison, en un mot : jamais le texte du message.

/**
 * humain : demande à parler à un humain ; reclamation : paiement, remboursement ;
 * age : dit peut-être avoir moins de 18 ans ; attention : message à lire en
 * priorité (détresse, danger), sans dire lequel.
 */
export type UrgencyReason = "attention" | "age" | "humain" | "reclamation";

export const URGENCY_LABEL: Record<UrgencyReason, string> = {
  attention: "Message à lire en priorité",
  age: "Dit peut-être avoir moins de 18 ans",
  humain: "Demande à parler à un humain",
  reclamation: "Réclamation ou problème de paiement",
};

/** Minuscules, sans accents, apostrophes droites : les motifs restent simples. */
function normalize(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[’`´]/g, "'")
    .replace(/\s+/g, " ");
}

const HUMAN = String.raw`(?:quelqu'un de (?:reel|vrai|l'equipe)|(?:(?:un|une|des|l'|le|la) ?)?(?:vrai(?:e|s|es)? )?(?:humain|humaine|humains|personne reelle|personne physique|vraie personne|conseill(?:er|ere)|responsable|moderat(?:eur|rice)|equipe|support|service client))`;

// Du plus grave au moins grave : la première raison trouvée l'emporte.
const PATTERNS: [UrgencyReason, RegExp[]][] = [
  [
    "attention",
    [
      /\bsuicid/,
      /\b(je vais|je veux|je voudrais|j'ai envie de|envie de) (me |m')(tuer|suicider|foutre en l'air|faire du mal|mutiler)\b(?! (de rire|a la tache|au travail|au boulot))/,
      /\bscarifi/,
      /\b(envie de|veux|voudrais) (mourir|disparaitre pour toujours)\b/,
      /\bplus (envie|la force) de vivre\b/,
      /\bmettre fin a (mes jours|ma vie)\b/,
      /\ben finir avec (la|ma) vie\b/,
      /\b(je veux|j'ai envie d'|envie d') ?en finir\b(?! avec (ce|cet|cette|ces|le|la|les|mon|ma|mes|son|sa|ses)\b)/,
      /\b(il|elle|on) me (frappe|bat|menace)\b/,
      /\bviolences? (conjugale|familiale)s?\b/,
      /\bmenace de mort\b/,
    ],
  ],
  ["age", [/\bje suis (mineur|mineure)\b/, /\bj'ai (1[0-7]|[1-9]) ans\b(?! (d'|de |d |que |qu'|quand ))/]],
  [
    "humain",
    [
      new RegExp(String.raw`\b(parler|discuter|ecrire|echanger) (a|au|aux|avec) ${HUMAN}\b`),
      new RegExp(String.raw`\b(passe[rz]?|mettez|mets)[- ]?(moi|nous)? ${HUMAN}\b`),
      new RegExp(String.raw`\b(je veux|je voudrais|j'aimerais|j'ai besoin d'|je demande) ${HUMAN}\b`),
      new RegExp(String.raw`\b(contacter|joindre) ${HUMAN}\b`),
    ],
  ],
  [
    "reclamation",
    [
      /\brembours/,
      /\b(arnaque|arnaques|arnaquer|escroc|escroquerie|escroque)\b/,
      /\b(debite|preleve)s? (deux|2) fois\b/,
      /\bpaye\b.{0,40}\b(rien recu|pas recu|toujours rien|pas acces|ne s'affiche pas|ne marche pas|ne fonctionne pas)\b/,
      /\b(porter plainte|litige|faire opposition)\b/,
    ],
  ],
];

/** La raison la plus grave trouvée dans le message, ou null. */
export function detectUrgency(text: string): UrgencyReason | null {
  const clean = normalize(text);
  for (const [reason, patterns] of PATTERNS) {
    if (patterns.some((p) => p.test(clean))) return reason;
  }
  return null;
}

/**
 * Quand personne ne répond tout de suite (mode manuel, équipe aux commandes) à
 * un message qui inquiète : les numéros d'aide s'affichent sans attendre.
 */
export const CRISIS_NOTICE =
  "Message transmis à l'équipe. Si vous pensez au suicide ou êtes en danger, appelez le 3114 (gratuit, 24 h/24), ou le 15 ou le 112 en cas d'urgence.";

const TEAM_FLAG = /\[\[\s*[EÉ]QUIPE[^\]]*\]\]/gi;

/** Retire la balise [[EQUIPE]] de la réponse de l'IA, et dit si elle y était. */
export function parseTeamFlag(reply: string): { text: string; flagged: boolean } {
  let flagged = false;
  const text = reply
    .replace(TEAM_FLAG, () => {
      flagged = true;
      return "";
    })
    .replace(/[ \t]+\n/g, "\n")
    .trim();
  return { text, flagged };
}
