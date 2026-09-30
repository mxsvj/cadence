import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import type { Step } from "./offers";
import type { AiSettings } from "./settings";

// Ce que l'IA a le droit de vendre, maintenant, dans cette conversation
// (une personne, une créatrice). Tout est décidé ici, côté serveur, avant
// d'écrire la consigne : l'IA ne voit que l'étape suivante du script, et
// seulement si tous les garde-fous le permettent. Le plafond de dépenses,
// la pause après un achat et le nombre d'offres payantes par jour valent
// pour la personne, toutes créatrices confondues.

/** Après une prise de nouvelles (lib/relances.ts), messages de la personne avant toute offre. */
export const NO_SALE_AFTER_RELANCE = 3;

type OfferRow = {
  id: number;
  creator_id: number;
  step_id: number | null;
  price_cents: number;
  status: "proposee" | "achetee" | "offerte" | "retiree";
  proposed_by: "ai" | "team";
  created_at: string;
};

/** Pourquoi l'IA ne peut pas proposer maintenant (pour la consigne et pour l'équipe). */
export type SaleBlock =
  | { reason: "fin" }
  | { reason: "equipe" }
  | { reason: "attente" }
  | { reason: "premiers_messages"; remaining: number }
  | { reason: "espacement"; remaining: number }
  | { reason: "nouvelles"; remaining: number }
  | { reason: "plafond" }
  | { reason: "pause"; hours: number }
  | { reason: "quota"; count: number };

export type SaleInput = {
  next: Pick<Step, "trigger_mode" | "is_paid" | "min_price_cents"> | null;
  /** Une offre attend la réponse de la personne (avec n'importe quelle créatrice). */
  pending: boolean;
  /** Messages de la personne dans cette conversation, celui qu'elle vient d'envoyer compris. */
  userMessages: number;
  /** Messages échangés depuis la dernière offre de cette conversation (Infinity s'il n'y en a pas). */
  sinceLastOffer: number;
  /** Messages de la personne depuis la dernière prise de nouvelles (null s'il n'y en a pas). */
  sinceRelance: number | null;
  /** Ce qui reste du plafond du mois (null : pas de plafond). */
  remainingCents: number | null;
  /** Heures depuis le dernier achat (null : aucun achat). */
  hoursSincePurchase: number | null;
  /** Offres payantes proposées par l'IA ces dernières 24 heures. */
  paidOffersToday: number;
};

type SaleRules = Pick<AiSettings, "sales_min_messages" | "sales_gap_messages" | "sales_pause_hours" | "sales_max_per_day">;

/**
 * Tous les garde-fous, dans l'ordre : le premier qui bloque est la raison.
 * Un contenu gratuit échappe au plafond, à la pause et au nombre par jour.
 */
export function saleBlock(input: SaleInput, rules: SaleRules): SaleBlock | null {
  const { next } = input;
  if (!next) return { reason: "fin" };
  if (next.trigger_mode !== "ia") return { reason: "equipe" };
  if (input.pending) return { reason: "attente" };
  if (input.userMessages < rules.sales_min_messages) {
    return { reason: "premiers_messages", remaining: rules.sales_min_messages - input.userMessages };
  }
  if (input.sinceLastOffer < rules.sales_gap_messages) {
    return { reason: "espacement", remaining: rules.sales_gap_messages - input.sinceLastOffer };
  }
  if (input.sinceRelance !== null && input.sinceRelance < NO_SALE_AFTER_RELANCE) {
    return { reason: "nouvelles", remaining: NO_SALE_AFTER_RELANCE - input.sinceRelance };
  }
  if (next.is_paid) {
    if (input.remainingCents !== null && input.remainingCents < next.min_price_cents) return { reason: "plafond" };
    if (rules.sales_pause_hours > 0 && input.hoursSincePurchase !== null && input.hoursSincePurchase < rules.sales_pause_hours) {
      return { reason: "pause", hours: Math.ceil(rules.sales_pause_hours - input.hoursSincePurchase) };
    }
    if (input.paidOffersToday >= rules.sales_max_per_day) return { reason: "quota", count: input.paidOffersToday };
  }
  return null;
}

