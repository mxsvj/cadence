import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import type { PersonaProfile } from "./persona-profile";

// Les réglages de l'IA et la fiche contact d'une personne, lus avec le
// client serveur : la personne connectée ne peut pas les lire elle-même.

export type AiMode = "auto" | "hybride" | "manuel";

export type AiSettings = {
  mode: AiMode;
  temperature: number;
  max_tokens: number;
  context_messages: number;
  persona: PersonaProfile;
  first_message: string;
  extra_instructions: string;
  spending_cap_cents: number;
  sales_min_messages: number;
  sales_gap_messages: number;
};

export type Contact = {
  user_id: string;
  ai_enabled: boolean;
  notes: string;
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
  temperature: 0.8,
  max_tokens: 600,
  context_messages: 20,
  persona: {},
  first_message: "",
  extra_instructions: "",
  spending_cap_cents: 10000,
  sales_min_messages: 10,
  sales_gap_messages: 12,
};

export async function loadSettings(admin: SupabaseClient): Promise<AiSettings> {
  const { data, error } = await admin.from("ai_settings").select("*").eq("id", 1).maybeSingle();
  if (error) throw new Error(`Réglages de l'IA illisibles : ${error.message}`);
  if (!data) return DEFAULT_SETTINGS;
  return { ...DEFAULT_SETTINGS, ...data, temperature: Number(data.temperature) } as AiSettings;
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

export async function loadContact(admin: SupabaseClient, userId: string): Promise<Contact> {
  const { data, error } = await admin.from("contacts").select("*").eq("user_id", userId).maybeSingle();
  if (error) throw new Error(`Fiche contact illisible : ${error.message}`);
  return data ? { ...defaultContact(userId), ...data } : defaultContact(userId);
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
