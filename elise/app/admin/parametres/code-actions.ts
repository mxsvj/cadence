"use server";

import { SCHEMA_HINT, requireAdmin, schemaOutdated } from "@/lib/admin";
import { newCode, normalizeCode } from "@/lib/access-code";
import { codeEmail, codeHash } from "@/lib/code-login";
import { createAdminClient } from "@/lib/supabase/admin";
import { createClient, currentUserId } from "@/lib/supabase/server";

// Les codes d'accès des clients, créés par l'équipe. Le code n'est montré
// qu'une fois, à sa création : la base n'en garde qu'une empreinte.

type Result<T = object> = ({ ok: true } & T) | { ok: false; error: string };

async function teamMember(): Promise<string> {
  const supabase = await createClient();
  await requireAdmin(supabase);
  const id = await currentUserId(supabase);
  if (!id) throw new Error("Session expirée.");
  return id;
}

function failure(err: unknown, fallback: string): { ok: false; error: string } {
  console.error(fallback, err);
  if (schemaOutdated(err)) return { ok: false, error: `${fallback.replace(/\.$/, "")} : ${SCHEMA_HINT}` };
  return { ok: false, error: fallback };
}

/** Un nouveau code pour ce compte (le précédent ne marche plus). */
async function storeCode(userId: string, label: string | null, createdBy: string): Promise<string> {
  const admin = createAdminClient();
  const code = newCode();
  const normalized = normalizeCode(code)!;
  const row: Record<string, unknown> = {
    user_id: userId,
    code_hash: codeHash(normalized),
    hint: normalized.slice(-4),
    created_at: new Date().toISOString(),
    created_by: createdBy,
    last_used_at: null,
  };
  if (label !== null) row.label = label;
  const { error } = await admin.from("access_codes").upsert(row, { onConflict: "user_id" });
  if (error) throw error;
  return code;
}

/** Un nouveau client : un compte sans e-mail réel, et son code. */
export async function createClientCode(label: string): Promise<Result<{ code: string; userId: string }>> {
  try {
    const by = await teamMember();
    const name = label.trim().slice(0, 60);
    const admin = createAdminClient();
    const { data, error } = await admin.auth.admin.createUser({
      email: codeEmail(),
      email_confirm: true,
      // Le prénom proposé à la première entrée (la personne peut le changer).
      user_metadata: name ? { display_name: name, via_code: true } : { via_code: true },
    });
    if (error || !data.user) throw error ?? new Error("Compte non créé.");
    try {
      const code = await storeCode(data.user.id, name, by);
      return { ok: true, code, userId: data.user.id };
    } catch (err) {
      // Pas de compte orphelin sans code.
      await admin.auth.admin.deleteUser(data.user.id).catch(() => undefined);
      throw err;
    }
  } catch (err) {
    return failure(err, "Le code n'a pas été créé.");
  }
}

/** Remplacer le code d'un client (code perdu ou partagé par erreur). */
export async function renewClientCode(userId: string): Promise<Result<{ code: string }>> {
  try {
    const by = await teamMember();
    if (!(await hasCode(userId))) return { ok: false, error: "Ce client n'a plus de code : créez-en un nouveau." };
    return { ok: true, code: await storeCode(userId, null, by) };
  } catch (err) {
    return failure(err, "Le nouveau code n'a pas été créé.");
  }
}

/** Un compte de client à code (jamais celui d'un membre de l'équipe). */
async function hasCode(userId: string): Promise<boolean> {
  const { data, error } = await createAdminClient().from("access_codes").select("user_id").eq("user_id", userId).maybeSingle();
  if (error) throw error;
  return data !== null;
}

/**
 * Désactiver le code : on n'entre plus avec, et le compte est bloqué (un
 * téléphone déjà connecté l'est encore au plus une heure, le temps que sa
 * session expire). Les conversations et achats restent dans la base.
 */
export async function removeClientCode(userId: string): Promise<Result> {
  try {
    await teamMember();
    if (!(await hasCode(userId))) return { ok: false, error: "Ce client n'a déjà plus de code." };
    const admin = createAdminClient();
    const { error: banError } = await admin.auth.admin.updateUserById(userId, { ban_duration: "876000h" });
    if (banError) throw banError;
    const { error } = await admin.from("access_codes").delete().eq("user_id", userId);
    if (error) throw error;
    return { ok: true };
  } catch (err) {
    return failure(err, "Le code n'a pas été désactivé.");
  }
}
