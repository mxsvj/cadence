"use server";

import { redirect } from "next/navigation";
import { eraseEverything } from "@/lib/memory";
import { createClient } from "@/lib/supabase/server";

export async function signOut() {
  const supabase = await createClient();
  await supabase.auth.signOut();
  redirect("/connexion");
}

// « Effacer toutes mes données » : messages, fiche et résumé. Au retour sur
// la page, Élise se présente à nouveau, comme au premier jour.
export async function eraseMyData(): Promise<{ error: string } | void> {
  const supabase = await createClient();
  try {
    await eraseEverything(supabase);
  } catch (err) {
    console.error("Effacement impossible :", err);
    return { error: "L'effacement n'a pas abouti. Réessayez dans un instant." };
  }
  redirect("/");
}
