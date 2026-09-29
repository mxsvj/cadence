"use server";

import { SCHEMA_HINT, requireAdmin, schemaOutdated } from "@/lib/admin";
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
  /** Pause après un achat et offres payantes par jour : envoyés seulement s'ils ont changé. */
  guards?: { pause_hours: number; max_per_day: number };
  /** Prendre des nouvelles : envoyé seulement si le réglage a changé. */
  relance?: { active: boolean; hours: number };
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
    if (form.relance && !between(form.relance.hours, 24, 336)) return { ok: false, error: "Délai d'absence : entre 24 heures et 2 semaines." };
    if (form.guards && !between(form.guards.pause_hours, 0, 720)) return { ok: false, error: "Pause après un achat : entre 0 et 720 heures." };
    if (form.guards && !between(form.guards.max_per_day, 1, 20)) return { ok: false, error: "Offres payantes par jour : entre 1 et 20." };

    const { error } = await supabase
      .from("ai_settings")
      .update({
        context_messages: Math.round(form.context_messages),
        extra_instructions: form.extra_instructions.trim(),
        spending_cap_cents: cap,
        sales_min_messages: Math.round(form.sales_min_messages),
        sales_gap_messages: Math.round(form.sales_gap_messages),
        ...(form.relance ? { relance_active: Boolean(form.relance.active), relance_heures: Math.round(form.relance.hours) } : {}),
        ...(form.guards
          ? { sales_pause_hours: Math.round(form.guards.pause_hours), sales_max_per_day: Math.round(form.guards.max_per_day) }
          : {}),
        updated_at: new Date().toISOString(),
      })
      .eq("id", 1);
    if (error) throw error;
    return { ok: true };
  } catch (err) {
    console.error("Paramètres non enregistrés :", err);
    if (schemaOutdated(err)) return { ok: false, error: `Les paramètres n'ont pas été enregistrés : ${SCHEMA_HINT}` };
    return { ok: false, error: "Les paramètres n'ont pas été enregistrés." };
  }
}
