import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import { MESSAGE_COLUMNS, loadFacts, loadMessages, loadSummary, toTurn, type Message } from "./memory";
import { describeStep as describe } from "./offers";
import { fillName, getFirstMessage, getPersona } from "./persona";
import { displayName } from "./persona-profile";
import { chatSystemPrompt, type SalePrompt, type Turn } from "./prompts";
import { loadSaleContext, proposeStep, type SaleContext } from "./sales";
import { ageFrom, type AiSettings, type Contact, type Profile } from "./settings";

// Une réponse de l'IA, de bout en bout : ce qu'elle reçoit (règles, personnage,
// personne, mémoire, vente) et ce qu'on enregistre ensuite.

function toSalePrompt(sale: SaleContext): SalePrompt {
  const next = sale.next;
  return {
    owned: sale.owned.map(describe),
    pending: sale.pending ? { description: describe(sale.pending.step), priceCents: sale.pending.priceCents } : null,
    next: next
      ? {
          description: describe(next),
          isPaid: next.is_paid,
          priceCents: next.price_cents,
          minCents: next.min_price_cents,
          maxCents: next.max_price_cents,
          messageMode: next.message_mode,
          instruction: next.message_mode === "ia" ? next.message_text.trim() : "",
        }
      : null,
    canPropose: sale.canPropose,
  };
}

export async function buildReply(input: {
  supabase: SupabaseClient;
  admin: SupabaseClient;
  userId: string;
  newMessage: string;
  now: Date;
  settings: AiSettings;
  contact: Contact;
  profile: Profile | null;
}) {
  const { supabase, admin, userId, settings, contact, profile } = input;
  const [facts, summary, recent, sale] = await Promise.all([
    loadFacts(supabase, userId),
    loadSummary(supabase, userId),
    loadMessages(supabase, userId, settings.context_messages - 1),
    loadSaleContext(admin, userId, settings),
  ]);

  const system = chatSystemPrompt({
    base: getPersona(),
    persona: settings.persona,
    person: {
      name: profile?.display_name,
      age: profile ? ageFrom(profile.birthdate, input.now) : undefined,
      city: contact.city,
      timezone: contact.timezone,
      notes: contact.notes,
      emojis: contact.emojis,
    },
    facts,
    summary: summary?.summary ?? null,
    sale: toSalePrompt(sale),
    extra: settings.extra_instructions,
    now: input.now,
  });
  const messages: Turn[] = [...recent.map(toTurn), { role: "user", content: input.newMessage }];
  return { system, messages, facts, sale, name: displayName(settings.persona) };
}

async function insertAiMessage(admin: SupabaseClient, userId: string, content: string): Promise<Message> {
  const { data, error } = await admin
    .from("messages")
    .insert({ user_id: userId, role: "assistant", author: "ai", content })
    .select(MESSAGE_COLUMNS)
    .single();
  if (error) throw new Error(`Réponse non enregistrée : ${error.message}`);
  return data as Message;
}

/**
 * Enregistre la réponse de l'IA et, si elle a proposé le contenu suivant et
 * que c'était permis, l'offre qui va avec. Le message de l'offre est la
 * réponse elle-même (message écrit par l'IA) ou le texte fixé par l'équipe.
 */
export async function saveReply(input: {
  admin: SupabaseClient;
  userId: string;
  text: string;
  proposal: { priceCents: number | null } | null;
  sale: SaleContext;
}): Promise<{ messages: Message[]; offerIds: number[] }> {
  const { admin, userId, proposal, sale } = input;
  const text = input.text.trim() || "Je suis là.";
  const step = sale.canPropose ? sale.next : null;

  if (!proposal || !step) return { messages: [await insertAiMessage(admin, userId, text)], offerIds: [] };

  const messages: Message[] = [];
  let offerMessage = text;
  if (step.message_mode === "fixe") {
    messages.push(await insertAiMessage(admin, userId, text));
    offerMessage = step.message_text;
  }
  try {
    const { offerId, messageId } = await proposeStep(admin, userId, step.id, proposal.priceCents, offerMessage);
    const { data, error } = await admin.from("messages").select(MESSAGE_COLUMNS).eq("id", messageId).single();
    if (error) throw error;
    messages.push(data as Message);
    return { messages, offerIds: [offerId] };
  } catch (err) {
    // L'offre a été refusée par la base (ordre, offre déjà en attente…) :
    // la réponse part quand même, sans offre.
    console.error("Offre de l'IA refusée :", err);
    if (step.message_mode !== "fixe") messages.push(await insertAiMessage(admin, userId, text));
    return { messages, offerIds: [] };
  }
}

/** Le message d'accueil : celui des réglages s'il existe, sinon celui du fichier. */
export function firstMessageFor(settings: AiSettings): string {
  const name = displayName(settings.persona);
  const custom = settings.first_message.trim();
  return custom ? fillName(custom, name) : getFirstMessage(name);
}
