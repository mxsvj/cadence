"use server";

import { requireAdmin } from "@/lib/admin";
import { sanitizePersona } from "@/lib/persona-profile";
import { createClient } from "@/lib/supabase/server";

// L'onglet Créatrices. Chaque action vérifie d'abord qu'on est
// administrateur ; la base le revérifie (règles de sécurité).

type Result<T = object> = ({ ok: true } & T) | { ok: false; error: string };

export type CreatorPayload = {
  id: number | null;
  persona: unknown;
  first_message: string;
  /** Ce que la créatrice fait avec chaque personne. */
  people: { user_id: string; ai_enabled: boolean; emojis: string }[];
};

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/**
 * « Valider » : enregistre la créatrice, son premier message et ses réglages
 * avec chaque personne. La première créatrice devient celle que l'IA incarne.
 */
export async function saveCreator(form: CreatorPayload): Promise<Result<{ id: number }>> {
  try {
    const supabase = await createClient();
    await requireAdmin(supabase);
    const { persona, error: personaError } = sanitizePersona(form.persona);
    if (personaError) return { ok: false, error: personaError };
    if (!persona.nom?.trim()) return { ok: false, error: "Donnez un nom à la créatrice (Profil du personnage → Nom)." };
    if (form.first_message.length > 2000) return { ok: false, error: "Premier message trop long (2 000 caractères)." };
    const people = Array.isArray(form.people) ? form.people : [];
    if (people.length > 5000 || !people.every((p) => UUID.test(p.user_id))) {
      return { ok: false, error: "La liste des personnes n'est pas valable. Rechargez la page." };
    }

    const now = new Date().toISOString();
    const row = { persona, first_message: form.first_message.trim(), updated_at: now };
    let id = form.id;
    if (id === null) {
      const { data, error } = await supabase.from("creators").insert(row).select("id").single();
      if (error) throw error;
      id = Number(data.id);
    } else {
      const { error } = await supabase.from("creators").update(row).eq("id", id);
      if (error) throw error;
    }

    if (people.length) {
      const { error } = await supabase.from("creator_contacts").upsert(
        people.map((p) => ({
          creator_id: id,
          user_id: p.user_id,
          ai_enabled: Boolean(p.ai_enabled),
          emojis: String(p.emojis ?? "").trim().slice(0, 400),
          updated_at: now,
        })),
        { onConflict: "creator_id,user_id" },
      );
      if (error) throw error;
    }

    // Tant qu'aucune créatrice n'est choisie dans l'onglet IA, c'est celle-ci.
    const { error: activeError } = await supabase
      .from("ai_settings")
      .update({ creator_id: id, updated_at: now })
      .eq("id", 1)
      .is("creator_id", null);
    if (activeError) throw activeError;
    return { ok: true, id };
  } catch (err) {
    console.error("Créatrice non enregistrée :", err);
    return { ok: false, error: "La créatrice n'a pas été enregistrée." };
  }
}

export async function deleteCreator(id: number): Promise<Result> {
  try {
    const supabase = await createClient();
    await requireAdmin(supabase);
    const { error } = await supabase.from("creators").delete().eq("id", id);
    if (error) throw error;
    return { ok: true };
  } catch (err) {
    console.error("Créatrice non supprimée :", err);
    return { ok: false, error: "La créatrice n'a pas été supprimée." };
  }
}
