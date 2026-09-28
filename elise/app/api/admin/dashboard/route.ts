import { NextResponse, type NextRequest } from "next/server";
import { adminStatus, loadDashboard, parsePeriod } from "@/lib/admin";
import { createClient, currentUserId } from "@/lib/supabase/server";

// Les chiffres du tableau de bord, que la page redemande toutes les quelques
// secondes pour afficher les achats en direct.
export async function GET(request: NextRequest) {
  const supabase = await createClient();
  if (!(await currentUserId(supabase))) {
    return NextResponse.json({ error: "Session expirée." }, { status: 401 });
  }
  if ((await adminStatus(supabase)) !== "admin") {
    return NextResponse.json({ error: "Introuvable." }, { status: 404 });
  }

  const params = request.nextUrl.searchParams;
  try {
    const data = await loadDashboard(supabase, params.get("client") || null, parsePeriod(params.get("jours")));
    return NextResponse.json(data, { headers: { "cache-control": "no-store" } });
  } catch (err) {
    console.error(err);
    return NextResponse.json({ error: "Les chiffres n'ont pas pu être chargés." }, { status: 500 });
  }
}
