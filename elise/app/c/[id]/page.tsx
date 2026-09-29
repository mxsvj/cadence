import { redirect } from "next/navigation";
import { connection } from "next/server";
import { Chat } from "@/app/chat";
import { Notice, SetupNotice, missingSettings } from "@/app/notice";
import { adminStatus } from "@/lib/admin";
import { firstMessageFor } from "@/lib/conversation";
import { MemoryError, ensureFirstMessage, loadMessages, type Message } from "@/lib/memory";
import { OFFER_COLUMNS, type Offer } from "@/lib/offers";
import { displayName } from "@/lib/persona-profile";
import { loadCreator, loadProfile, loadSettings } from "@/lib/settings";
import { createAdminClient } from "@/lib/supabase/admin";
import { createClient, currentUserId } from "@/lib/supabase/server";

/** Messages affichés à l'ouverture (les plus récents). */
const DISPLAY_MESSAGES = 200;

type Loaded =
  | { messages: Message[]; offers: Offer[]; name: string; relances: { ok: boolean } | null; others: boolean }
  | { problem: string }
  | "profil"
  | "indisponible";

// La conversation avec une créatrice. Elle ne voit que ce qui s'est dit
// avec elle : ses messages, sa mémoire, ses offres.
export default async function ConversationPage({ params }: PageProps<"/c/[id]">) {
  await connection();
  if (missingSettings().length) return <SetupNotice />;
  const supabase = await createClient();
  const userId = await currentUserId(supabase);
  if (!userId) redirect("/connexion");
  const creatorId = Number((await params).id);
  if (!Number.isSafeInteger(creatorId) || creatorId <= 0) redirect("/");
  const isAdmin = (await adminStatus(supabase)) === "admin";

  let loaded: Loaded;
  try {
    const admin = createAdminClient();
    const [profile, settings, creator, online] = await Promise.all([
      loadProfile(supabase, userId),
      loadSettings(admin),
      loadCreator(admin, creatorId),
      supabase.rpc("creatrices_disponibles"),
    ]);
    if (!profile) {
      loaded = "profil";
    } else if (!creator?.active) {
      loaded = "indisponible";
    } else {
      await ensureFirstMessage(supabase, admin, userId, creator.id, firstMessageFor(creator));
      const [messages, offers] = await Promise.all([
        loadMessages(supabase, userId, creator.id, DISPLAY_MESSAGES),
        supabase.from("offers").select(OFFER_COLUMNS).eq("user_id", userId).eq("creator_id", creator.id).order("id"),
        // La visite compte comme un retour, même sans écrire (prendre des
        // nouvelles). Sans importance si la base n'est pas encore à jour.
        isAdmin ? null : supabase.rpc("marquer_visite"),
      ]);
      loaded = {
        messages,
        offers: (offers.data ?? []) as Offer[],
        name: displayName(creator.persona),
        relances: settings.relance_active ? { ok: profile.relances_ok !== false } : null,
        others: ((online.data ?? []) as unknown[]).length > 1,
      };
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

  // Âge et prénom d'abord : le site est réservé aux personnes majeures.
  if (loaded === "profil") redirect("/bienvenue");
  // Plus en ligne : retour au choix des créatrices.
  if (loaded === "indisponible") redirect("/");
  if ("problem" in loaded) {
    return (
      <Notice title="La conversation n'a pas pu s'ouvrir">
        <p>{loaded.problem}</p>
        <p className="text-muted">Rechargez la page dans un instant.</p>
      </Notice>
    );
  }

  // La clé change quand tout a été effacé : la conversation repart de zéro.
  return (
    <Chat
      key={`${creatorId}-${loaded.messages[0]?.id ?? "vide"}`}
      creatorId={creatorId}
      initialMessages={loaded.messages}
      initialOffers={loaded.offers}
      name={loaded.name}
      isAdmin={isAdmin}
      relances={loaded.relances}
      others={loaded.others}
    />
  );
}
