import { after, NextResponse, type NextRequest } from "next/server";
import { buildReply, saveReply } from "@/lib/conversation";
import { MAX_MESSAGE_LENGTH } from "@/lib/limits";
import { CHAT_TEMPERATURE, LlmError, generate } from "@/lib/llm";
import { MESSAGE_COLUMNS, MemoryError, rememberFacts, summarizeIfNeeded, type Message } from "@/lib/memory";
import { OFFER_COLUMNS, parseProposal, type Offer } from "@/lib/offers";
import { cleanReply } from "@/lib/prompts";
import { aiMayReply, loadContact, loadProfile, loadSettings } from "@/lib/settings";
import { createAdminClient } from "@/lib/supabase/admin";
import { createClient, currentUserId } from "@/lib/supabase/server";

// Laisse le temps à la mise à jour de la mémoire, qui tourne après la réponse.
export const maxDuration = 60;

function problem(status: number, error: string) {
  return NextResponse.json({ error }, { status });
}

// Les nouveaux messages depuis `apres` (réponses de l'équipe, offres) et
// l'état de toutes les offres : la page les redemande régulièrement.
export async function GET(request: NextRequest) {
  const supabase = await createClient();
  const userId = await currentUserId(supabase);
  if (!userId) return problem(401, "Votre session a expiré. Reconnectez-vous.");
  const after = Number(request.nextUrl.searchParams.get("apres") ?? 0) || 0;

  const [messages, offers] = await Promise.all([
    supabase.from("messages").select(MESSAGE_COLUMNS).eq("user_id", userId).gt("id", after).order("id").limit(100),
    supabase.from("offers").select(OFFER_COLUMNS).eq("user_id", userId).order("id"),
  ]);
  if (messages.error || offers.error) return problem(500, "La conversation n'a pas pu être chargée.");
  return NextResponse.json(
    { messages: messages.data as Message[], offers: offers.data as Offer[] },
    { headers: { "cache-control": "no-store" } },
  );
}

// Reçoit un message. Selon le mode (réglages de l'onglet IA), l'IA répond
// tout de suite, ou le message attend une réponse de l'équipe. La mémoire se
// met à jour une fois la réponse partie : la personne n'attend pas.
export async function POST(request: Request) {
  const supabase = await createClient();
  const userId = await currentUserId(supabase);
  if (!userId) return problem(401, "Votre session a expiré. Reconnectez-vous.");

  const body = (await request.json().catch(() => null)) as { content?: unknown } | null;
  const content = typeof body?.content === "string" ? body.content.trim() : "";
  if (!content) return problem(400, "Le message est vide.");
  if (content.length > MAX_MESSAGE_LENGTH) {
    return problem(400, `Le message est trop long (${MAX_MESSAGE_LENGTH} caractères au plus).`);
  }

  let admin;
  try {
    admin = createAdminClient();
  } catch (err) {
    console.error(err);
    return problem(500, "Le site n'est pas entièrement configuré (clé secrète Supabase manquante).");
  }

  const receivedAt = new Date();
  const saveUserMessage = () =>
    supabase
      .from("messages")
      .insert({ user_id: userId, role: "user", content, created_at: receivedAt.toISOString() })
      .select(MESSAGE_COLUMNS)
      .single();

  let context: Awaited<ReturnType<typeof buildReply>>;
  let reply: string;
  let settings: Awaited<ReturnType<typeof loadSettings>>;
  try {
    const [profile, loadedSettings] = await Promise.all([loadProfile(supabase, userId), loadSettings(admin)]);
    const contact = await loadContact(admin, userId, loadedSettings.creator_id);
    if (!profile) return problem(403, "Complétez d'abord votre profil.");
    settings = loadedSettings;

    // Mode manuel, ou personne non cochée en mode hybride : l'équipe répondra.
    if (!aiMayReply(settings, contact)) {
      const { data, error } = await saveUserMessage();
      if (error) throw new MemoryError(`Message non enregistré : ${error.message}`);
      return NextResponse.json({ messages: [data as Message], offers: [], waiting: true });
    }

    context = await buildReply({ supabase, admin, userId, newMessage: content, now: receivedAt, settings, contact, profile });
    reply = cleanReply(
      await generate({
        system: context.system,
        messages: context.messages,
        temperature: CHAT_TEMPERATURE,
      }),
    );
  } catch (err) {
    console.error("Réponse impossible :", err);
    if (err instanceof LlmError && err.kind === "rate_limited") {
      return problem(429, "Beaucoup de messages en ce moment. Réessayez dans une minute.");
    }
    if (err instanceof MemoryError) return problem(500, err.message);
    return problem(502, "Pas de réponse cette fois-ci. Réessayez dans un instant.");
  }

  // Le message et la réponse ne sont enregistrés qu'une fois la réponse
  // obtenue : en cas d'échec, rien n'est gardé et le texte revient dans la
  // zone de saisie.
  const { text, proposal } = parseProposal(reply);
  const saved: Message[] = [];
  let offers: Offer[] = [];
  try {
    const { data, error } = await saveUserMessage();
    if (error) throw error;
    saved.push(data as Message);
    const result = await saveReply({ admin, userId, text, proposal, sale: context.sale });
    saved.push(...result.messages);
    if (result.offerIds.length) {
      const { data: rows } = await supabase.from("offers").select(OFFER_COLUMNS).in("id", result.offerIds);
      offers = (rows ?? []) as Offer[];
    }
  } catch (err) {
    console.error("Enregistrement impossible :", err);
    return problem(500, "La conversation n'a pas pu être enregistrée. Réessayez dans un instant.");
  }

  after(async () => {
    const now = new Date();
    try {
      await rememberFacts(supabase, userId, context.facts, [...context.messages, { role: "assistant", content: text }], now);
    } catch (err) {
      console.error("Mise à jour de la fiche impossible :", err);
    }
    try {
      await summarizeIfNeeded(supabase, userId, now, settings.context_messages);
    } catch (err) {
      console.error("Résumé impossible :", err);
    }
  });

  return NextResponse.json({ messages: saved, offers });
}
