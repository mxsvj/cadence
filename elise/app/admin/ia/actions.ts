"use server";

import { revalidatePath } from "next/cache";
import { requireAdmin } from "@/lib/admin";
import type { AiMode } from "@/lib/settings";
import { createClient } from "@/lib/supabase/server";

// L'onglet IA : qui répond, et quelles créatrices sont en ligne (les
// personnes choisissent parmi elles). L'action vérifie d'abord qu'on est
// administrateur ; la base le revérifie.

type Result = { ok: true } | { ok: false; error: string };

export type SettingsForm = {
  mode: AiMode;
  /** Les créatrices en ligne : les personnes peuvent les choisir. */
  online: number[];
};

export async function saveSettings(form: SettingsForm): Promise<Result> {
  try {
    const supabase = await createClient();
    await requireAdmin(supabase);
    if (!["auto", "hybride", "manuel"].includes(form.mode)) return { ok: false, error: "Mode inconnu." };
    const online = [...new Set(Array.isArray(form.online) ? form.online : [])].filter((id) => Number.isSafeInteger(id) && id > 0);
    if (!online.length) return { ok: false, error: "Gardez au moins une créatrice en ligne : sinon, personne ne peut parler." };
    const { data: known, error: readError } = await supabase.from("creators").select("id").in("id", online);
    if (readError) throw readError;
    if ((known ?? []).length !== online.length) return { ok: false, error: "Une créatrice n'existe plus. Rechargez la page." };

    const now = new Date().toISOString();
    const [settings, on, off] = await Promise.all([
      supabase.from("ai_settings").update({ mode: form.mode, updated_at: now }).eq("id", 1),
      supabase.from("creators").update({ active: true, updated_at: now }).in("id", online),
      supabase.from("creators").update({ active: false, updated_at: now }).not("id", "in", `(${online.join(",")})`),
    ]);
    for (const r of [settings, on, off]) if (r.error) throw r.error;
    revalidatePath("/admin", "layout");
    return { ok: true };
  } catch (err) {
    console.error("Réglages non enregistrés :", err);
    return { ok: false, error: "Les réglages n'ont pas été enregistrés." };
  }
}
