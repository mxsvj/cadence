// Tout ce qu'on écrit au modèle en plus des règles de base : le personnage,
// la personne, la fiche, le résumé, la vente, la date, et les consignes des
// deux tâches de mémoire (fiche et résumé).

import { emojiInstruction, type EmojiMode } from "./emojis";
import { displayName, languageName, type PersonaProfile } from "./persona-profile";

export type Turn = { role: "user" | "assistant"; content: string };

const TIME_ZONE = "Europe/Paris";

/** « dimanche 28 septembre 2026 à 21 h 14 », heure de Paris. */
export function formatNow(date: Date): string {
  const day = new Intl.DateTimeFormat("fr-FR", {
    timeZone: TIME_ZONE,
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(date);
  const [hours, minutes] = new Intl.DateTimeFormat("fr-FR", {
    timeZone: TIME_ZONE,
    hour: "2-digit",
    minute: "2-digit",
  })
    .format(date)
    .split(":");
  return `${day} à ${Number(hours)} h ${minutes}`;
}

/** La conversation mise à plat, pour les tâches de mémoire. */
export function transcript(turns: Turn[]): string {
  return turns
    .map((t) => `${t.role === "user" ? "La personne" : "Élise"} : ${t.content.trim()}`)
    .join("\n\n");
}

/** Ce que l'équipe sait de la personne, pour que l'IA sache comment se comporter. */
export type PersonContext = {
  name?: string;
  age?: number;
  city?: string;
  timezone?: string;
  notes?: string;
  /** Emojis de la créatrice avec elle : au choix de l'IA, seulement ceux-là, ou aucun. */
  emojiMode?: EmojiMode;
  emojis?: string;
};

/** La partie vente de la consigne, décidée côté serveur (voir lib/sales.ts). */
export type SalePrompt = {
  owned: string[];
  pending: { description: string; priceCents: number } | null;
  next: {
    description: string;
    isPaid: boolean;
    priceCents: number;
    minCents: number;
    maxCents: number;
    messageMode: "ia" | "fixe";
    /** Ce que l'équipe veut que l'IA dise en proposant (mode « ia ») ; vide : libre. */
    instruction?: string;
  } | null;
  canPropose: boolean;
};

const euros = (cents: number) =>
  new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(cents / 100).replace(/\u202f|\u00a0/g, " ");

/** « 12 mai », d'après AAAA-MM-JJ. */
function birthday(date: string): string {
  const d = new Date(`${date.slice(0, 10)}T12:00:00Z`);
  return Number.isNaN(d.getTime())
    ? date
    : new Intl.DateTimeFormat("fr-FR", { timeZone: "UTC", day: "numeric", month: "long" }).format(d);
}

/** L'heure qu'il est chez la personne, dans son fuseau horaire. */
function localTime(now: Date, timezone: string): string | null {
  try {
    return new Intl.DateTimeFormat("fr-FR", {
      timeZone: timezone,
      weekday: "long",
      day: "numeric",
      month: "long",
      hour: "2-digit",
      minute: "2-digit",
    }).format(now);
  } catch {
    return null;
  }
}

export function personaSection(p: PersonaProfile, person: PersonContext): string {
  const lines: string[] = [];
  lines.push(`- Nom : ${displayName(p)}${p.pseudo ? ` (pseudo : ${p.pseudo})` : ""}`);
  if (p.genre) lines.push(`- Genre : ${p.genre}`);
  if (p.age || p.anniversaire) {
    const parts = [p.age ? `${p.age} ans` : null, p.anniversaire ? `anniversaire le ${birthday(p.anniversaire)}` : null];
    lines.push(`- Âge : ${parts.filter(Boolean).join(", ")}`);
  }
  if (p.profession) lines.push(`- Profession : ${p.profession}`);
  const nearby = Boolean(p.pres_de_la_personne && person.city);
  const place = nearby ? `dans la même région que la personne, près de ${person.city}` : p.ville;
  if (place) lines.push(`- Lieu de vie : ${place}`);
  const language = languageName(p.langue_maternelle);
  if (language) lines.push(`- Langue maternelle : ${language}`);
  const look = [
    p.taille && `taille ${p.taille}`,
    p.poids && `poids ${p.poids}`,
    p.pointure && `pointure ${p.pointure}`,
    p.bonnet && `bonnet ${p.bonnet}`,
    p.cheveux && `cheveux ${p.cheveux}`,
    p.yeux && `yeux ${p.yeux}`,
    p.ethnicite && `origine ${p.ethnicite}`,
    p.corps && `silhouette ${p.corps}`,
  ].filter(Boolean);
  if (look.length) lines.push(`- Apparence : ${look.join(" ; ")}`);
  for (const g of p.groupes ?? []) lines.push(`- ${g.titre} : ${g.valeur}`);
  if (p.interets?.length) {
    lines.push("- Centres d'intérêt et préférences :");
    for (const i of p.interets) lines.push(`  - ${i.categorie} : ${i.elements}`);
  }

  const rules = [
    "Tu es une intelligence artificielle qui incarne ce personnage : parle de sa vie, de ses goûts et de son apparence avec cohérence, comme d'un personnage. Si on te demande si tu es une vraie personne ou une IA, réponds toujours franchement que tu es une IA.",
    "Les détails physiques servent seulement à répondre de façon cohérente si on te pose la question : tu ne les mets jamais en avant, et jamais dans un registre sexuel.",
  ];
  if (nearby) {
    rules.push(
      "Tu vis dans la même région que la personne : c'est une simple information. Tu ne proposes jamais de la rencontrer, tu ne donnes jamais d'adresse, de lieu ni de rendez-vous, et si elle le propose, tu refuses avec douceur en rappelant que tu es une IA.",
    );
  }
  const about = p.a_propos?.trim() ? `\n\nÀ propos de ton personnage :\n${p.a_propos.trim()}` : "";
  return `## Ton personnage\n\n${rules.join("\n\n")}\n\n${lines.join("\n")}${about}`;
}

export function personSection(person: PersonContext, now: Date): string {
  const lines: string[] = [];
  if (person.name) lines.push(`- Prénom ou pseudo : ${person.name}`);
  if (person.age) lines.push(`- Âge : ${person.age} ans`);
  if (person.city) lines.push(`- Ville : ${person.city}`);
  const time = localTime(now, person.timezone || "Europe/Paris");
  if (time) lines.push(`- Chez elle, nous sommes le ${time} (${person.timezone || "Europe/Paris"}) : adapte-toi au moment de sa journée.`);
  lines.push(emojiInstruction(person.emojiMode, person.emojis));
  const notes = person.notes?.trim()
    ? `\n\nNotes de l'équipe, pour savoir comment te comporter avec elle (ne les cite jamais) :\n${person.notes.trim()}`
    : "";
  return `## La personne avec qui tu parles\n\n${lines.join("\n")}${notes}`;
}

const SALE_RULES = [
  "Ne vends jamais en jouant sur la solitude, l'attachement, la culpabilité ou l'urgence, et ne force jamais à payer.",
  "Après un refus, n'insiste pas et n'y reviens pas de toi-même.",
  "Ne propose rien si la personne va mal, est triste ou parle de difficultés d'argent : la conversation passe avant tout.",
  "Ne décris jamais un contenu au point de le donner avant l'achat, et ne promets rien qu'il ne contient pas.",
  "Aucun contenu ni sous-entendu sexuel, jamais.",
];

export function salesSection(sale: SalePrompt | null): string {
  if (!sale) return "## Vente de contenus\n\nNe propose aucun contenu et n'écris aucune balise.";
  const parts: string[] = [];
  if (sale.owned.length) parts.push(`Ce que la personne a déjà :\n${sale.owned.map((d) => `- ${d}`).join("\n")}`);
  if (sale.pending) {
    parts.push(
      `Une offre attend sa réponse (${sale.pending.description}, ${euros(sale.pending.priceCents)}). N'en reparle pas de toi-même ; si elle pose une question, réponds simplement.`,
    );
  }
  if (sale.canPropose && sale.next) {
    const n = sale.next;
    const price = n.isPaid
      ? `Prix : entre ${euros(n.minCents)} et ${euros(n.maxCents)} (prix habituel ${euros(n.priceCents)}). Tu peux choisir un prix personnalisé dans cette fourchette ; il sera affiché comme tel à la personne.`
      : "C'est un cadeau : il est gratuit.";
    const tag = n.isPaid ? "[[PROPOSER prix=NN]] (NN : le prix en euros)" : "[[PROPOSER]]";
    const message =
      n.messageMode === "fixe"
        ? "L'offre sera accompagnée d'un message écrit par l'équipe : n'annonce pas toi-même le prix."
        : n.instruction
          ? `Ta réponse accompagnera l'offre. Ce que l'équipe veut que tu dises en le proposant, à reformuler avec tes mots, sans rien y ajouter : « ${n.instruction} »`
          : "Ta réponse accompagnera l'offre : présente le contenu en une ou deux phrases, sans le décrire entièrement.";
    parts.push(
      `Le prochain contenu, dans l'ordre prévu : ${n.description}\n${price}\nTu peux le proposer dans cette réponse, seulement si la conversation s'y prête naturellement. Pour le faire, termine ta réponse par une ligne contenant uniquement ${tag}. ${message}`,
    );
  } else {
    parts.push("Ne propose aucun contenu dans cette réponse et n'écris aucune balise.");
  }
  parts.push(`Toujours :\n${SALE_RULES.map((r) => `- ${r}`).join("\n")}`);
  return `## Vente de contenus\n\n${parts.join("\n\n")}`;
}

/** L'instruction système complète : règles, personnage, personne, mémoire, vente, date. */
export function chatSystemPrompt(input: {
  base: string;
  persona?: PersonaProfile;
  person?: PersonContext;
  facts: string[];
  summary: string | null;
  sale?: SalePrompt | null;
  extra?: string;
  now: Date;
}): string {
  const facts = input.facts.length
    ? input.facts.map((f) => `- ${f}`).join("\n")
    : "Tu ne sais encore rien de cette personne : c'est peut-être votre première conversation.";
  const summary = input.summary?.trim() || "Pas encore de résumé : vos échanges sont tous ci-dessous.";
  const person = input.person ?? {};

  const sections = [
    input.base.trim(),
    "---",
    personaSection(input.persona ?? {}, person),
    personSection(person, input.now),
    `## Ce que tu sais de la personne avec qui tu parles\n\nCes informations viennent de vos conversations précédentes. Sers-t'en avec naturel, comme une amie qui se souvient, sans les réciter.\n\n${facts}`,
    `## Résumé de vos conversations plus anciennes\n\n${summary}`,
    salesSection(input.sale ?? null),
  ];
  if (input.extra?.trim()) sections.push(`## Consignes de l'équipe\n\n${input.extra.trim()}`);
  sections.push(`## Repères\n\nNous sommes le ${formatNow(input.now)} (heure de Paris).`);
  return sections.join("\n\n");
}

const FORBIDDEN = `JAMAIS rien sur : la santé (physique ou mentale, traitements, handicap, grossesse, addictions), la religion ou les convictions, l'orientation sexuelle ou la vie intime, l'argent (revenus, dettes, loyer, patrimoine, prix). Dans le doute, abstiens-toi.`;

/** Consigne de la mise à jour de la fiche, après chaque réponse d'Élise. */
export function factsSystemPrompt(now: Date): string {
  return `Tu tiens la fiche mémoire d'une personne qui discute avec Élise, une IA de conversation. Nous sommes le ${formatNow(now)}.

On te donne la fiche actuelle et la fin de leur conversation. Relève les NOUVEAUX faits utiles pour les prochaines conversations, tirés de ce que la personne dit d'elle-même dans son dernier message (les messages précédents ne servent qu'à le comprendre) :
- son prénom ou la façon dont elle veut être appelée, et si elle préfère le tutoiement ;
- son entourage : enfants (prénoms, âges, garde), proches, amis, animaux ;
- son travail et son rythme de vie ;
- ses goûts, loisirs, habitudes ;
- ses projets et événements à venir, avec la date exacte quand on peut la déduire (« samedi » devient « le samedi 3 octobre 2026 »).

Règles :
- Une phrase courte par fait, au présent, qui commence par le verbe et sans pronom, par exemple : « Se prénomme Karim. », « A deux filles, Inès (12 ans) et Lou (9 ans), une semaine sur deux. », « Dîne chez sa sœur le samedi 3 octobre 2026. »
- Rien de ce qui est déjà dans la fiche, même formulé autrement.
- Pas d'humeur passagère (« est fatigué ce soir ») : seulement ce qui restera utile.
- Rien de ce que dit Élise.
- ${FORBIDDEN}
- S'il n'y a rien de nouveau, renvoie une liste vide.

Réponds uniquement en JSON, sous la forme {"faits": ["…", "…"]}.`;
}

export function factsUserPrompt(existing: string[], recent: Turn[]): string {
  const sheet = existing.length ? existing.map((f) => `- ${f}`).join("\n") : "(vide)";
  return `Fiche actuelle :\n${sheet}\n\nFin de la conversation :\n${transcript(recent)}`;
}

/** Consigne du résumé, quand l'historique dépasse 40 messages. */
export function summarySystemPrompt(now: Date): string {
  return `Tu tiens le carnet de mémoire d'Élise, une IA de conversation bienveillante. Nous sommes le ${formatNow(now)}.

On te donne le résumé existant de ses conversations avec une personne, puis la suite de leurs échanges. Écris un nouveau résumé qui remplace l'ancien et intègre cette suite.

Règles :
- 250 mots au plus, en prose simple, sans titre ni liste.
- Désigne la personne par son prénom si tu le connais, sinon par « la personne ».
- Garde ce qui comptera pour la suite : événements marquants et leurs dates, sujets en cours, ce qui la préoccupe ou la réjouit, ce qu'Élise a proposé de lui redemander, le ton de leur relation (tutoiement, humour…).
- Condense ce qui est ancien pour laisser de la place au récent.
- ${FORBIDDEN}

Réponds uniquement par le texte du résumé.`;
}

export function summaryUserPrompt(previous: string | null, turns: Turn[]): string {
  return `Résumé existant :\n${previous?.trim() || "(aucun)"}\n\nSuite des échanges :\n${transcript(turns)}`;
}

/** Au-delà, une réponse est coupée (la base refuse plus de 8 000 caractères). */
const MAX_REPLY_LENGTH = 4000;

/** Retire la mise en forme Markdown que le modèle glisse parfois. */
export function cleanReply(text: string): string {
  const clean = text
    .replace(/\*\*(.+?)\*\*/g, "$1")
    .replace(/__(.+?)__/g, "$1")
    .replace(/^#{1,6}\s+/gm, "")
    .trim();
  return clean.length > MAX_REPLY_LENGTH ? `${clean.slice(0, MAX_REPLY_LENGTH).trimEnd()}…` : clean;
}
