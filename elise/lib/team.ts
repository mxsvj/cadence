import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import { MESSAGE_COLUMNS, type Message } from "./memory";
import type { Script, Step } from "./offers";
import { displayName } from "./persona-profile";
import { loadContact, loadSettings, type AiMode, type Contact } from "./settings";

// Ce que voit l'équipe dans l'onglet « Messages ». Tout est lu avec la
// session de l'administrateur : la base (RLS et fonctions admin_*) vérifie
// elle-même qu'il en est bien un.

export type InboxItem = {
  user_id: string;
  email: string;
  nom: string;
  dernier: { id: number; auteur: "user" | "ai" | "team"; type: "text" | "offer"; texte: string; date: string };
  non_lus: number;
  ia_autorisee: boolean;
  depense_cents: number;
};

export type Person = {
  user_id: string;
  email: string;
  nom: string;
  age: number | null;
  inscrit_le: string;
  depense_cents: number;
  depense_mois_cents: number;
  plafond_cents: number | null;
  script_id: number | null;
  prochaine_etape: Step | null;
};

export type TeamOffer = {
  id: number;
  step_id: number | null;
  content_type: Step["content_type"];
  photo_count: number;
  video_count: number;
  price_cents: number;
  personalized: boolean;
  status: "proposee" | "achetee" | "offerte" | "retiree";
  proposed_by: "ai" | "team";
  bids_refused: number;
  last_bid_cents: number | null;
  last_bid_status: "acceptee" | "refusee" | null;
  created_at: string;
  purchased_at: string | null;
};

export type Thread = {
  person: Person;
  contact: Contact;
  /** La créatrice active (son IA autorisée et ses emojis sont dans la fiche), ou null. */
  creatorName: string | null;
  messages: Message[];
  offers: TeamOffer[];
  steps: Record<number, Pick<Step, "id" | "title" | "content_type">>;
  scripts: Script[];
  facts: string[];
};

function check<T>(r: { data: T | null; error: { message: string } | null }, what: string): T {
  if (r.error) throw new Error(`${what} : ${r.error.message}`);
  return r.data as T;
}

export async function loadInbox(supabase: SupabaseClient): Promise<{ mode: AiMode; conversations: InboxItem[] }> {
  const [list, settings] = await Promise.all([
    supabase.rpc("admin_boite"),
    supabase.from("ai_settings").select("mode").eq("id", 1).maybeSingle(),
  ]);
  return {
    conversations: check(list, "Conversations illisibles") as InboxItem[],
    mode: ((check(settings, "Réglages illisibles") as { mode: AiMode } | null)?.mode ?? "auto") as AiMode,
  };
}

export async function loadThread(supabase: SupabaseClient, userId: string): Promise<Thread | null> {
  const [person, settings, messages, offers, scripts, facts] = await Promise.all([
    supabase.rpc("admin_personne", { p_user: userId }),
    loadSettings(supabase),
    supabase.from("messages").select(MESSAGE_COLUMNS).eq("user_id", userId).order("id", { ascending: false }).limit(300),
    supabase.from("offers").select("*").eq("user_id", userId).order("id"),
    // « * » : creator_id n'existe qu'une fois schema.sql relancé.
    supabase.from("scripts").select("*").order("position").order("id"),
    supabase.from("user_facts").select("fact").eq("user_id", userId).order("id"),
  ]);
  const p = check(person, "Personne introuvable") as Person | null;
  if (!p) return null;
  // La fiche, avec ce que la créatrice active fait avec cette personne.
  const contact = await loadContact(supabase, userId, settings.creator_id);

  const offerRows = check(offers, "Offres illisibles") as TeamOffer[];
  const stepIds = [...new Set(offerRows.map((o) => o.step_id).filter((id): id is number => id !== null))];
  const steps: Thread["steps"] = {};
  if (stepIds.length) {
    const rows = check(
      await supabase.from("script_steps").select("id, title, content_type").in("id", stepIds),
      "Étapes illisibles",
    ) as Thread["steps"][number][];
    for (const s of rows) steps[s.id] = s;
  }

  return {
    person: p,
    contact,
    creatorName: settings.creator ? displayName(settings.creator.persona) : null,
    messages: (check(messages, "Messages illisibles") as Message[]).reverse(),
    offers: offerRows,
    steps,
    scripts: usableScripts(check(scripts, "Scripts illisibles") as Script[], settings.creator_id, contact.script_id),
    facts: (check(facts, "Fiche illisible") as { fact: string }[]).map((f) => f.fact),
  };
}

/**
 * Les scripts qu'on peut choisir dans la fiche : ceux de la créatrice active
 * et ceux qui servent à toutes. Celui déjà choisi reste visible, signalé,
 * s'il est à une autre créatrice (l'IA ne s'en sert pas).
 */
export function usableScripts(scripts: Script[], activeCreator: number | null, chosen: number | null): Script[] {
  return scripts.flatMap((s) => {
    const owner = s.creator_id == null ? null : Number(s.creator_id);
    if (owner === null || owner === activeCreator) return [{ ...s, creator_id: owner }];
    if (s.id === chosen) return [{ ...s, creator_id: owner, name: `${s.name} (autre créatrice : pas utilisé)` }];
    return [];
  });
}

/** Les fuseaux horaires que connaît le navigateur ou le serveur. */
export function timeZones(): string[] {
  try {
    return Intl.supportedValuesOf("timeZone");
  } catch {
    return ["Europe/Paris"];
  }
}
