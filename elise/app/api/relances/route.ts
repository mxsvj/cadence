import { NextResponse } from "next/server";
import { cronSecret, runRelances } from "@/lib/relances";
import { createAdminClient } from "@/lib/supabase/admin";
import { sameKey } from "@/lib/team-access";

// Appelée une fois par jour par Vercel (vercel.json → crons), avec l'en-tête
// « Authorization: Bearer <CRON_SECRET> ». Sans ce secret, personne ne peut
// la déclencher.
export const maxDuration = 60;
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const secret = cronSecret();
  if (!secret) return NextResponse.json({ error: "CRON_SECRET manque dans Vercel." }, { status: 503 });
  if (!sameKey(request.headers.get("authorization") ?? "", `Bearer ${secret}`)) {
    return NextResponse.json({ error: "Accès refusé." }, { status: 401 });
  }
  try {
    const report = await runRelances(createAdminClient());
    console.log("Prises de nouvelles :", report);
    return NextResponse.json(report, { headers: { "cache-control": "no-store" } });
  } catch (err) {
    console.error("Prises de nouvelles impossibles :", err);
    return NextResponse.json({ error: "Le passage n'a pas abouti." }, { status: 500 });
  }
}
