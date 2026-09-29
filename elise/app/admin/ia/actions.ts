"use server";

import { requireAdmin } from "@/lib/admin";
import { sanitizePersona } from "@/lib/persona-profile";
import type { AiMode } from "@/lib/settings";
import { createClient } from "@/lib/supabase/server";

// Les réglages de l'onglet IA. Chaque action vérifie d'abord qu'on est
// administrateur ; la base le revérifie (règles de sécurité).

type Result = { ok: true } | { ok: false; error: string };

// Le mode et le personnage. Les réglages fins et les garde-fous de la vente
// s'enregistrent depuis l'onglet Paramètres (app/admin/parametres).
export type SettingsForm = {
  mode: AiMode;
  persona: unknown;
};

async function adminClient() {
  const supabase = await createClient();
  await requireAdmin(supabase);
  return supabase;
}

export async function saveSettings(form: SettingsForm): Promise<Result> {
  try {
    const supabase = await adminClient();
    if (!["auto", "hybride", "manuel"].includes(form.mode)) return { ok: false, error: "Mode inconnu." };
    const { persona, error: personaError } = sanitizePersona(form.persona);
    if (personaError) return { ok: false, error: personaError };

    const { error } = await supabase
      .from("ai_settings")
      .update({ mode: form.mode, persona, updated_at: new Date().toISOString() })
      .eq("id", 1);
    if (error) throw error;
    return { ok: true };
  } catch (err) {
    console.error("Réglages non enregistrés :", err);
    return { ok: false, error: "Les réglages n'ont pas été enregistrés." };
  }
}

/** Mode hybride : cocher ou décocher une personne. */
export async function setAiEnabled(userId: string, enabled: boolean): Promise<Result> {
  try {
    const supabase = await adminClient();
    const { error } = await supabase
      .from("contacts")
      .upsert({ user_id: userId, ai_enabled: enabled, updated_at: new Date().toISOString() }, { onConflict: "user_id" });
    if (error) throw error;
    return { ok: true };
  } catch (err) {
    console.error(err);
    return { ok: false, error: "Le changement n'a pas été enregistré." };
  }
}

/** Les emojis que l'IA utilisera avec une personne. */
export async function saveEmojis(userId: string, emojis: string): Promise<Result> {
  try {
    const supabase = await adminClient();
    const { error } = await supabase
      .from("contacts")
      .upsert({ user_id: userId, emojis: emojis.trim().slice(0, 400), updated_at: new Date().toISOString() }, { onConflict: "user_id" });
    if (error) throw error;
    return { ok: true };
  } catch (err) {
    console.error(err);
    return { ok: false, error: "Les emojis n'ont pas été enregistrés." };
  }
}
