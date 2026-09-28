import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { supabaseEnv } from "@/lib/supabase/env";

// Passe avant chaque page : rafraîchit la session Supabase (stockée dans des
// cookies) et renvoie vers /connexion quiconque n'est pas connecté.
export async function proxy(request: NextRequest) {
  const env = supabaseEnv();
  // Pas encore configuré : on laisse passer, la page affiche quoi faire.
  if (!env) return NextResponse.next({ request });

  let response = NextResponse.next({ request });

  const supabase = createServerClient(env.url, env.key, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet, headers) {
        for (const { name, value } of cookiesToSet) request.cookies.set(name, value);
        response = NextResponse.next({ request });
        for (const { name, value, options } of cookiesToSet) response.cookies.set(name, value, options);
        for (const [key, value] of Object.entries(headers)) response.headers.set(key, value);
      },
    },
  });

  const { data } = await supabase.auth.getClaims();
  const signedIn = Boolean(data?.claims?.sub);
  const path = request.nextUrl.pathname;
  const isPublic = path.startsWith("/connexion") || path.startsWith("/auth/") || path.startsWith("/api/");

  if (!signedIn && !isPublic) return redirectKeepingCookies(request, response, "/connexion");
  if (signedIn && path.startsWith("/connexion")) return redirectKeepingCookies(request, response, "/");
  return response;
}

function redirectKeepingCookies(request: NextRequest, from: NextResponse, to: string) {
  const redirect = NextResponse.redirect(new URL(to, request.url));
  for (const cookie of from.cookies.getAll()) redirect.cookies.set(cookie);
  return redirect;
}

// Pas de contrôle pour les fichiers du site (scripts, images, icônes, manifeste).
export const config = {
  matcher: ["/((?!_next/static|_next/image|manifest.webmanifest|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)"],
};
