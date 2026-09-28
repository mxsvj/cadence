import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import { selectNewFacts, parseFactsResponse } from "./facts";
import { generate } from "./llm";
import {
  factsSystemPrompt,
  factsUserPrompt,
  summarySystemPrompt,
  summaryUserPrompt,
  type Turn,
} from "./prompts";

// La mémoire d'Élise, rangée dans trois tables Supabase :
//   messages   → toute la conversation ;
//   user_facts → la fiche (faits courts sur la personne) ;
//   summaries  → le résumé de ce qui est trop ancien pour être relu.
// Les lectures passent par le client de la personne connectée : la base
// (Row Level Security) refuse tout ce qui ne lui appartient pas. Les
// messages de l'IA, eux, sont écrits par le serveur (client admin) : une
// personne ne peut pas écrire au nom de l'IA ni de l'équipe.

/** Messages relus par le modèle à chaque réponse (réglable dans l'onglet IA). */
export const CONTEXT_MESSAGES = 20;
/** Plafond de faits envoyés au modèle (les plus récents). */
const MAX_FACTS_IN_PROMPT = 150;

export type Message = Turn & {
  id: number;
  created_at: string;
  /** Qui a écrit : la personne, l'IA ou l'équipe. */
  author: "user" | "ai" | "team";
  kind: "text" | "offer";
  offer_id: number | null;
};

export const MESSAGE_COLUMNS = "id, role, author, kind, offer_id, content, created_at";

/** Un message tel que le modèle le relit : on lui signale l'équipe et les offres. */
export function toTurn(m: Message): Turn {
  if (m.author === "team") return { role: "assistant", content: `(Message de l'équipe) ${m.content}` };
  if (m.kind === "offer") return { role: "assistant", content: `(Offre de contenu envoyée) ${m.content}` };
  return { role: m.role, content: m.content };
}

export class MemoryError extends Error {
  constructor(message: string, readonly cause?: unknown) {
    super(message);
    this.name = "MemoryError";
  }
}

// Traduit les erreurs de la base en phrases utiles.
function fail(what: string, error: { code?: string; message?: string }): never {
  const missingTable = error.code === "PGRST205" || error.code === "42P01" || error.code === "PGRST202";
  throw new MemoryError(
    missingTable
      ? "La base de données n'est pas prête : le script supabase/schema.sql n'a pas encore été lancé dans Supabase."
      : `${what} : ${error.message ?? "erreur inconnue"}`,
    error,
  );
}

/** Les derniers messages, du plus ancien au plus récent. */
export async function loadMessages(supabase: SupabaseClient, userId: string, limit: number): Promise<Message[]> {
  const { data, error } = await supabase
    .from("messages")
    .select(MESSAGE_COLUMNS)
    .eq("user_id", userId)
    .order("id", { ascending: false })
    .limit(limit);
  if (error) fail("Lecture des messages impossible", error);
  return (data as Message[]).reverse();
}

/** Premier passage (ou tout vient d'être effacé) : l'IA dit bonjour. */
export async function ensureFirstMessage(
  supabase: SupabaseClient,
  admin: SupabaseClient,
  userId: string,
  text: string,
): Promise<void> {
  const { count, error } = await supabase
    .from("messages")
    .select("id", { count: "exact", head: true })
    .eq("user_id", userId);
  if (error) fail("Lecture des messages impossible", error);
  if (count) return;

  const { error: insertError } = await admin
    .from("messages")
    .insert({ user_id: userId, role: "assistant", author: "ai", content: text });
  if (insertError) fail("Impossible d'enregistrer le premier message", insertError);
}

export async function loadFacts(supabase: SupabaseClient, userId: string): Promise<string[]> {
  const { data, error } = await supabase
    .from("user_facts")
    .select("fact")
    .eq("user_id", userId)
    .order("id", { ascending: false })
    .limit(MAX_FACTS_IN_PROMPT);
  if (error) fail("Lecture de la fiche impossible", error);
  return (data as { fact: string }[]).map((r) => r.fact).reverse();
}

