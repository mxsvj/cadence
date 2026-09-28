"use server";

import { createClient } from "@/lib/supabase/server";

// Les boutons de démonstration du tableau de bord. Chaque fonction SQL
// vérifie d'abord que la personne connectée est administratrice.

type Result = { error?: string };

async function call(fn: string, args?: Record<string, unknown>): Promise<Result> {
  const supabase = await createClient();
  const { error } = await supabase.rpc(fn, args);
  if (error) {
    console.error(`${fn} :`, error);
    return { error: "L'opération n'a pas abouti. Réessayez dans un instant." };
  }
  return {};
}

export async function simulatePurchase(): Promise<Result> {
  return call("admin_simuler_achat");
}

export async function fillDemo(): Promise<Result> {
  return call("admin_remplir_demo", { p_jours: 60 });
}

export async function clearDemo(): Promise<Result> {
  return call("admin_vider_demo");
}
