import { redirect } from "next/navigation";
import { connection } from "next/server";
import { adminStatus } from "@/lib/admin";
import { firstMessageFor } from "@/lib/conversation";
import { MemoryError, ensureFirstMessage, loadMessages, type Message } from "@/lib/memory";
import { OFFER_COLUMNS, type Offer } from "@/lib/offers";
import { displayName } from "@/lib/persona-profile";
import { loadProfile, loadSettings } from "@/lib/settings";
import { createAdminClient } from "@/lib/supabase/admin";
import { createClient, currentUserId } from "@/lib/supabase/server";
import { Chat } from "./chat";
import { Notice, SetupNotice, missingSettings } from "./notice";

/** Messages affichés à l'ouverture (les plus récents). */
const DISPLAY_MESSAGES = 200;

type Loaded = { messages: Message[]; offers: Offer[]; name: string } | { problem: string } | "profil";

export default async function Home() {
  await connection(); // toujours calculée à la visite, jamais figée au déploiement
  if (missingSettings().length) return <SetupNotice />;
  const supabase = await createClient();
  const userId = await currentUserId(supabase);
  if (!userId) redirect("/connexion");

  let loaded: Loaded;
  try {
    const admin = createAdminClient();
    const [profile, settings] = await Promise.all([loadProfile(supabase, userId), loadSettings(admin)]);
    if (!profile) {
      loaded = "profil";
    } else {
      await ensureFirstMessage(supabase, admin, userId, firstMessageFor(settings));
      const [messages, offers] = await Promise.all([
        loadMessages(supabase, userId, DISPLAY_MESSAGES),
        supabase.from("offers").select(OFFER_COLUMNS).eq("user_id", userId).order("id"),
      ]);
      loaded = { messages, offers: (offers.data ?? []) as Offer[], name: displayName(settings.persona) };
    }
  } catch (err) {
    console.error(err);
    loaded = {
      problem:
        err instanceof MemoryError
          ? err.message
          : "La base de données ne répond pas, ou le script supabase/schema.sql doit être relancé.",
    };
  }

  // Âge et prénom d'abord : Élise est réservée aux personnes majeures.
  if (loaded === "profil") redirect("/bienvenue");
  if ("problem" in loaded) {
    return (
      <Notice title="Élise ne trouve pas ses souvenirs">
        <p>{loaded.problem}</p>
        <p className="text-muted">Rechargez la page dans un instant.</p>
      </Notice>
    );
  }

  const isAdmin = (await adminStatus(supabase)) === "admin";
  // La clé change quand tout a été effacé : la conversation repart de zéro.
  return (
    <Chat
      key={loaded.messages[0]?.id ?? "vide"}
      initialMessages={loaded.messages}
      initialOffers={loaded.offers}
      name={loaded.name}
      isAdmin={isAdmin}
    />
  );
}
