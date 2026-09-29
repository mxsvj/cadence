"use server";

import { requireAdmin } from "@/lib/admin";
import { parseEuros } from "@/lib/offers";
import { createClient } from "@/lib/supabase/server";

// L'onglet Paramètres : les réglages fins de l'IA et les garde-fous de la
// vente. L'action vérifie d'abord qu'on est administrateur ; la base le
// revérifie (règles de sécurité).

type Result = { ok: true } | { ok: false; error: string };

export type ParametersForm = {
  temperature: number;
  max_tokens: number;
  context_messages: number;
  first_message: string;
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
    if (!between(form.temperature, 0, 2)) return { ok: false, error: "La créativité doit être entre 0 et 2." };
    if (!between(form.max_tokens, 100, 4000)) return { ok: false, error: "La longueur doit être entre 100 et 4 000." };
    if (!between(form.context_messages, 6, 60)) return { ok: false, error: "Entre 6 et 60 messages relus." };
    if (!between(form.sales_min_messages, 0, 1000) || !between(form.sales_gap_messages, 0, 1000)) {
      return { ok: false, error: "Nombres de messages invalides." };
    }
    if (form.first_message.length > 2000) return { ok: false, error: "Premier message trop long (2 000 caractères)." };
    if (form.extra_instructions.length > 5000) return { ok: false, error: "Consignes trop longues (5 000 caractères)." };
    const cap = parseEuros(form.spending_cap || "0");
    if (cap === null) return { ok: false, error: "Plafond illisible : indiquez un montant en euros." };

    const { error } = await supabase
      .from("ai_settings")
      .update({
        temperature: Math.round(form.temperature * 100) / 100,
        max_tokens: Math.round(form.max_tokens),
        context_messages: Math.round(form.context_messages),
        first_message: form.first_message.trim(),
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
