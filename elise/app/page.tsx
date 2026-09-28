import { redirect } from "next/navigation";
import { connection } from "next/server";
import { adminStatus } from "@/lib/admin";
import { MemoryError, ensureFirstMessage, loadMessages, type Message } from "@/lib/memory";
import { supabaseEnv } from "@/lib/supabase/env";
import { createClient, currentUserId } from "@/lib/supabase/server";
import { Chat } from "./chat";
import { Notice, SetupNotice } from "./notice";

/** Messages affichés à l'ouverture (les plus récents). */
const DISPLAY_MESSAGES = 200;

export default async function Home() {
  await connection(); // toujours calculée à la visite, jamais figée au déploiement
  if (!supabaseEnv()) return <SetupNotice />;
  const supabase = await createClient();
  const userId = await currentUserId(supabase);
  if (!userId) redirect("/connexion");

  let messages: Message[] | null = null;
  let problem = "La base de données ne répond pas.";
  try {
    await ensureFirstMessage(supabase, userId);
    messages = await loadMessages(supabase, userId, DISPLAY_MESSAGES);
  } catch (err) {
    console.error(err);
    if (err instanceof MemoryError) problem = err.message;
  }

  if (!messages) {
    return (
      <Notice title="Élise ne trouve pas ses souvenirs">
        <p>{problem}</p>
        <p className="text-muted">Rechargez la page dans un instant.</p>
      </Notice>
    );
  }
  const isAdmin = (await adminStatus(supabase)) === "admin";
  // La clé change quand tout a été effacé : la conversation repart de zéro.
  return <Chat key={messages[0]?.id ?? "vide"} initialMessages={messages} isAdmin={isAdmin} />;
}
