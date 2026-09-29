"use server";

import { redirect } from "next/navigation";
import { eraseEverything } from "@/lib/memory";
import { createClient } from "@/lib/supabase/server";

export async function signOut() {
  const supabase = await createClient();
  await supabase.auth.signOut();
  redirect("/connexion");
}

// « Recevoir des nouvelles » : la personne accepte, ou non, que l'IA lui
// écrive après une absence.
export async function setRelances(ok: boolean): Promise<{ error: string } | void> {
  const supabase = await createClient();
  const { error } = await supabase.rpc("regler_relances", { p_ok: Boolean(ok) });
  if (error) {
    console.error("Réglage des nouvelles impossible :", error);
    return { error: "Le réglage n'a pas été enregistré. Réessayez dans un instant." };
  }
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
