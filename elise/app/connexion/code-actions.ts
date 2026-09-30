"use server";

import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { normalizeCode } from "@/lib/access-code";
import { checkProfile } from "@/lib/age";
import { codeAttempts, codeEmail, sameCode } from "@/lib/code-login";
import { createAdminClient } from "@/lib/supabase/admin";
import { createClient } from "@/lib/supabase/server";

export type CodeState = { error?: string; code?: string; name?: string; birthdate?: string };

// Entrer avec le code unique, son prénom et sa date de naissance : un compte
// de test est créé pour cette personne, puis sa session s'ouvre par un lien
// de connexion à usage unique, jamais envoyé (comme le lien de l'équipe).
export async function enterWithCode(_previous: CodeState, formData: FormData): Promise<CodeState> {
  const typed = String(formData.get("code") ?? "").trim();
  const name = String(formData.get("nom") ?? "").trim();
  const birthdate = String(formData.get("naissance") ?? "");
  const keep = { code: typed, name, birthdate };

  const code = normalizeCode(typed);
  if (!code) return { ...keep, error: "Le code fait 8 lettres et chiffres, par exemple ABCD-EFGH." };
  const invalid = checkProfile(name, birthdate);
  if (invalid) return { ...keep, error: invalid };

  const h = await headers();
  const ip = h.get("x-forwarded-for")?.split(",")[0]?.trim() || h.get("x-real-ip") || "inconnue";
  if (!codeAttempts.allow(ip)) return { ...keep, error: "Trop d'essais. Attendez quelques minutes avant de réessayer." };

  try {
    const admin = createAdminClient();
    const { data: current, error } = await admin.from("entry_code").select("code").eq("id", 1).maybeSingle();
    if (error) throw error;
    if (!sameCode(normalizeCode(current?.code), code)) {
      return { ...keep, error: "Ce n'est pas le bon code. Vérifiez-le auprès de la personne qui vous l'a donné." };
    }

    const { data: created, error: createError } = await admin.auth.admin.createUser({
      email: codeEmail(),
      email_confirm: true,
      user_metadata: { display_name: name, via_code: true },
    });
    if (createError || !created.user?.email) throw createError ?? new Error("Compte non créé.");
    const { data: link, error: linkError } = await admin.auth.admin.generateLink({ type: "magiclink", email: created.user.email });
    if (linkError) throw linkError;
    const supabase = await createClient();
    const { error: verifyError } = await supabase.auth.verifyOtp({ type: "magiclink", token_hash: link.properties.hashed_token });
    if (verifyError) throw verifyError;
    // Déjà connecté avec la nouvelle session : le prénom et l'âge (la base refuse les mineurs).
    const { error: profileError } = await supabase.rpc("enregistrer_profil", { p_nom: name, p_naissance: birthdate });
    if (profileError) console.error("Profil non enregistré à l'entrée (la page Bienvenue le redemandera) :", profileError);
  } catch (err) {
    console.error("Entrée par code impossible :", err);
    return { ...keep, error: "L'entrée n'a pas marché. Réessayez dans un instant." };
  }
  redirect("/");
}
