"use server";

import { SCHEMA_HINT, schemaOutdated } from "@/lib/admin";
import { newCode } from "@/lib/access-code";
import { createClient } from "@/lib/supabase/server";

export type EntryCode = { code: string; change_le: string };

/** Un nouveau code d'entrée : l'ancien ne marche plus, les personnes déjà entrées le restent. */
export async function changeEntryCode(): Promise<({ ok: true } & EntryCode) | { ok: false; error: string }> {
  const supabase = await createClient();
  // La base vérifie elle-même que la personne connectée est de l'équipe.
  const { data, error } = await supabase.rpc("admin_changer_code_entree", { p_code: newCode() });
  if (error) {
    console.error("Code d'entrée non changé :", error);
    return { ok: false, error: schemaOutdated(error) ? `Le code n'a pas changé : ${SCHEMA_HINT}` : "Le code n'a pas changé." };
  }
  return { ok: true, ...(data as EntryCode) };
}
