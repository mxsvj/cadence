import "server-only";
import type { SupabaseClient } from "@supabase/supabase-js";
import type { PersonRow } from "./creator-form";

/** Toutes les personnes inscrites, avec ce que la créatrice fait avec chacune. */
export async function loadPeople(supabase: SupabaseClient, creatorId: number | null): Promise<PersonRow[]> {
  const [profiles, rows] = await Promise.all([
    supabase.from("profiles").select("user_id, display_name").order("display_name"),
    creatorId === null
      ? Promise.resolve({ data: [], error: null })
      : supabase.from("creator_contacts").select("user_id, ai_enabled, emojis").eq("creator_id", creatorId),
  ]);
  if (profiles.error) throw new Error(profiles.error.message);
  if (rows.error) throw new Error(rows.error.message);
  const byUser = new Map((rows.data ?? []).map((r) => [r.user_id as string, r]));
  return (profiles.data ?? []).map((p) => ({
    user_id: p.user_id as string,
    name: p.display_name as string,
    ai_enabled: (byUser.get(p.user_id)?.ai_enabled as boolean | undefined) ?? true,
    emojis: (byUser.get(p.user_id)?.emojis as string | undefined) ?? "",
  }));
}
