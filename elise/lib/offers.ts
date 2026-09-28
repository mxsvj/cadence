// Les types de la vente, partagés entre le navigateur et le serveur, et
// quelques outils sans secret (lecture de la balise de l'IA, montants).

export type ContentType = "image" | "video" | "texte";

/** Une étape d'un script de vente (visible de l'équipe seulement). */
export type Step = {
  id: number;
  script_id: number;
  position: number;
  title: string;
  content_type: ContentType;
  content_text: string;
  media_path: string | null;
  ai_description: string;
  message_mode: "ia" | "fixe";
  message_text: string;
  trigger_mode: "ia" | "equipe";
  is_paid: boolean;
  price_cents: number;
  min_price_cents: number;
  max_price_cents: number;
};

export type Script = { id: number; name: string; position: number };

/** Une offre telle que la personne la voit : jamais de prix minimum ici. */
export type Offer = {
  id: number;
  content_type: ContentType;
  price_cents: number;
  personalized: boolean;
  status: "proposee" | "achetee" | "offerte" | "retiree";
  bids_refused: number;
  last_bid_cents: number | null;
  last_bid_status: "acceptee" | "refusee" | null;
};

export const OFFER_COLUMNS =
  "id, content_type, price_cents, personalized, status, bids_refused, last_bid_cents, last_bid_status";

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
