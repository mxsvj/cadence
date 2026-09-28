// Tri des faits proposés par le modèle avant de les ranger dans la fiche.
// Le modèle a pour consigne de ne jamais relever de données sensibles ; ce
// fichier est la ceinture en plus des bretelles : au moindre mot qui touche à
// la santé, la religion, l'orientation sexuelle ou l'argent, le fait est jeté.
// Quitte à jeter parfois un fait anodin : mieux vaut oublier que trop retenir.
//
// Les mots s'écrivent sans accents. Un mot attrape tout ce qui commence par
// lui (« psy » attrape « psychologue ») ; un « ! » final exige le mot entier
// (« foi! » ne doit pas attraper « fois »).

const SENSITIVE_WORDS: Record<string, string[]> = {
  santé: [
    "sante", "malad", "medic", "medecin", "docteur", "hopital", "hospitalis", "clinique", "urgences",
    "traitement", "therap", "psy", "depress", "antidepress", "deprim", "anxi", "anxiolyt",
    "somnifere", "calmant", "angoiss", "burn out",
    "burnout", "insomn", "cancer", "tumeur", "diabet", "cardia", "tension arterielle",
    "cholesterol", "chirurg", "enceinte", "grossesse", "fausse couche", "handicap",
    "addict", "alcool", "drogue", "cannabis", "sevrage", "suicid", "automutil",
    "trouble", "bipolaire", "schizo", "autis", "tdah!", "migraine", "douleur",
    "allergi", "symptom", "diagnost", "ordonnance", "infirm", "kine", "vaccin",
    "covid", "sida!", "vih!", "fauteuil roulant",
  ],
  religion: [
    "relig", "dieu!", "dieux!", "priere", "prier!", "mosquee", "eglise", "synagogue",
    "temple!", "musulman", "islam", "chretien", "catholique", "protestant", "evangel",
    "juif", "juive", "judaism", "bouddh", "hindou", "athee", "agnostique", "croyant",
    "foi!", "ramadan", "careme", "messe!", "bapteme", "spiritualite", "coran", "bible",
    "torah",
  ],
  orientation: [
    "homosex", "hetero", "bisex", "gay!", "gays!", "lesbien", "queer", "lgbt",
    "orientation sexuelle", "transgenre", "non binaire", "sexualite", "sexuel",
    "asexuel", "pansexuel", "coming out",
  ],
  argent: [
    "argent", "salaire", "euro!", "euros!", "dollar", "dette", "credit", "emprunt",
    "loyer", "revenus!", "banque", "bancaire", "impot", "pension alimentaire",
    "chomage", "rsa!", "smic!", "patrimoine", "heritage", "fauche", "budget",
    "economies", "epargne", "facture", "surendett", "huissier", "paie!", "prime!",
    "remuneration", "gagne bien", "gagne mal", "fortune", "riche!", "riches!", "pauvre",
  ],
};

const SENSITIVE_PATTERNS = Object.values(SENSITIVE_WORDS)
  .flat()
  .map((word) => {
    const whole = word.endsWith("!");
    const body = (whole ? word.slice(0, -1) : word).replace(/ /g, "[\\s-]+");
    return new RegExp(`(^|[^a-z])${body}${whole ? "([^a-z]|$)" : ""}`);
  });

/** Minuscules, sans accents ni ponctuation superflue : pour comparer. */
export function normalizeFact(text: string): string {
  return text
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .replace(/[’']/g, " ")
    .replace(/[^a-z0-9\s-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function isSensitive(fact: string): boolean {
  const normalized = normalizeFact(fact);
  return /[€$£]/.test(fact) || SENSITIVE_PATTERNS.some((re) => re.test(normalized));
}

/** Lit la réponse du modèle, même entourée de texte ou de ```json. */
export function parseFactsResponse(raw: string): string[] {
  const match = raw.match(/\{[\s\S]*\}|\[[\s\S]*\]/);
  if (!match) return [];
  try {
    const data: unknown = JSON.parse(match[0]);
    const list = Array.isArray(data) ? data : (data as { faits?: unknown }).faits;
    return Array.isArray(list) ? list.filter((f): f is string => typeof f === "string") : [];
  } catch {
    return [];
  }
}

const MAX_NEW_FACTS_PER_TURN = 5;
const MAX_FACT_LENGTH = 200;

/** Garde les faits nouveaux, courts et sans donnée sensible. */
export function selectNewFacts(candidates: string[], existing: string[]): string[] {
  const seen = new Set(existing.map(normalizeFact));
  const kept: string[] = [];
  for (const candidate of candidates) {
    const fact = candidate.replace(/\s+/g, " ").trim();
    const key = normalizeFact(fact);
    if (!key || fact.length > MAX_FACT_LENGTH) continue;
    if (seen.has(key) || isSensitive(fact)) continue;
    seen.add(key);
    kept.push(fact);
    if (kept.length === MAX_NEW_FACTS_PER_TURN) break;
  }
  return kept;
}
