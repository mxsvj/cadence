"use server";

import { requireAdmin } from "@/lib/admin";
import type { AiMode } from "@/lib/settings";
import { createClient } from "@/lib/supabase/server";

// L'onglet IA : qui répond, et quelle créatrice l'IA incarne. L'action
// vérifie d'abord qu'on est administrateur ; la base le revérifie.

type Result = { ok: true } | { ok: false; error: string };

export type SettingsForm = {
  mode: AiMode;
  /** La créatrice que l'IA incarne ; null : le personnage par défaut. */
  creator_id: number | null;
};

export async function saveSettings(form: SettingsForm): Promise<Result> {
  try {
    const supabase = await createClient();
    await requireAdmin(supabase);
    if (!["auto", "hybride", "manuel"].includes(form.mode)) return { ok: false, error: "Mode inconnu." };
    if (form.creator_id !== null) {
      const { data } = await supabase.from("creators").select("id").eq("id", form.creator_id).maybeSingle();
      if (!data) return { ok: false, error: "Cette créatrice n'existe plus. Rechargez la page." };
    }
    const { error } = await supabase
      .from("ai_settings")
      .update({ mode: form.mode, creator_id: form.creator_id, updated_at: new Date().toISOString() })
      .eq("id", 1);
    if (error) throw error;
    return { ok: true };
  } catch (err) {
    console.error("Réglages non enregistrés :", err);
    return { ok: false, error: "Les réglages n'ont pas été enregistrés." };
  }
}
