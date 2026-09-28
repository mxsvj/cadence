import { NextResponse } from "next/server";
import { offerError, offerId } from "@/lib/offer-api";
import { OFFER_COLUMNS, type Offer } from "@/lib/offers";
import { createClient, currentUserId } from "@/lib/supabase/server";

// Acheter une offre à son prix affiché. Aucun service de paiement n'est
// encore branché : l'achat est enregistré comme « démo », sans débit.
export async function POST(_request: Request, ctx: RouteContext<"/api/offres/[id]/acheter">) {
  const id = offerId((await ctx.params).id);
  if (!id) return NextResponse.json({ error: "Offre introuvable." }, { status: 404 });
  const supabase = await createClient();
  if (!(await currentUserId(supabase))) return NextResponse.json({ error: "Session expirée." }, { status: 401 });

  const { error } = await supabase.rpc("acheter_offre", { p_offre: id });
  if (error) return offerError(error);
  const { data } = await supabase.from("offers").select(OFFER_COLUMNS).eq("id", id).single();
  return NextResponse.json({ offer: data as Offer });
}
