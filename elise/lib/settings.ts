import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import { isEmojiMode, type EmojiMode } from "./emojis";
import type { PersonaProfile } from "./persona-profile";

// Les réglages de l'IA et la fiche contact d'une personne, lus avec le
// client serveur : la personne connectée ne peut pas les lire elle-même.

export type AiMode = "auto" | "hybride" | "manuel";

/** Une créatrice : le personnage que l'IA incarne, son premier message, et si les personnes peuvent la choisir. */
export type Creator = { id: number; persona: PersonaProfile; first_message: string; active: boolean };

export type AiSettings = {
  mode: AiMode;
  context_messages: number;
  extra_instructions: string;
  sales_min_messages: number;
  sales_gap_messages: number;
  /** Pause après un achat, en heures (0 : aucune). */
  sales_pause_hours: number;
  /** Offres payantes proposées par l'IA sur 24 heures, au plus. */
  sales_max_per_day: number;
  /** Prendre des nouvelles après une absence (onglet Paramètres), et au bout de combien d'heures. */
  relance_active: boolean;
  relance_heures: number;
};

export type Contact = {
  user_id: string;
  /** Avec la créatrice de la conversation : l'IA peut-elle répondre en mode hybride ? */
  ai_enabled: boolean;
  /** L'équipe a pris la main dans cette conversation : l'IA se tait, quel que soit le mode. */
  manual: boolean;
  notes: string;
  /** Avec la créatrice de la conversation : emojis au choix de l'IA, seulement ceux de la liste, ou aucun. */
  emoji_mode: EmojiMode;
  emojis: string;
  city: string;
  timezone: string;
  script_id: number | null;
  last_read_message_id: number;
};

/** relances_ok : la personne accepte que l'IA prenne de ses nouvelles (absent avant schema.sql relancé). */
export type Profile = { display_name: string; birthdate: string; relances_ok?: boolean; vu_le?: string | null };

export const DEFAULT_SETTINGS: AiSettings = {
  mode: "auto",
  context_messages: 20,
  extra_instructions: "",
  sales_min_messages: 10,
  sales_gap_messages: 12,
  sales_pause_hours: 24,
  sales_max_per_day: 1,
  relance_active: false,
  relance_heures: 48,
};

export async function loadCreator(admin: SupabaseClient, id: number): Promise<Creator | null> {
  if (!Number.isSafeInteger(id) || id <= 0) return null;
  const { data, error } = await admin.from("creators").select("*").eq("id", id).maybeSingle();
  if (error) throw new Error(`Créatrice illisible : ${error.message}`);
  if (!data) return null;
  return {
    id: Number(data.id),
    persona: (data.persona ?? {}) as PersonaProfile,
    first_message: (data.first_message as string) ?? "",
    active: data.active === true,
  };
}

export async function loadSettings(admin: SupabaseClient): Promise<AiSettings> {
  const { data, error } = await admin.from("ai_settings").select("*").eq("id", 1).maybeSingle();
  if (error) throw new Error(`Réglages de l'IA illisibles : ${error.message}`);
  if (!data) return DEFAULT_SETTINGS;
  return {
    mode: data.mode ?? DEFAULT_SETTINGS.mode,
    context_messages: data.context_messages ?? DEFAULT_SETTINGS.context_messages,
    extra_instructions: data.extra_instructions ?? "",
    sales_min_messages: data.sales_min_messages ?? DEFAULT_SETTINGS.sales_min_messages,
    sales_gap_messages: data.sales_gap_messages ?? DEFAULT_SETTINGS.sales_gap_messages,
    sales_pause_hours: data.sales_pause_hours ?? DEFAULT_SETTINGS.sales_pause_hours,
    sales_max_per_day: data.sales_max_per_day ?? DEFAULT_SETTINGS.sales_max_per_day,
    relance_active: data.relance_active === true,
    relance_heures: data.relance_heures ?? DEFAULT_SETTINGS.relance_heures,
  };
}

export function defaultContact(userId: string): Contact {
  return {
    user_id: userId,
    ai_enabled: true,
    manual: false,
    notes: "",
    emoji_mode: "libre",
    emojis: "",
    city: "",
    timezone: "Europe/Paris",
    script_id: null,
    last_read_message_id: 0,
  };
}

/**
 * La fiche d'une personne : ce que l'équipe sait d'elle (contacts, commun à
 * toutes les créatrices), et ce que la créatrice de la conversation fait avec
 * elle (creator_contacts : IA autorisée, emojis).
 */
export async function loadContact(admin: SupabaseClient, userId: string, creatorId: number): Promise<Contact> {
  const [contact, withCreator] = await Promise.all([
    admin.from("contacts").select("*").eq("user_id", userId).maybeSingle(),
    // « * » : une colonne ajoutée plus tard ne casse pas la conversation tant
    // que schema.sql n'a pas été relancé.
    admin.from("creator_contacts").select("*").eq("creator_id", creatorId).eq("user_id", userId).maybeSingle(),
  ]);
  if (contact.error) throw new Error(`Fiche contact illisible : ${contact.error.message}`);
  if (withCreator.error) throw new Error(`Réglages de la créatrice illisibles : ${withCreator.error.message}`);
  const own = (withCreator.data ?? {}) as { ai_enabled?: boolean; manual?: boolean; emoji_mode?: unknown; emojis?: string };
  const emojis = own.emojis ?? "";
  return {
    ...defaultContact(userId),
    ...(contact.data ?? {}),
    ai_enabled: own.ai_enabled ?? true,
    manual: own.manual === true,
    // Sans le réglage (schema.sql pas encore relancé) : une liste remplie vaut « seulement ceux-là ».
    emoji_mode: isEmojiMode(own.emoji_mode) ? own.emoji_mode : emojis.trim() ? "choisis" : "libre",
    emojis,
  };
}

/** L'IA répond-elle à cette personne, dans le mode choisi ? */
export function aiMayReply(settings: AiSettings, contact: Contact): boolean {
  if (settings.mode === "manuel" || contact.manual) return false;
  if (settings.mode === "hybride") return contact.ai_enabled;
  return true;
}

export async function loadProfile(supabase: SupabaseClient, userId: string): Promise<Profile | null> {
  const { data, error } = await supabase
    .from("profiles")
    .select("*")
    .eq("user_id", userId)
    .maybeSingle();
  if (error) throw new Error(`Profil illisible : ${error.message}`);
  return data as Profile | null;
}

export { ageFrom } from "./age";