type SummaryRow = { summary: string; last_message_id: number };

export async function loadSummary(supabase: SupabaseClient, userId: string): Promise<SummaryRow | null> {
  const { data, error } = await supabase
    .from("summaries")
    .select("summary, last_message_id")
    .eq("user_id", userId)
    .maybeSingle();
  if (error) fail("Lecture du résumé impossible", error);
  return data as SummaryRow | null;
}

/**
 * Après chaque réponse : un second appel au modèle relève les nouveaux faits
 * sur la personne, qu'on range dans la fiche sans doublon.
 */
export async function rememberFacts(
  supabase: SupabaseClient,
  userId: string,
  existing: string[],
  recent: Turn[],
  now: Date,
): Promise<string[]> {
  const raw = await generate({
    system: factsSystemPrompt(now),
    messages: [{ role: "user", content: factsUserPrompt(existing, recent.slice(-6)) }],
    temperature: 0,
    maxTokens: 500,
    json: true,
  });
  const fresh = selectNewFacts(parseFactsResponse(raw), existing);
  const saved: string[] = [];
  for (const fact of fresh) {
    const { error } = await supabase.from("user_facts").insert({ user_id: userId, fact });
    if (!error) saved.push(fact);
    else if (error.code !== "23505") fail("Impossible d'enregistrer un fait", error); // 23505 = déjà connu
  }
  return saved;
}

/**
 * Quand plus de 40 messages ne sont pas encore résumés (deux fois le nombre
 * de messages relus), les plus anciens, tous sauf les 20 derniers, rejoignent
 * le résumé.
 */
export async function summarizeIfNeeded(
  supabase: SupabaseClient,
  userId: string,
  now: Date,
  contextMessages = CONTEXT_MESSAGES,
): Promise<boolean> {
  const previous = await loadSummary(supabase, userId);
  const after = previous?.last_message_id ?? 0;

  const { count, error } = await supabase
    .from("messages")
    .select("id", { count: "exact", head: true })
    .eq("user_id", userId)
    .gt("id", after);
  if (error) fail("Lecture des messages impossible", error);
  if ((count ?? 0) <= contextMessages * 2) return false;

  const { data, error: readError } = await supabase
    .from("messages")
    .select(MESSAGE_COLUMNS)
    .eq("user_id", userId)
    .gt("id", after)
    .order("id", { ascending: true });
  if (readError) fail("Lecture des messages impossible", readError);
  const pending = data as Message[];
  const toSummarize = pending.slice(0, pending.length - contextMessages);
  if (toSummarize.length === 0) return false;

  const summary = await generate({
    system: summarySystemPrompt(now),
    messages: [{ role: "user", content: summaryUserPrompt(previous?.summary ?? null, toSummarize.map(toTurn)) }],
    temperature: 0.2,
    maxTokens: 800,
  });
  const row = {
    summary: summary.trim(),
    last_message_id: toSummarize[toSummarize.length - 1].id,
    updated_at: now.toISOString(),
  };

  // Si deux résumés partent en même temps, seul le premier compte : on ne
  // met à jour que si personne n'est passé entre-temps.
  if (previous) {
    const { error: updateError } = await supabase
      .from("summaries")
      .update(row)
      .eq("user_id", userId)
      .eq("last_message_id", previous.last_message_id);
    if (updateError) fail("Impossible d'enregistrer le résumé", updateError);
  } else {
    const { error: insertError } = await supabase.from("summaries").insert({ user_id: userId, ...row });
    if (insertError && insertError.code !== "23505") fail("Impossible d'enregistrer le résumé", insertError);
  }
  return true;
}

/** Le bouton « Effacer toutes mes données ». */
export async function eraseEverything(supabase: SupabaseClient): Promise<void> {
  const { error } = await supabase.rpc("effacer_mes_donnees");
  if (error) fail("L'effacement a échoué", error);
}
