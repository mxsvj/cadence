// Le profil du personnage que l'IA incarne, réglé par l'équipe dans l'onglet
// « IA ». Partagé entre le navigateur (formulaire) et le serveur (consigne).

export type CustomGroup = { titre: string; valeur: string };
export type InterestCategory = { categorie: string; elements: string };

export type PersonaProfile = {
  nom?: string;
  pseudo?: string;
  genre?: string;
  age?: number;
  anniversaire?: string; // AAAA-MM-JJ
  profession?: string;
  ville?: string;
  /** Se dire dans la même région que la personne (sans jamais proposer de la rencontrer). */
  pres_de_la_personne?: boolean;
  langue_maternelle?: string; // code de langue (fr, it, pt-BR…)
  taille?: string;
  poids?: string;
  pointure?: string;
  bonnet?: string;
  cheveux?: string;
  yeux?: string;
  ethnicite?: string;
  corps?: string;
  /** Tatouages, piercings… tout ce que l'équipe veut ajouter. */
  groupes?: CustomGroup[];
  /** Centres d'intérêt et préférences, rangés par catégories libres. */
  interets?: InterestCategory[];
  /** Tout le reste, en texte libre. */
  a_propos?: string;
  /** Sa personnalité et sa façon d'écrire : les consignes de ton pour l'IA. */
  ton?: string;
};

export const DEFAULT_NAME = "Élise";
export const MIN_PERSONA_AGE = 18;
export const MAX_TEXT = 5000;

export const GENRES = ["Femme", "Homme", "Non binaire"];
export const SILHOUETTES = ["Mince", "Élancée", "Moyenne", "Athlétique", "Musclée", "Pulpeuse", "Ronde", "Forte"];

// Toutes les langues que le navigateur sait nommer : l'équipe peut en
// choisir n'importe laquelle comme langue maternelle du personnage.
const LANGUAGE_CODES = (
  "af ak am ar as az be bg bm bn bo br bs ca cs cy da de dz ee el en eo es et eu fa ff fi fo fr fy ga gd gl gu " +
  "gv ha he hi hr hu hy ia id ig ii is it ja jv ka ki kk kl km kn ko ks ku kw ky lb lg ln lo lt lu lv mg mi mk " +
  "ml mn mr ms mt my nb nd ne nl nn om or os pa pl ps pt qu rm rn ro ru rw sa sd se sg si sk sl sn so sq sr su " +
  "sv sw ta te tg th ti tk to tr tt ug uk ur uz vi wo xh yi yo zh zu ber crs gsw haw kab ht lij nap oc sc scn vec"
).split(" ");

export function languageOptions(): { code: string; nom: string }[] {
  const names = new Intl.DisplayNames(["fr"], { type: "language" });
  return LANGUAGE_CODES.map((code) => {
    const nom = names.of(code) ?? code;
    return { code, nom: nom.charAt(0).toUpperCase() + nom.slice(1) };
  })
    .filter((l) => l.nom.toLowerCase() !== l.code)
    .sort((a, b) => a.nom.localeCompare(b.nom, "fr"));
}

export function languageName(code: string | undefined): string | null {
  if (!code) return null;
  try {
    const nom = new Intl.DisplayNames(["fr"], { type: "language" }).of(code);
    return nom ?? code;
  } catch {
    return code;
  }
}

export function displayName(p: PersonaProfile): string {
  return p.nom?.trim() || p.pseudo?.trim() || DEFAULT_NAME;
}

/** Nettoie un profil reçu d'un formulaire : champs connus, longueurs bornées, âge ≥ 18. */
export function sanitizePersona(input: unknown): { persona: PersonaProfile; error?: string } {
  const src = (typeof input === "object" && input !== null ? input : {}) as Record<string, unknown>;
  const text = (key: string, max = 120) => {
    const v = src[key];
    return typeof v === "string" && v.trim() ? v.trim().slice(0, max) : undefined;
  };
  const persona: PersonaProfile = {
    nom: text("nom", 60),
    pseudo: text("pseudo", 60),
    genre: text("genre", 40),
    anniversaire: text("anniversaire", 10),
    profession: text("profession"),
    ville: text("ville"),
    pres_de_la_personne: src.pres_de_la_personne === true,
    langue_maternelle: text("langue_maternelle", 16),
    taille: text("taille", 20),
    poids: text("poids", 20),
    pointure: text("pointure", 20),
    bonnet: text("bonnet", 20),
    cheveux: text("cheveux", 60),
    yeux: text("yeux", 60),
    ethnicite: text("ethnicite", 80),
    corps: text("corps", 60),
    a_propos: text("a_propos", MAX_TEXT),
    ton: text("ton", MAX_TEXT),
  };
  const age = Number(src.age);
  if (src.age !== undefined && src.age !== "" && src.age !== null) {
    if (!Number.isInteger(age) || age < MIN_PERSONA_AGE || age > 99) {
      return { persona, error: `L'âge du personnage doit être un nombre entier d'au moins ${MIN_PERSONA_AGE} ans.` };
    }
    persona.age = age;
  }
  const pairs = <T>(key: string, a: string, b: string, maxB: number): T[] =>
    (Array.isArray(src[key]) ? (src[key] as Record<string, unknown>[]) : [])
      .map((g) => ({
        [a]: typeof g?.[a] === "string" ? (g[a] as string).trim().slice(0, 60) : "",
        [b]: typeof g?.[b] === "string" ? (g[b] as string).trim().slice(0, maxB) : "",
      }))
      .filter((g) => g[a] && g[b])
      .slice(0, 30) as T[];
  persona.groupes = pairs<CustomGroup>("groupes", "titre", "valeur", 500);
  persona.interets = pairs<InterestCategory>("interets", "categorie", "elements", 1000);
  // On ne garde que les champs remplis.
  for (const key of Object.keys(persona) as (keyof PersonaProfile)[]) {
    const v = persona[key];
    if (v === undefined || v === false || (Array.isArray(v) && v.length === 0)) delete persona[key];
  }
  return { persona };
}
