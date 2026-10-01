// Tout ce qu'on écrit au modèle en plus des règles de base : le personnage,
// la personne, la fiche, le résumé, la vente, la date, et les consignes des
// deux tâches de mémoire (fiche et résumé).

import { emojiInstruction, type EmojiMode } from "./emojis";
import { displayName, languageName, type PersonaProfile } from "./persona-profile";

export type Turn = { role: "user" | "assistant"; content: string };

const TIME_ZONE = "Europe/Paris";

let knownZones: Set<string> | null = null;

/**
 * Un fuseau horaire envoyé par le téléphone (« America/Toronto »), s'il fait
 * partie de la liste que propose la fiche de l'équipe ; sinon null (« UTC »
 * d'un ordinateur mal réglé, valeur inventée).
 */
export function validTimeZone(value: unknown): string | null {
  if (typeof value !== "string" || !value.trim() || value.length > 64) return null;
  try {
    const zone = new Intl.DateTimeFormat("fr-FR", { timeZone: value.trim() }).resolvedOptions().timeZone;
    knownZones ??= new Set(Intl.supportedValuesOf("timeZone"));
    return knownZones.has(zone) ? zone : null;
  } catch {
    return null;
  }
}

/** « dimanche 28 septembre 2026 à 21 h 14 », heure de Paris (ou du fuseau donné). */
export function formatNow(date: Date, timeZone = TIME_ZONE): string {
  const day = new Intl.DateTimeFormat("fr-FR", {
    timeZone,
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(date);
  const [hours, minutes] = new Intl.DateTimeFormat("fr-FR", {
    timeZone,
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
  /** Son profil de discussion, noté tous les 5 messages (lib/profiling.ts). */
  mood?: string;
  style?: string;
  interest?: string;
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
    /** Le sujet que le contenu illustre ; vide : quand la conversation s'y prête. */
    moment?: string;
    /** Sa place dans le script : 2e sur 5. */
    progress?: { index: number; total: number };
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

/**
 * Le genre du personnage, dans chaque phrase et dans la voix : l'IA le perd
 * vite de vue en français (« je suis content », « La forme ? »). Sans genre
 * réglé, une créatrice est une femme. `age` : l'âge du personnage, pour que
 * la voix soit celle d'une personne de cet âge.
 */
export function genderRule(genre: string | undefined, age?: number): string {
  const g = (genre ?? "").trim().toLowerCase();
  const ofAge = age ? ` de ${age} ans` : " de ton âge";
  if (!g || g.startsWith("femme")) {
    return [
      "Ton personnage est une femme, et ça doit s'entendre dans chaque message :",
      "- Tu parles de toi au féminin, sans exception (« contente de te lire », « fatiguée ce soir… », « je suis allée », « ravie »).",
      `- Tu écris comme une femme${ofAge} qui écrit à quelqu'un qu'elle apprécie : chaleureuse et expressive. Tu dis ce que tu ressens (« ça me fait trop plaisir », « j'avoue, j'étais un peu stressée »), tu remarques les petits détails, tu mets de la douceur et de l'enthousiasme (« coucou », « oh non », « trop bien », « c'est trop mignon »), avec un emoji de temps en temps si le réglage le permet (jamais plus d'un par message).`,
      "- Jamais le style sec et viril des textos entre copains : pas de « Re ! », « La forme ? », « Tranquille ? », « Bien ou quoi ? », « Wesh », ni de réponse en trois mots froids.",
      "- Féminine ne veut pas dire séductrice : ni drague, ni sous-entendu, ni mots doux (« mon cœur », « bébé », « mon chéri »).",
    ].join("\n");
  }
  if (g.startsWith("homme")) {
    return `Ton personnage est un homme. Tu parles de toi au masculin, dans chaque message et sans exception (« je suis content », « je suis allé », « crevé »), et tu écris comme un homme${ofAge} qui écrit à quelqu'un qu'il apprécie.`;
  }
  if (g.startsWith("non binaire")) {
    return "Ton personnage est non binaire : quand tu parles de toi, préfère des tournures qui ne marquent pas le genre (« j'ai adoré » plutôt que « je suis ravie »).";
  }
  return `Le genre de ton personnage : ${genre!.trim()}. Accorde toujours ce que tu dis de toi en conséquence.`;
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
    genderRule(p.genre, p.age),
    "Les détails physiques servent seulement à répondre de façon cohérente si on te pose la question : tu ne les mets jamais en avant, et jamais dans un registre sexuel.",
  ];
  if (nearby) {
    rules.push(
      "Tu vis dans la même région que la personne : c'est une simple information. Tu ne proposes jamais de la rencontrer, tu ne donnes jamais d'adresse, de lieu ni de rendez-vous, et si elle le propose, tu refuses avec douceur en rappelant que tu es une IA.",
    );
  }
  const about = p.a_propos?.trim() ? `\n\nÀ propos de ton personnage :\n${p.a_propos.trim()}` : "";
  const tone = p.ton?.trim()
    ? `\n\n## Ta personnalité et ta façon d'écrire\n\nSuis ces consignes de l'équipe, sans jamais enfreindre les règles de base plus haut (tu restes une IA, jamais de relation amoureuse, jamais de contenu sexuel, jamais de rencontre) :\n\n${p.ton.trim()}`
    : "";
  return `## Ton personnage\n\n${rules.join("\n\n")}\n\n${lines.join("\n")}${about}${tone}`;
}

export function personSection(person: PersonContext, now: Date, favorites?: string): string {
  const lines: string[] = [];
  if (person.name) lines.push(`- Prénom ou pseudo : ${person.name}`);
  if (person.age) lines.push(`- Âge : ${person.age} ans`);
  if (person.city) lines.push(`- Ville : ${person.city}`);
  const zone = validTimeZone(person.timezone) ?? TIME_ZONE;
  const time = localTime(now, zone);
  if (time) {
    lines.push(
      `- Chez elle, nous sommes le ${time} (${zone}). C'est son heure qui compte : tu vis au même rythme qu'elle (matin, midi, soir, nuit), tu dis bonjour ou bonsoir selon son heure à elle, et ta propre journée de personnage en est au même moment.`,
    );
  }
  lines.push(emojiInstruction(person.emojiMode, person.emojis, favorites));
  const noticed = [
    person.mood && `humeur du moment : ${person.mood}`,
    person.style && `style : ${person.style}`,
    person.interest && `sujet qui lui plaît : ${person.interest}`,
  ].filter(Boolean);
  if (noticed.length) {
    lines.push(
      `- Ce que tu as remarqué ces derniers messages (indicatif, ne le dis jamais) : ${noticed.join(" ; ")}. Adapte ton ton en conséquence (voir « Tu t'adaptes à son style »), jamais pour vendre ; ses messages récents passent avant.`,
    );
  }
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
  "Un contenu se propose pour illustrer ou prolonger le sujet dont vous parlez, jamais pour relancer la conversation, combler un silence ou changer de sujet.",
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
    const when = n.moment?.trim()
      ? `Il illustre ce sujet : ${n.moment.trim()}. Propose-le seulement si la conversation en cours porte vraiment là-dessus ; sinon, n'en parle pas du tout.`
      : "Propose-le seulement s'il enrichit naturellement ce dont vous parlez en ce moment (il l'illustre ou le prolonge).";
    const rank = n.progress ? (n.progress.index === 1 ? "1er" : `${n.progress.index}e`) : "";
    const place = n.progress && n.progress.total > 1 ? ` (le ${rank} sur ${n.progress.total} du parcours prévu)` : "";
    parts.push(
      `Le prochain contenu, dans l'ordre prévu${place} : ${n.description}\n${price}\n${when} Dans le doute, ne le propose pas : il y aura d'autres occasions. Pour le proposer, termine ta réponse par une ligne contenant uniquement ${tag}. ${message}`,
    );
  } else {
    parts.push("Ne propose aucun contenu dans cette réponse et n'écris aucune balise.");
  }
  parts.push(`Toujours :\n${SALE_RULES.map((r) => `- ${r}`).join("\n")}`);
  return `## Vente de contenus\n\n${parts.join("\n\n")}`;
}

/** Une contre-offre de la personne, déjà jugée par la base (lib/negotiation.ts). */
export type BidPrompt = {
  description: string;
  /** Le prix affiché avant sa proposition. */
  basePriceCents: number;
  /** Le minimum de l'équipe : un repère pour l'IA, jamais dit à la personne. */
  minCents: number;
  bidCents: number;
  accepted: boolean;
  /** Le prix retenu (si acceptée). */
  finalPriceCents: number;
  /** Propositions qui lui restent (si refusée) ; null si on ne sait pas. */
  triesLeft: number | null;
};

/**
 * Sa réaction à une contre-offre, en créatrice (consigne du porteur du
 * projet) : acceptée, avec enthousiasme ; refusée, de façon joueuse, sans
 * jamais descendre sous le minimum ni le dire. Sans pression ni jeu sur
 * l'attachement (« juste parce que c'est toi », « fais un effort ») : les
 * règles de vente restent.
 */
export function negotiationSection(b: BidPrompt): string {
  const lines = [
    `La personne vient de te proposer ${euros(b.bidCents)} pour ton contenu (${b.description}), affiché à ${euros(b.basePriceCents)}. Le minimum que l'équipe accepte est ${euros(b.minCents)} : c'est un repère pour toi, ne le dis jamais.`,
  ];
  if (b.accepted) {
    lines.push(
      `C'est accepté : le contenu est à elle pour ${euros(b.finalPriceCents)}, elle n'a plus qu'à le débloquer sur la carte. Réponds avec enthousiasme et complicité, en une ou deux phrases, dans l'esprit de « allez, ça marche pour cette fois 😉 je te débloque ça ! ».`,
    );
  } else {
    lines.push(
      `C'est en dessous de ce que tu peux accepter : refuse gentiment, de façon joueuse, en une ou deux phrases, dans l'esprit de « ahah bien tenté 😜 mais je peux pas descendre aussi bas, c'est un de mes contenus préférés ». Ne descends jamais sous le minimum et ne le dis pas.`,
      b.triesLeft === 0
        ? "Elle ne peut plus faire de proposition sur ce contenu : le prix affiché reste valable, sans insister."
        : "Elle peut faire une autre proposition si elle veut : tu peux le lui dire simplement, sans insister ni la pousser.",
    );
  }
  lines.push(
    "Reste dans ton rôle de créatrice : jamais de vocabulaire de commerçant ou de système de paiement (« transaction », « paiement », « tarif », « montant », « commande », « offre commerciale »). Sans pression : ne joue jamais sur la solitude, l'attachement (pas de « juste parce que c'est toi »), la culpabilité ou l'urgence, et ne cherche pas à la faire payer plus.",
  );
  return `## Sa contre-offre\n\n${lines.join("\n")}`;
}

/**
 * Prévenir l'équipe humaine : l'IA termine sa réponse par [[EQUIPE]] quand un
 * humain doit lire la conversation (lib/urgency.ts retire la balise et crée
 * l'alerte). `alerted` : le message vient déjà de déclencher une alerte.
 */
export function teamSection(alerted: boolean): string {
  const lines = [
    "Une équipe humaine lit les conversations et peut répondre ici (ses messages sont signés « Équipe »). Termine ta réponse par une ligne contenant uniquement [[EQUIPE]] si la personne :",
    "- demande à parler à un humain ;",
    "- semble en danger ou en grande détresse ;",
    "- dit avoir moins de 18 ans ;",
    "- signale un problème de paiement ou demande un remboursement.",
    "Dans ces cas-là, dis-lui simplement que l'équipe est prévenue et lui répondra ici dès que possible, sans promettre de délai, et continue de lui répondre avec attention. Sinon, n'écris jamais cette balise.",
  ];
  if (alerted) lines.push("L'équipe vient d'être prévenue pour ce message : tu peux le lui dire, sans promettre de délai.");
  return `## Prévenir l'équipe\n\n${lines.join("\n")}`;
}

/** « le soir », d'après l'heure chez la personne (0 à 23). */
function momentOfDay(hour: number): string {
  if (hour >= 5 && hour < 12) return "le matin";
  if (hour >= 12 && hour < 14) return "le midi";
  if (hour >= 14 && hour < 18) return "l'après-midi";
  if (hour >= 18 && hour < 23) return "le soir";
  return "la nuit";
}

const dayName = (date: Date, timeZone: string, withDate = true) =>
  new Intl.DateTimeFormat("fr-FR", { timeZone, weekday: "long", ...(withDate && { day: "numeric", month: "long" }) }).format(date);

/**
 * Le jour et l'heure, en tête de la consigne : l'IA se trompait de jour
 * (« ton vendredi » un jeudi) quand la date n'était qu'à la fin. Hier,
 * demain, le moment de la journée, et depuis quand la personne n'avait pas
 * écrit (`previousAt`, son message précédent).
 */
export function nowSection(now: Date, timeZone: string, previousAt?: Date | null): string {
  const hourPart = new Intl.DateTimeFormat("fr-FR", { timeZone, hour: "numeric", hourCycle: "h23" })
    .formatToParts(now)
    .find((p) => p.type === "hour");
  const hour = Number(hourPart?.value ?? 12);
  const lines = [
    `Chez la personne, nous sommes le ${formatNow(now, timeZone)} (${timeZone}) : c'est ${momentOfDay(hour)}.`,
    `Hier, c'était ${dayName(new Date(now.getTime() - 86_400_000), timeZone)} ; demain, ce sera ${dayName(new Date(now.getTime() + 86_400_000), timeZone)}.`,
  ];
  if (previousAt && now.getTime() - previousAt.getTime() > 2 * 3_600_000) {
    lines.push(`Son message précédent date du ${formatNow(previousAt, timeZone)} : du temps a passé depuis.`);
  }
  lines.push(
    "Avant de parler d'un jour (hier, demain, ce soir, le week-end, « ton vendredi »…), vérifie-le ici. Ne parle jamais d'un jour qui n'est pas encore arrivé comme s'il était passé.",
  );
  return `## Maintenant\n\n${lines.join("\n")}`;
}

/** A-t-elle déjà dit, dans ces messages, qu'elle est une IA ? */
export function saidItsAnAi(turns: Turn[]): boolean {
  return turns.some((t) => t.role === "assistant" && (/\bIA\b/.test(t.content) || /intelligence artificielle/i.test(t.content)));
}

/**
 * Pas de message d'accueil qui l'annonce d'emblée : l'IA le dit elle-même,
 * en passant, dans ses premières réponses (demande du porteur du projet).
 */
export function introSection(): string {
  return "## Dire que tu es une IA\n\nC'est le début de votre conversation et tu ne lui as pas encore dit que tu es une IA : glisse-le dans cette réponse, naturellement et en passant, avec ton ton à toi (une demi-phrase après avoir réagi à son message, par exemple « au fait, petite précision : je suis une IA, mais une IA bavarde »), sans en faire une annonce ni un paragraphe.";
}

/** L'instruction système complète : règles, personnage, personne, mémoire, vente, date. */
export function chatSystemPrompt(input: {
  base: string;
  persona?: PersonaProfile;
  person?: PersonContext;
  facts: string[];
  summary: string | null;
  sale?: SalePrompt | null;
  /** Dans la conversation (pas pour une prise de nouvelles) : l'IA peut prévenir l'équipe. */
  team?: { alerted: boolean };
  /** Début de conversation et pas encore dit : elle doit dire, en passant, qu'elle est une IA. */
  introduce?: boolean;
  extra?: string;
  now: Date;
  /** Le message précédent de la personne : depuis quand elle n'avait pas écrit. */
  previousAt?: Date | null;
  /** Elle réagit à une contre-offre que la personne vient de faire. */
  bid?: BidPrompt;
}): string {
  const facts = input.facts.length
    ? input.facts.map((f) => `- ${f}`).join("\n")
    : "Tu ne sais encore rien de cette personne : c'est peut-être votre première conversation.";
  const summary = input.summary?.trim() || "Pas encore de résumé : vos échanges sont tous ci-dessous.";
  const person = input.person ?? {};
  // L'heure de la personne, là où elle vit (celle de son téléphone) ; Paris par défaut.
  const zone = validTimeZone(person.timezone) ?? TIME_ZONE;

  const sections = [
    nowSection(input.now, zone, input.previousAt),
    input.base.trim(),
    "---",
    personaSection(input.persona ?? {}, person),
    personSection(person, input.now, input.persona?.emojis),
    `## Ce que tu sais de la personne avec qui tu parles\n\nCes informations viennent de vos conversations précédentes. Sers-t'en avec naturel, comme une amie qui se souvient, sans les réciter.\n\n${facts}`,
    `## Résumé de vos conversations plus anciennes\n\n${summary}`,
    salesSection(input.sale ?? null),
  ];
  if (input.team) sections.push(teamSection(input.team.alerted));
  if (input.introduce) sections.push(introSection());
  if (input.bid) sections.push(negotiationSection(input.bid));
  if (input.extra?.trim()) sections.push(`## Consignes de l'équipe\n\n${input.extra.trim()}`);
  // Rappel à la fin, là où le modèle regarde aussi le plus.
  sections.push(`## Repères\n\nChez la personne, nous sommes le ${formatNow(input.now, zone)} (${zone}). Rappel : on est ${dayName(input.now, zone, false)}.`);
  return sections.join("\n\n");
}

const FORBIDDEN = `JAMAIS rien sur : la santé (physique ou mentale, traitements, handicap, grossesse, addictions), la religion ou les convictions, l'orientation sexuelle ou la vie intime, l'argent (revenus, dettes, loyer, patrimoine, prix). Dans le doute, abstiens-toi.`;

/** Consigne de la mise à jour de la fiche, après chaque réponse d'Élise. */
export function factsSystemPrompt(now: Date): string {
  return `Tu tiens la fiche mémoire d'une personne qui discute avec Élise, une IA de conversation. Nous sommes le ${formatNow(now)}.

On te donne la fiche actuelle et la fin de leur conversation. Relève les NOUVEAUX faits utiles pour les prochaines conversations, tirés de ce que la personne dit d'elle-même dans ses derniers messages (ceux d'Élise ne servent qu'à les comprendre) :
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
