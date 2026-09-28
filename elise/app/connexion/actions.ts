"use server";

import type { AuthError } from "@supabase/supabase-js";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";

export type AuthState = { error?: string; info?: string; email?: string };

// Connexion ou inscription par e-mail et mot de passe (Supabase Auth).
export async function authenticate(_previous: AuthState, formData: FormData): Promise<AuthState> {
  const mode = formData.get("mode") === "inscription" ? "inscription" : "connexion";
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");
  if (!email || !password) return { error: "Indiquez votre adresse e-mail et un mot de passe.", email };

  const supabase = await createClient();

  if (mode === "connexion") {
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) return { error: explain(error), email };
    redirect("/");
  }

  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: { emailRedirectTo: `${await siteOrigin()}/auth/callback` },
  });
  if (error) return { error: explain(error), email };
  // Confirmation par e-mail désactivée dans Supabase : on est déjà connecté.
  if (data.session) redirect("/");
  // Adresse déjà inscrite : Supabase ne le dit pas franchement, par prudence.
  if (data.user && data.user.identities?.length === 0) {
    return { error: "Un compte existe déjà avec cette adresse. Connectez-vous plutôt.", email };
  }
  return {
    info: "Presque fini : ouvrez l'e-mail que nous venons de vous envoyer et cliquez sur le lien. Pensez à regarder dans les indésirables.",
    email,
  };
}

async function siteOrigin(): Promise<string> {
  const h = await headers();
  const origin = h.get("origin");
  if (origin) return origin;
  const host = h.get("x-forwarded-host") ?? h.get("host");
  const proto = h.get("x-forwarded-proto") ?? "https";
  return `${proto}://${host}`;
}

function explain(error: AuthError): string {
  switch (error.code) {
    case "invalid_credentials":
      return "Adresse e-mail ou mot de passe incorrect.";
    case "email_not_confirmed":
      return "Votre adresse n'est pas encore confirmée : cliquez sur le lien reçu par e-mail.";
    case "user_already_exists":
    case "email_exists":
      return "Un compte existe déjà avec cette adresse. Connectez-vous plutôt.";
    case "weak_password":
      return "Mot de passe trop faible : au moins 6 caractères.";
    case "email_address_invalid":
    case "validation_failed":
      return "Cette adresse e-mail ne semble pas valide.";
    case "over_email_send_rate_limit":
    case "over_request_rate_limit":
      return "Trop de tentatives en peu de temps. Réessayez un peu plus tard.";
    case "signup_disabled":
      return "Les inscriptions sont fermées pour le moment.";
    default:
      return `Une erreur est survenue (${error.message}). Réessayez dans un instant.`;
  }
}
