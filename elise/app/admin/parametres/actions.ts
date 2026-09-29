"use server";

import { requireAdmin } from "@/lib/admin";
import { parseEuros } from "@/lib/offers";
import { createClient } from "@/lib/supabase/server";

// L'onglet Paramètres : les réglages fins de l'IA (mémoire, consignes) et les
// garde-fous de la vente. L'action vérifie d'abord qu'on est administrateur ; la base le
// revérifie (règles de sécurité).

type Result = { ok: true } | { ok: false; error: string };

export type ParametersForm = {
  context_messages: number;
  extra_instructions: string;
  spending_cap: string; // en euros
  sales_min_messages: number;
  sales_gap_messages: number;
};

const between = (n: number, min: number, max: number) => Number.isFinite(n) && n >= min && n <= max;

export async function saveParameters(form: ParametersForm): Promise<Result> {
  try {
    const supabase = await createClient();
    await requireAdmin(supabase);
    if (!between(form.context_messages, 6, 60)) return { ok: false, error: "Entre 6 et 60 messages relus." };
    if (!between(form.sales_min_messages, 0, 1000) || !between(form.sales_gap_messages, 0, 1000)) {
      return { ok: false, error: "Nombres de messages invalides." };
    }
    if (form.extra_instructions.length > 5000) return { ok: false, error: "Consignes trop longues (5 000 caractères)." };
    const cap = parseEuros(form.spending_cap || "0");
    if (cap === null) return { ok: false, error: "Plafond illisible : indiquez un montant en euros." };

    const { error } = await supabase
      .from("ai_settings")
      .update({
        context_messages: Math.round(form.context_messages),
        extra_instructions: form.extra_instructions.trim(),
        spending_cap_cents: cap,
        sales_min_messages: Math.round(form.sales_min_messages),
        sales_gap_messages: Math.round(form.sales_gap_messages),
        updated_at: new Date().toISOString(),
      })
      .eq("id", 1);
    if (error) throw error;
    return { ok: true };
  } catch (err) {
    console.error("Paramètres non enregistrés :", err);
    return { ok: false, error: "Les paramètres n'ont pas été enregistrés." };
  }
}
