import { after, NextResponse, type NextRequest } from "next/server";
import { buildReply, saveReply } from "@/lib/conversation";
import { MAX_MESSAGE_LENGTH } from "@/lib/limits";
import { CHAT_TEMPERATURE, LlmError, generate } from "@/lib/llm";
import { MESSAGE_COLUMNS, MemoryError, memoryDue, rememberFacts, summarizeIfNeeded, type Message } from "@/lib/memory";
import { flushAlerts, raiseUrgency } from "@/lib/notify";
import { OFFER_COLUMNS, parseProposal, type Offer } from "@/lib/offers";
import { cleanReply } from "@/lib/prompts";
import { RateLimiter, chatMessagesPerMinute } from "@/lib/rate-limit";
import { aiMayReply, loadContact, loadCreator, loadProfile, loadSettings } from "@/lib/settings";
import { createAdminClient } from "@/lib/supabase/admin";
import { createClient, currentUserId } from "@/lib/supabase/server";
import { CRISIS_NOTICE, detectUrgency, parseTeamFlag, type UrgencyReason } from "@/lib/urgency";

// Laisse le temps à la mise à jour de la mémoire, qui tourne après la réponse.
export const maxDuration = 60;

const limiter = new RateLimiter(chatMessagesPerMinute(), 60_000);

function problem(status: number, error: string) {
  return NextResponse.json({ error }, { status });
}

/** La créatrice de la conversation, telle que la page l'envoie. */
function creatorParam(value: unknown): number | null {
  const id = Number(value);
  return Number.isSafeInteger(id) && id > 0 ? id : null;
}

// Les nouveaux messages depuis `apres` (réponses de l'équipe, offres) et
// l'état des offres, dans la conversation avec la créatrice `c` : la page
// les redemande régulièrement.
export async function GET(request: NextRequest) {
  const supabase = await createClient();
  const userId = await currentUserId(supabase);
  if (!userId) return problem(401, "Votre session a expiré. Reconnectez-vous.");
  const after = Number(request.nextUrl.searchParams.get("apres") ?? 0) || 0;
  const creatorId = creatorParam(request.nextUrl.searchParams.get("c"));
  if (creatorId === null) return problem(400, "Conversation inconnue.");

  const [messages, offers] = await Promise.all([
    supabase
      .from("messages")
      .select(MESSAGE_COLUMNS)
      .eq("user_id", userId)
      .eq("creator_id", creatorId)
      .gt("id", after)
      .order("id")
      .limit(100),
    supabase.from("offers").select(OFFER_COLUMNS).eq("user_id", userId).eq("creator_id", creatorId).order("id"),
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
  if (!limiter.allow(userId)) return problem(429, "Vous écrivez très vite : attendez quelques secondes avant le prochain message.");

  const body = (await request.json().catch(() => null)) as { content?: unknown; creator?: unknown } | null;
  const content = typeof body?.content === "string" ? body.content.trim() : "";
  const creatorId = creatorParam(body?.creator);
  if (creatorId === null) return problem(400, "Conversation inconnue.");
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
  const origin = new URL(request.url).origin;
  // Demande d'un humain, détresse, âge, paiement : l'équipe est prévenue.
  const urgency = detectUrgency(content);
  const alertTeam = (reason: UrgencyReason, source: "mots" | "ia") =>
    after(async () => {
      if (await raiseUrgency(admin, userId, creatorId, reason, source)) await flushAlerts(admin, origin);
    });
  const saveUserMessage = () =>
    supabase
      .from("messages")
      .insert({ user_id: userId, creator_id: creatorId, role: "user", content, created_at: receivedAt.toISOString() })
      .select(MESSAGE_COLUMNS)
      .single();

  let context: Awaited<ReturnType<typeof buildReply>>;
  let reply: string;
  let settings: Awaited<ReturnType<typeof loadSettings>>;
  try {
    const [profile, loadedSettings, creator, contact] = await Promise.all([
      loadProfile(supabase, userId),
      loadSettings(admin),
      loadCreator(admin, creatorId),
      loadContact(admin, userId, creatorId),
    ]);
    if (!profile) return problem(403, "Complétez d'abord votre profil.");
    // Seulement avec une créatrice en ligne : la base le revérifie en
    // enregistrant le message.
    if (!creator?.active) return problem(410, "Cette créatrice n'est plus disponible. Choisissez-en une autre.");
    settings = loadedSettings;

    // Mode manuel, ou personne non cochée en mode hybride : l'équipe répondra.
    if (!aiMayReply(settings, contact)) {
      const { data, error } = await saveUserMessage();
      if (error) throw new MemoryError(`Message non enregistré : ${error.message}`);
      if (urgency) alertTeam(urgency, "mots");
      // Personne ne répond tout de suite : un message inquiétant reçoit les numéros d'aide sans attendre.
      const notice = urgency === "attention" ? CRISIS_NOTICE : undefined;
      return NextResponse.json({ messages: [data as Message], offers: [], waiting: true, notice });
    }

    context = await buildReply({
      supabase,
      admin,
      userId,
      creator,
      newMessage: content,
      now: receivedAt,
      settings,
      contact,
      profile,
      teamAlerted: urgency !== null,
    });
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
  // [[EQUIPE]] : l'IA juge qu'un humain doit lire la conversation.
  const flag = parseTeamFlag(reply);
  const parsed = parseProposal(flag.text);
  const text = parsed.text;
  // Jamais d'offre dans une réponse qui prévient l'équipe.
  const proposal = urgency || flag.flagged ? null : parsed.proposal;
  const saved: Message[] = [];
  let offers: Offer[] = [];
  try {
    const { data, error } = await saveUserMessage();
    if (error) throw error;
    saved.push(data as Message);
    const result = await saveReply({ admin, userId, creatorId, text, proposal, sale: context.sale });
    saved.push(...result.messages);
    if (result.offerIds.length) {
      const { data: rows } = await supabase.from("offers").select(OFFER_COLUMNS).in("id", result.offerIds);
      offers = (rows ?? []) as Offer[];
    }
  } catch (err) {
    console.error("Enregistrement impossible :", err);
    return problem(500, "La conversation n'a pas pu être enregistrée. Réessayez dans un instant.");
  }

  if (urgency || flag.flagged) alertTeam(urgency ?? "attention", urgency ? "mots" : "ia");

  // La fiche et le résumé : tous les MEMORY_EVERY messages de la personne.
  if (memoryDue(context.sale.userMessages)) {
    after(async () => {
      const now = new Date();
      try {
        await rememberFacts(supabase, userId, creatorId, context.facts, [...context.messages, { role: "assistant", content: text }], now);
      } catch (err) {
        console.error("Mise à jour de la fiche impossible :", err);
      }
      try {
        await summarizeIfNeeded(supabase, userId, creatorId, now, settings.context_messages, context.summary);
      } catch (err) {
        console.error("Résumé impossible :", err);
      }
    });
  }

  return NextResponse.json({ messages: saved, offers });
}
