// Les deux réglages Supabase. Ils ne sont pas secrets : c'est la sécurité
// au niveau des lignes, dans la base, qui protège les données.
export function supabaseEnv(): { url: string; key: string } | null {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL?.trim();
  const key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY?.trim();
  return url && key ? { url, key } : null;
}
