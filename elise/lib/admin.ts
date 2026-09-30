import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import { parisToday, periodRange, type DashboardData, type DashboardFilters } from "./dashboard";

// Accès au tableau de bord. La base vérifie elle-même, dans chaque fonction,
// que la personne connectée est administratrice (table public.admins).

/** Codes d'erreur d'une fonction absente : le script SQL n'a pas été relancé. */
const MISSING = new Set(["PGRST202", "42883"]);

export type AdminStatus = "admin" | "not_admin" | "schema_outdated";

/** Colonne, table ou fonction absente : le script SQL n'a pas été relancé. */
const OUTDATED = new Set([...MISSING, "PGRST204", "PGRST205", "42703", "42P01"]);

export function schemaOutdated(err: unknown): boolean {
  const code = (err as { code?: unknown } | null)?.code;
  return typeof code === "string" && OUTDATED.has(code);
}

export const SCHEMA_HINT = "la base doit être mise à jour : relancez supabase/schema.sql dans Supabase (SQL Editor → Run).";

export async function adminStatus(supabase: SupabaseClient): Promise<AdminStatus> {
  const { data, error } = await supabase.rpc("is_admin");
  if (error) return MISSING.has(error.code) ? "schema_outdated" : "not_admin";
  return data === true ? "admin" : "not_admin";
}

/**
 * Les chiffres pour les filtres choisis. Des dates précises incomplètes
 * retombent sur les 30 derniers jours. Tant que schema.sql n'est pas relancé,
 * l'ancienne fonction répond (sans créatrice ni net), marquée « outdated ».
 */
export async function loadDashboard(
  supabase: SupabaseClient,
  filters: DashboardFilters,
  today: string = parisToday(),
): Promise<DashboardData> {
  const range = periodRange(filters, today) ?? periodRange({ period: "30j" }, today)!;
  const { data, error } = await supabase.rpc("admin_dashboard", {
    p_debut: range.debut,
    p_fin: range.fin,
    p_creator: filters.creator,
    p_net: filters.net,
  });
  if (!error) return data as DashboardData;
  if (!schemaOutdated(error)) throw new Error(`Tableau de bord indisponible : ${error.message}`);

  const days = range.debut === null ? 365 : Math.round((Date.parse(range.fin) - Date.parse(range.debut)) / 86_400_000) + 1;
  const old = await supabase.rpc("admin_dashboard", { p_client: null, p_jours: Math.min(Math.max(days, 1), 365) });
  if (old.error) throw new Error(`Tableau de bord indisponible : ${old.error.message}`);
  return { ...(old.data as DashboardData), outdated: true };
}

/** Pour les routes et actions de l'équipe : refuse net si on n'est pas administrateur. */
export async function requireAdmin(supabase: SupabaseClient): Promise<void> {
  if ((await adminStatus(supabase)) !== "admin") throw new Error("Réservé aux administrateurs.");
}