/** Les garde-fous, réunis : l'IA peut-elle proposer l'étape suivante maintenant ? */
export function mayPropose(input: SaleInput, rules: SaleRules): boolean {
  return saleBlock(input, rules) === null;
}

const plural = (n: number, word: string) => `${n} ${word}${n > 1 ? "s" : ""}`;

/** La même chose, en une phrase pour l'équipe (fiche de la personne). */
export function describeBlock(block: SaleBlock | null, next: Pick<Step, "title"> | null): string {
  if (!block) return `L'IA peut proposer « ${next?.title ?? "le contenu suivant"} » dès que la conversation s'y prête.`;
  switch (block.reason) {
    case "fin":
      return "Le script est terminé pour cette conversation.";
    case "equipe":
      return "Le prochain contenu se propose par l'équipe, depuis cette fiche.";
    case "attente":
      return "Une offre attend déjà sa réponse.";
    case "premiers_messages":
      return `Première offre dans ${plural(block.remaining, "message")} de la personne.`;
    case "espacement":
      return `Prochaine offre dans ${plural(block.remaining, "message")}.`;
    case "nouvelles":
      return `Juste après une prise de nouvelles : encore ${plural(block.remaining, "message")} de la personne.`;
    case "plafond":
      return "Son plafond du mois ne permet pas ce contenu.";
    case "pause":
      return `Pause après son dernier achat : encore ${plural(block.hours, "heure")}.`;
    case "quota":
      return `Déjà ${plural(block.count, "offre payante")} dans les dernières 24 heures.`;
  }
}

export type SaleContext = {
  /** L'étape suivante du script, dans l'ordre. */
  next: Step | null;
  /** Sa place dans le script : 2e sur 5. */
  progress: { index: number; total: number } | null;
  /** Une offre de cette conversation qui attend encore la réponse de la personne. */
  pending: { priceCents: number; step: Step | null } | null;
  /** Ce que la personne a déjà acheté ou reçu dans cette conversation. */
  owned: Step[];
  /** Ce qui reste du plafond du mois (null : pas de plafond). */
  remainingCents: number | null;
  /** L'IA peut-elle proposer l'étape suivante dans cette réponse ? */
  canPropose: boolean;
  /** Sinon, pourquoi. */
  block: SaleBlock | null;
};

const HOUR = 3_600_000;

