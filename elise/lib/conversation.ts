import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import { MESSAGE_COLUMNS, loadFacts, loadMessages, loadSummary, toTurn, type Message } from "./memory";
import { describeStep as describe } from "./offers";
import { fillName, getFirstMessage, getPersona } from "./persona";
import { displayName } from "./persona-profile";
import { chatSystemPrompt, saidItsAnAi, type SalePrompt, type Turn } from "./prompts";
import { loadSaleContext, proposeStep, type SaleContext } from "./sales";
import { ageFrom, type AiSettings, type Contact, type Creator, type Profile } from "./settings";

// Une réponse de l'IA, de bout en bout : ce qu'elle reçoit (règles, personnage,
// personne, mémoire, vente) et ce qu'on enregistre ensuite. Tout se passe
// dans une seule conversation (une personne, une créatrice) : rien de ce qui
// a été dit à une autre créatrice n'y entre.

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
          moment: next.moment ?? "",
          progress: sale.progress ?? undefined,
        }
      : null,
    canPropose: sale.canPropose,
  };
}

function previousUserMessageAt(recent: Message[]): Date | null {
  const last = recent.findLast((m) => m.role === "user");
  return last ? new Date(last.created_at) : null;
}

/** Elle dit qu'elle est une IA, au plus tard en répondant à ce message de la personne. */
export const INTRO_WITHIN = 3;

export async function buildReply(input: {
  supabase: SupabaseClient;
  admin: SupabaseClient;
  userId: string;
  creator: Creator;
  newMessage: string;
  now: Date;
  settings: AiSettings;
  contact: Contact;
  profile: Profile | null;
  /** Le message vient de déclencher une alerte d'urgence (lib/urgency.ts). */
  teamAlerted?: boolean;
  /** Le fuseau horaire du téléphone de la personne ; sinon, celui de sa fiche. */
  timezone?: string | null;
}) {
  const { supabase, admin, userId, creator, settings, contact, profile } = input;
  const [facts, summary, recent, loaded] = await Promise.all([
    loadFacts(supabase, userId, creator.id),
    loadSummary(supabase, userId, creator.id),
    loadMessages(supabase, userId, creator.id, settings.context_messages - 1),
    loadSaleContext(admin, userId, creator.id, settings),
  ]);
  // Le message vient de prévenir l'équipe : aucune offre dans cette réponse.
  const sale: SaleContext = input.teamAlerted ? { ...loaded, canPropose: false, block: { reason: "urgence" } } : loaded;

  const system = chatSystemPrompt({
    base: getPersona(),
    persona: creator.persona,
    person: {
      name: profile?.display_name,
      age: profile ? ageFrom(profile.birthdate, input.now) : undefined,
      city: contact.city,
      timezone: input.timezone || contact.timezone,
      notes: contact.notes,
      emojiMode: contact.emoji_mode,
      emojis: contact.emojis,
    },
    facts,
    summary: summary?.summary ?? null,
    sale: toSalePrompt(sale),
    team: { alerted: input.teamAlerted ?? false },
    // Ses trois premiers messages : si elle ne l'a pas encore dit, elle dit qu'elle est une IA.
    introduce: sale.userMessages <= INTRO_WITHIN && !saidItsAnAi(recent.map(toTurn)),
    extra: settings.extra_instructions,
    now: input.now,
    // Son dernier message avant celui-ci (pas encore enregistré) : depuis quand elle n'avait pas écrit.
    previousAt: previousUserMessageAt(recent),
  });
  const messages: Turn[] = [...recent.map(toTurn), { role: "user", content: input.newMessage }];
  return { system, messages, facts, summary, sale, name: displayName(creator.persona) };
}

async function insertAiMessage(admin: SupabaseClient, userId: string, creatorId: number, content: string): Promise<Message> {
  const { data, error } = await admin
    .from("messages")
    .insert({ user_id: userId, creator_id: creatorId, role: "assistant", author: "ai", content })
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
  creatorId: number;
  text: string;
  proposal: { priceCents: number | null } | null;
  sale: SaleContext;
}): Promise<{ messages: Message[]; offerIds: number[] }> {
  const { admin, userId, creatorId, proposal, sale } = input;
  const text = input.text.trim() || "Je suis là.";
  const step = sale.canPropose ? sale.next : null;

  if (!proposal || !step) return { messages: [await insertAiMessage(admin, userId, creatorId, text)], offerIds: [] };

  const messages: Message[] = [];
  let offerMessage = text;
  if (step.message_mode === "fixe") {
    messages.push(await insertAiMessage(admin, userId, creatorId, text));
    offerMessage = step.message_text;
  }
  try {
    const { offerId, messageId } = await proposeStep(admin, userId, creatorId, step.id, proposal.priceCents, offerMessage);
    const { data, error } = await admin.from("messages").select(MESSAGE_COLUMNS).eq("id", messageId).single();
    if (error) throw error;
    messages.push(data as Message);
    return { messages, offerIds: [offerId] };
  } catch (err) {
    // L'offre a été refusée par la base (ordre, offre déjà en attente…) :
    // la réponse part quand même, sans offre.
    console.error("Offre de l'IA refusée :", err);
    if (step.message_mode !== "fixe") messages.push(await insertAiMessage(admin, userId, creatorId, text));
    return { messages, offerIds: [] };
  }
}

/** Le message d'accueil : celui de la créatrice s'il existe, sinon celui du fichier. */
export function firstMessageFor(creator: Pick<Creator, "persona" | "first_message">): string {
  const name = displayName(creator.persona);
  const custom = creator.first_message.trim();
  return custom ? fillName(custom, name) : getFirstMessage(name);
}
