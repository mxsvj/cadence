"use server";

import { requireAdmin } from "@/lib/admin";
import { parseEuros } from "@/lib/offers";
import { sanitizePersona } from "@/lib/persona-profile";
import type { AiMode } from "@/lib/settings";
import { createClient } from "@/lib/supabase/server";

// Les réglages de l'onglet IA. Chaque action vérifie d'abord qu'on est
// administrateur ; la base le revérifie (règles de sécurité).

type Result = { ok: true } | { ok: false; error: string };

export type SettingsForm = {
  mode: AiMode;
  temperature: number;
  max_tokens: number;
  context_messages: number;
  first_message: string;
  extra_instructions: string;
  spending_cap: string; // en euros
  sales_min_messages: number;
  sales_gap_messages: number;
  persona: unknown;
};

async function adminClient() {
  const supabase = await createClient();
  await requireAdmin(supabase);
  return supabase;
}

const between = (n: number, min: number, max: number) => Number.isFinite(n) && n >= min && n <= max;

export async function saveSettings(form: SettingsForm): Promise<Result> {
  try {
    const supabase = await adminClient();
    if (!["auto", "hybride", "manuel"].includes(form.mode)) return { ok: false, error: "Mode inconnu." };
    if (!between(form.temperature, 0, 2)) return { ok: false, error: "La créativité doit être entre 0 et 2." };
    if (!between(form.max_tokens, 100, 4000)) return { ok: false, error: "La longueur doit être entre 100 et 4 000." };
    if (!between(form.context_messages, 6, 60)) return { ok: false, error: "Entre 6 et 60 messages relus." };
    if (!between(form.sales_min_messages, 0, 1000) || !between(form.sales_gap_messages, 0, 1000)) {
      return { ok: false, error: "Nombres de messages invalides." };
    }
    if (form.first_message.length > 2000) return { ok: false, error: "Premier message trop long (2 000 caractères)." };
    if (form.extra_instructions.length > 5000) return { ok: false, error: "Consignes trop longues (5 000 caractères)." };
    const cap = parseEuros(form.spending_cap || "0");
    if (cap === null) return { ok: false, error: "Plafond illisible : indiquez un montant en euros." };
    const { persona, error: personaError } = sanitizePersona(form.persona);
    if (personaError) return { ok: false, error: personaError };

    const { error } = await supabase
      .from("ai_settings")
      .update({
        mode: form.mode,
        temperature: Math.round(form.temperature * 100) / 100,
        max_tokens: Math.round(form.max_tokens),
        context_messages: Math.round(form.context_messages),
        first_message: form.first_message.trim(),
        extra_instructions: form.extra_instructions.trim(),
        spending_cap_cents: cap,
        sales_min_messages: Math.round(form.sales_min_messages),
        sales_gap_messages: Math.round(form.sales_gap_messages),
        persona,
        updated_at: new Date().toISOString(),
      })
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
