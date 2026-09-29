import { NextResponse } from "next/server";
import { offerError, offerId } from "@/lib/offer-api";
import type { MediaItem } from "@/lib/offers";
import { CONTENT_BUCKET, createAdminClient } from "@/lib/supabase/admin";
import { createClient, currentUserId } from "@/lib/supabase/server";

// Le contenu acheté. La base vérifie d'abord que la personne l'a bien acheté
// (ou reçu en cadeau) ; chaque photo ou vidéo ne sort alors que par un lien
// valable cinq minutes. Sans achat : rien, pas même un aperçu.
export async function GET(_request: Request, ctx: RouteContext<"/api/offres/[id]/contenu">) {
  const id = offerId((await ctx.params).id);
  if (!id) return NextResponse.json({ error: "Contenu introuvable." }, { status: 404 });
  const supabase = await createClient();
  if (!(await currentUserId(supabase))) return NextResponse.json({ error: "Session expirée." }, { status: 401 });

  const { data, error } = await supabase.rpc("mon_contenu", { p_offre: id });
  if (error) return offerError(error);
  const content = data as { type: "image" | "video" | "texte"; texte: string; media: MediaItem[] | null };

  const storage = createAdminClient().storage.from(CONTENT_BUCKET);
  const signed = await Promise.all((content.media ?? []).map((m) => storage.createSignedUrl(m.path, 300)));
  const failed = signed.find((s) => s.error);
  if (failed) {
    console.error(failed.error);
    return NextResponse.json({ error: "Un fichier n'a pas pu être chargé." }, { status: 500 });
  }
  const items = (content.media ?? []).map((m, i) => ({ kind: m.kind, url: signed[i].data!.signedUrl }));
  return NextResponse.json(
    { type: content.type, texte: content.texte, items },
    { headers: { "cache-control": "private, no-store" } },
  );
}
