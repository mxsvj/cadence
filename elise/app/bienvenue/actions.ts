"use server";

import { redirect } from "next/navigation";
import { checkProfile } from "@/lib/age";
import { createClient } from "@/lib/supabase/server";

export type ProfileState = { error?: string; name?: string; birthdate?: string };

// Enregistre le prénom et la date de naissance ; la base refuse les mineurs.
export async function saveProfile(_previous: ProfileState, formData: FormData): Promise<ProfileState> {
  const name = String(formData.get("nom") ?? "").trim();
  const birthdate = String(formData.get("naissance") ?? "");
  const invalid = checkProfile(name, birthdate);
  if (invalid) return { error: invalid, name, birthdate };

  const supabase = await createClient();
  const { error } = await supabase.rpc("enregistrer_profil", { p_nom: name, p_naissance: birthdate });
  if (error) return { error: error.message || "Le profil n'a pas pu être enregistré.", name, birthdate };
  redirect("/");
}
