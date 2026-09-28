import { NextResponse } from "next/server";
import { offerError, offerId } from "@/lib/offer-api";
import { OFFER_COLUMNS, parseEuros, type Offer } from "@/lib/offers";
import { createClient, currentUserId } from "@/lib/supabase/server";

// Faire une offre, comme sur un site de revente. La base l'accepte si elle
// atteint le prix minimum de l'étape, sans jamais le révéler.
export async function POST(request: Request, ctx: RouteContext<"/api/offres/[id]/proposition">) {
  const id = offerId((await ctx.params).id);
  if (!id) return NextResponse.json({ error: "Offre introuvable." }, { status: 404 });
  const supabase = await createClient();
  if (!(await currentUserId(supabase))) return NextResponse.json({ error: "Session expirée." }, { status: 401 });

  const body = (await request.json().catch(() => null)) as { montant?: unknown } | null;
  const cents = typeof body?.montant === "string" ? parseEuros(body.montant) : null;
  if (!cents) return NextResponse.json({ error: "Indiquez un montant en euros, par exemple 7,50." }, { status: 400 });

  const { data: result, error } = await supabase.rpc("faire_une_offre", { p_offre: id, p_montant_cents: cents });
  if (error) return offerError(error);
  const { data } = await supabase.from("offers").select(OFFER_COLUMNS).eq("id", id).single();
  return NextResponse.json({ result, offer: data as Offer });
}
