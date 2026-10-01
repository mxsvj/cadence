import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import { buildReply, saveReply } from "./conversation";
import { CHAT_TEMPERATURE, generate } from "./llm";
import type { Message } from "./memory";
import { describeStep, parseProposal, type Step } from "./offers";
import { cleanReply, type BidPrompt } from "./prompts";
import { aiMayReply, loadContact, loadCreator, loadProfile, loadSettings } from "./settings";
import { parseTeamFlag } from "./urgency";

// Après une contre-offre (que la base a déjà acceptée ou refusée), la
// créatrice réagit dans la conversation, comme elle le ferait elle-même.

export type BidResult = { statut: "acceptee" | "refusee"; prix_cents: number; essais_restants?: number };

const euros = (cents: number) =>
  new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(cents / 100).replace(/ | /g, " ");

/**
 * Sa réaction, écrite et enregistrée. Rien si l'IA ne répond pas à cette
 * personne (mode manuel, main prise, personne décochée) ou si une urgence
 * est ouverte : l'équipe s'en occupe.
 */
export async function negotiationReply(input: {
  supabase: SupabaseClient;
  admin: SupabaseClient;
  userId: string;
  offer: { creator_id: number; step_id: number | null };
  basePriceCents: number;
  bidCents: number;
  result: BidResult;
  timezone?: string | null;
  now?: Date;
}): Promise<Message[]> {
  const { supabase, admin, userId, result } = input;
  const creatorId = Number(input.offer.creator_id);
  const [settings, creator, contact, profile, step] = await Promise.all([
    loadSettings(admin),
    loadCreator(admin, creatorId),
    loadContact(admin, userId, creatorId),
    loadProfile(supabase, userId),
    input.offer.step_id
      ? admin.from("script_steps").select("*").eq("id", input.offer.step_id).maybeSingle()
      : Promise.resolve({ data: null, error: null }),
  ]);
  if (!creator?.active || !aiMayReply(settings, contact)) return [];
  const s = (step.data ?? null) as Step | null;
  const bid: BidPrompt = {
    description: describeStep(s),
    basePriceCents: input.basePriceCents,
    minCents: s?.min_price_cents ?? input.basePriceCents,
    bidCents: input.bidCents,
    accepted: result.statut === "acceptee",
    finalPriceCents: result.prix_cents,
    triesLeft: result.statut === "refusee" ? (result.essais_restants ?? null) : null,
  };
  const context = await buildReply({
    supabase,
    admin,
    userId,
    creator,
    // Ce que la personne vient de faire, dit au modèle (pas enregistré dans la conversation).
    newMessage: `(Je te propose ${euros(input.bidCents)} pour ton contenu.)`,
    now: input.now ?? new Date(),
    settings,
    contact,
    profile,
    timezone: input.timezone,
    bid,
  });
  if (context.sale.block?.reason === "urgence") return [];
  const raw = cleanReply(await generate({ system: context.system, messages: context.messages, temperature: CHAT_TEMPERATURE }));
  const text = parseProposal(parseTeamFlag(raw).text).text;
  if (!text) return [];
  const { messages } = await saveReply({ admin, userId, creatorId, text, proposal: null, sale: context.sale });
  return messages;
}
