"use server";

import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { formatCode, normalizeCode } from "@/lib/access-code";
import { codeAttempts, codeHash } from "@/lib/code-login";
import { createAdminClient } from "@/lib/supabase/admin";
import { createClient } from "@/lib/supabase/server";

export type CodeState = { error?: string; code?: string };

// Entrer avec son code d'accès, sans e-mail ni mot de passe : on retrouve le
// compte du code, puis on ouvre sa session par un lien de connexion à usage
// unique, jamais envoyé (comme le lien de l'équipe).
export async function enterWithCode(_previous: CodeState, formData: FormData): Promise<CodeState> {
  const typed = String(formData.get("code") ?? "").trim();
  const code = normalizeCode(typed);
  if (!code) return { error: "Le code fait 8 lettres et chiffres, par exemple ABCD-EFGH.", code: typed };

  const h = await headers();
  const ip = h.get("x-forwarded-for")?.split(",")[0]?.trim() || h.get("x-real-ip") || "inconnue";
  if (!codeAttempts.allow(ip)) return { error: "Trop d'essais. Attendez quelques minutes avant de réessayer.", code: typed };

  try {
    const admin = createAdminClient();
    const { data: row, error } = await admin.from("access_codes").select("user_id").eq("code_hash", codeHash(code)).maybeSingle();
    if (error) throw error;
    if (!row) return { error: "Ce code n'existe pas. Vérifiez-le, ou demandez un nouveau code.", code: formatCode(code) };

    const { data: found, error: userError } = await admin.auth.admin.getUserById(row.user_id);
    const email = found.user?.email;
    if (userError || !email) throw userError ?? new Error("Compte du code sans adresse.");
    const { data: link, error: linkError } = await admin.auth.admin.generateLink({ type: "magiclink", email });
    if (linkError) throw linkError;
    const supabase = await createClient();
    const { error: verifyError } = await supabase.auth.verifyOtp({ type: "magiclink", token_hash: link.properties.hashed_token });
    if (verifyError) throw verifyError;
    await admin.from("access_codes").update({ last_used_at: new Date().toISOString() }).eq("user_id", row.user_id);
  } catch (err) {
    console.error("Entrée par code impossible :", err);
    return { error: "L'entrée n'a pas marché. Réessayez dans un instant.", code: formatCode(code) };
  }
  // Première fois : prénom et date de naissance (18 ans minimum), puis la conversation.
  redirect("/");
}
