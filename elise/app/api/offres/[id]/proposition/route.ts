import { NextResponse } from "next/server";
import type { Message } from "@/lib/memory";
import { negotiationReply, type BidResult } from "@/lib/negotiation";
import { flushAlertsLater } from "@/lib/notify";
import { offerError, offerId } from "@/lib/offer-api";
import { OFFER_COLUMNS, parseEuros, type Offer } from "@/lib/offers";
import { validTimeZone } from "@/lib/prompts";
import { createAdminClient } from "@/lib/supabase/admin";
import { createClient, currentUserId } from "@/lib/supabase/server";
import { typingDelayMs } from "@/lib/typing";

// La créatrice réagit à la contre-offre : le modèle a le temps de répondre.
export const maxDuration = 60;

// Faire une offre, comme sur un site de revente. La base l'accepte si elle
// atteint le prix minimum de l'étape, sans jamais le révéler.
export async function POST(request: Request, ctx: RouteContext<"/api/offres/[id]/proposition">) {
  const id = offerId((await ctx.params).id);
  if (!id) return NextResponse.json({ error: "Offre introuvable." }, { status: 404 });
  const supabase = await createClient();
  const userId = await currentUserId(supabase);
  if (!userId) return NextResponse.json({ error: "Session expirée." }, { status: 401 });

  const body = (await request.json().catch(() => null)) as { montant?: unknown; tz?: unknown } | null;
  const cents = typeof body?.montant === "string" ? parseEuros(body.montant) : null;
  if (!cents) return NextResponse.json({ error: "Indiquez un montant en euros, par exemple 7,50." }, { status: 400 });

  // Le prix affiché avant la proposition (la base le change si elle l'accepte).
  const { data: before } = await supabase.from("offers").select("price_cents, creator_id, step_id").eq("id", id).maybeSingle();
  const { data: result, error } = await supabase.rpc("faire_une_offre", { p_offre: id, p_montant_cents: cents });
  if (error) return offerError(error);
  // La base a prévenu l'équipe de cette contre-offre : on l'envoie sur Discord ou Telegram.
  flushAlertsLater(new URL(request.url).origin);
  const { data } = await supabase.from("offers").select(OFFER_COLUMNS).eq("id", id).single();

  // La créatrice réagit dans la conversation. Si ça échoue, la contre-offre reste faite.
  let messages: Message[] = [];
  if (before) {
    try {
      messages = await negotiationReply({
        supabase,
        admin: createAdminClient(),
        userId,
        offer: before as { creator_id: number; step_id: number | null },
        basePriceCents: Number(before.price_cents),
        bidCents: cents,
        result: result as BidResult,
        timezone: validTimeZone(body?.tz),
      });
    } catch (err) {
      console.error("Réaction à la contre-offre impossible :", err);
    }
  }
  const typingMs = messages.length ? typingDelayMs(messages.map((m) => m.content).join(" ")) : 0;
  return NextResponse.json({ result, offer: data as Offer, messages, typingMs });
}
