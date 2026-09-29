// Les types de la vente, partagés entre le navigateur et le serveur, et
// quelques outils sans secret (lecture de la balise de l'IA, montants).

export type ContentType = "image" | "video" | "texte";

/** Une photo ou une vidéo d'un message du script, dans le dossier privé. */
export type MediaItem = { path: string; kind: "image" | "video" };

/** Au plus 10 photos et vidéos par message du script (la base le vérifie aussi). */
export const MAX_MEDIA = 10;

/**
 * Un message d'un script de vente (visible de l'équipe seulement) : des
 * photos et vidéos, un texte, ou les deux ; gratuit ou payant ; et ce que
 * l'IA dit en le proposant.
 */
export type Step = {
  id: number;
  script_id: number;
  position: number;
  title: string;
  /** Le type principal, déduit du contenu : vidéo s'il y en a une, sinon photo, sinon texte. */
  content_type: ContentType;
  content_text: string;
  media: MediaItem[];
  ai_description: string;
  message_mode: "ia" | "fixe";
  message_text: string;
  /** Le sujet que ce contenu illustre : l'IA ne le propose que si on en parle (vide : quand ça s'y prête). */
  moment?: string;
  trigger_mode: "ia" | "equipe";
  is_paid: boolean;
  price_cents: number;
  min_price_cents: number;
  max_price_cents: number;
};

/** Un script de vente ; creator_id : la créatrice à qui il est, null s'il sert à toutes. */
export type Script = { id: number; name: string; position: number; creator_id?: number | null };

/** Une offre telle que la personne la voit : jamais de prix minimum ici. */
export type Offer = {
  id: number;
  content_type: ContentType;
  photo_count: number;
  video_count: number;
  price_cents: number;
  personalized: boolean;
  status: "proposee" | "achetee" | "offerte" | "retiree";
  bids_refused: number;
  last_bid_cents: number | null;
  last_bid_status: "acceptee" | "refusee" | null;
};

export const OFFER_COLUMNS =
  "id, content_type, photo_count, video_count, price_cents, personalized, status, bids_refused, last_bid_cents, last_bid_status";

/** Le type principal d'un message du script, d'après ce qu'il contient. */
export function mainType(media: MediaItem[]): ContentType {
  if (media.some((m) => m.kind === "video")) return "video";
  return media.length ? "image" : "texte";
}

export function mediaCounts(media: MediaItem[]): { photos: number; videos: number } {
  return {
    photos: media.filter((m) => m.kind === "image").length,
    videos: media.filter((m) => m.kind === "video").length,
  };
}

/**
 * Ce que contient un message, sans rien en montrer : « 3 photos et 1 vidéo »,
 * « 1 photo », ou « un texte » quand il n'y a ni photo ni vidéo.
 */
export function contentLabel(photos: number, videos: number): string {
  const parts: string[] = [];
  if (photos) parts.push(`${photos} photo${photos > 1 ? "s" : ""}`);
  if (videos) parts.push(`${videos} vidéo${videos > 1 ? "s" : ""}`);
  return parts.length ? parts.join(" et ") : "un texte";
}

/**
 * Ce que l'IA sait d'un message du script : sa description et ce qu'il
 * contient (« 3 photos et 1 vidéo »), jamais son titre interne.
 */
export function describeStep(step: Step | null): string {
  if (!step) return "un contenu";
  const { photos, videos } = mediaCounts(step.media ?? []);
  const what = contentLabel(photos, videos);
  const description = step.ai_description.trim();
  return description ? `${description} (${what})` : what;
}

export const MAX_REFUSED_BIDS = 3;

const PROPOSAL = /\[\[\s*PROPOSER(?:\s+prix\s*=\s*([0-9]+(?:[.,][0-9]{1,2})?))?[^\]]*\]\]/gi;

/**
 * L'IA signale qu'elle propose le contenu suivant en ajoutant une balise
 * [[PROPOSER prix=12]] à la fin de sa réponse. On la retire du texte et on en
 * tire le prix voulu (en centimes), que la base ramènera dans la fourchette.
 */
export function parseProposal(reply: string): { text: string; proposal: { priceCents: number | null } | null } {
  let priceCents: number | null = null;
  let found = false;
  const text = reply
    .replace(PROPOSAL, (_, price: string | undefined) => {
      if (!found && price) priceCents = Math.round(Number(price.replace(",", ".")) * 100);
      found = true;
      return "";
    })
    .replace(/[ \t]+\n/g, "\n")
    .trim();
  return { text, proposal: found ? { priceCents } : null };
}

/** « 12,5 » ou « 12.50 » ou « 12 € » → 1250 ; null si illisible. */
export function parseEuros(input: string): number | null {
  const clean = input.replace(/\s|€/g, "").replace(",", ".");
  if (!/^\d+(\.\d{1,2})?$/.test(clean)) return null;
  return Math.round(Number(clean) * 100);
}
