import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import type { DashboardData } from "./dashboard";
import { PERIODS } from "./dashboard";

// Accès au tableau de bord. La base vérifie elle-même, dans chaque fonction,
// que la personne connectée est administratrice (table public.admins).

/** Codes d'erreur d'une fonction absente : le script SQL n'a pas été relancé. */
const MISSING = new Set(["PGRST202", "42883"]);

export type AdminStatus = "admin" | "not_admin" | "schema_outdated";

export async function adminStatus(supabase: SupabaseClient): Promise<AdminStatus> {
  const { data, error } = await supabase.rpc("is_admin");
  if (error) return MISSING.has(error.code) ? "schema_outdated" : "not_admin";
  return data === true ? "admin" : "not_admin";
}

export function parsePeriod(value: string | null | undefined): number {
  const days = Number(value);
  return (PERIODS as readonly number[]).includes(days) ? days : 30;
}

export async function loadDashboard(
  supabase: SupabaseClient,
  client: string | null,
  days: number,
): Promise<DashboardData> {
  const { data, error } = await supabase.rpc("admin_dashboard", { p_client: client, p_jours: days });
  if (error) throw new Error(`Tableau de bord indisponible : ${error.message}`);
  return data as DashboardData;
}

/** Pour les routes et actions de l'équipe : refuse net si on n'est pas administrateur. */
export async function requireAdmin(supabase: SupabaseClient): Promise<void> {
  if ((await adminStatus(supabase)) !== "admin") throw new Error("Réservé aux administrateurs.");
}
