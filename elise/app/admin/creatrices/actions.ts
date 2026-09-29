"use server";

import { revalidatePath } from "next/cache";
import { SCHEMA_HINT, requireAdmin, schemaOutdated } from "@/lib/admin";
import { cleanEmojis, isEmojiMode, type EmojiMode } from "@/lib/emojis";
import { sanitizePersona } from "@/lib/persona-profile";
import { createClient } from "@/lib/supabase/server";

// L'onglet Créatrices. Chaque action vérifie d'abord qu'on est
// administrateur ; la base le revérifie (règles de sécurité).

type Result<T = object> = ({ ok: true } & T) | { ok: false; error: string };

/** Ce que la créatrice fait avec une personne : lui répondre, et avec quels emojis. */
export type PersonSetting = { user_id: string; ai_enabled: boolean; emoji_mode: EmojiMode; emojis: string };

export type CreatorPayload = {
  id: number | null;
  persona: unknown;
  first_message: string;
  /** Seulement les personnes dont le réglage a changé. */
  people: PersonSetting[];
  /** « Valider » : le prénom devient obligatoire, et la première créatrice validée devient active. */
  validate: boolean;
};

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function failure(err: unknown, what: string): { ok: false; error: string } {
  console.error(`${what} :`, err);
  if (schemaOutdated(err)) return { ok: false, error: `${what} : ${SCHEMA_HINT}` };
  const detail = (err as { message?: unknown } | null)?.message;
  return { ok: false, error: typeof detail === "string" && detail ? `${what} (${detail.replace(/\.$/, "")}).` : `${what}.` };
}

/**
 * Enregistre la créatrice telle qu'elle est : appelée toute seule à chaque
 * changement (la page n'attend pas « Valider »), et par « Valider ». La
 * première fois, la créatrice est créée et son numéro renvoyé.
 */
export async function saveCreator(form: CreatorPayload): Promise<Result<{ id: number }>> {
  try {
    const supabase = await createClient();
    await requireAdmin(supabase);
    const { persona, error: personaError } = sanitizePersona(form.persona);
    if (personaError) return { ok: false, error: personaError };
    if (form.validate && !persona.nom?.trim()) {
      return { ok: false, error: "Ajoutez son prénom (Profil du personnage → Prénom) avant de valider. Le reste est déjà enregistré." };
    }
    const firstMessage = String(form.first_message ?? "");
    if (firstMessage.length > 2000) return { ok: false, error: "Premier message trop long (2 000 caractères)." };
    const people = Array.isArray(form.people) ? form.people : [];
    if (people.length > 5000 || !people.every((p) => UUID.test(p?.user_id))) {
      return { ok: false, error: "La liste des personnes n'est pas valable. Rechargez la page." };
    }

    const now = new Date().toISOString();
    const row = { persona, first_message: firstMessage.trim(), updated_at: now };
    let id = form.id;
    if (id === null) {
      const { data, error } = await supabase.from("creators").insert(row).select("id").single();
      if (error) throw error;
      id = Number(data.id);
    } else {
      const { data, error } = await supabase.from("creators").update(row).eq("id", id).select("id");
      if (error) throw error;
      if (!data?.length) return { ok: false, error: "Cette créatrice n'existe plus (supprimée ?). Revenez à la liste." };
    }

    if (people.length) {
      const { error } = await supabase.from("creator_contacts").upsert(
        people.map((p) => {
          return {
            creator_id: id,
            user_id: p.user_id,
            ai_enabled: Boolean(p.ai_enabled),
            emoji_mode: isEmojiMode(p.emoji_mode) ? p.emoji_mode : "libre",
            emojis: cleanEmojis(p.emojis),
            updated_at: now,
          };
        }),
        { onConflict: "creator_id,user_id" },
      );
      if (error) throw error;
    }

    // Tant qu'aucune créatrice n'est choisie dans l'onglet IA, c'est la
    // première validée.
    if (form.validate) {
      const { error } = await supabase
        .from("ai_settings")
        .update({ creator_id: id, updated_at: now })
        .eq("id", 1)
        .is("creator_id", null);
      if (error) throw error;
    }
    // La liste (et l'onglet IA) à jour, même en revenant avec « retour ».
    revalidatePath("/admin", "layout");
    return { ok: true, id };
  } catch (err) {
    return failure(err, "La créatrice n'a pas été enregistrée");
  }
}

export async function deleteCreator(id: number): Promise<Result> {
  try {
    const supabase = await createClient();
    await requireAdmin(supabase);
    const { error } = await supabase.from("creators").delete().eq("id", id);
    if (error) throw error;
    revalidatePath("/admin", "layout");
    return { ok: true };
  } catch (err) {
    return failure(err, "La créatrice n'a pas été supprimée");
  }
}
