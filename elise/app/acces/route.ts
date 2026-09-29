import { NextResponse, type NextRequest } from "next/server";
import { createAdminClient } from "@/lib/supabase/admin";
import { createClient } from "@/lib/supabase/server";
import { accessKey, sameKey } from "@/lib/team-access";

// Le lien secret de l'équipe : /acces?cle=… ouvre la session du compte
// administrateur, puis le tableau de bord. Sans e-mail ni mot de passe.
export async function GET(request: NextRequest) {
  const url = request.nextUrl;
  // Une page qui dit pourquoi, visible même par qui est déjà connecté.
  const refuse = (raison: string) => NextResponse.redirect(new URL(`/acces/refus?raison=${raison}`, url));

  const expected = accessKey();
  if (!expected) {
    console.warn("Lien de l'équipe refusé : ADMIN_ACCESS_KEY manque ou fait moins de 24 caractères.");
    return refuse("absente");
  }
  if (!sameKey(url.searchParams.get("cle") ?? "", expected)) return refuse("cle");

  try {
    const admin = createAdminClient();
    // Le compte administrateur (supabase/admin.sql) : c'est lui qui ouvre la session.
    const { data: rows, error } = await admin.from("admins").select("user_id").order("user_id").limit(1);
    if (error) throw error;
    if (!rows?.length) return refuse("equipe");

    const { data: found, error: userError } = await admin.auth.admin.getUserById(rows[0].user_id);
    const email = found.user?.email;
    if (userError || !email) throw userError ?? new Error("Compte administrateur sans adresse e-mail.");

    // Un lien de connexion à usage unique, jamais envoyé : on l'utilise aussitôt.
    const { data: link, error: linkError } = await admin.auth.admin.generateLink({ type: "magiclink", email });
    if (linkError) throw linkError;
    const supabase = await createClient();
    const { error: verifyError } = await supabase.auth.verifyOtp({
      type: "magiclink",
      token_hash: link.properties.hashed_token,
    });
    if (verifyError) throw verifyError;
  } catch (err) {
    console.error("Lien de l'équipe : la session n'a pas pu s'ouvrir.", err);
    return refuse("panne");
  }
  // Adresse propre : la clé ne reste pas affichée dans la barre d'adresse.
  return NextResponse.redirect(new URL("/admin", url));
}
