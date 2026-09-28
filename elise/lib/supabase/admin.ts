import "server-only";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { supabaseEnv } from "./env";

// Le client « serveur » de Supabase, avec la clé secrète : il passe outre les
// règles de sécurité de la base. Il ne sert qu'à ce que la personne connectée
// ne doit pas pouvoir lire elle-même : les réglages de l'IA, les notes de
// l'équipe, les prix minimum, les fichiers à vendre. Jamais dans le navigateur.

export function secretKey(): string | null {
  return process.env.SUPABASE_SECRET_KEY?.trim() || null;
}

let cached: SupabaseClient | null = null;

export function createAdminClient(): SupabaseClient {
  const env = supabaseEnv();
  const key = secretKey();
  if (!env || !key) {
    throw new Error("Supabase n'est pas entièrement configuré (SUPABASE_SECRET_KEY manquante).");
  }
  cached ??= createClient(env.url, key, {
    auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
  });
  return cached;
}

/** Le dossier privé des médias à vendre. */
export const CONTENT_BUCKET = "contenus";
