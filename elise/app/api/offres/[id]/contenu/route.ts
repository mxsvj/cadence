import { NextResponse } from "next/server";
import { offerError, offerId } from "@/lib/offer-api";
import { CONTENT_BUCKET, createAdminClient } from "@/lib/supabase/admin";
import { createClient, currentUserId } from "@/lib/supabase/server";

// Le contenu acheté. La base vérifie d'abord que la personne l'a bien acheté
// (ou reçu en cadeau) ; un fichier ne sort alors que par un lien valable
// cinq minutes. Sans achat : rien, pas même un aperçu.
export async function GET(_request: Request, ctx: RouteContext<"/api/offres/[id]/contenu">) {
  const id = offerId((await ctx.params).id);
  if (!id) return NextResponse.json({ error: "Contenu introuvable." }, { status: 404 });
  const supabase = await createClient();
  if (!(await currentUserId(supabase))) return NextResponse.json({ error: "Session expirée." }, { status: 401 });

  const { data, error } = await supabase.rpc("mon_contenu", { p_offre: id });
  if (error) return offerError(error);
  const content = data as { type: "image" | "video" | "texte"; texte: string; media_path: string | null };

  let url: string | null = null;
  if (content.media_path) {
    const signed = await createAdminClient().storage.from(CONTENT_BUCKET).createSignedUrl(content.media_path, 300);
    if (signed.error) {
      console.error(signed.error);
      return NextResponse.json({ error: "Le fichier n'a pas pu être chargé." }, { status: 500 });
    }
    url = signed.data.signedUrl;
  }
  return NextResponse.json(
    { type: content.type, texte: content.texte, url },
    { headers: { "cache-control": "private, no-store" } },
  );
}
