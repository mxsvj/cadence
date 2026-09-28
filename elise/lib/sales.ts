import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import type { Step } from "./offers";
import type { AiSettings } from "./settings";

// Ce que l'IA a le droit de vendre, maintenant, à cette personne. Tout est
// décidé ici, côté serveur, avant d'écrire la consigne : l'IA ne voit que
// l'étape suivante du script, et seulement si les garde-fous le permettent.

type OfferRow = {
  id: number;
  step_id: number | null;
  price_cents: number;
  status: "proposee" | "achetee" | "offerte" | "retiree";
};

export type SaleContext = {
  /** L'étape suivante du script, dans l'ordre. */
  next: Step | null;
  /** Une offre qui attend encore la réponse de la personne. */
  pending: { priceCents: number; step: Step | null } | null;
  /** Ce que la personne a déjà acheté ou reçu. */
  owned: Step[];
  /** L'IA peut-elle proposer l'étape suivante dans cette réponse ? */
  canPropose: boolean;
};

export async function loadSaleContext(
  admin: SupabaseClient,
  userId: string,
  settings: AiSettings,
): Promise<SaleContext> {
  const [next, offers, userCount, lastOffer, spent, cap] = await Promise.all([
    admin.rpc("prochaine_etape", { p_user: userId }),
    admin.from("offers").select("id, step_id, price_cents, status").eq("user_id", userId).order("id"),
    admin.from("messages").select("id", { count: "exact", head: true }).eq("user_id", userId).eq("role", "user"),
    admin.from("messages").select("id").eq("user_id", userId).eq("kind", "offer").order("id", { ascending: false }).limit(1),
    admin.rpc("depense_du_mois", { p_user: userId }),
    admin.rpc("plafond_de", { p_user: userId }),
  ]);
  for (const r of [next, offers, userCount, lastOffer, spent, cap]) {
    if (r.error) throw new Error(`Contexte de vente illisible : ${r.error.message}`);
  }

  const rows = (offers.data ?? []) as OfferRow[];
  const stepIds = [...new Set(rows.map((o) => o.step_id).filter((id): id is number => id !== null))];
  const steps = new Map<number, Step>();
  if (stepIds.length) {
    const { data, error } = await admin.from("script_steps").select("*").in("id", stepIds);
    if (error) throw new Error(`Étapes illisibles : ${error.message}`);
    for (const s of data as Step[]) steps.set(s.id, s);
  }

  const nextStep = (next.data as Step | null)?.id ? (next.data as Step) : null;
  const pendingRow = rows.find((o) => o.status === "proposee") ?? null;
  const owned = rows
    .filter((o) => o.status === "achetee" || o.status === "offerte")
    .map((o) => (o.step_id !== null ? steps.get(o.step_id) : undefined))
    .filter((s): s is Step => Boolean(s));

  // Messages échangés depuis la dernière offre (tous si aucune offre).
  let sinceLastOffer = Number.POSITIVE_INFINITY;
  const lastOfferId = (lastOffer.data as { id: number }[] | null)?.[0]?.id;
  if (lastOfferId) {
    const { count, error } = await admin
      .from("messages")
      .select("id", { count: "exact", head: true })
      .eq("user_id", userId)
      .gt("id", lastOfferId);
    if (error) throw new Error(`Messages illisibles : ${error.message}`);
    sinceLastOffer = count ?? 0;
  }

  // + 1 : le message que la personne vient d'envoyer, pas encore enregistré.
  const userMessages = (userCount.count ?? 0) + 1;
  const spentCents = Number(spent.data ?? 0);
  const capCents = cap.data === null || cap.data === undefined ? null : Number(cap.data);
  const withinCap = !nextStep?.is_paid || capCents === null || spentCents + nextStep.min_price_cents <= capCents;

  const canPropose =
    nextStep !== null &&
    nextStep.trigger_mode === "ia" &&
    pendingRow === null &&
    userMessages >= settings.sales_min_messages &&
    sinceLastOffer >= settings.sales_gap_messages &&
    withinCap;

  return {
    next: nextStep,
    pending: pendingRow
      ? { priceCents: pendingRow.price_cents, step: pendingRow.step_id !== null ? (steps.get(pendingRow.step_id) ?? null) : null }
      : null,
    owned,
    canPropose,
  };
}

/** Propose l'étape à la personne (la base vérifie l'ordre et borne le prix). */
export async function proposeStep(
  admin: SupabaseClient,
  userId: string,
  stepId: number,
  priceCents: number | null,
  message: string,
): Promise<{ offerId: number; messageId: number }> {
  const { data, error } = await admin.rpc("proposer_etape", {
    p_user: userId,
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
