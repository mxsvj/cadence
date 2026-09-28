import { after, NextResponse } from "next/server";
import { LlmError, generate } from "@/lib/llm";
import { MemoryError, prepareReply, rememberFacts, summarizeIfNeeded, type Message } from "@/lib/memory";
import { MAX_MESSAGE_LENGTH } from "@/lib/limits";
import { cleanReply } from "@/lib/prompts";
import { createClient, currentUserId } from "@/lib/supabase/server";

// Laisse le temps à la mise à jour de la mémoire, qui tourne après la réponse.
export const maxDuration = 60;

function problem(status: number, error: string) {
  return NextResponse.json({ error }, { status });
}

// Reçoit un message, fait répondre Élise, enregistre les deux, puis met la
// mémoire à jour une fois la réponse partie (la personne n'attend pas).
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

  const receivedAt = new Date();
  let reply: string;
  let context: Awaited<ReturnType<typeof prepareReply>>;
  try {
    context = await prepareReply(supabase, userId, content, receivedAt);
    reply = cleanReply(
      await generate({ system: context.system, messages: context.messages, maxTokens: 600, temperature: 0.8 }),
    );
  } catch (err) {
    console.error("Réponse d'Élise impossible :", err);
    if (err instanceof LlmError && err.kind === "rate_limited") {
      return problem(429, "Élise reçoit beaucoup de messages en ce moment. Réessayez dans une minute.");
    }
    if (err instanceof MemoryError) return problem(500, err.message);
    return problem(502, "Élise n'a pas pu répondre cette fois-ci. Réessayez dans un instant.");
  }

  // Les deux messages sont enregistrés ensemble, seulement une fois la
  // réponse obtenue : en cas d'échec, rien n'est gardé et le texte revient
  // dans la zone de saisie.
  const { data, error } = await supabase
    .from("messages")
    .insert([
      { user_id: userId, role: "user", content, created_at: receivedAt.toISOString() },
      { user_id: userId, role: "assistant", content: reply },
    ])
    .select("id, role, content, created_at")
    .order("id", { ascending: true });
  if (error) {
    console.error("Enregistrement impossible :", error);
    return problem(500, "La conversation n'a pas pu être enregistrée. Réessayez dans un instant.");
  }

  after(async () => {
    const now = new Date();
    try {
      await rememberFacts(supabase, userId, context.facts, [...context.messages, { role: "assistant", content: reply }], now);
    } catch (err) {
      console.error("Mise à jour de la fiche impossible :", err);
    }
    try {
      await summarizeIfNeeded(supabase, userId, now);
    } catch (err) {
      console.error("Résumé impossible :", err);
    }
  });

  return NextResponse.json({ messages: data as Message[] });
}
