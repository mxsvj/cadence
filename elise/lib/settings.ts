import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import type { PersonaProfile } from "./persona-profile";

// Les réglages de l'IA et la fiche contact d'une personne, lus avec le
// client serveur : la personne connectée ne peut pas les lire elle-même.

export type AiMode = "auto" | "hybride" | "manuel";

/** Une créatrice : le personnage que l'IA incarne, et son premier message. */
export type Creator = { id: number; persona: PersonaProfile; first_message: string };

export type AiSettings = {
  mode: AiMode;
  context_messages: number;
  extra_instructions: string;
  spending_cap_cents: number;
  sales_min_messages: number;
  sales_gap_messages: number;
  /** La créatrice choisie dans l'onglet IA (null : personnage par défaut). */
  creator_id: number | null;
  creator: Creator | null;
};

export type Contact = {
  user_id: string;
  /** Avec la créatrice active : l'IA peut-elle répondre en mode hybride ? */
  ai_enabled: boolean;
  notes: string;
  /** Avec la créatrice active : les seuls emojis que l'IA utilise. */
  emojis: string;
  city: string;
  timezone: string;
  script_id: number | null;
  spending_cap_cents: number | null;
  last_read_message_id: number;
};

export type Profile = { display_name: string; birthdate: string };

export const DEFAULT_SETTINGS: AiSettings = {
  mode: "auto",
  context_messages: 20,
  extra_instructions: "",
  spending_cap_cents: 10000,
  sales_min_messages: 10,
  sales_gap_messages: 12,
  creator_id: null,
  creator: null,
};

export async function loadCreator(admin: SupabaseClient, id: number): Promise<Creator | null> {
  const { data, error } = await admin.from("creators").select("id, persona, first_message").eq("id", id).maybeSingle();
  if (error) throw new Error(`Créatrice illisible : ${error.message}`);
  return data ? { ...(data as Creator), id: Number(data.id) } : null;
}

export async function loadSettings(admin: SupabaseClient): Promise<AiSettings> {
  const { data, error } = await admin.from("ai_settings").select("*").eq("id", 1).maybeSingle();
  if (error) throw new Error(`Réglages de l'IA illisibles : ${error.message}`);
  if (!data) return DEFAULT_SETTINGS;
  const creatorId = data.creator_id === null || data.creator_id === undefined ? null : Number(data.creator_id);
  return {
    mode: data.mode ?? DEFAULT_SETTINGS.mode,
    context_messages: data.context_messages ?? DEFAULT_SETTINGS.context_messages,
    extra_instructions: data.extra_instructions ?? "",
    spending_cap_cents: data.spending_cap_cents ?? DEFAULT_SETTINGS.spending_cap_cents,
    sales_min_messages: data.sales_min_messages ?? DEFAULT_SETTINGS.sales_min_messages,
    sales_gap_messages: data.sales_gap_messages ?? DEFAULT_SETTINGS.sales_gap_messages,
    creator_id: creatorId,
    creator: creatorId === null ? null : await loadCreator(admin, creatorId),
  };
}

export function defaultContact(userId: string): Contact {
  return {
    user_id: userId,
    ai_enabled: true,
    notes: "",
    emojis: "",
    city: "",
    timezone: "Europe/Paris",
    script_id: null,
    spending_cap_cents: null,
    last_read_message_id: 0,
  };
}

/**
 * La fiche d'une personne : ce que l'équipe sait d'elle (contacts), et ce que
 * la créatrice active fait avec elle (creator_contacts : IA autorisée, emojis).
 */
export async function loadContact(admin: SupabaseClient, userId: string, creatorId: number | null): Promise<Contact> {
  const [contact, withCreator] = await Promise.all([
    admin.from("contacts").select("*").eq("user_id", userId).maybeSingle(),
    creatorId === null
      ? Promise.resolve({ data: null, error: null })
      : admin.from("creator_contacts").select("ai_enabled, emojis").eq("creator_id", creatorId).eq("user_id", userId).maybeSingle(),
  ]);
  if (contact.error) throw new Error(`Fiche contact illisible : ${contact.error.message}`);
  if (withCreator.error) throw new Error(`Réglages de la créatrice illisibles : ${withCreator.error.message}`);
  const own = (withCreator.data ?? {}) as { ai_enabled?: boolean; emojis?: string };
  return {
    ...defaultContact(userId),
    ...(contact.data ?? {}),
    ai_enabled: own.ai_enabled ?? true,
    emojis: own.emojis ?? "",
  };
}

/** L'IA répond-elle à cette personne, dans le mode choisi ? */
export function aiMayReply(settings: AiSettings, contact: Contact): boolean {
  if (settings.mode === "manuel") return false;
  if (settings.mode === "hybride") return contact.ai_enabled;
  return true;
}

export async function loadProfile(supabase: SupabaseClient, userId: string): Promise<Profile | null> {
  const { data, error } = await supabase
    .from("profiles")
    .select("display_name, birthdate")
    .eq("user_id", userId)
    .maybeSingle();
  if (error) throw new Error(`Profil illisible : ${error.message}`);
  return data as Profile | null;
}

export { ageFrom } from "./age";
