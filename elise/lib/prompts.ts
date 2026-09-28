// Tout ce qu'on écrit au modèle en plus de la persona : la fiche, le résumé,
// la date, et les consignes des deux tâches de mémoire (fiche et résumé).

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

/** L'instruction système d'Élise : persona + fiche + résumé + date. */
export function chatSystemPrompt(input: {
  persona: string;
  facts: string[];
  summary: string | null;
  now: Date;
}): string {
  const facts = input.facts.length
    ? input.facts.map((f) => `- ${f}`).join("\n")
    : "Tu ne sais encore rien de cette personne : c'est peut-être votre première conversation.";
  const summary = input.summary?.trim() || "Pas encore de résumé : vos échanges sont tous ci-dessous.";

  return `${input.persona.trim()}

---

## Ce que tu sais de la personne avec qui tu parles

Ces informations viennent de vos conversations précédentes. Sers-t'en avec naturel, comme une amie qui se souvient, sans les réciter.

${facts}

## Résumé de vos conversations plus anciennes

${summary}

## Repères

Nous sommes le ${formatNow(input.now)} (heure de Paris).`;
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
