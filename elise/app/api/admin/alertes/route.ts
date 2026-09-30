import { NextResponse } from "next/server";
import { requireAdmin } from "@/lib/admin";
import { createClient, currentUserId } from "@/lib/supabase/server";
import { loadAlerts } from "@/lib/team";

// Les alertes à traiter, redemandées régulièrement par l'espace de l'équipe
// (bandeau flash et pastille de l'onglet Messages).
export async function GET() {
  const supabase = await createClient();
  if (!(await currentUserId(supabase))) return NextResponse.json({ error: "Session expirée." }, { status: 401 });
  try {
    await requireAdmin(supabase);
  } catch {
    return NextResponse.json({ error: "Introuvable." }, { status: 404 });
  }
  try {
    const alerts = await loadAlerts(supabase);
    return NextResponse.json(
      { alerts: alerts ?? [], outdated: alerts === null },
      { headers: { "cache-control": "no-store" } },
    );
  } catch (err) {
    console.error(err);
    return NextResponse.json({ error: "Les alertes n'ont pas pu être chargées." }, { status: 500 });
  }
}