export async function loadSaleContext(
  admin: SupabaseClient,
  userId: string,
  creatorId: number,
  settings: AiSettings,
  /** Le message que la personne vient d'envoyer, pas encore enregistré, compte-t-il ? */
  incoming = true,
): Promise<SaleContext> {
  const since = new Date(Date.now() - 24 * HOUR).toISOString();
  const conversation = () => admin.from("messages").select("id").eq("user_id", userId).eq("creator_id", creatorId);
  const [next, offers, userCount, lastOffer, lastRelance, spent, cap, lastPurchase] = await Promise.all([
    admin.rpc("prochaine_etape", { p_user: userId, p_creator: creatorId }),
    admin.from("offers").select("id, creator_id, step_id, price_cents, status, proposed_by, created_at").eq("user_id", userId).order("id"),
    admin.from("messages").select("id", { count: "exact", head: true }).eq("user_id", userId).eq("creator_id", creatorId).eq("role", "user"),
    conversation().eq("kind", "offer").order("id", { ascending: false }).limit(1),
    conversation().eq("kind", "relance").order("id", { ascending: false }).limit(1),
    admin.rpc("depense_du_mois", { p_user: userId }),
    admin.rpc("plafond_de", { p_user: userId }),
    admin.from("purchases").select("created_at").eq("user_id", userId).order("created_at", { ascending: false }).limit(1),
  ]);
  for (const r of [next, offers, userCount, lastOffer, lastRelance, spent, cap, lastPurchase]) {
    if (r.error) throw new Error(`Contexte de vente illisible : ${r.error.message}`);
  }

  const rows = ((offers.data ?? []) as OfferRow[]).map((o) => ({ ...o, creator_id: Number(o.creator_id) }));
  const here = rows.filter((o) => o.creator_id === creatorId);
  const nextStep = (next.data as Step | null)?.id ? (next.data as Step) : null;

  // Les étapes utiles : celles des offres de cette conversation, et le script en cours.
  const stepIds = [...new Set(here.map((o) => o.step_id).filter((id): id is number => id !== null))];
  const steps = new Map<number, Step>();
  let progress: SaleContext["progress"] = null;
  const [owned, scriptSteps] = await Promise.all([
    stepIds.length ? admin.from("script_steps").select("*").in("id", stepIds) : Promise.resolve({ data: [], error: null }),
    nextStep ? admin.from("script_steps").select("id").eq("script_id", nextStep.script_id).order("position").order("id") : null,
  ]);
  if (owned.error) throw new Error(`Étapes illisibles : ${owned.error.message}`);
  for (const s of (owned.data ?? []) as Step[]) steps.set(s.id, s);
  if (scriptSteps && !scriptSteps.error && nextStep) {
    const ids = (scriptSteps.data as { id: number }[]).map((s) => s.id);
    progress = { index: ids.indexOf(nextStep.id) + 1, total: ids.length };
  }

  const pendingHere = here.find((o) => o.status === "proposee") ?? null;
  const pendingAnywhere = rows.some((o) => o.status === "proposee");

  // Messages échangés dans cette conversation depuis sa dernière offre.
  const countAfter = async (id: number, userOnly: boolean) => {
    let query = admin.from("messages").select("id", { count: "exact", head: true }).eq("user_id", userId).eq("creator_id", creatorId).gt("id", id);
    if (userOnly) query = query.eq("role", "user");
    const { count, error } = await query;
    if (error) throw new Error(`Messages illisibles : ${error.message}`);
    return count ?? 0;
  };
  const lastOfferId = (lastOffer.data as { id: number }[] | null)?.[0]?.id;
  const lastRelanceId = (lastRelance.data as { id: number }[] | null)?.[0]?.id;
  const extra = incoming ? 1 : 0;
  const [sinceLastOffer, sinceRelance] = await Promise.all([
    lastOfferId ? countAfter(lastOfferId, false) : Number.POSITIVE_INFINITY,
    lastRelanceId ? countAfter(lastRelanceId, true).then((n) => n + extra) : null,
  ]);

  const spentCents = Number(spent.data ?? 0);
  const capCents = cap.data === null || cap.data === undefined ? null : Number(cap.data);
  const remainingCents = capCents === null ? null : Math.max(0, capCents - spentCents);
  const purchasedAt = (lastPurchase.data as { created_at: string }[] | null)?.[0]?.created_at;
  const input: SaleInput = {
    next: nextStep,
    pending: pendingAnywhere,
    userMessages: (userCount.count ?? 0) + extra,
    sinceLastOffer,
    sinceRelance,
    remainingCents,
    hoursSincePurchase: purchasedAt ? (Date.now() - new Date(purchasedAt).getTime()) / HOUR : null,
    paidOffersToday: rows.filter((o) => o.proposed_by === "ai" && o.price_cents > 0 && o.created_at >= since).length,
  };
  const block = saleBlock(input, settings);

  return {
    next: nextStep,
    progress,
    pending: pendingHere
      ? { priceCents: pendingHere.price_cents, step: pendingHere.step_id !== null ? (steps.get(pendingHere.step_id) ?? null) : null }
      : null,
    owned: here
      .filter((o) => o.status === "achetee" || o.status === "offerte")
      .map((o) => (o.step_id !== null ? steps.get(o.step_id) : undefined))
      .filter((s): s is Step => Boolean(s)),
    remainingCents,
    canPropose: block === null,
    block,
  };
}

/** Propose l'étape à la personne, dans cette conversation (la base vérifie l'ordre, le plafond, et borne le prix). */
export async function proposeStep(
  admin: SupabaseClient,
  userId: string,
  creatorId: number,
  stepId: number,
  priceCents: number | null,
  message: string,
): Promise<{ offerId: number; messageId: number }> {
  const { data, error } = await admin.rpc("proposer_etape", {
    p_user: userId,
    p_creator: creatorId,
    p_step: stepId,
    p_prix_cents: priceCents,
    p_message: message,
    p_par: "ai",
    p_auteur: null,
  });
  if (error) throw new Error(`Offre impossible : ${error.message}`);
  const result = data as { offre: { id: number }; message_id: number };
  return { offerId: result.offre.id, messageId: result.message_id };
}
